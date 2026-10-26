"""Autorizacao exige vinculo antes de revelar existencia dos recursos."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from src.domain.erros import AcessoNegado, RecursoNaoEncontrado
from src.repositories.dados_contas import clientes_exemplo
from src.services.autorizacao_service import AutorizacaoService


def test_outro_cliente_e_403_sem_consultar_repositorio():
    repositorio = Mock()
    with pytest.raises(AcessoNegado):
        AutorizacaoService(repositorio).obter_cliente(SimpleNamespace(cliente_id="cliente_01"), "cliente_02")
    repositorio.obter.assert_not_called()


def test_proprio_cliente_ausente_e_404():
    repositorio = Mock()
    repositorio.obter.return_value = None
    with pytest.raises(RecursoNaoEncontrado):
        AutorizacaoService(repositorio).obter_cliente(SimpleNamespace(cliente_id="ausente"), "ausente")


def test_cliente_inativo_e_recusado():
    repositorio = Mock()
    cliente = clientes_exemplo()[0]
    cliente.status = "inativo"
    repositorio.obter.return_value = cliente
    with pytest.raises(AcessoNegado):
        AutorizacaoService(repositorio).obter_cliente(SimpleNamespace(cliente_id=cliente.id), cliente.id)


def test_retorna_cliente_proprio_ativo():
    repositorio = Mock()
    cliente = clientes_exemplo()[0]
    repositorio.obter.return_value = cliente
    assert AutorizacaoService(repositorio).obter_cliente(SimpleNamespace(cliente_id=cliente.id), cliente.id) is cliente
