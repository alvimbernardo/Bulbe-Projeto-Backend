"""Isolamento das dependencias entre instancias da aplicacao."""

from src.main import create_app


def test_aplicacoes_tem_repositorios_e_entidades_independentes():
    primeira = create_app()
    segunda = create_app()
    primeira.state.usina_service.obter("usina_01").nome = "Alterada no teste"
    assert segunda.state.usina_service.obter("usina_01").nome == "Usina Solar Montes Claros I"
    assert primeira.state.credito_service is not segunda.state.credito_service
    assert primeira.state.depoimento_service is not segunda.state.depoimento_service
    primeira.dependency_overrides[object] = lambda: None
    assert segunda.dependency_overrides == {}
