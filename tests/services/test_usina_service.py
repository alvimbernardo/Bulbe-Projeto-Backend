"""Testes do UsinaService (US06)."""

from datetime import datetime

import pytest

from src.domain.erros import DadoInvalido, RecursoNaoEncontrado
from src.domain.usina import StatusUsina
from src.repositories.dados_exemplo import BRASILIA
from src.repositories.usina_repository import InMemoryUsinaRepository
from src.services.usina_service import UsinaService


def test_sem_filtro_lista_so_usinas_ativas(usina_service):
    resultado = usina_service.listar()
    assert [u.id for u in resultado.pagina.itens] == ["usina_01", "usina_02"]
    assert resultado.pagina.total == 2
    assert all(u.status is StatusUsina.ativa for u in resultado.pagina.itens)


def test_filtro_por_status(usina_service):
    resultado = usina_service.listar(status="inativa")
    assert [u.id for u in resultado.pagina.itens] == ["usina_04"]


def test_status_invalido_e_recusado(usina_service):
    with pytest.raises(DadoInvalido) as erro:
        usina_service.listar(status="desligada")
    assert erro.value.status == 400


def test_paginacao(usina_service):
    resultado = usina_service.listar(page=2, limit=1)
    assert [u.id for u in resultado.pagina.itens] == ["usina_02"]
    assert (resultado.pagina.page, resultado.pagina.limit, resultado.pagina.total) == (2, 1, 2)


def test_atualizado_em_e_o_mais_recente_da_listagem(usina_service):
    resultado = usina_service.listar()
    assert resultado.atualizado_em == datetime(2026, 9, 1, 9, 0, tzinfo=BRASILIA)


def test_listagem_vazia_nao_quebra():
    resultado = UsinaService(InMemoryUsinaRepository()).listar()
    assert resultado.pagina.itens == []
    assert resultado.pagina.total == 0
    assert resultado.atualizado_em is None


def test_obter_retorna_usina_de_qualquer_status(usina_service):
    usina = usina_service.obter("usina_04")
    assert usina.status is StatusUsina.inativa
    assert usina.regiao == "Norte de Minas"


def test_obter_usina_inexistente_e_404(usina_service):
    with pytest.raises(RecursoNaoEncontrado) as erro:
        usina_service.obter("usina_99")
    assert erro.value.status == 404
