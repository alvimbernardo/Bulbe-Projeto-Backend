"""Contrato e repositorio em memoria dos repasses."""

from abc import ABC, abstractmethod
from typing import Iterable

from sqlalchemy.orm import sessionmaker

from src.db.models import RepasseModel
from src.domain.repasse import Repasse


class RepasseRepository(ABC):
    @abstractmethod
    def obter_por_fatura(self, fatura_id: str) -> Repasse | None: ...


class InMemoryRepasseRepository(RepasseRepository):
    def __init__(self, repasses: Iterable[Repasse] = ()) -> None:
        self._repasses = {r.fatura_id: r for r in repasses}

    def obter_por_fatura(self, fatura_id: str) -> Repasse | None:
        return self._repasses.get(fatura_id)


class SqlRepasseRepository(RepasseRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def obter_por_fatura(self, fatura_id: str) -> Repasse | None:
        with self._sessoes() as sessao:
            modelo = sessao.get(RepasseModel, fatura_id)
            return modelo.para_dominio() if modelo else None
