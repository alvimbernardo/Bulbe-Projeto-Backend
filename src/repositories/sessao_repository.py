"""Interface de sessoes e implementacao em memoria com revogacao atomica."""

from abc import ABC, abstractmethod
from datetime import datetime
from threading import Lock

from src.domain.sessao import Sessao


class SessaoRepository(ABC):
    @abstractmethod
    def salvar(self, sessao: Sessao) -> None: ...

    @abstractmethod
    def obter(self, sessao_id: str) -> Sessao | None: ...

    @abstractmethod
    def invalidar(self, sessao_id: str, agora: datetime) -> bool: ...

    @abstractmethod
    def limpar_expiradas(self, agora: datetime) -> None: ...


class InMemorySessaoRepository(SessaoRepository):
    def __init__(self) -> None:
        self._sessoes: dict[str, Sessao] = {}
        self._lock = Lock()

    def salvar(self, sessao: Sessao) -> None:
        with self._lock:
            if sessao.id in self._sessoes:
                raise ValueError("Identificador de sessao ja existente.")
            self._sessoes[sessao.id] = sessao

    def obter(self, sessao_id: str) -> Sessao | None:
        with self._lock:
            return self._sessoes.get(sessao_id)

    def invalidar(self, sessao_id: str, agora: datetime) -> bool:
        with self._lock:
            sessao = self._sessoes.get(sessao_id)
            return sessao.invalidar(agora) if sessao is not None else False

    def limpar_expiradas(self, agora: datetime) -> None:
        with self._lock:
            self._sessoes = {
                chave: sessao for chave, sessao in self._sessoes.items()
                if sessao.esta_valida(agora)
            }
