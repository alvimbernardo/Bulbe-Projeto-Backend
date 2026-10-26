# Review da Sprint 2 — roteiro e limites da demonstracao

## Entrega implementada

As 17 operacoes obrigatorias e a preferencia de ativacao (US12) estao implementadas nas quatro camadas. US15, banco de dados, SQLAlchemy e migrations continuam fora desta entrega.

## Execucao

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn src.main:app --reload
```

Abra `http://localhost:8000/docs`. Os dados sao ficticios e todos os repositorios sao recriados ao reiniciar a aplicacao.

## Contas demonstrativas

| Cliente | Email | Senha de exemplo | Situacao |
| --- | --- | --- | --- |
| cliente_01 | cliente01@exemplo.com | Bulbe2026! | Ativacao em andamento, fatura paga e fatura aberta |
| cliente_02 | cliente02@exemplo.com | Bulbe2026! | Ativacao concluida, fatura propria |
| cliente_03 | cliente03@exemplo.com | A definir no primeiro acesso | Elegivel, sem conta no inicio |

Para cadastrar cliente_03, use `identificador_cliente: BULBE-003` e `codigo_verificacao: 345678`, com email acima e senha de 8 a 72 bytes UTF-8. A politica provisoria exige cliente ativo, email correspondente e codigo correto. As chaves e o processo oficial de verificacao ainda precisam ser validados com a Bulbe. Cadastro duplicado retorna 409; vinculo nao confirmado retorna 422.

## Sequencia da demonstracao

1. Consultar `GET /v1/usinas`, filtrar por status e paginar.
2. Consultar creditos de agosto de 2026: usina_01 = R$ 43.980,75; resumo das duas ativas = R$ 74.096,15.
3. Mostrar competencia ausente (400), mes sem credito individual (404) e resumo incompleto (503).
4. Listar depoimentos e comprovar que depoimento_03 retorna 404.
5. Criar conta de cliente_03 e repetir o cadastro para mostrar 409.
6. Fazer login como cliente_01 em `POST /v1/sessoes`; copiar `access_token` e usar o botao **Authorize** do Swagger.
7. Consultar `GET /v1/clientes/cliente_01`; alterar para cliente_02 e mostrar 403, inclusive para um id inexistente.
8. Consultar ativacao e etapas; conferir ordem e percentual calculado.
9. Listar faturas, consultar fatura_01, pagamento e repasse; mostrar fatura_02 aberta e pagamento ausente com 404.
10. Consultar uma fatura de cliente_02 pelo caminho de cliente_01 e mostrar 404, sem revelar o dono.
11. Salvar preferencias de ativacao com PUT, repetir para demonstrar idempotencia e testar canal nao suportado (422).
12. Mostrar historico sem configuracao (404), ou usar configuracao HTTPS aprovada para demonstrar 302.
13. Encerrar a sessao com DELETE e tentar reutilizar o mesmo token: 401.

## JWT e configuracao do historico

O login retorna JWT HS256 em `access_token`, `token_type: bearer` e os identificadores da sessao, conta e cliente. A validade padrao e de 30 minutos. Assinatura, algoritmo fixo, emissor, audiencia e claims temporais sao validados. A sessao tambem precisa continuar ativa no repositorio: logout revoga imediatamente e conta desativada perde acesso. Depois de cinco tentativas falhas, o identificador fica limitado pela janela de cinco minutos. Nao ha refresh token nesta sprint.

`BULBE_JWT_SECRET` pode fornecer uma chave de pelo menos 32 bytes. Se estiver ausente, cada instancia gera uma chave aleatoria temporaria. Tokens e sessoes nao sobrevivem ao reinicio. Esta implementacao em memoria destina-se a um unico processo; multiplos workers nao compartilham contas, bloqueios ou sessoes.

O historico externo nao possui endereco oficial inventado. Para demonstra-lo, configure **ambos**:

```powershell
$env:BULBE_HISTORICO_URL = 'https://historico.example/faturas'
$env:BULBE_HISTORICO_HOSTS_APROVADOS = 'historico.example'
```

O dominio `.example` serve somente de ilustracao; substitua pelo destino HTTPS aprovado. A API nao busca essa pagina: envia um redirecionamento 302. O host precisa coincidir exatamente com a lista configurada; HTTP, credenciais embutidas, portas diferentes de 443 e destinos fora da lista sao recusados. Sem destino ha 404; configuracao insegura retorna 503.

## Validacao e revisao

Os testes cobrem as regras, as interfaces em memoria, concorrencia de cadastro/login, JWT adulterado e expirado, revogacao, isolamento entre clientes, paginas vazias e privacidade das respostas. O workflow de CI executa `pytest` convencional em Linux com Python 3.11 e 3.14.

No ambiente restrito de implementacao, o TestClient padrao trava ao criar o socketpair interno do asyncio no Windows. A validacao HTTP local usou um adaptador temporario de event loop em memoria; esse adaptador nao integra a aplicacao nem os testes versionados. O CI e a execucao convencional na maquina da equipe precisam ser confirmados antes do merge.

Testes aprovados e revisao automatizada nao substituem a revisao por colega, o merge na main, a atualizacao do board e o ensaio ao vivo exigidos pela Definicao de Pronto.
