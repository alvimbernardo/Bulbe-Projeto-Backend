"""Historico e preferencias passam pela autenticacao e autorizacao reais."""

import pytest




def login(client):
    resposta = client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "Bulbe2026!"})
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_preferencia_put_idempotente_e_isolada_por_cliente(client):
    headers = login(client)
    rota = "/v1/clientes/cliente_01/preferencias-notificacao/ativacao"
    resposta = client.put(rota, json={"habilitada": True, "canais": ["email"]}, headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["tipo"] == "ativacao"
    assert client.put(rota, json={"habilitada": True, "canais": ["email"]}, headers=headers).json() == resposta.json()
    assert client.put(rota, json={"habilitada": False, "canais": []}, headers=headers).json()["habilitada"] is False
    assert client.put(rota.replace("cliente_01", "cliente_02"), json={"habilitada": True, "canais": ["email"]}, headers=headers).status_code == 403


@pytest.mark.parametrize("corpo,status", [
    ({"habilitada": True, "canais": ["sms"]}, 422),
    ({"habilitada": True, "canais": []}, 422),
    ({"habilitada": "sim", "canais": ["email"]}, 400),
    ({"habilitada": True}, 400),
])
def test_preferencia_valida_entrada_e_canais(client, corpo, status):
    resposta = client.put("/v1/clientes/cliente_01/preferencias-notificacao/ativacao", json=corpo, headers=login(client))
    assert resposta.status_code == status
    assert set(resposta.json()) == {"codigo", "mensagem", "detalhes", "request_id"}


def test_preferencia_sem_login_e_401(client):
    resposta = client.put("/v1/clientes/cliente_01/preferencias-notificacao/ativacao", json={"habilitada": True, "canais": ["email"]})
    assert resposta.status_code == 401


