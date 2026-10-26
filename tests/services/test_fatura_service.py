"""Regras de propriedade, periodo e ausencia de dados de faturas."""

from unittest.mock import Mock

import pytest

from src.domain.erros import DadoInvalido, RecursoNaoEncontrado
from src.domain.pagamento import StatusPagamento
from src.domain.repasse import StatusRepasse
from src.repositories.dados_faturas import faturas_exemplo, pagamentos_exemplo, repasses_exemplo
from src.repositories.fatura_repository import InMemoryFaturaRepository
from src.repositories.pagamento_repository import InMemoryPagamentoRepository
from src.repositories.repasse_repository import InMemoryRepasseRepository
from src.services.fatura_service import FaturaService


@pytest.fixture
def service():
    return FaturaService(
        InMemoryFaturaRepository(faturas_exemplo()),
        InMemoryPagamentoRepository(pagamentos_exemplo()),
        InMemoryRepasseRepository(repasses_exemplo()),
    )


def test_lista_faturas_somente_do_cliente_com_mais_recente_primeiro(service):
    resultado = service.listar("cliente_01", page=1, limit=1)
    assert [f.id for f in resultado.pagina.itens] == ["fatura_02"]
    assert resultado.pagina.total == 2
    assert resultado.atualizado_em == faturas_exemplo()[1].atualizado_em
    assert service.listar("cliente_01", page=2, limit=1).pagina.itens[0].id == "fatura_01"


def test_filtro_competencia_e_ausencia_de_periodo(service):
    resultado = service.listar("cliente_01", "2026-08")
    assert [f.id for f in resultado.pagina.itens] == ["fatura_01"]
    vazio = service.listar("cliente_01", "2026-10")
    assert vazio.pagina.itens == []
    assert vazio.pagina.total == 0
    assert vazio.atualizado_em is None


@pytest.mark.parametrize("competencia", ["", "agosto", "2026-8", "2026-13", "1999-01"])
def test_competencia_invalida_e_recusada_antes_de_consultar_repositorio(competencia):
    faturas = Mock()
    service = FaturaService(faturas, Mock(), Mock())
    with pytest.raises(DadoInvalido):
        service.listar("cliente_01", competencia)
    faturas.listar_por_cliente.assert_not_called()


def test_lista_defende_propriedade_mesmo_se_repositorio_retornar_outro_cliente():
    faturas = Mock()
    faturas.listar_por_cliente.return_value = faturas_exemplo()
    service = FaturaService(faturas, Mock(), Mock())
    assert [f.id for f in service.listar("cliente_02").pagina.itens] == ["fatura_03"]


@pytest.mark.parametrize("metodo", ["obter", "pagamento", "repasse"])
@pytest.mark.parametrize("fatura_id", ["ausente", "fatura_03"])
def test_fatura_ausente_ou_de_outro_cliente_retorna_mesmo_404(service, metodo, fatura_id):
    with pytest.raises(RecursoNaoEncontrado) as erro:
        getattr(service, metodo)("cliente_01", fatura_id)
    assert str(erro.value) == "Fatura nao encontrada."


def test_nao_consulta_pagamento_nem_repasse_sem_confirmar_propriedade():
    faturas, pagamentos, repasses = Mock(), Mock(), Mock()
    faturas.obter.return_value = faturas_exemplo()[2]
    service = FaturaService(faturas, pagamentos, repasses)
    for metodo in (service.pagamento, service.repasse):
        with pytest.raises(RecursoNaoEncontrado):
            metodo("cliente_01", "fatura_03")
    pagamentos.obter_por_fatura.assert_not_called()
    repasses.obter_por_fatura.assert_not_called()


def test_pagamento_confirmado_pendente_e_recusado_sao_estados_distintos(service):
    assert service.pagamento("cliente_01", "fatura_01").esta_confirmado()
    assert service.pagamento("cliente_01", "fatura_02").status is StatusPagamento.pendente
    assert service.pagamento("cliente_02", "fatura_03").foi_recusado()


def test_pagamento_ausente_nao_e_inventado_como_recusado():
    service = FaturaService(
        InMemoryFaturaRepository(faturas_exemplo()), InMemoryPagamentoRepository(), InMemoryRepasseRepository(),
    )
    with pytest.raises(RecursoNaoEncontrado, match="Nao ha pagamento"):
        service.pagamento("cliente_01", "fatura_01")


def test_repasse_ordenado_e_ausente(service):
    repasse = service.repasse("cliente_01", "fatura_01")
    assert repasse.status is StatusRepasse.em_andamento
    assert [e.ordem for e in repasse.etapas_ordenadas()] == [1, 2, 3]
    assert repasse.obter_etapa_atual().id == "repasse_etapa_02"
    with pytest.raises(RecursoNaoEncontrado, match="Nao ha repasse"):
        service.repasse("cliente_01", "fatura_02")


@pytest.mark.parametrize("page,limit", [(0, 20), (1, 0), (1, 101)])
def test_paginacao_invalida(service, page, limit):
    with pytest.raises(DadoInvalido):
        service.listar("cliente_01", page=page, limit=limit)
