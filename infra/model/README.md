# SAPTARSHI model host

The agent API talks to any **OpenAI-compatible** chat endpoint:

`POST {MODEL_BASE_URL}/chat/completions`

Set these in `.env` (see repo `.env.example`):

- `MODEL_BASE_URL` — e.g. `http://127.0.0.1:8001/v1` (stub) or `https://<gpu-host>:8000/v1`
- `MODEL_API_KEY` — bearer token if the host requires one
- `HF_MODEL_ID` / `MODEL_NAME` — Hugging Face id, e.g. `Qwen/Qwen2.5-7B-Instruct`

The browser never calls the GPU. Only FastAPI does.

## Local stub (no GPU)

From the repo root:

```bash
docker compose up --build
```

`stub-llm` listens on port **8001** and returns routing JSON plus placeholder rishi answers so the voice UI can be built without a model.

Without Docker:

```bash
cd apps/stub-llm
pip install -r requirements.txt
uvicorn main:app --port 8001
```

## vLLM on a cheap GPU (RunPod / Vast / A10)

On the GPU box, after NVIDIA drivers + Docker:

```bash
export HF_MODEL_ID=Qwen/Qwen2.5-7B-Instruct

docker run --gpus all --ipc=host -p 8000:8000 \
  -e HUGGING_FACE_HUB_TOKEN=$HF_TOKEN \
  vllm/vllm-openai:latest \
  --model $HF_MODEL_ID \
  --host 0.0.0.0 \
  --port 8000
```

Then on your laptop:

```bash
MODEL_BASE_URL=http://<gpu-ip>:8000/v1
MODEL_API_KEY=empty-or-your-token
MODEL_NAME=$HF_MODEL_ID
```

Point FastAPI at that URL (compose override or `.env`). No CORS on vLLM is required.

## Hugging Face TGI

TGI is not OpenAI-native. Put a compatibility proxy in front, or switch later. Prefer vLLM for this prototype.

## Fine-tunes later

Serve the adapter-merged (or LoRA) model with the same `vllm serve` command. Agents do not change.
