"""Testes de integracao dos repositorios SQL de ativacao, faturas, pagamentos e repasses."""

from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models import FaturaModel
from src.domain.ativacao import StatusAtivacao
from src.domain.pagamento import StatusPagamento
from src.domain.repasse import StatusRepasse
from src.repositories.ativacao_repository import SqlAtivacaoRepository
from src.repositories.dados_exemplo import BRASILIA
from src.repositories.fatura_repository import SqlFaturaRepository
from src.repositories.pagamento_repository import SqlPagamentoRepository
from src.repositories.repasse_repository import SqlRepasseRepository


def test_ativacao_volta_com_etapas_em_ordem_e_percentual(sessoes_com_dados):
    ativacao = SqlAtivacaoRepository(sessoes_com_dados).obter("cliente_01")
    assert ativacao.status is StatusAtivacao.em_andamento
    assert [etapa.ordem for etapa in ativacao.etapas] == [1, 2, 3, 4]
    assert ativacao.calcular_percentual() == 50
    assert ativacao.obter_etapa_atual().id == "etapa_03"


def test_cliente_sem_ativacao_devolve_none(sessoes_com_dados):
    assert SqlAtivacaoRepository(sessoes_com_dados).obter("cliente_03") is None


def test_faturas_do_cliente_da_mais_recente_para_a_mais_antiga(sessoes_com_dados):
    faturas = SqlFaturaRepository(sessoes_com_dados).listar_por_cliente("cliente_01")
    assert [f.id for f in faturas] == ["fatura_02", "fatura_01"]
    assert faturas[1].valor.valor == Decimal("89.90")
    assert faturas[1].vencimento == date(2026, 8, 15)


def test_fatura_de_cliente_inexistente_e_recusada_pela_chave_estrangeira(sessoes_com_dados):
    from datetime import datetime

    with sessoes_com_dados() as sessao:
        sessao.add(
            FaturaModel(
                id="fatura_99", cliente_id="cliente_99", identificador_exibivel="LIC 9999-9",
                competencia="2026-08", valor=Decimal("10.00"), moeda="BRL", status="aberta",
                vencimento=date(2026, 8, 15), atualizado_em=datetime(2026, 8, 1, 9, tzinfo=BRASILIA),
            )
        )
        with pytest.raises(IntegrityError):
            sessao.commit()


def test_pagamento_confirmado_mantem_forma_valor_e_data(sessoes_com_dados):
    pagamento = SqlPagamentoRepository(sessoes_com_dados).obter_por_fatura("fatura_01")
    assert pagamento.status is StatusPagamento.confirmado
    assert pagamento.forma == "pix"
    assert pagamento.valor.valor == Decimal("89.90")
    assert pagamento.pago_em.utcoffset() is not None


def test_repasse_volta_com_a_linha_do_tempo(sessoes_com_dados):
    repasse = SqlRepasseRepository(sessoes_com_dados).obter_por_fatura("fatura_01")
    assert repasse.status is StatusRepasse.em_andamento
    assert [e.id for e in repasse.etapas] == ["repasse_etapa_01", "repasse_etapa_02", "repasse_etapa_03"]
    assert SqlRepasseRepository(sessoes_com_dados).obter_por_fatura("fatura_02") is None
