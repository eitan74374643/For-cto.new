#!/usr/bin/env python3
"""
Example Usage - How to use the trained model

This script demonstrates various ways to use your trained Gemini 3 Pro-level coder
after the training pipeline completes.
"""

import sys
from pathlib import Path


def example_1_gui():
    """Example 1: Using the Gradio GUI (Easiest)"""
    print("=" * 80)
    print("📝 EXAMPLE 1: Using the Gradio GUI")
    print("=" * 80)
    print("""
The easiest way to use your model is through the Gradio interface:

1. Launch the GUI:
   ```bash
   python 5_gui_app.py
   ```

2. Open your browser to: http://localhost:7860

3. Try these example prompts:
   - "Implement a thread-safe LRU cache with O(1) operations"
   - "Create a binary search tree with self-balancing"
   - "Review this code for bugs: [paste your code]"

4. Switch between modes:
   - Fast Mode: Uses the merged model (faster)
   - Reliable Mode: Uses base + adapters (more accurate)

The GUI provides:
- 💬 Chat interface
- 🔄 Easy mode switching
- 📝 Example prompts
- 🧹 Auto GPU cleanup
""")


def example_2_python_api():
    """Example 2: Using the Python API"""
    print("=" * 80)
    print("📝 EXAMPLE 2: Using the Python API")
    print("=" * 80)
    print("""
For programmatic access, use the Python API:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load the merged model
model_path = "models/Final_Merged_Coder_8B"
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Prepare prompt
prompt = '''Task: Implement a thread-safe LRU cache with O(1) operations

Provide a detailed solution with plan, code, and critique.'''

# Generate
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
outputs = model.generate(
    **inputs,
    max_new_tokens=1000,
    temperature=0.7,
    top_p=0.9,
    do_sample=True
)

# Decode and print
response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
print(response)
```

This gives you full control over:
- Generation parameters
- Batch processing
- Custom prompts
- Integration into your pipeline
""")


def example_3_multi_agent():
    """Example 3: Using the Multi-Agent Pipeline"""
    print("=" * 80)
    print("📝 EXAMPLE 3: Using the Multi-Agent Pipeline")
    print("=" * 80)
    print("""
For the full 3-agent experience (Plan → Code → Critique):

```python
from importlib import import_module

# Import the multi-agent module
multi_agent = import_module('4_run_multi_agent')

# Create pipeline (use merged model)
pipeline = multi_agent.create_pipeline(use_merged=True)

# Run full 3-agent pipeline
result = pipeline.run_pipeline(
    "Implement a rate limiter using token bucket algorithm"
)

# Access individual components
print("=" * 80)
print("PLAN:")
print(result['plan'])
print("=" * 80)
print("CODE:")
print(result['code'])
print("=" * 80)
print("CRITIQUE:")
print(result['critique'])
print("=" * 80)

# Or use the formatted output
print(pipeline.format_output(result))

# Cleanup when done
pipeline.cleanup()
```

This approach provides:
- Structured output (plan, code, critique)
- Individual agent access
- Pretty formatting
- Memory management
""")


def example_4_gguf_llama_cpp():
    """Example 4: Using GGUF with llama.cpp"""
    print("=" * 80)
    print("📝 EXAMPLE 4: Using GGUF with llama.cpp")
    print("=" * 80)
    print("""
For edge deployment or CPU usage, use the GGUF model:

**Command Line:**
```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Run inference
./main -m ../models/Final_Gemini3_Coder_8B.gguf \\
       -p "Implement a binary search tree" \\
       -n 500 \\
       --temp 0.7 \\
       --top-p 0.9
```

**As a Server:**
```bash
# Start llama.cpp server
./server -m ../models/Final_Gemini3_Coder_8B.gguf \\
         --host 0.0.0.0 \\
         --port 8080 \\
         -ngl 35  # Number of GPU layers (adjust for your GPU)

# Then make HTTP requests
curl http://localhost:8080/completion \\
  -H "Content-Type: application/json" \\
  -d '{
    "prompt": "Implement a LRU cache",
    "n_predict": 500,
    "temperature": 0.7
  }'
```

**Python (llama-cpp-python):**
```python
from llama_cpp import Llama

# Load GGUF model
llm = Llama(
    model_path="models/Final_Gemini3_Coder_8B.gguf",
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=35  # Adjust based on GPU
)

# Generate
output = llm(
    "Implement a thread-safe queue",
    max_tokens=500,
    temperature=0.7,
    top_p=0.9
)

print(output['choices'][0]['text'])
```

Benefits:
- Small size (~4GB vs ~16GB)
- CPU compatible
- Fast inference
- Low memory usage
""")


def example_5_separate_adapters():
    """Example 5: Using Adapters Separately"""
    print("=" * 80)
    print("📝 EXAMPLE 5: Using Individual Adapters")
    print("=" * 80)
    print("""
For maximum flexibility, use adapters individually:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import torch

# Load base model
base_model = AutoModelForCausalLM.from_pretrained(
    "unsloth/Meta-Llama-3.1-8B-Instruct",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("unsloth/Meta-Llama-3.1-8B-Instruct")

# Load planner adapter
planner = PeftModel.from_pretrained(base_model, "models/lora_planner")

# Use planner
prompt = "Plan how to implement a LRU cache"
inputs = tokenizer(prompt, return_tensors="pt").to(planner.device)
outputs = planner.generate(**inputs, max_new_tokens=300)
plan = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("PLAN:", plan)

# Switch to coder adapter
coder = PeftModel.from_pretrained(base_model, "models/lora_coder")
prompt = f"Based on this plan: {plan}\\n\\nImplement the code:"
inputs = tokenizer(prompt, return_tensors="pt").to(coder.device)
outputs = coder.generate(**inputs, max_new_tokens=600)
code = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("CODE:", code)

# Switch to critic adapter
critic = PeftModel.from_pretrained(base_model, "models/lora_critic")
prompt = f"Review this code:\\n{code}\\n\\nProvide a critique:"
inputs = tokenizer(prompt, return_tensors="pt").to(critic.device)
outputs = critic.generate(**inputs, max_new_tokens=400)
critique = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("CRITIQUE:", critique)
```

This allows:
- Fine-grained control
- Custom agent combinations
- Adapter experimentation
- Memory efficiency
""")


def example_6_batch_processing():
    """Example 6: Batch Processing"""
    print("=" * 80)
    print("📝 EXAMPLE 6: Batch Processing")
    print("=" * 80)
    print("""
Process multiple coding tasks in batch:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "models/Final_Merged_Coder_8B",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("models/Final_Merged_Coder_8B")

# Prepare batch of tasks
tasks = [
    "Implement a binary search tree",
    "Create a thread-safe queue",
    "Design a rate limiter",
    "Build a LRU cache"
]

# Process batch
results = []
for task in tasks:
    prompt = f"Task: {task}\\n\\nProvide plan, code, and critique."
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    outputs = model.generate(
        **inputs,
        max_new_tokens=1000,
        temperature=0.7
    )
    
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    results.append({
        'task': task,
        'response': response
    })
    
    # Clear cache between generations
    torch.cuda.empty_cache()

# Save results
import json
with open('batch_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"Processed {len(results)} tasks")
```

Use cases:
- Code review pipeline
- Automated refactoring
- Documentation generation
- Test case creation
""")


def example_7_custom_prompts():
    """Example 7: Custom Prompt Engineering"""
    print("=" * 80)
    print("📝 EXAMPLE 7: Custom Prompt Engineering")
    print("=" * 80)
    print("""
Craft effective prompts for best results:

**1. Structured Prompts:**
```python
prompt = '''Task: Implement a thread-safe LRU cache

Requirements:
- O(1) get and put operations
- Thread-safe using appropriate locking
- Generic type support
- Comprehensive error handling
- Unit tests included

Provide:
1. Design plan with data structures
2. Complete implementation
3. Critical review of edge cases'''
```

**2. Code Review Prompts:**
```python
code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
'''

prompt = f'''Review this code for:
1. Time/space complexity
2. Potential bugs
3. Edge cases
4. Optimization opportunities
5. Best practices

Code:
{code}

Provide detailed critique and improved version.'''
```

**3. Refactoring Prompts:**
```python
prompt = '''Refactor this code to follow SOLID principles:

[paste code here]

Provide:
1. Analysis of current issues
2. Refactored version
3. Explanation of improvements'''
```

**4. Algorithm Design Prompts:**
```python
prompt = '''Design an algorithm to solve:

Problem: Find the longest increasing subsequence in an array

Constraints:
- Time complexity: O(n log n) or better
- Space complexity: O(n) or better
- Handle negative numbers
- Handle duplicates

Provide:
1. Algorithm approach and rationale
2. Implementation with comments
3. Complexity analysis'''
```

Tips:
- Be specific about requirements
- Request structured output
- Specify complexity constraints
- Ask for explanations
- Include test cases
""")


def example_8_integration():
    """Example 8: Integration Examples"""
    print("=" * 80)
    print("📝 EXAMPLE 8: Integration into Applications")
    print("=" * 80)
    print("""
Integrate the model into your applications:

**1. FastAPI Service:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# Load model at startup
model = None
tokenizer = None

@app.on_event("startup")
async def load_model():
    global model, tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        "models/Final_Merged_Coder_8B",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("models/Final_Merged_Coder_8B")

class CodeRequest(BaseModel):
    task: str
    max_tokens: int = 1000

@app.post("/generate")
async def generate_code(request: CodeRequest):
    inputs = tokenizer(request.task, return_tensors="pt").to(model.device)
    outputs = model.generate(**inputs, max_new_tokens=request.max_tokens)
    response = tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
    return {"response": response}
```

**2. VS Code Extension:**
```javascript
// Call your API from VS Code extension
const axios = require('axios');

async function generateCode(task) {
    const response = await axios.post('http://localhost:8000/generate', {
        task: task,
        max_tokens: 1000
    });
    return response.data.response;
}
```

**3. CLI Tool:**
```python
import click
from transformers import AutoModelForCausalLM, AutoTokenizer

@click.command()
@click.argument('task')
@click.option('--max-tokens', default=1000)
def generate(task, max_tokens):
    model = AutoModelForCausalLM.from_pretrained("models/Final_Merged_Coder_8B")
    tokenizer = AutoTokenizer.from_pretrained("models/Final_Merged_Coder_8B")
    
    inputs = tokenizer(task, return_tensors="pt")
    outputs = model.generate(**inputs, max_new_tokens=max_tokens)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    click.echo(response)

if __name__ == '__main__':
    generate()
```

**4. Slack Bot:**
```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app = App(token="your-token")

@app.message("!code")
def handle_code_request(message, say):
    task = message['text'].replace('!code', '').strip()
    response = generate_code(task)  # Your generation function
    say(f"```\\n{response}\\n```")

if __name__ == "__main__":
    handler = SocketModeHandler(app, "your-app-token")
    handler.start()
```
""")


def main():
    """Main function - display all examples"""
    print("\n" + "=" * 80)
    print("🎓 EXAMPLE USAGE GUIDE")
    print("   How to use your trained Gemini 3 Pro-level coder")
    print("=" * 80)
    print("""
This guide shows 8 different ways to use your trained model:

1. Gradio GUI (easiest)
2. Python API (most flexible)
3. Multi-Agent Pipeline (structured)
4. GGUF with llama.cpp (edge deployment)
5. Individual Adapters (experimental)
6. Batch Processing (production)
7. Custom Prompts (best results)
8. Integration Examples (real-world)

Note: Examples assume training is complete and models exist in models/ directory.
""")
    
    try:
        example_1_gui()
        input("\\nPress Enter to continue...")
        
        example_2_python_api()
        input("\\nPress Enter to continue...")
        
        example_3_multi_agent()
        input("\\nPress Enter to continue...")
        
        example_4_gguf_llama_cpp()
        input("\\nPress Enter to continue...")
        
        example_5_separate_adapters()
        input("\\nPress Enter to continue...")
        
        example_6_batch_processing()
        input("\\nPress Enter to continue...")
        
        example_7_custom_prompts()
        input("\\nPress Enter to continue...")
        
        example_8_integration()
        
        print("\n" + "=" * 80)
        print("✅ END OF EXAMPLES")
        print("=" * 80)
        print("""
For more information:
- README.md - Full documentation
- QUICKSTART.md - Getting started
- PROJECT_STRUCTURE.md - Architecture details

Happy coding! 🚀
""")
        
    except KeyboardInterrupt:
        print("\\n\\n👋 Examples interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()
