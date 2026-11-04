"""Tipos de coluna que preservam o fuso horario em qualquer banco."""

from datetime import datetime

from sqlalchemy import String
from sqlalchemy.types import TypeDecorator


class DataHoraComFuso(TypeDecorator):
    impl = String(32)
    cache_ok = True

    def process_bind_param(self, valor: datetime | None, _dialeto) -> str | None:
        return valor.isoformat() if valor is not None else None

    def process_result_value(self, valor: str | None, _dialeto) -> datetime | None:
        return datetime.fromisoformat(valor) if valor is not None else None
