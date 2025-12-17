#!/usr/bin/env python3
"""
Training Script - The Trainer
Trains 3 distinct LoRA adapters: lora_planner, lora_coder, lora_critic
"""

import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import torch
from datasets import Dataset
from tqdm import tqdm

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('training.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AdapterTrainer:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.data_path = self.project_path / "data" / "training_data.jsonl"
        self.models_path = self.project_path / "models"
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        self.checkpoints_path = self.project_path / "checkpoints"
        self.checkpoints_path.mkdir(parents=True, exist_ok=True)
        
        self.adapters = ["lora_planner", "lora_coder", "lora_critic"]
        
    def load_dataset(self):
        """Load training data from JSONL"""
        try:
            logger.info(f"📂 Loading dataset from {self.data_path}")
            
            if not self.data_path.exists():
                logger.error(f"❌ Dataset not found: {self.data_path}")
                return None
            
            samples = []
            with open(self.data_path, 'r') as f:
                for line in f:
                    samples.append(json.loads(line))
            
            logger.info(f"✅ Loaded {len(samples)} samples")
            return samples
            
        except Exception as e:
            logger.error(f"❌ Error loading dataset: {e}")
            raise
    
    def prepare_training_data(self, samples, adapter_type):
        """
        Prepare training data specific to each adapter type
        
        lora_planner: Focus on planning sections
        lora_coder: Focus on code sections
        lora_critic: Focus on critique sections
        """
        formatted_data = []
        
        for sample in samples:
            task = sample['task']
            response = sample['response']
            
            # Create adapter-specific training examples
            if adapter_type == "lora_planner":
                # Extract planning section
                prompt = f"Task: {task}\n\nProvide a detailed plan to solve this problem. Break it down into logical steps."
                # Try to extract plan from response
                if "PLAN" in response.upper():
                    plan_section = response.split("CODE")[0] if "CODE" in response.upper() else response
                    formatted_data.append({
                        "instruction": prompt,
                        "output": plan_section.strip()
                    })
                else:
                    # Use first third of response
                    words = response.split()
                    plan_section = ' '.join(words[:len(words)//3])
                    formatted_data.append({
                        "instruction": prompt,
                        "output": plan_section.strip()
                    })
                    
            elif adapter_type == "lora_coder":
                # Extract code section
                prompt = f"Task: {task}\n\nImplement the solution with clean, efficient code."
                # Try to extract code from response
                if "```" in response:
                    code_section = response
                    formatted_data.append({
                        "instruction": prompt,
                        "output": code_section.strip()
                    })
                else:
                    # Use middle third
                    words = response.split()
                    code_section = ' '.join(words[len(words)//3:2*len(words)//3])
                    formatted_data.append({
                        "instruction": prompt,
                        "output": code_section.strip()
                    })
                    
            elif adapter_type == "lora_critic":
                # Extract critique section
                prompt = f"Task: {task}\n\nCode:\n{response}\n\nProvide a critical review identifying bugs, edge cases, and improvements."
                # Try to extract critique from response
                if "CRITIQUE" in response.upper():
                    critique_section = response.split("CRITIQUE")[-1] if "CRITIQUE" in response.upper() else response
                    formatted_data.append({
                        "instruction": prompt,
                        "output": critique_section.strip()
                    })
                else:
                    # Use last third
                    words = response.split()
                    critique_section = ' '.join(words[2*len(words)//3:])
                    formatted_data.append({
                        "instruction": prompt,
                        "output": critique_section.strip()
                    })
        
        logger.info(f"✅ Prepared {len(formatted_data)} examples for {adapter_type}")
        return formatted_data
    
    def format_for_training(self, examples):
        """Format examples for instruction tuning"""
        formatted = []
        
        for ex in examples:
            text = f"""### Instruction:
{ex['instruction']}

### Response:
{ex['output']}"""
            formatted.append({"text": text})
        
        return Dataset.from_list(formatted)
    
    def train_adapter(self, adapter_name, train_dataset):
        """Train a single LoRA adapter using Unsloth"""
        try:
            logger.info(f"🚀 Training {adapter_name}...")
            
            from unsloth import FastLanguageModel
            from trl import SFTTrainer
            from transformers import TrainingArguments
            
            # Output path for this adapter
            output_dir = self.models_path / adapter_name
            checkpoint_dir = self.checkpoints_path / adapter_name
            
            # Check for existing checkpoint
            resume_from_checkpoint = None
            if checkpoint_dir.exists() and any(checkpoint_dir.iterdir()):
                logger.info(f"📂 Found existing checkpoint for {adapter_name}")
                # Find the latest checkpoint
                checkpoints = [d for d in checkpoint_dir.iterdir() if d.is_dir()]
                if checkpoints:
                    resume_from_checkpoint = max(checkpoints, key=lambda x: x.stat().st_mtime)
                    logger.info(f"   Resuming from: {resume_from_checkpoint}")
            
            # Load base model
            logger.info("   Loading base model...")
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name="unsloth/Meta-Llama-3.1-8B-Instruct",
                max_seq_length=2048,
                dtype=None,
                load_in_4bit=True,
            )
            
            # Configure LoRA
            logger.info("   Configuring LoRA...")
            model = FastLanguageModel.get_peft_model(
                model,
                r=16,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                               "gate_proj", "up_proj", "down_proj"],
                lora_alpha=16,
                lora_dropout=0.05,
                bias="none",
                use_gradient_checkpointing="unsloth",
                random_state=3407,
            )
            
            # Training arguments
            training_args = TrainingArguments(
                output_dir=str(checkpoint_dir),
                per_device_train_batch_size=2,
                gradient_accumulation_steps=4,
                warmup_steps=100,
                max_steps=1000,
                learning_rate=2e-4,
                fp16=not torch.cuda.is_bf16_supported(),
                bf16=torch.cuda.is_bf16_supported(),
                logging_steps=10,
                save_steps=250,
                save_total_limit=3,
                optim="adamw_8bit",
                weight_decay=0.01,
                lr_scheduler_type="cosine",
                seed=3407,
                report_to="tensorboard",
            )
            
            # Trainer
            logger.info("   Initializing trainer...")
            trainer = SFTTrainer(
                model=model,
                tokenizer=tokenizer,
                train_dataset=train_dataset,
                dataset_text_field="text",
                max_seq_length=2048,
                args=training_args,
            )
            
            # Train
            logger.info(f"   Starting training for {adapter_name}...")
            logger.info(f"   Training samples: {len(train_dataset)}")
            
            trainer.train(resume_from_checkpoint=resume_from_checkpoint)
            
            # Save final adapter
            logger.info(f"   Saving {adapter_name}...")
            model.save_pretrained(str(output_dir))
            tokenizer.save_pretrained(str(output_dir))
            
            logger.info(f"✅ {adapter_name} training complete!")
            logger.info(f"   Saved to: {output_dir}")
            
            # Cleanup
            del model
            del trainer
            torch.cuda.empty_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error training {adapter_name}: {e}", exc_info=True)
            return False
    
    def train_all_adapters(self):
        """Train all three adapters"""
        logger.info("=" * 80)
        logger.info("🎓 TRAINING THREE LORA ADAPTERS")
        logger.info("=" * 80)
        
        # Load dataset
        samples = self.load_dataset()
        if not samples:
            logger.error("❌ Failed to load dataset")
            return False
        
        # Train each adapter
        for adapter_name in self.adapters:
            logger.info(f"\n{'='*80}")
            logger.info(f"📚 Training: {adapter_name}")
            logger.info(f"{'='*80}")
            
            # Check if already trained
            output_dir = self.models_path / adapter_name
            if output_dir.exists() and (output_dir / "adapter_config.json").exists():
                logger.info(f"✅ {adapter_name} already exists. Skipping...")
                continue
            
            # Prepare data for this adapter
            adapter_data = self.prepare_training_data(samples, adapter_name)
            train_dataset = self.format_for_training(adapter_data)
            
            # Train
            success = self.train_adapter(adapter_name, train_dataset)
            
            if not success:
                logger.error(f"❌ Failed to train {adapter_name}")
                return False
            
            # Small delay between adapters
            import time
            time.sleep(5)
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 ALL ADAPTERS TRAINED SUCCESSFULLY!")
        logger.info("=" * 80)
        
        return True


def main():
    """Main entry point"""
    try:
        # Detect project path
        project_path = Path.cwd()
        
        logger.info("=" * 80)
        logger.info("🎓 ADAPTER TRAINING")
        logger.info(f"   Project: {project_path}")
        logger.info("=" * 80)
        
        trainer = AdapterTrainer(project_path)
        success = trainer.train_all_adapters()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Training interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
