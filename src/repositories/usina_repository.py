"""Repositorio de usinas."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.usina import Usina


class UsinaRepository(ABC):
    @abstractmethod
    def listar(self) -> list[Usina]: ...

    @abstractmethod
    def obter(self, usina_id: str) -> Usina | None: ...


class InMemoryUsinaRepository(UsinaRepository):
    def __init__(self, usinas: Iterable[Usina] = ()) -> None:
        self._usinas: dict[str, Usina] = {usina.id: usina for usina in usinas}

    def listar(self) -> list[Usina]:
        return sorted(self._usinas.values(), key=lambda usina: usina.id)

    def obter(self, usina_id: str) -> Usina | None:
        return self._usinas.get(usina_id)
