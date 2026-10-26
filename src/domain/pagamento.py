"""Situacao de pagamento, distinta da ausencia de registro (US10)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.domain.dinheiro import Dinheiro
from src.domain.erros import DadoInvalido


class StatusPagamento(str, Enum):
    pendente = "pendente"
    confirmado = "confirmado"
    recusado = "recusado"
    estornado = "estornado"


@dataclass(frozen=True)
class Pagamento:
    fatura_id: str
    status: StatusPagamento
    atualizado_em: datetime
    forma: str | None = None
    pago_em: datetime | None = None
    valor: Dinheiro | None = None

    def __post_init__(self) -> None:
        if not self.fatura_id.strip():
            raise DadoInvalido("fatura_id", "Informe a fatura do pagamento.")
        try:
            object.__setattr__(self, "status", StatusPagamento(self.status))
        except ValueError:
            raise DadoInvalido("status", "Situacao de pagamento invalida.") from None
        if self.atualizado_em.utcoffset() is None or (
            self.pago_em is not None and self.pago_em.utcoffset() is None
        ):
            raise DadoInvalido("pagamento", "Datas do pagamento precisam informar o fuso horario.")
        if self.esta_confirmado() and (
            self.pago_em is None or self.valor is None or not (self.forma or "").strip()
        ):
            raise DadoInvalido("pagamento", "Pagamento confirmado exige forma, valor e data de confirmacao.")
        if self.status in (StatusPagamento.pendente, StatusPagamento.recusado) and self.pago_em is not None:
            raise DadoInvalido("pago_em", "Pagamento pendente ou recusado nao possui data de confirmacao.")
        if self.pago_em is not None and self.pago_em > self.atualizado_em:
            raise DadoInvalido("pago_em", "A confirmacao nao pode ser posterior a atualizacao do pagamento.")

    def esta_confirmado(self) -> bool:
        return self.status is StatusPagamento.confirmado

    def foi_recusado(self) -> bool:
        return self.status is StatusPagamento.recusado
