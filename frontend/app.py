import streamlit as st
import requests
import pandas as pd

# URL da nossa nova API interna (o nome 'api' é resolvido pelo Docker Compose)
API_URL = "http://api:8000" 

# --- Configurações e Estado da Sessão ---
# Config da pagina
st.set_page_config(
    page_title="A vista ou Parcelado?",
    layout='centered'
)

# --- 1. INICIALIZAÇÃO DA MEMÓRIA DO APP (SESSION STATE) ---
if "situacao_de_compra" not in st.session_state:
    st.session_state.situacao_de_compra = None

if "relatorio_ia" not in st.session_state:
    st.session_state.relatorio_ia = None


# Aplicação propriamente dita
st.title("A vista ou Parcelado?")
st.subheader("Pensando em fazer alguma compra? Cole o link do produto que você está desejando e descubra qual a melhor opção compra!")

url = st.text_input("Cole o Link do Produto")
botao_analisar = st.button("Analise a melhor opção!")

# --- 2. GATILHO DO BOTÃO PRINCIPAL ---
if botao_analisar:
    if not url:
        st.warning("Tem que colar um link de produto primeiro.")
    else:
        st.session_state.relatorio_ia = None
        st.session_state.situacao_de_compra = None
        
        with st.spinner("Analisando o link... O robô está acessando a loja e calculando as opções."):
            try:
                response = requests.post(f"{API_URL}/analisar-url", json={"url": url}, timeout=60)
                response.raise_for_status() # Lança um erro para respostas 4xx ou 5xx
                st.session_state.situacao_de_compra = response.json()
            except requests.exceptions.RequestException as e:
                st.error(f"Falha na comunicação com o servidor de análise: {e}")
            except Exception as e:
                st.error(f"Ocorreu um erro inesperado: {e}")
        
        # Se a API retornou um erro no corpo da resposta
        if st.session_state.situacao_de_compra and "detail" in st.session_state.situacao_de_compra:
            st.error(f"Erro na análise: {st.session_state.situacao_de_compra['detail']}")
            st.session_state.situacao_de_compra = None
        else:
            st.rerun()

# --- 3. BLOCOS DE EXIBIÇÃO (FORA DO IF DO BOTÃO PRINCIPAL) ---
# Se a nossa "gaveta" tiver dados salvos, renderizamos a tela inteira.
# Isso garante que interações secundárias (como o botão da IA) não sumam com os gráficos!
if st.session_state.situacao_de_compra is not None:
    situacao_de_compra = st.session_state.situacao_de_compra
    
    # Convertendo o dicionário do DataFrame de volta para um DataFrame Pandas
    if 'df_evolucao' in situacao_de_compra and isinstance(situacao_de_compra['df_evolucao'], list):
        situacao_de_compra['df_evolucao'] = pd.DataFrame(situacao_de_compra['df_evolucao'])

    if "erro" not in situacao_de_compra:
        st.markdown("---")
        st.subheader(f"🏆 Decisão Recomendada: Pagar **{situacao_de_compra['melhor_opcao']}**")

        # Estrutura em 2 colunas amplas para não cortar os textos
        col_esquerda, col_direita = st.columns(2)

        with col_esquerda:
            st.markdown("### 💰 Valores de Face")
            st.metric(
                label="Preço Regular (Sem Desconto)", 
                value=f"R$ {situacao_de_compra['preco_regular']:.2f}",
                help="O preço padrão do produto parcelado. Muitas vezes é o valor de referência sobre o qual os e-commerces aplicam o desconto à vista."
            )
            st.metric(
                label="Valor Presente das Parcelas (VP)", 
                value=f"R$ {situacao_de_compra['valor_presente_parcelas']:.2f}",
                help="Quanto a soma de todas as parcelas futuras vale HOJE. Calculamos isso descontando o rendimento que esse dinheiro teria se ficasse no CDI mês a mês."
            )
            st.metric(
                label="Desconto Nominal À Vista", 
                value=f"R$ {situacao_de_compra['desconto_nominal_avista']:.2f}",
                delta=f"{((situacao_de_compra['preco_regular'] - situacao_de_compra['preco_avista']) / situacao_de_compra['preco_regular']):.1%} de desconto",
                help="A diferença bruta em Reais entre o preço regular e o preço com desconto (Pix/Boleto), junto com o percentual real de desconto aplicado pelo site."
            )

        with col_direita:
            st.markdown("### 📊 Taxas e Vantagem Real")
            st.metric(
                label="Juros do Parcelamento (TIR)", 
                value=f"{situacao_de_compra['tir_mensal']:.2%} a.m.",
                help="Taxa Interna de Retorno. É a taxa de juros real implícita que você aceita 'pagar' ao abrir mão do desconto à vista para parcelar o produto."
            )
            st.metric(
                label="Custo de Oportunidade (CDI Atual)", 
                value=f"{situacao_de_compra['cdi_mensal']:.2%} a.m.",
                help=f"Rendimento do CDI mensal equivalente, calculado com base na taxa Selic atual capturada em tempo real direto do Banco Central ({situacao_de_compra['cdi_anual']:.2%} a.a.)."
            )
            
            vantagem = situacao_de_compra['vantagem_real_parcelado']
            st.metric(
                label="Vantagem Real Estimada (VP)", 
                value=f"R$ {abs(vantagem):.2f}",
                delta="Melhor Parcelar" if vantagem > 0 else "Melhor À Vista",
                delta_color="normal" if vantagem > 0 else "inverse",
                help="A diferença financeira matemática entre pagar à vista hoje ou parcelar e investir o saldo. Mostra em Reais de hoje qual decisão protege melhor seu patrimônio."
            )

        st.markdown("---")
        st.markdown("### 📈 Detalhamento da Estratégia no Tempo")
        
        df_dados = situacao_de_compra['df_evolucao']

        st.write("Acompanhe o comportamento do saldo mês a mês se você optasse por investir o valor equivalente à vista:")
        df_exibicao = df_dados.rename(columns={
            "Saldo Rendendo (R$)": "Saldo Investido (R$)",
            "Parcela Paga (R$)": "Valor da Parcela (R$)"
        })
        st.dataframe(df_exibicao.set_index("Mês"), width="stretch")
        
        if situacao_de_compra['lucro_prejuizo_final'] > 0:
            st.success(f"💰 Deixando o dinheiro no CDI e parcelando, sobram **R$ {situacao_de_compra['lucro_prejuizo_final']:.2f}** líquidos no seu bolso após pagar todas as parcelas!")
        else:
            st.error(f"📉 Pagar à vista te economiza o equivalente a **R$ {abs(situacao_de_compra['lucro_prejuizo_final']):.2f}** em juros reais frente ao custo de oportunidade do parcelamento.")

        st.write("Visualização gráfica da curva de evolução do seu patrimônio durante o parcelamento:")
        st.line_chart(
            data=df_dados, 
            x="Mês", 
            y="Saldo Rendendo (R$)", 
            color="#29b5e8"
        )

        # --- 4. SEÇÃO DO ESPECIALISTA IA ---
        if 'uso_llm' not in st.session_state:
            st.session_state.uso_llm = 0
        LIMITE_USO = 3 

        if st.session_state.relatorio_ia is None:
            if st.button("✨ Gerar Parecer Econômico Detalhado"):
                
                # 2. Verifica se o usuário estourou a cota ANTES de chamar a IA
                if st.session_state.uso_llm >= LIMITE_USO:
                    st.error("⚠️ Você atingiu o limite de análises gratuitas nesta sessão. Tente novamente mais tarde!")
                else:
                    with st.spinner("A Inteligência Artificial está analisando o seu cenário..."):
                        try:
                            # Passamos o dicionário completo para a API
                            response = requests.post(f"{API_URL}/gerar-parecer", json=situacao_de_compra, timeout=30)
                            response.raise_for_status()
                            st.session_state.relatorio_ia = response.json().get("parecer")
                            st.session_state.uso_llm += 1
                        except requests.exceptions.RequestException as e:
                            st.error(f"Não foi possível gerar o parecer: {e}")
                        st.rerun()
        else:
            # 4. Feedback visual opcional: mostra quantas análises ainda restam
            tentativas_restantes = LIMITE_USO - st.session_state.uso_llm
            st.caption(f"Você ainda tem **{tentativas_restantes}** requisições de IA restantes.")
            
            if st.button("🔄 Análise Pronta (Clique para recalcular)"):
                st.session_state.relatorio_ia = None
                st.rerun()

        if st.session_state.relatorio_ia is not None:
            st.info("💡 **Parecer Técnico da IA:**")
            
            # Dica extra: Se o LLM ainda estiver mandando R$ "quebrado", faça o replace aqui
            texto_formatado = st.session_state.relatorio_ia.replace("R$", "R\\$")
            st.markdown(texto_formatado)
            
    else:
        st.error("A extração dos dados financeiros retornou um erro interno.")