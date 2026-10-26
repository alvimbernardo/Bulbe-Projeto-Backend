"""Verificacao deterministica de JWT: assinatura, claims e datas."""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

from src.domain.erros import NaoAutenticado
from src.domain.sessao import Sessao
from src.services.token_service import TokenService

SEGREDO = "chave-apenas-dos-testes-com-pelo-menos-64-bytes-para-nao-gerar-alerta"
AGORA = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


@pytest.fixture
def tokens():
    return TokenService(SEGREDO, relogio=lambda: AGORA)


def claims_validos():
    return {
        "sub": "conta_01", "cliente_id": "cliente_01", "jti": "sessao_01",
        "iat": int(AGORA.timestamp()), "exp": int((AGORA + timedelta(minutes=30)).timestamp()),
        "iss": "bulbe-api", "aud": "bulbe-clientes",
    }


def test_emissao_usa_claims_da_sessao_e_algoritmo_fixo(tokens):
    sessao = Sessao("sessao_01", "conta_01", "cliente_01", AGORA, AGORA + tokens.duracao)
    token = tokens.emitir(sessao)
    assert jwt.get_unverified_header(token)["alg"] == "HS256"
    assert tokens.validar(token) == claims_validos()


@pytest.mark.parametrize("campo", ["sub", "cliente_id", "jti", "iat", "exp", "iss", "aud"])
def test_claims_obrigatorios_nao_podem_faltar(tokens, campo):
    claims = claims_validos()
    del claims[campo]
    with pytest.raises(NaoAutenticado):
        tokens.validar(jwt.encode(claims, SEGREDO, algorithm="HS256"))


@pytest.mark.parametrize("alteracoes", [
    {"exp": int(AGORA.timestamp())},
    {"iat": int((AGORA + timedelta(seconds=1)).timestamp())},
    {"exp": int(AGORA.timestamp()) - 1},
    {"iat": "123"}, {"exp": True}, {"exp": 123.5},
    {"iss": "outro-emissor"}, {"aud": "outra-audiencia"},
    {"aud": ["bulbe-clientes"]}, {"sub": 123}, {"cliente_id": ""}, {"jti": 123},
    {"nbf": int((AGORA + timedelta(seconds=1)).timestamp())}, {"nbf": "amanha"},
])
def test_claims_invalidos_sao_recusados(tokens, alteracoes):
    claims = claims_validos() | alteracoes
    with pytest.raises(NaoAutenticado):
        tokens.validar(jwt.encode(claims, SEGREDO, algorithm="HS256"))


@pytest.mark.parametrize("token", ["", "invalido", "a.b.c", "x" * 8193])
def test_token_malformado_retorna_401(tokens, token):
    with pytest.raises(NaoAutenticado) as erro:
        tokens.validar(token)
    assert erro.value.status == 401


def test_assinatura_errada_e_token_alterado_sao_recusados(tokens):
    claims = claims_validos()
    for chave in ("outra-chave-de-testes-com-32-bytes-ou-mais", SEGREDO):
        token = jwt.encode(claims, chave, algorithm="HS256")
        if chave == SEGREDO:
            partes = token.split(".")
            partes[2] = ("A" if partes[2][0] != "A" else "B") + partes[2][1:]
            token = ".".join(partes)
        with pytest.raises(NaoAutenticado):
            tokens.validar(token)


@pytest.mark.parametrize("algoritmo", ["HS384", "none"])
def test_algoritmo_fornecido_pelo_token_nao_e_aceito(tokens, algoritmo):
    token = jwt.encode(claims_validos(), None if algoritmo == "none" else SEGREDO, algorithm=algoritmo)
    with pytest.raises(NaoAutenticado):
        tokens.validar(token)


def test_expiracao_usa_o_relogio_injetado():
    agora = [AGORA]
    tokens = TokenService(SEGREDO, relogio=lambda: agora[0], duracao=timedelta(seconds=10))
    sessao = Sessao("s", "c", "cliente", AGORA, AGORA + tokens.duracao)
    token = tokens.emitir(sessao)
    agora[0] += timedelta(seconds=9)
    assert tokens.validar(token)["jti"] == "s"
    agora[0] += timedelta(seconds=1)
    with pytest.raises(NaoAutenticado):
        tokens.validar(token)


def test_chave_fraca_e_relogio_sem_fuso_sao_recusados():
    with pytest.raises(ValueError):
        TokenService("curta")
    with pytest.raises(ValueError):
        TokenService(SEGREDO, relogio=lambda: datetime(2026, 10, 26)).agora()


def test_chaves_aleatorias_sao_isoladas_por_instancia():
    um = TokenService(relogio=lambda: AGORA)
    outro = TokenService(relogio=lambda: AGORA)
    token = um.emitir(Sessao("s", "c", "cliente", AGORA, AGORA + um.duracao))
    with pytest.raises(NaoAutenticado):
        outro.validar(token)
