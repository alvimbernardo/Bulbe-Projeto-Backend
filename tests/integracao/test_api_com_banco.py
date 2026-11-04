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


@pytest.fixture
def app_com_banco_e_chave(monkeypatch, app_com_banco):
    monkeypatch.setenv("BULBE_JWT_SECRET", "chave-de-teste-com-mais-de-32-bytes-bulbe")
    return app_com_banco


def _login(client, email="cliente01@exemplo.com", senha="Bulbe2026!") -> dict:
    resposta = client.post("/v1/sessoes", json={"email": email, "senha": senha})
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_jornada_do_cliente_com_banco(app_com_banco_e_chave):
    with TestClient(app_com_banco_e_chave()) as client:
        headers = _login(client)
        assert client.get("/v1/clientes/cliente_01", headers=headers).status_code == 200
        assert client.get("/v1/clientes/cliente_02", headers=headers).status_code == 403
        ativacao = client.get("/v1/clientes/cliente_01/ativacao", headers=headers).json()
        assert ativacao["percentual"] == 50
        faturas = client.get("/v1/clientes/cliente_01/faturas", headers=headers).json()
        assert [f["id"] for f in faturas["data"]] == ["fatura_02", "fatura_01"]
        pagamento = client.get("/v1/clientes/cliente_01/faturas/fatura_01/pagamento", headers=headers)
        assert pagamento.status_code == 200
        repasse = client.get("/v1/clientes/cliente_01/faturas/fatura_01/repasse", headers=headers)
        assert repasse.status_code == 200


def test_conta_criada_continua_existindo_depois_do_reinicio(app_com_banco_e_chave):
    cadastro = {
        "email": "cliente03@exemplo.com",
        "senha": "Senha12345",
        "identificador_cliente": "BULBE-003",
        "codigo_verificacao": "345678",
    }
    with TestClient(app_com_banco_e_chave()) as client:
        assert client.post("/v1/contas", json=cadastro).status_code == 201
    with TestClient(app_com_banco_e_chave()) as depois_do_reinicio:
        assert depois_do_reinicio.post("/v1/contas", json=cadastro).status_code == 409
        headers = _login(depois_do_reinicio, "cliente03@exemplo.com", "Senha12345")
        assert depois_do_reinicio.get("/v1/clientes/cliente_03", headers=headers).status_code == 200


def test_logout_continua_valendo_depois_do_reinicio(app_com_banco_e_chave):
    with TestClient(app_com_banco_e_chave()) as client:
        headers = _login(client)
        assert client.delete("/v1/sessoes/atual", headers=headers).status_code == 204
    with TestClient(app_com_banco_e_chave()) as depois_do_reinicio:
        assert depois_do_reinicio.get("/v1/clientes/cliente_01", headers=headers).status_code == 401


def test_preferencia_salva_continua_depois_do_reinicio(app_com_banco_e_chave):
    corpo = {"habilitada": True, "canais": ["email"]}
    rota = "/v1/clientes/cliente_01/preferencias-notificacao/ativacao"
    with TestClient(app_com_banco_e_chave()) as client:
        primeira = client.put(rota, json=corpo, headers=_login(client)).json()
    with TestClient(app_com_banco_e_chave()) as depois_do_reinicio:
        repetida = depois_do_reinicio.put(rota, json=corpo, headers=_login(depois_do_reinicio)).json()
    assert repetida == primeira
