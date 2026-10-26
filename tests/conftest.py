"""Fixtures compartilhadas pelos testes."""

import pytest
from fastapi.testclient import TestClient

from src.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
