"""Testes do objeto de valor Pagina."""

import pytest

from src.domain.erros import DadoInvalido
from src.domain.pagina import Pagina


def test_recorta_a_pagina_pedida():
    pagina = Pagina.de(list(range(1, 46)), page=3, limit=20)
    assert pagina.itens == [41, 42, 43, 44, 45]
    assert pagina.total == 45


def test_pagina_alem_do_fim_vem_vazia():
    assert Pagina.de([1, 2, 3], page=5, limit=2).itens == []


@pytest.mark.parametrize("page, limit", [(0, 20), (1, 0), (1, 101)])
def test_valores_fora_do_intervalo_sao_recusados(page, limit):
    with pytest.raises(DadoInvalido):
        Pagina.de([1, 2, 3], page=page, limit=limit)
