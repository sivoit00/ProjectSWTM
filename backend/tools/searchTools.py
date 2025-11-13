from typing import List, Dict

DUMMY_LAWYERS = [
    {"name": "Kanzlei Müller", "city": "München", "specialties": ["Verkehrsrecht", "Schadensersatz"], "phone": "089-1234"},
    {"name": "Rechtsanwalt Schmid", "city": "München", "specialties": ["Verkehrsrecht"], "phone": "089-5678"},
    {"name": "Kanzlei Becker", "city": "Berlin", "specialties": ["Familienrecht"], "phone": "030-1111"},
    {"name": "Kanzlei Hoffmann", "city": "Hamburg", "specialties": ["Verkehrsrecht"], "phone": "040-2222"},
]

def search_lawyers_by_city(city: str, topic: str, max_results: int = 3) -> List[Dict]:
    city = city.lower().strip()
    topic = topic.lower().strip()
    results = []
    for entry in DUMMY_LAWYERS:
        if entry["city"].lower() == city and any(topic in s.lower() for s in entry["specialties"]):
            results.append(entry)
    return results[:max_results]
