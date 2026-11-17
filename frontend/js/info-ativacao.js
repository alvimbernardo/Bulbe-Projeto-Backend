// CONTROLE DOS CARDS EXPANSÍVEIS (ACCORDION) - LINHA DO TEMPO
const stepTriggers = document.querySelectorAll('.step-title-trigger');

stepTriggers.forEach(trigger => {
    trigger.addEventListener('click', () => {
        // Encontra a etapa inteira que foi clicada
        const currentStep = trigger.closest('.timeline-step');
        const arrow = trigger.querySelector('.accordion-arrow');
        
        // Verifica se a etapa clicada já está aberta
        const isOpen = currentStep.classList.contains('active');
        
        // Fecha TODAS as etapas antes de abrir a nova
        document.querySelectorAll('.timeline-step').forEach(step => {
            step.classList.remove('active');
            const stepArrow = step.querySelector('.accordion-arrow');
            if (stepArrow) stepArrow.textContent = '▼';
        });

        // Se não estava aberta, abre ela e vira a seta para cima
        if (!isOpen) {
            currentStep.classList.add('active');
            if (arrow) arrow.textContent = '▲';
        }
    });
});