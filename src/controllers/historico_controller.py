"""Redirecionamento autenticado para historico aprovado (US14)."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from src.controllers.autorizacao import exigir_cliente
from src.controllers.schemas import Erro

router = APIRouter(prefix="/v1/clientes/{clienteId}", tags=["Faturas"], responses={
    400: {"model": Erro}, 401: {"model": Erro}, 403: {"model": Erro},
    404: {"model": Erro}, 503: {"model": Erro}, "4XX": {"model": Erro},
})


@router.get("/historico-faturas-externo", status_code=302, response_class=RedirectResponse,
            operation_id="redirecionarHistoricoFaturas", responses={302: {
                "description": "Redireciona para o destino HTTPS aprovado.",
                "headers": {"Location": {"schema": {"type": "string", "format": "uri"}}},
            }})
def historico_externo(request: Request, cliente_id: Annotated[str, Depends(exigir_cliente)]):
    destino = request.app.state.historico_service.obter_destino(cliente_id)
    return RedirectResponse(destino, status_code=302, headers={"Cache-Control": "no-store"})
