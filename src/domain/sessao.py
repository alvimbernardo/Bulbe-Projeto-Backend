"""Sessao autenticada e revogavel em memoria (US01 e US02)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Sessao:
    id: str
    conta_id: str
    cliente_id: str
    criada_em: datetime
    expira_em: datetime
    invalidada_em: datetime | None = None

    def __post_init__(self) -> None:
        if not self.id or not self.conta_id or not self.cliente_id:
            raise ValueError("Sessao precisa de identificadores de sessao, conta e cliente.")
        if self.criada_em.utcoffset() is None or self.expira_em.utcoffset() is None:
            raise ValueError("Datas da sessao precisam de fuso horario.")
        if self.expira_em <= self.criada_em:
            raise ValueError("A expiracao precisa ser posterior a criacao da sessao.")

    def esta_valida(self, agora: datetime) -> bool:
        return self.invalidada_em is None and self.criada_em <= agora < self.expira_em

    def invalidar(self, agora: datetime) -> bool:
        if not self.esta_valida(agora):
            return False
        self.invalidada_em = agora
        return True
