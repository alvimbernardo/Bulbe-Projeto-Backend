"""Preferencia idempotente de atualizacoes de ativacao (US12)."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.erros import ErroDeNegocio


@dataclass(frozen=True)
class PreferenciaNotificacao:
    cliente_id: str
    habilitada: bool
    canais: tuple[str, ...]
    atualizada_em: datetime

    @classmethod
    def criar(cls, cliente_id: str, habilitada: bool, canais: list[str], agora: datetime):
        normalizados = tuple(sorted(set(canais)))
        if any(canal != "email" for canal in normalizados) or (habilitada and not normalizados):
            raise ErroDeNegocio(
                "CANAL_NAO_SUPORTADO", "Selecione email ao habilitar as atualizacoes.", 422,
                [{"campo": "canais", "mensagem": "Somente o canal email e suportado."}],
            )
        return cls(cliente_id, habilitada, normalizados, agora)

    def mesma_configuracao(self, outra: "PreferenciaNotificacao") -> bool:
        return self.habilitada == outra.habilitada and self.canais == outra.canais
