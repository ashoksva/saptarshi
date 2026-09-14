# SAPTARSHI

Voice-first web prototype: a FastAPI supervisor routes to seven rishi agents. All agents call one OpenAI-compatible Hugging Face model (or the local stub).

## Run locally (stub model, no GPU)

```bash
cp .env.example .env
docker compose up --build
```

- Web: http://localhost:3000
- API: http://localhost:8000/health
- Stub LLM: http://localhost:8001/health

Without Docker, three terminals:

```bash
# stub
cd apps/stub-llm && pip install -r requirements.txt && uvicorn main:app --port 8001

# api
cd apps/api && pip install -r requirements.txt
PYTHONPATH=../../packages/agents:. uvicorn app.main:app --reload --port 8000

# web
cd apps/web && npm install && npm run dev
```

Hold the star to talk (Chrome / Edge). Safari speech support is limited; type instead.

## Real GPU model

See [infra/model/README.md](infra/model/README.md). Set `MODEL_BASE_URL` to your vLLM endpoint.

## HTTP contract (mobile later)

`POST /v1/chat` with `{ "text": "..." }` returns `{ reply, spoken, agents_used, agents_display, route_reason, primary }`.
