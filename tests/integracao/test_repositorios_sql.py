"""Testes de integracao dos repositorios SQL de usinas, creditos e depoimentos."""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models import CreditoUsinaModel
from src.domain.competencia import Competencia
from src.domain.usina import StatusUsina
from src.repositories.credito_usina_repository import SqlCreditoUsinaRepository
from src.repositories.dados_exemplo import BRASILIA
from src.repositories.depoimento_repository import SqlDepoimentoRepository
from src.repositories.usina_repository import SqlUsinaRepository

AGOSTO = Competencia(2026, 8)


def test_listar_usinas_devolve_entidades_do_dominio_em_ordem(sessoes_com_dados):
    usinas = SqlUsinaRepository(sessoes_com_dados).listar()
    assert [u.id for u in usinas] == ["usina_01", "usina_02", "usina_03", "usina_04"]
    assert usinas[2].status is StatusUsina.em_manutencao
    assert usinas[0].atualizada_em == datetime(2026, 9, 1, 9, 0, tzinfo=BRASILIA)


def test_obter_usina_inexistente_devolve_none(sessoes_com_dados):
    assert SqlUsinaRepository(sessoes_com_dados).obter("usina_99") is None


def test_credito_volta_do_banco_sem_perder_centavos(sessoes_com_dados):
    credito = SqlCreditoUsinaRepository(sessoes_com_dados).obter("usina_01", AGOSTO)
    assert credito.creditos.valor == Decimal("43980.75")
    assert credito.creditos.moeda == "BRL"
    assert credito.competencia == AGOSTO


def test_listar_creditos_filtra_pela_competencia(sessoes_com_dados):
    creditos = SqlCreditoUsinaRepository(sessoes_com_dados).listar_por_competencia(AGOSTO)
    assert [c.usina_id for c in creditos] == ["usina_01", "usina_02", "usina_03"]
    assert all(c.competencia == AGOSTO for c in creditos)


def test_credito_de_usina_inexistente_e_recusado_pela_chave_estrangeira(sessoes_com_dados):
    with sessoes_com_dados() as sessao:
        sessao.add(
            CreditoUsinaModel(
                usina_id="usina_99",
                competencia="2026-08",
                valor=Decimal("10.00"),
                moeda="BRL",
                atualizado_em=datetime(2026, 9, 10, 9, 0, tzinfo=BRASILIA),
            )
        )
        with pytest.raises(IntegrityError):
            sessao.commit()


def test_depoimento_mantem_autorizacao_e_economia(sessoes_com_dados):
    repositorio = SqlDepoimentoRepository(sessoes_com_dados)
    autorizado = repositorio.obter("depoimento_01")
    nao_autorizado = repositorio.obter("depoimento_03")
    assert autorizado.pode_ser_publicado() is True
    assert autorizado.economia_mensal.valor == Decimal("85.40")
    assert nao_autorizado.pode_ser_publicado() is False
    assert nao_autorizado.economia_mensal is None


def test_dados_continuam_no_banco_em_uma_nova_sessao(engine, sessoes_com_dados):
    from src.db.database import criar_fabrica_de_sessoes

    outra_fabrica = criar_fabrica_de_sessoes(engine)
    assert len(SqlUsinaRepository(outra_fabrica).listar()) == 4
    assert len(SqlDepoimentoRepository(outra_fabrica).listar()) == 3


def test_seed_pode_rodar_duas_vezes_sem_duplicar(sessoes_com_dados):
    from src.db.seed import carregar_dados_de_exemplo

    carregar_dados_de_exemplo(sessoes_com_dados)
    assert len(SqlUsinaRepository(sessoes_com_dados).listar()) == 4
    assert len(SqlCreditoUsinaRepository(sessoes_com_dados).listar_por_competencia(AGOSTO)) == 3
