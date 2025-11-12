from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import kunden, fahrzeuge, auftraege, werkstaetten, ki, openai_route

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fahrzeugservice API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "Fahrzeugservice-API läuft 🚗"}

app.include_router(kunden.router)
app.include_router(fahrzeuge.router)
app.include_router(auftraege.router)
app.include_router(werkstaetten.router)
app.include_router(ki.router)
app.include_router(openai_route.router)
