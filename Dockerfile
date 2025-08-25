# Use uma imagem oficial do Python 3.10 em uma versão slim para manter o tamanho pequeno.
FROM python:3.11-slim-buster

# Defina o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copie o arquivo de requisitos para aproveitar o cache do Docker.
COPY requirements.txt ./

# Instale as dependências.
RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante do código da sua aplicação para o contêiner.
COPY . .

# Expõe a porta em que a aplicação será executada.
EXPOSE 8000

# O comando para iniciar a aplicação com Uvicorn.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]