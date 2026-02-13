# Chat-bot (Docker)

⚡ Lightweight DCIM chatbot backed by Ollama and a scheduled data fetcher.

---

## Prerequisites ✅

- Docker Engine & Docker Compose (Compose V2 recommended)
- (Optional) Python 3.11 and virtualenv for local development

---

## Quick start — run with Docker Compose 🔧

1. Build and start the whole stack:

```bash
# from repository root
docker compose up --build -d
```

2. Verify services are running:

```bash
docker compose ps
```

3. Check logs (live):

```bash
docker compose logs -f chatbot
# or
docker compose logs -f fetcher
```

4. The chatbot HTTP API will be available at:

- Chatbot: `http://localhost:8000`
- Ollama (LLM): `http://localhost:11434`

Example query (browser or curl):

```bash
curl "http://localhost:8000/ask?query=How%20many%20active%20sites%3F"
```

---

## What each service does 📚

- `ollama` — local model runtime (image: `ollama/ollama:latest`) exposed on port `11434`.
- `chatbot` — FastAPI app that queries Ollama and serves `/ask` (port `8000`).
- `fetcher` — periodic job that fetches external APIs and writes `latest.json` into `./data`.

Data file persisted to: `./data/latest.json` (mounted into both services).

---

## Environment / configuration ⚙️

- `fetcher` uses an `.env` file for credentials (when running via Docker Compose it reads the repository `.env`).

Important `.env` variables for `fetcher` (examples shown in `fetcher/fetcher.py`):

- `LOGIN_URL` — authentication endpoint
- `USERNAME` — API username
- `AUTH_TOKEN` — optional pre-created token (if provided, login step is skipped)
- `SITENAME` — optional

Create a `.env` in the repo root with the required values before starting the stack.

---

## Run services locally (without Docker) — dev mode 🧑‍💻

1. Create & activate a virtualenv (Windows example):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r chatbot-docker\app\requirements.txt
```

2. Run the FastAPI app (requires Ollama reachable at `OLLAMA_URL` env var):

```powershell
$env:OLLAMA_URL = 'http://localhost:11434'
uvicorn main:app --host 0.0.0.0 --port 8000
```

3. Run the fetcher (in a separate shell):

```powershell
pip install -r chatbot-docker\fetcher\requirements.txt
python chatbot-docker\fetcher\fetcher.py
```

---

## Health checks & troubleshooting ⚠️

- If `chatbot` returns errors, confirm `ollama` is reachable at `http://ollama:11434` (inside compose) or `http://localhost:11434` (local).
- Check logs:
  - `docker compose logs -f ollama`
  - `docker compose logs -f chatbot`
  - `docker compose logs -f fetcher`
- If the `fetcher` cannot write data, ensure `./data` is writable and `.env` contains valid credentials.

> Tip: Compose waits for `ollama` healthcheck before starting `chatbot` — if Ollama fails to start, `chatbot` will be delayed.

---

## Useful commands

- Start: `docker compose up --build -d`
- Stop: `docker compose down`
- Rebuild a single service: `docker compose up --build chatbot -d`
- View logs: `docker compose logs -f chatbot`

---

## API usage example

- Root status:

```bash
curl http://localhost:8000/
# => {"status": "Chatbot API is running"}
```

- Ask endpoint (streaming response):

```bash
curl "http://localhost:8000/ask?query=Show%20dashboard%20summary"
```

---

## File locations

- Application: `chatbot-docker/app`
- Fetcher: `chatbot-docker/fetcher`
- Compose config: `chatbot-docker/docker-compose.yml`
- Persisted data: `data/latest.json`

---

If you want, I can: add an example `.env`, extend README with deployment notes, or add a Postman collection. Which would you like next? 💡
