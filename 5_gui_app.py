#!/usr/bin/env python3
"""
GUI Application - The Interface
Gradio chat interface for interacting with the trained model
"""

import os
import logging
import sys
from pathlib import Path
import torch
import signal
import atexit

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gui_app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class CoderGUI:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.models_path = self.project_path / "models"
        
        self.pipeline = None
        self.mode = "fast"  # "fast" or "reliable"
        
        # Register cleanup handlers
        atexit.register(self.cleanup)
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("\n🛑 Shutdown signal received")
        self.cleanup()
        sys.exit(0)
    
    def cleanup(self):
        """Free GPU memory on shutdown"""
        try:
            logger.info("🧹 Cleaning up GPU memory...")
            
            if self.pipeline:
                self.pipeline.cleanup()
            
            torch.cuda.empty_cache()
            logger.info("✅ Cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def verify_models(self):
        """Verify required models exist"""
        logger.info("🔍 Verifying models...")
        
        # Check for merged model
        merged_path = self.models_path / "Final_Merged_Coder_8B"
        has_merged = merged_path.exists() and (merged_path / "config.json").exists()
        
        # Check for GGUF
        gguf_path = self.models_path / "Final_Gemini3_Coder_8B.gguf"
        has_gguf = gguf_path.exists()
        
        # Check for adapters
        adapters = ["lora_planner", "lora_coder", "lora_critic"]
        has_adapters = all(
            (self.models_path / adapter).exists()
            for adapter in adapters
        )
        
        logger.info(f"   Merged Model: {'✅' if has_merged else '❌'}")
        logger.info(f"   GGUF Model: {'✅' if has_gguf else '❌'}")
        logger.info(f"   Adapters: {'✅' if has_adapters else '❌'}")
        
        return has_merged or has_adapters
    
    def load_pipeline(self, mode="fast"):
        """
        Load the appropriate model pipeline
        
        Args:
            mode: "fast" (merged model) or "reliable" (base + adapters)
        """
        try:
            logger.info(f"📥 Loading pipeline in {mode.upper()} mode...")
            
            # Import the multi-agent pipeline
            from importlib import import_module
            multi_agent = import_module('4_run_multi_agent')
            
            use_merged = (mode == "fast")
            self.pipeline = multi_agent.create_pipeline(
                self.project_path,
                use_merged=use_merged
            )
            
            if self.pipeline:
                self.mode = mode
                logger.info(f"✅ Pipeline loaded in {mode.upper()} mode")
                return True
            else:
                logger.error("❌ Failed to load pipeline")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error loading pipeline: {e}", exc_info=True)
            return False
    
    def process_message(self, message, history):
        """
        Process a chat message
        
        Args:
            message: User's input message
            history: Chat history
        
        Returns:
            Updated response
        """
        try:
            if not self.pipeline:
                return "⚠️ Model not loaded. Please wait..."
            
            logger.info(f"💬 Processing: {message[:50]}...")
            
            # Check if this is a full pipeline request or simple generation
            if any(keyword in message.lower() for keyword in ["implement", "create", "build", "design", "write"]):
                # Use full 3-agent pipeline
                result = self.pipeline.run_pipeline(message)
                
                if result:
                    response = f"""## 🧠 PLAN
{result['plan']}

---

## 💻 CODE
{result['code']}

---

## 🔍 CRITIQUE
{result['critique']}
"""
                    return response
                else:
                    return "❌ Error processing request. Please try again."
            else:
                # Simple generation
                response = self.pipeline.generate(message, agent=None, max_tokens=800)
                return response if response else "❌ Error generating response."
                
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return f"❌ Error: {str(e)}"
    
    def create_interface(self):
        """Create Gradio interface"""
        try:
            import gradio as gr
            
            logger.info("🎨 Creating Gradio interface...")
            
            # Custom CSS
            custom_css = """
            .container {
                max-width: 1200px;
                margin: auto;
            }
            .gradio-container {
                font-family: 'Arial', sans-serif;
            }
            """
            
            # Mode selection callback
            def change_mode(mode):
                logger.info(f"🔄 Switching to {mode} mode...")
                self.cleanup()
                success = self.load_pipeline(mode)
                if success:
                    return f"✅ Switched to {mode.upper()} mode"
                else:
                    return f"❌ Failed to switch to {mode} mode"
            
            # Create interface
            with gr.Blocks(css=custom_css, title="Gemini 3 Pro Coder") as interface:
                gr.Markdown("""
                # 🚀 Gemini 3 Pro-Level Coding Specialist
                
                An autonomous AI coding assistant trained on 15,000+ examples using multi-adapter LoRA fine-tuning.
                
                **Capabilities:**
                - Novel algorithm design
                - Production-ready code generation
                - Self-critical code review
                - Edge case analysis
                
                **Usage Tips:**
                - Use action verbs like "implement", "create", "build" for full 3-agent pipeline
                - Ask specific coding questions for focused responses
                - Request explanations, optimizations, or debugging help
                """)
                
                with gr.Row():
                    mode_selector = gr.Radio(
                        choices=["fast", "reliable"],
                        value=self.mode,
                        label="Mode",
                        info="Fast: Merged model (faster). Reliable: Base + Adapters (more accurate)"
                    )
                    mode_status = gr.Textbox(label="Status", value=f"✅ Loaded in {self.mode.upper()} mode", interactive=False)
                
                mode_selector.change(
                    fn=change_mode,
                    inputs=[mode_selector],
                    outputs=[mode_status]
                )
                
                chatbot = gr.ChatInterface(
                    fn=self.process_message,
                    examples=[
                        "Implement a thread-safe LRU cache with O(1) operations",
                        "Create a binary search tree with self-balancing",
                        "Build a rate limiter using token bucket algorithm",
                        "Design a distributed cache with consistent hashing",
                        "Implement merge sort with in-place optimization",
                    ],
                    title="Chat with the Coder",
                    description="Ask me to implement algorithms, review code, or explain concepts",
                    theme="soft",
                    retry_btn="🔄 Retry",
                    undo_btn="↩️ Undo",
                    clear_btn="🗑️ Clear",
                )
                
                gr.Markdown("""
                ---
                
                **Model Details:**
                - Base: Llama-3.1-8B-Instruct
                - Training: 3x LoRA Adapters (Planner + Coder + Critic)
                - Optimization: Unsloth
                - Context: 2048 tokens
                
                **Note:** First response may be slower due to model loading.
                """)
            
            return interface
            
        except Exception as e:
            logger.error(f"❌ Error creating interface: {e}", exc_info=True)
            return None
    
    def launch(self, share=False):
        """Launch the GUI application"""
        logger.info("=" * 80)
        logger.info("🎨 LAUNCHING GUI APPLICATION")
        logger.info("=" * 80)
        
        # Verify models
        if not self.verify_models():
            logger.error("❌ Required models not found!")
            logger.error("   Please run the training pipeline first (0_master_controller.py)")
            return False
        
        # Load pipeline
        if not self.load_pipeline(mode="fast"):
            logger.error("❌ Failed to load pipeline")
            return False
        
        # Create interface
        interface = self.create_interface()
        if not interface:
            logger.error("❌ Failed to create interface")
            return False
        
        # Launch
        try:
            logger.info("🌐 Starting Gradio server...")
            logger.info("   Press Ctrl+C to stop")
            
            interface.launch(
                share=share,
                server_name="0.0.0.0",
                server_port=7860,
                show_error=True,
            )
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error launching interface: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    try:
        # Detect project path
        project_path = Path.cwd()
        
        logger.info("=" * 80)
        logger.info("🎨 GUI APPLICATION")
        logger.info(f"   Project: {project_path}")
        logger.info("=" * 80)
        
        # Create and launch GUI
        gui = CoderGUI(project_path)
        
        # Check if share mode requested
        share = "--share" in sys.argv
        
        success = gui.launch(share=share)
        
        if not success:
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ GUI interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
