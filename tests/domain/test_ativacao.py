"""Invariantes e comportamento do progresso de ativacao (US09)."""

from dataclasses import FrozenInstanceError
from datetime import date, datetime, timedelta, timezone

import pytest

from src.domain.ativacao import Ativacao, EtapaAtivacao, StatusAtivacao
from src.domain.erros import DadoInvalido
from src.repositories.dados_ativacao import ativacoes_exemplo

AGORA = datetime(2026, 10, 26, 12, tzinfo=timezone.utc)


def etapa(ordem, status="pendente", **campos):
    return EtapaAtivacao(f"etapa_{ordem}", ordem, f"Etapa {ordem}", status, **campos)


def test_percentual_e_etapa_atual_calculados_da_mesma_lista():
    ativacao = ativacoes_exemplo()[0]
    assert ativacao.calcular_percentual() == 50
    assert ativacao.obter_etapa_atual().id == "etapa_03"
    assert [e.status for e in ativacao.etapas] == ["concluida", "concluida", "atual", "pendente"]


def test_etapas_sao_ordenadas_e_percentual_truncado():
    ativacao = Ativacao("cliente", "em_andamento", [etapa(3), etapa(1, "concluida"), etapa(2, "atual")], AGORA)
    assert [e.ordem for e in ativacao.etapas] == [1, 2, 3]
    assert ativacao.calcular_percentual() == 33


@pytest.mark.parametrize("status,estados,percentual", [
    ("nao_iniciada", ["pendente", "pendente"], 0),
    ("cancelada", ["concluida", "pendente"], 50),
    ("concluida", ["concluida", "concluida"], 100),
])
def test_estados_sem_etapa_atual(status, estados, percentual):
    ativacao = Ativacao("cliente", status, [etapa(i, s) for i, s in enumerate(estados, 1)], AGORA)
    assert ativacao.calcular_percentual() == percentual
    assert ativacao.obter_etapa_atual() is None


@pytest.mark.parametrize("status,estados", [
    ("em_andamento", ["atual", "atual"]),
    ("em_andamento", ["pendente", "atual"]),
    ("em_andamento", ["atual", "concluida"]),
    ("em_andamento", ["concluida", "pendente"]),
    ("concluida", ["concluida", "pendente"]),
    ("nao_iniciada", ["concluida", "pendente"]),
    ("nao_iniciada", ["atual", "pendente"]),
    ("cancelada", ["atual", "pendente"]),
    ("cancelada", ["concluida", "concluida"]),
])
def test_recusa_status_e_sequencias_incoerentes(status, estados):
    with pytest.raises(DadoInvalido):
        Ativacao("cliente", status, [etapa(i, s) for i, s in enumerate(estados, 1)], AGORA)


@pytest.mark.parametrize("etapas", [
    [],
    [etapa(1), etapa(1)],
    [etapa(1), EtapaAtivacao("etapa_1", 2, "Repetida", "pendente")],
])
def test_recusa_etapas_vazias_ordens_ou_ids_duplicados(etapas):
    with pytest.raises(DadoInvalido):
        Ativacao("cliente", "nao_iniciada", etapas, AGORA)


@pytest.mark.parametrize("campos", [
    {"id": "", "ordem": 1, "nome": "Etapa", "status": "pendente"},
    {"id": "etapa", "ordem": 0, "nome": "Etapa", "status": "pendente"},
    {"id": "etapa", "ordem": 1, "nome": " ", "status": "pendente"},
    {"id": "etapa", "ordem": 1, "nome": "Etapa", "status": "invalido"},
])
def test_recusa_dados_invalidos_de_etapa(campos):
    with pytest.raises(DadoInvalido):
        EtapaAtivacao(**campos)


def test_data_conclusao_exige_fuso_e_etapa_concluida():
    with pytest.raises(DadoInvalido):
        etapa(1, "concluida", concluida_em=AGORA.replace(tzinfo=None))
    with pytest.raises(DadoInvalido):
        etapa(1, "pendente", concluida_em=AGORA)
    with pytest.raises(DadoInvalido):
        Ativacao("cliente", "nao_iniciada", [etapa(1)], AGORA.replace(tzinfo=None))


def test_conclusao_avanca_etapa_sem_modificar_instancia_original():
    original = Ativacao("cliente", "em_andamento", [etapa(1, "atual"), etapa(2)], AGORA)
    nova = original.concluir_etapa_atual(AGORA + timedelta(hours=1))
    assert original.calcular_percentual() == 0
    assert original.obter_etapa_atual().id == "etapa_1"
    assert nova.calcular_percentual() == 50
    assert nova.obter_etapa_atual().id == "etapa_2"
    assert nova.etapas[0].concluida_em == AGORA + timedelta(hours=1)


def test_conclusao_final_atualiza_status_e_remove_previsao():
    ativacao = Ativacao("cliente", "em_andamento", [etapa(1, "atual")], AGORA,
                       previsao_conclusao=date(2026, 11, 1))
    final = ativacao.concluir_etapa_atual(AGORA + timedelta(hours=1))
    assert final.status is StatusAtivacao.concluida
    assert final.calcular_percentual() == 100
    assert final.obter_etapa_atual() is None
    assert final.previsao_conclusao is None
    with pytest.raises(DadoInvalido):
        final.concluir_etapa_atual(AGORA + timedelta(hours=2))


def test_recusa_conclusao_de_etapa_pendente_ou_anterior_a_atualizacao():
    with pytest.raises(DadoInvalido):
        etapa(1).concluir(AGORA)
    with pytest.raises(DadoInvalido):
        etapa(1, "concluida").iniciar()
    ativacao = Ativacao("cliente", "em_andamento", [etapa(1, "atual")], AGORA)
    with pytest.raises(DadoInvalido):
        ativacao.concluir_etapa_atual(AGORA - timedelta(seconds=1))


def test_entidades_imutaveis_e_lista_copiada():
    etapas = [etapa(1)]
    ativacao = Ativacao("cliente", "nao_iniciada", etapas, AGORA)
    etapas.append(etapa(2))
    assert len(ativacao.etapas) == 1
    with pytest.raises(FrozenInstanceError):
        ativacao.etapas[0].status = "concluida"
