# Bulbe — Projeto Backend

Backend da plataforma **Bulbe Energia**, desenvolvido pela equipe **Squad Master** na disciplina Projeto Ciência de Dados II, do Ibmec. A API dará suporte ao frontend do Projeto Ciência de Dados I, com consultas de usinas, créditos de energia, ativação, faturas, pagamentos e repasses à CEMIG.

## Sobre o projeto

- **Empresa parceira:** Bulbe Energia.
- **Problema que o projeto resolve:** fornecer ao frontend dados consistentes sobre os serviços da Bulbe e permitir que cada cliente acompanhe sua ativação, suas faturas e seus pagamentos com acesso protegido. A evolução prevista substitui conteúdo fixo e simulações do frontend por informações obtidas das fontes oficiais.
- **Continuidade:** este repositório contém o backend construído no Projeto Ciência de Dados II para atender às funcionalidades levantadas no frontend do Projeto Ciência de Dados I. O link do repositório do frontend ainda não está registrado na documentação.
- **Estágio atual:** endpoints publicos e 8 de 8 entregas seguintes implementadas com dados ficticios em memoria. Ultima entrega: Contrato, jornada integrada, roteiro da review e CI Linux Python 3.11/3.14. Banco e migrations pertencem a Sprint 3; US15 continua fora do escopo.

### Requisitos do sistema

O [documento de requisitos técnicos](docs/requisitos/requisitos-tecnicos-template.md) registra **25 requisitos funcionais (RF001–RF025)** e **12 requisitos não funcionais (RNF001–RNF012)**, derivados das telas e ações do frontend.

| Frente | Requisitos | Comportamento previsto |
| --- | --- | --- |
| Área pública e navegação | RF001, RF002, RF014 | Conteúdo institucional e acesso ao login/cadastro; páginas e linha do tempo estática podem ser atendidas pelo frontend. |
| Contas e sessões | RF003–RF005, RF007 | Autenticar, encerrar sessão, iniciar cadastro/primeiro acesso e vincular a conta ao cliente Bulbe elegível. |
| Dados individuais | RF006 | Exigir sessão válida e autorização para consultar recursos do próprio cliente. |
| Usinas e créditos | RF008–RF011 | Listar usinas, consultar créditos por competência e calcular o total monetário do mesmo período. |
| Depoimentos | RF012, RF013 | Exibir somente depoimentos e campos públicos autorizados. |
| Ativação | RF015–RF019 | Retornar progresso coerente, etapas concluídas, etapa atual e etapas pendentes. |
| Preferências de atualização | RF020 | Registrar a preferência de receber atualizações da ativação pelos canais aprovados. |
| Faturas, pagamentos e repasses | RF021–RF024 | Consultar faturas, situação de pagamento, etapas de repasse à CEMIG e acessar o histórico externo com redirecionamento seguro. |
| Notificações | RF025 | Consultar notificações e atualizar o estado de leitura, caso o recurso permaneça no escopo; fora da Sprint 2. |

Os requisitos não funcionais orientam a implementação:

- **Segurança e privacidade (RNF001–RNF004):** proteger credenciais e dados pessoais, usar hash de senha com salt, validar autorização no backend e minimizar a exposição de dados conforme os requisitos de LGPD do projeto.
- **Consistência e atualidade (RNF005–RNF007):** manter cliente, competência, valores e etapas coerentes; informar ausência ou indisponibilidade de dados e sua referência temporal quando relevante.
- **Contrato e integração (RNF008–RNF010, RNF012):** manter contrato versionado, validar entradas e saídas, padronizar erros e preservar compatibilidade com os consumidores.
- **Desempenho e disponibilidade (RNF011):** definir metas mensuráveis antes da implementação; a documentação ainda não estabelece valores.

Políticas de primeiro acesso e sessão, fontes oficiais, divulgação pública dos créditos, fórmulas monetárias, canais de atualização e integração com o histórico externo ainda dependem de validação com a Bulbe. As decisões pendentes estão na [lista de endpoints](docs/requisitos/lista-endpoints.md#observações-e-decisões-pendentes).

## Equipe

**Squad Master** — responsabilidades da Sprint 2 conforme a divisão fornecida pela equipe.

| Nome | Matrícula | Frente principal |
| --- | --- | --- |
| Bernardo Alvim | 202508427141 | Estrutura base, dados de exemplo, testes e proteção de dados. |
| Felipe Nunes | 202501440487 | Usinas, créditos, total gerado e depoimentos. |
| Caio Freitas | 202503206091 | Login, logout e histórico externo de faturas. |
| Luca Bellei | 202501560229 | Cadastro, primeiro acesso e vínculo da conta. |
| Vinicius Bianchetti | 202503792106 | Ativação, faturas, repasse e preferências. |

## Tecnologias utilizadas

| Tecnologia | Uso no projeto |
| --- | --- |
| Python 3.11 ou superior | Linguagem do backend. |
| FastAPI | Framework da API e geração da documentação interativa. |
| Uvicorn | Servidor ASGI para execução local. |
| Pydantic 2 | Validação e serialização de dados. |
| pytest | Execução dos testes automatizados. |
| HTTPX e TestClient | Requisições à aplicação nos testes. |
| OpenAPI 3.1 e Swagger UI | Contrato da API e documentação das rotas implementadas. |
| PlantUML | Diagramas UML versionados em `.puml`, com imagens em SVG. |
| Git e GitHub | Versionamento, issues, pull requests e board do projeto. |

As dependências estão em [`requirements.txt`](requirements.txt). A Sprint 2 prevê armazenamento em memória. **SQLAlchemy está previsto para a Sprint 3**, mas ainda não foi adicionado às dependências; o banco de dados e sua configuração ainda não estão definidos neste repositório.

## Arquitetura

A API segue uma arquitetura em quatro camadas:

1. **Apresentação (`controllers/`):** recebe requisições HTTP, valida os dados de entrada e formata respostas e status codes.
2. **Serviço (`services/`):** aplica regras de negócio e orquestra o acesso aos repositórios.
3. **Domínio (`domain/`):** reúne entidades com comportamento próprio e erros de negócio.
4. **Persistência (`repositories/`):** define interfaces e implementações de acesso a dados, inicialmente em memória.

O fluxo é **Controller → Service → Repository**, com serviços e repositórios utilizando as entidades de domínio. Os serviços recebem repositórios por injeção de dependência. A função `create_app()` em [`src/main.py`](src/main.py) cria a aplicação, compõe os repositórios em memória e serviços e registra as rotas e os handlers de erro. Cada instância recebe seus próprios dados de exemplo. As dependências em `controllers/dependencias.py` obtêm os serviços da aplicação e permitem substituições com `app.dependency_overrides` nos testes.

As regras de negócio devem ficar nos serviços e nas entidades: validar o vínculo do cliente à sessão, somar créditos da mesma competência, calcular o progresso da ativação e filtrar depoimentos autorizados. Os critérios completos estão no [backlog da Sprint 2](docs/sprints/backlog-sprint-2.md).

### Diagramas do projeto

- **Casos de uso da API:** [PlantUML](docs/diagramas/casos-de-uso-api.puml) · [SVG](docs/diagramas/casos-de-uso-api.svg).
- **Sequência da autenticação:** [PlantUML](docs/diagramas/sequencia-autenticacao.puml) · [SVG](docs/diagramas/sequencia-autenticacao.svg).
- **Atividades da autenticação:** [PlantUML](docs/diagramas/atividade-autenticacao.puml) · [SVG](docs/diagramas/atividade-autenticacao.svg).
- **Classes do domínio:** [PlantUML](docs/diagramas/classes-dominio.puml) · [SVG](docs/diagramas/classes-dominio.svg).

## Estrutura de pastas

```text
src/
├── controllers/             Rotas públicas, dependências e modelos de resposta
├── services/                Regras e orquestração de usinas, créditos e depoimentos
├── repositories/            Interfaces, implementações em memória e dados de exemplo
├── domain/                  Entidades, objetos de valor e erros de negócio
└── main.py                  Aplicação, registro de rotas e handlers de erro
tests/
├── conftest.py              Aplicação e TestClient novos a cada teste
├── controllers/             Testes HTTP dos seis endpoints públicos
├── domain/                  Testes das entidades e objetos de valor
├── repositories/            Testes dos repositórios em memória
├── services/                Testes dos serviços, incluindo mocks
└── test_base.py             Testes da base da API e dos erros
docs/
├── api/                     Contrato OpenAPI e orientação de consulta
├── diagramas/               Diagramas UML em PlantUML e SVG
├── requisitos/              Requisitos técnicos e lista de endpoints
└── sprints/                 Backlog, critérios de aceite e plano da Sprint 2
requirements.txt             Dependências da aplicação e dos testes
pytest.ini                   Configuração do pytest
```

## Como executar o projeto

Requer Python 3.11 ou superior. Execute os comandos a partir da raiz do repositório.

1. Clonar o repositório e entrar na pasta:

   ```bash
   git clone https://github.com/bernardoalvimibmec/Bulbe-Projeto-Backend.git
   cd Bulbe-Projeto-Backend
   ```

2. Criar um ambiente virtual:

   ```bash
   python -m venv .venv
   ```

3. Ativar o ambiente virtual:

   **Windows (PowerShell):**

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **Linux ou macOS:**

   ```bash
   source .venv/bin/activate
   ```

4. Instalar as dependências:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Iniciar o servidor:

   ```bash
   python -m uvicorn src.main:app --reload
   ```

A base atual funciona sem variáveis de ambiente, arquivo `.env` ou migrations. Essas configurações deverão ser documentadas quando a persistência e as integrações forem implementadas.

- **API e rota de status:** <http://localhost:8000/>.
- **Swagger UI:** <http://localhost:8000/docs>.
- **ReDoc:** <http://localhost:8000/redoc>.
- **Contrato gerado pela aplicação:** <http://localhost:8000/openapi.json>.

## Como rodar os testes

Com o ambiente virtual ativo e as dependências instaladas:

```bash
python -m pytest
```

Para executar somente os testes da base:

```bash
python -m pytest tests/test_base.py
```

A suíte verifica domínio, repositórios, serviços e os endpoints públicos, incluindo filtros, paginação, competências, valores monetários numéricos, ausência de dados, totais incompletos e privacidade dos depoimentos. Também cobre status, Swagger/OpenAPI, erros, validação de entrada, métodos não permitidos e propagação de `X-Request-ID`. Os testes HTTP usam uma aplicação nova por teste, com repositórios e dependências isolados. Os testes de autorização serão acrescentados junto da área do cliente.

Para executar somente os testes HTTP públicos:

```bash
python -m pytest tests/controllers -q
```

## Documentação da API

O [contrato completo](docs/api/openapi.yaml) define **21 operações em OpenAPI 3.1**, com parâmetros, schemas, respostas e status codes. Consulte também a [lista de endpoints e exemplos](docs/requisitos/lista-endpoints.md) e as [orientações da documentação da API](docs/api/README.md).

**Implementação atual:** `/docs` e `/openapi.json` mostram as operacoes entregues nesta branch, incluindo as etapas anteriores da sequencia da Sprint 2. Consulte o registro abaixo.

### Demonstração dos endpoints públicos (US06, US07, US08 e US11)

Com o servidor em execução, abra `/docs` ou consulte:

| Consulta | Caminho e resultado esperado com os dados de exemplo |
| --- | --- |
| Usinas ativas | `GET /v1/usinas` — duas usinas ativas, `page=1`, `limit=20`, `total=2`. |
| Filtro e paginação | `GET /v1/usinas?status=inativa&page=1&limit=1` — `usina_04`. |
| Detalhes | `GET /v1/usinas/usina_01` — inclui `regiao` e `atualizado_em`. |
| Créditos por competência | `GET /v1/usinas/usina_01/creditos?competencia=2026-08` — R$ 43.980,75. |
| Total das ativas | `GET /v1/creditos-usinas/resumo?competencia=2026-08` — R$ 74.096,15, duas usinas. |
| Depoimentos autorizados | `GET /v1/depoimentos` — dois depoimentos, com paginação. |
| Detalhes do depoimento | `GET /v1/depoimentos/depoimento_01` — somente campos públicos. |

Todas essas consultas dispensam autenticação e usam dados fictícios. A publicação de créditos reais depende da aprovação da Bulbe. A competência é obrigatória nas duas consultas de créditos. Parâmetros inválidos retornam **400**; recurso inexistente, crédito ausente ou depoimento não autorizado retornam **404**; resumo com créditos faltantes retorna **503**, sem total parcial. `GET /v1/depoimentos/depoimento_03` demonstra a proteção de um depoimento não autorizado.

Os valores de `{ valor, moeda }` são números JSON, com cálculo monetário em `Decimal` no domínio. Os depoimentos omitem campos opcionais sem valor e nunca expõem `cliente_id` nem `publicacao_autorizada`. Uma listagem vazia mantém `total=0`; quando não há usinas no filtro, `atualizado_em` é `null`, sem inventar uma data. O mesmo vale para o resumo sem usinas no critério, com quantidade e total iguais a zero.

| Método | Rota | Descrição |
| --- | --- | --- |
| POST | `/v1/contas` | Cadastro/primeiro acesso e vínculo ao cliente Bulbe. |
| POST | `/v1/sessoes` | Autenticação do cliente. |
| DELETE | `/v1/sessoes/atual` | Encerramento da sessão atual. |
| GET | `/v1/clientes/{clienteId}` | Dados básicos do cliente vinculado. |
| GET | `/v1/usinas` | Listagem paginada de usinas, ativas por padrão. |
| GET | `/v1/usinas/{usinaId}` | Detalhes de uma usina. |
| GET | `/v1/usinas/{usinaId}/creditos` | Créditos monetários da usina por competência. |
| GET | `/v1/creditos-usinas/resumo` | Total monetário dos créditos no período. |
| GET | `/v1/depoimentos` | Listagem de depoimentos autorizados. |
| GET | `/v1/depoimentos/{depoimentoId}` | Detalhes de um depoimento público autorizado. |
| GET | `/v1/clientes/{clienteId}/ativacao` | Progresso consolidado da ativação. |
| GET | `/v1/clientes/{clienteId}/ativacao/etapas` | Etapas concluídas, atual e pendentes. |
| PUT | `/v1/clientes/{clienteId}/preferencias-notificacao/ativacao` | Preferência de atualizações da ativação. |
| GET | `/v1/clientes/{clienteId}/faturas` | Listagem de faturas do cliente. |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}` | Detalhes de uma fatura. |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}/pagamento` | Situação do pagamento da fatura. |
| GET | `/v1/clientes/{clienteId}/faturas/{faturaId}/repasse` | Etapas do repasse à CEMIG. |
| GET | `/v1/clientes/{clienteId}/historico-faturas-externo` | Redirecionamento seguro para o histórico externo. |
| GET | `/v1/clientes/{clienteId}/notificacoes` | Listagem de notificações; fora da Sprint 2. |
| GET | `/v1/clientes/{clienteId}/notificacoes/{notificacaoId}` | Detalhes de uma notificação; fora da Sprint 2. |
| PATCH | `/v1/clientes/{clienteId}/notificacoes/{notificacaoId}` | Atualização do estado de leitura; fora da Sprint 2. |

As rotas de dados individuais exigem sessão válida e vínculo entre a conta e o `clienteId` informado. O contrato prevê `401` para ausência de autenticação e `403` para acesso aos recursos de outro cliente. A divulgação pública dos créditos por usina e dos totais depende de aprovação da Bulbe.

Os handlers existentes padronizam erros de negócio, validação e erros HTTP neste formato:

```json
{
  "codigo": "RECURSO_NAO_ENCONTRADO",
  "mensagem": "O recurso solicitado nao foi encontrado.",
  "detalhes": [],
  "request_id": "req_01"
}
```

Datas seguem ISO 8601, datas com hora incluem fuso horário e valores monetários usam o objeto `{ valor, moeda }`. Consultas de créditos usam competência `AAAA-MM`; listagens paginadas usam `page` e `limit`.

## Banco de dados

Na Sprint 2, os repositórios serão implementados **em memória**, com dados de exemplo para a demonstração. Esses dados não representam informações oficiais e não serão persistidos entre execuções.

O [diagrama de classes do domínio](docs/diagramas/classes-dominio.svg) modela contas, sessões, clientes, usinas, créditos, depoimentos, ativação, faturas, pagamentos, repasses, preferências e notificações. Ele orienta a modelagem, mas ainda não é um modelo físico do banco.

A persistência com SQLAlchemy está prevista para a Sprint 3. Ainda não há modelo lógico/físico, dicionário de dados ou migrations implementados e versionados; a escolha do banco e a configuração de conexão serão documentadas nessa etapa.

## Sprints e backlog

- **Board do projeto:** [Backend Sprint 1 — GitHub Projects](https://github.com/users/bernardoalvimibmec/projects/3/views/1).
- **Issues:** [backlog no GitHub](https://github.com/bernardoalvimibmec/Bulbe-Projeto-Backend/issues).
- **Sprint 1:** elicitação dos requisitos, definição do contrato da API e modelagem UML.
- **Sprint 2:** de **07/10/2026 a 21/10/2026**, com **Review em 26/10/2026**. Objetivo: API funcionando de ponta a ponta com dados em memória, quatro camadas, regras de negócio e testes passando.
- **Planejamento detalhado:** [backlog da Sprint 2](docs/sprints/backlog-sprint-2.md), com prioridades, dependências, critérios de aceite e definição de pronto.

### Divisão de trabalho da Sprint 2

| Integrante | Itens | Pontos |
| --- | --- | --- |
| Bernardo Alvim | TEC-01, TEC-02, TEC-03, US04 | 13 |
| Felipe Nunes | US06, US07, US08, US11 | 14 |
| Caio Freitas | US01, US02, US14 | 12 |
| Luca Bellei | US03, US05 | 13 |
| Vinicius Bianchetti | US09, US10, US13, US12 | 16 |
| **Total da divisão informada** | **3 itens técnicos e 14 histórias de usuário** | **68** |

A tabela registra a divisão enviada pela equipe, incluindo **US12** na carga de Vinicius. O backlog detalhado ainda apresenta US12 como item de folga: são **65 pontos de compromisso base + 3 pontos de US12**. **US15** permanece fora da Sprint 2.

As principais dependências são a estrutura técnica (TEC-01), a autenticação (US01) e a autorização por vínculo (US04). Usinas, créditos e depoimentos podem ser desenvolvidos em paralelo, utilizando os dados de exemplo.

### Critérios de entrega

Cada item deve seguir o contrato, aparecer na documentação da API quando aplicável, ter testes passando e ser integrado à `main` por pull request revisado por um colega. O responsável deve manter o card e a estimativa atualizados no board. A [definição de pronto completa](docs/sprints/backlog-sprint-2.md#definição-de-pronto) está no backlog.

## Convenção de commits e branches

- **Branches:** `main` como base estável; branches de trabalho por funcionalidade, como `feature/nome-da-funcionalidade`, e por documentação, como `docs/readme`.
- **Commits:** padrão Conventional Commits, com prefixos `feat:`, `fix:`, `docs:`, `test:`, `refactor:` e `chore:`.
- **Pull requests:** revisados por pelo menos um integrante do grupo antes do merge.
- **Fluxo:** escolher um card e movê-lo para “Em andamento”, criar a branch a partir da `main`, implementar e testar, abrir o pull request, obter revisão e mover o card para “Concluído” após o merge.

## Extensão universitária

O projeto se conecta ao eixo de **sustentabilidade e educação ambiental** ao tornar mais acessíveis as informações sobre usinas e créditos de energia, além de dar transparência à jornada do cliente na Bulbe. A consulta de dados de geração e de ativação pode apoiar a compreensão dos serviços de energia e de seus benefícios pelos usuários.

O registro formal da atividade de extensão, das ações realizadas e de seus resultados deverá ser complementado na Aula 32, conforme a estrutura acadêmica do projeto.

## Contexto acadêmico

Projeto desenvolvido para a disciplina **Projeto Ciência de Dados II**, no **Ibmec**, no **2º semestre de 2026**, sob orientação do professor **Cristiano de Macedo Neto, M.Sc.** Dá continuidade ao frontend entregue em Projeto Ciência de Dados I e utiliza a demanda da Bulbe Energia como contexto de aplicação.

## Entregas adicionais da Sprint 2

1. Cadastro elegivel com vinculo confirmado, hash bcrypt e unicidade atomica.
2. Login JWT, sessao revogavel, expiracao e limite de tentativas.
3. Dados do cliente e autorizacao reutilizavel, com 401 e 403.
4. Ativacao e etapas ordenadas com progresso calculado e acesso protegido.
5. Faturas, pagamentos e etapas de repasse com verificacao de propriedade.
6. Historico externo autenticado, HTTPS e host aprovado, sem destino inventado.
7. US12 opcional: preferencias idempotentes e canal email validado.
8. Contrato, jornada integrada, roteiro da review e CI Linux Python 3.11/3.14.

Contas demonstrativas: `cliente01@exemplo.com` e `cliente02@exemplo.com`, senha ficticia `Bulbe2026!`. Primeiro acesso de `cliente03@exemplo.com`: identificador `BULBE-003`, codigo ficticio `345678`, senha definida no cadastro. O vinculo exige cliente ativo, email correspondente e codigo correto; a politica oficial ainda precisa de validacao com a Bulbe. Senhas usam bcrypt com salt e limite de 72 bytes UTF-8.

O login retorna `access_token` JWT HS256 com validade de 30 minutos e `token_type: bearer`. Use `Authorization: Bearer <access_token>` ou Authorize no Swagger. Logout revoga a sessao. O limite e de cinco tentativas falhas por cinco minutos. `BULBE_JWT_SECRET` aceita pelo menos 32 bytes; ausente, a chave e aleatoria por instancia. Reinicio descarta dados e sessoes; usar um unico processo nesta implementacao em memoria.

Historico externo: `BULBE_HISTORICO_URL` configura o destino HTTPS; `BULBE_HISTORICO_HOSTS_APROVADOS` informa hosts exatos separados por virgula. Sem endereco ha 404; destino inseguro retorna 503. Nenhum endereco oficial e inventado.

A entrega cobre as 17 operacoes obrigatorias e a preferencia US12. Consulte o [roteiro da review](docs/sprints/roteiro-review-sprint2.md). O CI executa pytest convencional em Linux com Python 3.11 e 3.14. A execucao HTTP neste ambiente Windows restrito foi validada com adaptador temporario em memoria, pois o socketpair do asyncio trava; confirmar pytest convencional na maquina da equipe/CI antes do merge.

A revisao automatizada nao substitui a revisao por um colega. Concluir no board somente depois dos testes convencionais, PR revisado e merge na main, conforme a Definicao de Pronto.
