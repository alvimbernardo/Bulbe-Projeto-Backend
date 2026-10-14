"""Entidade Usina (US06)."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from src.domain.erros import DadoInvalido


class StatusUsina(str, Enum):
    ativa = "ativa"
    em_manutencao = "em_manutencao"
    inativa = "inativa"


def converter_status(valor: str | StatusUsina, campo: str = "status") -> StatusUsina:
    try:
        return StatusUsina(valor)
    except ValueError:
        raise DadoInvalido(campo, "Status deve ser ativa, em_manutencao ou inativa.") from None


@dataclass
class Usina:
    id: str
    nome: str
    cidade: str
    estado: str
    regiao: str
    status: StatusUsina
    atualizada_em: datetime

    def __post_init__(self) -> None:
        if len(self.nome.strip()) < 3:
            raise DadoInvalido("nome", "O nome da usina deve ter pelo menos 3 caracteres.")
        estado = self.estado.strip().upper()
        if len(estado) != 2 or not estado.isalpha():
            raise DadoInvalido("estado", "O estado deve ser a sigla da UF, por exemplo MG.")
        self.estado = estado
        self.status = converter_status(self.status)

    def esta_ativa(self) -> bool:
        return self.status == StatusUsina.ativa

    def aparece_na_listagem(self, status_filtro: StatusUsina | None = None) -> bool:
        if status_filtro is None:
            return self.esta_ativa()
        return self.status == converter_status(status_filtro)

    @property
    def localizacao(self) -> str:
        return f"{self.cidade} - {self.estado}"
