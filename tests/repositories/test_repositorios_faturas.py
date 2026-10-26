"""Consultas em memoria de faturas e seus recursos associados."""

from src.repositories.dados_faturas import faturas_exemplo, pagamentos_exemplo, repasses_exemplo
from src.repositories.fatura_repository import InMemoryFaturaRepository
from src.repositories.pagamento_repository import InMemoryPagamentoRepository
from src.repositories.repasse_repository import InMemoryRepasseRepository


def test_fatura_repository_isola_cliente_e_ordena_por_competencia():
    repositorio = InMemoryFaturaRepository(faturas_exemplo())
    assert [f.id for f in repositorio.listar_por_cliente("cliente_01")] == ["fatura_02", "fatura_01"]
    assert [f.id for f in repositorio.listar_por_cliente("cliente_02")] == ["fatura_03"]
    assert repositorio.listar_por_cliente("ausente") == []
    assert repositorio.obter("fatura_01").cliente_id == "cliente_01"
    assert repositorio.obter("ausente") is None


def test_recursos_associados_ausentes_sao_none():
    pagamentos = InMemoryPagamentoRepository(pagamentos_exemplo())
    repasses = InMemoryRepasseRepository(repasses_exemplo())
    assert pagamentos.obter_por_fatura("fatura_01").esta_confirmado()
    assert pagamentos.obter_por_fatura("ausente") is None
    assert repasses.obter_por_fatura("fatura_01").obter_etapa_atual().ordem == 2
    assert repasses.obter_por_fatura("fatura_02") is None
