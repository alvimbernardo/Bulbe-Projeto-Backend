"""Modelos de resposta da area publica, conforme o contrato OpenAPI."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.domain.usina import StatusUsina


class Dinheiro(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    valor: float
    moeda: str


class UsinaResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    cidade: str
    estado: str = Field(min_length=2, max_length=2)
    status: StatusUsina


class Usina(UsinaResumo):
    regiao: str
    atualizado_em: datetime = Field(validation_alias="atualizada_em")


class Paginacao(BaseModel):
    page: int
    limit: int
    total: int


class ListaUsinas(Paginacao):
    data: list[UsinaResumo]
    atualizado_em: datetime | None


class CreditoUsina(BaseModel):
    usina_id: str
    competencia: str
    creditos: Dinheiro
    atualizado_em: datetime


class ResumoCreditos(BaseModel):
    competencia: str
    criterio: str
    quantidade_usinas: int
    total_creditos: Dinheiro
    atualizado_em: datetime | None


class Depoimento(BaseModel):
    id: str
    nome_publico: str
    localidade: str
    avaliacao: int = Field(ge=1, le=5)
    texto: str
    economia_mensal: Dinheiro | None = None
    dias_para_ativacao: int | None = None
    percentual_desconto: float | None = None
    tempo_conta_ativa_meses: int | None = None


class ListaDepoimentos(Paginacao):
    data: list[Depoimento]


class DetalheErro(BaseModel):
    campo: str
    mensagem: str


class Erro(BaseModel):
    codigo: str
    mensagem: str
    detalhes: list[DetalheErro]
    request_id: str


RESPOSTAS_PUBLICAS = {
    400: {"model": Erro, "description": "Campos ou parametros invalidos."},
    404: {"model": Erro, "description": "Recurso nao encontrado."},
    503: {"model": Erro, "description": "Dados temporariamente indisponiveis."},
    # Substitui o 422 automatico do FastAPI: o handler do projeto retorna 400.
    "4XX": {"model": Erro, "description": "Erro no formato padrao da API."},
}
