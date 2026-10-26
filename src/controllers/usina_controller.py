"""Consultas publicas de usinas (US06)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.controllers.dependencias import obter_usina_service
from src.controllers.schemas import ListaUsinas, RESPOSTAS_PUBLICAS, Usina, UsinaResumo
from src.domain.usina import StatusUsina
from src.services.usina_service import UsinaService

router = APIRouter(prefix="/v1/usinas", tags=["Usinas"], responses=RESPOSTAS_PUBLICAS)
Servico = Annotated[UsinaService, Depends(obter_usina_service)]


@router.get("", response_model=ListaUsinas, operation_id="listarUsinas")
def listar_usinas(
    service: Servico,
    status: StatusUsina | None = None,
    page: Annotated[int, Query(ge=1)] = 1,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ListaUsinas:
    """Lista usinas ativas por padrao, com filtro de situacao e paginacao."""
    resultado = service.listar(status=status, page=page, limit=limit)
    pagina = resultado.pagina
    return ListaUsinas(
        data=[UsinaResumo.model_validate(usina) for usina in pagina.itens],
        page=pagina.page, limit=pagina.limit, total=pagina.total,
        atualizado_em=resultado.atualizado_em,
    )


@router.get("/{usinaId}", response_model=Usina, operation_id="obterUsina")
def obter_usina(usinaId: str, service: Servico) -> Usina:
    """Retorna os detalhes de uma usina, incluindo regiao e atualizacao."""
    return Usina.model_validate(service.obter(usinaId))
