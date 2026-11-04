"""Preferencias em memoria com substituicao atomica e idempotente."""

from abc import ABC, abstractmethod
from threading import Lock

from sqlalchemy.orm import sessionmaker

from src.db.models import PreferenciaNotificacaoModel
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


class SqlPreferenciaRepository(PreferenciaRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def salvar(self, preferencia: PreferenciaNotificacao) -> PreferenciaNotificacao:
        with self._sessoes() as sessao:
            modelo = sessao.get(PreferenciaNotificacaoModel, preferencia.cliente_id, with_for_update=True)
            if modelo is not None:
                anterior = modelo.para_dominio()
                if anterior.mesma_configuracao(preferencia):
                    return anterior
            sessao.merge(PreferenciaNotificacaoModel.de_dominio(preferencia))
            sessao.commit()
            return preferencia
