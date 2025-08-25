# Aplicação de Gerenciamento de Tarefas com FastAPI e Docker

Este projeto é uma aplicação web de gerenciamento de tarefas, construída com o framework **FastAPI**, que se conecta a um banco de dados **SQLite**. A aplicação é empacotada e executada em um contêiner Docker, usando `pip` para gerenciar as dependências e **Docker Compose** para orquestrar o ambiente.

## Pré-requisitos

Certifique-se de ter o **Docker** e o **Docker Compose** instalados em sua máquina.

## Como Usar

Siga os passos abaixo para clonar o repositório, configurar as variáveis de ambiente, construir a imagem Docker e executar a aplicação.

### 1. Configurar as Variáveis de Ambiente

Crie um arquivo chamado `.env` na raiz do seu projeto e adicione suas credenciais de usuário e senha, conforme o exemplo abaixo. **Substitua `seu_usuario` e `sua_senha_secreta` por valores de sua escolha.**

```
USER=seu_usuario
PASS=sua_senha_secreta
```

### 2. Construir e Executar os Contêineres

Para construir a imagem Docker e iniciar os contêineres em segundo plano, abra o terminal no diretório do projeto e use o seguinte comando:

```bash
docker-compose up --build -d
```

### 3. Acessar a Aplicação

A aplicação estará acessível no seu navegador em:

[http://localhost:8000/docs](http://localhost:8000/docs)

Você será solicitado a autenticar. Use as credenciais que você definiu no arquivo `.env`.

### 4. Parar a Aplicação

Para parar os contêineres e remover a rede, use o seguinte comando no terminal:

```bash
docker-compose down
```
