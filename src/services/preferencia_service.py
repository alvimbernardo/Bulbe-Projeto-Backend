"""Alteracao de preferencias de ativacao; nao envia notificacoes."""

from collections.abc import Callable
from datetime import datetime, timezone

from src.domain.preferencia_notificacao import PreferenciaNotificacao
from src.repositories.preferencia_repository import PreferenciaRepository


class PreferenciaService:
    def __init__(self, preferencias: PreferenciaRepository,
                 relogio: Callable[[], datetime] = lambda: datetime.now(timezone.utc)) -> None:
        self._preferencias = preferencias
        self._relogio = relogio

    def alterar(self, cliente_id: str, habilitada: bool, canais: list[str]) -> PreferenciaNotificacao:
        preferencia = PreferenciaNotificacao.criar(cliente_id, habilitada, canais, self._relogio())
        return self._preferencias.salvar(preferencia)
