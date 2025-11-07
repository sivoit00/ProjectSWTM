from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from backend.database import SessionLocal, engine
import backend.models as models, backend.schemas as schemas
from datetime import date
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import openai
from pydantic import BaseModel

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


# ---------------- HOME ----------------
@app.get("/")
def home():
    return {"message": "Fahrzeugservice-API läuft 🚗"}


# ---------------- KUNDEN ----------------
@app.get("/kunden", response_model=list[schemas.Kunde])
def get_kunden(db: Session = Depends(get_db)):
    return db.query(models.Kunde).all()


@app.post("/kunden", response_model=schemas.Kunde)
def create_kunde(kunde: schemas.KundeCreate, db: Session = Depends(get_db)):
    neuer_kunde = models.Kunde(**kunde.dict())
    db.add(neuer_kunde)
    db.commit()
    db.refresh(neuer_kunde)
    return neuer_kunde


# ---------------- FAHRZEUGE ----------------
@app.get("/fahrzeuge", response_model=list[schemas.Fahrzeug])
def get_fahrzeuge(db: Session = Depends(get_db)):
    return db.query(models.Fahrzeug).all()

@app.post("/fahrzeuge", response_model=schemas.Fahrzeug)
def create_fahrzeug(fahrzeug: schemas.FahrzeugCreate, db: Session = Depends(get_db)):
    neues_fahrzeug = models.Fahrzeug(**fahrzeug.dict())
    db.add(neues_fahrzeug)
    db.commit()
    db.refresh(neues_fahrzeug)
    return neues_fahrzeug


# ---------------- WERKSTÄTTEN ----------------
@app.get("/werkstatt", response_model=list[schemas.Werkstatt])
def get_werkstatt(db: Session = Depends(get_db)):
    return db.query(models.Werkstatt).all()

@app.post("/werkstatt", response_model=schemas.Werkstatt)
def create_werkstatt(werkstatt: schemas.WerkstattCreate, db: Session = Depends(get_db)):
    neue_werkstatt = models.Werkstatt(**werkstatt.dict())
    db.add(neue_werkstatt)
    db.commit()
    db.refresh(neue_werkstatt)
    return neue_werkstatt


# ---------------- AUFTRÄGE ----------------
@app.get("/auftraege", response_model=list[schemas.Auftrag])
def get_auftraege(db: Session = Depends(get_db)):
    return db.query(models.Auftrag).all()

@app.post("/auftraege", response_model=schemas.Auftrag)
def create_auftrag(auftrag: schemas.AuftragCreate, db: Session = Depends(get_db)):
    neuer_auftrag = models.Auftrag(**auftrag.dict())
    if not neuer_auftrag.erstellt_am:
        neuer_auftrag.erstellt_am = date.today()
    db.add(neuer_auftrag)
    db.commit()
    db.refresh(neuer_auftrag)
    return neuer_auftrag


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
