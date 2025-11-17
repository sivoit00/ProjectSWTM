from database import Base
from .kunde import Kunde
from .fahrzeug import Fahrzeug
from .werkstatt import Werkstatt
from .auftrag import Auftrag
from .ki_aktion import KIAktion

__all__ = ["Base", "Kunde", "Fahrzeug", "Werkstatt", "Auftrag", "KIAktion"]
