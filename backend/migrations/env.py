import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from database import DATABASE_URL, Base
from models.customer import Customer
from models.vehicle import Vehicle
from models.insurance import Insurance
from models.workshop import Workshop
from models.lawyer import Lawyer
from models.chat_conversation import ChatConversation
from models.chat_message import ChatMessage
from models.damage_event import DamageEvent
from models.guardrails_log import GuardrailsLog
from models.notifications import Notification

config = context.config

if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    raise ValueError("DATABASE_URL konnte nicht aus backend.database geladen werden!")

section = config.config_ini_section
config.set_section_option(section, "sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    # Ignoriere alle Tabellen, die mit 'langchain' beginnen
    if type_ == "table" and name.startswith("langchain"):
        return False
    return True

def run_migrations_online() -> None:

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            compare_type=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()