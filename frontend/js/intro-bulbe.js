// CONTROLE DA SIDEBAR (MANTIDO DO SEU CÓDIGO)
const menuBtn = document.getElementById('menuBtn');
const closeBtn = document.getElementById('closeBtn');
const sidebar = document.getElementById('sidebar');

menuBtn.addEventListener('click', () => {
    sidebar.style.width = '250px';
});

closeBtn.addEventListener('click', () => {
    sidebar.style.width = '0';
});

// CONTROLE DOS CARDS EXPANSÍVEIS (ACCORDION LOGIC)
const cardTriggers = document.querySelectorAll('.card-header-trigger');

cardTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
        const currentCard = trigger.closest('.card');
        const arrow = trigger.querySelector('.accordion-arrow');
        
        // Verifica se o card clicado já está aberto
        const isOpen = currentCard.classList.contains('active');
        
        // [OPCIONAL] Fecha todos os outros cards antes de abrir o novo
        document.querySelectorAll('.card').forEach(card => {
            card.classList.remove('active');
            const cardArrow = card.querySelector('.accordion-arrow');
            if (cardArrow) cardArrow.textContent = '▼';
        });

        // Se o card não estava aberto, abre ele e vira a seta para cima
        if (!isOpen) {
            currentCard.classList.add('active');
            arrow.textContent = '▲';
        }
    });
});

// CONTROLE DA NAVBAR INFERIOR (MANTIDO DO SEU CÓDIGO)
function setActiveNav(clickedButton) {
    const navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(item => {
        item.classList.remove('active');
    });
    clickedButton.classList.add('active');
}