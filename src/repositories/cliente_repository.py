"""Consulta ao cadastro corporativo em memoria (US05)."""

from abc import ABC, abstractmethod
from typing import Iterable

from src.domain.cliente import Cliente


class ClienteRepository(ABC):
    @abstractmethod
    def obter(self, cliente_id: str) -> Cliente | None: ...

    @abstractmethod
    def obter_por_identificador(self, identificador_cliente: str) -> Cliente | None: ...


class InMemoryClienteRepository(ClienteRepository):
    def __init__(self, clientes: Iterable[Cliente] = ()) -> None:
        self._clientes: dict[str, Cliente] = {}
        self._por_identificador: dict[str, Cliente] = {}
        for cliente in clientes:
            if cliente.id in self._clientes or cliente.identificador_cliente in self._por_identificador:
                raise ValueError("Cadastro de exemplo contem clientes duplicados.")
            self._clientes[cliente.id] = cliente
            self._por_identificador[cliente.identificador_cliente] = cliente

    def obter(self, cliente_id: str) -> Cliente | None:
        return self._clientes.get(cliente_id)

    def obter_por_identificador(self, identificador_cliente: str) -> Cliente | None:
        return self._por_identificador.get(identificador_cliente)
