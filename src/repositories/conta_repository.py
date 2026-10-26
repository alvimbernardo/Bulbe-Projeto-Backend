"""Persistencia em memoria, com unicidade atomica de conta, cliente e email."""

from abc import ABC, abstractmethod
from threading import Lock
from typing import Iterable

from src.domain.conta import Conta, ContaJaExistente


class ContaRepository(ABC):
    @abstractmethod
    def obter(self, conta_id: str) -> Conta | None: ...

    @abstractmethod
    def obter_por_email(self, email: str) -> Conta | None: ...

    @abstractmethod
    def obter_por_cliente(self, cliente_id: str) -> Conta | None: ...

    @abstractmethod
    def salvar(self, conta: Conta) -> None: ...


class InMemoryContaRepository(ContaRepository):
    def __init__(self, contas: Iterable[Conta] = ()) -> None:
        self._contas: dict[str, Conta] = {}
        self._por_email: dict[str, Conta] = {}
        self._por_cliente: dict[str, Conta] = {}
        self._lock = Lock()
        for conta in contas:
            self.salvar(conta)

    def obter(self, conta_id: str) -> Conta | None:
        with self._lock:
            return self._contas.get(conta_id)

    def obter_por_email(self, email: str) -> Conta | None:
        with self._lock:
            return self._por_email.get(email.strip().casefold())

    def obter_por_cliente(self, cliente_id: str) -> Conta | None:
        with self._lock:
            return self._por_cliente.get(cliente_id)

    def salvar(self, conta: Conta) -> None:
        """Cria uma conta; uma corrida de cadastro nunca produz duplicidade."""
        with self._lock:
            if (conta.id in self._contas or conta.email in self._por_email
                    or conta.cliente_id in self._por_cliente):
                raise ContaJaExistente()
            self._contas[conta.id] = conta
            self._por_email[conta.email] = conta
            self._por_cliente[conta.cliente_id] = conta
