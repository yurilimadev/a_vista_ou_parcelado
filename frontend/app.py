import streamlit as st
import requests
import pandas as pd

API_URL = "http://api:8000"

st.set_page_config(
    page_title="A vista ou Parcelado?",
    layout='centered'
)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if "parecer" not in st.session_state:
    st.session_state.parecer = None

if "modo_entrada" not in st.session_state:
    st.session_state.modo_entrada = "link"

st.title("A vista ou Parcelado?")
st.subheader("Descubra a melhor forma de pagamento para suas compras!")

tab_link, tab_manual = st.tabs(["📋 Colar Link", "✏️ Inserir Valores Manualmente"])

with tab_link:
    st.markdown("### Cole o link do produto")
    st.caption("O sistema vai tentar extrair automaticamente as informações da página.")
    url = st.text_input("URL do Produto", placeholder="https://www.loja.com.br/produto/...")
    
    if st.button("🔍 Analisar", key="btn_link"):
        if not url:
            st.warning("Cole um link de produto primeiro.")
        else:
            st.session_state.resultado = None
            st.session_state.parecer = None
            
            with st.spinner("Analisando o link..."):
                try:
                    response = requests.post(f"{API_URL}/analisar-url", json={"url": url}, timeout=60)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.resultado = data.get("situacao")
                    st.session_state.parecer = data.get("parecer")
                except requests.exceptions.RequestException as e:
                    st.error(f"Falha na comunicação com o servidor: {e}")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
            
            if st.session_state.resultado and "detail" in st.session_state.resultado:
                st.error(f"Erro na análise: {st.session_state.resultado['detail']}")
                st.session_state.resultado = None
            else:
                st.rerun()

with tab_manual:
    st.markdown("### Informe os valores do produto")
    st.caption("Encontre essas informações na página do produto, perto do botão de compra.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        preco_avista = st.number_input(
            "💵 Preço à Vista (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Valor com desconto Pix ou boleto. Procure por 'R$ X.XX à vista' ou 'Pix' na página."
        )
        
        numero_parcelas = st.number_input(
            "📅 Número de Parcelas",
            min_value=1,
            step=1,
            help="Quantidade de parcelas sem juros. Procure por 'em até Xx sem juros' na página."
        )
    
    with col2:
        preco_total_parcelado = st.number_input(
            "💳 Preço Total Parcelado (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Soma de todas as parcelas (preço cheio, sem desconto). Procure pelo valor total parcelado."
        )
        
        valor_parcela = st.number_input(
            "🔢 Valor da Parcela (R$)",
            min_value=0.0,
            step=0.01,
            format="%.2f",
            help="Valor de cada parcela. O sistema calcula automaticamente se você informar o total e o número de parcelas."
        )
    
    if numero_parcelas > 0 and preco_total_parcelado > 0 and valor_parcela == 0:
        valor_calculado = preco_total_parcelado / numero_parcelas
        st.info(f"📌 Parcela calculada: R$ {valor_calculado:.2f} (x{numero_parcelas})")
    
    if st.button("✨ Analisar", key="btn_manual"):
        if preco_avista <= 0:
            st.warning("Informe o preço à vista.")
        elif preco_total_parcelado <= 0:
            st.warning("Informe o preço total parcelado.")
        elif numero_parcelas < 1:
            st.warning("Informe o número de parcelas.")
        else:
            valor_final_parcela = valor_parcela if valor_parcela > 0 else preco_total_parcelado / numero_parcelas
            
            st.session_state.resultado = None
            st.session_state.parecer = None
            
            with st.spinner("Gerando análise..."):
                try:
                    payload = {
                        "preco_avista": preco_avista,
                        "preco_total_parcelado": preco_total_parcelado,
                        "numero_parcelas": numero_parcelas,
                        "valor_parcela": valor_final_parcela
                    }
                    response = requests.post(f"{API_URL}/analisar-dados-manuais", json=payload, timeout=30)
                    response.raise_for_status()
                    data = response.json()
                    st.session_state.resultado = data.get("situacao")
                    st.session_state.parecer = data.get("parecer")
                except requests.exceptions.RequestException as e:
                    st.error(f"Falha na comunicação com o servidor: {e}")
                except Exception as e:
                    st.error(f"Ocorreu um erro: {e}")
            
            if st.session_state.resultado and "detail" in st.session_state.resultado:
                st.error(f"Erro na análise: {st.session_state.resultado['detail']}")
                st.session_state.resultado = None
            else:
                st.rerun()

if st.session_state.resultado is not None:
    resultado = st.session_state.resultado
    parecer = st.session_state.parecer
    
    if 'df_evolucao' in resultado and isinstance(resultado['df_evolucao'], list):
        resultado['df_evolucao'] = pd.DataFrame(resultado['df_evolucao'])
    
    st.markdown("---")
    st.subheader(f"🏆 Decisão: **{resultado['melhor_opcao']}**")
    
    col_esq, col_dir = st.columns(2)
    
    with col_esq:
        st.markdown("### 💰 Valores")
        st.metric(
            label="Preço Regular",
            value=f"R$ {resultado['preco_regular']:.2f}"
        )
        st.metric(
            label="Preço à Vista",
            value=f"R$ {resultado['preco_avista']:.2f}",
            delta=f"{((resultado['preco_regular'] - resultado['preco_avista']) / resultado['preco_regular']):.1%} desconto"
        )
        st.metric(
            label="Valor Presente Parcelas",
            value=f"R$ {resultado['valor_presente_parcelas']:.2f}"
        )
    
    with col_dir:
        st.markdown("### 📊 Análise")
        st.metric(
            label="Juros Parcelamento (TIR)",
            value=f"{resultado['tir_mensal']:.2%} a.m."
        )
        st.metric(
            label="CDI Atual",
            value=f"{resultado['cdi_mensal']:.2%} a.m."
        )
        vantagem = resultado['vantagem_real_parcelado']
        st.metric(
            label="Vantagem Real",
            value=f"R$ {abs(vantagem):.2f}",
            delta="Melhor Parcelar" if vantagem > 0 else "Melhor À Vista"
        )
    
    st.markdown("---")
    
    if resultado['lucro_prejuizo_final'] > 0:
        st.success(f"💰 Sobram **R$ {resultado['lucro_prejuizo_final']:.2f}** parcelando e investindo!")
    else:
        st.error(f"📉 Pagar à vista economiza **R$ {abs(resultado['lucro_prejuizo_final']):.2f}**.")
    
    if parecer:
        st.markdown("---")
        st.markdown("### 💡 Explicando um pouc mais")
        texto_formatado = parecer.replace("R$", "R\\$")
        st.markdown(texto_formatado)
    
    if st.button("🔄 Nova Análise"):
        st.session_state.resultado = None
        st.session_state.parecer = None
        st.rerun()
