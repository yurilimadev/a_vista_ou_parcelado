import streamlit as st
import numpy_financial  as npf
import requests
import pandas as pd
import numpy as np

@st.cache_data(ttl=3360)
def pegar_custo_de_oportunidade():
    try:
        # Código 432 é a meta Selic definida pelo COPOM, ótima para custo de oportunidade líquido
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5.0)
        dados = response.json()
        # A taxa vem como string de percentual diário anualizado (ex: "10.50")
        taxa_anual = float(dados[0]['valor']) / 100
        return taxa_anual
    except Exception as e:
        print(f"Erro ao buscar CDI no BACEN: {e}. Usando fallback de 10.5% a.a.")
        return 0.105 # Fallback seguro se a API do governo oscilar
    
@st.cache_data(ttl=3360)
def analisar_situacao_de_compra(info_llm):
    cdi = pegar_custo_de_oportunidade()

    p_vista=info_llm.get("preco_avista")
    p_parcelado=info_llm.get("preco_total_parcelado")
    n_parcelas=info_llm.get("numero_parcelas")
    v_parcela=info_llm.get("valor_parcela")
    p_sem_desconto = info_llm.get("valor_completo") or p_parcelado

    cdi_mensal = (1 + cdi) ** (1/12) -1 
    valor_presente_parcelas = abs(npf.pv(cdi_mensal, n_parcelas, v_parcela))

    fluxo_caixa = [p_vista] + [-v_parcela] * n_parcelas
    
    try:
        tir_mensal = npf.irr(fluxo_caixa)
        # Se o numpy retornar None, nan ou inf, força para 0.0
        if tir_mensal is None or np.isnan(tir_mensal) or np.isinf(tir_mensal):
            tir_mensal = 0.0
    except:
        tir_mensal = 0.0
        
    tir_anual = (1+tir_mensal) ** 12 - 1
    print(tir_mensal, tir_anual)

    
    print(cdi_mensal)
    melhor_opcao = "À VISTA" if tir_mensal > cdi_mensal else "PARCELADO (Investindo o saldo)"

    saldo_investido = p_vista - v_parcela
    historico_saldo = []

    for mes in range(1, n_parcelas + 1):
        saldo_investido = saldo_investido * (1 + cdi_mensal)
        historico_saldo.append({
            "Mês": mes,
            "Saldo Rendendo (R$)": round(saldo_investido, 2),
            "Parcela Paga (R$)": v_parcela
        })
        # Desconta a próxima parcela (no fim do mês)
        saldo_investido -= v_parcela

    df_evolucao = pd.DataFrame(historico_saldo)
    return {
        "tir_mensal": tir_mensal,
        "tir_anual": tir_anual,
        "cdi_mensal": cdi_mensal,
        "cdi_anual": cdi,
        "melhor_opcao": melhor_opcao,
        "df_evolucao": df_evolucao,
        "lucro_prejuizo_final": round(saldo_investido, 2),
        "preco_regular": p_sem_desconto,
        "preco_avista": p_vista,
        "valor_presente_parcelas": round(valor_presente_parcelas, 2),
        # Desconto real: Diferença entre o valor de mercado (regular) e o à vista
        "desconto_nominal_avista": round(p_sem_desconto - p_vista, 2) if p_sem_desconto else 0,
        # Economia Matemática: Se o VP das parcelas for menor que o preço à vista, 
        # parcelar é matematicamente mais barato do que pagar à vista hoje.
        "vantagem_real_parcelado": round(p_vista - valor_presente_parcelas, 2)
    }
if __name__ == "__main__":
    resultado_json = {
        "valor_completo":724,
        "preco_avista":689,
        "preco_total_parcelado": 689,
        "numero_parcelas":10,
        "valor_parcela":68.9
    }
    x = analisar_situacao_de_compra(info_llm=resultado_json)
    print(x)
    
