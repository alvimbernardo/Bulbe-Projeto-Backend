"""Emissao e verificacao de JWT HS256 com claims e relogio controlados."""

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Any

import jwt

from src.domain.erros import NaoAutenticado
from src.domain.sessao import Sessao


def agora_utc() -> datetime:
    return datetime.now(timezone.utc)


class TokenService:
    def __init__(
        self,
        segredo: str | None = None,
        *,
        emissor: str = "bulbe-api",
        audiencia: str = "bulbe-clientes",
        duracao: timedelta = timedelta(minutes=30),
        relogio: Callable[[], datetime] = agora_utc,
    ) -> None:
        # Sem configuracao, a chave aleatoria vale so para esta instancia de demo.
        chave = token_urlsafe(48) if segredo is None else segredo
        if len(chave.encode("utf-8")) < 32:
            raise ValueError("JWT_SECRET precisa de pelo menos 32 bytes.")
        if not emissor or not audiencia or duracao < timedelta(seconds=1):
            raise ValueError("Emissor, audiencia e duracao do JWT precisam ser validos.")
        self._segredo = chave
        self._emissor = emissor
        self._audiencia = audiencia
        self.duracao = duracao
        self._relogio = relogio

    def agora(self) -> datetime:
        instante = self._relogio()
        if instante.utcoffset() is None:
            raise ValueError("O relogio precisa retornar data com fuso horario.")
        return instante.astimezone(timezone.utc).replace(microsecond=0)

    def emitir(self, sessao: Sessao) -> str:
        return jwt.encode(
            {
                "sub": sessao.conta_id,
                "cliente_id": sessao.cliente_id,
                "jti": sessao.id,
                "iat": int(sessao.criada_em.timestamp()),
                "exp": int(sessao.expira_em.timestamp()),
                "iss": self._emissor,
                "aud": self._audiencia,
            },
            self._segredo,
            algorithm="HS256",
        )

    def validar(self, token: str) -> dict[str, Any]:
        if not isinstance(token, str) or not token or len(token) > 8192:
            raise NaoAutenticado()
        try:
            claims = jwt.decode(
                token,
                self._segredo,
                algorithms=["HS256"],
                issuer=self._emissor,
                audience=self._audiencia,
                options={
                    "require": ["sub", "cliente_id", "jti", "iat", "exp", "iss", "aud"],
                    "strict_aud": True,
                    # As verificacoes temporais usam abaixo o mesmo relogio da sessao.
                    "verify_exp": False,
                    "verify_iat": False,
                    "verify_nbf": False,
                },
            )
            for campo in ("sub", "cliente_id", "jti"):
                if not isinstance(claims[campo], str) or not claims[campo].strip():
                    raise NaoAutenticado()
            for campo in ("iat", "exp"):
                if type(claims[campo]) is not int:
                    raise NaoAutenticado()
            instante = self.agora().timestamp()
            if not claims["iat"] <= instante < claims["exp"] or claims["exp"] <= claims["iat"]:
                raise NaoAutenticado()
            if "nbf" in claims:
                if type(claims["nbf"]) is not int or claims["nbf"] > instante:
                    raise NaoAutenticado()
            return claims
        except jwt.PyJWTError:
            raise NaoAutenticado() from None
