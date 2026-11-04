"""Carga dos dados de demonstracao de usinas, creditos e depoimentos no banco."""

from sqlalchemy.orm import sessionmaker

from src.db.database import criar_engine, criar_fabrica_de_sessoes
from src.db.models import CreditoUsinaModel, DepoimentoModel, UsinaModel
from src.repositories.dados_exemplo import creditos_exemplo, depoimentos_exemplo, usinas_exemplo


def carregar_dados_de_exemplo(sessoes: sessionmaker) -> dict[str, int]:
    usinas = usinas_exemplo()
    creditos = creditos_exemplo()
    depoimentos = depoimentos_exemplo()
    with sessoes() as sessao:
        for usina in usinas:
            sessao.merge(UsinaModel.de_dominio(usina))
        sessao.flush()
        for credito in creditos:
            sessao.merge(CreditoUsinaModel.de_dominio(credito))
        for depoimento in depoimentos:
            sessao.merge(DepoimentoModel.de_dominio(depoimento))
        sessao.commit()
    return {"usinas": len(usinas), "creditos_usinas": len(creditos), "depoimentos": len(depoimentos)}


if __name__ == "__main__":
    totais = carregar_dados_de_exemplo(criar_fabrica_de_sessoes(criar_engine()))
    print(", ".join(f"{quantidade} {tabela}" for tabela, quantidade in totais.items()))
