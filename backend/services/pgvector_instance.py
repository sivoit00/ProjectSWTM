
from services.config import settings
from langchain_openai import OpenAIEmbeddings
from langchain_postgres.vectorstores import PGVector


_db_instance = None

def get():
    global _db_instance
    if _db_instance is None:
        connection_string = settings.DATABASE_URI
        collection_name = settings.EMBEDDING_COLLECTION_NAME 
        embeddings = OpenAIEmbeddings()
        _db_instance = PGVector(
            connection=connection_string,
            embeddings=embeddings,
            collection_name=collection_name,
            use_jsonb=True,
        )
    return _db_instance