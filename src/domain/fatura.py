"""Fatura vinculada a um cliente (US10)."""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum

from src.domain.competencia import Competencia
from src.domain.dinheiro import Dinheiro
from src.domain.erros import DadoInvalido


class StatusFatura(str, Enum):
    aberta = "aberta"
    paga = "paga"
    vencida = "vencida"
    cancelada = "cancelada"


@dataclass(frozen=True)
class Fatura:
    id: str
    cliente_id: str
    identificador_exibivel: str
    competencia: Competencia
    valor: Dinheiro
    status: StatusFatura
    vencimento: date
    atualizado_em: datetime

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.cliente_id.strip():
            raise DadoInvalido("fatura", "Fatura e cliente precisam de identificadores.")
        if not self.identificador_exibivel.strip():
            raise DadoInvalido("identificador_exibivel", "Informe o identificador exibivel da fatura.")
        try:
            object.__setattr__(self, "status", StatusFatura(self.status))
        except ValueError:
            raise DadoInvalido("status", "Situacao de fatura invalida.") from None
        if self.atualizado_em.utcoffset() is None:
            raise DadoInvalido("atualizado_em", "A atualizacao da fatura precisa informar o fuso horario.")

    def pertence_ao_cliente(self, cliente_id: str) -> bool:
        return self.cliente_id == cliente_id

    def pertence_a_competencia(self, competencia: Competencia) -> bool:
        return self.competencia == competencia

    def esta_paga(self) -> bool:
        return self.status is StatusFatura.paga
