"""Servico da ativacao com repositorio real e mock."""

from unittest.mock import Mock

import pytest

from src.domain.erros import RecursoNaoEncontrado
from src.repositories.ativacao_repository import InMemoryAtivacaoRepository
from src.repositories.dados_ativacao import ativacoes_exemplo
from src.services.ativacao_service import AtivacaoService


def test_obter_e_listar_etapas_preservam_mesmo_conjunto_e_atualizacao():
    service = AtivacaoService(InMemoryAtivacaoRepository(ativacoes_exemplo()))
    ativacao = service.obter("cliente_01")
    listagem = service.listar_etapas("cliente_01")
    assert listagem.cliente_id == ativacao.cliente_id
    assert listagem.etapas == ativacao.etapas
    assert listagem.atualizado_em == ativacao.atualizado_em


@pytest.mark.parametrize("metodo", ["obter", "listar_etapas"])
def test_cliente_sem_ativacao_retorna_404(metodo):
    repositorio = Mock()
    repositorio.obter.return_value = None
    with pytest.raises(RecursoNaoEncontrado) as erro:
        getattr(AtivacaoService(repositorio), metodo)("cliente_03")
    assert erro.value.status == 404
    repositorio.obter.assert_called_once_with("cliente_03")
