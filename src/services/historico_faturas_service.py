"""Consulta e validacao do destino externo aprovado (US14)."""

from src.domain.erros import FonteIndisponivel, RecursoNaoEncontrado, DadoInvalido
from src.repositories.historico_repository import HistoricoRepository


class HistoricoFaturasService:
    def __init__(self, destinos: HistoricoRepository, hosts_aprovados: frozenset[str]) -> None:
        self._destinos = destinos
        self._hosts_aprovados = frozenset(host.casefold() for host in hosts_aprovados)

    def obter_destino(self, cliente_id: str) -> str:
        destino = self._destinos.obter(cliente_id)
        if destino is None:
            raise RecursoNaoEncontrado("Historico externo nao configurado para este cliente.")
        try:
            return destino.validar(self._hosts_aprovados)
        except DadoInvalido:
            raise FonteIndisponivel("O destino do historico externo nao esta disponivel.") from None
