# Review da Sprint 3 — roteiro e limites da demonstração

## Entrega implementada

As 18 operações da Sprint 2 agora persistem em banco relacional: 13 tabelas criadas por duas migrations do Alembic (`0001` e `0002`), repositórios SQL com a mesma interface dos repositórios em memória, seed de demonstração e testes de integração com banco de teste. Services, Controllers e Domínio não mudaram. Detalhe dos itens em [`backlog-sprint-3.md`](backlog-sprint-3.md) e modelo em [`modelo-banco.svg`](../diagramas/modelo-banco.svg).

## Preparação, antes da aula

Na raiz do projeto, com o ambiente virtual ativo:

```powershell
git pull
python -m pip install -r requirements.txt
Remove-Item bulbe.db -ErrorAction SilentlyContinue
alembic upgrade head
alembic current
python -m src.db.seed
$env:BULBE_JWT_SECRET = "chave-da-demonstracao-com-mais-de-32-bytes"
python -m uvicorn src.main:app --reload
```

- `alembic upgrade head` deve mostrar `0001` e `0002`; `alembic current` deve mostrar `0002 (head)`.
- O seed deve mostrar `4 usinas, 6 creditos_usinas, 3 depoimentos, 4 clientes, 2 contas, 2 ativacoes, 3 faturas, 3 pagamentos, 1 repasses`.
- `BULBE_JWT_SECRET` fixa a chave dos tokens, para o passo 6 funcionar depois de reiniciar a API. Use o mesmo terminal para subir a API todas as vezes.
- Para mostrar as tabelas, instale no VS Code uma extensão de visualização de SQLite (por exemplo, SQLite Viewer) e abra o `bulbe.db`.

## Sequência da demonstração

1. **Modelo do banco.** Abrir `docs/diagramas/modelo-banco.svg`: 13 tabelas, chaves primárias e estrangeiras (`creditos_usinas` → `usinas`; `contas`, `faturas`, `ativacoes` → `clientes`; `pagamentos`, `repasses` → `faturas`).
2. **Migrations no Git.** Mostrar `migrations/versions/` e o `.gitignore` com `*.db`. O schema nasce da migration, nunca do startup da API.
3. **Dados no banco.** Abrir o `bulbe.db` na extensão e mostrar as linhas de `usinas` e `faturas`.
4. **API lendo do banco.** No Swagger (`http://localhost:8000/docs`): `GET /v1/usinas` e `GET /v1/creditos-usinas/resumo?competencia=2026-08` = R$ 74.096,15.
5. **Gravar e reiniciar.** `POST /v1/contas` com `email` cliente03@exemplo.com, `senha` Senha12345, `identificador_cliente` BULBE-003 e `codigo_verificacao` 345678: resposta 201. Parar a API com Ctrl+C e subir de novo. Repetir o mesmo cadastro: 409, porque a conta continua no banco. Fazer login com a conta nova em `POST /v1/sessoes`: 201.
6. **Logout que sobrevive ao reinício.** Login como cliente01@exemplo.com / Bulbe2026!, copiar o `access_token`, usar no Authorize. `GET /v1/clientes/cliente_01`: 200. `DELETE /v1/sessoes/atual`: 204. Reiniciar a API e repetir o GET com o mesmo token: 401, porque a sessão revogada está gravada.
7. **Testes.** Parar a API e rodar `python -m pytest -q`: 433 passed. Mostrar `tests/integracao/`: banco SQLite temporário por teste, testes das chaves estrangeiras, da persistência após reinício e das migrations.
8. **Esquecer o commit, de propósito.** Em `src/repositories/conta_repository.py`, no método `salvar`, trocar `sessao.commit()` por `sessao.flush()` e rodar `python -m pytest -q`: 1 failed, 432 passed. Só o teste de integração `test_conta_criada_continua_existindo_depois_do_reinicio` pega o erro; os testes unitários usam repositórios em memória e continuam verdes. Desfazer a troca e rodar de novo: 433 passed.

## Perguntas prováveis

- **Por que Services e Controllers não mudaram?** Cada repositório é uma interface com duas implementações, em memória e SQL. Só o `src/main.py` escolhe qual usar.
- **Como o banco impede conta duplicada?** `contas.cliente_id` e `contas.email` são únicos no próprio banco. Mesmo dois cadastros simultâneos resultam em um 201 e um 409.
- **Por que o histórico externo não virou tabela?** O destino aprovado é configuração (`BULBE_HISTORICO_URL`), não dado de cliente.
- **Como trocar para PostgreSQL?** Instalar `psycopg[binary]`, definir `BULBE_DATABASE_URL=postgresql+psycopg://usuario:senha@localhost:5432/bulbe` e rodar `alembic upgrade head`. O código não muda.
- **Os testes apagam o banco de desenvolvimento?** Não. Os testes de integração usam um SQLite temporário em cada teste, e os unitários usam os repositórios em memória.

## Limites

- Os dados continuam fictícios; ainda não há integração com fontes corporativas reais da Bulbe nem com a CEMIG.
- SQLite no desenvolvimento; PostgreSQL depende de confirmação do professor (item S3-10 do backlog).
- Sem `BULBE_JWT_SECRET`, cada inicialização gera uma chave nova e os tokens anteriores deixam de valer.
- O limite de tentativas de login continua em memória, por processo.
