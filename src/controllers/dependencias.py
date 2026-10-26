"""Acesso aos servicos compostos no main, sem escolher repositorios aqui."""

from fastapi import Request

from src.services.credito_service import CreditoService
from src.services.depoimento_service import DepoimentoService
from src.services.usina_service import UsinaService


def obter_usina_service(request: Request) -> UsinaService:
    return request.app.state.usina_service


def obter_credito_service(request: Request) -> CreditoService:
    return request.app.state.credito_service


def obter_depoimento_service(request: Request) -> DepoimentoService:
    return request.app.state.depoimento_service
