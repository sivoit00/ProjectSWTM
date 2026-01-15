import os
import requests
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger(__name__)

SERPAPI_KEY = os.environ.get("SERPAPI_KEY")
llm = ChatOpenAI(temperature=0.0, model="gpt-5.2") 

def extract_email_from_url(url: str) -> str:
    """
    Besucht eine URL, reinigt den HTML-Code und lässt eine KI nach der Kontakt-Email suchen.
    """
    if not url:
        return "Keine Website"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code != 200:
            return "Seite nicht erreichbar"
    
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for script in soup(["script", "style"]):
            script.extract()
            
        text_content = soup.get_text()[:4000]
        
        extraction_prompt = f"""
        Suche im folgenden Text nach einer Kontakt-Email-Adresse für den Anwalt oder die Kanzlei.
        Gib NUR die E-Mail zurück. Wenn keine gefunden wird, antworte mit 'N/A'.
        
        Text:
        {text_content}
        """
        
        result = llm.invoke(extraction_prompt)
        return result.content.strip()

    except Exception as e:
        log.warning(f"Email Scraping Fehler bei {url}: {e}")
        return "N/A"


def search_google_maps(query: str, num_results: int = 3) -> List[Dict]:
    """
    Generische Funktion für SerpAPI Google Maps Suche + Email Scraping.
    Kann für Anwälte, Werkstätten, Ärzte etc. genutzt werden.
    """
    if not SERPAPI_KEY:
        return [{"error": "SERPAPI_KEY fehlt."}]

    url = "https://serpapi.com/search.json"
    params = {
        "engine": "google_maps", 
        "q": query, 
        "google_domain": "google.com", 
        "hl": "de", 
        "num": num_results, 
        "api_key": SERPAPI_KEY
    }
    
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        
        results = []
        local_results = data.get("local_results", [])
        
        if not local_results and "organic_results" in data:
             local_results = data.get("organic_results", [])[:num_results]

        for item in local_results:
            website_url = item.get("website")

            found_email = "Nicht gefunden"
            if website_url:
                found_email = extract_email_from_url(website_url)

            entry = {
                "name": item.get("title"),
                "email": found_email,
                "website": website_url,
                "telefon": item.get("phone") or "Keine Nummer",
                "anschrift": item.get("address") or "Keine Adresse",
                "bewertung": item.get("rating") or "Keine Bewertung",
                "reviews": item.get("reviews") or 0
            }
            results.append(entry)
            
        return results

    except Exception as e:
        log.error(f"Google Search Fehler: {e}")
        return []