// content.js
function getPageText() {
  // Remove tags que não interessam para a análise
  document.querySelectorAll('script, style, header, footer, nav, noscript, svg, iframe, form, button').forEach(el => el.remove());
  return document.body.innerText;
}

// Envia o texto limpo para o runtime da extensão
chrome.runtime.sendMessage({
  type: "PAGE_CONTENT",
  content: getPageText()
});
