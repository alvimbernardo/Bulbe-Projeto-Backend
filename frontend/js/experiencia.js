const navItems = document.querySelectorAll('.bottom-nav .nav-item');

navItems.forEach(item => {
    item.addEventListener('click', () => {
        // Remove a classe active de todos os itens da navegação
        navItems.forEach(nav => nav.classList.remove('active'));
        
        // Adiciona a classe active no item clicado
        item.classList.add('active');
        
        const nomeAba = item.querySelector('span').textContent;
        console.log(`Mudando para a tela: ${nomeAba}`);
    });
});

function iniciais(nome) {
    return nome.split(' ').filter((parte) => parte.length > 2).slice(0, 2).map((parte) => parte[0].toUpperCase()).join('');
}

function elemento(tag, classe, texto) {
    const el = document.createElement(tag);
    if (classe) el.className = classe;
    if (texto !== undefined) el.textContent = texto;
    return el;
}

function metrica(valor, rotulo) {
    const item = elemento('div', 'metric-item');
    item.append(elemento('div', 'metric-value', valor), elemento('div', 'metric-label', rotulo));
    return item;
}

function criarCardDeDepoimento(depoimento, indice) {
    const card = elemento('div', 'card');

    const cabecalho = elemento('div', 'card-header');
    const usuario = elemento('div', 'user-info');
    const detalhes = elemento('div', 'user-details');
    detalhes.append(
        elemento('h3', null, depoimento.nome_publico),
        elemento('p', null, depoimento.localidade),
        elemento('div', 'stars', '★'.repeat(depoimento.avaliacao) + '☆'.repeat(5 - depoimento.avaliacao)),
    );
    usuario.append(elemento('div', `avatar cor-${indice % 2}`, iniciais(depoimento.nome_publico)), detalhes);

    const economia = elemento('div', 'savings');
    economia.append(
        elemento('span', 'savings-amount', `-R$${Math.round(depoimento.economia_mensal.valor)}`),
        elemento('span', 'savings-period', '/mês'),
    );
    cabecalho.append(usuario, economia);

    const metricas = elemento('div', 'metrics');
    metricas.append(
        metrica(String(depoimento.dias_para_ativacao), 'dias p/ ativar'),
        metrica(`${Number(depoimento.percentual_desconto)}%`, 'de desconto'),
        metrica(String(depoimento.tempo_conta_ativa_meses), 'meses ativa'),
    );

    const texto = elemento('div', 'testimonial');
    texto.append(elemento('p', null, `"${depoimento.texto}"`));

    card.append(cabecalho, metricas, texto);
    return card;
}

document.addEventListener('DOMContentLoaded', async () => {
    const container = document.getElementById('depoimentosCards');
    try {
        const resposta = await BulbeApi.requisitar('GET', '/v1/depoimentos');
        container.replaceChildren(...resposta.data.map(criarCardDeDepoimento));
    } catch (erro) {
        const aviso = elemento('p', 'api-aviso erro', erro.message);
        container.replaceChildren(aviso);
    }
});
