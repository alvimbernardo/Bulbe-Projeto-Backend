"""Destinos por cliente em memoria; configuracao vem do ponto de composicao."""

from abc import ABC, abstractmethod
from collections.abc import Mapping

from src.domain.destino_historico import DestinoHistorico


class HistoricoRepository(ABC):
    @abstractmethod
    def obter(self, cliente_id: str) -> DestinoHistorico | None: ...


class InMemoryHistoricoRepository(HistoricoRepository):
    def __init__(self, destinos: Mapping[str, DestinoHistorico] | None = None) -> None:
        self._destinos = dict(destinos or {})

    def obter(self, cliente_id: str) -> DestinoHistorico | None:
        return self._destinos.get(cliente_id)
