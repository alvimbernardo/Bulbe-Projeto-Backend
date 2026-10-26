"""Conta digital com senha protegida por bcrypt (US03)."""

from dataclasses import dataclass, field
from datetime import datetime

import bcrypt

from src.domain.cliente import normalizar_email
from src.domain.erros import DadoInvalido, ErroDeNegocio


class ContaJaExistente(ErroDeNegocio):
    def __init__(self) -> None:
        super().__init__("CONTA_JA_EXISTENTE", "Ja existe uma conta para este cliente ou email.", 409)


def validar_senha_de_cadastro(senha: str) -> None:
    if len(senha) < 8:
        raise DadoInvalido("senha", "A senha deve ter pelo menos 8 caracteres.")
    try:
        tamanho = len(senha.encode("utf-8"))
    except UnicodeEncodeError:
        raise DadoInvalido("senha", "A senha deve conter caracteres UTF-8 validos.") from None
    if tamanho > 72:
        raise DadoInvalido("senha", "A senha deve ter no maximo 72 bytes em UTF-8.")


@dataclass
class Conta:
    id: str
    cliente_id: str
    email: str
    senha_hash: bytes = field(repr=False)
    status: str
    criada_em: datetime

    def __post_init__(self) -> None:
        self.email = normalizar_email(self.email)
        if self.status not in {"ativa", "bloqueada", "inativa"}:
            raise DadoInvalido("status", "Status da conta deve ser ativa, bloqueada ou inativa.")
        if not self.id.strip() or not self.cliente_id.strip():
            raise DadoInvalido("cliente_id", "A conta precisa estar vinculada a um cliente.")
        if self.criada_em.utcoffset() is None:
            raise DadoInvalido("criada_em", "O instante de criacao deve informar o fuso horario.")
        if not isinstance(self.senha_hash, bytes) or not self.senha_hash.startswith((b"$2a$", b"$2b$", b"$2y$")):
            raise DadoInvalido("senha_hash", "A conta deve armazenar um hash bcrypt.")

    @classmethod
    def criar(
        cls, id: str, cliente_id: str, email: str, senha: str, criada_em: datetime,
    ) -> "Conta":
        validar_senha_de_cadastro(senha)
        senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt(rounds=12))
        return cls(id, cliente_id, email, senha_hash, "ativa", criada_em)

    def esta_ativa(self) -> bool:
        return self.status == "ativa"

    def validar_senha(self, senha: str) -> bool:
        """Senhas longas sao recusadas, sem truncamento silencioso do bcrypt."""
        try:
            senha_bytes = senha.encode("utf-8")
        except UnicodeEncodeError:
            return False
        if not senha_bytes or len(senha_bytes) > 72:
            return False
        return bcrypt.checkpw(senha_bytes, self.senha_hash)
