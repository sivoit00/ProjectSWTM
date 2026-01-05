from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Aasal22!!@db:5432/fahrzeugservice"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def ensure_chat_messages_schema():
    """Lightweight migration to support multi-chat threads.

    Adds chat_messages.conversation_id and an index if they are missing.
    Safe to call repeatedly.
    """
    inspector = inspect(engine)

    if "chat_messages" not in inspector.get_table_names():
        return

    existing_columns = {c.get("name") for c in inspector.get_columns("chat_messages")}
    with engine.begin() as conn:
        if "conversation_id" not in existing_columns:
            conn.execute(
                text(
                    "ALTER TABLE chat_messages "
                    "ADD COLUMN conversation_id VARCHAR NOT NULL DEFAULT 'default'"
                )
            )

        conn.execute(
            text(
                "CREATE INDEX IF NOT EXISTS ix_chat_messages_user_conv "
                "ON chat_messages (user_id, conversation_id)"
            )
        )


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# NOTE: If you want a local SQLite fallback for development, you can use:
# SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
