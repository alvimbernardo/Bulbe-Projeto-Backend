"""Contrato e repositorio em memoria de faturas."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.fatura import Fatura


class FaturaRepository(ABC):
    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[Fatura]: ...

    @abstractmethod
    def obter(self, fatura_id: str) -> Fatura | None: ...


class InMemoryFaturaRepository(FaturaRepository):
    def __init__(self, faturas: Iterable[Fatura] = ()) -> None:
        self._faturas = {f.id: f for f in faturas}

    def listar_por_cliente(self, cliente_id: str) -> list[Fatura]:
        return sorted(
            (f for f in self._faturas.values() if f.pertence_ao_cliente(cliente_id)),
            key=lambda fatura: (fatura.competencia, fatura.id), reverse=True,
        )

    def obter(self, fatura_id: str) -> Fatura | None:
        return self._faturas.get(fatura_id)
