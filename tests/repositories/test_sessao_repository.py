"""Revogacao atomica e limpeza das sessoes em memoria."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from src.domain.sessao import Sessao
from src.repositories.sessao_repository import InMemorySessaoRepository

AGORA = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


def test_apenas_um_logout_concorrente_invalida_sessao():
    repositorio = InMemorySessaoRepository()
    repositorio.salvar(Sessao("s", "c", "cliente", AGORA, AGORA + timedelta(minutes=30)))
    with ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(lambda _: repositorio.invalidar("s", AGORA), range(8)))
    assert resultados.count(True) == 1
    assert not repositorio.obter("s").esta_valida(AGORA)
    assert not repositorio.invalidar("ausente", AGORA)


def test_limpeza_remove_revogadas_e_expiradas_sem_apagar_ativas():
    repositorio = InMemorySessaoRepository()
    for identificador, minutos in (("ativa", 30), ("expirada", 1), ("revogada", 30)):
        repositorio.salvar(Sessao(identificador, "c", "cliente", AGORA, AGORA + timedelta(minutes=minutos)))
    repositorio.invalidar("revogada", AGORA)
    repositorio.limpar_expiradas(AGORA + timedelta(minutes=2))
    assert repositorio.obter("ativa") is not None
    assert repositorio.obter("expirada") is None
    assert repositorio.obter("revogada") is None
