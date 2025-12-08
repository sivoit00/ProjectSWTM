import logging
from pathlib import Path

from dotenv import load_dotenv
from pydantic.v1 import BaseSettings

logging.basicConfig(level=logging.INFO)
logging.getLogger('httpx').setLevel(logging.WARNING)

load_dotenv()


class Settings(BaseSettings):
    OPENAI_API_KEY: str

    project_root = Path(__file__).parent
    
    DOCUMENTS_PATH: str = str(project_root / "uploads")

   
    DATABASE_SCHEMA: str = "postgresql+psycopg"
    DATABASE_HOST: str = "projectswtm.c9gqueuwynyt.eu-north-1.rds.amazonaws.com" 
    DATABASE_PORT: int = 5432          
    DATABASE_USER: str = "postgres"    
    DATABASE_PASSWORD: str = "Aasal22!!"  
    DATABASE_NAME: str = "fahrzeugservice"    
    DATABASE_SSLMODE: str = "require" 
    DATABASE_OPTIONS: str = ""         
    EMBEDDING_COLLECTION_NAME: str = "documents"


    @property
    def DATABASE_URI(self) -> str:
            base = f"{self.DATABASE_SCHEMA}://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
            params = []
            if self.DATABASE_SSLMODE:
                params.append(f"sslmode={self.DATABASE_SSLMODE}")
            if self.DATABASE_OPTIONS:
                params.append(self.DATABASE_OPTIONS)
            return base + ("?" + "&".join(params) if params else "")


settings = Settings()