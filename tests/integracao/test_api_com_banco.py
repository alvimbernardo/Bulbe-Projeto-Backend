"""Testes da API com os repositorios SQL ligados a um banco de teste."""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def app_com_banco(monkeypatch, url_banco_teste, sessoes_com_dados):
    monkeypatch.setenv("BULBE_PERSISTENCIA", "banco")
    monkeypatch.setenv("BULBE_DATABASE_URL", url_banco_teste)
    return create_app


def test_listagem_de_usinas_vem_do_banco(app_com_banco):
    with TestClient(app_com_banco()) as client:
        resposta = client.get("/v1/usinas")
    assert resposta.status_code == 200
    assert [u["id"] for u in resposta.json()["data"]] == ["usina_01", "usina_02"]


def test_resumo_de_agosto_calculado_com_dados_do_banco(app_com_banco):
    with TestClient(app_com_banco()) as client:
        resposta = client.get("/v1/creditos-usinas/resumo", params={"competencia": "2026-08"})
    assert resposta.status_code == 200
    assert resposta.json()["total_creditos"] == {"valor": 74096.15, "moeda": "BRL"}


def test_depoimento_nao_autorizado_continua_404_com_banco(app_com_banco):
    with TestClient(app_com_banco()) as client:
        assert client.get("/v1/depoimentos/depoimento_03").status_code == 404
        assert client.get("/v1/depoimentos/depoimento_01").status_code == 200


def test_dados_sobrevivem_ao_reinicio_da_aplicacao(app_com_banco):
    with TestClient(app_com_banco()) as primeira:
        antes = primeira.get("/v1/usinas/usina_02").json()
    with TestClient(app_com_banco()) as depois_do_reinicio:
        resposta = depois_do_reinicio.get("/v1/usinas/usina_02")
    assert resposta.status_code == 200
    assert resposta.json() == antes
