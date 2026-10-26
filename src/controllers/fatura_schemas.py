"""Respostas de faturas, pagamentos e repasses conforme o contrato."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from src.controllers.schemas import Dinheiro, Paginacao
from src.domain.fatura import Fatura as FaturaEntidade, StatusFatura
from src.domain.pagamento import StatusPagamento
from src.domain.repasse import StatusEtapaRepasse, StatusRepasse


class FaturaResumo(BaseModel):
    id: str
    identificador_exibivel: str
    competencia: str
    valor: Dinheiro
    status: StatusFatura

    @classmethod
    def de_entidade(cls, fatura: FaturaEntidade) -> "FaturaResumo":
        return cls(
            id=fatura.id, identificador_exibivel=fatura.identificador_exibivel,
            competencia=str(fatura.competencia), valor=Dinheiro.model_validate(fatura.valor),
            status=fatura.status,
        )


class Fatura(FaturaResumo):
    cliente_id: str
    vencimento: date
    atualizado_em: datetime

    @classmethod
    def de_entidade(cls, fatura: FaturaEntidade) -> "Fatura":
        return cls(
            **FaturaResumo.de_entidade(fatura).model_dump(),
            cliente_id=fatura.cliente_id, vencimento=fatura.vencimento,
            atualizado_em=fatura.atualizado_em,
        )


class ListaFaturas(Paginacao):
    data: list[FaturaResumo]
    atualizado_em: datetime | None


class Pagamento(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fatura_id: str
    status: StatusPagamento
    atualizado_em: datetime
    forma: str | None = None
    pago_em: datetime | None = None
    valor: Dinheiro | None = None


class EtapaRepasse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ordem: int
    nome: str
    status: StatusEtapaRepasse
    ocorrido_em: datetime | None = None
    previsao: date | None = None
    mensagem: str | None = None


class Repasse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    fatura_id: str
    status: StatusRepasse
    etapas: list[EtapaRepasse]
    atualizado_em: datetime
