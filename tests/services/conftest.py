"""Fixtures dos testes de servico."""

import pytest

from src.repositories.credito_usina_repository import InMemoryCreditoUsinaRepository
from src.repositories.dados_exemplo import creditos_exemplo, depoimentos_exemplo, usinas_exemplo
from src.repositories.depoimento_repository import InMemoryDepoimentoRepository
from src.repositories.usina_repository import InMemoryUsinaRepository
from src.services.credito_service import CreditoService
from src.services.depoimento_service import DepoimentoService
from src.services.usina_service import UsinaService


@pytest.fixture
def usina_repository() -> InMemoryUsinaRepository:
    return InMemoryUsinaRepository(usinas_exemplo())


@pytest.fixture
def credito_repository() -> InMemoryCreditoUsinaRepository:
    return InMemoryCreditoUsinaRepository(creditos_exemplo())


@pytest.fixture
def usina_service(usina_repository) -> UsinaService:
    return UsinaService(usina_repository)


@pytest.fixture
def credito_service(usina_repository, credito_repository) -> CreditoService:
    return CreditoService(usina_repository, credito_repository)


@pytest.fixture
def depoimento_service() -> DepoimentoService:
    return DepoimentoService(InMemoryDepoimentoRepository(depoimentos_exemplo()))
