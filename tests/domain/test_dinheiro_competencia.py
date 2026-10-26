"""Testes dos objetos de valor Dinheiro e Competencia."""

from decimal import Decimal

import pytest

from src.domain.competencia import Competencia
from src.domain.dinheiro import Dinheiro
from src.domain.erros import DadoInvalido


def test_dinheiro_arredonda_para_duas_casas():
    assert Dinheiro(Decimal("10.005")).valor == Decimal("10.01")


def test_dinheiro_soma_sem_erro_de_float():
    assert (Dinheiro(Decimal("0.10")) + Dinheiro(Decimal("0.20"))).valor == Decimal("0.30")


def test_dinheiro_nao_aceita_valor_negativo():
    with pytest.raises(DadoInvalido):
        Dinheiro(Decimal("-1"))


def test_dinheiro_nao_soma_moedas_diferentes():
    with pytest.raises(DadoInvalido):
        Dinheiro(Decimal("10"), "BRL") + Dinheiro(Decimal("10"), "USD")


def test_competencia_de_texto_valido():
    competencia = Competencia.de_texto("2026-08")
    assert (competencia.ano, competencia.mes) == (2026, 8)
    assert str(competencia) == "2026-08"


@pytest.mark.parametrize("texto", ["2026-13", "2026-00", "08-2026", "2026/08", "", "2026-8"])
def test_competencia_invalida_vira_erro_400(texto):
    with pytest.raises(DadoInvalido) as erro:
        Competencia.de_texto(texto)
    assert erro.value.status == 400
    assert erro.value.detalhes[0]["campo"] == "competencia"


@pytest.mark.parametrize("moeda", ["RS", "REAL", "R1"])
def test_dinheiro_com_moeda_fora_do_padrao_e_recusado(moeda):
    with pytest.raises(DadoInvalido) as erro:
        Dinheiro(Decimal("10.00"), moeda)
    assert erro.value.detalhes[0]["campo"] == "moeda"
