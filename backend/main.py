from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes import kunden, fahrzeuge, werkstaetten, auftraege, ki, openai_route

Base.metadata.create_all(bind=engine)

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

app.include_router(kunden.router, prefix="/kunden", tags=["Customers"])
app.include_router(fahrzeuge.router, prefix="/fahrzeuge", tags=["Vehicles"])
app.include_router(werkstaetten.router, prefix="/werkstatt", tags=["Workshops"])
app.include_router(auftraege.router, prefix="/auftraege", tags=["Orders"])
app.include_router(ki.router, prefix="/ki", tags=["AI"])
app.include_router(openai_route.router, prefix="", tags=["Chat"])


@app.get("/", tags=["Root"])
def home():
    return {"message": "Vehicle Service API is running 🚗", "version": "2.0.0"}

