"""Login, limite de tentativas e logout efetivo (US01 e US02)."""

from collections import deque
from datetime import datetime, timedelta
from functools import lru_cache
from hashlib import sha256
from secrets import token_bytes
from threading import Lock
from uuid import uuid4

import bcrypt

from src.domain.erros import ErroDeNegocio, NaoAutenticado
from src.domain.sessao import Sessao
from src.repositories.conta_repository import ContaRepository
from src.repositories.sessao_repository import SessaoRepository
from src.services.token_service import TokenService


@lru_cache(maxsize=1)
def _hash_ficticio() -> bytes:
    """Um bcrypt real para evitar resposta rapida que revele conta inexistente."""
    return bcrypt.hashpw(token_bytes(32), bcrypt.gensalt(rounds=12))


class SessaoService:
    def __init__(
        self,
        contas: ContaRepository,
        sessoes: SessaoRepository,
        tokens: TokenService,
        *,
        limite_tentativas: int = 5,
        janela_tentativas: timedelta = timedelta(minutes=5),
        max_identificadores: int = 10000,
    ) -> None:
        if limite_tentativas < 1 or janela_tentativas <= timedelta(0) or max_identificadores < 1:
            raise ValueError("Limites de autenticacao precisam ser positivos.")
        self._contas = contas
        self._sessoes = sessoes
        self._tokens = tokens
        self._limite = limite_tentativas
        self._janela = janela_tentativas
        self._max_identificadores = max_identificadores
        self._tentativas: dict[str, deque[datetime]] = {}
        self._lock = Lock()
        self._ultima_limpeza: datetime | None = None
        self._dummy_hash = _hash_ficticio()

    def _reservar_tentativa(self, identificador: str, agora: datetime) -> None:
        with self._lock:
            corte = agora - self._janela
            if self._ultima_limpeza is None or agora - self._ultima_limpeza >= self._janela:
                self._tentativas = {
                    chave: deque(t for t in tempos if t > corte)
                    for chave, tempos in self._tentativas.items() if tempos and tempos[-1] > corte
                }
                self._ultima_limpeza = agora
            tempos = self._tentativas.get(identificador, deque())
            while tempos and tempos[0] <= corte:
                tempos.popleft()
            if len(tempos) >= self._limite or (
                identificador not in self._tentativas and len(self._tentativas) >= self._max_identificadores
            ):
                raise ErroDeNegocio("MUITAS_TENTATIVAS", "Muitas tentativas. Aguarde antes de tentar novamente.", 429)
            # Reserva antes do bcrypt para que chamadas concorrentes respeitem o limite.
            tempos.append(agora)
            self._tentativas[identificador] = tempos

    def autenticar(self, email: str, senha: str) -> tuple[Sessao, str]:
        email_normalizado = email.strip().casefold()
        identificador = sha256(email_normalizado.encode("utf-8")).hexdigest()
        agora = self._tokens.agora()
        self._reservar_tentativa(identificador, agora)
        conta = self._contas.obter_por_email(email_normalizado)
        if conta is None:
            # A senha ficticia nunca autentica; truncamento so evita erro da biblioteca.
            bcrypt.checkpw(senha.encode("utf-8")[:72], self._dummy_hash)
            senha_valida = False
        else:
            senha_valida = conta.validar_senha(senha)
        if not senha_valida or conta is None or not conta.esta_ativa() or not conta.cliente_id:
            raise NaoAutenticado("Credenciais invalidas.")
        sessao = Sessao(
            id=f"sessao_{uuid4().hex}", conta_id=conta.id, cliente_id=conta.cliente_id,
            criada_em=agora, expira_em=agora + self._tokens.duracao,
        )
        self._sessoes.limpar_expiradas(agora)
        self._sessoes.salvar(sessao)
        token = self._tokens.emitir(sessao)
        with self._lock:
            self._tentativas.pop(identificador, None)
        return sessao, token

    def validar_token(self, token: str) -> Sessao:
        claims = self._tokens.validar(token)
        sessao = self._sessoes.obter(claims["jti"])
        if sessao is None or not sessao.esta_valida(self._tokens.agora()):
            raise NaoAutenticado()
        if (
            claims["sub"] != sessao.conta_id or claims["cliente_id"] != sessao.cliente_id
            or claims["iat"] != int(sessao.criada_em.timestamp())
            or claims["exp"] != int(sessao.expira_em.timestamp())
        ):
            raise NaoAutenticado()
        conta = self._contas.obter(sessao.conta_id)
        if conta is None or not conta.esta_ativa() or conta.cliente_id != sessao.cliente_id:
            raise NaoAutenticado()
        return sessao

    def encerrar(self, token: str) -> None:
        sessao = self.validar_token(token)
        if not self._sessoes.invalidar(sessao.id, self._tokens.agora()):
            raise NaoAutenticado()
