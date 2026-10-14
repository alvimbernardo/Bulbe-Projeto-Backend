"""Repositorio de creditos por usina."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.competencia import Competencia
from src.domain.credito_usina import CreditoUsina


class CreditoUsinaRepository(ABC):
    @abstractmethod
    def obter(self, usina_id: str, competencia: Competencia) -> CreditoUsina | None: ...

    @abstractmethod
    def listar_por_competencia(self, competencia: Competencia) -> list[CreditoUsina]: ...


class InMemoryCreditoUsinaRepository(CreditoUsinaRepository):
    def __init__(self, creditos: Iterable[CreditoUsina] = ()) -> None:
        self._creditos: dict[tuple[str, Competencia], CreditoUsina] = {
            (credito.usina_id, credito.competencia): credito for credito in creditos
        }

    def obter(self, usina_id: str, competencia: Competencia) -> CreditoUsina | None:
        return self._creditos.get((usina_id, competencia))

    def listar_por_competencia(self, competencia: Competencia) -> list[CreditoUsina]:
        return sorted(
            (c for c in self._creditos.values() if c.competencia == competencia),
            key=lambda credito: credito.usina_id,
        )
