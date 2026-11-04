"""Testes das migrations do Alembic."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from src.db.database import criar_engine

RAIZ = Path(__file__).resolve().parents[2]
TABELAS = {
    "usinas", "creditos_usinas", "depoimentos", "clientes", "contas", "sessoes", "ativacoes",
    "etapas_ativacao", "faturas", "pagamentos", "repasses", "etapas_repasse", "preferencias_notificacao",
}


def _config(monkeypatch, url: str) -> Config:
    monkeypatch.setenv("BULBE_DATABASE_URL", url)
    config = Config(str(RAIZ / "alembic.ini"))
    config.set_main_option("script_location", str(RAIZ / "migrations"))
    return config


def test_upgrade_head_cria_as_tabelas(monkeypatch, url_banco_teste):
    command.upgrade(_config(monkeypatch, url_banco_teste), "head")
    engine = criar_engine(url_banco_teste)
    tabelas = set(inspect(engine).get_table_names())
    engine.dispose()
    assert TABELAS | {"alembic_version"} <= tabelas


def test_downgrade_base_remove_as_tabelas(monkeypatch, url_banco_teste):
    config = _config(monkeypatch, url_banco_teste)
    command.upgrade(config, "head")
    command.downgrade(config, "base")
    engine = criar_engine(url_banco_teste)
    tabelas = set(inspect(engine).get_table_names())
    engine.dispose()
    assert not TABELAS & tabelas
