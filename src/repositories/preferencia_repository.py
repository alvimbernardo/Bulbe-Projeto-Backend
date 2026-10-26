"""Preferencias em memoria com substituicao atomica e idempotente."""

from abc import ABC, abstractmethod
from threading import Lock

from src.domain.preferencia_notificacao import PreferenciaNotificacao


class PreferenciaRepository(ABC):
    @abstractmethod
    def salvar(self, preferencia: PreferenciaNotificacao) -> PreferenciaNotificacao: ...


class InMemoryPreferenciaRepository(PreferenciaRepository):
    def __init__(self) -> None:
        self._preferencias: dict[str, PreferenciaNotificacao] = {}
        self._lock = Lock()

    def salvar(self, preferencia: PreferenciaNotificacao) -> PreferenciaNotificacao:
        with self._lock:
            anterior = self._preferencias.get(preferencia.cliente_id)
            if anterior and anterior.mesma_configuracao(preferencia):
                return anterior
            self._preferencias[preferencia.cliente_id] = preferencia
            return preferencia
