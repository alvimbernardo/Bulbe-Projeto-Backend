"""Controller do primeiro acesso; as regras ficam no servico e dominio."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from src.controllers.conta_schemas import ContaCriacao, ContaResposta
from src.controllers.schemas import Erro
from src.services.conta_service import ContaService


def obter_conta_service(request: Request) -> ContaService:
    return request.app.state.conta_service


router = APIRouter(prefix="/v1/contas", tags=["Contas e sessoes"], responses={
    400: {"model": Erro, "description": "Campos invalidos."},
    409: {"model": Erro, "description": "Cliente ou email ja possui conta."},
    422: {"model": Erro, "description": "Elegibilidade ou vinculo nao confirmado."},
})


@router.post("", status_code=201, response_model=ContaResposta, operation_id="criarConta")
def criar_conta(
    corpo: ContaCriacao, service: Annotated[ContaService, Depends(obter_conta_service)],
) -> ContaResposta:
    """Cria conta apenas para cliente ativo com email e codigo conferidos."""
    conta = service.criar(**corpo.model_dump())
    return ContaResposta.model_validate(conta)
