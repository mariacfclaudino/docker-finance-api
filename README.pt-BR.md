# 🐳 API de Controle Financeiro (versão com Docker)

API RESTful de finanças pessoais (FastAPI + SQLAlchemy + SQLite) **conteinerizada com Docker**.

> Este repositório é a versão containerizada do projeto. O código da API é o mesmo da versão sem Docker ([repositório original](https://github.com/mariacfclaudino/API-Controle-Financeiro)); a diferença está nos arquivos de infraestrutura descritos abaixo.

## 📑 Sumário

- [Por que Docker neste projeto](#-por-que-docker-neste-projeto)
- [O que foi adicionado](#-o-que-foi-adicionado)
- [Como rodar](#-como-rodar)
- [Entendendo cada arquivo](#-entendendo-cada-arquivo)
- [Persistência do banco de dados](#-persistência-do-banco-de-dados)
- [Variáveis de ambiente](#️-variáveis-de-ambiente)
- [Comandos úteis](#-comandos-úteis)
- [Problemas comuns](#-problemas-comuns)
- [Sobre a API](#-sobre-a-api)

## 🎯 Por que Docker neste projeto

| Sem Docker                                                     | Com Docker                                      |
| -------------------------------------------------------------- | ----------------------------------------------- |
| Instalar Python 3.10+ na versão certa                          | Só precisa do Docker instalado                  |
| Criar e ativar o `venv`, rodar `pip install`                   | Tudo acontece dentro da imagem                  |
| "Funciona na minha máquina"                                    | Mesmo ambiente em qualquer máquina ou servidor  |
| Banco `.db` solto na pasta do projeto                          | Banco em volume gerenciado pelo Docker          |
| Vários comandos para subir                                     | `docker compose up --build`                     |

## 📦 O que foi adicionado

Em relação à versão sem Docker, o projeto ganhou três arquivos na raiz:

```
API-Controle-Financeiro/
├── app/                    
├── Dockerfile               
├── docker-compose.yml       
├── .dockerignore            
├── .env.example
└── requirements.txt
```

## 🚀 Como rodar

**Pré-requisito:** [Docker](https://docs.docker.com/get-docker/) com Docker Compose (já vem junto no Docker Desktop).

```bash
# 1. Clonar
git clone https://github.com/mariacfclaudino/docker-finance-api.git
cd docker-finance-api

# 2. Criar o .env e ajustar a SECRET_KEY
cp .env.example .env

# 3. Construir a imagem e subir o container
docker compose up --build
```

Pronto. A API está em `http://localhost:8000` e a documentação Swagger em `http://localhost:8000/docs`.

Para rodar em segundo plano, use `docker compose up -d --build`.

## 🔍 Entendendo cada arquivo

### `Dockerfile`: a receita da imagem

```dockerfile
FROM python:3.12-slim
```
Imagem base com Python já instalado. A variante `slim` é bem menor que a completa, o que deixa o build e o download mais rápidos.

```dockerfile
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
```
Evita criar arquivos `.pyc`, faz os logs aparecerem em tempo real no terminal e impede que o pip guarde cache dentro da imagem.

```dockerfile
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```
Primeiro copia **só** o `requirements.txt` e instala as dependências; depois copia o projeto todo. O `COPY . .` leva tudo para a imagem, por isso o `.dockerignore` é essencial: ele deixa `.env`, `.venv/` e `*.db` de fora. Isso importa por causa do **cache de camadas**: se você mudar apenas o código, o Docker reaproveita a camada das dependências e o rebuild leva segundos em vez de minutos.

```dockerfile
RUN useradd --create-home appuser \
    && mkdir /data \
    && chown appuser:appuser /data
USER appuser
```
Cria um usuário comum e a pasta `/data` (onde ficará o banco). A aplicação roda **sem privilégios de root**, uma boa prática de segurança.

```dockerfile
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Documenta a porta e define o comando de inicialização. O `--host 0.0.0.0` é essencial: sem ele, a API escutaria só dentro do container e não seria acessível de fora.

### `docker-compose.yml`: como o container roda

```yaml
services:
  api:
    build: .                        # constrói a imagem a partir do Dockerfile
    ports:
      - "8000:8000"                 # porta_do_seu_pc:porta_do_container
    env_file:
      - .env                        # carrega as variáveis do .env em runtime
    environment:
      DATABASE_URL: sqlite:////data/financial.db   # aponta o banco para o volume
    volumes:
      - db_data:/data               # volume persistente montado em /data
    restart: unless-stopped         # reinicia sozinho se cair
    healthcheck: ...                # verifica periodicamente se a API responde
```

Pontos importantes:

- **`env_file`** injeta o `.env` só na hora de rodar. Ele **não** é copiado para dentro da imagem, então a `SECRET_KEY` não vaza se você publicar a imagem.
- **`environment`** tem prioridade sobre o `.env`. Por isso o `DATABASE_URL` é sobrescrito: dentro do container o banco precisa ficar no volume `/data`, não na pasta do código.
- **`healthcheck`** acessa `/docs` a cada 30 segundos. O `docker compose ps` mostra `healthy` ou `unhealthy`.

### `.dockerignore`: o que fica de fora da imagem

```
.venv/    __pycache__/    *.pyc    .git/    .env    *.db  ...
```
Funciona como o `.gitignore`, mas para o `docker build`. Deixa a imagem menor e impede que o `.env` (segredos) e bancos locais entrem nela.

## 💾 Persistência do banco de dados

Containers são **descartáveis**: tudo que fica dentro deles some quando são removidos. Como o SQLite é um arquivo, ele precisa ficar fora do ciclo de vida do container. Por isso o Compose usa um **volume nomeado** (`db_data`) montado em `/data`.

| Ação                                       | Dados do banco |
| ------------------------------------------ | -------------- |
| `docker compose restart`                   | ✅ mantidos     |
| `docker compose down`                      | ✅ mantidos     |
| `docker compose up --build` (rebuild)      | ✅ mantidos     |
| `docker compose down -v`                   | ❌ **apagados** |

Para inspecionar o volume:

```bash
docker volume ls
docker volume inspect api-controle-financeiro_db_data
```

> O nome do volume recebe como prefixo o nome da pasta do projeto, por isso pode variar na sua máquina.

## ⚙️ Variáveis de ambiente

Definidas no `.env` (copie de `.env.example`):

| Variável                      | Descrição                                  | Exemplo                          |
| ----------------------------- | ------------------------------------------ | -------------------------------- |
| `SECRET_KEY`                  | Chave usada para assinar os tokens JWT     | gere com `openssl rand -hex 32`  |
| `DATABASE_URL`                | URL do banco (**sobrescrita pelo Compose**) | `sqlite:///./financial.db`       |
| `ALGORITHM`                   | Algoritmo do JWT                           | `HS256`                          |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiração do token, em minutos             | `30`                             |

> ⚠️ Nunca faça commit do `.env`.

## 🧰 Comandos úteis

```bash
# Ciclo de vida
docker compose up --build        # constrói e sobe (com logs no terminal)
docker compose up -d             # sobe em segundo plano
docker compose stop              # para sem remover
docker compose down              # para e remove containers (mantém o volume)
docker compose down -v           # remove também o volume (apaga o banco!)

# Observação e depuração
docker compose ps                # estado e saúde dos serviços
docker compose logs -f api       # logs em tempo real
docker compose exec api sh       # abre um terminal dentro do container
docker compose build --no-cache  # reconstrói a imagem do zero

# Imagem
docker images                    # lista imagens locais
docker image prune               # remove imagens sem uso
```

### Build e execução sem Compose

```bash
docker build -t controle-financeiro-api .

docker run -d --name controle-financeiro-api \
  -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL=sqlite:////data/financial.db \
  -v controle_financeiro_data:/data \
  controle-financeiro-api
```

## 🩹 Problemas comuns

**`port is already allocated` / porta 8000 em uso**
Outro processo usa a porta. Pare-o ou troque o mapeamento no Compose para `"8080:8000"` e acesse por `localhost:8080`.

**A API não abre no navegador, mas o container está rodando**
Confira se o `CMD` usa `--host 0.0.0.0`. Com `127.0.0.1`, a API só aceita conexões de dentro do container.

**`no such table` ao chamar a API**
O banco no volume está vazio e as tabelas não foram criadas. Verifique se o `main.py` chama `Base.metadata.create_all(...)` na inicialização.

**Mudei o código e nada mudou**
Faltou reconstruir a imagem: `docker compose up --build`.

**Mudei o `.env` e nada mudou**
Recrie o container: `docker compose up -d --force-recreate`.

**`ModuleNotFoundError: No module named 'uvicorn'`**
Adicione `uvicorn` (ou `fastapi[standard]`) ao `requirements.txt` e reconstrua.

**Quero começar com o banco zerado**
`docker compose down -v` e depois `docker compose up --build`.

## 📘 Sobre a API

API de finanças pessoais com cadastro de usuários, autenticação JWT e gerenciamento de contas, categorias e transações.

**Stack:** FastAPI · SQLAlchemy · SQLite · python-jose · Passlib + bcrypt · Pydantic

| Método | Rota            | Descrição                        | Autenticação |
| ------ | --------------- | -------------------------------- | ------------ |
| POST   | `/createuser`   | Cria um novo usuário             | Não          |
| POST   | `/login`        | Retorna um token JWT             | Não          |
| GET    | `/accounts`     | Lista as contas                  | Sim          |
| POST   | `/accounts`     | Cria uma conta                   | Sim          |
| GET    | `/categories`   | Lista as categorias              | Sim          |
| POST   | `/categories`   | Cria uma categoria               | Sim          |
| GET    | `/transactions` | Lista as transações              | Sim          |
| POST   | `/transactions` | Registra uma transação           | Sim          |

Rotas protegidas exigem o cabeçalho `Authorization: Bearer <token>`. A documentação interativa completa está em `/docs`.

## 📄 Licença

Projeto sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).

## 👤 Autora

**Maria** · [@mariacfclaudino](https://github.com/mariacfclaudino)
