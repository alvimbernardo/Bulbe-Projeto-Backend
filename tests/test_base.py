"""
Testes da base do projeto (TEC-01 e TEC-03): API no ar e formato padrao de erro.
"""

from fastapi import APIRouter
import pytest
from pydantic import BaseModel

from src.domain.erros import ErroDeNegocio, RecursoNaoEncontrado

# Rotas usadas so nos testes, para exercitar os handlers de erro.
_rotas_de_teste = APIRouter(prefix="/_teste", include_in_schema=False)


class _Corpo(BaseModel):
    email: str
    idade: int


@_rotas_de_teste.get("/erro-negocio")
def _erro_negocio() -> None:
    raise ErroDeNegocio("CONTA_JA_EXISTENTE", "Ja existe uma conta para este cliente.", 409)


@_rotas_de_teste.get("/nao-encontrado")
def _nao_encontrado() -> None:
    raise RecursoNaoEncontrado()


@_rotas_de_teste.post("/validacao")
def _validacao(corpo: _Corpo) -> dict:
    return corpo.model_dump()


@pytest.fixture(autouse=True)
def registrar_rotas_de_teste(app):
    app.include_router(_rotas_de_teste)

CAMPOS_DO_ERRO = {"codigo", "mensagem", "detalhes", "request_id"}


def test_api_no_ar(client):
    resposta = client.get("/")
    assert resposta.status_code == 200
    assert resposta.json()["versao"] == "v1"


def test_swagger_disponivel(client):
    assert client.get("/docs").status_code == 200
    assert client.get("/openapi.json").status_code == 200


def test_erro_de_negocio_no_formato_do_contrato(client):
    resposta = client.get("/_teste/erro-negocio")
    corpo = resposta.json()
    assert resposta.status_code == 409
    assert set(corpo) == CAMPOS_DO_ERRO
    assert corpo["codigo"] == "CONTA_JA_EXISTENTE"


def test_recurso_nao_encontrado(client):
    resposta = client.get("/_teste/nao-encontrado")
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_validacao_vira_400_com_detalhes(client):
    resposta = client.post("/_teste/validacao", json={"email": "a@b.com", "idade": "abc"})
    corpo = resposta.json()
    assert resposta.status_code == 400
    assert set(corpo) == CAMPOS_DO_ERRO
    assert corpo["codigo"] == "REQUISICAO_INVALIDA"
    assert corpo["detalhes"][0]["campo"] == "idade"


def test_rota_inexistente_no_formato_do_contrato(client):
    resposta = client.get("/v1/rota-que-nao-existe")
    assert resposta.status_code == 404
    assert set(resposta.json()) == CAMPOS_DO_ERRO


def test_metodo_nao_permitido(client):
    resposta = client.delete("/")
    assert resposta.status_code == 405
    assert resposta.json()["codigo"] == "METODO_NAO_PERMITIDO"


def test_request_id_reaproveita_cabecalho(client):
    resposta = client.get("/v1/rota-que-nao-existe", headers={"X-Request-ID": "req_abc"})
    assert resposta.json()["request_id"] == "req_abc"
