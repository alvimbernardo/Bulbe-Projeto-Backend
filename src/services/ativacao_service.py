"""Consultas da ativacao e suas etapas ordenadas (US09)."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.ativacao import Ativacao, EtapaAtivacao
from src.domain.erros import RecursoNaoEncontrado
from src.repositories.ativacao_repository import AtivacaoRepository


@dataclass(frozen=True)
class ListagemEtapasAtivacao:
    cliente_id: str
    etapas: tuple[EtapaAtivacao, ...]
    atualizado_em: datetime


class AtivacaoService:
    def __init__(self, ativacoes: AtivacaoRepository) -> None:
        self._ativacoes = ativacoes

    def obter(self, cliente_id: str) -> Ativacao:
        ativacao = self._ativacoes.obter(cliente_id)
        if ativacao is None:
            raise RecursoNaoEncontrado("Ativacao nao encontrada para este cliente.")
        return ativacao

    def listar_etapas(self, cliente_id: str) -> ListagemEtapasAtivacao:
        ativacao = self.obter(cliente_id)
        return ListagemEtapasAtivacao(ativacao.cliente_id, ativacao.etapas, ativacao.atualizado_em)
