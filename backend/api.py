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

class DadosManuaisRequest(BaseModel):
    preco_avista: float
    preco_total_parcelado: float
    numero_parcelas: int
    valor_parcela: float | None = None

def _gerar_resposta_completa(situacao: dict) -> dict:
    """Gera o parecer e retorna resposta completa com situacao + parecer."""
    try:
        parecer = gerar_explicacao_detalhada(situacao)
    except Exception as e:
        parecer = f"Não foi possível gerar o parecer: {e}"
    return {
        "situacao": situacao,
        "parecer": parecer
    }

@app.post("/analisar-texto")
def analisar_endpoint(request: AnaliseRequest):
    """Recebe o texto de uma página e retorna a análise completa (situacao + parecer)."""
    try:
        dados_llm = carregar_analisador(request.page_content)
        if not dados_llm:
            raise HTTPException(status_code=400, detail="LLM não conseguiu extrair dados.")

        situacao = analisar_situacao_de_compra(dados_llm)
        return _gerar_resposta_completa(situacao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@app.post("/analisar-url")
def analisar_url_endpoint(request: AnaliseURLRequest):
    """Recebe uma URL, faz o scraping e retorna a análise completa (situacao + parecer)."""
    try:
        texto_pagina = extrair_texto_html(request.url)
        if not texto_pagina:
            raise HTTPException(status_code=400, detail="Falha ao extrair conteúdo da URL.")

        dados_llm = carregar_analisador(texto_pagina)
        if not dados_llm:
            raise HTTPException(status_code=400, detail="LLM não conseguiu extrair dados do texto.")

        situacao = analisar_situacao_de_compra(dados_llm)
        return _gerar_resposta_completa(situacao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

@app.post("/analisar-dados-manuais")
def analisar_dados_manuais_endpoint(request: DadosManuaisRequest):
    """Recebe dados inseridos manualmente e retorna a análise completa (situacao + parecer)."""
    try:
        info_llm = {
            "preco_avista": request.preco_avista,
            "preco_total_parcelado": request.preco_total_parcelado,
            "numero_parcelas": request.numero_parcelas,
            "valor_parcela": request.valor_parcela if request.valor_parcela else request.preco_total_parcelado / request.numero_parcelas,
            "valor_completo": request.preco_total_parcelado
        }

        situacao = analisar_situacao_de_compra(info_llm)
        return _gerar_resposta_completa(situacao)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno no servidor: {str(e)}")

