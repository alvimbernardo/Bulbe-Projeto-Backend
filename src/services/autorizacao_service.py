"""Vinculo entre sessao e cliente, compartilhado pela area individual (US04)."""

from src.domain.cliente import Cliente
from src.domain.erros import AcessoNegado, RecursoNaoEncontrado
from src.domain.sessao import Sessao
from src.repositories.cliente_repository import ClienteRepository


class AutorizacaoService:
    def __init__(self, clientes: ClienteRepository) -> None:
        self._clientes = clientes

    def obter_cliente(self, sessao: Sessao, cliente_id: str) -> Cliente:
        # Recusa o outro id antes de consultar sua existencia.
        if sessao.cliente_id != cliente_id:
            raise AcessoNegado()
        cliente = self._clientes.obter(cliente_id)
        if cliente is None:
            raise RecursoNaoEncontrado("Cliente nao encontrado.")
        if not cliente.esta_ativo():
            raise AcessoNegado("O cadastro do cliente nao esta ativo.")
        return cliente
