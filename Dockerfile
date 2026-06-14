# Usa uma imagem oficial enxuta do Python
FROM python:3.11-slim

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia primeiro o arquivo de requisitos para aproveitar o cache do Docker
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Instala o Chromium e todas as dependências do sistema operacional que o Playwright exige
RUN playwright install chromium && playwright install-deps chromium

# Copia o restante do código fonte do projeto
COPY . .

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando que inicia o Streamlit, acessível para a máquina local
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]