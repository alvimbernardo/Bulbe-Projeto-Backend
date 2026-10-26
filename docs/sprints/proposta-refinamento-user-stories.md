# Proposta de refinamento do backlog — Bulbe

> Preparada e aplicada pelo navegador em 26/10/2026. As 18 issues existentes foram refinadas em Markdown e transferidas para o board Backend Sprint 2, com prioridade e Estimate nos campos nativos. As descrições atuais das issues são a referência final; este documento preserva a proposta usada na revisão. Prioridades e pontos foram mantidos, sem nova estimativa da equipe.

## Fontes e critério

- [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 3–8: um backlog por produto; histórias na perspectiva do consumidor; critérios de aceite por comportamento; DoD; Fibonacci.
- [Backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md): escopo, divisão e estimativas.
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml): rotas, status e schemas.
- [Board Backend Sprint 1](https://github.com/users/alvimbernardo/projects/3/views/1): após a revisão, somente os 6 entregáveis históricos em Done.
- [Board Backend Sprint 2](https://github.com/users/alvimbernardo/projects/4/views/1): após a revisão, 12 itens em To do (51 pontos), 4 em In progress (14 pontos) e 2 em Backlog (8 pontos). Sem novas issues ou duplicatas. P0 = Alta, P1 = Média, P2 = Baixa.

## Organização proposta

| Destino | Issues | Tratamento |
| --- | --- | --- |
| Sprint 1 — entregáveis históricos | #1, #2, #3, #4, #5, #6 | Manter concluídos; são entregáveis de planejamento/documentação, não inventar histórias de API para eles. |
| Sprint 2 — implementação obrigatória | #7–#20, #22, #23 | Associar as mesmas issues ao board da Sprint 2; remover apenas a associação à Sprint 1 após conferir o destino. Não excluir nem duplicar issues. |
| Sprint 2 — opcional | #21 (US12) | Selecionar somente se houver capacidade. |
| Backlog futuro | #24 (US15) | Mantida na coluna Backlog do segundo board, explicitamente fora do compromisso da Sprint 2; responsável a definir. |

As histórias de API podem ter sido planejadas na Sprint 1. A associação à sprint de implementação precisa refletir quando serão entregues. Um único backlog de produto pode ter visões diferentes por sprint. Antes de movimentar, conferir os cards do segundo board para evitar duplicidades.

## Responsabilidade e capacidade

| Responsável | Itens obrigatórios | Pontos |
| --- | --- | --- |
| Bernardo (@alvimbernardo) | TEC-01, TEC-02, TEC-03, US04 | 13 |
| Caio (@CaioFreitas10) | US01, US02, US14 | 12 |
| Felipe (@FelipeMedeiros30) | US06, US07, US08, US11 | 14 |
| Luca (@lucabelleig) | US03, US05 | 13 |
| Vinicius (@viniciusbianchetti12) | US09, US10, US13 | 13 |
| **Total documentado** | **16 itens (13 histórias e 3 técnicos)** | **65** |

US12 adiciona 3 pontos opcionais a Vinicius. US15 tem 5 pontos no backlog futuro. Story points representam esforço relativo, não horas. A capacidade precisa ser validada pela equipe; esta revisão preserva as estimativas registradas.

## Aplicação no GitHub

1. Atualizar as descrições das issues existentes com as seções abaixo, mantendo IDs, histórico e assignees.
2. Conferir no board da Sprint 2 se cada issue já está associada; adicionar somente as ausentes.
3. Preencher os campos nativos de prioridade e Estimate com os valores das descrições. Esta proposta em Markdown não altera campos nativos do Project.
4. Preservar o estado de trabalho: US06, US07, US08 e US11 estavam em In progress. Não marcar como Done pela existência das camadas internas.
5. Retirar do board da Sprint 1 apenas os vínculos dos itens de implementação, mantendo os seis entregáveis concluídos.
6. Manter US12 como opcional e US15 no backlog futuro. Conferir a ausência de duplicatas.

## Descrições em Markdown para as issues existentes

# TEC-01 — Estrutura base, injeção de dependência e erro padronizado — issue #17

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/17)

## Objetivo técnico

Como equipe de desenvolvimento, queremos a estrutura `src/` com as quatro camadas e um formato de erro único, para que cada story só precise adicionar a sua parte.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | TEC-01 |
| Tipo | Item técnico habilitador |
| Responsável | @alvimbernardo |
| Prioridade | Alta |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 1 |
| Requisitos de origem | RNF009, RNF010 |

## Abrangência

- Transversal aos endpoints e às quatro camadas da API.

## Critérios de aceite

- [ ] `src/main.py` sobe com `uvicorn src.main:app --reload` e expõe `/docs`.
- [ ] Serviços recebem repositórios pelo construtor; `main.py` é o único lugar que decide qual implementação de repositório usar.
- [ ] Erros de negócio, de validação do Pydantic e de rota inexistente saem todos no formato do contrato: `codigo`, `mensagem`, `detalhes`, `request_id`.

## Dependências

Base transversal: coordenar a implementação com as histórias que usam a estrutura, os repositórios e os testes.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# TEC-02 — Repositórios em memória com dados de exemplo da Bulbe — issue #18

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/18)

## Objetivo técnico

Como equipe, queremos repositórios em memória com dados de exemplo coerentes, para demonstrar a API na Review II sem depender das fontes oficiais.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | TEC-02 |
| Tipo | Item técnico habilitador |
| Responsável | @alvimbernardo |
| Prioridade | Alta |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 2 |
| Requisitos de origem | RNF006 |

## Abrangência

- Transversal aos endpoints e às quatro camadas da API.

## Critérios de aceite

- [ ] Cada repositório tem uma interface (classe abstrata) e uma implementação `InMemory...`.
- [ ] Dados de exemplo com pelo menos: 4 usinas (uma inativa), créditos em duas competências, 2 clientes com conta, ativação em andamento, faturas paga e em aberto, repasse em andamento, 3 depoimentos (um não autorizado).
- [ ] Dados de exemplo ficam separados do código de produção, para serem trocados pelo seed do banco na Sprint 3.

## Dependências

Base transversal: coordenar a implementação com as histórias que usam a estrutura, os repositórios e os testes.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# TEC-03 — Base de testes (pytest, TestClient, fixtures) — issue #19

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/19)

## Objetivo técnico

Como equipe, queremos uma base de testes pronta, para que cada story já nasça com testes.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | TEC-03 |
| Tipo | Item técnico habilitador |
| Responsável | @alvimbernardo |
| Prioridade | Alta |
| Estimativa | 2 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 3 |
| Requisitos de origem | — |

## Abrangência

- Transversal aos endpoints e às quatro camadas da API.

## Critérios de aceite

- [ ] `pytest` roda a partir da raiz com um comando.
- [ ] Fixture de `TestClient` e fixtures de repositórios em memória limpos a cada teste.
- [ ] Teste de fumaça: `GET /` responde 200 e `/docs` está disponível.

## Dependências

Base transversal: coordenar a implementação com as histórias que usam a estrutura, os repositórios e os testes.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US01 — Autenticar cliente — issue #7

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/7)

## User Story de API

Como aplicação cliente, eu quero enviar credenciais válidas e receber um token de sessão, para que o usuário acesse sua área individual.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US01 |
| Tipo | User Story |
| Responsável | @CaioFreitas10 |
| Prioridade | Alta |
| Estimativa | 8 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 4 |
| Requisitos de origem | RF003, RNF002 |

## Endpoints

- `POST /v1/sessoes`

## Critérios de aceite

- [ ] Credenciais válidas retornam **201** com `sessao_id`, `conta_id`, `cliente_id` e `expira_em`, conforme o contrato.
- [ ] Credenciais inválidas retornam 401 sem revelar qual campo falhou.
- [ ] Senha armazenada somente como hash com salt, nunca devolvida na resposta nem registrada em logs; transporte protegido por HTTPS no ambiente publicado.
- [ ] Tentativas repetidas são limitadas e retornam 429.

## Dependências

#9 e #11 (conta vinculada ativa nos dados de exemplo); #17, #18 e #19.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

Alinhamento ao contrato: criação da sessão retorna 201, substituindo o 200 da descrição anterior. JWT é o mecanismo previsto para a implementação; a representação do token e do cabeçalho deve ser formalizada no OpenAPI antes da integração, pois o contrato atual descreve identificadores de sessão.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US02 — Encerrar sessão — issue #8

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/8)

## User Story de API

Como aplicação cliente, eu quero encerrar a sessão atual, para que o token deixe de valer quando o usuário clicar em Sair.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US02 |
| Tipo | User Story |
| Responsável | @CaioFreitas10 |
| Prioridade | Alta |
| Estimativa | 2 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 5 |
| Requisitos de origem | RF005 |

## Endpoints

- `DELETE /v1/sessoes/atual`

## Critérios de aceite

- [ ] `DELETE /v1/sessoes/atual` com sessão válida retorna 204 sem corpo.
- [ ] A mesma sessão, usada depois, retorna 401.
- [ ] Sem sessão ou com sessão inválida retorna 401.

## Dependências

#7 (sessão e validação de token).

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

Alinhamento ao contrato: token expirado ou inválido retorna 401; isso substitui o sucesso idempotente descrito anteriormente.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US04 — Proteger dados individuais — issue #10

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/10)

## User Story de API

Como aplicação cliente, eu quero que a API recuse acesso aos dados de outro cliente, para que cada pessoa veja apenas as próprias informações.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US04 |
| Tipo | User Story |
| Responsável | @alvimbernardo |
| Prioridade | Alta |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 6 |
| Requisitos de origem | RF006, RNF003 |

## Endpoints

- `GET /v1/clientes/{clienteId}`

## Critérios de aceite

- [ ] `GET /v1/clientes/{clienteId}` do próprio cliente retorna 200 com os dados básicos.
- [ ] Sem sessão retorna 401.
- [ ] Sessão válida consultando outro `clienteId` retorna 403, mesmo que esse cliente exista.
- [ ] A regra é reaproveitada por todas as rotas `/v1/clientes/{clienteId}/...`.

## Dependências

#7 (sessão válida) e #11 (vínculo).

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US06 — Listar usinas ativas — issue #12

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/12)

## User Story de API

Como aplicação frontend, eu quero listar as usinas da Bulbe, para exibir os cards de usinas na página pública.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US06 |
| Tipo | User Story |
| Responsável | @FelipeMedeiros30 |
| Prioridade | Alta |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 7 |
| Requisitos de origem | RF008, RF011 |

## Endpoints

- `GET /v1/usinas`
- `GET /v1/usinas/{usinaId}`

## Critérios de aceite

- [ ] `GET /v1/usinas` retorna a lista paginada com `page`, `limit`, `total` e `atualizado_em`.
- [ ] Sem filtro, retorna só usinas ativas; `?status=` filtra pela situação.
- [ ] `GET /v1/usinas/{usinaId}` retorna a usina com região; id inexistente retorna 404.
- [ ] Lista sem resultados retorna 200 com `data: []`, mantendo os metadados de paginação.

## Dependências

#17 (estrutura), #18 (dados em memória) e #19 (base de testes). Rotas públicas, sem dependência de autenticação.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US07 — Consultar crédito gerado por usina — issue #13

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/13)

## User Story de API

Como aplicação frontend, eu quero consultar os créditos de uma usina em uma competência, para exibir o valor em reais no card da usina.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US07 |
| Tipo | User Story |
| Responsável | @FelipeMedeiros30 |
| Prioridade | Alta |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 8 |
| Requisitos de origem | RF009 |

## Endpoints

- `GET /v1/usinas/{usinaId}/creditos`

## Critérios de aceite

- [ ] Competência válida retorna 200 com `creditos` no formato `{ valor, moeda }`.
- [ ] Competência ausente ou fora do formato `AAAA-MM` retorna 400.
- [ ] Usina inexistente ou período sem dado retorna 404, nunca um valor zero inventado.
- [ ] Resposta inclui `usina_id`, `competencia` e `atualizado_em`.

## Dependências

#17 (estrutura), #18 (dados em memória) e #19 (base de testes). Rotas públicas, sem dependência de autenticação.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

Na Sprint 2 os dados são de exemplo e ficam em memória. Falta de registro no período retorna 404; indisponibilidade de fonte externa é um cenário distinto, tratado conforme o contrato quando existir essa integração.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US08 — Consultar total gerado — issue #14

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/14)

## User Story de API

Como aplicação frontend, eu quero o total de créditos de todas as usinas no período, para exibir o card "Total gerado".

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US08 |
| Tipo | User Story |
| Responsável | @FelipeMedeiros30 |
| Prioridade | Alta |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 9 |
| Requisitos de origem | RF010 |

## Endpoints

- `GET /v1/creditos-usinas/resumo`

## Critérios de aceite

- [ ] Retorna `total_creditos`, `quantidade_usinas` e o `criterio` usado.
- [ ] O total é a soma dos créditos das usinas do critério na mesma competência.
- [ ] Competência inválida retorna 400.
- [ ] Teste unitário do cálculo no Service, sem subir a API.

## Dependências

#17 (estrutura), #18 (dados em memória) e #19 (base de testes). Rotas públicas, sem dependência de autenticação.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US09 — Consultar progresso da ativação — issue #15

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/15)

## User Story de API

Como aplicação cliente, eu quero o progresso real da ativação, para exibir percentual, etapa atual, etapas concluídas e pendentes.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US09 |
| Tipo | User Story |
| Responsável | @viniciusbianchetti12 |
| Prioridade | Alta |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 10 |
| Requisitos de origem | RF015–RF019 |

## Endpoints

- `GET /v1/clientes/{clienteId}/ativacao`
- `GET /v1/clientes/{clienteId}/ativacao/etapas`

## Critérios de aceite

- [ ] `.../ativacao` retorna status, percentual e etapa atual.
- [ ] `.../ativacao/etapas` retorna as etapas na ordem oficial, cada uma como `concluida`, `atual` ou `pendente`.
- [ ] O percentual é calculado a partir das etapas concluídas e bate com a lista de etapas.
- [ ] Cliente sem ativação retorna 404; outro cliente retorna 403.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.

## Dependências

#10 (autorização do cliente).

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US10 — Consultar fatura e situação do pagamento — issue #16

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/16)

## User Story de API

Como aplicação cliente, eu quero os dados da fatura vigente e o status do pagamento, para exibir valor, competência e situação ao cliente.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US10 |
| Tipo | User Story |
| Responsável | @viniciusbianchetti12 |
| Prioridade | Alta |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 11 |
| Requisitos de origem | RF021, RF022 |

## Endpoints

- `GET /v1/clientes/{clienteId}/faturas`
- `GET /v1/clientes/{clienteId}/faturas/{faturaId}`
- `GET /v1/clientes/{clienteId}/faturas/{faturaId}/pagamento`

## Critérios de aceite

- [ ] Valor, competência e identificador exibível visíveis.
- [ ] Situação do pagamento com forma, data e hora quando houver.
- [ ] Período sem fatura retorna resposta explícita (lista vazia ou 404 na fatura específica), não um erro genérico.
- [ ] Outro cliente retorna 403.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.

## Dependências

#10 (autorização do cliente).

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US13 — Acompanhar o repasse à CEMIG — issue #22

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/22)

## User Story de API

Como aplicação cliente, eu quero as etapas do repasse de uma fatura, para exibir a linha do tempo do repasse à CEMIG.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US13 |
| Tipo | User Story |
| Responsável | @viniciusbianchetti12 |
| Prioridade | Alta |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 12 |
| Requisitos de origem | RF023 |

## Endpoints

- `GET /v1/clientes/{clienteId}/faturas/{faturaId}/repasse`

## Critérios de aceite

- [ ] Retorna status geral e etapas em ordem, com `ocorrido_em`, `previsao` e `mensagem`.
- [ ] Fatura sem repasse retorna 404; outro cliente retorna 403.
- [ ] Previsão é informada somente para etapas não concluídas.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.

## Dependências

#10 e #16.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US03 — Iniciar cadastro / primeiro acesso — issue #9

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/9)

## User Story de API

Como aplicação cliente, eu quero enviar os dados de primeiro acesso, para que um cliente Bulbe elegível crie sua conta digital.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US03 |
| Tipo | User Story |
| Responsável | @lucabelleig |
| Prioridade | Alta |
| Estimativa | 8 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 13 |
| Requisitos de origem | RF004 |

## Endpoints

- `POST /v1/contas`

## Critérios de aceite

- [ ] Dados válidos de cliente elegível retornam 201 com a conta criada.
- [ ] Campos ausentes ou malformados retornam 400 no formato de erro padrão.
- [ ] Cliente que já tem conta retorna 409.
- [ ] Cliente inelegível ou vínculo não confirmado retorna 422.
- [ ] Senha guardada apenas como hash.

## Dependências

#11 (vínculo), desenvolvido na mesma branch; #17, #18 e #19.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

Alinhamento ao contrato: erro de formato retorna 400; recusa pela regra de elegibilidade/vínculo retorna 422. A política de primeiro acesso ainda depende de validação com a Bulbe; na Sprint 2, usar cenários explicitamente definidos nos dados de exemplo.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US05 — Associar conta digital ao cadastro Bulbe — issue #11

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/11)

## User Story de API

Como aplicação cliente, eu quero que a conta criada fique vinculada ao cadastro correto do cliente, para que os dados individuais exibidos sejam os dele.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US05 |
| Tipo | User Story |
| Responsável | @lucabelleig |
| Prioridade | Alta |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 14 |
| Requisitos de origem | RF007 |

## Endpoints

- `POST /v1/contas`

## Critérios de aceite

- [ ] O vínculo usa o `identificador_cliente` informado no primeiro acesso.
- [ ] Conta sem vínculo confirmado não acessa nenhuma rota de cliente.
- [ ] A resposta de criação de conta traz o `cliente_id` vinculado.
- [ ] Cliente inelegível ou vínculo não confirmado retorna 422; conta já existente para o cliente retorna 409.

## Dependências

#9 (cadastro), desenvolvido na mesma branch; não cria endpoint adicional.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

Alinhamento ao contrato: esta história implementa o vínculo no POST /v1/contas, junto da US03. Consulta do perfil é escopo da US04. Não criar um segundo endpoint de cadastro nem contabilizar a mesma entrega duas vezes.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US11 — Listar depoimentos públicos autorizados — issue #20

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/20)

## User Story de API

Como aplicação frontend, eu quero listar os depoimentos autorizados, para exibir as histórias de clientes sem conteúdo fixo no HTML.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US11 |
| Tipo | User Story |
| Responsável | @FelipeMedeiros30 |
| Prioridade | Média |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 15 |
| Requisitos de origem | RF012, RF013, RNF004 |

## Endpoints

- `GET /v1/depoimentos`
- `GET /v1/depoimentos/{depoimentoId}`

## Critérios de aceite

- [ ] `GET /v1/depoimentos` retorna só depoimentos com publicação autorizada.
- [ ] Depoimento não autorizado consultado por id retorna 404.
- [ ] Nenhum dado pessoal além dos campos públicos do contrato.

## Dependências

#17 (estrutura), #18 (dados em memória) e #19 (base de testes). Rotas públicas, sem dependência de autenticação.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US14 — Acessar histórico externo de faturas — issue #23

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/23)

## User Story de API

Como aplicação cliente, eu quero ser redirecionada ao histórico oficial de faturas, para que o cliente consulte faturas antigas no sistema da Bulbe.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US14 |
| Tipo | User Story |
| Responsável | @CaioFreitas10 |
| Prioridade | Média |
| Estimativa | 2 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 |
| Ordem no backlog documentado | 16 |
| Requisitos de origem | RF024 |

## Endpoints

- `GET /v1/clientes/{clienteId}/historico-faturas-externo`

## Critérios de aceite

- [ ] Retorna 302 com cabeçalho `Location` apontando para uma URL HTTPS configurada.
- [ ] Destino não configurado retorna 404; outro cliente retorna 403.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.

## Dependências

#10.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US12 — Configurar atualizações da ativação — issue #21

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/21)

## User Story de API

Como aplicação cliente, eu quero salvar a preferência de receber atualizações da ativação, para que o botão "Receber atualizações" funcione de verdade.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US12 |
| Tipo | User Story |
| Responsável | @viniciusbianchetti12 |
| Prioridade | Média |
| Estimativa | 3 story points (Fibonacci) |
| Sprint de implementação | Sprint 2 — opcional, se houver capacidade |
| Ordem no backlog documentado | 17 |
| Requisitos de origem | RF020 |

## Endpoints

- `PUT /v1/clientes/{clienteId}/preferencias-notificacao/ativacao`

## Critérios de aceite

- [ ] PUT com canal suportado retorna 200 com a preferência salva.
- [ ] Repetir o mesmo PUT não cria duplicidade.
- [ ] Canal não suportado retorna 422.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.

## Dependências

#10 e #15; somente se houver capacidade após os itens obrigatórios.

## Escopo e regras

- Sprint 2: quatro camadas, regras no domínio/serviços e repositórios em memória com dados de exemplo.
- Banco relacional, ORM e migrations ficam para a Sprint 3.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---

# US15 — Consultar e marcar notificações — issue #24

[Issue existente](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/issues/24)

## User Story de API

Como aplicação cliente, eu quero listar notificações e marcá-las como lidas, para exibir o contador de não lidas.

## Planejamento

| Campo | Valor |
| --- | --- |
| ID | US15 |
| Tipo | User Story |
| Responsável | A definir pela equipe |
| Prioridade | Baixa |
| Estimativa | 5 story points (Fibonacci) |
| Sprint de implementação | Backlog do produto — fora da Sprint 2 |
| Ordem no backlog documentado | 18 |
| Requisitos de origem | RF025 |

## Endpoints

- `GET /v1/clientes/{clienteId}/notificacoes`
- `GET /v1/clientes/{clienteId}/notificacoes/{notificacaoId}`
- `PATCH /v1/clientes/{clienteId}/notificacoes/{notificacaoId}`

## Critérios de aceite

- [ ] Lista paginada com `nao_lidas`; filtro `?lida=`.
- [ ] PATCH altera só o estado de leitura e registra `lida_em`.
- [ ] Sem sessão válida retorna 401; tentativa de acessar dados de outro cliente retorna 403.
- [ ] Consulta individual retorna somente notificação pertencente ao cliente autenticado; recurso inexistente retorna 404.

## Dependências

#10; depende de confirmação do escopo com a Bulbe.

## Escopo e regras

- Escopo futuro; confirmar com a Bulbe antes de selecionar para uma sprint.

Fora do compromisso da Sprint 2. Responsável ainda não definido; não atribuir a um integrante sem definição da equipe.

## Definição de Pronto (DoD)

- [ ] Código integrado à `main` por Pull Request aprovado por pelo menos um colega.
- [ ] Testes automatizados das regras e dos comportamentos HTTP aplicáveis escritos e passando com `pytest`.
- [ ] Endpoint(s), quando aplicável, documentado(s) em Swagger/OpenAPI (`/docs`).
- [ ] Sem erros conhecidos em ambiente de teste; rota, verbo, status e schemas coerentes com o contrato.
- [ ] README atualizado quando necessário; card com responsável, estimativa e situação registrados no board.

## Rastreabilidade

- Modelo de escrita, critérios de aceite, DoD e Fibonacci: [Aula 05 — Product Backlog e Planning Sprint 1](https://docs.google.com/presentation/d/1nwAxDoA6SO6oa4d3s4Ytv5-pexO_1oDGZVv5zKnG5-g/edit?usp=drivesdk), slides 4–8.
- Escopo, responsáveis e estimativas: [backlog documentado da Sprint 2](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/sprints/backlog-sprint-2.md).
- [Contrato OpenAPI](https://github.com/alvimbernardo/Bulbe-Projeto-Backend/blob/main/docs/api/openapi.yaml).
- História refinada na issue existente, preservando ID e histórico. Planejar uma história na Sprint 1 não significa concluir sua implementação naquela sprint.

---


