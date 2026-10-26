"""Rotas protegidas de faturas, pagamento e repasse (US10 e US13)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from src.controllers.autorizacao import exigir_cliente
from src.controllers.fatura_schemas import Fatura, FaturaResumo, ListaFaturas, Pagamento, Repasse
from src.controllers.schemas import Erro, RESPOSTAS_PUBLICAS
from src.services.fatura_service import FaturaService

router = APIRouter(
    prefix="/v1/clientes/{clienteId}/faturas", tags=["Faturas"],
    responses={**RESPOSTAS_PUBLICAS, 401: {"model": Erro}, 403: {"model": Erro}},
)


def obter_fatura_service(request: Request) -> FaturaService:
    return request.app.state.fatura_service


Cliente = Annotated[str, Depends(exigir_cliente)]
Servico = Annotated[FaturaService, Depends(obter_fatura_service)]


@router.get("", response_model=ListaFaturas, operation_id="listarFaturas")
def listar_faturas(
    cliente_id: Cliente, service: Servico,
    competencia: Annotated[str | None, Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$")] = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ListaFaturas:
    """Lista somente faturas do cliente autenticado; periodo sem faturas retorna lista vazia."""
    resultado = service.listar(cliente_id, competencia, page, limit)
    pagina = resultado.pagina
    return ListaFaturas(
        data=[FaturaResumo.de_entidade(fatura) for fatura in pagina.itens],
        page=pagina.page, limit=pagina.limit, total=pagina.total,
        atualizado_em=resultado.atualizado_em,
    )


@router.get("/{faturaId}", response_model=Fatura, operation_id="obterFatura")
def obter_fatura(faturaId: str, cliente_id: Cliente, service: Servico) -> Fatura:
    """Exibe uma fatura do cliente; identificador de outro cliente tambem retorna 404."""
    return Fatura.de_entidade(service.obter(cliente_id, faturaId))


@router.get("/{faturaId}/pagamento", response_model=Pagamento, response_model_exclude_none=True, operation_id="obterPagamentoFatura")
def obter_pagamento(faturaId: str, cliente_id: Cliente, service: Servico) -> Pagamento:
    """Pagamento ausente retorna 404, enquanto um pagamento recusado tem status explicito."""
    return Pagamento.model_validate(service.pagamento(cliente_id, faturaId))


@router.get("/{faturaId}/repasse", response_model=Repasse, operation_id="obterRepasseFatura")
def obter_repasse(faturaId: str, cliente_id: Cliente, service: Servico) -> Repasse:
    """Retorna etapas ordenadas, sem previsao para eventos ja concluidos."""
    return Repasse.model_validate(service.repasse(cliente_id, faturaId))
