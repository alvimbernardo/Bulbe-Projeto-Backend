"""Objeto de valor Pagina."""

from dataclasses import dataclass
from typing import Generic, Sequence, TypeVar

from src.domain.erros import DadoInvalido

T = TypeVar("T")

LIMITE_PADRAO = 20
LIMITE_MAXIMO = 100


@dataclass(frozen=True)
class Pagina(Generic[T]):
    itens: list[T]
    page: int
    limit: int
    total: int

    @classmethod
    def de(cls, itens: Sequence[T], page: int = 1, limit: int = LIMITE_PADRAO) -> "Pagina[T]":
        if page < 1:
            raise DadoInvalido("page", "A pagina deve ser maior ou igual a 1.")
        if not 1 <= limit <= LIMITE_MAXIMO:
            raise DadoInvalido("limit", f"O limite deve estar entre 1 e {LIMITE_MAXIMO}.")
        inicio = (page - 1) * limit
        return cls(list(itens[inicio : inicio + limit]), page, limit, len(itens))
