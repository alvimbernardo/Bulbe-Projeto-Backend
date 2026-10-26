"""Invariantes do dominio financeiro do cliente."""

from dataclasses import replace
from datetime import date, datetime

import pytest

from src.domain.erros import DadoInvalido
from src.domain.pagamento import StatusPagamento
from src.domain.repasse import Repasse, StatusEtapaRepasse, StatusRepasse
from src.repositories.dados_faturas import faturas_exemplo, pagamentos_exemplo, repasses_exemplo


def test_fatura_identifica_dono_competencia_e_pagamento():
    paga, aberta, _ = faturas_exemplo()
    assert paga.pertence_ao_cliente("cliente_01")
    assert not paga.pertence_ao_cliente("cliente_02")
    assert paga.pertence_a_competencia(paga.competencia)
    assert paga.esta_paga()
    assert not aberta.esta_paga()


@pytest.mark.parametrize("alteracoes", [
    {"cliente_id": ""}, {"identificador_exibivel": " "}, {"status": "desconhecido"},
    {"atualizado_em": datetime(2026, 8, 1)},
])
def test_fatura_invalida_e_recusada(alteracoes):
    with pytest.raises(DadoInvalido):
        replace(faturas_exemplo()[0], **alteracoes)


@pytest.mark.parametrize("alteracoes", [
    {"forma": None}, {"valor": None}, {"pago_em": None}, {"status": "invalido"},
    {"pago_em": datetime(2026, 8, 15)}, {"atualizado_em": datetime(2026, 8, 15)},
])
def test_pagamento_confirmado_exige_dados_coerentes(alteracoes):
    with pytest.raises(DadoInvalido):
        replace(pagamentos_exemplo()[0], **alteracoes)


def test_pendente_e_recusado_nao_podem_ter_data_de_confirmacao():
    confirmado = pagamentos_exemplo()[0]
    for status in (StatusPagamento.pendente, StatusPagamento.recusado):
        with pytest.raises(DadoInvalido):
            replace(confirmado, status=status)


def test_repasse_calcula_status_a_partir_das_etapas():
    andamento = repasses_exemplo()[0]
    assert andamento.status is StatusRepasse.em_andamento
    etapas_pendentes = tuple(
        replace(e, status=StatusEtapaRepasse.pendente, ocorrido_em=None) for e in andamento.etapas
    )
    pendente = Repasse(andamento.fatura_id, etapas_pendentes, andamento.atualizado_em)
    assert pendente.status is StatusRepasse.nao_iniciado
    assert pendente.obter_etapa_atual() is None
    etapas_concluidas = tuple(
        replace(e, status=StatusEtapaRepasse.concluida, ocorrido_em=andamento.atualizado_em, previsao=None)
        for e in andamento.etapas
    )
    concluido = Repasse(andamento.fatura_id, etapas_concluidas, andamento.atualizado_em)
    assert concluido.status is StatusRepasse.concluido
    assert concluido.obter_etapa_atual() is None


def test_repasse_ordena_etapas_sem_alterar_os_eventos():
    repasse = repasses_exemplo()[0]
    invertido = Repasse(repasse.fatura_id, tuple(reversed(repasse.etapas)), repasse.atualizado_em)
    assert invertido.etapas_ordenadas() == repasse.etapas_ordenadas()


def test_repasse_recusa_duas_etapas_atuais_ordens_e_ids_repetidos():
    repasse = repasses_exemplo()[0]
    primeira, atual, pendente = repasse.etapas
    combinacoes = [
        (primeira, atual, replace(pendente, status=StatusEtapaRepasse.atual)),
        (primeira, atual, replace(pendente, ordem=atual.ordem)),
        (primeira, atual, replace(pendente, id=atual.id)),
        (replace(primeira, status=StatusEtapaRepasse.pendente, ocorrido_em=None), atual,
         replace(pendente, status=StatusEtapaRepasse.concluida, ocorrido_em=repasse.atualizado_em)),
        (primeira, replace(atual, status=StatusEtapaRepasse.pendente), pendente),
    ]
    for etapas in combinacoes:
        with pytest.raises(DadoInvalido):
            Repasse(repasse.fatura_id, etapas, repasse.atualizado_em)


def test_etapa_concluida_nao_aceita_previsao_e_precisa_evento():
    primeira = repasses_exemplo()[0].etapas[0]
    with pytest.raises(DadoInvalido):
        replace(primeira, previsao=date(2026, 8, 18))
    with pytest.raises(DadoInvalido):
        replace(primeira, ocorrido_em=None)


def test_repasse_recusa_lista_vazia_e_atualizacao_anterior_ao_evento():
    repasse = repasses_exemplo()[0]
    with pytest.raises(DadoInvalido):
        Repasse(repasse.fatura_id, (), repasse.atualizado_em)
    with pytest.raises(DadoInvalido):
        replace(repasse, atualizado_em=repasse.atualizado_em.replace(day=14))
