"""Fluxo HTTP completo das US06, US07, US08 e US11."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.controllers.dependencias import obter_depoimento_service, obter_usina_service
from src.domain.depoimento import Depoimento
from src.domain.erros import FonteIndisponivel
from src.repositories.credito_usina_repository import InMemoryCreditoUsinaRepository
from src.repositories.depoimento_repository import InMemoryDepoimentoRepository
from src.repositories.usina_repository import InMemoryUsinaRepository
from src.services.credito_service import CreditoService
from src.services.depoimento_service import DepoimentoService
from src.services.usina_service import UsinaService


def test_lista_usinas_ativas_com_paginacao_e_apenas_campos_do_resumo(client):
    resposta = client.get("/v1/usinas")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert (corpo["page"], corpo["limit"], corpo["total"]) == (1, 20, 2)
    assert [u["id"] for u in corpo["data"]] == ["usina_01", "usina_02"]
    assert all(u["status"] == "ativa" for u in corpo["data"])
    assert set(corpo["data"][0]) == {"id", "nome", "cidade", "estado", "status"}
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None


@pytest.mark.parametrize("status,usina_id", [("inativa", "usina_04"), ("em_manutencao", "usina_03")])
def test_filtro_de_usinas_por_status(client, status, usina_id):
    resposta = client.get("/v1/usinas", params={"status": status})
    assert resposta.status_code == 200
    assert [u["id"] for u in resposta.json()["data"]] == [usina_id]


@pytest.mark.parametrize("rota", ["/v1/usinas", "/v1/depoimentos"])
def test_paginacao_preserva_total_e_retorna_pagina_vazia(client, rota):
    segunda = client.get(rota, params={"page": 2, "limit": 1}).json()
    assert (segunda["page"], segunda["limit"], segunda["total"]) == (2, 1, 2)
    assert segunda["data"][0]["id"].endswith("02")
    vazia = client.get(rota, params={"page": 3, "limit": 1})
    assert vazia.status_code == 200
    assert vazia.json()["data"] == []
    assert vazia.json()["total"] == 2


@pytest.mark.parametrize("rota", ["/v1/usinas", "/v1/depoimentos"])
@pytest.mark.parametrize("parametros,campo", [
    ({"page": 0}, "page"), ({"page": "abc"}, "page"),
    ({"limit": 0}, "limit"), ({"limit": 101}, "limit"), ({"limit": "abc"}, "limit"),
])
def test_paginacao_invalida_retorna_400_padronizado(client, rota, parametros, campo):
    resposta = client.get(rota, params=parametros, headers={"X-Request-ID": "req_pagina"})
    assert resposta.status_code == 400
    corpo = resposta.json()
    assert set(corpo) == {"codigo", "mensagem", "detalhes", "request_id"}
    assert corpo["codigo"] == "REQUISICAO_INVALIDA"
    assert corpo["detalhes"][0]["campo"] == campo
    assert corpo["request_id"] == "req_pagina"


def test_detalhes_da_usina_incluem_regiao_e_atualizado_em(client):
    resposta = client.get("/v1/usinas/usina_04")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["status"] == "inativa"
    assert corpo["regiao"] == "Norte de Minas"
    assert "atualizada_em" not in corpo
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None


@pytest.mark.parametrize("rota", [
    "/v1/usinas/ausente", "/v1/usinas/ausente/creditos?competencia=2026-08",
    "/v1/usinas/usina_01/creditos?competencia=2026-09",
    "/v1/depoimentos/ausente", "/v1/depoimentos/depoimento_03",
])
def test_recursos_ausentes_ou_nao_autorizados_retornam_404(client, rota):
    resposta = client.get(rota, headers={"X-Request-ID": "req_ausente"})
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"
    assert resposta.json()["request_id"] == "req_ausente"


@pytest.mark.parametrize("competencia,valor", [("2026-07", 41250.00), ("2026-08", 43980.75)])
def test_creditos_serializam_competencia_e_dinheiro_como_numero(client, competencia, valor):
    resposta = client.get("/v1/usinas/usina_01/creditos", params={"competencia": competencia})
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["usina_id"] == "usina_01"
    assert corpo["competencia"] == competencia
    assert corpo["creditos"] == {"valor": valor, "moeda": "BRL"}
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None


@pytest.mark.parametrize("rota", ["/v1/usinas/usina_01/creditos", "/v1/creditos-usinas/resumo"])
@pytest.mark.parametrize("competencia", [None, "", "2026-8", "08-2026", "2026-00", "2026-13", "0000-08"])
def test_competencia_ausente_ou_invalida_retorna_400(client, rota, competencia):
    parametros = {} if competencia is None else {"competencia": competencia}
    resposta = client.get(rota, params=parametros)
    assert resposta.status_code == 400
    assert resposta.json()["codigo"] == "REQUISICAO_INVALIDA"
    assert resposta.json()["detalhes"][0]["campo"] == "competencia"


@pytest.mark.parametrize("parametros,campo", [
    ({"status": "desligada"}, "status"), ({"status": ""}, "status"),
    ({"competencia": "2026-08", "status_usina": "desligada"}, "status_usina"),
])
def test_filtros_invalidos_retornam_400(client, parametros, campo):
    rota = "/v1/usinas" if campo == "status" else "/v1/creditos-usinas/resumo"
    resposta = client.get(rota, params=parametros)
    assert resposta.status_code == 400
    assert resposta.json()["detalhes"][0]["campo"] == campo


@pytest.mark.parametrize("competencia,status,valor,quantidade,criterio", [
    ("2026-08", "ativa", 74096.15, 2, "usinas_ativas"),
    ("2026-07", "ativa", 69980.50, 2, "usinas_ativas"),
    ("2026-08", "em_manutencao", 9870.00, 1, "usinas_em_manutencao"),
])
def test_resumo_usa_mesma_competencia_e_status(client, competencia, status, valor, quantidade, criterio):
    resposta = client.get("/v1/creditos-usinas/resumo", params={
        "competencia": competencia, "status_usina": status,
    })
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["competencia"] == competencia
    assert corpo["criterio"] == criterio
    assert corpo["quantidade_usinas"] == quantidade
    assert corpo["total_creditos"] == {"valor": valor, "moeda": "BRL"}
    assert datetime.fromisoformat(corpo["atualizado_em"]).utcoffset() is not None


def test_resumo_padrao_considera_ativas_e_recusa_total_incompleto(client):
    resposta = client.get("/v1/creditos-usinas/resumo?competencia=2026-08")
    assert resposta.json()["criterio"] == "usinas_ativas"
    resposta = client.get("/v1/creditos-usinas/resumo?competencia=2026-09")
    assert resposta.status_code == 503
    assert resposta.json()["codigo"] == "FONTE_INDISPONIVEL"
    assert "total_creditos" not in resposta.json()


def test_depoimentos_expoem_somente_campos_publicos(client):
    resposta = client.get("/v1/depoimentos")
    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["total"] == 2
    assert [d["id"] for d in corpo["data"]] == ["depoimento_01", "depoimento_02"]
    campos_publicos = {
        "id", "nome_publico", "localidade", "avaliacao", "texto", "economia_mensal",
        "dias_para_ativacao", "percentual_desconto", "tempo_conta_ativa_meses",
    }
    for depoimento in corpo["data"]:
        assert set(depoimento) == campos_publicos
        detalhe = client.get(f"/v1/depoimentos/{depoimento['id']}")
        assert detalhe.status_code == 200
        assert detalhe.json() == depoimento


def test_depoimento_sem_campos_opcionais_omite_valores_ausentes(app, client):
    service = DepoimentoService(InMemoryDepoimentoRepository([
        Depoimento("minimo", "Cliente", "MG", 5, "Otimo", True, cliente_id="privado"),
    ]))
    app.dependency_overrides[obter_depoimento_service] = lambda: service
    detalhe = client.get("/v1/depoimentos/minimo").json()
    assert set(detalhe) == {"id", "nome_publico", "localidade", "avaliacao", "texto"}
    assert client.get("/v1/depoimentos").json()["data"] == [detalhe]


def test_repositorios_vazios_nao_inventam_data_de_atualizacao(app, client):
    usinas = InMemoryUsinaRepository()
    app.state.usina_service = UsinaService(usinas)
    app.state.credito_service = CreditoService(usinas, InMemoryCreditoUsinaRepository())
    app.state.depoimento_service = DepoimentoService(InMemoryDepoimentoRepository())
    assert client.get("/v1/usinas").json() == {
        "data": [], "page": 1, "limit": 20, "total": 0, "atualizado_em": None,
    }
    assert client.get("/v1/depoimentos").json() == {"data": [], "page": 1, "limit": 20, "total": 0}
    resumo = client.get("/v1/creditos-usinas/resumo?competencia=2026-08")
    assert resumo.status_code == 200
    assert resumo.json()["quantidade_usinas"] == 0
    assert resumo.json()["atualizado_em"] is None


def test_indisponibilidade_do_servico_e_propagada_no_formato_padrao(app, client):
    service = Mock(spec=UsinaService)
    service.listar.side_effect = FonteIndisponivel()
    app.dependency_overrides[obter_usina_service] = lambda: service
    resposta = client.get("/v1/usinas")
    assert resposta.status_code == 503
    assert resposta.json()["codigo"] == "FONTE_INDISPONIVEL"


def test_openapi_documenta_seis_operacoes_publicas_e_respostas_reais(client):
    contrato = client.get("/openapi.json").json()
    operacoes = {
        "/v1/usinas": "listarUsinas", "/v1/usinas/{usinaId}": "obterUsina",
        "/v1/usinas/{usinaId}/creditos": "obterCreditosUsina",
        "/v1/creditos-usinas/resumo": "obterResumoCreditos",
        "/v1/depoimentos": "listarDepoimentos", "/v1/depoimentos/{depoimentoId}": "obterDepoimento",
    }
    assert {"/", *operacoes} <= set(contrato["paths"])
    for rota, operation_id in operacoes.items():
        operacao = contrato["paths"][rota]["get"]
        assert operacao["operationId"] == operation_id
        assert not operacao.get("security")
        assert {"200", "400", "404", "503"} <= set(operacao["responses"])
        assert "422" not in operacao["responses"]
    parametros = contrato["paths"]["/v1/usinas/{usinaId}/creditos"]["get"]["parameters"]
    assert next(p for p in parametros if p["name"] == "competencia")["required"] is True
    dinheiro = contrato["components"]["schemas"]["Dinheiro"]["properties"]["valor"]
    assert dinheiro["type"] == "number"
