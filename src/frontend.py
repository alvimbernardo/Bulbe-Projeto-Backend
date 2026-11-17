"""Entrega das telas do frontend pela propria API e liberacao de CORS para o Live Server."""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

PASTA_FRONTEND = Path(__file__).resolve().parent.parent / "frontend"
PAGINA_INICIAL = "/app/pages/preview.html"
ORIGENS_PADRAO = "http://127.0.0.1:5500,http://localhost:5500"


def origens_permitidas() -> list[str]:
    valor = os.getenv("BULBE_CORS_ORIGENS", ORIGENS_PADRAO)
    return [origem.strip() for origem in valor.split(",") if origem.strip()]


def configurar_frontend(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origens_permitidas(),
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
    )
    if not PASTA_FRONTEND.is_dir():
        return

    @app.get("/app", include_in_schema=False)
    def abrir_telas() -> RedirectResponse:
        return RedirectResponse(PAGINA_INICIAL)

    app.mount("/app", StaticFiles(directory=PASTA_FRONTEND, html=True), name="frontend")
