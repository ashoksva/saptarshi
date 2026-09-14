# Day 2 — QLoRA adapter (preparation)

No GPU is running. This folder is the **training kit** for when you have a dataset.

Day 2 is a **different pod** from Day 1: **PyTorch**, not `vllm/vllm-openai`. Training and serving on the same vLLM container will OOM or fight for VRAM.

## What you must bring

A JSONL file. Each line:

```json
{"messages": [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

Two useful example types (both can live in one file):

1. **Router** — system = supervisor prompt, assistant = JSON `{"primary":"bharadvaja",...}`
2. **Specialist** — system = that rishi’s prompt, assistant = the answer you want

Copy [`data/example.jsonl`](data/example.jsonl) and replace with **your** rows. A few dozen is a smoke test; hundreds+ is a real first adapter. Mix both types if you want better routing **and** better answers.

Validate before you pay for a GPU:

```bash
python training/validate_data.py training/data/example.jsonl
```

## Weather sample (Hyderabad, 2025)

For Atri learning data, one city:

- CSV: [`data/weather_hyderabad_2025.csv`](data/weather_hyderabad_2025.csv) (365 days)
- Source: [Open-Meteo historical forecast](https://open-meteo.com/en/docs/historical-forecast-api) (not IMD). Prototype-friendly, no API key.

This CSV is **observations/model history**, not chat JSONL. Next step is converting rows into Atri `messages` examples, then `train_qlora.py`.

## Train (Runpod 4090, ~$0.74/hr Secure)

1. Create a **PyTorch CUDA** pod (official Runpod PyTorch template / `runpod/pytorch` image), **not** vLLM. 60+ GB disk. Jupyter or SSH.
2. Copy this `training/` folder onto the pod (`/workspace/saptarshi-training` is fine).
3. Install and run:

```bash
pip install -r requirements.txt
python train_qlora.py --data data/your.jsonl --output /workspace/saptarshi-adapter
```

Base model defaults to `Qwen/Qwen2.5-7B-Instruct` (4-bit QLoRA). First run downloads ~15 GB again unless you mount a volume.

4. When it finishes, **download** `/workspace/saptarshi-adapter` (adapter `safetensors` + `adapter_config.json`, not the full 7B).
5. **Terminate** the training pod.

On a 4090, a small JSONL is often **30–90 minutes**. Watch loss; stop if it spikes.

## Day 3 (later)

Serve **Instruct + this adapter** with vLLM (`--enable-lora` / `--lora-modules`). Keep the adapter on your laptop or Hugging Face until then.

## Do not

- Train on the Day 1 vLLM image
- Leave the training pod running overnight
- Commit `training/output/` or private datasets
