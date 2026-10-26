"""Busca e garantia atomica de unicidade no repositorio de contas."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace

import pytest

from src.domain.conta import ContaJaExistente
from src.repositories.cliente_repository import InMemoryClienteRepository
from src.repositories.conta_repository import InMemoryContaRepository
from src.repositories.dados_contas import clientes_exemplo, contas_exemplo


def test_buscas_por_id_identificador_email_e_cliente():
    clientes = InMemoryClienteRepository(clientes_exemplo())
    contas = InMemoryContaRepository(contas_exemplo())
    assert clientes.obter("cliente_01") is clientes.obter_por_identificador("BULBE-001")
    assert contas.obter("conta_01") is contas.obter_por_cliente("cliente_01")
    assert contas.obter_por_email(" CLIENTE01@EXEMPLO.COM ").id == "conta_01"
    assert clientes.obter("ausente") is None
    assert contas.obter("ausente") is None
    assert contas.obter_por_email("ausente@exemplo.com") is None


@pytest.mark.parametrize("alteracoes", [
    {"id": "conta_01", "cliente_id": "outro", "email": "outro@exemplo.com"},
    {"id": "outra", "email": "outro@exemplo.com"},
    {"id": "outra", "cliente_id": "outro"},
])
def test_recusa_duplicidade_de_id_cliente_ou_email(alteracoes):
    original = contas_exemplo()[0]
    repo = InMemoryContaRepository([original])
    with pytest.raises(ContaJaExistente):
        repo.salvar(replace(original, **alteracoes))


def test_cadastros_concorrentes_nao_criam_duas_contas_para_mesmo_cliente():
    original = contas_exemplo()[0]
    repo = InMemoryContaRepository()
    candidatos = [replace(original, id=f"conta_{n}", email=f"cliente{n}@exemplo.com") for n in range(12)]

    def tentar_salvar(conta):
        try:
            repo.salvar(conta)
            return True
        except ContaJaExistente:
            return False

    with ThreadPoolExecutor(max_workers=6) as executor:
        resultados = list(executor.map(tentar_salvar, candidatos))
    assert resultados.count(True) == 1
    assert repo.obter_por_cliente(original.cliente_id) is not None


def test_seeds_sao_instancias_novas_a_cada_aplicacao():
    primeiro = clientes_exemplo()
    segundo = clientes_exemplo()
    primeiro[0].status = "inativo"
    assert segundo[0].esta_ativo()
    contas_exemplo()[0].status = "bloqueada"
    assert contas_exemplo()[0].esta_ativa()
