"""Fluxos HTTP de login, validacao e logout com dados ficticios."""

from datetime import datetime, timezone
import json

import pytest


def login(client):
    resposta = client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "Bulbe2026!"})
    assert resposta.status_code == 201
    return resposta


def test_login_retorna_sessao_e_token_sem_expor_credenciais(client):
    resposta = login(client)
    corpo = resposta.json()
    assert set(corpo) == {"sessao_id", "conta_id", "cliente_id", "expira_em", "access_token", "token_type"}
    assert corpo["cliente_id"] == "cliente_01"
    assert corpo["conta_id"] == "conta_01"
    assert corpo["token_type"] == "bearer"
    assert len(corpo["access_token"].split(".")) == 3
    assert datetime.fromisoformat(corpo["expira_em"]).utcoffset() is not None
    assert resposta.headers["cache-control"] == "no-store"
    assert "Bulbe2026!" not in resposta.text


def test_logout_retorna_204_sem_corpo_e_token_nao_pode_ser_reutilizado(client):
    token = login(client).json()["access_token"]
    cabecalhos = {"Authorization": f"Bearer {token}"}
    resposta = client.delete("/v1/sessoes/atual", headers=cabecalhos)
    assert resposta.status_code == 204
    assert resposta.content == b""
    resposta = client.delete("/v1/sessoes/atual", headers=cabecalhos)
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"


@pytest.mark.parametrize("cabecalho", [None, "Bearer invalido", "Basic abc", "Bearer"])
def test_logout_exige_bearer_valido(client, cabecalho):
    headers = {} if cabecalho is None else {"Authorization": cabecalho}
    headers["X-Request-ID"] = "req_sessao"
    resposta = client.delete("/v1/sessoes/atual", headers=headers)
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"
    assert resposta.json()["request_id"] == "req_sessao"


@pytest.mark.parametrize("email", ["cliente01@exemplo.com", "ausente@exemplo.com"])
def test_credenciais_invalidas_nao_revelam_existencia_da_conta(client, email):
    resposta = client.post("/v1/sessoes", json={"email": email, "senha": "incorreta"})
    assert resposta.status_code == 401
    assert resposta.json()["mensagem"] == "Credenciais invalidas."


@pytest.mark.parametrize("corpo", [
    {}, {"email": "cliente01@exemplo.com"}, {"email": "invalido", "senha": "x"},
    {"email": "cliente01@exemplo.com", "senha": ""},
    {"email": "cliente01@exemplo.com", "senha": "a" * 73},
    {"email": "cliente01@exemplo.com", "senha": "á" * 37},
    {"email": "cliente01@exemplo.com", "senha": "\ud800"},
])
def test_entrada_invalida_retorna_400_sem_expor_senha(client, corpo):
    resposta = client.post("/v1/sessoes", content=json.dumps(corpo), headers={"Content-Type": "application/json"})
    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "REQUISICAO_INVALIDA"
    assert set(resposta.json()) == {"codigo", "mensagem", "detalhes", "request_id"}


def test_tentativas_repetidas_retornam_429_antes_de_validar_credencial(client):
    for _ in range(5):
        assert client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "errada"}).status_code == 401
    resposta = client.post("/v1/sessoes", json={"email": "CLIENTE01@EXEMPLO.COM", "senha": "Bulbe2026!"})
    assert resposta.status_code == 429
    assert resposta.json()["codigo"] == "MUITAS_TENTATIVAS"


def test_sessao_expirada_retorna_401_sem_esperar(app, client, monkeypatch):
    tokens = app.state.sessao_service._tokens
    agora = [datetime.now(timezone.utc).replace(microsecond=0)]
    monkeypatch.setattr(tokens, "_relogio", lambda: agora[0])
    token = login(client).json()["access_token"]
    agora[0] += tokens.duracao
    resposta = client.delete("/v1/sessoes/atual", headers={"Authorization": f"Bearer {token}"})
    assert resposta.status_code == 401
