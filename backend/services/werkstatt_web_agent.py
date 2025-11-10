from typing import Optional
import os
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains import SequentialChain
from langchain_community.tools.tavily_search import TavilySearchResults
from sqlalchemy.orm import Session
from database import SessionLocal
import models


def run_werkstatt_agent_sequential(user_query: str) -> str:
    """
    Sequential Chain mit 2 Agenten:
    
    AGENT 1 (Klassifizierungs-Agent):
    - Nimmt die Anfrage entgegen
    - Analysiert, ob es um Werkstattsuche geht
    - Extrahiert relevante Parameter (PLZ, Ort, Fahrzeugtyp)
    - Entscheidet: Weiterleiten an Agent 2 oder direkt beantworten
    
    AGENT 2 (Werkstatt-Such-Agent):
    - Wird nur aktiviert bei Werkstattsuche
    - Sucht im Internet nach Werkstätten
    - Durchsucht die lokale Datenbank
    - Kombiniert beide Quellen zu einer Empfehlung
    
    Beispiel Flow:
    User: "Finde mir eine gute Werkstatt in Berlin"
    → Agent 1: Erkennt "Werkstattsuche", extrahiert "Berlin"
    → Agent 2: Sucht im Web + DB, kombiniert Ergebnisse
    → Output: Konkrete Werkstatt-Empfehlungen
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY ist nicht konfiguriert")
    
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-nano-2025-08-07")
    llm = ChatOpenAI(openai_api_key=api_key, model_name=model_name, temperature=1.0)
    
    # ============================================
    # AGENT 1: Klassifizierungs-Agent
    # ============================================
    
    classification_template = """Du bist Agent 1, ein Klassifizierungs-Agent für Fahrzeugservice-Anfragen.

Deine Aufgabe: Analysiere die Anfrage und entscheide, ob sie an Agent 2 (Werkstatt-Such-Agent) weitergeleitet werden soll.

ANFRAGE: {user_input}

Analysiere und gib folgendes Format zurück:

KATEGORIE: [WERKSTATT_SUCHE oder ANDERE]

WEITERLEITEN: [JA oder NEIN]

EXTRAHIERTE PARAMETER:
- Ort/PLZ: [falls vorhanden]
- Fahrzeugtyp: [falls vorhanden]
- Spezielle Anforderungen: [z.B. "gute Bewertungen", "günstig", "Spezialist"]

BEGRÜNDUNG: [Warum diese Entscheidung?]

ANWEISUNG FÜR AGENT 2: [Was soll Agent 2 konkret tun?]

Beispiele:
- "Finde Werkstatt in Berlin" → WERKSTATT_SUCHE, WEITERLEITEN: JA
- "Wie oft Ölwechsel?" → ANDERE, WEITERLEITEN: NEIN
"""
    
    agent1_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(template=classification_template, input_variables=["user_input"]),
        output_key="classification"
    )
    
    # ============================================
    # AGENT 2: Werkstatt-Such-Agent mit Web-Suche
    # ============================================
    
    werkstatt_search_template = """Du bist Agent 2, ein spezialisierter Werkstatt-Such-Agent.

Du erhältst von Agent 1:
{classification}

ORIGINALANFRAGE:
{user_input}

Deine Aufgaben:

1. PRÜFE die Klassifizierung von Agent 1:
   - Falls WEITERLEITEN: NEIN → Gib eine allgemeine Antwort zur ursprünglichen Frage
   - Falls WEITERLEITEN: JA → Führe Werkstattsuche durch

2. BEI WERKSTATTSUCHE:
   a) Nutze die extrahierten Parameter für Internet-Suche
   b) Suche passende Werkstätten in unserer Datenbank: {db_results}
   c) Recherchiere im Internet: {web_results}
   d) Kombiniere beide Quellen

3. ANTWORT-FORMAT:
   - Bei Werkstattsuche: Konkrete Empfehlungen mit Namen, Adressen, Begründung
   - Bei anderen Fragen: Freundliche, hilfreiche Antwort zur Ursprungsfrage
   - Halte die Antwort kurz und prägnant.
   - Benutze  bei deiner Antwort keine begriffe wie API Key fehlt, so etwas ist nur eine Information fuer den Entwickler.

Antworte auf Deutsch, freundlich und professionell.
"""
    
    agent2_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate(
            template=werkstatt_search_template,
            input_variables=["classification", "user_input", "db_results", "web_results"]
        ),
        output_key="final_answer"
    )
    
    # ============================================
    # Führe Agent 1 aus
    # ============================================
    
    agent1_result = agent1_chain({"user_input": user_query})
    classification = agent1_result["classification"]
    
    print(f"\n=== AGENT 1 KLASSIFIZIERUNG ===\n{classification}\n")
    
    # ============================================
    # Entscheide basierend auf Agent 1
    # ============================================
    
    if "WEITERLEITEN: JA" in classification or "WERKSTATT_SUCHE" in classification:
        # Werkstattsuche durchführen
        
        # 1. Datenbank durchsuchen
        db_results = search_werkstaetten_in_db(user_query, classification)
        
        # 2. Internet durchsuchen (falls TAVILY_API_KEY vorhanden)
        web_results = search_werkstaetten_in_web(user_query, classification)
        
        # 3. Agent 2 ausführen
        agent2_result = agent2_chain({
            "classification": classification,
            "user_input": user_query,
            "db_results": db_results,
            "web_results": web_results
        })
        
        return agent2_result["final_answer"]
    
    else:
        # Keine Werkstattsuche - Agent 2 beantwortet direkt
        agent2_result = agent2_chain({
            "classification": classification,
            "user_input": user_query,
            "db_results": "Nicht relevant (keine Werkstattsuche)",
            "web_results": "Nicht relevant (keine Werkstattsuche)"
        })
        
        return agent2_result["final_answer"]


# ============================================
# Helper-Funktionen
# ============================================

def search_werkstaetten_in_db(user_query: str, classification: str) -> str:
    """Durchsucht die Werkstatt-Datenbank"""
    db = SessionLocal()
    try:
        # Extrahiere Suchbegriffe aus Query
        query_lower = user_query.lower()
        
        # Hole alle Werkstätten
        werkstaetten = db.query(models.Werkstatt).all()
        
        if not werkstaetten:
            return "❌ Keine Werkstätten in unserer Datenbank vorhanden."
        
        # Filter nach Ort/PLZ
        filtered = []
        for w in werkstaetten:
            # Prüfe Matches
            ort_match = w.ort and w.ort.lower() in query_lower
            plz_match = w.plz and str(w.plz) in user_query
            name_match = w.name and w.name.lower() in query_lower
            
            # Auch in Klassifizierung suchen
            if classification:
                ort_in_class = w.ort and w.ort.lower() in classification.lower()
                plz_in_class = w.plz and str(w.plz) in classification
                
                if ort_match or plz_match or name_match or ort_in_class or plz_in_class:
                    filtered.append(w)
            else:
                if ort_match or plz_match or name_match:
                    filtered.append(w)
        
        # Falls keine gefunden, zeige alle (max 10)
        if not filtered:
            filtered = werkstaetten[:10]
            prefix = "ℹ️ Keine exakte Übereinstimmung. Alle verfügbaren Werkstätten:\n"
        else:
            prefix = f"✅ Gefundene Werkstätten in unserer Datenbank ({len(filtered)}):\n"
        
        # Formatiere Ergebnis
        result = prefix
        for w in filtered:
            anzahl_auftraege = len(w.auftraege) if hasattr(w, 'auftraege') else 0
            result += f"  • {w.name}\n"
            result += f"    📍 {w.adresse}, {w.plz} {w.ort}\n"
            result += f"    📊 Aufträge: {anzahl_auftraege}\n"
            result += f"    🆔 ID: {w.id}\n\n"
        
        return result
        
    except Exception as e:
        return f"❌ Fehler beim DB-Zugriff: {str(e)}"
    finally:
        db.close()


def search_werkstaetten_in_web(user_query: str, classification: str) -> str:
    """Durchsucht das Internet nach Werkstätten"""
    tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_api_key:
        return "⚠️ Internet-Suche nicht verfügbar (TAVILY_API_KEY fehlt in .env)"
    
    try:
        # Extrahiere Ort aus Klassifizierung oder Query
        search_query = extract_search_query(user_query, classification)
        
        # Tavily Search Tool
        search = TavilySearchResults(
            api_key=tavily_api_key,
            max_results=3,
            search_depth="basic",
            include_answer=True
        )
        
        # Führe Suche aus
        results = search.run(search_query)
        
        return f"🌐 Internet-Recherche zu '{search_query}':\n\n{results}"
        
    except Exception as e:
        return f"❌ Internet-Suche fehlgeschlagen: {str(e)}"


def extract_search_query(user_query: str, classification: str) -> str:
    """Erstellt optimierte Such-Query für Internet"""
    # Versuche Ort aus Klassifizierung zu extrahieren
    ort = None
    
    if "Ort/PLZ:" in classification:
        lines = classification.split("\n")
        for line in lines:
            if "Ort/PLZ:" in line:
                ort = line.split("Ort/PLZ:")[1].strip().replace("[", "").replace("]", "")
                break
    
    # Erstelle Such-Query
    if ort and ort.lower() not in ["keine", "nicht vorhanden", "k.a."]:
        return f"Autowerkstatt KFZ Werkstatt {ort} Bewertungen Empfehlung"
    else:
        # Fallback auf ursprüngliche Query
        return f"Autowerkstatt {user_query}"
