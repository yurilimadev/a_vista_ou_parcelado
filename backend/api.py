# api.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from extrator import extrair_texto_html
from analisador import carregar_analisador, gerar_explicacao_detalhada
from custo_de_oportunidade import analisar_situacao_de_compra

app = FastAPI()

class AnaliseRequest(BaseModel):
    page_content: str

class AnaliseURLRequest(BaseModel):
    url: str

@app.post("/analisar-texto")
def analisar_endpoint(request: AnaliseRequest):
    """Recebe o texto de uma página e retorna a análise financeira."""
    try:
        dados_llm = carregar_analisador(request.page_content)
        if not dados_llm:
            raise HTTPException(status_code=400, detail="LLM não conseguiu extrair dados.")

        situacao = analisar_situacao_de_compra(dados_llm)
        return situacao
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@app.post("/analisar-url")
def analisar_url_endpoint(request: AnaliseURLRequest):
    """Recebe uma URL, faz o scraping e retorna a análise financeira."""
    try:
        texto_pagina = extrair_texto_html(request.url)
        if not texto_pagina:
            raise HTTPException(status_code=400, detail="Falha ao extrair conteúdo da URL.")

        dados_llm = carregar_analisador(texto_pagina)
        if not dados_llm:
            raise HTTPException(status_code=400, detail="LLM não conseguiu extrair dados do texto.")

        situacao = analisar_situacao_de_compra(dados_llm)
        return situacao
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

# Opcional: Endpoint para o parecer da IA
@app.post("/gerar-parecer")
def gerar_parecer_endpoint(situacao: dict):
    try:
        parecer = gerar_explicacao_detalhada(situacao)
        return {"parecer": parecer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar parecer da IA: {str(e)}")

