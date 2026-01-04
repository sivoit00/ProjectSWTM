import logging
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
import services.pgvector_instance  

load_dotenv()
log = logging.getLogger(__name__)

# Basisverzeichnis des Backends (.. / .. von agents/tools)
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))




def search_vector_db(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
    """Search the PGVector database and return top-k matches with scores.

    This tool intentionally does *retrieval only* (no second LLM call / synthesis),
    because the Repair-Agent already performs the final answer generation.

    Returns a list of dicts containing: id, metadata, page_content, score.
    """

    try:
        db = services.pgvector_instance.get()
    except Exception as e:
        log.error(f"Vector DB fetch failed: {e}")
        return [{"error": f"Vector DB fetch failed: {e}"}]

    
    query_text = query
    try:
        base_uploads = os.path.abspath(os.path.join(BACKEND_DIR, "uploads"))
        if isinstance(query, str) and query.endswith(('.txt', '.md', '.pdf')):
            candidate_path = os.path.join(base_uploads, query)
            if os.path.exists(candidate_path):
                with open(candidate_path, 'r', encoding='utf-8', errors='ignore') as f:
                    query_text = f.read()[:4000]
    except Exception as e:
        log.warning(f"Filename-based query handling failed: {e}")

    try:
        results = db.similarity_search_with_score(query_text, k=top_k)
    except Exception as e:
        log.error(f"Vector similarity search failed: {e}")
        return [{"error": f"Vector similarity search failed: {e}"}]

    formatted: List[Dict[str, Any]] = []   
    for doc, score in results:
        print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")
        formatted.append(
            {
                "id": getattr(doc, "id", None),
                "metadata": getattr(doc, "metadata", {}),
                "page_content": getattr(doc, "page_content", ""),
                "score": float(score),
            }
        )

    return formatted

    




