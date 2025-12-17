#!/usr/bin/env python3
"""
Dataset Generator - The Generator
Creates 15k+ high-quality coding examples using Chain of Thought methodology.
"""

import os
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
import torch
from tqdm import tqdm
import ast

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('dataset_generation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class DatasetGenerator:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.data_path = self.project_path / "data"
        self.data_path.mkdir(parents=True, exist_ok=True)
        self.output_file = self.data_path / "training_data.jsonl"
        
        self.model = None
        self.tokenizer = None
        self.target_samples = 15000
        self.current_count = 0
        
        # Load existing data count
        if self.output_file.exists():
            with open(self.output_file, 'r') as f:
                self.current_count = sum(1 for _ in f)
            logger.info(f"📊 Found {self.current_count} existing samples")
    
    def load_model(self):
        """Load Llama-3.1-8B-Instruct using Unsloth"""
        try:
            logger.info("🔧 Loading Llama-3.1-8B-Instruct with Unsloth...")
            
            from unsloth import FastLanguageModel
            
            model, tokenizer = FastLanguageModel.from_pretrained(
                model_name="unsloth/Meta-Llama-3.1-8B-Instruct",
                max_seq_length=2048,
                dtype=None,
                load_in_4bit=True,
            )
            
            # Configure for inference
            FastLanguageModel.for_inference(model)
            
            self.model = model
            self.tokenizer = tokenizer
            
            logger.info("✅ Model loaded successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            raise
    
    def get_gemini_system_prompt(self):
        """System prompt that enforces Gemini 3 Pro-level reasoning"""
        return """You are an elite AI coding specialist with Gemini 3 Pro-level capabilities. You excel at:
1. Novel algorithm design with optimal time/space complexity
2. Deep logical reasoning and problem decomposition
3. Self-critical code review and bug detection
4. Clean, production-ready code with edge case handling

When given a coding task, you MUST follow this 3-step Chain of Thought:

**PLAN**: Break down the problem into logical steps. Consider edge cases, optimal algorithms, and data structures.

**CODE**: Implement clean, efficient, well-commented code. Use proper error handling and validation.

**CRITIQUE**: Review your code critically. Identify potential bugs, edge cases, optimization opportunities, and suggest improvements.

Your responses must be thorough, logically sound, and demonstrate expert-level engineering."""
    
    def generate_coding_tasks(self):
        """Generate diverse coding tasks"""
        tasks = [
            # Algorithms
            "Implement a dynamic programming solution for the longest increasing subsequence problem",
            "Create an efficient algorithm to find all anagrams in a string",
            "Design a LRU cache with O(1) operations using a doubly linked list and hash map",
            "Implement Dijkstra's shortest path algorithm with a priority queue",
            "Build a trie data structure for autocomplete functionality",
            "Create a binary search tree with insertion, deletion, and balancing",
            "Implement merge sort with in-place optimization",
            "Design a sliding window algorithm for maximum sum subarray",
            "Build a graph traversal system using both BFS and DFS",
            "Implement the knapsack problem using dynamic programming",
            
            # Data Structures
            "Design a min-heap that supports efficient insertion and deletion",
            "Create a circular buffer with thread-safe operations",
            "Implement a bloom filter for membership testing",
            "Build a segment tree for range queries",
            "Design a union-find data structure with path compression",
            "Create a skip list with logarithmic search time",
            "Implement a B-tree for database indexing",
            "Build a rope data structure for efficient string operations",
            "Design a persistent data structure with structural sharing",
            "Create a quadtree for spatial indexing",
            
            # System Design
            "Design a rate limiter using token bucket algorithm",
            "Implement a distributed cache with consistent hashing",
            "Create a message queue with priority scheduling",
            "Build a load balancer with health checking",
            "Design a URL shortener with collision handling",
            "Implement a file synchronization system",
            "Create a search engine indexer with inverted index",
            "Build a time-series database with compression",
            "Design a recommendation system using collaborative filtering",
            "Implement a distributed locking mechanism",
            
            # Web & APIs
            "Create a REST API with authentication and rate limiting",
            "Build a WebSocket server for real-time chat",
            "Implement GraphQL resolver with data loader pattern",
            "Design a microservice with circuit breaker pattern",
            "Create an API gateway with request routing",
            "Build a OAuth2 authentication server",
            "Implement server-side rendering with caching",
            "Design a content delivery system with edge caching",
            "Create a streaming API for large datasets",
            "Build a webhook delivery system with retries",
            
            # Database & Storage
            "Design a database migration system with rollback support",
            "Implement a query builder with SQL injection prevention",
            "Create a connection pool with automatic scaling",
            "Build a full-text search engine",
            "Design a sharding strategy for horizontal scaling",
            "Implement optimistic locking for concurrent updates",
            "Create a caching layer with cache invalidation",
            "Build a data replication system for high availability",
            "Design a backup and recovery mechanism",
            "Implement a time-travel query system",
            
            # Machine Learning
            "Implement gradient descent optimization from scratch",
            "Create a neural network layer with backpropagation",
            "Build a decision tree classifier with pruning",
            "Design a k-means clustering algorithm",
            "Implement linear regression with regularization",
            "Create a convolutional layer for image processing",
            "Build a word embedding model",
            "Design a reinforcement learning agent",
            "Implement batch normalization for neural networks",
            "Create a attention mechanism for transformers",
            
            # Security
            "Implement AES encryption with proper key management",
            "Create a password hashing system with salt and pepper",
            "Build a CSRF protection middleware",
            "Design a secure session management system",
            "Implement input validation and sanitization",
            "Create a secure file upload handler",
            "Build a XSS prevention system",
            "Design a secret scanning tool for code repositories",
            "Implement certificate pinning for API calls",
            "Create a security audit logging system",
            
            # Concurrency
            "Implement a thread-safe producer-consumer queue",
            "Create a deadlock detection algorithm",
            "Build a parallel merge sort using thread pool",
            "Design a read-write lock with fairness guarantees",
            "Implement a concurrent hash map with lock striping",
            "Create an actor model for concurrent computation",
            "Build a task scheduler with dependency resolution",
            "Design a semaphore-based resource manager",
            "Implement a wait-free queue using atomic operations",
            "Create a parallel map-reduce framework",
            
            # Parsing & Compilation
            "Build a JSON parser with error recovery",
            "Implement a regex engine with backtracking",
            "Create a markdown to HTML converter",
            "Design a SQL query parser",
            "Implement a lexical analyzer for a programming language",
            "Build an abstract syntax tree generator",
            "Create a code formatter with style rules",
            "Design a template engine with variable interpolation",
            "Implement a domain-specific language interpreter",
            "Build a bytecode compiler and virtual machine",
            
            # Testing & Quality
            "Create a property-based testing framework",
            "Implement a mock object generator",
            "Build a code coverage analyzer",
            "Design a fuzzing tool for input testing",
            "Create a performance benchmarking suite",
            "Implement a snapshot testing system",
            "Build a mutation testing framework",
            "Design a continuous integration pipeline",
            "Create a static analysis tool for bug detection",
            "Implement a load testing framework",
        ]
        
        return tasks
    
    def validate_code(self, code_text):
        """Check if code can be parsed (basic validation)"""
        try:
            # Try to parse as Python code
            ast.parse(code_text)
            return True
        except:
            # If it contains code blocks, extract and validate those
            if "```python" in code_text:
                code_blocks = []
                parts = code_text.split("```python")
                for part in parts[1:]:
                    if "```" in part:
                        code_block = part.split("```")[0].strip()
                        code_blocks.append(code_block)
                
                if code_blocks:
                    try:
                        for block in code_blocks:
                            ast.parse(block)
                        return True
                    except:
                        return False
            return False
    
    def generate_sample(self, task):
        """Generate a single Chain of Thought sample"""
        try:
            system_prompt = self.get_gemini_system_prompt()
            user_prompt = f"Task: {task}\n\nProvide your response following the PLAN → CODE → CRITIQUE structure."
            
            # Format for Llama 3.1 Instruct
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            inputs = self.tokenizer.apply_chat_template(
                messages,
                tokenize=True,
                add_generation_prompt=True,
                return_tensors="pt"
            ).to(self.model.device)
            
            # Generate
            outputs = self.model.generate(
                inputs,
                max_new_tokens=1500,
                temperature=0.8,
                top_p=0.95,
                do_sample=True,
                repetition_penalty=1.1
            )
            
            # Decode
            response = self.tokenizer.decode(outputs[0][inputs.shape[1]:], skip_special_tokens=True)
            
            # Validate response has all sections
            has_plan = "PLAN" in response.upper() or "plan" in response.lower()
            has_code = "CODE" in response.upper() or "```" in response
            has_critique = "CRITIQUE" in response.upper() or "critique" in response.lower()
            
            if has_plan and has_code and has_critique:
                # Basic code validation
                if self.validate_code(response):
                    return {
                        "task": task,
                        "response": response,
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    logger.debug(f"⚠️ Code validation failed for task: {task[:50]}...")
                    return None
            else:
                logger.debug(f"⚠️ Incomplete response for task: {task[:50]}...")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error generating sample: {e}")
            return None
    
    def save_sample(self, sample):
        """Save a single sample to JSONL (append mode)"""
        try:
            with open(self.output_file, 'a') as f:
                f.write(json.dumps(sample) + '\n')
            return True
        except Exception as e:
            logger.error(f"❌ Error saving sample: {e}")
            return False
    
    def generate_dataset(self):
        """Main generation loop"""
        logger.info(f"🎯 Target: {self.target_samples} samples")
        logger.info(f"📊 Current: {self.current_count} samples")
        
        if self.current_count >= self.target_samples:
            logger.info("✅ Dataset already complete!")
            return True
        
        remaining = self.target_samples - self.current_count
        logger.info(f"🔄 Generating {remaining} more samples...")
        
        # Load model
        self.load_model()
        
        # Generate tasks
        base_tasks = self.generate_coding_tasks()
        tasks = []
        
        # Expand tasks with variations
        variations = [
            "Implement {} with comprehensive error handling",
            "Design {} optimized for production use",
            "Create {} with detailed documentation",
            "Build {} with unit tests",
            "Develop {} considering edge cases",
        ]
        
        for task in base_tasks:
            tasks.append(task)
            for variation in variations[:2]:  # Add 2 variations per task
                tasks.append(variation.format(task.lower()))
        
        # Ensure we have enough unique tasks
        while len(tasks) < remaining:
            tasks.extend(base_tasks)
        
        # Generate samples
        successful = 0
        attempts = 0
        max_attempts = remaining * 3  # Allow for failures
        
        with tqdm(total=remaining, desc="Generating samples") as pbar:
            while successful < remaining and attempts < max_attempts:
                task = tasks[attempts % len(tasks)]
                attempts += 1
                
                sample = self.generate_sample(task)
                
                if sample:
                    if self.save_sample(sample):
                        successful += 1
                        self.current_count += 1
                        pbar.update(1)
                        
                        # Log progress every 100 samples
                        if successful % 100 == 0:
                            logger.info(f"✅ Generated {successful}/{remaining} samples")
                
                # Free memory periodically
                if attempts % 50 == 0:
                    torch.cuda.empty_cache()
        
        final_count = self.current_count
        logger.info(f"🎉 Dataset generation complete!")
        logger.info(f"   Total samples: {final_count}")
        logger.info(f"   Output file: {self.output_file}")
        
        return final_count >= self.target_samples


def main():
    """Main entry point"""
    try:
        # Detect project path
        project_path = Path.cwd()
        
        # Check if we're in a subdirectory structure
        if (Path.cwd().parent / "data").exists():
            project_path = Path.cwd().parent
        
        logger.info("=" * 80)
        logger.info("📚 DATASET GENERATOR")
        logger.info(f"   Project: {project_path}")
        logger.info("=" * 80)
        
        generator = DatasetGenerator(project_path)
        success = generator.generate_dataset()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
