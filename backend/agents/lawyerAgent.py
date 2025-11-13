from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI
from tools.searchTools import search_lawyers_by_city
from typing import Dict, Any

search_city_tool = Tool(
    name="search_lawyers_by_city",
    func=lambda q: search_lawyers_by_city(**q),
    description="Suche Anwälte in einer Stadt. Erwartet dict: {'city': str, 'topic': str, 'max_results': int}."
)

TOOLS = [search_city_tool]
llm = OpenAI(temperature=0.0)

agent = initialize_agent(
    TOOLS,
    llm,
    agent="zero-shot-react-description",
    verbose=False
)

def find_lawyers(request: Dict[str, Any]) -> Dict[str, Any]:
    """Wrapper-Funktion, damit FastAPI den Agent einfach nutzen kann."""
    city = request.get("city", "")
    topic = request.get("topic", "Verkehrsrecht")
    max_results = int(request.get("max_results", 3))
    results = search_lawyers_by_city(city, topic, max_results)
    return {"query": {"city": city, "topic": topic}, "results": results}
