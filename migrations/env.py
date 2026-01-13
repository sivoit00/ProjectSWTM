import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# 1. DOTENV LADEN
from dotenv import load_dotenv
load_dotenv()

# 2. MODELLE IMPORTIEREN
# WICHTIG: Ersetze 'app.database' durch den Pfad, wo deine 'Base' liegt
# Ersetze 'Base' durch den Namen deiner deklarativen Basis
from app.database import Base 

config = context.config

# 3. DB-URL AUS .ENV SETZEN
# Wir überschreiben den Wert aus der alembic.ini mit dem aus der .env
section = config.config_ini_section
config.set_section_option(section, "sqlalchemy.url", os.getenv("DATABASE_URL"))

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Hier die Metadaten deiner Modelle übergeben
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    # Hier wird die URL genutzt, die wir oben per os.getenv gesetzt haben
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            # Sorgt dafür, dass Alembic auch Schema-Änderungen erkennt
            compare_type=True 
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()