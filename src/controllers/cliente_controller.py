"""Dados basicos do cliente autenticado (US04)."""

from typing import Annotated, Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict

from src.controllers.autorizacao import obter_cliente_autorizado
from src.controllers.schemas import Erro
from src.domain.cliente import Cliente as ClienteDominio


class Cliente(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome_exibicao: str
    email: str
    status: Literal["ativo", "inativo"]


router = APIRouter(prefix="/v1/clientes", tags=["Clientes"], responses={
    400: {"model": Erro}, 401: {"model": Erro}, 403: {"model": Erro},
    404: {"model": Erro}, "4XX": {"model": Erro},
})


@router.get("/{clienteId}", response_model=Cliente, operation_id="obterCliente")
def obter_cliente(cliente: Annotated[ClienteDominio, Depends(obter_cliente_autorizado)]) -> Cliente:
    return Cliente.model_validate(cliente)
