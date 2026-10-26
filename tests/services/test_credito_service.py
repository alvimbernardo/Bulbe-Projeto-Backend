"""Testes do CreditoService (US07 e US08)."""

from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.competencia import Competencia
from src.domain.erros import DadoInvalido, FonteIndisponivel, RecursoNaoEncontrado
from src.repositories.dados_exemplo import BRASILIA


def test_creditos_da_usina_na_competencia(credito_service):
    credito = credito_service.creditos_da_usina("usina_01", "2026-08")
    assert credito.creditos.valor == Decimal("43980.75")
    assert credito.creditos.moeda == "BRL"
    assert str(credito.competencia) == "2026-08"


@pytest.mark.parametrize("competencia", [None, "", "2026-8", "08-2026", "2026-13"])
def test_competencia_ausente_ou_invalida_e_400(credito_service, competencia):
    with pytest.raises(DadoInvalido) as erro:
        credito_service.creditos_da_usina("usina_01", competencia)
    assert erro.value.status == 400


def test_usina_inexistente_e_404(credito_service):
    with pytest.raises(RecursoNaoEncontrado):
        credito_service.creditos_da_usina("usina_99", "2026-08")


def test_periodo_sem_dado_e_404_e_nao_zero(credito_service):
    with pytest.raises(RecursoNaoEncontrado) as erro:
        credito_service.creditos_da_usina("usina_01", "2026-09")
    assert "2026-09" in erro.value.mensagem


def test_resumo_soma_so_usinas_ativas_da_competencia(credito_service):
    resumo = credito_service.resumo("2026-08")
    assert resumo.total_creditos.valor == Decimal("74096.15")
    assert resumo.quantidade_usinas == 2
    assert resumo.criterio == "usinas_ativas"
    assert resumo.atualizado_em == datetime(2026, 9, 10, 9, 0, tzinfo=BRASILIA)


def test_resumo_nao_mistura_competencias(credito_service):
    assert credito_service.resumo("2026-07").total_creditos.valor == Decimal("69980.50")


def test_resumo_por_outro_status(credito_service):
    resumo = credito_service.resumo("2026-08", status_usina="em_manutencao")
    assert resumo.total_creditos.valor == Decimal("9870.00")
    assert resumo.quantidade_usinas == 1
    assert resumo.criterio == "usinas_em_manutencao"


def test_resumo_com_credito_faltando_e_503(credito_service):
    with pytest.raises(FonteIndisponivel) as erro:
        credito_service.resumo("2026-09")
    assert erro.value.status == 503


def test_resumo_com_status_invalido_e_400(credito_service):
    with pytest.raises(DadoInvalido) as erro:
        credito_service.resumo("2026-08", status_usina="desligada")
    assert erro.value.detalhes[0]["campo"] == "status_usina"


def test_resumo_sem_competencia_e_400(credito_service):
    with pytest.raises(DadoInvalido):
        credito_service.resumo(None)


def test_aceita_competencia_ja_convertida(credito_service):
    credito = credito_service.creditos_da_usina("usina_01", Competencia(2026, 8))
    assert credito.creditos.valor == Decimal("43980.75")
    resumo = credito_service.resumo(Competencia(2026, 8))
    assert resumo.total_creditos.valor == Decimal("74096.15")
