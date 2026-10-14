"""Servico de depoimentos publicos (US11)."""

from src.domain.depoimento import Depoimento
from src.domain.erros import RecursoNaoEncontrado
from src.domain.pagina import LIMITE_PADRAO, Pagina
from src.repositories.depoimento_repository import DepoimentoRepository


class DepoimentoService:
    def __init__(self, depoimentos: DepoimentoRepository) -> None:
        self._depoimentos = depoimentos

    def listar(self, page: int = 1, limit: int = LIMITE_PADRAO) -> Pagina[Depoimento]:
        publicaveis = [d for d in self._depoimentos.listar() if d.pode_ser_publicado()]
        return Pagina.de(publicaveis, page, limit)

    def obter(self, depoimento_id: str) -> Depoimento:
        depoimento = self._depoimentos.obter(depoimento_id)
        if depoimento is None or not depoimento.pode_ser_publicado():
            raise RecursoNaoEncontrado("Depoimento nao encontrado.")
        return depoimento
