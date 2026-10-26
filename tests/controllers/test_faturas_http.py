"""Rotas privadas das US10/US13: autenticacao, propriedade e serializacao."""

from datetime import datetime

import pytest

from src.repositories.dados_faturas import faturas_exemplo
from src.repositories.fatura_repository import InMemoryFaturaRepository
from src.repositories.pagamento_repository import InMemoryPagamentoRepository
from src.repositories.repasse_repository import InMemoryRepasseRepository
from src.services.fatura_service import FaturaService


@pytest.fixture
def sessao_cliente1(client):
    resposta = client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "Bulbe2026!"})
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


ROTAS = ["", "/fatura_01", "/fatura_01/pagamento", "/fatura_01/repasse"]


@pytest.mark.parametrize("sufixo", ROTAS)
def test_faturas_exigem_sessao(client, sufixo):
    resposta = client.get(f"/v1/clientes/cliente_01/faturas{sufixo}")
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "NAO_AUTENTICADO"


@pytest.mark.parametrize("sufixo", ROTAS)
def test_faturas_de_outro_cliente_na_url_retornam_403(client, sessao_cliente1, sufixo):
    resposta = client.get(f"/v1/clientes/cliente_02/faturas{sufixo}", headers=sessao_cliente1)
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ACESSO_NEGADO"


@pytest.mark.parametrize("sufixo", ["", "/pagamento", "/repasse"])
def test_id_de_fatura_de_outro_cliente_e_ocultado(client, sessao_cliente1, sufixo):
    resposta = client.get(f"/v1/clientes/cliente_01/faturas/fatura_03{sufixo}", headers=sessao_cliente1)
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_lista_faturas_filtra_competencia_e_pagina_sem_misturar_clientes(client, sessao_cliente1):
    rota = "/v1/clientes/cliente_01/faturas"
    resposta = client.get(rota, params={"page": 2, "limit": 1}, headers=sessao_cliente1)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert (corpo["page"], corpo["limit"], corpo["total"]) == (2, 1, 2)
    assert [f["id"] for f in corpo["data"]] == ["fatura_01"]
    assert set(corpo["data"][0]) == {"id", "identificador_exibivel", "competencia", "valor", "status"}
    filtrada = client.get(rota, params={"competencia": "2026-09"}, headers=sessao_cliente1)
    assert filtrada.status_code == 200
    assert [f["id"] for f in filtrada.json()["data"]] == ["fatura_02"]
    vazia = client.get(rota, params={"competencia": "2026-10"}, headers=sessao_cliente1)
    assert vazia.status_code == 200
    assert vazia.json() == {"data": [], "page": 1, "limit": 20, "total": 0, "atualizado_em": None}


@pytest.mark.parametrize("parametros,campo", [
    ({"competencia": "2026-13"}, "competencia"), ({"competencia": "0000-01"}, "competencia"),
    ({"competencia": ""}, "competencia"), ({"page": 0}, "page"), ({"limit": 101}, "limit"),
])
def test_parametros_invalidos_retornam_400_padronizado(client, sessao_cliente1, parametros, campo):
    resposta = client.get("/v1/clientes/cliente_01/faturas", params=parametros, headers=sessao_cliente1)
    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "REQUISICAO_INVALIDA"
    assert resposta.json()["detalhes"][0]["campo"] == campo


def test_detalhe_da_fatura_serializa_valor_numerico_e_datas(client, sessao_cliente1):
    resposta = client.get("/v1/clientes/cliente_01/faturas/fatura_01", headers=sessao_cliente1)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["cliente_id"] == "cliente_01"
    assert corpo["competencia"] == "2026-08"
    assert corpo["valor"] == {"valor": 89.9, "moeda": "BRL"}
    assert corpo["status"] == "paga"
    assert corpo["vencimento"] == "2026-08-15"
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None


def test_pagamento_confirmado_e_pendente(client, sessao_cliente1):
    resposta = client.get("/v1/clientes/cliente_01/faturas/fatura_01/pagamento", headers=sessao_cliente1)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "confirmado"
    assert corpo["forma"] == "pix"
    assert corpo["valor"] == {"valor": 89.9, "moeda": "BRL"}
    assert datetime.fromisoformat(corpo["pago_em"]).utcoffset() is not None
    pendente = client.get("/v1/clientes/cliente_01/faturas/fatura_02/pagamento", headers=sessao_cliente1)
    assert pendente.status_code == 200
    assert pendente.json()["status"] == "pendente"
    assert "pago_em" not in pendente.json()


def test_pagamento_recusado_nao_e_ausente(client):
    login = client.post("/v1/sessoes", json={"email": "cliente02@exemplo.com", "senha": "Bulbe2026!"})
    assert login.status_code == 201
    resposta = client.get("/v1/clientes/cliente_02/faturas/fatura_03/pagamento", headers={
        "Authorization": f"Bearer {login.json()['access_token']}",
    })
    assert resposta.status_code == 200
    assert resposta.json()["status"] == "recusado"


def test_pagamento_ausente_e_repasse_ausente_retornam_404(app, client, sessao_cliente1):
    app.state.fatura_service = FaturaService(
        InMemoryFaturaRepository(faturas_exemplo()), InMemoryPagamentoRepository(), InMemoryRepasseRepository(),
    )
    for recurso in ("pagamento", "repasse"):
        resposta = client.get(f"/v1/clientes/cliente_01/faturas/fatura_01/{recurso}", headers=sessao_cliente1)
        assert resposta.status_code == 404
        assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_repasse_exibe_etapas_ordenadas_e_sem_previsao_em_concluidas(client, sessao_cliente1):
    resposta = client.get("/v1/clientes/cliente_01/faturas/fatura_01/repasse", headers=sessao_cliente1)
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["fatura_id"] == "fatura_01"
    assert corpo["status"] == "em_andamento"
    assert [e["ordem"] for e in corpo["etapas"]] == [1, 2, 3]
    assert [e["status"] for e in corpo["etapas"]] == ["concluida", "atual", "pendente"]
    assert corpo["etapas"][0]["ocorrido_em"] is not None
    assert corpo["etapas"][0]["previsao"] is None
    assert corpo["etapas"][1]["previsao"] == "2026-08-18"
