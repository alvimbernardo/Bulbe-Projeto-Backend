"""Regras de validade e revogacao da entidade Sessao."""

from datetime import datetime, timedelta, timezone

import pytest

from src.domain.sessao import Sessao

AGORA = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


def test_sessao_so_vale_no_intervalo_e_antes_de_invalidada():
    sessao = Sessao("s", "c", "cliente", AGORA, AGORA + timedelta(minutes=30))
    assert sessao.esta_valida(AGORA)
    assert not sessao.esta_valida(AGORA - timedelta(seconds=1))
    assert not sessao.esta_valida(sessao.expira_em)
    assert sessao.invalidar(AGORA)
    assert not sessao.esta_valida(AGORA)
    assert not sessao.invalidar(AGORA)


@pytest.mark.parametrize("criacao,expiracao", [
    (AGORA, AGORA), (AGORA, AGORA - timedelta(seconds=1)),
    (AGORA.replace(tzinfo=None), AGORA), (AGORA, AGORA.replace(tzinfo=None)),
])
def test_sessao_recusa_datas_incoerentes(criacao, expiracao):
    with pytest.raises(ValueError):
        Sessao("s", "c", "cliente", criacao, expiracao)
