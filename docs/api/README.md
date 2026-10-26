# Contrato da API

| Arquivo | Conteúdo |
| --- | --- |
| [`openapi.yaml`](openapi.yaml) | Contrato formal em OpenAPI 3.1: os 21 endpoints, parâmetros, corpos, respostas, status codes e formato de erro. |
| [`../requisitos/lista-endpoints.md`](../requisitos/lista-endpoints.md) | Lista de endpoints com descrição, requisito de origem, exemplos e decisões pendentes. |

## Como visualizar o `openapi.yaml`

- **No navegador:** abra o [Swagger Editor](https://editor.swagger.io), vá em *File → Import file* e escolha o `openapi.yaml`.
- **No VS Code:** instale a extensão *OpenAPI (Swagger) Editor* e abra o arquivo.
- **Com a API rodando:** o FastAPI gera a documentação do que já está implementado em http://localhost:8000/docs. Conforme as stories forem entregues, as rotas de `/docs` devem bater com este contrato.

## Resumo dos endpoints

As seis operações públicas de usinas, créditos, resumo e depoimentos já estão implementadas, além de `GET /`. Contas, sessões e rotas individuais continuam planejadas. Consulte o [roteiro de demonstração no README](../../README.md#demonstração-dos-endpoints-públicos-us06-us07-us08-e-us11).

O contrato aceita `atualizado_em: null` na listagem de usinas e no resumo de créditos quando não houver usinas no critério, pois não existe uma data de origem para informar. Campos opcionais dos depoimentos sem valor são omitidos. Entradas inválidas retornam `400` no formato `Erro`, inclusive falhas de validação do FastAPI; o Swagger das rotas públicas documenta esse comportamento.

| Método | Rota | Autenticação |
| --- | --- | --- |
| POST | `/v1/contas` | pública |
| POST | `/v1/sessoes` | pública |
| DELETE | `/v1/sessoes/atual` | sessão |
| GET | `/v1/clientes/{clienteId}` | sessão + vínculo |
| GET | `/v1/usinas` | pública |
| GET | `/v1/usinas/{usinaId}` | pública |
| GET | `/v1/usinas/{usinaId}/creditos` | pública |
| GET | `/v1/creditos-usinas/resumo` | pública |
| GET | `/v1/depoimentos` | pública |
| GET | `/v1/depoimentos/{depoimentoId}` | pública |
| GET | `/v1/clientes/{clienteId}/ativacao` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/ativacao/etapas` | sessão + vínculo |
| PUT | `/v1/clientes/{clienteId}/preferencias-notificacao/ativacao` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/faturas` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}/pagamento` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}/repasse` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/historico-faturas-externo` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/notificacoes` | sessão + vínculo |
| GET | `/v1/clientes/{clienteId}/notificacoes/{notificacaoId}` | sessão + vínculo |
| PATCH | `/v1/clientes/{clienteId}/notificacoes/{notificacaoId}` | sessão + vínculo |

"Sessão + vínculo" significa que a requisição precisa de uma sessão válida e que o `clienteId` da URL tem de ser o cliente vinculado a essa sessão. Caso contrário, a API responde 401 (sem sessão) ou 403 (outro cliente).
