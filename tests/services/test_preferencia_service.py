"""Seguranca do redirecionamento e idempotencia das preferencias."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import pytest
from src.domain.erros import DadoInvalido, ErroDeNegocio, FonteIndisponivel, RecursoNaoEncontrado
from src.repositories.preferencia_repository import InMemoryPreferenciaRepository
from src.services.preferencia_service import PreferenciaService

def test_preferencia_repetida_nao_altera_data_e_mudanca_substitui():
    datas = iter([datetime(2026, 10, 26, tzinfo=timezone.utc) + timedelta(seconds=i) for i in range(3)])
    service = PreferenciaService(InMemoryPreferenciaRepository(), lambda: next(datas))
    primeira = service.alterar('cliente_01', True, ['email', 'email'])
    repetida = service.alterar('cliente_01', True, ['email'])
    assert repetida is primeira
    alterada = service.alterar('cliente_01', False, [])
    assert alterada.atualizada_em > primeira.atualizada_em
    assert alterada.canais == ()

@pytest.mark.parametrize('habilitada,canais', [(True, []), (True, ['sms']), (False, ['whatsapp'])])
def test_canais_sem_suporte_sao_422(habilitada, canais):
    with pytest.raises(ErroDeNegocio) as erro:
        PreferenciaService(InMemoryPreferenciaRepository()).alterar('cliente_01', habilitada, canais)
    assert erro.value.status == 422

def test_preferencia_concorrente_preserva_um_registro_idempotente():
    service = PreferenciaService(InMemoryPreferenciaRepository())
    with ThreadPoolExecutor(max_workers=4) as executor:
        resultados = list(executor.map(lambda _: service.alterar('cliente_01', True, ['email']), range(12)))
    assert all((preferencia is resultados[0] for preferencia in resultados))
