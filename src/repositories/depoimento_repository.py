"""Repositorio de depoimentos."""

from abc import ABC, abstractmethod
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.db.models import DepoimentoModel
from src.domain.depoimento import Depoimento


class DepoimentoRepository(ABC):
    @abstractmethod
    def listar(self) -> list[Depoimento]: ...

    @abstractmethod
    def obter(self, depoimento_id: str) -> Depoimento | None: ...


class InMemoryDepoimentoRepository(DepoimentoRepository):
    def __init__(self, depoimentos: Iterable[Depoimento] = ()) -> None:
        self._depoimentos: dict[str, Depoimento] = {d.id: d for d in depoimentos}

    def listar(self) -> list[Depoimento]:
        return sorted(self._depoimentos.values(), key=lambda depoimento: depoimento.id)

    def obter(self, depoimento_id: str) -> Depoimento | None:
        return self._depoimentos.get(depoimento_id)


class SqlDepoimentoRepository(DepoimentoRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def listar(self) -> list[Depoimento]:
        with self._sessoes() as sessao:
            modelos = sessao.scalars(select(DepoimentoModel).order_by(DepoimentoModel.id)).all()
            return [modelo.para_dominio() for modelo in modelos]

    def obter(self, depoimento_id: str) -> Depoimento | None:
        with self._sessoes() as sessao:
            modelo = sessao.get(DepoimentoModel, depoimento_id)
            return modelo.para_dominio() if modelo else None
