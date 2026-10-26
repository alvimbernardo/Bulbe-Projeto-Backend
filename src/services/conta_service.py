"""Primeiro acesso e vinculo confirmado ao cliente corporativo (US03/US05)."""

from datetime import datetime, timezone
from uuid import uuid4

from src.domain.cliente import ClienteInelegivel, normalizar_email
from src.domain.conta import Conta, ContaJaExistente, validar_senha_de_cadastro
from src.domain.erros import DadoInvalido
from src.repositories.cliente_repository import ClienteRepository
from src.repositories.conta_repository import ContaRepository


class ContaService:
    def __init__(self, clientes: ClienteRepository, contas: ContaRepository) -> None:
        self._clientes = clientes
        self._contas = contas

    def criar(
        self, email: str, senha: str, identificador_cliente: str,
        codigo_verificacao: str | None = None,
    ) -> Conta:
        email = normalizar_email(email)
        validar_senha_de_cadastro(senha)
        if not identificador_cliente.strip():
            raise DadoInvalido("identificador_cliente", "Informe o identificador do cliente.")
        cliente = self._clientes.obter_por_identificador(identificador_cliente)
        if cliente is None or not cliente.confirmar_vinculo(email, codigo_verificacao):
            raise ClienteInelegivel()
        if self._contas.obter_por_cliente(cliente.id) or self._contas.obter_por_email(email):
            raise ContaJaExistente()
        conta = Conta.criar(
            id=f"conta_{uuid4().hex}", cliente_id=cliente.id, email=email,
            senha=senha, criada_em=datetime.now(timezone.utc),
        )
        self._contas.salvar(conta)
        return conta
