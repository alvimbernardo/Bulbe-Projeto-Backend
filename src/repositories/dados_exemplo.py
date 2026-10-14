"""Dados de exemplo de usinas, creditos e depoimentos para os repositorios em memoria."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.domain.competencia import Competencia
from src.domain.credito_usina import CreditoUsina
from src.domain.depoimento import Depoimento
from src.domain.dinheiro import Dinheiro
from src.domain.usina import StatusUsina, Usina

BRASILIA = timezone(timedelta(hours=-3))

JULHO_2026 = Competencia(2026, 7)
AGOSTO_2026 = Competencia(2026, 8)


def _data(mes: int, dia: int) -> datetime:
    return datetime(2026, mes, dia, 9, 0, tzinfo=BRASILIA)


def usinas_exemplo() -> list[Usina]:
    return [
        Usina("usina_01", "Usina Solar Montes Claros I", "Montes Claros", "MG", "Norte de Minas",
              StatusUsina.ativa, _data(9, 1)),
        Usina("usina_02", "Usina Solar Janauba", "Janauba", "MG", "Norte de Minas",
              StatusUsina.ativa, _data(9, 1)),
        Usina("usina_03", "Usina Solar Pirapora", "Pirapora", "MG", "Norte de Minas",
              StatusUsina.em_manutencao, _data(9, 3)),
        Usina("usina_04", "Usina Solar Montes Claros II", "Montes Claros", "MG", "Norte de Minas",
              StatusUsina.inativa, _data(6, 30)),
    ]


def creditos_exemplo() -> list[CreditoUsina]:
    valores = {
        JULHO_2026: {"usina_01": "41250.00", "usina_02": "28730.50", "usina_03": "15890.20"},
        AGOSTO_2026: {"usina_01": "43980.75", "usina_02": "30115.40", "usina_03": "9870.00"},
    }
    return [
        CreditoUsina(usina_id, competencia, Dinheiro(Decimal(valor)),
                     _data(competencia.mes + 1, 10 if usina_id != "usina_03" else 12))
        for competencia, por_usina in valores.items()
        for usina_id, valor in por_usina.items()
    ]


def depoimentos_exemplo() -> list[Depoimento]:
    return [
        Depoimento(
            id="depoimento_01",
            nome_publico="Cliente de Montes Claros",
            localidade="Montes Claros - MG",
            avaliacao=5,
            texto="A conta de luz ficou mais barata ja no segundo mes.",
            publicacao_autorizada=True,
            economia_mensal=Dinheiro(Decimal("85.40")),
            dias_para_ativacao=72,
            percentual_desconto=Decimal("15"),
            tempo_conta_ativa_meses=8,
            cliente_id="cliente_01",
        ),
        Depoimento(
            id="depoimento_02",
            nome_publico="Comercio de Janauba",
            localidade="Janauba - MG",
            avaliacao=4,
            texto="Processo simples e acompanhamento claro da ativacao.",
            publicacao_autorizada=True,
            economia_mensal=Dinheiro(Decimal("312.90")),
            dias_para_ativacao=65,
            percentual_desconto=Decimal("12"),
            tempo_conta_ativa_meses=5,
            cliente_id="cliente_02",
        ),
        Depoimento(
            id="depoimento_03",
            nome_publico="Cliente de Pirapora",
            localidade="Pirapora - MG",
            avaliacao=5,
            texto="Recomendo para quem quer economizar.",
            publicacao_autorizada=False,
            cliente_id="cliente_03",
        ),
    ]
