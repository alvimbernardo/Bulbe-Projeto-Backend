"""Testes dos servicos isolados dos repositorios com Mock."""

from unittest.mock import Mock

import pytest

from src.domain.erros import DadoInvalido, FonteIndisponivel, RecursoNaoEncontrado
from src.repositories.dados_exemplo import depoimentos_exemplo, usinas_exemplo
from src.services.credito_service import CreditoService
from src.services.depoimento_service import DepoimentoService
from src.services.usina_service import UsinaService


def test_usina_service_consulta_o_repositorio_pelo_id():
    repositorio = Mock()
    repositorio.obter.return_value = None
    service = UsinaService(repositorio)

    with pytest.raises(RecursoNaoEncontrado):
        service.obter("usina_07")

    repositorio.obter.assert_called_once_with("usina_07")


def test_credito_service_nao_busca_credito_de_usina_inexistente():
    usinas = Mock()
    usinas.obter.return_value = None
    creditos = Mock()
    service = CreditoService(usinas, creditos)

    with pytest.raises(RecursoNaoEncontrado):
        service.creditos_da_usina("usina_99", "2026-08")

    usinas.obter.assert_called_once_with("usina_99")
    creditos.obter.assert_not_called()


def test_credito_service_recusa_competencia_antes_de_consultar_repositorios():
    usinas = Mock()
    creditos = Mock()
    service = CreditoService(usinas, creditos)

    with pytest.raises(DadoInvalido):
        service.resumo("agosto")

    usinas.listar.assert_not_called()
    creditos.listar_por_competencia.assert_not_called()


def test_credito_service_resumo_sem_creditos_das_ativas_e_indisponivel():
    usinas = Mock()
    usinas.listar.return_value = usinas_exemplo()
    creditos = Mock()
    creditos.listar_por_competencia.return_value = []
    service = CreditoService(usinas, creditos)

    with pytest.raises(FonteIndisponivel) as erro:
        service.resumo("2026-08")

    assert erro.value.status == 503


def test_depoimento_service_esconde_depoimento_nao_autorizado():
    nao_autorizado = next(d for d in depoimentos_exemplo() if not d.publicacao_autorizada)
    repositorio = Mock()
    repositorio.obter.return_value = nao_autorizado
    service = DepoimentoService(repositorio)

    with pytest.raises(RecursoNaoEncontrado):
        service.obter(nao_autorizado.id)

    repositorio.obter.assert_called_once_with(nao_autorizado.id)
