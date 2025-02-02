# Usar a imagem oficial do Python 3.12 slim
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Configuração do diretório de trabalho
WORKDIR /workspace

# Copiar apenas o arquivo de dependências primeiro (para aproveitar o cache de camadas do Docker)
COPY requirements.txt /workspace/

# Instalar dependências do Python
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar o restante dos arquivos do projeto
COPY . /workspace

# Comando padrão para executar o script
CMD ["python", "main.py"]