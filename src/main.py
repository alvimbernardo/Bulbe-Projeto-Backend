"""Ponto de entrada da API Bulbe."""

from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.controllers.credito_controller import router as credito_router
from src.controllers.depoimento_controller import router as depoimento_router
from src.controllers.status_controller import router as status_router
from src.controllers.usina_controller import router as usina_router
from src.domain.erros import ErroDeNegocio
from src.repositories.credito_usina_repository import InMemoryCreditoUsinaRepository
from src.repositories.dados_exemplo import creditos_exemplo, depoimentos_exemplo, usinas_exemplo
from src.repositories.depoimento_repository import InMemoryDepoimentoRepository
from src.repositories.usina_repository import InMemoryUsinaRepository
from src.services.credito_service import CreditoService
from src.services.depoimento_service import DepoimentoService
from src.services.usina_service import UsinaService
from src.controllers.conta_controller import router as conta_router
from src.repositories.cliente_repository import InMemoryClienteRepository
from src.repositories.conta_repository import InMemoryContaRepository
from src.repositories.dados_contas import clientes_exemplo, contas_exemplo
from src.services.conta_service import ContaService


def _request_id(request: Request) -> str:
    return request.headers.get("X-Request-ID") or f"req_{uuid4().hex[:12]}"


def resposta_de_erro(
    request: Request,
    status: int,
    codigo: str,
    mensagem: str,
    detalhes: list[dict] | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "codigo": codigo,
            "mensagem": mensagem,
            "detalhes": detalhes or [],
            "request_id": _request_id(request),
        },
    )


def tratar_erro_de_negocio(request: Request, exc: ErroDeNegocio) -> JSONResponse:
    return resposta_de_erro(request, exc.status, exc.codigo, exc.mensagem, exc.detalhes)


def tratar_erro_de_validacao(request: Request, exc: RequestValidationError) -> JSONResponse:
    detalhes = [
        {
            "campo": ".".join(str(parte) for parte in erro.get("loc", ())[1:]) or str(erro.get("loc", "")),
            "mensagem": erro.get("msg", ""),
        }
        for erro in exc.errors()
    ]
    return resposta_de_erro(
        request,
        400,
        "REQUISICAO_INVALIDA",
        "Um ou mais campos da requisicao sao invalidos.",
        detalhes,
    )


def tratar_erro_http(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    padroes = {
        401: ("NAO_AUTENTICADO", "E necessario estar autenticado."),
        403: ("ACESSO_NEGADO", "Voce nao tem permissao para acessar este recurso."),
        404: ("RECURSO_NAO_ENCONTRADO", "O recurso solicitado nao foi encontrado."),
        405: ("METODO_NAO_PERMITIDO", "Metodo HTTP nao permitido para esta rota."),
    }
    codigo, mensagem = padroes.get(exc.status_code, ("ERRO_HTTP", str(exc.detail)))
    return resposta_de_erro(request, exc.status_code, codigo, mensagem)


def create_app() -> FastAPI:
    """Compoe repositorios e servicos novos para cada instancia da aplicacao."""
    app = FastAPI(
        title="API Bulbe Energia",
        description="Backend da plataforma Bulbe Energia, Projeto Ciencia de Dados II (Squad Master).",
        version="1.0.0",
    )
    usinas = InMemoryUsinaRepository(usinas_exemplo())
    creditos = InMemoryCreditoUsinaRepository(creditos_exemplo())
    depoimentos = InMemoryDepoimentoRepository(depoimentos_exemplo())
    app.state.usina_service = UsinaService(usinas)
    app.state.credito_service = CreditoService(usinas, creditos)
    app.state.depoimento_service = DepoimentoService(depoimentos)
    clientes = InMemoryClienteRepository(clientes_exemplo())
    contas = InMemoryContaRepository(contas_exemplo())
    app.state.conta_service = ContaService(clientes, contas)

    app.add_exception_handler(ErroDeNegocio, tratar_erro_de_negocio)
    app.add_exception_handler(RequestValidationError, tratar_erro_de_validacao)
    app.add_exception_handler(StarletteHTTPException, tratar_erro_http)
    app.include_router(status_router)
    app.include_router(usina_router)
    app.include_router(credito_router)
    app.include_router(depoimento_router)
    app.include_router(conta_router)
    return app


app = create_app()
