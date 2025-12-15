#!/usr/bin/env python3
"""
Master Controller - The Brain
This is the ONLY script you need to run.
It orchestrates the entire 15-day autonomous training and deployment pipeline.
"""

import os
import sys
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_controller.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MasterController:
    def __init__(self):
        self.project_path = None
        self.is_colab = False
        self.max_retries = 5
        self.retry_delay = 60
        
    def detect_environment(self):
        """Detect if running on Google Colab or Local PC"""
        try:
            import google.colab
            self.is_colab = True
            logger.info("🌐 Detected Google Colab environment")
            return True
        except ImportError:
            self.is_colab = False
            logger.info("💻 Detected Local PC environment")
            return False
    
    def setup_environment(self):
        """Setup project path based on environment"""
        if self.is_colab:
            try:
                from google.colab import drive
                logger.info("📂 Mounting Google Drive...")
                drive.mount('/content/drive', force_remount=False)
                self.project_path = Path('/content/drive/MyDrive/AI_Project_Master')
                logger.info(f"✅ Drive mounted successfully")
            except Exception as e:
                logger.error(f"❌ Failed to mount Google Drive: {e}")
                raise
        else:
            self.project_path = Path.cwd()
            logger.info(f"✅ Using local directory: {self.project_path}")
        
        # Create project directory if it doesn't exist
        self.project_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.project_path / "checkpoints").mkdir(exist_ok=True)
        (self.project_path / "logs").mkdir(exist_ok=True)
        (self.project_path / "models").mkdir(exist_ok=True)
        (self.project_path / "data").mkdir(exist_ok=True)
        
        # Change to project directory
        os.chdir(self.project_path)
        logger.info(f"✅ Working directory: {os.getcwd()}")
        
        return self.project_path
    
    def check_gpu(self):
        """Verify CUDA is available"""
        try:
            import torch
            if torch.cuda.is_available():
                gpu_name = torch.cuda.get_device_name(0)
                gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
                logger.info(f"✅ GPU Available: {gpu_name}")
                logger.info(f"   GPU Memory: {gpu_memory:.2f} GB")
                return True
            else:
                logger.warning("⚠️ CUDA not available. Training will be very slow!")
                return False
        except Exception as e:
            logger.error(f"❌ Error checking GPU: {e}")
            return False
    
    def run_script(self, script_name, step_name, check_path=None):
        """
        Run a Python script with retry logic
        
        Args:
            script_name: Name of the Python script to run
            step_name: Human-readable step name for logging
            check_path: Optional path to check if step is already complete
        """
        if check_path and Path(check_path).exists():
            logger.info(f"✅ {step_name} already completed. Skipping...")
            return True
        
        logger.info(f"🚀 Starting {step_name}...")
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"   Attempt {attempt}/{self.max_retries}")
                
                # Get the script path (from current directory)
                script_path = Path.cwd() / script_name
                
                # If script doesn't exist in project path, try parent directory
                if not script_path.exists():
                    parent_script = Path(__file__).parent / script_name
                    if parent_script.exists():
                        script_path = parent_script
                
                if not script_path.exists():
                    logger.error(f"❌ Script not found: {script_path}")
                    return False
                
                # Run the script
                result = subprocess.run(
                    [sys.executable, str(script_path)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                
                logger.info(f"✅ {step_name} completed successfully!")
                if result.stdout:
                    logger.info(f"Output:\n{result.stdout}")
                
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ {step_name} failed on attempt {attempt}")
                logger.error(f"Error output:\n{e.stderr}")
                
                if attempt < self.max_retries:
                    logger.info(f"⏳ Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"❌ {step_name} failed after {self.max_retries} attempts")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Unexpected error in {step_name}: {e}")
                if attempt < self.max_retries:
                    time.sleep(self.retry_delay)
                else:
                    return False
        
        return False
    
    def run_pipeline(self):
        """Execute the complete 15-day training pipeline"""
        logger.info("=" * 80)
        logger.info("🧠 MASTER CONTROLLER INITIATED")
        logger.info("   Gemini 3 Pro-Level Coding Specialist Training Pipeline")
        logger.info("=" * 80)
        
        start_time = datetime.now()
        
        # Step 0: Environment Setup
        logger.info("\n📋 STEP 0: Environment Setup")
        self.detect_environment()
        self.setup_environment()
        self.check_gpu()
        
        # Step 1: Data Generation
        logger.info("\n📋 STEP 1: Dataset Generation")
        data_path = self.project_path / "data" / "training_data.jsonl"
        if not self.run_script(
            "1_generate_massive_dataset.py",
            "Dataset Generation",
            check_path=data_path
        ):
            logger.error("❌ Pipeline failed at Step 1: Dataset Generation")
            return False
        
        # Step 2: Training Three Adapters
        logger.info("\n📋 STEP 2: Training Three LoRA Adapters")
        adapters_path = self.project_path / "models" / "lora_planner"
        if not self.run_script(
            "2_train_three_adapters.py",
            "Training Three Adapters",
            check_path=adapters_path
        ):
            logger.error("❌ Pipeline failed at Step 2: Training")
            return False
        
        # Step 3: Merge Final Product
        logger.info("\n📋 STEP 3: Merging Final Model")
        merged_path = self.project_path / "models" / "Final_Merged_Coder_8B"
        if not self.run_script(
            "3_merge_final_product.py",
            "Merging Final Product",
            check_path=merged_path
        ):
            logger.error("❌ Pipeline failed at Step 3: Merging")
            return False
        
        # Step 4: Quantize to GGUF
        logger.info("\n📋 STEP 4: Quantizing to GGUF")
        gguf_path = self.project_path / "models" / "Final_Gemini3_Coder_8B.gguf"
        if not self.run_script(
            "6_quantize_for_deployment.py",
            "Quantization for Deployment",
            check_path=gguf_path
        ):
            logger.error("❌ Pipeline failed at Step 4: Quantization")
            return False
        
        # Step 5: Launch GUI (ONLY if GGUF exists)
        logger.info("\n📋 STEP 5: Launching GUI Application")
        if gguf_path.exists():
            logger.info("✅ GGUF file verified. Safe to launch GUI!")
            logger.info("🎨 Starting Gradio Interface...")
            
            # Note: GUI will run in foreground - this is intentional
            try:
                script_path = Path.cwd() / "5_gui_app.py"
                if not script_path.exists():
                    script_path = Path(__file__).parent / "5_gui_app.py"
                
                subprocess.run([sys.executable, str(script_path)])
            except KeyboardInterrupt:
                logger.info("\n👋 GUI closed by user")
            except Exception as e:
                logger.error(f"❌ GUI error: {e}")
        else:
            logger.error("❌ GGUF file not found. Cannot launch GUI.")
            return False
        
        # Pipeline Complete
        end_time = datetime.now()
        duration = end_time - start_time
        
        logger.info("\n" + "=" * 80)
        logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info(f"   Total Duration: {duration}")
        logger.info(f"   Project Path: {self.project_path}")
        logger.info("=" * 80)
        
        return True


def main():
    """Main entry point"""
    controller = MasterController()
    
    try:
        success = controller.run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Pipeline interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
