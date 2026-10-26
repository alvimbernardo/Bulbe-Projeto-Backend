"""Preferencias de atualizacoes de ativacao (US12)."""

from datetime import datetime
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, ConfigDict, StrictBool

from src.controllers.autorizacao import exigir_cliente
from src.controllers.schemas import Erro


class PreferenciaNotificacaoEntrada(BaseModel):
    habilitada: StrictBool
    canais: list[str]


class PreferenciaNotificacao(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_serialization_defaults_required=True)

    cliente_id: str
    tipo: Literal["ativacao"] = "ativacao"
    habilitada: bool
    canais: list[str]
    atualizada_em: datetime


router = APIRouter(prefix="/v1/clientes/{clienteId}", tags=["Ativacao"], responses={
    400: {"model": Erro}, 401: {"model": Erro}, 403: {"model": Erro},
    422: {"model": Erro}, "4XX": {"model": Erro},
})


@router.put("/preferencias-notificacao/ativacao", response_model=PreferenciaNotificacao,
            operation_id="salvarPreferenciaAtivacao")
def alterar_preferencia(corpo: PreferenciaNotificacaoEntrada, request: Request,
                       cliente_id: Annotated[str, Depends(exigir_cliente)]) -> PreferenciaNotificacao:
    preferencia = request.app.state.preferencia_service.alterar(cliente_id, corpo.habilitada, corpo.canais)
    return PreferenciaNotificacao.model_validate(preferencia)
