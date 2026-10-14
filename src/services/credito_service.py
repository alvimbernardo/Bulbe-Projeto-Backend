"""Servico de creditos das usinas (US07 e US08)."""

from src.domain.competencia import Competencia
from src.domain.credito_usina import CreditoUsina, ResumoCreditos
from src.domain.erros import DadoInvalido, RecursoNaoEncontrado
from src.domain.usina import StatusUsina, converter_status
from src.repositories.credito_usina_repository import CreditoUsinaRepository
from src.repositories.usina_repository import UsinaRepository


def _competencia(valor: str | Competencia | None) -> Competencia:
    if isinstance(valor, Competencia):
        return valor
    if not valor:
        raise DadoInvalido("competencia", "A competencia e obrigatoria no formato AAAA-MM.")
    return Competencia.de_texto(valor)


class CreditoService:
    def __init__(self, usinas: UsinaRepository, creditos: CreditoUsinaRepository) -> None:
        self._usinas = usinas
        self._creditos = creditos

    def creditos_da_usina(self, usina_id: str, competencia: str | Competencia | None) -> CreditoUsina:
        periodo = _competencia(competencia)
        if self._usinas.obter(usina_id) is None:
            raise RecursoNaoEncontrado("Usina nao encontrada.")
        credito = self._creditos.obter(usina_id, periodo)
        if credito is None:
            raise RecursoNaoEncontrado(f"Nao ha creditos registrados para esta usina em {periodo}.")
        return credito

    def resumo(
        self,
        competencia: str | Competencia | None,
        status_usina: str | StatusUsina = StatusUsina.ativa,
    ) -> ResumoCreditos:
        periodo = _competencia(competencia)
        status = converter_status(status_usina, campo="status_usina")
        return ResumoCreditos.calcular(
            periodo,
            self._usinas.listar(),
            self._creditos.listar_por_competencia(periodo),
            status,
        )
