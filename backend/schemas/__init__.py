from .kunde_schema import KundeBase, KundeCreate, Kunde
from .fahrzeug_schema import FahrzeugBase, FahrzeugCreate, Fahrzeug
from .werkstatt_schema import WerkstattBase, WerkstattCreate, Werkstatt
from .auftrag_schema import AuftragBase, AuftragCreate, Auftrag
from .ki_aktion_schema import KIAktionCreate, KIAktionSchema
from .rechtsanwalt_schema import Rechtsanwalt, RechtsanwaltCreate
from .versicherung_schema import Versicherung, VersicherungCreate

__all__ = [
    "KundeBase", "KundeCreate", "Kunde",
    "FahrzeugBase", "FahrzeugCreate", "Fahrzeug",
    "WerkstattBase", "WerkstattCreate", "Werkstatt",
    "AuftragBase", "AuftragCreate", "Auftrag",
    "KIAktionCreate", "KIAktionSchema",
    "Rechtsanwalt", "RechtsanwaltCreate",
    "Versicherung", "VersicherungCreate"
]
