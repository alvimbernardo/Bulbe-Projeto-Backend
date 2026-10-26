"""Primeiro acesso elegivel, duplicidade e confirmacao do vinculo."""

from dataclasses import replace

import pytest

from src.domain.cliente import ClienteInelegivel
from src.domain.conta import ContaJaExistente
from src.domain.erros import DadoInvalido
from src.repositories.cliente_repository import InMemoryClienteRepository
from src.repositories.conta_repository import InMemoryContaRepository
from src.repositories.dados_contas import clientes_exemplo, contas_exemplo, SENHA_EXEMPLO
from src.services.conta_service import ContaService


@pytest.fixture
def cadastro():
    contas = InMemoryContaRepository(contas_exemplo())
    return ContaService(InMemoryClienteRepository(clientes_exemplo()), contas), contas


def test_cadastro_cria_conta_ativa_e_vinculada_sem_guardar_senha(cadastro):
    service, contas = cadastro
    conta = service.criar(" CLIENTE03@EXEMPLO.COM ", SENHA_EXEMPLO, "BULBE-003", "345678")
    assert conta.cliente_id == "cliente_03"
    assert conta.email == "cliente03@exemplo.com"
    assert conta.esta_ativa()
    assert conta.validar_senha(SENHA_EXEMPLO)
    assert conta.criada_em.utcoffset() is not None
    assert contas.obter_por_cliente("cliente_03") is conta
    assert contas.obter_por_email("CLIENTE03@EXEMPLO.COM") is conta


def test_cliente_ja_cadastrado_retorna_409(cadastro):
    service, _ = cadastro
    with pytest.raises(ContaJaExistente) as erro:
        service.criar("cliente01@exemplo.com", SENHA_EXEMPLO, "BULBE-001", "123456")
    assert erro.value.status == 409


@pytest.mark.parametrize("email,identificador,codigo", [
    ("cliente03@exemplo.com", "inexistente", "345678"),
    ("cliente04@exemplo.com", "BULBE-004", "456789"),
    ("outra@exemplo.com", "BULBE-003", "345678"),
    ("cliente03@exemplo.com", "BULBE-003", None),
    ("cliente03@exemplo.com", "BULBE-003", "incorreto"),
])
def test_vinculo_nao_confirmado_ou_cliente_inelegivel_retorna_422(cadastro, email, identificador, codigo):
    service, contas = cadastro
    with pytest.raises(ClienteInelegivel) as erro:
        service.criar(email, SENHA_EXEMPLO, identificador, codigo)
    assert erro.value.status == 422
    assert contas.obter_por_cliente("cliente_03") is None


def test_campos_invalidos_sao_400_mesmo_sem_passar_pelo_controller(cadastro):
    service, _ = cadastro
    with pytest.raises(DadoInvalido):
        service.criar("invalido", SENHA_EXEMPLO, "BULBE-003", "345678")
    with pytest.raises(DadoInvalido):
        service.criar("cliente03@exemplo.com", "curta", "BULBE-003", "345678")
    with pytest.raises(DadoInvalido):
        service.criar("cliente03@exemplo.com", SENHA_EXEMPLO, "   ", "345678")


def test_email_ja_associado_a_outra_conta_nao_cria_segunda_conta():
    clientes = clientes_exemplo()
    clientes[2] = replace(clientes[2], email="cliente01@exemplo.com")
    service = ContaService(InMemoryClienteRepository(clientes), InMemoryContaRepository(contas_exemplo()))
    with pytest.raises(ContaJaExistente):
        service.criar("cliente01@exemplo.com", SENHA_EXEMPLO, "BULBE-003", "345678")
