from fastapi import FastAPI, Depends, Header
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models, schemas
from datetime import date, datetime, timedelta
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from pydantic import BaseModel
import bcrypt
from jose import jwt, JWTError
from typing import Optional

# JWT Konfiguration
JWT_SECRET_KEY = "supersecretkey123"  # In Produktion: Umgebungsvariable!
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_MINUTES = 60

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fahrzeugservice API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency für DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# JWT Helper-Funktionen
def create_access_token(data: dict):
    """JWT Token erstellen"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


def hash_password(password: str) -> str:
    """Passwort mit bcrypt hashen"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Passwort verifizieren"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_current_user(authorization: Optional[str] = Header(None), db: Session = Depends(get_db)):
    """JWT Token validieren und aktuellen User zurückgeben"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")
    
    try:
        # "Bearer <token>" Format
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Ungültiges Authentifizierungsschema")
        
        # Token dekodieren
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("user_id")
        
        if user_id is None:
            raise HTTPException(status_code=401, detail="Ungültiger Token")
        
        # User aus DB laden
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User nicht gefunden")
        
        return user
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Token konnte nicht validiert werden")
    except ValueError:
        raise HTTPException(status_code=401, detail="Ungültiges Token Format")



# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"message": "Fahrzeugservice-API läuft 🚗"}


# ---------------- LOGIN / AUTH ----------------
@app.post("/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login mit Email und Passwort - gibt JWT Token zurück"""
    # User suchen
    user = db.query(models.User).filter(models.User.email == user_login.email).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Ungültige Email oder Passwort")
    
    # Passwort prüfen
    if not verify_password(user_login.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Ungültige Email oder Passwort")
    
    # JWT Token erstellen
    access_token = create_access_token(data={"sub": user.email, "user_id": user.id})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register", response_model=schemas.UserResponse)
def register(user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    """Neuen User registrieren und automatisch Kunde anlegen"""
    # Prüfen ob Email bereits existiert (User oder Kunde)
    existing_user = db.query(models.User).filter(models.User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email bereits registriert")
    
    existing_kunde = db.query(models.Kunde).filter(models.Kunde.email == user_create.email).first()
    if existing_kunde:
        raise HTTPException(status_code=400, detail="Kunde mit dieser Email existiert bereits")
    
    # Passwort hashen
    hashed_pw = hash_password(user_create.password)
    
    # User erstellen
    new_user = models.User(
        email=user_create.email,
        password_hash=hashed_pw,
        name=user_create.name
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Automatisch Kunde-Datensatz anlegen
    new_kunde = models.Kunde(
        name=user_create.name or user_create.email,  # Name oder Email als Fallback
        email=user_create.email,
        telefon=None  # Optional, kann später ergänzt werden
    )
    
    db.add(new_kunde)
    db.commit()
    db.refresh(new_kunde)
    
    return new_user


@app.get("/me")
def get_current_user_info(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aktuelle User-Info mit Kunde-Daten abrufen"""
    # Kunde über Email finden
    kunde = db.query(models.Kunde).filter(models.Kunde.email == current_user.email).first()
    
    if not kunde:
        return {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "name": current_user.name,
            },
            "kunde": None,
            "stats": {
                "fahrzeuge": 0,
                "auftraege": 0
            }
        }
    
    # Fahrzeuge und Aufträge zählen
    fahrzeuge_count = db.query(models.Fahrzeug).filter(models.Fahrzeug.kunde_id == kunde.id).count()
    auftraege_count = db.query(models.Auftrag).join(models.Fahrzeug).filter(
        models.Fahrzeug.kunde_id == kunde.id
    ).count()
    
    return {
        "user": {
            "id": current_user.id,
            "email": current_user.email,
            "name": current_user.name,
        },
        "kunde": {
            "id": kunde.id,
            "name": kunde.name,
            "email": kunde.email,
            "telefon": kunde.telefon
        },
        "stats": {
            "fahrzeuge": fahrzeuge_count,
            "auftraege": auftraege_count
        }
    }


@app.get("/auftraege/me", response_model=list[schemas.Auftrag])
def get_my_auftraege(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Aufträge des eingeloggten Users abrufen"""
    # Kunde über Email des Users finden
    kunde = db.query(models.Kunde).filter(models.Kunde.email == current_user.email).first()
    
    if not kunde:
        # User hat keinen Kunden-Datensatz -> keine Aufträge
        return []
    
    # Aufträge über Fahrzeuge des Kunden laden
    auftraege = db.query(models.Auftrag).join(models.Fahrzeug).filter(
        models.Fahrzeug.kunde_id == kunde.id
    ).all()
    
    return auftraege


# ---------------- KUNDEN ----------------
@app.get("/kunden", response_model=list[schemas.Kunde])
def get_kunden(db: Session = Depends(get_db)):
    """Alle Kunden abrufen"""
    return db.query(models.Kunde).all()


@app.get("/kunden/{kunde_id}", response_model=schemas.Kunde)
def get_kunde(kunde_id: int, db: Session = Depends(get_db)):
    """Einzelnen Kunden abrufen"""
    kunde = db.query(models.Kunde).filter(models.Kunde.id == kunde_id).first()
    if not kunde:
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunde_id} nicht gefunden")
    return kunde


@app.post("/kunden", response_model=schemas.Kunde)
def create_kunde(kunde: schemas.KundeCreate, db: Session = Depends(get_db)):
    """Neuen Kunden anlegen"""
    neuer_kunde = models.Kunde(**kunde.dict())
    db.add(neuer_kunde)
    db.commit()
    db.refresh(neuer_kunde)
    return neuer_kunde


@app.put("/kunden/{kunde_id}", response_model=schemas.Kunde)
def update_kunde(kunde_id: int, kunde: schemas.KundeCreate, db: Session = Depends(get_db)):
    """Kundendaten aktualisieren"""
    db_kunde = db.query(models.Kunde).filter(models.Kunde.id == kunde_id).first()
    if not db_kunde:
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunde_id} nicht gefunden")
    
    for key, value in kunde.dict().items():
        setattr(db_kunde, key, value)
    
    db.commit()
    db.refresh(db_kunde)
    return db_kunde


@app.delete("/kunden/{kunde_id}")
def delete_kunde(kunde_id: int, db: Session = Depends(get_db)):
    """Kunden löschen"""
    kunde = db.query(models.Kunde).filter(models.Kunde.id == kunde_id).first()
    if not kunde:
        raise HTTPException(status_code=404, detail=f"Kunde mit ID {kunde_id} nicht gefunden")
    
    db.delete(kunde)
    db.commit()
    return {"message": f"Kunde {kunde_id} erfolgreich gelöscht"}


# ---------------- FAHRZEUGE ----------------
@app.get("/fahrzeuge", response_model=list[schemas.Fahrzeug])
def get_fahrzeuge(db: Session = Depends(get_db)):
    """Alle Fahrzeuge abrufen"""
    return db.query(models.Fahrzeug).all()


@app.get("/fahrzeuge/{fahrzeug_id}", response_model=schemas.Fahrzeug)
def get_fahrzeug(fahrzeug_id: int, db: Session = Depends(get_db)):
    """Einzelnes Fahrzeug abrufen"""
    fahrzeug = db.query(models.Fahrzeug).filter(models.Fahrzeug.id == fahrzeug_id).first()
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug mit ID {fahrzeug_id} nicht gefunden")
    return fahrzeug


@app.post("/fahrzeuge", response_model=schemas.Fahrzeug)
def create_fahrzeug(fahrzeug: schemas.FahrzeugCreate, db: Session = Depends(get_db)):
    """Neues Fahrzeug anlegen"""
    neues_fahrzeug = models.Fahrzeug(**fahrzeug.dict())
    db.add(neues_fahrzeug)
    db.commit()
    db.refresh(neues_fahrzeug)
    return neues_fahrzeug


@app.put("/fahrzeuge/{fahrzeug_id}", response_model=schemas.Fahrzeug)
def update_fahrzeug(fahrzeug_id: int, fahrzeug: schemas.FahrzeugCreate, db: Session = Depends(get_db)):
    """Fahrzeugdaten aktualisieren"""
    db_fahrzeug = db.query(models.Fahrzeug).filter(models.Fahrzeug.id == fahrzeug_id).first()
    if not db_fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug mit ID {fahrzeug_id} nicht gefunden")
    
    for key, value in fahrzeug.dict().items():
        setattr(db_fahrzeug, key, value)
    
    db.commit()
    db.refresh(db_fahrzeug)
    return db_fahrzeug


@app.delete("/fahrzeuge/{fahrzeug_id}")
def delete_fahrzeug(fahrzeug_id: int, db: Session = Depends(get_db)):
    """Fahrzeug löschen"""
    fahrzeug = db.query(models.Fahrzeug).filter(models.Fahrzeug.id == fahrzeug_id).first()
    if not fahrzeug:
        raise HTTPException(status_code=404, detail=f"Fahrzeug mit ID {fahrzeug_id} nicht gefunden")
    
    db.delete(fahrzeug)
    db.commit()
    return {"message": f"Fahrzeug {fahrzeug_id} erfolgreich gelöscht"}


# ---------------- WERKSTÄTTEN ----------------
@app.get("/werkstatt", response_model=list[schemas.Werkstatt])
def get_werkstatt(db: Session = Depends(get_db)):
    """Alle Werkstätten abrufen"""
    return db.query(models.Werkstatt).all()


@app.get("/werkstatt/{werkstatt_id}", response_model=schemas.Werkstatt)
def get_werkstatt_by_id(werkstatt_id: int, db: Session = Depends(get_db)):
    """Einzelne Werkstatt abrufen"""
    werkstatt = db.query(models.Werkstatt).filter(models.Werkstatt.id == werkstatt_id).first()
    if not werkstatt:
        raise HTTPException(status_code=404, detail=f"Werkstatt mit ID {werkstatt_id} nicht gefunden")
    return werkstatt


@app.post("/werkstatt", response_model=schemas.Werkstatt)
def create_werkstatt(werkstatt: schemas.WerkstattCreate, db: Session = Depends(get_db)):
    """Neue Werkstatt anlegen"""
    neue_werkstatt = models.Werkstatt(**werkstatt.dict())
    db.add(neue_werkstatt)
    db.commit()
    db.refresh(neue_werkstatt)
    return neue_werkstatt


@app.put("/werkstatt/{werkstatt_id}", response_model=schemas.Werkstatt)
def update_werkstatt(werkstatt_id: int, werkstatt: schemas.WerkstattCreate, db: Session = Depends(get_db)):
    """Werkstattdaten aktualisieren"""
    db_werkstatt = db.query(models.Werkstatt).filter(models.Werkstatt.id == werkstatt_id).first()
    if not db_werkstatt:
        raise HTTPException(status_code=404, detail=f"Werkstatt mit ID {werkstatt_id} nicht gefunden")
    
    for key, value in werkstatt.dict().items():
        setattr(db_werkstatt, key, value)
    
    db.commit()
    db.refresh(db_werkstatt)
    return db_werkstatt


@app.delete("/werkstatt/{werkstatt_id}")
def delete_werkstatt(werkstatt_id: int, db: Session = Depends(get_db)):
    """Werkstatt löschen"""
    werkstatt = db.query(models.Werkstatt).filter(models.Werkstatt.id == werkstatt_id).first()
    if not werkstatt:
        raise HTTPException(status_code=404, detail=f"Werkstatt mit ID {werkstatt_id} nicht gefunden")
    
    db.delete(werkstatt)
    db.commit()
    return {"message": f"Werkstatt {werkstatt_id} erfolgreich gelöscht"}


# ---------------- AUFTRÄGE ----------------
@app.get("/auftraege", response_model=list[schemas.Auftrag])
def get_auftraege(db: Session = Depends(get_db)):
    """Alle Aufträge abrufen"""
    return db.query(models.Auftrag).all()


@app.get("/auftraege/{auftrag_id}", response_model=schemas.Auftrag)
def get_auftrag(auftrag_id: int, db: Session = Depends(get_db)):
    """Einzelnen Auftrag abrufen"""
    auftrag = db.query(models.Auftrag).filter(models.Auftrag.id == auftrag_id).first()
    if not auftrag:
        raise HTTPException(status_code=404, detail=f"Auftrag mit ID {auftrag_id} nicht gefunden")
    return auftrag


@app.post("/auftraege", response_model=schemas.Auftrag)
def create_auftrag(auftrag: schemas.AuftragCreate, db: Session = Depends(get_db)):
    """Neuen Auftrag anlegen"""
    neuer_auftrag = models.Auftrag(**auftrag.dict())
    if not neuer_auftrag.erstellt_am:
        neuer_auftrag.erstellt_am = date.today()
    db.add(neuer_auftrag)
    db.commit()
    db.refresh(neuer_auftrag)
    return neuer_auftrag


@app.put("/auftraege/{auftrag_id}", response_model=schemas.Auftrag)
def update_auftrag(auftrag_id: int, auftrag: schemas.AuftragCreate, db: Session = Depends(get_db)):
    """Auftragsdaten aktualisieren"""
    db_auftrag = db.query(models.Auftrag).filter(models.Auftrag.id == auftrag_id).first()
    if not db_auftrag:
        raise HTTPException(status_code=404, detail=f"Auftrag mit ID {auftrag_id} nicht gefunden")
    
    for key, value in auftrag.dict().items():
        setattr(db_auftrag, key, value)
    
    db.commit()
    db.refresh(db_auftrag)
    return db_auftrag


@app.delete("/auftraege/{auftrag_id}")
def delete_auftrag(auftrag_id: int, db: Session = Depends(get_db)):
    """Auftrag löschen"""
    auftrag = db.query(models.Auftrag).filter(models.Auftrag.id == auftrag_id).first()
    if not auftrag:
        raise HTTPException(status_code=404, detail=f"Auftrag mit ID {auftrag_id} nicht gefunden")
    
    db.delete(auftrag)
    db.commit()
    return {"message": f"Auftrag {auftrag_id} erfolgreich gelöscht"}


# ---------------- KI-ENDPOINT ----------------
@app.post("/ki/auftrag", response_model=schemas.KIAktionSchema)
def ki_create_auftrag(action: schemas.KIAktionCreate, db: Session = Depends(get_db)):
    # Einfache Heuristik: wenn werkstatt_id gegeben, verwende sie, sonst wähle erste Werkstatt
    werkstatt_id = action.werkstatt_id
    if werkstatt_id is None:
        werk = db.query(models.Werkstatt).first()
        if werk:
            werkstatt_id = werk.id

    # Falls Fahrzeuginfo fehlt, versuchen wir es nicht automatisch zuzuordnen
    if action.fahrzeug_id is None and action.kunde_id is None:
        antwort = "Danke für Ihre Nachricht. Bitte geben Sie mindestens eine Fahrzeug- oder Kunden-ID an."
        ki = models.KIAktion(nachricht=action.nachricht, antwort=antwort, auftrag_id=None)
        db.add(ki)
        db.commit()
        db.refresh(ki)
        return ki

    # Erstelle Auftrag
    auftrag = models.Auftrag(
        beschreibung=action.nachricht,
        status="offen",
        erstellt_am=date.today(),
        fahrzeug_id=action.fahrzeug_id,
        werkstatt_id=werkstatt_id,
        kosten=0,
    )
    db.add(auftrag)
    db.commit()
    db.refresh(auftrag)

    # Schreibe KIAktion
    antwort = f"Ihr Auftrag wurde erstellt (ID {auftrag.id}). Wir haben Werkstatt-ID {werkstatt_id} zugewiesen."
    ki = models.KIAktion(nachricht=action.nachricht, antwort=antwort, auftrag_id=auftrag.id)
    db.add(ki)
    db.commit()
    db.refresh(ki)

    return ki


# ---------------- OPENAI CHAT ----------------
class OpenAIRequest(BaseModel):
    message: str


@app.post("/openai/chat")
def openai_chat(req: OpenAIRequest, db: Session = Depends(get_db)):
    """Forward user message to OpenAI (uses OPENAI_API_KEY env var) and store a KIAktion.

    Returns JSON: { "response": "..." }
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured on server")

    try:
        openai.api_key = api_key
        model_name = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        # call ChatCompletion endpoint
        resp = openai.ChatCompletion.create(
            model=model_name,
            messages=[{"role": "user", "content": req.message}],
            max_tokens=600,
            temperature=0.7,
        )
        answer = resp.choices[0].message.content.strip()

        # persist the KIAktion (optional)
        ki = models.KIAktion(nachricht=req.message, antwort=answer, auftrag_id=None)
        db.add(ki)
        db.commit()
        db.refresh(ki)

        return {"response": answer}
    except Exception as e:
        # Log full traceback for debugging
        import traceback
        tb = traceback.format_exc()
        print("OpenAI call failed:", tb)
        # Return the original OpenAI message if available
        detail = str(e)
        try:
            if hasattr(e, 'user_message'):
                detail = e.user_message
            elif hasattr(e, 'error') and isinstance(e.error, dict) and 'message' in e.error:
                detail = e.error['message']
        except Exception:
            pass
        raise HTTPException(status_code=500, detail=detail)


# --- Zusätzliche Filterfunktionen ---

# 🔹 Alle Fahrzeuge eines Kunden abrufen
@app.get("/kunden/{kunde_id}/fahrzeuge", response_model=list[schemas.Fahrzeug])
def get_fahrzeuge_von_kunde(kunde_id: int, db: Session = Depends(get_db)):
    return db.query(models.Fahrzeug).filter(models.Fahrzeug.kunde_id == kunde_id).all()


# 🔹 Alle Aufträge eines Fahrzeugs abrufen
@app.get("/fahrzeuge/{fahrzeug_id}/auftraege", response_model=list[schemas.Auftrag])
def get_auftraege_von_fahrzeug(fahrzeug_id: int, db: Session = Depends(get_db)):
    return db.query(models.Auftrag).filter(models.Auftrag.fahrzeug_id == fahrzeug_id).all()


# 🔹 Aufträge nach Status (z. B. offen oder abgeschlossen)
@app.get("/auftraege/status/{status}", response_model=list[schemas.Auftrag])
def get_auftraege_nach_status(status: str, db: Session = Depends(get_db)):
    return db.query(models.Auftrag).filter(models.Auftrag.status.ilike(status)).all()

