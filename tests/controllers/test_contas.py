"""Cadastro via HTTP; main compoe os repositorios e o ContaService."""

import pytest

CORPO_VALIDO = {
    "email": "cliente03@exemplo.com", "senha": "Bulbe2026!",
    "identificador_cliente": "BULBE-003", "codigo_verificacao": "345678",
}


def test_cadastro_http_responde_201_sem_hash_ou_dados_privados(client):
    resposta = client.post("/v1/contas", json=CORPO_VALIDO)
    assert resposta.status_code == 201
    conta = resposta.json()
    assert set(conta) == {"id", "cliente_id", "email", "status", "criada_em"}
    assert conta["cliente_id"] == "cliente_03"
    assert conta["status"] == "ativa"
    repetida = client.post("/v1/contas", json=CORPO_VALIDO)
    assert repetida.status_code == 409
    assert repetida.json()["codigo"] == "CONTA_JA_EXISTENTE"


@pytest.mark.parametrize("alteracoes", [
    {"senha": "curta"}, {"senha": "á" * 40}, {"email": "invalido"},
    {"email": None}, {"identificador_cliente": "   "},
])
def test_cadastro_http_campos_invalidos_retorna_400(client, alteracoes):
    resposta = client.post("/v1/contas", json={**CORPO_VALIDO, **alteracoes})
    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "REQUISICAO_INVALIDA"


@pytest.mark.parametrize("campo", ["email", "senha", "identificador_cliente"])
def test_cadastro_http_campo_obrigatorio_ausente_retorna_400(client, campo):
    corpo = {k: v for k, v in CORPO_VALIDO.items() if k != campo}
    resposta = client.post("/v1/contas", json=corpo)
    assert resposta.status_code == 400
    assert resposta.json()["detalhes"][0]["campo"] == campo


def test_codigo_ausente_retorna_422_de_negocio(client):
    corpo = {k: v for k, v in CORPO_VALIDO.items() if k != "codigo_verificacao"}
    resposta = client.post("/v1/contas", json=corpo, headers={"X-Request-ID": "req_cadastro"})
    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "CLIENTE_INELEGIVEL"
    assert resposta.json()["request_id"] == "req_cadastro"
