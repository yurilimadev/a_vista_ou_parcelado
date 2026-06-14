# À vista ou Parcelado

Esse app foi criado inspirado em curso de Matemática Financeira da Escola Virtual do Governo. Essa ideia de aplicação veio por causa de uma grande dúvida que temos quando vamos fazer a aquisição de algum bem: Compra a vista ou parcelado? Afinal, qual a melhor opção?

De acordo com a matemática financeira temos que pensar no conceito que dinheiro perde seu valor no tempo. E quando estamos fazendo essa analise temos sempre que pensar quanto o dinheiro vale hoje e quanto ele vai valer no futuro e com mais alguns calculos podemos fazer comparações com taxas e verificar qual a melhor decisão a ser tomada.

Esse projeto engloba conceitos como
- Fluxo de Caixa
- Valor Presente
- Valor Futuro
- Taxa Interna de Retorno 

# Como usar esse aplicativo?

A utilização é bastante simples e direta:

1. **Acesse o aplicativo** pelo navegador.
2. **Cole o link do produto** de qualquer site de e-commerce na caixa de texto indicada.
3. **Clique em "Analise a melhor opção!"** e aguarde os cálculos. O robô vai acessar a loja, ler a página e identificar as condições de pagamento.
4. **Verifique os painéis de resultados:** A tela exibirá a decisão recomendada (À vista ou Parcelado), o Valor Presente das parcelas, a Taxa de Juros embutida (TIR), o CDI atualizado e uma projeção mês a mês de como o seu dinheiro renderia.
5. **Aprofunde-se com IA (Opcional):** Você também pode clicar no botão **"✨ Gerar Parecer Econômico Detalhado"** para receber uma explicação humanizada, elaborada por inteligência artificial, sobre o porquê de uma escolha ser melhor que a outra para o seu bolso.

# Como foi feito esse aplicativo?

O projeto foi construído em **Python** e opera dividindo as tarefas em módulos específicos (Stack e Features):

- **`app.py` (Streamlit):** O coração da aplicação e a interface com o usuário. Rápida e interativa.
- **`extrator.py` (Playwright & BeautifulSoup):** Responsável por fazer o web scraping. Ele abre um navegador invisível, acessa o link do e-commerce simulando um usuário humano (para burlar bloqueios), e extrai todo o texto da página, limpando tags inúteis.
- **`analisador.py` (OpenRouter API com LLM):** Pega a montoeira de texto lida do site e utiliza Inteligência Artificial (modelo Qwen) para extrair os dados limpos: preço cheio, à vista, valor e quantidade de parcelas. Esse módulo também gera o parecer financeiro humanizado.
- **`custo_de_oportunidade.py` (Requests, Pandas & Numpy Financial):** Consulta a API pública do Banco Central do Brasil para buscar a taxa Selic em tempo real e calcula o custo de oportunidade (CDI). Com isso, aplica os cálculos de Valor Presente e Taxa Interna de Retorno (TIR) para gerar um fluxo de caixa (evolução do seu saldo rendendo ao longo do tempo).

# Quer usar o app na sua casa?

Você pode rodar este projeto de duas formas: usando a sua própria máquina (ambiente virtual) ou isolando a aplicação em um container utilizando **Docker**.

### 1. Preparação Inicial (Para ambas as opções)

Primeiro, baixe o código fonte e configure a sua chave de API:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd a_vista_ou_parcelado
```

Crie um arquivo `.env` na raiz do projeto e insira a sua chave do OpenRouter:
```env
OPENROUTER_API_KEY=sua_chave_de_api_aqui
```

### 2. Opção A: Sem Docker (Instalação Local Padrão)

Crie um ambiente virtual (recomendado) e instale todas as bibliotecas necessárias:
```bash
python -m venv venv
source venv/bin/activate  # No Windows, utilize: venv\Scripts\activate
pip install streamlit playwright beautifulsoup4 numpy-financial requests pandas numpy openai python-dotenv
playwright install chromium
```

Inicie a aplicação localmente:
```bash
streamlit run app.py
```

### 2. Opção B: Com Docker

Caso não queira instalar o Python e dependências de navegador na sua máquina, utilize o Docker. Com o serviço rodando, construa a imagem da aplicação:
```bash
docker build -t avista-parcelado .
```

Depois, rode o container repassando o seu arquivo de credenciais e a porta padrão do Streamlit (8501):
```bash
docker run -p 8501:8501 --env-file .env avista-parcelado
```

# Próximos Desafios

Como a educação e inteligência financeira são temas muito amplos, o projeto continuará evoluindo. Os nossos próximos grandes desafios são:

- **Gestão Eficiente de Tokens (Limpeza Avançada de HTML):** Aprimorar os algoritmos de tratamento e sumarização de texto bruto extraído via web scraping. O objetivo é enviar um conteúdo ainda mais enxuto e preciso para a IA (LLM), reduzindo custos de API e melhorando o tempo de resposta.
- **Expansão das Análises Financeiras:** Reutilizar a inteligência e os cálculos de Taxa Interna de Retorno (TIR), Taxa Mínima de Atratividade (TMA/TAM) e Fluxo de Caixa para ajudar o usuário em outras situações de crédito, tais como:
  - Comparação de **Financiamentos** (imobiliários, automotivos, etc).
  - Avaliação de viabilidade de **Empréstimos** e renegociação de dívidas.