"""Respostas HTTP de ativacao conforme o contrato da US09."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.ativacao import StatusAtivacao, StatusEtapaAtivacao


class AtivacaoResposta(BaseModel):
    cliente_id: str
    status: StatusAtivacao
    percentual: int = Field(ge=0, le=100)
    etapa_atual_id: str | None = None
    iniciada_em: date | None = None
    previsao_conclusao: date | None = None
    atualizado_em: datetime


class EtapaAtivacaoResposta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    ordem: int
    nome: str
    status: StatusEtapaAtivacao
    concluida_em: datetime | None = None
    previsao_conclusao: date | None = None


class ListaEtapasAtivacaoResposta(BaseModel):
    cliente_id: str
    data: list[EtapaAtivacaoResposta]
    atualizado_em: datetime
