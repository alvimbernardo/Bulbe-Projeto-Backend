"""Ativacao HTTP autenticada, incluindo autorizacao antes da consulta."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.repositories.dados_contas import SENHA_EXEMPLO


def cabecalho(client, numero=1):
    resposta = client.post("/v1/sessoes", json={
        "email": f"cliente0{numero}@exemplo.com", "senha": SENHA_EXEMPLO,
    })
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_progresso_bate_com_etapas_e_tem_fuso_horario(client):
    headers = cabecalho(client)
    resposta = client.get("/v1/clientes/cliente_01/ativacao", headers=headers)
    assert resposta.status_code == 200
    corpo = resposta.json()
    etapas = client.get("/v1/clientes/cliente_01/ativacao/etapas", headers=headers)
    assert etapas.status_code == 200
    lista = etapas.json()
    assert corpo["cliente_id"] == lista["cliente_id"] == "cliente_01"
    assert corpo["status"] == "em_andamento"
    assert corpo["percentual"] == 50
    assert corpo["atualizado_em"] == lista["atualizado_em"]
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None
    assert [e["ordem"] for e in lista["data"]] == [1, 2, 3, 4]
    concluidas = sum(e["status"] == "concluida" for e in lista["data"])
    assert corpo["percentual"] == concluidas * 100 // len(lista["data"])
    atuais = [e["id"] for e in lista["data"] if e["status"] == "atual"]
    assert atuais == [corpo["etapa_atual_id"]]


def test_ativacao_concluida_sem_etapa_atual(client):
    headers = cabecalho(client, 2)
    resposta = client.get("/v1/clientes/cliente_02/ativacao", headers=headers)
    assert resposta.status_code == 200
    assert resposta.json()["percentual"] == 100
    assert resposta.json()["status"] == "concluida"
    assert resposta.json().get("etapa_atual_id") is None


@pytest.mark.parametrize("sufixo", ["", "/etapas"])
def test_sem_sessao_retorna_401_antes_de_consultar_servico(app, client, sufixo):
    service = Mock()
    app.state.ativacao_service = service
    resposta = client.get(f"/v1/clientes/cliente_01/ativacao{sufixo}")
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"
    assert not service.mock_calls


@pytest.mark.parametrize("sufixo", ["", "/etapas"])
def test_outro_cliente_retorna_403_antes_de_consultar_servico(app, client, sufixo):
    headers = cabecalho(client)
    service = Mock()
    app.state.ativacao_service = service
    resposta = client.get(f"/v1/clientes/cliente_02/ativacao{sufixo}", headers=headers)
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ACESSO_NEGADO"
    assert not service.mock_calls


@pytest.mark.parametrize("sufixo", ["", "/etapas"])
def test_cliente_sem_ativacao_retorna_404_explicito(client, sufixo):
    cadastro = client.post("/v1/contas", json={
        "email": "cliente03@exemplo.com", "senha": SENHA_EXEMPLO,
        "identificador_cliente": "BULBE-003", "codigo_verificacao": "345678",
    })
    assert cadastro.status_code == 201
    resposta = client.get(f"/v1/clientes/cliente_03/ativacao{sufixo}", headers=cabecalho(client, 3))
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"
