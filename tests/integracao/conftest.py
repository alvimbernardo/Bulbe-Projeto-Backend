"""Fixtures dos testes de integracao com banco SQLite temporario."""

import pytest

from src.db.database import Base, criar_engine, criar_fabrica_de_sessoes
from src.db.seed import carregar_dados_de_exemplo


@pytest.fixture
def url_banco_teste(tmp_path) -> str:
    return f"sqlite:///{(tmp_path / 'bulbe_test.db').as_posix()}"


@pytest.fixture
def engine(url_banco_teste):
    engine = criar_engine(url_banco_teste)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def sessoes(engine):
    return criar_fabrica_de_sessoes(engine)


@pytest.fixture
def sessoes_com_dados(sessoes):
    carregar_dados_de_exemplo(sessoes)
    return sessoes
