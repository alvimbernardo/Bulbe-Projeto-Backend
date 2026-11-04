"""Carga dos dados de demonstracao no banco."""

from sqlalchemy.orm import sessionmaker

from src.db.database import criar_engine, criar_fabrica_de_sessoes
from src.db.models import (
    AtivacaoModel,
    ClienteModel,
    ContaModel,
    CreditoUsinaModel,
    DepoimentoModel,
    FaturaModel,
    PagamentoModel,
    RepasseModel,
    UsinaModel,
)
from src.repositories.dados_ativacao import ativacoes_exemplo
from src.repositories.dados_contas import clientes_exemplo, contas_exemplo
from src.repositories.dados_exemplo import creditos_exemplo, depoimentos_exemplo, usinas_exemplo
from src.repositories.dados_faturas import faturas_exemplo, pagamentos_exemplo, repasses_exemplo

_ETAPAS = (
    ("usinas", UsinaModel, usinas_exemplo),
    ("creditos_usinas", CreditoUsinaModel, creditos_exemplo),
    ("depoimentos", DepoimentoModel, depoimentos_exemplo),
    ("clientes", ClienteModel, clientes_exemplo),
    ("contas", ContaModel, contas_exemplo),
    ("ativacoes", AtivacaoModel, ativacoes_exemplo),
    ("faturas", FaturaModel, faturas_exemplo),
    ("pagamentos", PagamentoModel, pagamentos_exemplo),
    ("repasses", RepasseModel, repasses_exemplo),
)


def carregar_dados_de_exemplo(sessoes: sessionmaker) -> dict[str, int]:
    totais: dict[str, int] = {}
    with sessoes() as sessao:
        for tabela, modelo, dados in _ETAPAS:
            entidades = dados()
            for entidade in entidades:
                sessao.merge(modelo.de_dominio(entidade))
            sessao.flush()
            totais[tabela] = len(entidades)
        sessao.commit()
    return totais


if __name__ == "__main__":
    totais = carregar_dados_de_exemplo(criar_fabrica_de_sessoes(criar_engine()))
    print(", ".join(f"{quantidade} {tabela}" for tabela, quantidade in totais.items()))
