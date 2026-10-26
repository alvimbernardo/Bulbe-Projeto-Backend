"""Clientes e contas ficticios para a demonstracao da Sprint 2.

Senha demonstrativa das contas existentes: Bulbe2026!
Os hashes abaixo foram gerados com salts distintos e custo 12. Os dados sao
novas entidades a cada chamada; apenas os hashes ficticios sao reutilizados.
"""

from datetime import datetime, timezone

from src.domain.cliente import Cliente
from src.domain.conta import Conta

SENHA_EXEMPLO = "Bulbe2026!"
_HASHES_EXEMPLO = (
    b"$2b$12$bL1.8SZYjnWPgCwMv5QP4ONxgDXWhkmkOOYvFceEVB49DGSqcxKKK",
    b"$2b$12$coTXsXeXP1P1P3G8HVczjO2a8eGn9W38SrCEtCNVvvYiwsfUbtPnK",
)


def clientes_exemplo() -> list[Cliente]:
    return [
        Cliente("cliente_01", "Cliente de Montes Claros", "cliente01@exemplo.com", "ativo", "BULBE-001", "123456"),
        Cliente("cliente_02", "Comercio de Janauba", "cliente02@exemplo.com", "ativo", "BULBE-002", "234567"),
        Cliente("cliente_03", "Cliente de Pirapora", "cliente03@exemplo.com", "ativo", "BULBE-003", "345678"),
        Cliente("cliente_04", "Cliente inativo", "cliente04@exemplo.com", "inativo", "BULBE-004", "456789"),
    ]


def contas_exemplo() -> list[Conta]:
    return [
        Conta(
            id=f"conta_0{numero}", cliente_id=f"cliente_0{numero}", email=f"cliente0{numero}@exemplo.com",
            senha_hash=senha_hash, status="ativa", criada_em=datetime(2026, 8, 1, 12, tzinfo=timezone.utc),
        )
        for numero, senha_hash in enumerate(_HASHES_EXEMPLO, start=1)
    ]
