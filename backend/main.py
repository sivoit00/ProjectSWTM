from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes import kunden, fahrzeuge, werkstaetten, auftraege, ki, openai_route, chat_history, files

Base.metadata.create_all(bind=engine)
import os
import openai
from pydantic import BaseModel
from agents.kiClone import route_message

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Vehicle Service API",
    description="API for vehicle service management with AI integration",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LawyerRequest(BaseModel):
    city: str
    topic: str = "Verkehrsrecht"
    max_results: int = 3

class KIMessage(BaseModel):
    message: str
app.include_router(kunden.router, prefix="/kunden", tags=["Customers"])
app.include_router(fahrzeuge.router, prefix="/fahrzeuge", tags=["Vehicles"])
app.include_router(werkstaetten.router, prefix="/werkstatt", tags=["Workshops"])
app.include_router(auftraege.router, prefix="/auftraege", tags=["Orders"])
app.include_router(ki.router, prefix="/ki", tags=["AI"])
app.include_router(openai_route.router, prefix="", tags=["Chat"])
app.include_router(chat_history.router)
app.include_router(files.router)


@app.get("/", tags=["Root"])
def home():
    return {"message": "Vehicle Service API is running 🚗", "version": "2.0.0"}

@app.post("/ki/message")
def ki_message(req: KIMessage, db: Session = Depends(get_db)): 
    result = route_message(req.message)
    return result