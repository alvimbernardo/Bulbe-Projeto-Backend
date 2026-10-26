"""Entrada do primeiro acesso e resposta publica da conta."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.cliente import normalizar_email
from src.domain.conta import validar_senha_de_cadastro


class ContaCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str = Field(max_length=254, json_schema_extra={"format": "email"})
    senha: str = Field(min_length=8, max_length=72, repr=False, json_schema_extra={"format": "password"})
    identificador_cliente: str = Field(min_length=1, max_length=100)
    codigo_verificacao: str | None = Field(default=None, min_length=1, max_length=128)

    @field_validator("email")
    @classmethod
    def validar_email(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("senha")
    @classmethod
    def validar_senha(cls, valor: str) -> str:
        validar_senha_de_cadastro(valor)
        return valor


class ContaResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cliente_id: str
    email: str
    status: Literal["ativa", "bloqueada", "inativa"]
    criada_em: datetime
