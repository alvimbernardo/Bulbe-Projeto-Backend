"""Servico de usinas (US06)."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.erros import RecursoNaoEncontrado
from src.domain.pagina import LIMITE_PADRAO, Pagina
from src.domain.usina import StatusUsina, Usina, converter_status
from src.repositories.usina_repository import UsinaRepository


@dataclass(frozen=True)
class ListagemUsinas:
    pagina: Pagina[Usina]
    atualizado_em: datetime | None


class UsinaService:
    def __init__(self, usinas: UsinaRepository) -> None:
        self._usinas = usinas

    def listar(
        self,
        status: str | StatusUsina | None = None,
        page: int = 1,
        limit: int = LIMITE_PADRAO,
    ) -> ListagemUsinas:
        filtro = converter_status(status) if status is not None else None
        selecionadas = [u for u in self._usinas.listar() if u.aparece_na_listagem(filtro)]
        atualizado_em = max((u.atualizada_em for u in selecionadas), default=None)
        return ListagemUsinas(Pagina.de(selecionadas, page, limit), atualizado_em)

    def obter(self, usina_id: str) -> Usina:
        usina = self._usinas.obter(usina_id)
        if usina is None:
            raise RecursoNaoEncontrado("Usina nao encontrada.")
        return usina
