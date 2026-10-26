
import pytest

from src.domain.destino_historico import DestinoHistorico
from src.repositories.historico_repository import InMemoryHistoricoRepository
from src.services.historico_faturas_service import HistoricoFaturasService



def login(client):
    resposta = client.post("/v1/sessoes", json={"email": "cliente01@exemplo.com", "senha": "Bulbe2026!"})
    assert resposta.status_code == 201
    return {"Authorization": f"Bearer {resposta.json()['access_token']}"}


def test_historico_redireciona_para_destino_aprovado(app, client):
    app.state.historico_service = HistoricoFaturasService(InMemoryHistoricoRepository({
        "cliente_01": DestinoHistorico("https://historico.example/faturas"),
    }), frozenset({"historico.example"}))
    resposta = client.get("/v1/clientes/cliente_01/historico-faturas-externo", headers=login(client), follow_redirects=False)
    assert resposta.status_code == 302
    assert resposta.headers["location"] == "https://historico.example/faturas"
    assert resposta.headers["cache-control"] == "no-store"


def test_historico_sem_destino_nao_inventa_link(client):
    resposta = client.get("/v1/clientes/cliente_01/historico-faturas-externo", headers=login(client), follow_redirects=False)
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "RECURSO_NAO_ENCONTRADO"


def test_configuracao_ambiente_so_redireciona_para_host_aprovado(monkeypatch):
    from fastapi.testclient import TestClient
    from src.main import create_app

    monkeypatch.setenv("BULBE_HISTORICO_URL", "https://historico.example/faturas")
    monkeypatch.setenv("BULBE_HISTORICO_HOSTS_APROVADOS", "historico.example")
    with TestClient(create_app()) as client:
        resposta = client.get("/v1/clientes/cliente_01/historico-faturas-externo", headers=login(client), follow_redirects=False)
        assert resposta.status_code == 302
        assert resposta.headers["location"] == "https://historico.example/faturas"
    monkeypatch.setenv("BULBE_HISTORICO_HOSTS_APROVADOS", "outro.example")
    with TestClient(create_app()) as client:
        resposta = client.get("/v1/clientes/cliente_01/historico-faturas-externo", headers=login(client), follow_redirects=False)
        assert resposta.status_code == 503
        assert "location" not in resposta.headers


@pytest.mark.parametrize("cliente_id,status", [("cliente_01", 401), ("cliente_02", 403), ("inexistente", 403)])
def test_historico_protegido(client, cliente_id, status):
    headers = {} if status == 401 else login(client)
    resposta = client.get(f"/v1/clientes/{cliente_id}/historico-faturas-externo", headers=headers, follow_redirects=False)
    assert resposta.status_code == status


