"""Repositorio de depoimentos."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.depoimento import Depoimento


class DepoimentoRepository(ABC):
    @abstractmethod
    def listar(self) -> list[Depoimento]: ...

    @abstractmethod
    def obter(self, depoimento_id: str) -> Depoimento | None: ...


class InMemoryDepoimentoRepository(DepoimentoRepository):
    def __init__(self, depoimentos: Iterable[Depoimento] = ()) -> None:
        self._depoimentos: dict[str, Depoimento] = {d.id: d for d in depoimentos}

    def listar(self) -> list[Depoimento]:
        return sorted(self._depoimentos.values(), key=lambda depoimento: depoimento.id)

    def obter(self, depoimento_id: str) -> Depoimento | None:
        return self._depoimentos.get(depoimento_id)
