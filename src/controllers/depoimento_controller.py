"""Consultas de depoimentos com campos publicos autorizados (US11)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.controllers.dependencias import obter_depoimento_service
from src.controllers.schemas import Depoimento, ListaDepoimentos, RESPOSTAS_PUBLICAS
from src.services.depoimento_service import DepoimentoService

router = APIRouter(prefix="/v1/depoimentos", tags=["Depoimentos"], responses=RESPOSTAS_PUBLICAS)
Servico = Annotated[DepoimentoService, Depends(obter_depoimento_service)]


@router.get("", response_model=ListaDepoimentos, response_model_exclude_none=True, operation_id="listarDepoimentos")
def listar_depoimentos(
    service: Servico,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ListaDepoimentos:
    """Lista somente depoimentos autorizados, sem identificadores privados."""
    pagina = service.listar(page=page, limit=limit)
    return ListaDepoimentos(
        data=[Depoimento.model_validate(item.dados_publicos()) for item in pagina.itens],
        page=pagina.page, limit=pagina.limit, total=pagina.total,
    )


@router.get("/{depoimentoId}", response_model=Depoimento, response_model_exclude_none=True, operation_id="obterDepoimento")
def obter_depoimento(depoimentoId: str, service: Servico) -> Depoimento:
    """Retorna 404 tanto para depoimento inexistente quanto nao autorizado."""
    return Depoimento.model_validate(service.obter(depoimentoId).dados_publicos())
