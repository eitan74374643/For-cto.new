# 📁 Project Structure & File Relationships

## 🎯 Execution Flow

```
START HERE
    ↓
┌──────────────────────────────────┐
│  0_master_controller.py          │ ← THE ONLY SCRIPT YOU RUN
│  (The Brain)                     │
└──────────────────────────────────┘
    ↓
    ├─→ Environment Detection (Colab vs Local)
    ├─→ Google Drive Mount (if Colab)
    ├─→ GPU Verification
    ↓
┌──────────────────────────────────┐
│  Step 1: Dataset Generation      │
│  1_generate_massive_dataset.py   │
│  - Creates 15k+ samples          │
│  - Uses Chain of Thought         │
│  - Saves incrementally           │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  Step 2: Adapter Training        │
│  2_train_three_adapters.py       │
│  - Trains lora_planner           │
│  - Trains lora_coder             │
│  - Trains lora_critic            │
│  - Auto-resume from checkpoints  │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  Step 3: Model Merging           │
│  3_merge_final_product.py        │
│  - Merges all 3 adapters         │
│  - Creates unified model         │
│  - Generates README              │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  Step 4: Quantization            │
│  6_quantize_for_deployment.py    │
│  - Converts to GGUF              │
│  - Q4_K_M quantization           │
│  - ~4GB output                   │
└──────────────────────────────────┘
    ↓
┌──────────────────────────────────┐
│  Step 5: GUI Launch              │
│  5_gui_app.py                    │
│  - Gradio interface              │
│  - Uses 4_run_multi_agent.py     │
│  - Auto GPU cleanup              │
└──────────────────────────────────┘
    ↓
  READY TO USE! 🎉
```

## 📂 File Descriptions

### Core Scripts (8 Files)

#### 1. `0_master_controller.py` (The Brain) 🧠
**Purpose**: Orchestrates the entire 15-day pipeline  
**When to Run**: This is the ONLY script you need to run manually  
**What It Does**:
- Detects environment (Colab vs Local)
- Mounts Google Drive if on Colab
- Verifies GPU availability
- Runs each step in sequence
- Handles crashes with retry logic
- Only launches GUI after GGUF exists

**Key Functions**:
```python
detect_environment()    # Colab or Local?
setup_environment()     # Mount Drive / Set paths
check_gpu()            # CUDA available?
run_script()           # Execute with retry
run_pipeline()         # Main orchestration
```

**Safety Features**:
- ✅ 5 retry attempts per step
- ✅ 60-second delay between retries
- ✅ Comprehensive logging
- ✅ Graceful error handling

---

#### 2. `1_generate_massive_dataset.py` (The Generator) 📚
**Purpose**: Creates 15,000+ high-quality training examples  
**When It Runs**: Automatically by master controller (Step 1)  
**What It Does**:
- Loads Llama-3.1-8B-Instruct using Unsloth
- Generates Chain of Thought examples (Plan → Code → Critique)
- Validates code syntax before saving
- Saves incrementally (no data loss)
- Creates `data/training_data.jsonl`

**Key Functions**:
```python
load_model()              # Load Llama-3.1-8B with Unsloth
get_gemini_system_prompt() # Gemini 3 Pro persona
generate_coding_tasks()   # 100+ diverse tasks
validate_code()           # Parse Python syntax
generate_sample()         # Single CoT example
save_sample()            # Append to JSONL
generate_dataset()       # Main loop
```

**Output Format**:
```json
{
  "task": "Implement a LRU cache...",
  "response": "PLAN: ... CODE: ... CRITIQUE: ...",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Safety Features**:
- ✅ Saves after every sample
- ✅ Resume from existing count
- ✅ Code validation filter
- ✅ GPU memory cleanup every 50 samples

---

#### 3. `2_train_three_adapters.py` (The Trainer) 🎓
**Purpose**: Trains 3 separate LoRA adapters  
**When It Runs**: Automatically by master controller (Step 2)  
**What It Does**:
- Trains `lora_planner` (planning specialist)
- Trains `lora_coder` (coding specialist)
- Trains `lora_critic` (review specialist)
- Saves checkpoints every 2 hours
- Auto-resumes from checkpoints

**Key Functions**:
```python
load_dataset()            # Load training_data.jsonl
prepare_training_data()   # Split for each adapter
format_for_training()     # Format as instruction-tuning
train_adapter()          # Train single adapter
train_all_adapters()     # Main loop
```

**Training Config**:
```python
# LoRA Settings
r=16                     # Rank
lora_alpha=16           # Scaling
lora_dropout=0.05       # Regularization

# Training Settings
per_device_train_batch_size=2
gradient_accumulation_steps=4
max_steps=1000
learning_rate=2e-4
save_steps=250          # Checkpoint every 250 steps
```

**Output Structure**:
```
models/
├── lora_planner/
│   ├── adapter_config.json
│   ├── adapter_model.bin
│   └── ...
├── lora_coder/
│   └── ...
└── lora_critic/
    └── ...
```

**Safety Features**:
- ✅ Checkpoint every 2 hours
- ✅ Auto-resume from latest checkpoint
- ✅ GPU cleanup between adapters
- ✅ Progress logging every 10 steps

---

#### 4. `3_merge_final_product.py` (The Merger) 🔀
**Purpose**: Merge all 3 adapters into one unified model  
**When It Runs**: Automatically by master controller (Step 3)  
**What It Does**:
- Loads base Llama-3.1-8B-Instruct
- Sequentially merges each adapter
- Saves as `Final_Merged_Coder_8B`
- Creates comprehensive README

**Key Functions**:
```python
verify_adapters()     # Check all exist
merge_adapters()      # Sequential merge
create_readme()       # Documentation
run()                # Main execution
```

**Merge Strategy**:
```
Base Model (16GB)
    ↓
+ lora_planner (200MB)
    ↓
= Intermediate Model 1
    ↓
+ lora_coder (200MB)
    ↓
= Intermediate Model 2
    ↓
+ lora_critic (200MB)
    ↓
= Final_Merged_Coder_8B (16GB)
```

**Output**:
```
models/Final_Merged_Coder_8B/
├── config.json
├── model-00001-of-00004.safetensors
├── model-00002-of-00004.safetensors
├── model-00003-of-00004.safetensors
├── model-00004-of-00004.safetensors
├── tokenizer.json
├── tokenizer_config.json
└── README.md
```

---

#### 5. `4_run_multi_agent.py` (The Logic Core) 🤖
**Purpose**: Helper library for multi-agent pipeline  
**When It Runs**: Imported by GUI and other scripts  
**What It Does**:
- Loads merged model OR base + adapters
- Provides unified interface for generation
- Implements 3-agent pipeline (Plan → Code → Critique)
- Dynamic adapter switching

**Key Classes**:
```python
class MultiAgentPipeline:
    load_models()              # Load model(s)
    generate()                 # Single generation
    run_pipeline()             # Full 3-agent flow
    format_output()            # Pretty formatting
    cleanup()                  # Free GPU memory
```

**Usage Example**:
```python
from importlib import import_module
multi_agent = import_module('4_run_multi_agent')

# Create pipeline
pipeline = multi_agent.create_pipeline(use_merged=True)

# Run full pipeline
result = pipeline.run_pipeline("Implement a binary search tree")

# Access results
print(result['plan'])
print(result['code'])
print(result['critique'])
```

**Two Modes**:
1. **Fast Mode** (`use_merged=True`): Single merged model
2. **Reliable Mode** (`use_merged=False`): Base + dynamic adapter switching

---

#### 6. `5_gui_app.py` (The Interface) 🎨
**Purpose**: Gradio chat interface for interacting with model  
**When It Runs**: Automatically after GGUF creation (Step 5)  
**What It Does**:
- Creates beautiful Gradio UI
- Two modes: Fast (merged) vs Reliable (adapters)
- Processes user queries
- Auto GPU cleanup on shutdown

**Key Classes**:
```python
class CoderGUI:
    verify_models()           # Check models exist
    load_pipeline()           # Load model
    process_message()         # Handle chat
    create_interface()        # Build Gradio UI
    launch()                 # Start server
    cleanup()                # Free GPU memory
```

**Interface Features**:
- 💬 Chat interface
- 🔄 Mode switching (Fast/Reliable)
- 📝 Example prompts
- 🎨 Beautiful UI with custom CSS
- 🧹 Auto cleanup on shutdown

**Access**:
- Local: http://localhost:7860
- Colab: Use `--share` flag for public URL

**Smart Detection**:
```python
if "implement" in message.lower():
    # Use full 3-agent pipeline
    result = pipeline.run_pipeline(message)
else:
    # Simple generation
    result = pipeline.generate(message)
```

---

#### 7. `6_quantize_for_deployment.py` (The Deployment) 📦
**Purpose**: Convert merged model to GGUF for efficient deployment  
**When It Runs**: Automatically by master controller (Step 4)  
**What It Does**:
- Converts to FP16 first
- Quantizes to Q4_K_M GGUF
- Reduces from ~16GB to ~4GB
- Creates deployment documentation

**Key Functions**:
```python
verify_merged_model()      # Check input exists
convert_to_fp16()         # FP16 conversion
quantize_to_gguf()        # GGUF quantization
create_deployment_info()  # Usage docs
cleanup_temp()            # Remove temp files
```

**Quantization Options**:
- Q4_K_M (default): ~4GB, great quality
- Q3_K_M: ~3GB, good quality
- Q5_K_M: ~5.5GB, excellent quality
- Q8_0: ~8GB, near-perfect quality

**Output**:
```
models/
├── Final_Gemini3_Coder_8B.gguf (4.2GB)
└── Final_Gemini3_Coder_8B.gguf.info.md
```

**Fallback Strategy**:
If llama.cpp not available:
1. Try llama-cpp-python
2. Create FP16 placeholder
3. Log instructions for manual quantization

---

### Supporting Files

#### 8. `requirements.txt`
**Purpose**: Python dependencies  
**Contents**:
```
torch>=2.0.0
unsloth[colab-new]
peft>=0.5.0
bitsandbytes>=0.41.0
transformers>=4.36.0
trl>=0.7.4
gradio>=4.0.0
llama-cpp-python>=0.2.0
tensorboard>=2.14.0
datasets>=2.14.0
huggingface_hub>=0.19.0
accelerate>=0.24.0
xformers
```

#### 9. `README.md`
**Purpose**: Comprehensive project documentation  
**Sections**:
- Project overview
- Features
- Quick start
- System requirements
- Training methodology
- Troubleshooting
- Deployment options

#### 10. `QUICKSTART.md`
**Purpose**: Simplified quick start guide  
**Sections**:
- One-command start
- Pre-flight checklist
- Timeline expectations
- Common issues
- Pro tips

#### 11. `.gitignore`
**Purpose**: Exclude large files from git  
**Excludes**:
- Models and checkpoints
- Training data
- Logs
- Temp files
- Python cache

---

## 🗂️ Generated Directory Structure

```
AI_Project_Master/                    # Root (on Drive or local)
│
├── 0_master_controller.py            # Main script
├── 1_generate_massive_dataset.py     # Dataset generator
├── 2_train_three_adapters.py         # Trainer
├── 3_merge_final_product.py          # Merger
├── 4_run_multi_agent.py              # Pipeline logic
├── 5_gui_app.py                      # GUI interface
├── 6_quantize_for_deployment.py      # Quantizer
├── requirements.txt                  # Dependencies
├── README.md                         # Documentation
├── QUICKSTART.md                     # Quick guide
├── PROJECT_STRUCTURE.md              # This file
├── .gitignore                        # Git exclusions
│
├── data/                             # Training data
│   ├── training_data.jsonl           # 15k+ samples (~500MB)
│   └── ...
│
├── models/                           # Trained models
│   ├── lora_planner/                 # Planner adapter (~200MB)
│   │   ├── adapter_config.json
│   │   ├── adapter_model.bin
│   │   └── ...
│   │
│   ├── lora_coder/                   # Coder adapter (~200MB)
│   │   └── ...
│   │
│   ├── lora_critic/                  # Critic adapter (~200MB)
│   │   └── ...
│   │
│   ├── Final_Merged_Coder_8B/        # Merged model (~16GB)
│   │   ├── config.json
│   │   ├── model-*.safetensors
│   │   ├── tokenizer.json
│   │   └── README.md
│   │
│   ├── Final_Gemini3_Coder_8B.gguf   # Quantized GGUF (~4GB)
│   └── Final_Gemini3_Coder_8B.gguf.info.md
│
├── checkpoints/                      # Training checkpoints
│   ├── lora_planner/
│   │   ├── checkpoint-250/
│   │   ├── checkpoint-500/
│   │   └── ...
│   ├── lora_coder/
│   │   └── ...
│   └── lora_critic/
│       └── ...
│
└── logs/                             # Log files
    ├── master_controller.log
    ├── dataset_generation.log
    ├── training.log
    ├── merging.log
    ├── quantization.log
    └── gui_app.log
```

## 📊 File Size Reference

| File/Directory | Size | Stage |
|----------------|------|-------|
| `training_data.jsonl` | ~500MB | After Step 1 |
| `lora_planner/` | ~200MB | After Step 2 |
| `lora_coder/` | ~200MB | After Step 2 |
| `lora_critic/` | ~200MB | After Step 2 |
| `Final_Merged_Coder_8B/` | ~16GB | After Step 3 |
| `Final_Gemini3_Coder_8B.gguf` | ~4GB | After Step 4 |
| **Total Project Size** | **~21GB** | Complete |

## 🔄 Data Flow

```
Llama-3.1-8B-Instruct (Base)
    ↓
1_generate_massive_dataset.py
    ↓
training_data.jsonl (15k samples)
    ↓
2_train_three_adapters.py
    ↓
┌─────────────┬─────────────┬─────────────┐
│  Planner    │   Coder     │   Critic    │
│  Adapter    │   Adapter   │   Adapter   │
└─────────────┴─────────────┴─────────────┘
    ↓
3_merge_final_product.py
    ↓
Final_Merged_Coder_8B (Unified Model)
    ↓
6_quantize_for_deployment.py
    ↓
Final_Gemini3_Coder_8B.gguf
    ↓
5_gui_app.py (uses 4_run_multi_agent.py)
    ↓
User Interface 🎨
```

## 🎯 Import Dependencies

```
0_master_controller.py
    ↓ (subprocess)
    ├─→ 1_generate_massive_dataset.py
    ├─→ 2_train_three_adapters.py
    ├─→ 3_merge_final_product.py
    ├─→ 6_quantize_for_deployment.py
    └─→ 5_gui_app.py
            ↓ (import)
            └─→ 4_run_multi_agent.py
```

## 🚀 Execution Order

1. **0_master_controller.py** (YOU RUN THIS)
2. → **1_generate_massive_dataset.py** (auto)
3. → **2_train_three_adapters.py** (auto)
4. → **3_merge_final_product.py** (auto)
5. → **6_quantize_for_deployment.py** (auto)
6. → **5_gui_app.py** (auto, uses **4_run_multi_agent.py**)

## 💾 State Persistence

Each script checks for existing outputs:
- ✅ Dataset exists? Skip generation
- ✅ Adapters exist? Skip training
- ✅ Merged model exists? Skip merging
- ✅ GGUF exists? Skip quantization
- ✅ Checkpoint exists? Resume training

This means you can:
- Stop and resume anytime
- Restart after crashes
- Re-run safely without losing progress

---

**Now you understand the complete architecture! 🎉**

**Ready to start? Just run:**
```bash
python 0_master_controller.py
```
