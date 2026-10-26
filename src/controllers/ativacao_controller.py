"""Rotas privadas da ativacao; autorizacao precede a consulta ao servico."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.controllers.autorizacao import exigir_cliente
from src.controllers.ativacao_schemas import (
    AtivacaoResposta, EtapaAtivacaoResposta, ListaEtapasAtivacaoResposta,
)
from src.controllers.schemas import Erro
from src.services.ativacao_service import AtivacaoService

router = APIRouter(
    prefix="/v1/clientes/{clienteId}/ativacao", tags=["Ativacao"],
    responses={
        400: {"model": Erro}, 401: {"model": Erro}, 403: {"model": Erro},
        404: {"model": Erro}, 503: {"model": Erro}, "4XX": {"model": Erro},
    },
)


def obter_ativacao_service(request: Request) -> AtivacaoService:
    return request.app.state.ativacao_service


ClienteAutorizado = Annotated[str, Depends(exigir_cliente)]
Servico = Annotated[AtivacaoService, Depends(obter_ativacao_service)]


@router.get("", response_model=AtivacaoResposta, response_model_exclude_none=True, operation_id="obterAtivacao")
def obter_ativacao(cliente_id: ClienteAutorizado, service: Servico) -> AtivacaoResposta:
    """Retorna o progresso calculado das etapas do cliente autenticado."""
    ativacao = service.obter(cliente_id)
    atual = ativacao.obter_etapa_atual()
    return AtivacaoResposta(
        cliente_id=ativacao.cliente_id, status=ativacao.status,
        percentual=ativacao.calcular_percentual(), etapa_atual_id=atual.id if atual else None,
        iniciada_em=ativacao.iniciada_em, previsao_conclusao=ativacao.previsao_conclusao,
        atualizado_em=ativacao.atualizado_em,
    )


@router.get("/etapas", response_model=ListaEtapasAtivacaoResposta, operation_id="listarEtapasAtivacao")
def listar_etapas_ativacao(cliente_id: ClienteAutorizado, service: Servico) -> ListaEtapasAtivacaoResposta:
    """Retorna etapas na ordem definida, com status e datas disponiveis."""
    resultado = service.listar_etapas(cliente_id)
    return ListaEtapasAtivacaoResposta(
        cliente_id=resultado.cliente_id,
        data=[EtapaAtivacaoResposta.model_validate(etapa) for etapa in resultado.etapas],
        atualizado_em=resultado.atualizado_em,
    )
