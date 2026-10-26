"""Dependencias de autorizacao reutilizadas em todas as rotas de cliente."""

from typing import Annotated

from fastapi import Depends, Request

from src.controllers.autenticacao import obter_sessao_atual
from src.domain.cliente import Cliente
from src.domain.sessao import Sessao


def obter_cliente_autorizado(
    clienteId: str,
    request: Request,
    sessao: Annotated[Sessao, Depends(obter_sessao_atual)],
) -> Cliente:
    return request.app.state.autorizacao_service.obter_cliente(sessao, clienteId)


def exigir_cliente(cliente: Annotated[Cliente, Depends(obter_cliente_autorizado)]) -> str:
    return cliente.id
