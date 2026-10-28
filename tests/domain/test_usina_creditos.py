"""Testes das regras de Usina (US06), CreditoUsina (US07) e ResumoCreditos (US08)."""

from datetime import datetime
from decimal import Decimal

import pytest

from src.domain.competencia import Competencia
from src.domain.credito_usina import CreditoUsina, ResumoCreditos
from src.domain.dinheiro import Dinheiro
from src.domain.erros import DadoInvalido, FonteIndisponivel
from src.domain.usina import StatusUsina, Usina

AGOSTO = Competencia(2026, 8)
JULHO = Competencia(2026, 7)


def nova_usina(id_, status="ativa"):
    return Usina(
        id=id_,
        nome=f"Usina {id_}",
        cidade="Montes Claros",
        estado="mg",
        regiao="Norte de Minas",
        status=status,
        atualizada_em=datetime(2026, 8, 17, 9, 0),
    )


def novo_credito(usina_id, valor, competencia=AGOSTO, dia=17):
    return CreditoUsina(usina_id, competencia, Dinheiro(Decimal(valor)), datetime(2026, 8, dia, 9, 0))


# ---- Usina (US06) ----

def test_usina_normaliza_uf_e_converte_status():
    usina = nova_usina("u1", status="em_manutencao")
    assert usina.estado == "MG"
    assert usina.status is StatusUsina.em_manutencao
    assert usina.localizacao == "Montes Claros - MG"


def test_usina_com_status_desconhecido_e_recusada():
    with pytest.raises(DadoInvalido):
        nova_usina("u1", status="desligada")


def test_sem_filtro_so_usinas_ativas_aparecem():
    assert nova_usina("u1", "ativa").aparece_na_listagem() is True
    assert nova_usina("u2", "inativa").aparece_na_listagem() is False
    assert nova_usina("u3", "em_manutencao").aparece_na_listagem() is False


def test_com_filtro_aparecem_as_do_status_pedido():
    assert nova_usina("u2", "inativa").aparece_na_listagem(StatusUsina.inativa) is True
    assert nova_usina("u1", "ativa").aparece_na_listagem(StatusUsina.inativa) is False


# ---- CreditoUsina (US07) ----

def test_credito_pertence_a_usina_e_competencia():
    credito = novo_credito("u1", "120.00")
    assert credito.pertence_a("u1", AGOSTO) is True
    assert credito.pertence_a("u1", JULHO) is False
    assert credito.pertence_a("u2", AGOSTO) is False


# ---- ResumoCreditos (US08) ----

def test_total_soma_so_usinas_ativas_da_mesma_competencia():
    usinas = [nova_usina("u1"), nova_usina("u2"), nova_usina("u3", "inativa")]
    creditos = [
        novo_credito("u1", "100.50"),
        novo_credito("u2", "200.25"),
        novo_credito("u3", "999.00"),            # usina inativa: fora do total
        novo_credito("u1", "500.00", JULHO),      # outro mes: fora do total
    ]

    resumo = ResumoCreditos.calcular(AGOSTO, usinas, creditos)

    assert resumo.total_creditos == Dinheiro(Decimal("300.75"))
    assert resumo.quantidade_usinas == 2
    assert resumo.criterio == "usinas_ativas"


def test_total_nao_e_exibido_se_faltar_credito_de_alguma_usina():
    usinas = [nova_usina("u1"), nova_usina("u2")]
    creditos = [novo_credito("u1", "100.00")]  # u2 sem credito em agosto

    with pytest.raises(FonteIndisponivel) as erro:
        ResumoCreditos.calcular(AGOSTO, usinas, creditos)
    assert erro.value.status == 503


def test_data_do_total_e_a_do_credito_mais_antigo():
    usinas = [nova_usina("u1"), nova_usina("u2")]
    creditos = [novo_credito("u1", "10", dia=20), novo_credito("u2", "10", dia=15)]

    resumo = ResumoCreditos.calcular(AGOSTO, usinas, creditos)

    assert resumo.atualizado_em == datetime(2026, 8, 15, 9, 0)


def test_total_por_outro_criterio():
    usinas = [nova_usina("u1"), nova_usina("u3", "inativa")]
    creditos = [novo_credito("u1", "10"), novo_credito("u3", "40")]

    resumo = ResumoCreditos.calcular(AGOSTO, usinas, creditos, StatusUsina.inativa)

    assert resumo.total_creditos.valor == Decimal("40.00")
    assert resumo.criterio == "usinas_inativas"


def test_usina_com_nome_curto_e_recusada():
    with pytest.raises(DadoInvalido) as erro:
        Usina(
            id="u1",
            nome="AB",
            cidade="Montes Claros",
            estado="MG",
            regiao="Norte de Minas",
            status="ativa",
            atualizada_em=datetime(2026, 8, 17, 9, 0),
        )
    assert erro.value.status == 400
    assert erro.value.detalhes[0]["campo"] == "nome"


@pytest.mark.parametrize("estado", ["M", "MGS", "M1"])
def test_usina_com_uf_invalida_e_recusada(estado):
    with pytest.raises(DadoInvalido) as erro:
        Usina(
            id="u1",
            nome="Usina Solar Teste",
            cidade="Montes Claros",
            estado=estado,
            regiao="Norte de Minas",
            status="ativa",
            atualizada_em=datetime(2026, 8, 17, 9, 0),
        )
    assert erro.value.detalhes[0]["campo"] == "estado"
