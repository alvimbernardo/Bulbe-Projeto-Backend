"""Entradas e respostas de sessao sem exposicao de hash de senha."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, SecretStr, field_validator

from src.domain.cliente import normalizar_email


class Credenciais(BaseModel):
    email: str = Field(min_length=3, max_length=254)
    senha: SecretStr = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def email_valido(cls, valor: str) -> str:
        return normalizar_email(valor)

    @field_validator("senha")
    @classmethod
    def senha_compativel_com_bcrypt(cls, valor: SecretStr) -> SecretStr:
        try:
            tamanho = len(valor.get_secret_value().encode("utf-8"))
        except UnicodeEncodeError:
            raise ValueError("Senha precisa conter caracteres UTF-8 validos.") from None
        if tamanho > 72:
            raise ValueError("Senha deve ter no maximo 72 bytes UTF-8.")
        return valor


class SessaoResposta(BaseModel):
    model_config = ConfigDict(json_schema_serialization_defaults_required=True)

    sessao_id: str
    conta_id: str
    cliente_id: str
    expira_em: datetime
    access_token: str
    token_type: Literal["bearer"] = "bearer"
