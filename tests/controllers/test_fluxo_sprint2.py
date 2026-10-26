"""Jornada integrada: cadastro, sessao, area individual e logout."""

import json

import pytest


def test_cliente_cria_conta_acessa_proprios_dados_e_sai(client):
    corpo = {"email": "cliente03@exemplo.com", "senha": "MinhaSenha2026!",
             "identificador_cliente": "BULBE-003", "codigo_verificacao": "345678"}
    assert client.post("/v1/contas", json=corpo).status_code == 201
    assert client.post("/v1/contas", json=corpo).status_code == 409
    resposta = client.post("/v1/sessoes", json={"email": corpo["email"], "senha": corpo["senha"]})
    assert resposta.status_code == 201
    headers = {"Authorization": f"Bearer {resposta.json()['access_token']}"}
    assert client.get("/v1/clientes/cliente_03", headers=headers).status_code == 200
    assert client.get("/v1/clientes/cliente_01/faturas", headers=headers).status_code == 403
    assert client.get("/v1/clientes/cliente_03/ativacao", headers=headers).status_code == 404
    faturas = client.get("/v1/clientes/cliente_03/faturas", headers=headers)
    assert faturas.status_code == 200 and faturas.json()["data"] == []
    assert client.delete("/v1/sessoes/atual", headers=headers).status_code == 204
    assert client.get("/v1/clientes/cliente_03", headers=headers).status_code == 401


@pytest.mark.parametrize("campo", ["senha", "email", "codigo_verificacao"])
def test_cadastro_rejeita_unicode_invalido_sem_erro_500(client, campo):
    corpo = {"email": "cliente03@exemplo.com", "senha": "MinhaSenha2026!",
             "identificador_cliente": "BULBE-003", "codigo_verificacao": "345678"}
    corpo[campo] = ("abcdefgh" if campo == "senha" else "") + "\ud800"
    resposta = client.post("/v1/contas", content=json.dumps(corpo), headers={"Content-Type": "application/json"})
    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "REQUISICAO_INVALIDA"
