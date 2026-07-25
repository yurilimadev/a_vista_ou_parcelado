// popup.js

// 1. Registrar listener PRIMEIRO (antes de injetar content.js)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "PAGE_CONTENT") {
    document.getElementById('status').innerText = '🔍 Analisando dados...';
    document.getElementById('status').className = 'loading';

    fetch('http://localhost:8000/analisar-texto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_content: request.content })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`Erro: ${response.statusText}`);
      }
      return response.json();
    })
    .then(data => {
      const situacao = data.situacao;
      const parecer = data.parecer;

      // Mostrar decisão
      document.getElementById('status').innerText = '✅ Análise Concluída!';
      document.getElementById('status').className = 'sucesso';
      
      const decisaoEl = document.getElementById('decisao');
      decisaoEl.innerText = `Decisão: Pagar ${situacao.melhor_opcao}`;
      decisaoEl.classList.remove('hidden');

      // Mostrar parecer
      if (parecer) {
        const parecerEl = document.getElementById('parecer');
        parecerEl.innerText = parecer;
        parecerEl.classList.remove('hidden');
      }
    })
    .catch(error => {
      document.getElementById('status').innerText = '❌ Erro na análise';
      document.getElementById('status').className = 'erro';
      document.getElementById('decisao').innerText = error.message;
      document.getElementById('decisao').classList.remove('hidden');
      document.getElementById('decisao').className = 'erro';
    });
  }
});

// 2. Depois de registrado o listener, injetar content.js
document.addEventListener('DOMContentLoaded', function() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      files: ['content.js']
    });
  });
});