"""Testes dos repositorios em memoria de usinas, creditos e depoimentos."""

from src.domain.competencia import Competencia
from src.repositories.credito_usina_repository import InMemoryCreditoUsinaRepository
from src.repositories.dados_exemplo import (
    AGOSTO_2026,
    creditos_exemplo,
    depoimentos_exemplo,
    usinas_exemplo,
)
from src.repositories.depoimento_repository import InMemoryDepoimentoRepository
from src.repositories.usina_repository import InMemoryUsinaRepository


def test_dados_de_exemplo_cobrem_os_cenarios():
    usinas = usinas_exemplo()
    assert len(usinas) == 4
    assert sum(1 for u in usinas if u.status.value == "inativa") == 1
    assert {c.competencia for c in creditos_exemplo()} == {Competencia(2026, 7), AGOSTO_2026}
    depoimentos = depoimentos_exemplo()
    assert len(depoimentos) == 3
    assert sum(1 for d in depoimentos if not d.publicacao_autorizada) == 1


def test_usina_repository_lista_ordenado_e_obtem_por_id():
    repositorio = InMemoryUsinaRepository(reversed(usinas_exemplo()))
    assert [u.id for u in repositorio.listar()] == ["usina_01", "usina_02", "usina_03", "usina_04"]
    assert repositorio.obter("usina_02").nome == "Usina Solar Janauba"
    assert repositorio.obter("usina_99") is None


def test_credito_repository_busca_por_usina_e_competencia():
    repositorio = InMemoryCreditoUsinaRepository(creditos_exemplo())
    assert repositorio.obter("usina_01", AGOSTO_2026).usina_id == "usina_01"
    assert repositorio.obter("usina_04", AGOSTO_2026) is None
    assert [c.usina_id for c in repositorio.listar_por_competencia(AGOSTO_2026)] == [
        "usina_01",
        "usina_02",
        "usina_03",
    ]
    assert repositorio.listar_por_competencia(Competencia(2026, 9)) == []


def test_depoimento_repository_obtem_por_id():
    repositorio = InMemoryDepoimentoRepository(depoimentos_exemplo())
    assert len(repositorio.listar()) == 3
    assert repositorio.obter("depoimento_03").publicacao_autorizada is False
    assert repositorio.obter("depoimento_99") is None


def test_repositorios_comecam_vazios():
    assert InMemoryUsinaRepository().listar() == []
    assert InMemoryDepoimentoRepository().listar() == []
