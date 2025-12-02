from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from routes import kunden, fahrzeuge, werkstaetten, auftraege, ki, openai_route, chat_history, files, ki_orchestrator, insurance, guardrails, admin_guardrails
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from agents.email_listener import check_inbox_for_replies
import logging

log = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

def run_email_check():
    """Wird vom Scheduler regelmäßig aufgerufen"""
    try:
        check_inbox_for_replies()
    except Exception as e:
        log.error(f"Fehler im Email-Scheduler: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_email_check, 'interval', seconds=60) 
    scheduler.start()
    log.info("Email-Scheduler gestartet (Check alle 60s).")
    yield
    scheduler.shutdown()
    log.info("Email-Scheduler beendet.")


app = FastAPI(
    title="Vehicle Service API",
    description="API for vehicle service management with AI integration",
    version="2.0.0",
    lifespan=lifespan 
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
app.include_router(openai_route.router, tags=["Chat"])
app.include_router(chat_history.router)
app.include_router(files.router)
app.include_router(ki_orchestrator.router, prefix="/ki-orchestrator", tags=["KI Orchestrator"])
app.include_router(insurance.router, prefix="/ki", tags=["Insurance"])
app.include_router(guardrails.router, prefix="/guardrails", tags=["GuardRails"])
app.include_router(admin_guardrails.router, prefix="/admin/guardrails", tags=["GuardRails Admin"])

@app.get("/", tags=["Root"])
def home():
    return {"message": "Vehicle Service API is running 🚗", "version": "2.0.0"}