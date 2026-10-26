"""Dependencia reutilizavel de sessao autenticada por Bearer JWT."""

from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.domain.erros import NaoAutenticado
from src.domain.sessao import Sessao
from src.services.sessao_service import SessaoService

bearer = HTTPBearer(auto_error=False, scheme_name="sessao", bearerFormat="JWT")


def obter_sessao_service(request: Request) -> SessaoService:
    return request.app.state.sessao_service


def obter_token(
    credencial: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> str:
    if credencial is None or credencial.scheme.casefold() != "bearer":
        raise NaoAutenticado()
    return credencial.credentials


def obter_sessao_atual(
    token: Annotated[str, Depends(obter_token)],
    service: Annotated[SessaoService, Depends(obter_sessao_service)],
) -> Sessao:
    return service.validar_token(token)
