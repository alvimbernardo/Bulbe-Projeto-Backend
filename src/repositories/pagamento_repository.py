"""Contrato e repositorio em memoria de pagamentos."""

from abc import ABC, abstractmethod
from typing import Iterable

from sqlalchemy.orm import sessionmaker

from src.db.models import PagamentoModel
from src.domain.pagamento import Pagamento


class PagamentoRepository(ABC):
    @abstractmethod
    def obter_por_fatura(self, fatura_id: str) -> Pagamento | None: ...


class InMemoryPagamentoRepository(PagamentoRepository):
    def __init__(self, pagamentos: Iterable[Pagamento] = ()) -> None:
        self._pagamentos = {p.fatura_id: p for p in pagamentos}

    def obter_por_fatura(self, fatura_id: str) -> Pagamento | None:
        return self._pagamentos.get(fatura_id)


class SqlPagamentoRepository(PagamentoRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def obter_por_fatura(self, fatura_id: str) -> Pagamento | None:
        with self._sessoes() as sessao:
            modelo = sessao.get(PagamentoModel, fatura_id)
            return modelo.para_dominio() if modelo else None
