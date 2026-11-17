"""Testes da entrega das telas pela API e do CORS para o Live Server."""

import pytest

PAGINAS = [
    "preview.html",
    "intro-bulbe.html",
    "usinas.html",
    "experiencia.html",
    "info-ativacao.html",
    "login.html",
    "ativacao.html",
    "fatura-e-repasse.html",
]


def test_app_redireciona_para_o_fluxo_de_telas(client):
    resposta = client.get("/app", follow_redirects=False)

    assert resposta.status_code == 307
    assert resposta.headers["location"] == "/app/pages/preview.html"


@pytest.mark.parametrize("pagina", PAGINAS)
def test_todas_as_telas_sao_servidas(client, pagina):
    resposta = client.get(f"/app/pages/{pagina}")

    assert resposta.status_code == 200
    assert "text/html" in resposta.headers["content-type"]


@pytest.mark.parametrize("pagina", ["usinas.html", "experiencia.html", "login.html", "ativacao.html", "fatura-e-repasse.html"])
def test_telas_ligadas_a_api_carregam_o_cliente_http(client, pagina):
    html = client.get(f"/app/pages/{pagina}").text

    assert '<script src="../js/api.js"></script>' in html


def test_cliente_http_e_os_estilos_sao_servidos(client):
    assert client.get("/app/js/api.js").status_code == 200
    assert client.get("/app/css/global.css").status_code == 200


def test_telas_nao_aparecem_no_contrato_da_api(client):
    caminhos = client.get("/openapi.json").json()["paths"]

    assert not any(caminho.startswith("/app") for caminho in caminhos)


def test_cors_libera_o_live_server(client):
    resposta = client.options(
        "/v1/usinas",
        headers={"Origin": "http://127.0.0.1:5500", "Access-Control-Request-Method": "GET"},
    )

    assert resposta.status_code == 200
    assert resposta.headers["access-control-allow-origin"] == "http://127.0.0.1:5500"


def test_cors_nao_libera_origem_desconhecida(client):
    resposta = client.get("/v1/usinas", headers={"Origin": "https://site-desconhecido.com"})

    assert "access-control-allow-origin" not in resposta.headers


def test_rotas_da_api_continuam_funcionando_com_as_telas(client):
    assert client.get("/v1/usinas").status_code == 200
    assert client.get("/app/pages/nao-existe.html").status_code == 404
