"""Testes do DepoimentoService (US11)."""

import pytest

from src.domain.erros import DadoInvalido, RecursoNaoEncontrado


def test_lista_so_depoimentos_autorizados(depoimento_service):
    pagina = depoimento_service.listar()
    assert [d.id for d in pagina.itens] == ["depoimento_01", "depoimento_02"]
    assert pagina.total == 2


def test_dados_publicos_nao_expoem_cliente(depoimento_service):
    for depoimento in depoimento_service.listar().itens:
        assert "cliente_id" not in depoimento.dados_publicos()


def test_obter_depoimento_autorizado(depoimento_service):
    assert depoimento_service.obter("depoimento_02").nome_publico == "Comercio de Janauba"


def test_depoimento_nao_autorizado_e_404(depoimento_service):
    with pytest.raises(RecursoNaoEncontrado) as erro:
        depoimento_service.obter("depoimento_03")
    assert erro.value.status == 404


def test_depoimento_inexistente_e_404(depoimento_service):
    with pytest.raises(RecursoNaoEncontrado):
        depoimento_service.obter("depoimento_99")


def test_paginacao_invalida_e_400(depoimento_service):
    with pytest.raises(DadoInvalido):
        depoimento_service.listar(limit=101)
