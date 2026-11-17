document.addEventListener('DOMContentLoaded', () => {
    // Seleção dos elementos
    const menuBtn = document.getElementById('menuBtn');
    const closeBtn = document.getElementById('closeBtn');
    const sidebar = document.getElementById('sidebar');

    const bellBtn = document.getElementById('bellBtn');
    const profileBtn = document.getElementById('profileBtn');

    const notificationsPanel = document.getElementById('notificationsPanel');
    const profilePanel = document.getElementById('profilePanel');

    // Função para limpar e fechar todos os menus ativos
    function fecharTudo() {
        if (sidebar) sidebar.style.width = '0';
        if (notificationsPanel) notificationsPanel.classList.remove('open');
        if (profilePanel) profilePanel.classList.remove('open');
    }

    // --- CONTROLE DA SIDEBAR ---
    if (menuBtn && sidebar) {
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Impede o documento de fechar o menu no mesmo clique
            fecharTudo();
            sidebar.style.width = '250px';
        });
    }

    if (closeBtn && sidebar) {
        closeBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            sidebar.style.width = '0';
        });
    }

    // --- CONTROLE DO SINO DE NOTIFICAÇÕES ---
    if (bellBtn && notificationsPanel) {
        bellBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const jaAberto = notificationsPanel.classList.contains('open');
            fecharTudo();
            if (!jaAberto) notificationsPanel.classList.add('open');
        });
    }

    // --- CONTROLE DO PERFIL ---
    if (profileBtn && profilePanel) {
        profileBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            const jaAberto = profilePanel.classList.contains('open');
            fecharTudo();
            if (!jaAberto) profilePanel.classList.add('open');
        });
    }

    // --- CLICOU FORA? FECHA TUDO ---
    document.addEventListener('click', () => {
        fecharTudo();
    });

    // Impede o fechamento se o usuário clicar dentro do próprio menu/popups
    [sidebar, notificationsPanel, profilePanel].forEach(painel => {
        if (painel) {
            painel.addEventListener('click', (e) => e.stopPropagation());
        }
    });
});
const COMPETENCIA_EXIBIDA = '2026-08';
const SITUACOES = { ativa: 'Ativa', em_manutencao: 'Em manutenção', inativa: 'Inativa' };

async function creditosDaUsina(usinaId) {
    try {
        const dados = await BulbeApi.requisitar('GET', `/v1/usinas/${usinaId}/creditos?competencia=${COMPETENCIA_EXIBIDA}`);
        return dados.creditos.valor;
    } catch (erro) {
        return null;
    }
}

function criarCardDeUsina(usina, credito, mostrarSituacao) {
    const card = document.createElement('div');
    card.className = 'card';

    const titulo = document.createElement('div');
    titulo.className = 'status';
    const ponto = document.createElement('span');
    ponto.className = `dot ${usina.status}`;
    titulo.append(ponto, usina.nome.replace('Usina Solar ', 'Usina '));

    const local = document.createElement('small');
    local.textContent = `${usina.cidade}, ${usina.estado}`;

    const valor = document.createElement('div');
    valor.className = 'price';
    valor.textContent = credito === null ? '—' : BulbeApi.formatar.dinheiro(credito);

    const legenda = document.createElement('span');
    legenda.className = 'credit';
    legenda.textContent = credito === null ? 'sem créditos no mês' : 'em crédito';

    card.append(titulo, local, valor, legenda);
    if (mostrarSituacao) {
        const situacao = document.createElement('span');
        situacao.className = 'situacao';
        situacao.textContent = SITUACOES[usina.status] || usina.status;
        card.append(situacao);
    }
    return card;
}

async function carregarUsinas(todas) {
    const container = document.getElementById('usinasCards');
    try {
        const consultas = todas
            ? ['ativa', 'em_manutencao', 'inativa'].map((status) => BulbeApi.requisitar('GET', `/v1/usinas?status=${status}`))
            : [BulbeApi.requisitar('GET', '/v1/usinas')];
        const usinas = (await Promise.all(consultas)).flatMap((pagina) => pagina.data);
        const creditos = await Promise.all(usinas.map((usina) => creditosDaUsina(usina.id)));
        container.replaceChildren(...usinas.map((usina, i) => criarCardDeUsina(usina, creditos[i], todas)));
        document.getElementById('usinasTitulo').textContent = todas ? `TODAS AS USINAS (${usinas.length})` : 'USINAS ATIVAS';
    } catch (erro) {
        const aviso = document.createElement('p');
        aviso.className = 'api-aviso erro';
        aviso.textContent = erro.message;
        container.replaceChildren(aviso);
    }
}

async function carregarResumo() {
    try {
        const resumo = await BulbeApi.requisitar('GET', `/v1/creditos-usinas/resumo?competencia=${COMPETENCIA_EXIBIDA}`);
        document.getElementById('totalCreditos').textContent = BulbeApi.formatar.dinheiro(resumo.total_creditos.valor);
        document.getElementById('totalCreditosLegenda').textContent =
            `Total gerado em ${BulbeApi.formatar.competencia(resumo.competencia).toLowerCase()} em créditos para clientes`;
    } catch (erro) {
        document.getElementById('totalCreditosLegenda').textContent = erro.message;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    let mostrandoTodas = false;
    const botao = document.getElementById('verTodasUsinas');
    botao.addEventListener('click', () => {
        mostrandoTodas = !mostrandoTodas;
        botao.textContent = mostrandoTodas ? 'Ver só as usinas ativas' : 'Ver todas as usinas';
        carregarUsinas(mostrandoTodas);
    });
    carregarUsinas(false);
    carregarResumo();
});
