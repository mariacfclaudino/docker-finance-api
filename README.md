# 🐳 Personal Finance API (Dockerized)

A RESTful API for personal finance management, built with **FastAPI** and **SQLAlchemy** and **containerized with Docker**. It supports user registration, JWT authentication, and management of accounts, categories, and transactions.

🇧🇷 [Leia em português](README.pt-BR.md)

> This is the Docker version of the project. The same API without Docker is available at [API-Controle-Financeiro](https://github.com/mariacfclaudino/API-Controle-Financeiro).

## 📑 Table of Contents

- [Why Docker](#-why-docker)
- [Quick Start](#-quick-start)
- [How It Works](#-how-it-works)
- [Data Persistence](#-data-persistence)
- [Environment Variables](#️-environment-variables)
- [Useful Commands](#-useful-commands)
- [Troubleshooting](#-troubleshooting)
- [About the API](#-about-the-api)

## 🎯 Why Docker

| Without Docker                              | With Docker                                |
| ------------------------------------------- | ------------------------------------------ |
| Install the right Python version            | Only Docker is required                    |
| Create a `venv` and run `pip install`       | Everything happens inside the image        |
| "It works on my machine"                    | Same environment on any machine or server  |
| A loose `.db` file in the project folder    | Database stored in a Docker-managed volume |
| Several commands to start                   | `docker compose up --build`                |

## 🚀 Quick Start

**Prerequisite:** [Docker](https://docs.docker.com/get-docker/) with Docker Compose (included in Docker Desktop).

```bash
# 1. Clone the repository
git clone https://github.com/mariacfclaudino/docker-finance-api.git
cd docker-finance-api

# 2. Create your .env file and set a SECRET_KEY
cp .env.example .env

# 3. Build the image and start the container
docker compose up --build
```

The API is now available at `http://localhost:8000`, with interactive Swagger docs at `http://localhost:8000/docs`.

To run in the background: `docker compose up -d --build`.

## 🔍 How It Works

```
├── app/                 
├── actions/              
├── Dockerfile            
├── docker-compose.yml    
├── .dockerignore         
├── .env.example          
└── requirements.txt
```

### Dockerfile

```dockerfile
FROM python:3.12-slim
```
Base image with Python preinstalled. The `slim` variant keeps the image small.

```dockerfile
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```
Dependencies are installed **before** the source code is copied. Docker caches each layer, so when only the code changes, rebuilds skip the slow `pip install` step. `COPY . .` copies the whole project, so the `.dockerignore` is essential: it keeps `.env`, `.venv/` and `*.db` out of the image.

```dockerfile
RUN useradd --create-home appuser \
    && mkdir /data \
    && chown appuser:appuser /data
USER appuser
```
Creates a non-root user and the `/data` folder where the SQLite database lives. The API runs **without root privileges**, which limits the damage if the app is ever compromised.

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```
Starts the server. `--host 0.0.0.0` is essential: without it, the API would only listen inside the container and be unreachable from your machine.

### docker-compose.yml

- **`build: .`** builds the image from the Dockerfile.
- **`ports: "8000:8000"`** maps `your_machine:container`.
- **`env_file: .env`** loads variables at runtime. The `.env` is **never copied into the image**, so secrets don't leak if you publish it.
- **`environment: DATABASE_URL`** overrides the value from `.env` so the database is stored in the persistent volume.
- **`volumes: db_data:/data`** keeps the database outside the container lifecycle.
- **`restart: unless-stopped`** restarts the container automatically if it crashes.
- **`healthcheck`** requests `/docs` every 30 seconds; `docker compose ps` shows `healthy` or `unhealthy`.

### .dockerignore

Keeps `.venv/`, `.git/`, `.env`, `*.db`, and cache files out of the image, making it smaller and safer.

## 💾 Data Persistence

Containers are disposable: anything stored inside them disappears when they are removed. Since SQLite is a single file, the Compose setup stores it in a **named volume** (`db_data`) mounted at `/data`.

| Action                                  | Database      |
| --------------------------------------- | ------------- |
| `docker compose restart`                | ✅ kept        |
| `docker compose down`                   | ✅ kept        |
| `docker compose up --build` (rebuild)   | ✅ kept        |
| `docker compose down -v`                | ❌ **deleted** |

## ⚙️ Environment Variables

Set these in your `.env` file (copy from `.env.example`):

| Variable                      | Description                                    | Example                         |
| ----------------------------- | ---------------------------------------------- | ------------------------------- |
| `SECRET_KEY`                  | Key used to sign JWT tokens                    | generate with `openssl rand -hex 32` |
| `DATABASE_URL`                | Database URL (**overridden by Compose**)       | `sqlite:///./financial.db`      |
| `ALGORITHM`                   | JWT algorithm                                  | `HS256`                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime in minutes                      | `30`                            |

> ⚠️ Never commit your `.env` file.

## 🧰 Useful Commands

```bash
# Lifecycle
docker compose up --build        # build and start (logs in terminal)
docker compose up -d             # start in the background
docker compose stop              # stop without removing
docker compose down              # stop and remove containers (keeps the volume)
docker compose down -v           # also remove the volume (deletes the database!)

# Inspection and debugging
docker compose ps                # service status and health
docker compose logs -f api       # live logs
docker compose exec api sh       # open a shell inside the container
docker compose build --no-cache  # rebuild the image from scratch
```

### Without Compose

```bash
docker build -t finance-api .

docker run -d --name finance-api \
  -p 8000:8000 \
  --env-file .env \
  -e DATABASE_URL=sqlite:////data/financial.db \
  -v finance_data:/data \
  finance-api
```

## 🩹 Troubleshooting

**`port is already allocated`**
Another process is using port 8000. Stop it, or change the mapping to `"8080:8000"` and use `localhost:8080`.

**`ModuleNotFoundError: No module named 'actions'`**
The `actions/` folder wasn't copied into the image. Make sure the Dockerfile copies it (`COPY . .` with a proper `.dockerignore`), then rebuild.

**The API doesn't open in the browser but the container is running**
Check that the `CMD` uses `--host 0.0.0.0`.

**`no such table`**
The database in the volume is empty and tables weren't created. Make sure `main.py` calls `Base.metadata.create_all(...)` on startup.

**I changed the code but nothing changed**
Rebuild the image: `docker compose up --build`.

**I changed the `.env` but nothing changed**
Recreate the container: `docker compose up -d --force-recreate`.

**I want a fresh database**
`docker compose down -v`, then `docker compose up --build`.

## 📘 About the API

**Stack:** FastAPI · SQLAlchemy · SQLite · python-jose · Passlib + bcrypt · Pydantic

| Method | Route           | Description                    | Auth required |
| ------ | --------------- | ------------------------------ | ------------- |
| POST   | `/createuser`   | Create a new user              | No            |
| POST   | `/login`        | Authenticate and get a JWT     | No            |
| GET    | `/accounts`     | List accounts                  | Yes           |
| POST   | `/accounts`     | Create an account              | Yes           |
| GET    | `/categories`   | List categories                | Yes           |
| POST   | `/categories`   | Create a category              | Yes           |
| GET    | `/transactions` | List transactions              | Yes           |
| POST   | `/transactions` | Record a transaction           | Yes           |

Protected routes require the header `Authorization: Bearer <token>`. Full interactive documentation is available at `/docs`.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 👤 Author

**Maria** · [@mariacfclaudino](https://github.com/mariacfclaudino)
