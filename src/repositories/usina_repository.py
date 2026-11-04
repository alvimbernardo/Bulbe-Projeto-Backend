"""Repositorio de usinas."""

from abc import ABC, abstractmethod
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.db.models import UsinaModel
from src.domain.usina import Usina


class UsinaRepository(ABC):
    @abstractmethod
    def listar(self) -> list[Usina]: ...

    @abstractmethod
    def obter(self, usina_id: str) -> Usina | None: ...


class InMemoryUsinaRepository(UsinaRepository):
    def __init__(self, usinas: Iterable[Usina] = ()) -> None:
        self._usinas: dict[str, Usina] = {usina.id: usina for usina in usinas}

    def listar(self) -> list[Usina]:
        return sorted(self._usinas.values(), key=lambda usina: usina.id)

    def obter(self, usina_id: str) -> Usina | None:
        return self._usinas.get(usina_id)


class SqlUsinaRepository(UsinaRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def listar(self) -> list[Usina]:
        with self._sessoes() as sessao:
            modelos = sessao.scalars(select(UsinaModel).order_by(UsinaModel.id)).all()
            return [modelo.para_dominio() for modelo in modelos]

    def obter(self, usina_id: str) -> Usina | None:
        with self._sessoes() as sessao:
            modelo = sessao.get(UsinaModel, usina_id)
            return modelo.para_dominio() if modelo else None
