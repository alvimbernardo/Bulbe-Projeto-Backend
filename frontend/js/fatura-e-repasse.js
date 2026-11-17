const ROTULOS_ETAPA = {
    concluida: { classe: 'concluido', bloco: 'conteudo-etapa', badge: 'bulbe-badge bulbe-badge-success', texto: 'concluído' },
    atual: { classe: 'atual', bloco: 'andamento', badge: 'bulbe-badge bulbe-badge-progress', texto: 'em andamento' },
    pendente: { classe: 'aguardando', bloco: 'pendente', badge: 'bulbe-badge bulbe-badge-pending', texto: 'pendente' },
};

const ROTULOS_STATUS_FATURA = { paga: 'Paga', aberta: 'Em aberto', vencida: 'Vencida', cancelada: 'Cancelada' };

function criar(tag, classe, texto) {
    const el = document.createElement(tag);
    if (classe) el.className = classe;
    if (texto !== undefined) el.textContent = texto;
    return el;
}

function itemDaTimeline(etapa) {
    const rotulo = ROTULOS_ETAPA[etapa.status] || ROTULOS_ETAPA.pendente;
    const item = criar('li', rotulo.classe);
    const bloco = criar('div', rotulo.bloco);
    const detalhes = [etapa.mensagem];
    if (etapa.ocorrido_em) detalhes.push(BulbeApi.formatar.dataCurta(etapa.ocorrido_em));
    if (etapa.previsao) detalhes.push(`Previsão: ${BulbeApi.formatar.dataCurta(etapa.previsao)}`);
    bloco.append(
        criar('h4', null, etapa.nome),
        criar('p', null, detalhes.filter(Boolean).join(' · ') || 'Aguardando a etapa anterior.'),
        criar('span', rotulo.badge, rotulo.texto),
    );
    item.append(criar('div', 'circulo'), bloco);
    return item;
}

function mostrarRepasse(repasse) {
    const lista = document.getElementById('timelineRepasse');
    lista.replaceChildren(...repasse.etapas.map(itemDaTimeline));
}

function mostrarSemRepasse(mensagem) {
    const lista = document.getElementById('timelineRepasse');
    lista.replaceChildren(itemDaTimeline({
        nome: 'Aguardando pagamento',
        status: 'atual',
        mensagem,
    }));
}

function mostrarCabecalho(fatura, pagamento) {
    const pago = pagamento && pagamento.status === 'confirmado';
    document.getElementById('valorFatura').textContent = BulbeApi.formatar.dinheiro(fatura.valor.valor);
    document.getElementById('detalheFatura').textContent =
        `Fatura Bulbe - ${BulbeApi.formatar.competencia(fatura.competencia)} - ${fatura.identificador_exibivel}`;
    document.getElementById('statusPagamento').textContent = pago ? 'Pagamento confirmado' : 'Aguardando pagamento';
    document.getElementById('iconePagamento').hidden = !pago;
    document.querySelector('.status-container').classList.toggle('pendente-pagamento', !pago);
    document.getElementById('formaPagamento').textContent = pago
        ? `Pago via ${pagamento.forma}`
        : `Vence em ${BulbeApi.formatar.data(fatura.vencimento)}`;
    document.querySelector('#cardPix img').hidden = !(pago && pagamento.forma === 'pix');
    document.getElementById('dataPagamento').textContent = pago
        ? BulbeApi.formatar.data(pagamento.pago_em)
        : BulbeApi.formatar.data(fatura.vencimento);
}

async function abrirFatura(faturaId) {
    document.querySelectorAll('.item-fatura').forEach((botao) => {
        botao.classList.toggle('selecionada', botao.dataset.faturaId === faturaId);
    });
    try {
        const fatura = await BulbeApi.doCliente(`/faturas/${faturaId}`);
        const pagamento = await BulbeApi.doCliente(`/faturas/${faturaId}/pagamento`).catch(() => null);
        mostrarCabecalho(fatura, pagamento);
        try {
            mostrarRepasse(await BulbeApi.doCliente(`/faturas/${faturaId}/repasse`));
        } catch (erro) {
            mostrarSemRepasse('O repasse à CEMIG começa assim que o pagamento desta fatura for confirmado.');
        }
    } catch (erro) {
        document.getElementById('statusPagamento').textContent = erro.message;
    }
}

function itemDaLista(fatura) {
    const botao = criar('button', 'item-fatura');
    botao.type = 'button';
    botao.dataset.faturaId = fatura.id;
    const textos = criar('div');
    textos.append(
        criar('strong', null, BulbeApi.formatar.competencia(fatura.competencia)),
        criar('small', null, `${fatura.identificador_exibivel} · ${ROTULOS_STATUS_FATURA[fatura.status] || fatura.status}`),
    );
    botao.append(textos, criar('span', 'valor-item', BulbeApi.formatar.dinheiro(fatura.valor.valor)));
    botao.addEventListener('click', () => abrirFatura(fatura.id));
    return botao;
}

document.addEventListener('DOMContentLoaded', async () => {
    const botaoVoltar = document.querySelector('.voltar');
    if (botaoVoltar) {
        botaoVoltar.addEventListener('click', () => window.history.back());
    }

    if (!BulbeApi.exigirLogin()) return;

    const secaoLista = document.getElementById('listaFaturas');
    const textoHistorico = document.getElementById('historicoTexto');
    document.querySelector('.historico').addEventListener('click', () => {
        secaoLista.hidden = !secaoLista.hidden;
        textoHistorico.textContent = secaoLista.hidden ? 'Ver histórico de faturas' : 'Esconder histórico';
    });

    try {
        const faturas = (await BulbeApi.doCliente('/faturas')).data;
        if (faturas.length === 0) {
            document.getElementById('statusPagamento').textContent = 'Você ainda não tem faturas.';
            return;
        }
        document.getElementById('listaFaturasItens').replaceChildren(...faturas.map(itemDaLista));
        const inicial = faturas.find((fatura) => fatura.status === 'paga') || faturas[0];
        await abrirFatura(inicial.id);
    } catch (erro) {
        document.getElementById('statusPagamento').textContent = erro.message;
        if (erro.status === 401) BulbeApi.exigirLogin();
    }
});
