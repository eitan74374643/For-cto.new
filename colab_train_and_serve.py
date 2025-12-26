import os
import sys
import json
import subprocess


def pip_install(*packages: str) -> None:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", *packages])


def main():
    # 0) Install dependencies
    # Unsloth install from git is recommended for Colab.
    pip_install("flask", "pyngrok", "datasets", "accelerate", "bitsandbytes", "peft", "transformers", "trl")
    pip_install("unsloth[colab-new]@git+https://github.com/unslothai/unsloth.git")

    import torch
    from datasets import load_dataset
    from flask import Flask, request, jsonify
    from pyngrok import ngrok

    from unsloth import FastLanguageModel

    # 1) Load dataset (JSONL)
    data_path = os.environ.get("SNAKE_DATASET", "/content/snake_dataset.jsonl")
    ds = load_dataset("json", data_files=data_path, split="train")

    def format_example(ex):
        prompt = (ex.get("prompt") or "").strip()
        response = (ex.get("response") or "").rstrip() + "\n"
        text = f"### Instruction:\n{prompt}\n\n### Response:\n{response}"
        return {"text": text}

    ds = ds.map(format_example, remove_columns=ds.column_names)

    # 2) Load base model in 4-bit + attach LoRA
    model_name = os.environ.get("BASE_MODEL", "deepseek-ai/deepseek-coder-1.3b-base")
    max_seq_length = int(os.environ.get("MAX_SEQ_LEN", "1024"))

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=max_seq_length,
        dtype=None,
        load_in_4bit=True,
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=16,
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "gate_proj",
            "up_proj",
            "down_proj",
        ],
        lora_alpha=16,
        lora_dropout=0.0,
        bias="none",
        use_gradient_checkpointing=True,
        random_state=3407,
    )

    from trl import SFTTrainer
    from transformers import TrainingArguments

    out_dir = os.environ.get("TRAIN_OUT", "/content/snakecoder_out")
    lora_dir = os.environ.get("LORA_DIR", "/content/snakecoder_lora")

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=ds,
        dataset_text_field="text",
        max_seq_length=max_seq_length,
        packing=True,
        args=TrainingArguments(
            per_device_train_batch_size=1,
            gradient_accumulation_steps=8,
            warmup_steps=10,
            num_train_epochs=float(os.environ.get("EPOCHS", "1")),
            learning_rate=2e-4,
            fp16=True,
            logging_steps=10,
            optim="adamw_8bit",
            weight_decay=0.01,
            lr_scheduler_type="linear",
            output_dir=out_dir,
            save_strategy="steps",
            save_steps=100,
            report_to="none",
        ),
    )

    trainer.train()

    trainer.model.save_pretrained(lora_dir)
    tokenizer.save_pretrained(lora_dir)

    # 3) Serve via Flask + ngrok
    app = Flask(__name__)

    authtoken = os.environ.get("NGROK_AUTHTOKEN", "").strip()
    if authtoken:
        ngrok.set_auth_token(authtoken)

    public_url = ngrok.connect(5000).public_url
    print("Public URL:", public_url)
    print("Desktop GUI endpoint:", public_url + "/generate")

    def build_instruct(prompt: str) -> str:
        prompt = (prompt or "").strip()
        return f"### Instruction:\n{prompt}\n\n### Response:\n"

    @app.get("/health")
    def health():
        return jsonify({"ok": True})

    @app.post("/generate")
    def generate():
        payload = request.get_json(force=True, silent=True) or {}
        prompt = payload.get("prompt", "")
        max_new_tokens = int(payload.get("max_new_tokens", 700))
        max_new_tokens = max(64, min(max_new_tokens, 1400))

        full_prompt = build_instruct(prompt)

        FastLanguageModel.for_inference(model)
        inputs = tokenizer(full_prompt, return_tensors="pt").to("cuda")

        with torch.no_grad():
            out = model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=0.15,
                top_p=0.95,
                do_sample=True,
                eos_token_id=tokenizer.eos_token_id,
            )

        text = tokenizer.decode(out[0], skip_special_tokens=True)
        marker = "### Response:"
        code = text
        if marker in text:
            code = text.split(marker, 1)[1].lstrip()

        return jsonify({"code": code, "raw_text": text})

    app.run(host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
