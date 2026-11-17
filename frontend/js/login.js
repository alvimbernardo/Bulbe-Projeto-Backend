document.addEventListener('DOMContentLoaded', () => {
  const menuBtn = document.getElementById('menuBtn');
  const closeBtn = document.getElementById('closeBtn');
  const sidebar = document.getElementById('sidebar');
  const tabs = [document.getElementById('loginTab'), document.getElementById('registerTab')];
  const panels = [document.getElementById('loginPanel'), document.getElementById('registerPanel')];
  const feedback = document.getElementById('authFeedback');
  const authCard = document.getElementById('authCard');
  const sessionCard = document.getElementById('sessionCard');
  const destino = new URLSearchParams(window.location.search).get('voltar') || 'ativacao.html';

  function setSidebar(open) {
    sidebar.classList.toggle('open', open);
    sidebar.setAttribute('aria-hidden', String(!open));
  }

  function mostrarMensagem(texto, tipo) {
    feedback.textContent = texto;
    feedback.classList.remove('erro', 'sucesso');
    feedback.classList.toggle('visible', Boolean(texto));
    if (tipo) feedback.classList.add(tipo);
  }

  function mostrarSessao() {
    const sessao = BulbeApi.sessao();
    authCard.hidden = Boolean(sessao);
    sessionCard.hidden = !sessao;
    if (sessao) {
      document.getElementById('sessionName').textContent = sessao.nome || 'cliente';
      document.getElementById('sessionEmail').textContent = sessao.email;
    }
  }

  async function enviar(form, acao) {
    if (!form.reportValidity()) return;
    const botao = form.querySelector('button[type="submit"]');
    botao.disabled = true;
    mostrarMensagem('Conectando com a API...', null);
    try {
      await acao();
      mostrarMensagem('Tudo certo! Abrindo sua jornada...', 'sucesso');
      window.location.href = destino;
    } catch (erro) {
      mostrarMensagem(erro.message, 'erro');
    } finally {
      botao.disabled = false;
    }
  }

  menuBtn.addEventListener('click', () => setSidebar(true));
  closeBtn.addEventListener('click', () => setSidebar(false));

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => {
      tabs.forEach((item, itemIndex) => {
        const active = itemIndex === index;
        item.classList.toggle('active', active);
        item.setAttribute('aria-selected', String(active));
        panels[itemIndex].hidden = !active;
      });
      mostrarMensagem('', null);
    });
  });

  document.querySelectorAll('[data-password-target]').forEach((button) => {
    button.addEventListener('click', () => {
      const input = document.getElementById(button.dataset.passwordTarget);
      const showPassword = input.type === 'password';
      input.type = showPassword ? 'text' : 'password';
      button.textContent = showPassword ? 'Ocultar' : 'Mostrar';
      button.setAttribute('aria-label', showPassword ? 'Ocultar senha' : 'Mostrar senha');
    });
  });

  const loginForm = document.getElementById('loginForm');
  loginForm.addEventListener('submit', (event) => {
    event.preventDefault();
    enviar(loginForm, () => BulbeApi.entrar(
      document.getElementById('loginEmail').value.trim(),
      document.getElementById('loginPassword').value,
    ));
  });

  const registerForm = document.getElementById('registerForm');
  registerForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const email = document.getElementById('registerEmail').value.trim();
    const senha = document.getElementById('registerPassword').value;
    enviar(registerForm, async () => {
      await BulbeApi.requisitar('POST', '/v1/contas', {
        corpo: {
          email,
          senha,
          identificador_cliente: document.getElementById('registerIdentifier').value.trim(),
          codigo_verificacao: document.getElementById('registerCode').value.trim(),
        },
      });
      await BulbeApi.entrar(email, senha);
    });
  });

  document.getElementById('logoutButton').addEventListener('click', async () => {
    await BulbeApi.sair().catch(() => null);
    mostrarSessao();
    mostrarMensagem('Você saiu da sua conta.', 'sucesso');
  });

  mostrarSessao();
});
