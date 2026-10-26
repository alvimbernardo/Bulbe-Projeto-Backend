"""Controllers de criacao e encerramento de sessoes (US01 e US02)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response

from src.controllers.autenticacao import obter_sessao_service, obter_token
from src.controllers.schemas import Erro
from src.controllers.sessao_schemas import Credenciais, SessaoResposta
from src.services.sessao_service import SessaoService

router = APIRouter(prefix="/v1/sessoes", tags=["Contas e sessoes"], responses={
    400: {"model": Erro, "description": "Dados invalidos."},
    401: {"model": Erro, "description": "Credenciais ou sessao invalidas."},
    429: {"model": Erro, "description": "Limite temporario de tentativas atingido."},
    "4XX": {"model": Erro, "description": "Erro no formato padrao da API."},
})
Servico = Annotated[SessaoService, Depends(obter_sessao_service)]


@router.post("", status_code=201, response_model=SessaoResposta, operation_id="criarSessao")
def criar_sessao(corpo: Credenciais, service: Servico, response: Response) -> SessaoResposta:
    sessao, token = service.autenticar(corpo.email, corpo.senha.get_secret_value())
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return SessaoResposta(
        sessao_id=sessao.id, conta_id=sessao.conta_id, cliente_id=sessao.cliente_id,
        expira_em=sessao.expira_em, access_token=token,
    )


@router.delete("/atual", status_code=204, response_class=Response, operation_id="encerrarSessao")
def encerrar_sessao(token: Annotated[str, Depends(obter_token)], service: Servico) -> Response:
    service.encerrar(token)
    return Response(status_code=204, headers={"Cache-Control": "no-store"})
