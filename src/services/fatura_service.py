"""Consultas de faturas do cliente e dos seus pagamentos e repasses."""

from dataclasses import dataclass
from datetime import datetime

from src.domain.competencia import Competencia
from src.domain.erros import RecursoNaoEncontrado
from src.domain.fatura import Fatura
from src.domain.pagamento import Pagamento
from src.domain.pagina import LIMITE_PADRAO, Pagina
from src.domain.repasse import Repasse
from src.repositories.fatura_repository import FaturaRepository
from src.repositories.pagamento_repository import PagamentoRepository
from src.repositories.repasse_repository import RepasseRepository


@dataclass(frozen=True)
class ListagemFaturas:
    pagina: Pagina[Fatura]
    atualizado_em: datetime | None


class FaturaService:
    def __init__(
        self, faturas: FaturaRepository,
        pagamentos: PagamentoRepository, repasses: RepasseRepository,
    ) -> None:
        self._faturas = faturas
        self._pagamentos = pagamentos
        self._repasses = repasses

    def listar(
        self, cliente_id: str, competencia: str | Competencia | None = None,
        page: int = 1, limit: int = LIMITE_PADRAO,
    ) -> ListagemFaturas:
        periodo = Competencia.de_texto(competencia) if isinstance(competencia, str) else competencia
        selecionadas = [
            f for f in self._faturas.listar_por_cliente(cliente_id)
            if f.pertence_ao_cliente(cliente_id) and (periodo is None or f.pertence_a_competencia(periodo))
        ]
        return ListagemFaturas(
            Pagina.de(selecionadas, page, limit),
            max((f.atualizado_em for f in selecionadas), default=None),
        )

    def obter(self, cliente_id: str, fatura_id: str) -> Fatura:
        fatura = self._faturas.obter(fatura_id)
        if fatura is None or not fatura.pertence_ao_cliente(cliente_id):
            raise RecursoNaoEncontrado("Fatura nao encontrada.")
        return fatura

    def pagamento(self, cliente_id: str, fatura_id: str) -> Pagamento:
        self.obter(cliente_id, fatura_id)
        pagamento = self._pagamentos.obter_por_fatura(fatura_id)
        if pagamento is None:
            raise RecursoNaoEncontrado("Nao ha pagamento registrado para esta fatura.")
        return pagamento

    def repasse(self, cliente_id: str, fatura_id: str) -> Repasse:
        self.obter(cliente_id, fatura_id)
        repasse = self._repasses.obter_por_fatura(fatura_id)
        if repasse is None:
            raise RecursoNaoEncontrado("Nao ha repasse registrado para esta fatura.")
        return repasse
