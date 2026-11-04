"""Contrato e repositorio em memoria de faturas."""

from abc import ABC, abstractmethod
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from src.db.models import FaturaModel
from src.domain.fatura import Fatura


class FaturaRepository(ABC):
    @abstractmethod
    def listar_por_cliente(self, cliente_id: str) -> list[Fatura]: ...

    @abstractmethod
    def obter(self, fatura_id: str) -> Fatura | None: ...


class InMemoryFaturaRepository(FaturaRepository):
    def __init__(self, faturas: Iterable[Fatura] = ()) -> None:
        self._faturas = {f.id: f for f in faturas}

    def listar_por_cliente(self, cliente_id: str) -> list[Fatura]:
        return sorted(
            (f for f in self._faturas.values() if f.pertence_ao_cliente(cliente_id)),
            key=lambda fatura: (fatura.competencia, fatura.id), reverse=True,
        )

    def obter(self, fatura_id: str) -> Fatura | None:
        return self._faturas.get(fatura_id)


class SqlFaturaRepository(FaturaRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def listar_por_cliente(self, cliente_id: str) -> list[Fatura]:
        consulta = (
            select(FaturaModel)
            .where(FaturaModel.cliente_id == cliente_id)
            .order_by(FaturaModel.competencia.desc(), FaturaModel.id.desc())
        )
        with self._sessoes() as sessao:
            return [modelo.para_dominio() for modelo in sessao.scalars(consulta).all()]

    def obter(self, fatura_id: str) -> Fatura | None:
        with self._sessoes() as sessao:
            modelo = sessao.get(FaturaModel, fatura_id)
            return modelo.para_dominio() if modelo else None
