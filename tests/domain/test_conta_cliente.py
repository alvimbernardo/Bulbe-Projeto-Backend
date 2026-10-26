"""Senha protegida e confirmacao do vinculo corporativo."""

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.domain.cliente import normalizar_email
from src.domain.conta import Conta, validar_senha_de_cadastro
from src.domain.erros import DadoInvalido
from src.repositories.dados_contas import clientes_exemplo, contas_exemplo, SENHA_EXEMPLO


def test_senha_exemplo_conferida_por_bcrypt_sem_exposicao_no_repr():
    primeira, segunda = contas_exemplo()
    assert primeira.validar_senha(SENHA_EXEMPLO)
    assert segunda.validar_senha(SENHA_EXEMPLO)
    assert primeira.senha_hash != segunda.senha_hash
    assert not primeira.validar_senha("SenhaIncorreta")
    assert not primeira.validar_senha("á" * 40)
    assert not primeira.validar_senha("")
    assert "senha_hash" not in repr(primeira)
    assert SENHA_EXEMPLO not in repr(primeira)


@pytest.mark.parametrize("senha", ["curta", "a" * 73, "á" * 37])
def test_senhas_fora_dos_limites_retorna_400(senha):
    with pytest.raises(DadoInvalido) as erro:
        validar_senha_de_cadastro(senha)
    assert erro.value.status == 400
    assert erro.value.detalhes[0]["campo"] == "senha"


def test_criacao_gera_salt_novo_e_guarda_somente_hash():
    instante = datetime.now(timezone.utc)
    primeira = Conta.criar("conta_a", "cliente_a", "a@exemplo.com", SENHA_EXEMPLO, instante)
    segunda = Conta.criar("conta_b", "cliente_b", "b@exemplo.com", SENHA_EXEMPLO, instante)
    assert primeira.senha_hash != segunda.senha_hash
    assert primeira.validar_senha(SENHA_EXEMPLO)
    assert not hasattr(primeira, "senha")


def test_senha_com_72_bytes_nao_e_truncada():
    senha = "a" * 72
    conta = Conta.criar("conta_a", "cliente_a", "a@exemplo.com", senha, datetime.now(timezone.utc))
    assert conta.validar_senha(senha)
    assert not conta.validar_senha(senha + "a")


def test_conta_exige_vinculo_hash_e_instante_com_fuso():
    conta = contas_exemplo()[0]
    for alteracoes in ({"cliente_id": ""}, {"senha_hash": b"texto-puro"}, {"criada_em": datetime(2026, 8, 1)}):
        with pytest.raises(DadoInvalido):
            replace(conta, **alteracoes)
    assert not replace(conta, status="bloqueada").esta_ativa()
    assert not replace(conta, status="inativa").esta_ativa()


@pytest.mark.parametrize("codigo", [None, "", "errado", "çãõ"])
def test_identificador_sem_codigo_correto_nao_confirma_vinculo(codigo):
    cliente = clientes_exemplo()[2]
    assert not cliente.confirmar_vinculo(cliente.email, codigo)


def test_vinculo_exige_email_codigo_e_cliente_ativo():
    cliente = clientes_exemplo()[2]
    assert cliente.confirmar_vinculo(" CLIENTE03@EXEMPLO.COM ", "345678")
    assert not cliente.confirmar_vinculo("outra@exemplo.com", "345678")
    assert not replace(cliente, status="inativo").confirmar_vinculo(cliente.email, "345678")
    assert "345678" not in repr(cliente)
    assert "BULBE-003" not in repr(cliente)


@pytest.mark.parametrize("email", ["sem-arroba", "a@@b.com", "a@b..com", "a b@c.com", "a@"])
def test_email_malformado_retorna_400(email):
    with pytest.raises(DadoInvalido):
        normalizar_email(email)
