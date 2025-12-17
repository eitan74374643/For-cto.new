#!/usr/bin/env python3
"""
Multi-Agent Pipeline - The Logic Core
Helper functions for running the 3-agent flow (Plan → Code → Critique)
"""

import logging
from pathlib import Path
import torch

logger = logging.getLogger(__name__)


class MultiAgentPipeline:
    """
    Orchestrates the 3-agent coding pipeline
    Dynamically loads and switches between adapters
    """
    
    def __init__(self, project_path=None, use_merged=False):
        """
        Initialize the multi-agent pipeline
        
        Args:
            project_path: Path to project directory
            use_merged: If True, use merged model. If False, use base + adapters
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.models_path = self.project_path / "models"
        self.use_merged = use_merged
        
        self.base_model = None
        self.tokenizer = None
        self.adapters = {}
        
        self.adapter_names = {
            "planner": "lora_planner",
            "coder": "lora_coder",
            "critic": "lora_critic"
        }
    
    def load_models(self):
        """Load base model and adapters"""
        try:
            from unsloth import FastLanguageModel
            
            if self.use_merged:
                # Load merged model
                logger.info("📥 Loading merged model...")
                merged_path = self.models_path / "Final_Merged_Coder_8B"
                
                self.base_model, self.tokenizer = FastLanguageModel.from_pretrained(
                    model_name=str(merged_path),
                    max_seq_length=2048,
                    dtype=None,
                    load_in_4bit=True,
                )
                
                FastLanguageModel.for_inference(self.base_model)
                logger.info("✅ Merged model loaded")
                
            else:
                # Load base model + adapters
                logger.info("📥 Loading base model...")
                self.base_model, self.tokenizer = FastLanguageModel.from_pretrained(
                    model_name="unsloth/Meta-Llama-3.1-8B-Instruct",
                    max_seq_length=2048,
                    dtype=None,
                    load_in_4bit=True,
                )
                
                logger.info("📥 Loading adapters...")
                from peft import PeftModel
                
                for agent_name, adapter_name in self.adapter_names.items():
                    adapter_path = self.models_path / adapter_name
                    if adapter_path.exists():
                        logger.info(f"   Loading {adapter_name}...")
                        adapter_model = PeftModel.from_pretrained(
                            self.base_model,
                            str(adapter_path),
                            adapter_name=agent_name
                        )
                        self.adapters[agent_name] = adapter_model
                    else:
                        logger.warning(f"⚠️ Adapter not found: {adapter_name}")
                
                logger.info("✅ Base model and adapters loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading models: {e}", exc_info=True)
            return False
    
    def generate(self, prompt, agent=None, max_tokens=500):
        """
        Generate response using specified agent
        
        Args:
            prompt: Input prompt
            agent: Which agent to use ('planner', 'coder', 'critic', or None for merged)
            max_tokens: Maximum tokens to generate
        """
        try:
            # Select model
            if self.use_merged or agent is None:
                model = self.base_model
            else:
                if agent in self.adapters:
                    model = self.adapters[agent]
                    # Set active adapter
                    model.set_adapter(agent)
                else:
                    logger.warning(f"⚠️ Agent '{agent}' not found, using base model")
                    model = self.base_model
            
            # Prepare input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=2048
            ).to(model.device)
            
            # Generate
            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_tokens,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True,
                    repetition_penalty=1.1
                )
            
            # Decode
            response = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"❌ Error generating response: {e}")
            return None
    
    def run_pipeline(self, task):
        """
        Run the complete 3-agent pipeline
        
        Args:
            task: Coding task to solve
            
        Returns:
            dict with plan, code, and critique
        """
        try:
            result = {
                "task": task,
                "plan": None,
                "code": None,
                "critique": None
            }
            
            # Step 1: Planning
            logger.info("🧠 Step 1: Planning...")
            plan_prompt = f"""Task: {task}

Provide a detailed plan to solve this problem. Break it down into logical steps, consider edge cases, and identify optimal algorithms and data structures."""
            
            result["plan"] = self.generate(plan_prompt, agent="planner", max_tokens=400)
            logger.info("✅ Plan generated")
            
            # Step 2: Coding
            logger.info("💻 Step 2: Coding...")
            code_prompt = f"""Task: {task}

Plan: {result["plan"]}

Implement the solution with clean, efficient, well-documented code. Include error handling and validation."""
            
            result["code"] = self.generate(code_prompt, agent="coder", max_tokens=800)
            logger.info("✅ Code generated")
            
            # Step 3: Critique
            logger.info("🔍 Step 3: Critique...")
            critique_prompt = f"""Task: {task}

Code:
{result["code"]}

Provide a critical review of this code. Identify:
1. Potential bugs or errors
2. Edge cases not handled
3. Performance optimization opportunities
4. Code quality improvements
5. Security concerns

Be thorough and specific."""
            
            result["critique"] = self.generate(critique_prompt, agent="critic", max_tokens=600)
            logger.info("✅ Critique generated")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error in pipeline: {e}")
            return None
    
    def format_output(self, result):
        """Format pipeline result for display"""
        if not result:
            return "Error: Pipeline failed"
        
        output = f"""## Task
{result['task']}

## 🧠 PLAN
{result['plan']}

## 💻 CODE
{result['code']}

## 🔍 CRITIQUE
{result['critique']}
"""
        return output
    
    def cleanup(self):
        """Free GPU memory"""
        if self.base_model:
            del self.base_model
        if self.adapters:
            del self.adapters
        torch.cuda.empty_cache()


def create_pipeline(project_path=None, use_merged=False):
    """
    Factory function to create and initialize a pipeline
    
    Args:
        project_path: Path to project directory
        use_merged: If True, use merged model. If False, use base + adapters
    
    Returns:
        Initialized MultiAgentPipeline
    """
    pipeline = MultiAgentPipeline(project_path, use_merged)
    
    if pipeline.load_models():
        return pipeline
    else:
        return None


# Example usage
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test with merged model
    logger.info("Testing multi-agent pipeline...")
    
    pipeline = create_pipeline(use_merged=True)
    
    if pipeline:
        result = pipeline.run_pipeline(
            "Implement a thread-safe LRU cache with O(1) get and put operations"
        )
        
        if result:
            print("\n" + "="*80)
            print(pipeline.format_output(result))
            print("="*80)
        
        pipeline.cleanup()
    else:
        logger.error("Failed to initialize pipeline")
