from openai import OpenAI
import json
import os
from dotenv import load_dotenv
import streamlit as st
import time


load_dotenv()

client = OpenAI(
        base_url = 'https://openrouter.ai/api/v1',
        api_key = os.environ.get("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": "http://localhost:8501", # Necessário para o OpenRouter
            "X-Title": "A vista ou Parcelado"   # Necessário para o OpenRouter
        }
    )

@st.cache_data(ttl=3360)
def carregar_analisador(texto_para_analise) -> str:
    

    prompt_system = (
        """
        Você é um assistente especialista em extração de dados financeiros de e-commerces. 
        Sua tarefa é ler o texto fornecido e extrair as condições de pagamento.
        Você deve responder APENAS com um objeto JSON válido, sem nenhuma explicação antes ou depois. 
        O JSON deve conter exatamente as seguintes chaves:\n
        {\n
        'valor_completo': float ou null (preço do produto sem nenhum desconto),\n
        'preco_avista': float ou null (preço com desconto à vista/Pix),\n
        'preco_total_parcelado': float ou null (soma de todas as parcelas se houver juros, ou o preço cheio),\n
        'numero_parcelas': int ou null (quantidade máxima de parcelas),\n
        'valor_parcela': float ou null (valor de cada parcela individual)\n
        }
        """
    )

    tentativas_maximas = 3
    for tentativa in range(tentativas_maximas):
        try:
            response = client.chat.completions.create(
                model="qwen/qwen-2.5-72b-instruct",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": prompt_system},
                    {"role": "user", "content": f"Texto do e-commerce: {texto_para_analise}"}
                ],
                temperature=0.1, 
                timeout=10.0
            )
            break  # Se funcionou, sai do loop de tentativas
            
        except Exception as e:
            # Se o erro for de "muitos pedidos" (código 429) e ainda houver tentativas
            if "429" in str(e) and tentativa < tentativas_maximas - 1:
                time.sleep(5)  # Espera 5 segundos como no caixa do supermercado
                continue
            
            print(f"Deu Ruim: {e}")
            return None  # Retorna vazio para o sistema não travar

    # O restante do seu código de limpeza continua aqui:
    conteudo_resposta = response.choices[0].message.content.strip()

    if conteudo_resposta.startswith("```"):
        conteudo_resposta = conteudo_resposta.replace("```json", "").replace("```", "").strip()

    resultado_json = json.loads(conteudo_resposta)
    print(resultado_json)
    return resultado_json
    

# analisar.py (ou o arquivo onde está o seu objeto 'client' da OpenAI)
@st.cache_data(ttl=3360)
def gerar_explicacao_detalhada(situacao_de_compra: dict) -> str:
    """
    Envia os resultados matemáticos mastigados para a LLM gerar uma
    análise humanizada, concisa e focada em finanças comportamentais.
    """
    
    # Extraímos apenas as variáveis críticas para economizar tokens
    melhor_opcao = situacao_de_compra["melhor_opcao"]
    p_regular = situacao_de_compra["preco_regular"]
    p_vista = situacao_de_compra["preco_avista"]
    vp_parcelas = situacao_de_compra["valor_presente_parcelas"]
    tir_m = situacao_de_compra["tir_mensal"]
    cdi_m = situacao_de_compra["cdi_mensal"]
    lucro_final = situacao_de_compra["lucro_prejuizo_final"]

    prompt_sistema = (
            "Você é um consultor financeiro especializado em finanças pessoais. "
            "Explique ao cliente por que a recomendação é a melhor decisão financeira. "
            "Use linguagem simples, tom amigável e direto. "
            "Máximo: 3 parágrafos curtos ou bullets.\n\n"

            "REGRAS DE FORMATAÇÃO MARKDOWN (Streamlit):\n"
            "FAÇA:\n"
            "   - Negrito: **texto** (dois asteriscos ANTES e DEPOIS)\n"
            "   - Moeda: Use SEMPRE barra invertida antes do cifrão para evitar bugs de renderização: R\\$ (Exemplo: R\\$ 50,00)\n"
            "   - Exemplo de valor em negrito: **R\\$ 4.742,82**\n\n"
            
            "NÃO FAÇA:\n"
            "   - Nunca use o cifrão sem a barra invertida (Nunca use: R$)\n"
            "   - Nunca deixe asterisco solto: R\\$ 50,00** ou **R\\$ 50,00\n"
            "   - Nunca use: `código` ou ~tachado~\n"
            "   - Nunca junte: R\\$50,00 (sempre R\\$ 50,00)\n\n"

            "EXEMPLO DE SAÍDA CORRETA:\n"
            "• Economia Real: No parcelamento, você paga **R\\$ 4.742,82**, "
            "mas à vista é **R\\$ 5.098,89**. Você economiza **R\\$ 356,07** imediatamente."
    )
    # Convertendo os dados cruciais em uma string compacta (pouquíssimos tokens)
    dados_resumidos = (
        f"Recomendação: {melhor_opcao}\n"
        f"Preço Regular: R${p_regular:.2f}\n"
        f"Preço à Vista: R${p_vista:.2f}\n"
        f"Valor Presente das Parcelas: R${vp_parcelas:.2f}\n"
        f"Taxa de Juros Embutida (TIR): {tir_m:.2%}/mês\n"
        f"Rendimento do Custo de Oportunidade (CDI): {cdi_m:.2%}/mês\n"
        f"Resultado Financeiro Final após o período: R${lucro_final:.2f}"
    )

    try:
        # Usando o mesmo modelo leve e rápido (Gemini Flash via OpenRouter)
        response = client.chat.completions.create(
            model="qwen/qwen-2.5-72b-instruct",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": f"Dados do cenário:\n{dados_resumidos}"}
            ],
            temperature=0.3
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        return f"Desculpe, não consegui gerar a explicação detalhada agora devido a um erro técnico: {e}"