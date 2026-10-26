"""Login e logout com repositorios reais e relogio injetado, sem HTTP."""

from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
import pytest

from src.domain.conta import Conta
from src.domain.erros import ErroDeNegocio, NaoAutenticado
from src.repositories.conta_repository import InMemoryContaRepository
from src.repositories.sessao_repository import InMemorySessaoRepository
from src.services.sessao_service import SessaoService
from src.services.token_service import TokenService

AGORA = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)
SEGREDO = "chave-apenas-dos-testes-de-sessao-com-32-bytes-ou-mais"
# Custo reduzido somente nesta fixture de teste; a producao e os seeds usam 12.
HASH_TESTE = bcrypt.hashpw(b"Senha2026!", bcrypt.gensalt(rounds=4))


@pytest.fixture
def contexto():
    agora = [AGORA]
    conta = Conta("conta_01", "cliente_01", "cliente@exemplo.com", HASH_TESTE, "ativa", AGORA)
    contas = InMemoryContaRepository([conta])
    sessoes = InMemorySessaoRepository()
    tokens = TokenService(SEGREDO, relogio=lambda: agora[0])
    service = SessaoService(contas, sessoes, tokens)
    return service, conta, contas, sessoes, tokens, agora


def test_login_valido_emite_token_e_sessao_vinculada(contexto):
    service, conta, _, _, tokens, _ = contexto
    sessao, token = service.autenticar(" CLIENTE@EXEMPLO.COM ", "Senha2026!")
    assert sessao.conta_id == conta.id
    assert sessao.cliente_id == conta.cliente_id
    assert sessao.expira_em == AGORA + tokens.duracao
    assert service.validar_token(token) is sessao


@pytest.mark.parametrize("email,senha", [
    ("cliente@exemplo.com", "errada"), ("ausente@exemplo.com", "errada"),
])
def test_credenciais_incorretas_retornam_mesmo_erro(contexto, email, senha):
    service = contexto[0]
    with pytest.raises(NaoAutenticado) as erro:
        service.autenticar(email, senha)
    assert (erro.value.status, erro.value.mensagem) == (401, "Credenciais invalidas.")


@pytest.mark.parametrize("status", ["bloqueada", "inativa"])
def test_login_recusa_conta_nao_ativa(contexto, status):
    service, conta, *_ = contexto
    conta.status = status
    with pytest.raises(NaoAutenticado):
        service.autenticar(conta.email, "Senha2026!")


def test_logout_invalida_token_imediatamente_sem_invalidar_outra_sessao(contexto):
    service = contexto[0]
    _, token = service.autenticar("cliente@exemplo.com", "Senha2026!")
    outra, outro_token = service.autenticar("cliente@exemplo.com", "Senha2026!")
    service.encerrar(token)
    with pytest.raises(NaoAutenticado):
        service.validar_token(token)
    with pytest.raises(NaoAutenticado):
        service.encerrar(token)
    assert service.validar_token(outro_token) is outra


def test_expiracao_da_sessao_recusa_reutilizacao(contexto):
    service, _, _, _, tokens, agora = contexto
    sessao, token = service.autenticar("cliente@exemplo.com", "Senha2026!")
    agora[0] = sessao.expira_em
    with pytest.raises(NaoAutenticado):
        service.validar_token(token)


@pytest.mark.parametrize("mudanca", ["status", "vinculo", "conta_removida"])
def test_sessao_deixa_de_valer_se_conta_perde_ativacao_ou_vinculo(contexto, mudanca, monkeypatch):
    service, conta, contas, *_ = contexto
    _, token = service.autenticar(conta.email, "Senha2026!")
    if mudanca == "status":
        conta.status = "bloqueada"
    elif mudanca == "vinculo":
        conta.cliente_id = "cliente_02"
    else:
        monkeypatch.setattr(contas, "obter", lambda _: None)
    with pytest.raises(NaoAutenticado):
        service.validar_token(token)


@pytest.mark.parametrize("claim,valor", [
    ("sub", "conta_02"), ("cliente_id", "cliente_02"), ("jti", "sessao_inexistente"),
    ("iat", int(AGORA.timestamp()) - 1),
    ("exp", int((AGORA + timedelta(minutes=60)).timestamp())),
])
def test_claims_assinados_precisam_corresponder_ao_estado_da_sessao(contexto, claim, valor):
    service, _, _, _, tokens, _ = contexto
    _, token = service.autenticar("cliente@exemplo.com", "Senha2026!")
    claims = tokens.validar(token)
    claims[claim] = valor
    forjado = jwt.encode(claims, SEGREDO, algorithm="HS256")
    with pytest.raises(NaoAutenticado):
        service.validar_token(forjado)


def test_bloqueio_de_tentativas_expira_sem_sleep_e_nao_e_burlado_por_maiusculas(contexto):
    service, _, _, _, _, agora = contexto
    for _ in range(5):
        with pytest.raises(NaoAutenticado):
            service.autenticar("cliente@exemplo.com", "errada")
    with pytest.raises(ErroDeNegocio) as erro:
        service.autenticar(" CLIENTE@EXEMPLO.COM ", "Senha2026!")
    assert (erro.value.status, erro.value.codigo) == (429, "MUITAS_TENTATIVAS")
    agora[0] += timedelta(minutes=5)
    assert service.autenticar("cliente@exemplo.com", "Senha2026!")[0].conta_id == "conta_01"


def test_login_valido_limpa_contador_de_falhas(contexto):
    service = contexto[0]
    for _ in range(4):
        with pytest.raises(NaoAutenticado):
            service.autenticar("cliente@exemplo.com", "errada")
    service.autenticar("cliente@exemplo.com", "Senha2026!")
    for _ in range(4):
        with pytest.raises(NaoAutenticado):
            service.autenticar("cliente@exemplo.com", "errada")
    assert service.autenticar("cliente@exemplo.com", "Senha2026!")[0].conta_id == "conta_01"


def test_quantidade_de_identificadores_de_tentativa_e_limitada(contexto):
    _, _, contas, sessoes, tokens, agora = contexto
    service = SessaoService(contas, sessoes, tokens, max_identificadores=2)
    for email in ("um@exemplo.com", "dois@exemplo.com"):
        with pytest.raises(NaoAutenticado):
            service.autenticar(email, "errada")
    with pytest.raises(ErroDeNegocio) as erro:
        service.autenticar("tres@exemplo.com", "errada")
    assert erro.value.status == 429
    agora[0] += timedelta(minutes=5)
    with pytest.raises(NaoAutenticado):
        service.autenticar("tres@exemplo.com", "errada")
    assert len(service._tentativas) == 1


def test_reserva_concorrente_de_tentativas_nao_ultrapassa_o_limite(contexto):
    from concurrent.futures import ThreadPoolExecutor

    service = contexto[0]
    def tentar(_):
        try:
            service.autenticar("cliente@exemplo.com", "errada")
        except ErroDeNegocio as erro:
            return erro.status
    with ThreadPoolExecutor(max_workers=8) as executor:
        status = list(executor.map(tentar, range(8)))
    assert status.count(401) == 5
    assert status.count(429) == 3


def test_token_assinado_sem_registro_de_sessao_e_recusado(contexto):
    service, _, _, sessoes, tokens, _ = contexto
    sessao, token = service.autenticar("cliente@exemplo.com", "Senha2026!")
    sessoes.invalidar(sessao.id, AGORA)
    sessoes.limpar_expiradas(AGORA)
    assert tokens.validar(token)["jti"] == sessao.id
    with pytest.raises(NaoAutenticado):
        service.validar_token(token)
