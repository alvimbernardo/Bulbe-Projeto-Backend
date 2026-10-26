"""Linha do tempo de repasse com ordem e estados coerentes (US13)."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from src.domain.erros import DadoInvalido


class StatusEtapaRepasse(str, Enum):
    concluida = "concluida"
    atual = "atual"
    pendente = "pendente"


class StatusRepasse(str, Enum):
    nao_iniciado = "nao_iniciado"
    em_andamento = "em_andamento"
    concluido = "concluido"


@dataclass(frozen=True)
class EtapaRepasse:
    id: str
    ordem: int
    nome: str
    status: StatusEtapaRepasse
    ocorrido_em: datetime | None = None
    previsao: date | None = None
    mensagem: str | None = None

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.nome.strip() or self.ordem < 1:
            raise DadoInvalido("etapas", "Etapa de repasse exige id, nome e ordem positiva.")
        try:
            object.__setattr__(self, "status", StatusEtapaRepasse(self.status))
        except ValueError:
            raise DadoInvalido("status", "Situacao de etapa de repasse invalida.") from None
        if self.esta_concluida() and (self.ocorrido_em is None or self.previsao is not None):
            raise DadoInvalido("etapas", "Etapa concluida exige data do evento e nao recebe previsao.")
        if not self.esta_concluida() and self.ocorrido_em is not None:
            raise DadoInvalido("ocorrido_em", "Somente uma etapa concluida possui data do evento.")
        if self.ocorrido_em is not None and self.ocorrido_em.utcoffset() is None:
            raise DadoInvalido("ocorrido_em", "A data do evento precisa informar o fuso horario.")

    def esta_concluida(self) -> bool:
        return self.status is StatusEtapaRepasse.concluida


@dataclass(frozen=True)
class Repasse:
    fatura_id: str
    etapas: tuple[EtapaRepasse, ...]
    atualizado_em: datetime

    def __post_init__(self) -> None:
        object.__setattr__(self, "etapas", tuple(sorted(self.etapas, key=lambda etapa: etapa.ordem)))
        if not self.fatura_id.strip() or not self.etapas:
            raise DadoInvalido("repasse", "Repasse exige uma fatura e pelo menos uma etapa.")
        if self.atualizado_em.utcoffset() is None:
            raise DadoInvalido("atualizado_em", "A atualizacao do repasse precisa informar o fuso horario.")
        if len({e.ordem for e in self.etapas}) != len(self.etapas) or len({e.id for e in self.etapas}) != len(self.etapas):
            raise DadoInvalido("etapas", "Identificadores e ordens das etapas nao podem se repetir.")
        estados = [e.status for e in self.etapas]
        concluidas = sum(e.esta_concluida() for e in self.etapas)
        atuais = estados.count(StatusEtapaRepasse.atual)
        if atuais > 1:
            raise DadoInvalido("etapas", "O repasse pode ter somente uma etapa atual.")
        esperados = [StatusEtapaRepasse.concluida] * concluidas
        if atuais:
            esperados += [StatusEtapaRepasse.atual]
        esperados += [StatusEtapaRepasse.pendente] * (len(self.etapas) - len(esperados))
        if estados != esperados or (0 < concluidas < len(self.etapas) and atuais != 1):
            raise DadoInvalido("etapas", "Etapas devem seguir a ordem: concluidas, atual e pendentes.")
        if any(e.ocorrido_em is not None and e.ocorrido_em > self.atualizado_em for e in self.etapas):
            raise DadoInvalido("atualizado_em", "A atualizacao nao pode anteceder um evento confirmado.")

    @property
    def status(self) -> StatusRepasse:
        if all(e.esta_concluida() for e in self.etapas):
            return StatusRepasse.concluido
        if self.obter_etapa_atual() is not None:
            return StatusRepasse.em_andamento
        return StatusRepasse.nao_iniciado

    def obter_etapa_atual(self) -> EtapaRepasse | None:
        return next((e for e in self.etapas if e.status is StatusEtapaRepasse.atual), None)

    def etapas_ordenadas(self) -> tuple[EtapaRepasse, ...]:
        return self.etapas
