(function () {
  const VALORES_PROGRESSO = [0, 25, 50, 75, 100];
  const PASSO_PROGRESSO = 25;
  const PROGRESSO_INICIAL = 50;
  const ETAPAS_DO_STATUS = {
    0: "Cadastro",
    25: "Valida\u00e7\u00e3o",
    50: "Homologa\u00e7\u00e3o",
    75: "Homologa\u00e7\u00e3o",
    100: "Cr\u00e9ditos Ativos",
  };
  const ESTADOS_DAS_ETAPAS = {
    0: ["active", "pending", "pending", "pending"],
    25: ["completed", "active", "pending", "pending"],
    50: ["completed", "completed", "active", "pending"],
    75: ["completed", "completed", "active", "pending"],
    100: ["completed", "completed", "completed", "completed"],
  };
  const STATUS_EM_ANALISE = "Em an\u00e1lise";
  const STATUS_CONCLUIDO = "Conclu\u00eddo";
  const LINHA_TOPO = 11;
  const LINHA_ALTURA_TOTAL = 132;
  const LINHA_PASSO = 43;

  let progressoAtual = PROGRESSO_INICIAL;

  function limitarPercentual(percentual) {
    const numero = Number(percentual);

    if (!Number.isFinite(numero)) {
      return 0;
    }

    return Math.min(100, Math.max(0, Math.round(numero)));
  }

  function obterMarcoDoProgresso(percentual) {
    if (percentual >= 100) {
      return 100;
    }

    if (percentual >= 75) {
      return 75;
    }

    if (percentual >= 50) {
      return 50;
    }

    if (percentual >= 25) {
      return 25;
    }

    return 0;
  }

  function definirBadge(badge, estado) {
    if (!badge) {
      return;
    }

    badge.classList.remove(
      "step-pill-success",
      "step-pill-active",
      "step-pill-pending",
      "bulbe-badge-success",
      "bulbe-badge-progress",
      "bulbe-badge-pending"
    );

    if (estado === "completed") {
      badge.textContent = STATUS_CONCLUIDO;
      badge.classList.add("step-pill-success", "bulbe-badge-success");
      return;
    }

    if (estado === "active") {
      badge.textContent = "Em andamento";
      badge.classList.add("step-pill-active", "bulbe-badge-progress");
      return;
    }

    badge.textContent = "Pendente";
    badge.classList.add("step-pill-pending", "bulbe-badge-pending");
  }

  function limparMarcador(marker) {
    if (!marker) {
      return;
    }

    marker.textContent = "";
  }

  function atualizarLinhaDasEtapas(stepsList, etapasConcluidas, totalEtapas) {
    if (!stepsList) {
      return;
    }

    const linhaConcluida =
      etapasConcluidas >= totalEtapas
        ? LINHA_ALTURA_TOTAL
        : etapasConcluidas * LINHA_PASSO;
    const linhaPendente = Math.max(0, LINHA_ALTURA_TOTAL - linhaConcluida);

    stepsList.style.setProperty("--steps-line-completed", `${linhaConcluida}px`);
    stepsList.style.setProperty("--steps-line-pending-top", `${LINHA_TOPO + linhaConcluida}px`);
    stepsList.style.setProperty("--steps-line-pending-height", `${linhaPendente}px`);
  }

  function atualizarBotoesDoSimulador() {
    const botaoAnterior = document.querySelector(".progress-arrow-left");
    const botaoProximo = document.querySelector(".progress-arrow-right");

    if (botaoAnterior) {
      botaoAnterior.disabled = progressoAtual <= 0;
    }

    if (botaoProximo) {
      botaoProximo.disabled = progressoAtual >= 100;
    }
  }

  function atualizarProgressoAtivacao(percentual) {
    const percentualNormalizado = limitarPercentual(percentual);
    const statusPercent = document.querySelector(".status-percent");
    const progressFill = document.querySelector(".progress-fill");
    const progressRing = document.querySelector(".hero-progress-ring");
    const statusCurrentStep = document.querySelector(".status-current-step");
    const statusActivationItem = document.querySelector(".status-item-activation");
    const statusActivationState = document.querySelector(".status-activation-state");
    const stepsCard = document.querySelector(".steps-card");
    const stepsList = stepsCard ? stepsCard.querySelector(".steps-list") : null;
    const etapas = stepsCard ? Array.from(stepsCard.querySelectorAll(".step")) : [];
    const marcoProgresso = obterMarcoDoProgresso(percentualNormalizado);
    const estadosDasEtapas = ESTADOS_DAS_ETAPAS[marcoProgresso];
    const ativacaoConcluida = percentualNormalizado >= 100;
    const etapasConcluidas = estadosDasEtapas.filter((estado) => estado === "completed").length;

    progressoAtual = percentualNormalizado;

    if (statusPercent) {
      statusPercent.textContent = `${percentualNormalizado}%`;
    }

    if (progressFill) {
      progressFill.style.width = `${percentualNormalizado}%`;
    }

    if (progressRing) {
      const strokeDashoffset = 100 - percentualNormalizado;
      progressRing.style.strokeDashoffset = String(strokeDashoffset);
      progressRing.classList.toggle("progress-empty", percentualNormalizado <= 0);
    }

    if (statusCurrentStep) {
      statusCurrentStep.textContent = ETAPAS_DO_STATUS[marcoProgresso];
    }

    if (statusActivationItem) {
      statusActivationItem.classList.toggle("status-is-completed", ativacaoConcluida);
      statusActivationItem.classList.toggle("status-is-analysis", !ativacaoConcluida);
    }

    if (statusActivationState) {
      statusActivationState.textContent = ativacaoConcluida
        ? STATUS_CONCLUIDO
        : STATUS_EM_ANALISE;
    }

    etapas.forEach((etapa, index) => {
      const estado = estadosDasEtapas[index] || "pending";
      const marcador = etapa.querySelector(".step-marker");
      const badge = etapa.querySelector(".step-pill");

      etapa.classList.remove("step-completed", "step-active", "step-pending");
      etapa.classList.add(`step-${estado}`);
      limparMarcador(marcador);
      definirBadge(badge, estado);
    });

    atualizarLinhaDasEtapas(stepsList, etapasConcluidas, etapas.length);
    atualizarBotoesDoSimulador();

    return percentualNormalizado;
  }

  function setProgressoAtivacao(percentual) {
    return atualizarProgressoAtivacao(percentual);
  }

  function moverProgresso(direcao) {
    const indiceAtual = VALORES_PROGRESSO.includes(progressoAtual)
      ? VALORES_PROGRESSO.indexOf(progressoAtual)
      : Math.round(progressoAtual / PASSO_PROGRESSO);
    const proximoIndice = Math.min(
      VALORES_PROGRESSO.length - 1,
      Math.max(0, indiceAtual + direcao)
    );

    setProgressoAtivacao(VALORES_PROGRESSO[proximoIndice]);
  }

  function prepararSimulador() {
    const botaoAnterior = document.querySelector(".progress-arrow-left");
    const botaoProximo = document.querySelector(".progress-arrow-right");

    if (botaoAnterior) {
      botaoAnterior.addEventListener("click", () => moverProgresso(-1));
    }

    if (botaoProximo) {
      botaoProximo.addEventListener("click", () => moverProgresso(1));
    }

    setProgressoAtivacao(PROGRESSO_INICIAL);
  }

  function descreverEtapa(etapa) {
    if (etapa.status === "concluida" && etapa.concluida_em) {
      return `Concluída em ${BulbeApi.formatar.data(etapa.concluida_em)}.`;
    }
    if (etapa.previsao_conclusao) {
      return `Previsão: ${BulbeApi.formatar.data(etapa.previsao_conclusao)}.`;
    }
    return "Aguardando as etapas anteriores.";
  }

  function preencherEtapas(etapas) {
    const artigos = Array.from(document.querySelectorAll(".steps-card .step"));
    etapas.forEach((etapa, index) => {
      const artigo = artigos[index];
      if (!artigo) {
        return;
      }
      artigo.querySelector(".step-heading span").textContent = etapa.nome;
      artigo.querySelector(".step-body p").textContent = descreverEtapa(etapa);
    });
  }

  function mostrarErro(mensagem) {
    const texto = document.getElementById("ativacaoTexto");
    if (texto) {
      texto.textContent = mensagem;
    }
  }

  function mostrarAtivacaoNaoIniciada() {
    const simulador = document.querySelector(".progress-simulator");
    if (simulador) {
      simulador.hidden = true;
    }
    setProgressoAtivacao(25);
    document.getElementById("ativacaoTitulo").textContent = "Recebemos o seu cadastro";
    document.getElementById("ativacaoTexto").textContent =
      "Sua conta foi criada. A Bulbe vai iniciar a ativação junto à distribuidora e as etapas aparecerão aqui.";
    document.querySelectorAll(".steps-card .step-body p").forEach((paragrafo, index) => {
      paragrafo.textContent = index === 0 ? "Sua conta foi criada." : "Aguardando o início da ativação.";
    });
    const previsao = document.getElementById("ativacaoPrevisao");
    if (previsao) {
      previsao.textContent = "Avisaremos por aqui quando a ativação começar.";
    }
  }

  async function carregarAtivacao() {
    if (!window.BulbeApi || !BulbeApi.exigirLogin()) {
      return;
    }
    try {
      const [ativacao, etapas] = await Promise.all([
        BulbeApi.doCliente("/ativacao"),
        BulbeApi.doCliente("/ativacao/etapas"),
      ]);
      const simulador = document.querySelector(".progress-simulator");
      if (simulador) {
        simulador.hidden = true;
      }
      setProgressoAtivacao(ativacao.percentual);
      preencherEtapas(etapas.data);
      const atual = etapas.data.find((etapa) => etapa.status === "atual");
      const etapaAtual = document.querySelector(".status-current-step");
      if (atual && etapaAtual) {
        etapaAtual.textContent = atual.nome;
      }
      const previsao = document.getElementById("ativacaoPrevisao");
      if (ativacao.status === "concluida") {
        document.getElementById("ativacaoTitulo").textContent = "Sua economia já está ativa";
        document.getElementById("ativacaoTexto").textContent =
          `A ativação foi concluída e seus créditos já aparecem na fatura. ${BulbeApi.sessao().nome || ""}`.trim();
        if (previsao) {
          previsao.textContent = "Acompanhe seus pagamentos na aba Faturas.";
        }
      } else if (previsao && ativacao.previsao_conclusao) {
        previsao.textContent = `Previsão de conclusão: ${BulbeApi.formatar.data(ativacao.previsao_conclusao)}.`;
      }
    } catch (erro) {
      if (erro.status === 404) {
        mostrarAtivacaoNaoIniciada();
        return;
      }
      mostrarErro(erro.message);
      if (erro.status === 401) {
        BulbeApi.exigirLogin();
      }
    }
  }

  function prepararPreferencia() {
    const botao = document.getElementById("receberAtualizacoes");
    const texto = document.getElementById("receberAtualizacoesTexto");
    if (!botao || !texto || !window.BulbeApi) {
      return;
    }
    let habilitada = false;
    botao.addEventListener("click", async () => {
      const sessao = BulbeApi.exigirLogin();
      if (!sessao) {
        return;
      }
      botao.disabled = true;
      try {
        await BulbeApi.requisitar(
          "PUT",
          `/v1/clientes/${sessao.clienteId}/preferencias-notificacao/ativacao`,
          { autenticada: true, corpo: { habilitada: !habilitada, canais: ["email"] } }
        );
        habilitada = !habilitada;
        texto.textContent = habilitada
          ? "Atualizações por e-mail ativadas ✓"
          : "Receber atualizações";
      } catch (erro) {
        texto.textContent = erro.message;
      } finally {
        botao.disabled = false;
      }
    });
  }

  window.atualizarProgressoAtivacao = atualizarProgressoAtivacao;
  window.setProgressoAtivacao = setProgressoAtivacao;

  document.addEventListener("DOMContentLoaded", () => {
    prepararSimulador();
    prepararPreferencia();
    carregarAtivacao();
  });
})();
