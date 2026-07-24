// popup.js
document.addEventListener('DOMContentLoaded', function() {
  chrome.tabs.query({ active: true, currentWindow: true }, function(tabs) {
    chrome.scripting.executeScript({
      target: { tabId: tabs[0].id },
      files: ['content.js']
    });
  });
});

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === "PAGE_CONTENT") {
    document.getElementById('status').innerText = 'Analisando...';

    // Faz a chamada para a nossa API Python
    fetch('http://localhost:8000/analisar-texto', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ page_content: request.content })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Erro na API: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
      // Exibe o resultado no popup
      document.getElementById('status').innerText = 'Análise Concluída!';
      document.getElementById('resultado').innerText = `Decisão: Pagar ${data.melhor_opcao}`;
    })
    .catch(error => {
      document.getElementById('status').innerText = 'Erro!';
      document.getElementById('resultado').innerText = error.message;
    });
  }
});
