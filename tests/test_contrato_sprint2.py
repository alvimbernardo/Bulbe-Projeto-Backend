"""Contrato versionado e OpenAPI da aplicacao evoluem juntos."""

from pathlib import Path

import yaml


def _resolver(documento, schema):
    if "$ref" in schema:
        return _resolver(documento, documento["components"]["schemas"][schema["$ref"].split("/")[-1]])
    campos = dict(schema.get("properties", {}))
    obrigatorios = set(schema.get("required", []))
    for parte in schema.get("allOf", []):
        propriedades, requeridos = _resolver(documento, parte)
        campos.update(propriedades)
        obrigatorios.update(requeridos)
    return campos, obrigatorios


def test_operacoes_da_sprint_respeitam_contrato_e_documentam_erros(app):
    caminho = Path(__file__).resolve().parents[1] / "docs/api/openapi.yaml"
    previsto = yaml.safe_load(caminho.read_text(encoding="utf-8"))
    gerado = app.openapi()
    operacoes = [(rota, verbo) for rota, item in previsto["paths"].items()
                 if "/notificacoes" not in rota for verbo in item if verbo in {"get", "post", "put", "delete"}]
    assert len(operacoes) == 18  # 17 obrigatorias e a preferencia opcional US12.
    assert len(gerado["paths"]) == 19  # Inclui GET /.
    for rota, verbo in operacoes:
        esperado = previsto["paths"][rota][verbo]
        atual = gerado["paths"][rota][verbo]
        assert atual["operationId"] == esperado["operationId"], rota
        publico = esperado.get("security") == []
        assert bool(atual.get("security")) is not publico, rota
        assert "422" not in atual["responses"] or rota.endswith("/contas") or "preferencias-notificacao" in rota
        for status, resposta in esperado["responses"].items():
            if status not in {"200", "201", "204", "302"}:
                continue
            assert status in atual["responses"], rota
            if "content" not in resposta:
                continue
            campos_esperados, requeridos = _resolver(previsto, resposta["content"]["application/json"]["schema"])
            campos_atuais, obrigatorios_atuais = _resolver(gerado, atual["responses"][status]["content"]["application/json"]["schema"])
            assert set(campos_atuais) == set(campos_esperados), rota
            assert requeridos == obrigatorios_atuais, rota
        parametros = []
        for parametro in esperado.get("parameters", []):
            if "$ref" in parametro:
                parametro = previsto["components"]["parameters"][parametro["$ref"].split("/")[-1]]
            parametros.append((parametro["name"], parametro["in"], parametro.get("required", False)))
        assert sorted(parametros) == sorted((p["name"], p["in"], p.get("required", False)) for p in atual.get("parameters", [])), rota
    assert gerado["components"]["securitySchemes"]["sessao"]["bearerFormat"] == "JWT"
