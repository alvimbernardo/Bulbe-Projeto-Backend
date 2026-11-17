(function () {
  const API_PADRAO = "http://127.0.0.1:8000";
  const CHAVE_SESSAO = "bulbe.sessao";

  function enderecoDaApi() {
    if (window.location.pathname.startsWith("/app/")) {
      return window.location.origin;
    }
    return API_PADRAO;
  }

  class ErroDaApi extends Error {
    constructor(status, codigo, mensagem) {
      super(mensagem);
      this.status = status;
      this.codigo = codigo;
    }
  }

  function lerSessao() {
    try {
      return JSON.parse(localStorage.getItem(CHAVE_SESSAO));
    } catch (erro) {
      return null;
    }
  }

  function salvarSessao(sessao) {
    try {
      localStorage.setItem(CHAVE_SESSAO, JSON.stringify(sessao));
    } catch (erro) {
      return;
    }
  }

  function limparSessao() {
    try {
      localStorage.removeItem(CHAVE_SESSAO);
    } catch (erro) {
      return;
    }
  }

  async function requisitar(metodo, caminho, opcoes = {}) {
    const cabecalhos = { Accept: "application/json" };
    const sessao = lerSessao();
    if (opcoes.autenticada && sessao) {
      cabecalhos.Authorization = `Bearer ${sessao.token}`;
    }
    if (opcoes.corpo !== undefined) {
      cabecalhos["Content-Type"] = "application/json";
    }

    let resposta;
    try {
      resposta = await fetch(enderecoDaApi() + caminho, {
        method: metodo,
        headers: cabecalhos,
        body: opcoes.corpo !== undefined ? JSON.stringify(opcoes.corpo) : undefined,
      });
    } catch (erro) {
      throw new ErroDaApi(0, "API_FORA_DO_AR", "Não foi possível falar com a API. Ela está rodando?");
    }

    if (resposta.status === 204) {
      return null;
    }

    const dados = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      if (resposta.status === 401 && opcoes.autenticada) {
        limparSessao();
      }
      throw new ErroDaApi(resposta.status, dados.codigo || "ERRO", dados.mensagem || "Erro inesperado.");
    }
    return dados;
  }

  async function entrar(email, senha) {
    const dados = await requisitar("POST", "/v1/sessoes", { corpo: { email, senha } });
    salvarSessao({ token: dados.access_token, clienteId: dados.cliente_id, email });
    const cliente = await requisitar("GET", `/v1/clientes/${dados.cliente_id}`, { autenticada: true });
    salvarSessao({ token: dados.access_token, clienteId: dados.cliente_id, email, nome: cliente.nome_exibicao });
    return lerSessao();
  }

  async function sair() {
    try {
      await requisitar("DELETE", "/v1/sessoes/atual", { autenticada: true });
    } finally {
      limparSessao();
    }
  }

  function exigirLogin() {
    const sessao = lerSessao();
    if (!sessao) {
      const destino = window.location.pathname.split("/").pop();
      window.location.href = `login.html?voltar=${encodeURIComponent(destino)}`;
      return null;
    }
    return sessao;
  }

  function doCliente(caminho) {
    const sessao = lerSessao();
    return requisitar("GET", `/v1/clientes/${sessao.clienteId}${caminho}`, { autenticada: true });
  }

  const MESES = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
    "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"];
  const MESES_CURTOS = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"];

  const formatar = {
    dinheiro(valor) {
      return Number(valor).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    },
    competencia(texto) {
      const [ano, mes] = texto.split("-").map(Number);
      return `${MESES[mes - 1]} ${ano}`;
    },
    data(texto) {
      const [ano, mes, dia] = texto.slice(0, 10).split("-");
      return `${dia}/${mes}/${ano}`;
    },
    dataCurta(texto) {
      const [ano, mes, dia] = texto.slice(0, 10).split("-").map(Number);
      const hora = texto.length > 10 ? ` - ${texto.slice(11, 16)}` : "";
      return `${String(dia).padStart(2, "0")} ${MESES_CURTOS[mes - 1]} ${ano}${hora}`;
    },
  };

  window.BulbeApi = {
    ErroDaApi,
    requisitar,
    entrar,
    sair,
    exigirLogin,
    doCliente,
    sessao: lerSessao,
    formatar,
  };
})();
