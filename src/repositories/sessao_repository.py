"""Interface de sessoes e implementacao em memoria com revogacao atomica."""

from abc import ABC, abstractmethod
from datetime import datetime
from threading import Lock

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from src.db.models import SessaoModel
from src.domain.sessao import Sessao


class SessaoRepository(ABC):
    @abstractmethod
    def salvar(self, sessao: Sessao) -> None: ...

    @abstractmethod
    def obter(self, sessao_id: str) -> Sessao | None: ...

    @abstractmethod
    def invalidar(self, sessao_id: str, agora: datetime) -> bool: ...

    @abstractmethod
    def limpar_expiradas(self, agora: datetime) -> None: ...


class InMemorySessaoRepository(SessaoRepository):
    def __init__(self) -> None:
        self._sessoes: dict[str, Sessao] = {}
        self._lock = Lock()

    def salvar(self, sessao: Sessao) -> None:
        with self._lock:
            if sessao.id in self._sessoes:
                raise ValueError("Identificador de sessao ja existente.")
            self._sessoes[sessao.id] = sessao

    def obter(self, sessao_id: str) -> Sessao | None:
        with self._lock:
            return self._sessoes.get(sessao_id)

    def invalidar(self, sessao_id: str, agora: datetime) -> bool:
        with self._lock:
            sessao = self._sessoes.get(sessao_id)
            return sessao.invalidar(agora) if sessao is not None else False

    def limpar_expiradas(self, agora: datetime) -> None:
        with self._lock:
            self._sessoes = {
                chave: sessao for chave, sessao in self._sessoes.items()
                if sessao.esta_valida(agora)
            }


class SqlSessaoRepository(SessaoRepository):
    def __init__(self, sessoes: sessionmaker) -> None:
        self._sessoes = sessoes

    def salvar(self, sessao: Sessao) -> None:
        with self._sessoes() as conexao:
            conexao.add(SessaoModel.de_dominio(sessao))
            try:
                conexao.commit()
            except IntegrityError:
                conexao.rollback()
                raise ValueError("Identificador de sessao ja existente.") from None

    def obter(self, sessao_id: str) -> Sessao | None:
        with self._sessoes() as conexao:
            modelo = conexao.get(SessaoModel, sessao_id)
            return modelo.para_dominio() if modelo else None

    def invalidar(self, sessao_id: str, agora: datetime) -> bool:
        with self._sessoes() as conexao:
            modelo = conexao.get(SessaoModel, sessao_id, with_for_update=True)
            if modelo is None:
                return False
            sessao = modelo.para_dominio()
            if not sessao.invalidar(agora):
                return False
            modelo.invalidada_em = sessao.invalidada_em
            conexao.commit()
            return True

    def limpar_expiradas(self, agora: datetime) -> None:
        with self._sessoes() as conexao:
            for modelo in conexao.scalars(select(SessaoModel)).all():
                if not modelo.para_dominio().esta_valida(agora):
                    conexao.delete(modelo)
            conexao.commit()
