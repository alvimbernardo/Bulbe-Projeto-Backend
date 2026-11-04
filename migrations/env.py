"""Ambiente do Alembic: usa o BULBE_DATABASE_URL e os modelos do projeto."""

import os
from logging.config import fileConfig

from alembic import context

from src.db import models  # noqa: F401
from src.db.database import Base, criar_engine

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

url = os.getenv("BULBE_DATABASE_URL") or config.get_main_option("sqlalchemy.url")
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    conexao_existente = config.attributes.get("connection")
    if conexao_existente is not None:
        _executar(conexao_existente)
        return
    engine = criar_engine(url)
    with engine.connect() as conexao:
        _executar(conexao)
    engine.dispose()


def _executar(conexao) -> None:
    context.configure(connection=conexao, target_metadata=target_metadata, render_as_batch=True)
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
