"""Testes de integracao dos repositorios SQL de clientes, contas, sessoes e preferencias."""

from datetime import datetime, timedelta, timezone

import pytest

from src.domain.conta import Conta, ContaJaExistente
from src.domain.preferencia_notificacao import PreferenciaNotificacao
from src.domain.sessao import Sessao
from src.repositories.cliente_repository import SqlClienteRepository
from src.repositories.conta_repository import SqlContaRepository
from src.repositories.dados_contas import SENHA_EXEMPLO
from src.repositories.preferencia_repository import SqlPreferenciaRepository
from src.repositories.sessao_repository import SqlSessaoRepository

AGORA = datetime(2026, 11, 4, 12, 0, tzinfo=timezone.utc)


def nova_sessao(sessao_id="sessao_teste", minutos=30):
    return Sessao(sessao_id, "conta_01", "cliente_01", AGORA, AGORA + timedelta(minutes=minutos))


def test_cliente_e_encontrado_pelo_identificador(sessoes_com_dados):
    cliente = SqlClienteRepository(sessoes_com_dados).obter_por_identificador("BULBE-003")
    assert cliente.id == "cliente_03"
    assert cliente.confirmar_vinculo("cliente03@exemplo.com", "345678") is True


def test_conta_do_seed_autentica_com_a_senha_de_exemplo(sessoes_com_dados):
    conta = SqlContaRepository(sessoes_com_dados).obter_por_email("Cliente01@Exemplo.com")
    assert conta.cliente_id == "cliente_01"
    assert conta.validar_senha(SENHA_EXEMPLO) is True


def test_banco_recusa_segunda_conta_para_o_mesmo_cliente(sessoes_com_dados):
    contas = SqlContaRepository(sessoes_com_dados)
    duplicada = Conta.criar("conta_dup", "cliente_01", "outro@exemplo.com", "Senha12345", AGORA)
    with pytest.raises(ContaJaExistente):
        contas.salvar(duplicada)
    assert contas.obter("conta_dup") is None


def test_banco_recusa_email_repetido(sessoes_com_dados):
    contas = SqlContaRepository(sessoes_com_dados)
    repetida = Conta.criar("conta_dup", "cliente_03", "cliente01@exemplo.com", "Senha12345", AGORA)
    with pytest.raises(ContaJaExistente):
        contas.salvar(repetida)


def test_sessao_invalidada_continua_invalida_em_nova_leitura(sessoes_com_dados):
    repositorio = SqlSessaoRepository(sessoes_com_dados)
    repositorio.salvar(nova_sessao())
    assert repositorio.invalidar("sessao_teste", AGORA + timedelta(minutes=1)) is True
    assert repositorio.invalidar("sessao_teste", AGORA + timedelta(minutes=2)) is False
    assert repositorio.obter("sessao_teste").esta_valida(AGORA + timedelta(minutes=3)) is False


def test_limpar_expiradas_mantem_somente_sessoes_validas(sessoes_com_dados):
    repositorio = SqlSessaoRepository(sessoes_com_dados)
    repositorio.salvar(nova_sessao("sessao_curta", minutos=5))
    repositorio.salvar(nova_sessao("sessao_longa", minutos=60))
    repositorio.limpar_expiradas(AGORA + timedelta(minutes=10))
    assert repositorio.obter("sessao_curta") is None
    assert repositorio.obter("sessao_longa") is not None


def test_preferencia_repetida_nao_altera_o_registro(sessoes_com_dados):
    repositorio = SqlPreferenciaRepository(sessoes_com_dados)
    primeira = repositorio.salvar(PreferenciaNotificacao.criar("cliente_01", True, ["email"], AGORA))
    repetida = repositorio.salvar(
        PreferenciaNotificacao.criar("cliente_01", True, ["email"], AGORA + timedelta(hours=1))
    )
    assert repetida == primeira
    desligada = repositorio.salvar(
        PreferenciaNotificacao.criar("cliente_01", False, [], AGORA + timedelta(hours=2))
    )
    assert desligada.habilitada is False
    assert desligada.canais == ()
