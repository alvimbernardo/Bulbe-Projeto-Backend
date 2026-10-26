from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import pytest
from src.domain.destino_historico import DestinoHistorico
from src.domain.erros import DadoInvalido, ErroDeNegocio, FonteIndisponivel, RecursoNaoEncontrado
from src.repositories.historico_repository import InMemoryHistoricoRepository
from src.services.historico_faturas_service import HistoricoFaturasService

@pytest.mark.parametrize('url', ['http://historico.example/faturas', 'https://malicioso.example/', '//historico.example/', 'https://usuario:senha@historico.example/', 'https://historico.example:444/', 'https://historico.example/faturas#fragmento', 'https://historico.example\\@malicioso.example/', 'https://historico.example/faturas\r\nLocation:malicioso', 'https://historico.example.evil.test/', 'https://historico.example:invalida/'])
def test_destino_inseguro_e_recusado(url):
    with pytest.raises(DadoInvalido):
        DestinoHistorico(url).validar(frozenset({'historico.example'}))

def test_historico_ausente_e_404_e_destino_invalido_e_503():
    service = HistoricoFaturasService(InMemoryHistoricoRepository(), frozenset())
    with pytest.raises(RecursoNaoEncontrado):
        service.obter_destino('cliente_01')
    service = HistoricoFaturasService(InMemoryHistoricoRepository({'cliente_01': DestinoHistorico('https://malicioso.example/')}), frozenset({'historico.example'}))
    with pytest.raises(FonteIndisponivel):
        service.obter_destino('cliente_01')
