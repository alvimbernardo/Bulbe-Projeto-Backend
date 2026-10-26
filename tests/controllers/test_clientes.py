"""HTTP da US04 com sessao real."""

import pytest


def login(client):
    resposta = client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "Bulbe2026!"})
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_cliente_proprio_tem_somente_campos_publicos(client):
    resposta = client.get("/v1/clientes/cliente_01", headers=login(client))
    assert resposta.status_code == 200
    assert set(resposta.json()) == {"id", "nome_exibicao", "email", "status"}
    assert resposta.json()["id"] == "cliente_01"


@pytest.mark.parametrize("cliente_id", ["cliente_02", "inexistente"])
def test_outro_cliente_e_403_mesmo_inexistente(client, cliente_id):
    resposta = client.get(f"/v1/clientes/{cliente_id}", headers=login(client))
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ACESSO_NEGADO"


@pytest.mark.parametrize("autorizacao", [None, "Bearer falso", "Basic abc", "Bearer"])
def test_cliente_sem_sessao_valida_e_401(client, autorizacao):
    headers = {} if autorizacao is None else {"Authorization": autorizacao}
    resposta = client.get("/v1/clientes/cliente_01", headers=headers)
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"


def test_logout_impede_acesso_ao_cliente(client):
    headers = login(client)
    assert client.delete("/v1/sessoes/atual", headers=headers).status_code == 204
    assert client.get("/v1/clientes/cliente_01", headers=headers).status_code == 401
