"""Interface e armazenamento em memoria de ativacoes por cliente."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.ativacao import Ativacao


class AtivacaoRepository(ABC):
    @abstractmethod
    def obter(self, cliente_id: str) -> Ativacao | None: ...


class InMemoryAtivacaoRepository(AtivacaoRepository):
    def __init__(self, ativacoes: Iterable[Ativacao] = ()) -> None:
        self._ativacoes = {ativacao.cliente_id: ativacao for ativacao in ativacoes}

    def obter(self, cliente_id: str) -> Ativacao | None:
        return self._ativacoes.get(cliente_id)
