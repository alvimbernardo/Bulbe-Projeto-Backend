# Backlog da Sprint 3 — API Bulbe

- **Equipe:** Squad Master
- **Sprint:** 3, de 28/10/2026 a 04/11/2026 (aulas 26 e 28)
- **Objetivo da sprint:** trocar a persistência em memória por um banco relacional, com SQLAlchemy 2 e migrations do Alembic, sem mudar Services, Controllers nem Domínio.
- **Review:** Sprint Review III, 11/11/2026, com dados persistidos, migrations versionadas e testes de integração rodando.
- **Estimativa:** story points na escala de Fibonacci (1, 2, 3, 5, 8, 13).
- **Modelo do banco:** [`docs/diagramas/modelo-banco.svg`](../diagramas/modelo-banco.svg) e a seção [Banco de dados](../../README.md#banco-de-dados) do README.

## Visão geral priorizada

A ordem da tabela é a ordem de execução. A base do banco (S3-01) desbloqueia todos os outros itens.

| ID | Item | Stories atendidas | Pontos | Prioridade | Responsável | Pull request | Situação |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S3-01 | Base do banco: SQLAlchemy, conexão, Alembic e configuração | todas | 3 | Alta | Felipe | #40 | Concluído |
| S3-02 | Tabelas e repositórios SQL de usinas, créditos e depoimentos | US06, US07, US08, US11 | 5 | Alta | Felipe | #40 | Concluído |
| S3-03 | Seed de demonstração no banco | todas | 2 | Alta | Felipe | #40, #41 | Concluído |
| S3-04 | Tabelas e repositórios SQL de clientes, contas e sessões | US01, US02, US03, US04, US05 | 5 | Alta | Felipe | #41 | Concluído |
| S3-05 | Tabelas e repositórios SQL de ativação, faturas, pagamentos, repasses e preferências | US09, US10, US12, US13 | 8 | Alta | Felipe | #41 | Concluído |
| S3-06 | Testes de integração com banco de teste | todas | 5 | Alta | Felipe | #40, #41 | Concluído |
| S3-07 | Diagrama do modelo do banco e documentação da sprint | — | 2 | Média | Felipe | #41, #42 | Concluído |
| S3-08 | Revisão dos pull requests e validação na máquina de cada integrante | — | 2 | Alta | Bernardo, Caio, Luca, Vinicius | — | A fazer |
| S3-09 | Roteiro e ensaio da Review III | — | 2 | Alta | Equipe | — | A fazer |
| S3-10 | PostgreSQL como banco da entrega | todas | 3 | Baixa | a definir | — | Backlog: aguarda confirmação do professor |

### Carga

| Situação | Itens | Pontos |
| --- | --- | --- |
| Concluído | S3-01 a S3-07 | 30 |
| A fazer antes da review | S3-08, S3-09 | 4 |
| Backlog | S3-10 | 3 |

O histórico externo de faturas (US14) não ganhou tabela: o destino aprovado vem da configuração (`BULBE_HISTORICO_URL` e `BULBE_HISTORICO_HOSTS_APROVADOS`) e não é dado de cliente. US15 continua fora do escopo.

### Dependências

- **S3-01** desbloqueia todos os itens: sem a conexão e o Alembic não há tabela nem migration.
- **S3-04** vem antes de **S3-05**, porque ativação, faturas e preferências têm chave estrangeira para `clientes`.
- **S3-03** e **S3-06** acompanham cada entrega: cada tabela nova entra no seed e ganha teste de integração no mesmo pull request.
- Migrations são geradas **uma de cada vez**, sempre a partir da `main` atualizada, para o Alembic não ficar com duas versões em paralelo.

## Detalhamento e critérios de aceite

### S3-01 — Base do banco (3 pts) · PR #40

Conexão com o banco configurável e Alembic pronto para a equipe.

- [x] `SQLAlchemy>=2` e `alembic` no `requirements.txt`.
- [x] `src/db/database.py` com `Base`, `criar_engine` e `criar_fabrica_de_sessoes`; o endereço vem de `BULBE_DATABASE_URL` (padrão `sqlite:///./bulbe.db`).
- [x] Chaves estrangeiras ativadas no SQLite (`PRAGMA foreign_keys=ON`).
- [x] `alembic.ini` e `migrations/env.py` usam o mesmo `BULBE_DATABASE_URL` e o `Base.metadata` do projeto.
- [x] Datas com fuso horário preservadas em qualquer banco (`DataHoraComFuso`).
- [x] `*.db` fora do Git.

### S3-02 — Usinas, créditos e depoimentos no banco (5 pts) · PR #40

- [x] Tabelas `usinas`, `creditos_usinas` (FK `usina_id` → `usinas`) e `depoimentos`, criadas pela migration `0001`.
- [x] `SqlUsinaRepository`, `SqlCreditoUsinaRepository` e `SqlDepoimentoRepository` com os mesmos métodos das versões em memória.
- [x] Os 11 endpoints públicos respondem igual com memória e com banco; o resumo de agosto/2026 continua R$ 74.096,15.
- [x] Crédito de usina inexistente é recusado pela chave estrangeira.

### S3-03 — Seed de demonstração (2 pts) · PRs #40 e #41

- [x] `python -m src.db.seed` grava usinas, créditos, depoimentos, clientes, contas, ativações, faturas, pagamentos e repasses.
- [x] Pode ser executado mais de uma vez sem duplicar registros.
- [x] Usa os mesmos dados fictícios da Sprint 2, para a demonstração continuar igual.

### S3-04 — Clientes, contas e sessões no banco (5 pts) · PR #41

- [x] Tabelas `clientes`, `contas` (FK `cliente_id`; `cliente_id` e `email` únicos) e `sessoes` (FK `conta_id` e `cliente_id`), criadas pela migration `0002`.
- [x] Cadastro repetido continua respondendo 409, agora garantido pela unicidade do banco.
- [x] Conta criada pela API continua existindo depois de reiniciar a aplicação.
- [x] Sessão revogada no logout continua inválida depois de reiniciar a aplicação.

### S3-05 — Ativação, faturas, pagamentos, repasses e preferências no banco (8 pts) · PR #41

- [x] Tabelas `ativacoes` e `etapas_ativacao`, `faturas`, `pagamentos`, `repasses` e `etapas_repasse`, e `preferencias_notificacao`, com FK para `clientes` ou `faturas`, criadas pela migration `0002`.
- [x] Etapas voltam do banco em ordem; o percentual da ativação de cliente_01 continua 50%.
- [x] Fatura de cliente inexistente é recusada pela chave estrangeira.
- [x] Preferência repetida não altera o registro (idempotência), também depois de reiniciar.
- [x] A jornada do cliente (login, 403, ativação, faturas, pagamento, repasse, preferência, cadastro, logout) responde igual com memória e com banco.

### S3-06 — Testes de integração (5 pts) · PRs #40 e #41

- [x] `tests/integracao/` cria um SQLite temporário para cada teste.
- [x] Testes dos repositórios SQL, das chaves estrangeiras e das unicidades.
- [x] Testes da API ligada ao banco, inclusive persistência após reinício.
- [x] Testes das migrations: `upgrade head` cria as 13 tabelas e `downgrade base` remove.
- [x] Testes unitários continuam sem banco (`BULBE_PERSISTENCIA=memoria`); total de 433 testes passando.

### S3-07 — Diagrama e documentação (2 pts) · PRs #41 e #42

- [x] Diagrama do modelo do banco em PlantUML e SVG, com chaves primárias, estrangeiras e unicidades.
- [x] README com o passo a passo do banco, variáveis de ambiente e como criar uma migration nova.
- [x] Este backlog e o roteiro da Review III em `docs/sprints/`.

### S3-08 — Revisão e validação pela equipe (2 pts)

- [ ] Cada integrante faz `git pull`, roda `python -m pytest -q` (433 passed), `alembic upgrade head` e `python -m src.db.seed` na própria máquina.
- [ ] Cada integrante confere as tabelas da sua área de responsabilidade da Sprint 2 no diagrama e no código.
- [ ] Pull requests da sprint revisados por um colega.

### S3-09 — Roteiro e ensaio da Review III (2 pts)

- [ ] Ensaio da sequência de [`roteiro-review-sprint3.md`](roteiro-review-sprint3.md) no notebook que será usado na aula.
- [ ] Banco de demonstração recriado do zero antes da aula.

### S3-10 — PostgreSQL na entrega (3 pts) · backlog

- [ ] Confirmar com o professor se a entrega final precisa de PostgreSQL ou se SQLite é aceito.
- [ ] Se precisar: instalar o driver `psycopg[binary]`, apontar `BULBE_DATABASE_URL` para o PostgreSQL e rodar `alembic upgrade head`. O código não muda.

## Plano da sprint, encontro a encontro

| Data | Foco | Itens |
| --- | --- | --- |
| 28/10 | Do modelo ao schema: SQLAlchemy e primeira migration | S3-01 |
| 04/11 | Repositórios SQL, seed e testes com banco de teste | S3-02 a S3-07 |
| até 10/11 | Revisão pela equipe e ensaio | S3-08, S3-09 |
| 11/11 | Sprint Review III | demonstração ao vivo |

## Definição de Pronto

Um item só vai para **Concluído** quando:

- está integrado na `main` por pull request revisado por um colega;
- `pytest` passa localmente antes de abrir o pull request;
- toda mudança de tabela vem por migration do Alembic, nunca por `create_all` no startup;
- `alembic check` não acusa diferença entre os modelos e as migrations;
- a tabela nova entra no seed e tem teste de integração;
- o card está movido no board, com responsável e estimativa registrados.
