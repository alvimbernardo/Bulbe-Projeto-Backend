"""Dados ficticios de faturas, pagamentos e repasses para demonstracao."""

from datetime import date, datetime
from decimal import Decimal

from src.domain.competencia import Competencia
from src.domain.dinheiro import Dinheiro
from src.domain.fatura import Fatura, StatusFatura
from src.domain.pagamento import Pagamento, StatusPagamento
from src.domain.repasse import EtapaRepasse, Repasse, StatusEtapaRepasse
from src.repositories.dados_exemplo import BRASILIA


def _data(mes: int, dia: int, hora: int = 9) -> datetime:
    return datetime(2026, mes, dia, hora, 0, tzinfo=BRASILIA)


def faturas_exemplo() -> list[Fatura]:
    return [
        Fatura("fatura_01", "cliente_01", "LIC 0001-0", Competencia(2026, 8),
               Dinheiro(Decimal("89.90")), StatusFatura.paga, date(2026, 8, 15), _data(8, 17)),
        Fatura("fatura_02", "cliente_01", "LIC 0002-0", Competencia(2026, 9),
               Dinheiro(Decimal("95.20")), StatusFatura.aberta, date(2026, 9, 15), _data(9, 1)),
        Fatura("fatura_03", "cliente_02", "LIC 0003-0", Competencia(2026, 8),
               Dinheiro(Decimal("210.00")), StatusFatura.aberta, date(2026, 8, 20), _data(8, 18)),
    ]


def pagamentos_exemplo() -> list[Pagamento]:
    return [
        Pagamento("fatura_01", StatusPagamento.confirmado, _data(8, 15, 12),
                  "pix", _data(8, 15, 11), Dinheiro(Decimal("89.90"))),
        Pagamento("fatura_02", StatusPagamento.pendente, _data(9, 1)),
        Pagamento("fatura_03", StatusPagamento.recusado, _data(8, 18), "cartao"),
    ]


def repasses_exemplo() -> list[Repasse]:
    return [Repasse("fatura_01", (
        EtapaRepasse("repasse_etapa_01", 1, "Pagamento confirmado", StatusEtapaRepasse.concluida,
                     ocorrido_em=_data(8, 15, 11), mensagem="Pagamento recebido pela Bulbe."),
        EtapaRepasse("repasse_etapa_02", 2, "Repasse a CEMIG", StatusEtapaRepasse.atual,
                     previsao=date(2026, 8, 18), mensagem="Repasse em processamento."),
        EtapaRepasse("repasse_etapa_03", 3, "Repasse concluido", StatusEtapaRepasse.pendente),
    ), _data(8, 17))]
