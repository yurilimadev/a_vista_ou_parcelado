from bs4 import BeautifulSoup
import time
from playwright.sync_api import sync_playwright
import streamlit as st

@st.cache_data(ttl=3360)
def extrair_texto_html(url) -> str:
    with sync_playwright() as p:

        navegador = p.chromium.launch(headless=True)

        contexto = p.chromium.launch_persistent_context(
            user_data_dir="./dados_navegador", # Salva os cookies aqui
            headless=False, # Mudar para False ajuda a burlar o bloqueio inicial!
            args=["--disable-blink-features=AutomationControlled"] # Oculta que é automatizado
        )
        page = contexto.new_page()

        page.goto(
            url = url,
            wait_until = "domcontentloaded"
        )
        page.evaluate(
            "window.scrollTo(0, document.body.scrollHeight / 2);"
        )
        time.sleep(4)
        html_bruto = page.content()

        navegador.close()

    soup = BeautifulSoup(html_bruto, 'html.parser')


    tags_para_remover = [
        "script", "style", "header", "footer", "nav", 
        "noscript", "svg", "iframe", "form", "button"
    ]

    for tag in soup(tags_para_remover):
        tag.decompose()

    texto_filtrado = soup.get_text(separator=' ')

    texto_para_analise = " ".join(texto_filtrado.split())

    return texto_para_analise
