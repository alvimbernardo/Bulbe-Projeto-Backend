"""Consultas e isolamento do repositorio de ativacoes em memoria."""

from src.repositories.ativacao_repository import InMemoryAtivacaoRepository
from src.repositories.dados_ativacao import ativacoes_exemplo


def test_repositorio_consulta_somente_cliente_solicitado():
    repositorio = InMemoryAtivacaoRepository(ativacoes_exemplo())
    assert repositorio.obter("cliente_01").cliente_id == "cliente_01"
    assert repositorio.obter("cliente_02").status == "concluida"
    assert repositorio.obter("cliente_03") is None


def test_repositorio_vazio_e_seeds_isolados():
    assert InMemoryAtivacaoRepository().obter("cliente_01") is None
    primeira = ativacoes_exemplo()[0]
    segunda = ativacoes_exemplo()[0]
    assert primeira is not segunda
    assert primeira.etapas[0] is not segunda.etapas[0]
