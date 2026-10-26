"""Consultas publicas dos creditos por competencia (US07 e US08)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.controllers.dependencias import obter_credito_service
from src.controllers.schemas import CreditoUsina, Dinheiro, RESPOSTAS_PUBLICAS, ResumoCreditos
from src.domain.usina import StatusUsina
from src.services.credito_service import CreditoService

router = APIRouter(prefix="/v1", tags=["Usinas"], responses=RESPOSTAS_PUBLICAS)
Servico = Annotated[CreditoService, Depends(obter_credito_service)]
Periodo = Annotated[str, Query(pattern=r"^\d{4}-(0[1-9]|1[0-2])$", description="Competencia AAAA-MM.")]


@router.get("/usinas/{usinaId}/creditos", response_model=CreditoUsina, operation_id="obterCreditosUsina")
def obter_creditos_usina(usinaId: str, competencia: Periodo, service: Servico) -> CreditoUsina:
    """Retorna o valor do periodo; ausencia de dados retorna 404, nunca zero simulado."""
    credito = service.creditos_da_usina(usinaId, competencia)
    return CreditoUsina(
        usina_id=credito.usina_id, competencia=str(credito.competencia),
        creditos=Dinheiro.model_validate(credito.creditos), atualizado_em=credito.atualizado_em,
    )


@router.get("/creditos-usinas/resumo", response_model=ResumoCreditos, operation_id="obterResumoCreditos")
def obter_resumo_creditos(
    competencia: Periodo,
    service: Servico,
    status_usina: StatusUsina = StatusUsina.ativa,
) -> ResumoCreditos:
    """Soma creditos da mesma competencia; dados incompletos retornam 503."""
    resumo = service.resumo(competencia, status_usina=status_usina)
    return ResumoCreditos(
        competencia=str(resumo.competencia), criterio=resumo.criterio,
        quantidade_usinas=resumo.quantidade_usinas,
        total_creditos=Dinheiro.model_validate(resumo.total_creditos),
        atualizado_em=resumo.atualizado_em,
    )
