# ⚡ Quick Start Guide

## 🎯 One Command to Rule Them All

```bash
python 0_master_controller.py
```

That's it! The master controller handles everything automatically.

## 📋 Pre-Flight Checklist

### Google Colab
- [ ] Upload all 8 Python files
- [ ] Run: `!pip install -r requirements.txt`
- [ ] Run: `!python 0_master_controller.py`
- [ ] ✅ System will auto-mount Google Drive

### Local PC
- [ ] Python 3.8+ installed
- [ ] CUDA toolkit installed (for GPU)
- [ ] Run: `pip install -r requirements.txt`
- [ ] Run: `python 0_master_controller.py`
- [ ] ✅ System will use current directory

## 🕐 What Happens Next?

### Day 1-3: Dataset Generation
```
📚 Generating 15,000+ training examples...
💾 Saving to: data/training_data.jsonl
✅ Progress saved after every sample
```

### Day 4-6: Training Planner Agent
```
🧠 Training lora_planner...
📊 Checkpoint saved every 2 hours
✅ Can resume if interrupted
```

### Day 7-9: Training Coder Agent
```
💻 Training lora_coder...
📊 Checkpoint saved every 2 hours
✅ Can resume if interrupted
```

### Day 10-12: Training Critic Agent
```
🔍 Training lora_critic...
📊 Checkpoint saved every 2 hours
✅ Can resume if interrupted
```

### Day 13: Merging
```
🔀 Merging all 3 adapters...
💾 Saving Final_Merged_Coder_8B
✅ Takes ~1 hour
```

### Day 14: Quantization
```
📦 Converting to GGUF (Q4_K_M)...
💾 Saving Final_Gemini3_Coder_8B.gguf
✅ Takes ~30 minutes
```

### Day 15: Launch!
```
🎨 Starting Gradio GUI...
🌐 Access at: http://localhost:7860
✅ Ready to use!
```

## 🚨 If Something Goes Wrong

### Crashed During Training?
**Just rerun the same command:**
```bash
python 0_master_controller.py
```
✅ It will automatically resume from the last checkpoint!

### Out of Memory?
Edit `2_train_three_adapters.py`:
```python
per_device_train_batch_size=1  # Reduce from 2
```

### Want to Skip GUI?
Comment out Step 5 in `0_master_controller.py`:
```python
# Step 5: Launch GUI (ONLY if GGUF exists)
# logger.info("\n📋 STEP 5: Launching GUI Application")
# ... (comment out this section)
```

## 📊 Checking Progress

### View Logs
```bash
# Master controller
tail -f master_controller.log

# Dataset generation
tail -f dataset_generation.log

# Training
tail -f training.log
```

### Check File Sizes
```bash
# Dataset
ls -lh data/training_data.jsonl

# Adapters
du -sh models/lora_*

# Final model
du -sh models/Final_Merged_Coder_8B

# GGUF
ls -lh models/Final_Gemini3_Coder_8B.gguf
```

### Tensorboard (During Training)
```bash
tensorboard --logdir=checkpoints/
```

## 🎮 Using the Final Model

### Option 1: Gradio GUI (Easiest)
```bash
python 5_gui_app.py
```
Open browser to http://localhost:7860

### Option 2: Python API
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained("models/Final_Merged_Coder_8B")
tokenizer = AutoTokenizer.from_pretrained("models/Final_Merged_Coder_8B")

prompt = "Implement a binary search tree"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=500)
print(tokenizer.decode(outputs[0]))
```

### Option 3: GGUF with llama.cpp
```bash
./llama.cpp/main -m models/Final_Gemini3_Coder_8B.gguf \
  -p "Implement a LRU cache" \
  -n 500 \
  --temp 0.7
```

### Option 4: Multi-Agent Pipeline
```python
from importlib import import_module
multi_agent = import_module('4_run_multi_agent')

pipeline = multi_agent.create_pipeline(use_merged=True)
result = pipeline.run_pipeline("Implement a thread-safe queue")
print(pipeline.format_output(result))
```

## 💡 Pro Tips

### Tip 1: Use Colab for Dataset Generation
Dataset generation is CPU-intensive. Colab's T4 GPU is perfect for this.

### Tip 2: Use Local for Training
If you have a powerful GPU (RTX 3090/4090), training locally is faster.

### Tip 3: Save Checkpoints to Cloud
```python
# In Colab, after each step:
!zip -r checkpoint.zip checkpoints/
# Download to keep
```

### Tip 4: Monitor GPU Usage
```bash
watch -n 1 nvidia-smi
```

### Tip 5: Free Tier Colab Strategy
- Run dataset generation (2-3 days)
- Train one adapter per session (3-4 days each)
- Let it disconnect, reconnect, auto-resumes!

## 🎯 Success Indicators

| Metric | Target | Check |
|--------|--------|-------|
| Training samples | 15,000+ | `wc -l data/training_data.jsonl` |
| Planner adapter | ~200MB | `du -sh models/lora_planner` |
| Coder adapter | ~200MB | `du -sh models/lora_coder` |
| Critic adapter | ~200MB | `du -sh models/lora_critic` |
| Merged model | ~16GB | `du -sh models/Final_Merged_Coder_8B` |
| GGUF model | ~4GB | `ls -lh models/*.gguf` |

## 🐛 Common Issues & Fixes

### Issue: "unsloth module not found"
```bash
pip install git+https://github.com/unslothai/unsloth.git
```

### Issue: "Cannot mount Google Drive"
```python
# In Colab, run manually first:
from google.colab import drive
drive.mount('/content/drive', force_remount=True)
```

### Issue: "Training too slow"
Check GPU is being used:
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))  # Should show GPU name
```

### Issue: "GUI not loading"
Check port:
```bash
# Kill existing Gradio
pkill -f gradio

# Or use different port
# Edit 5_gui_app.py, change server_port=7860 to 7861
```

## 📞 Need Help?

1. **Check logs** - Most errors are logged with solutions
2. **Read traceback** - Python errors are usually self-explanatory
3. **Google the error** - Likely someone had it before
4. **Check disk space** - `df -h` (need ~50GB free)
5. **Check GPU memory** - `nvidia-smi` (need 12GB+ VRAM)

## 🎉 You're Ready!

**Just run:**
```bash
python 0_master_controller.py
```

**Then sit back and watch your Gemini 3 Pro-level coder come to life! 🚀**

---

**Estimated Total Time**: ~15 days (fully autonomous)  
**Estimated Total Storage**: ~25GB  
**Estimated GPU Time**: ~360 hours  

**Cost Estimate**:
- Google Colab Free: $0 (just time)
- Google Colab Pro: $10/month
- AWS/GCP GPU: ~$300-500
- Local GPU: $0 (electricity ~$20)

**Choose your adventure and get started! 🎮**
