"""Conexao com o banco: engine, fabrica de sessoes e classe base dos modelos."""

import os

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

URL_PADRAO = "sqlite:///./bulbe.db"


class Base(DeclarativeBase):
    pass


def url_do_banco() -> str:
    return os.getenv("BULBE_DATABASE_URL", URL_PADRAO)


def persistencia_em_banco() -> bool:
    return os.getenv("BULBE_PERSISTENCIA", "banco").strip().casefold() == "banco"


def criar_engine(url: str | None = None) -> Engine:
    url = url or url_do_banco()
    if not url.startswith("sqlite"):
        return create_engine(url)
    engine = create_engine(url, connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _ativar_chaves_estrangeiras(conexao, _registro) -> None:
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def criar_fabrica_de_sessoes(engine: Engine) -> sessionmaker:
    return sessionmaker(bind=engine, expire_on_commit=False)
