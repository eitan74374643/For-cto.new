# Snake Coder AI (from scratch)

This repo contains 3 components:

1) **Desktop GUI** (Windows/Linux) using **CustomTkinter** that sends prompts to a Colab-hosted server and displays syntax-highlighted code.
2) **Dataset generator** that produces **100+** prompt/code pairs for Snake Game variants in **JSONL**.
3) **Colab training + server** that fine-tunes **DeepSeek-Coder-1.3B** using **4-bit + LoRA** (Unsloth) and serves generations via **Flask + ngrok**.

## 1) Desktop GUI

### Install
```bash
pip install customtkinter requests
```

### Run
```bash
python desktop_gui.py
```

Set **Colab Server URL** to the printed ngrok URL + `/generate`.

## 2) Generate training data

```bash
python generate_snake_dataset.py --out snake_dataset.jsonl --n 120
```

Each JSONL line includes:
- `prompt`
- `response` (full runnable pygame snake code)

## 3) Colab training + server

In Google Colab:
- Upload `snake_dataset.jsonl` to `/content/` (default)
- Run `colab_train_and_serve.py`

Notes:
- Set `NGROK_AUTHTOKEN` in Colab env for stable ngrok usage.
- Defaults are tuned for Colab Free Tier (T4) using 4-bit quantization + LoRA.
