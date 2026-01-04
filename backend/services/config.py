import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    # backend/services
    project_root = Path(__file__).parent

    # Einheitlicher Upload-/Dokumentenpfad: backend/uploads
    DOCUMENTS_PATH: str = str(project_root.parent / "uploads")


    # DB configuration is read from environment/.env via BaseSettings.
    # Keep only non-secret defaults here; credentials must not be hardcoded.
    DATABASE_SCHEMA: str = "postgresql+psycopg"
    DATABASE_HOST: str
    DATABASE_PORT: int = 5432
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    DATABASE_SSLMODE: str = "require"
    DATABASE_OPTIONS: str = ""
    EMBEDDING_COLLECTION_NAME: str = "documents"


    @property
    def DATABASE_URI(self) -> str:
        base = (
            f"{self.DATABASE_SCHEMA}://"
            f"{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )
        params = []
        if self.DATABASE_SSLMODE:
            params.append(f"sslmode={self.DATABASE_SSLMODE}")
        if self.DATABASE_OPTIONS:
            params.append(self.DATABASE_OPTIONS)
        return base + ("?" + "&".join(params) if params else "")


settings = Settings()