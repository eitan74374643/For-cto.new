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
import shutil
from pathlib import Path
from datetime import datetime, timedelta

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
    def __init__(self, max_runtime_hours=4):
        self.project_path = None
        self.is_colab = False
        self.is_kaggle = False
        self.max_retries = 5
        self.retry_delay = 60
        self.max_runtime_hours = max_runtime_hours
        self.max_runtime_seconds = max_runtime_hours * 3600
        self.start_time = time.time()
        self.should_exit = False
        
    def detect_environment(self):
        """Detect if running on Google Colab, Kaggle, or Local PC"""
        # Check for Kaggle
        if os.path.exists('/kaggle/working'):
            self.is_kaggle = True
            logger.info("🔬 Detected Kaggle environment")
            return True
        
        # Check for Colab
        try:
            import google.colab
            self.is_colab = True
            logger.info("🌐 Detected Google Colab environment")
            return True
        except ImportError:
            pass
        
        # Default to local
        self.is_colab = False
        self.is_kaggle = False
        logger.info("💻 Detected Local PC environment")
        return False
    
    def setup_environment(self):
        """Setup project path based on environment"""
        if self.is_kaggle:
            # Kaggle: Use /kaggle/working as base
            self.project_path = Path('/kaggle/working/AI_Project_Master')
            logger.info(f"✅ Using Kaggle working directory: {self.project_path}")
        elif self.is_colab:
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
    
    def check_time_limit(self):
        """Check if we've exceeded the time limit"""
        elapsed = time.time() - self.start_time
        remaining = self.max_runtime_seconds - elapsed
        
        if remaining <= 0:
            logger.warning("⏰ Time limit reached!")
            return True
        
        # Warn at 30 minutes remaining
        if remaining <= 1800 and remaining > 1740:
            logger.warning(f"⚠️ Time warning: {remaining/60:.1f} minutes remaining")
        
        return False
    
    def force_save_checkpoints(self):
        """Force save all checkpoints and progress to persistent storage"""
        logger.info("=" * 80)
        logger.info("💾 FORCE SAVING ALL CHECKPOINTS AND PROGRESS")
        logger.info("=" * 80)
        
        try:
            # Save to Kaggle working directory if on Kaggle
            if self.is_kaggle:
                kaggle_save_path = Path('/kaggle/working')
                logger.info(f"📂 Saving to Kaggle: {kaggle_save_path}")
                
                # Copy critical directories to Kaggle working
                for dir_name in ['checkpoints', 'data', 'models', 'logs']:
                    src_dir = self.project_path / dir_name
                    dst_dir = kaggle_save_path / dir_name
                    
                    if src_dir.exists():
                        logger.info(f"   Copying {dir_name}...")
                        if dst_dir.exists():
                            shutil.rmtree(dst_dir)
                        shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
                        logger.info(f"   ✅ {dir_name} saved")
                    else:
                        logger.info(f"   ⚠️ {dir_name} not found, skipping")
                
                # Save progress file
                progress_file = kaggle_save_path / 'training_progress.txt'
                with open(progress_file, 'w') as f:
                    f.write(f"Last checkpoint: {datetime.now().isoformat()}\n")
                    f.write(f"Elapsed time: {(time.time() - self.start_time)/3600:.2f} hours\n")
                    f.write(f"Project path: {self.project_path}\n")
                logger.info(f"   ✅ Progress file saved")
            
            # Also save progress marker in project directory
            progress_file = self.project_path / 'last_checkpoint.txt'
            with open(progress_file, 'w') as f:
                f.write(f"Last checkpoint: {datetime.now().isoformat()}\n")
                f.write(f"Elapsed time: {(time.time() - self.start_time)/3600:.2f} hours\n")
                f.write(f"Environment: {'Kaggle' if self.is_kaggle else 'Colab' if self.is_colab else 'Local'}\n")
            
            logger.info("✅ All checkpoints saved successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error saving checkpoints: {e}", exc_info=True)
            return False
    
    def run_script(self, script_name, step_name, check_path=None):
        """
        Run a Python script with retry logic and time limit checking
        
        Args:
            script_name: Name of the Python script to run
            step_name: Human-readable step name for logging
            check_path: Optional path to check if step is already complete
        """
        # Check time limit before starting
        if self.check_time_limit():
            logger.warning(f"⏰ Time limit reached before starting {step_name}")
            self.should_exit = True
            return False
        
        if check_path and Path(check_path).exists():
            logger.info(f"✅ {step_name} already completed. Skipping...")
            return True
        
        logger.info(f"🚀 Starting {step_name}...")
        elapsed_hours = (time.time() - self.start_time) / 3600
        logger.info(f"   ⏱️ Elapsed time: {elapsed_hours:.2f} hours / {self.max_runtime_hours} hours")
        
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
                
                # Check time limit after completion
                if self.check_time_limit():
                    logger.warning(f"⏰ Time limit reached after {step_name}")
                    self.should_exit = True
                
                return True
                
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ {step_name} failed on attempt {attempt}")
                logger.error(f"Error output:\n{e.stderr}")
                
                # Check time limit before retry
                if self.check_time_limit():
                    logger.warning(f"⏰ Time limit reached, aborting retries")
                    self.should_exit = True
                    return False
                
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
        """Execute the complete 15-day training pipeline with 4-hour safety timer"""
        logger.info("=" * 80)
        logger.info("🧠 MASTER CONTROLLER INITIATED")
        logger.info("   Gemini 3 Pro-Level Coding Specialist Training Pipeline")
        logger.info(f"   ⏰ Safety Timer: {self.max_runtime_hours} hours")
        logger.info("=" * 80)
        
        start_time_dt = datetime.now()
        
        try:
            # Step 0: Environment Setup
            logger.info("\n📋 STEP 0: Environment Setup")
            self.detect_environment()
            self.setup_environment()
            self.check_gpu()
            
            # Log initial time status
            logger.info(f"⏱️ Started at: {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"⏰ Will auto-save and exit at: {(start_time_dt + timedelta(hours=self.max_runtime_hours)).strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Step 1: Data Generation
            if not self.should_exit:
                logger.info("\n📋 STEP 1: Dataset Generation")
                data_path = self.project_path / "data" / "training_data.jsonl"
                if not self.run_script(
                    "1_generate_massive_dataset.py",
                    "Dataset Generation",
                    check_path=data_path
                ):
                    if not self.should_exit:
                        logger.error("❌ Pipeline failed at Step 1: Dataset Generation")
                    return False
            
            # Step 2: Training Three Adapters
            if not self.should_exit:
                logger.info("\n📋 STEP 2: Training Three LoRA Adapters")
                adapters_path = self.project_path / "models" / "lora_planner"
                if not self.run_script(
                    "2_train_three_adapters.py",
                    "Training Three Adapters",
                    check_path=adapters_path
                ):
                    if not self.should_exit:
                        logger.error("❌ Pipeline failed at Step 2: Training")
                    return False
            
            # Step 3: Merge Final Product
            if not self.should_exit:
                logger.info("\n📋 STEP 3: Merging Final Model")
                merged_path = self.project_path / "models" / "Final_Merged_Coder_8B"
                if not self.run_script(
                    "3_merge_final_product.py",
                    "Merging Final Product",
                    check_path=merged_path
                ):
                    if not self.should_exit:
                        logger.error("❌ Pipeline failed at Step 3: Merging")
                    return False
            
            # Step 4: Quantize to GGUF
            if not self.should_exit:
                logger.info("\n📋 STEP 4: Quantizing to GGUF")
                gguf_path = self.project_path / "models" / "Final_Gemini3_Coder_8B.gguf"
                if not self.run_script(
                    "6_quantize_for_deployment.py",
                    "Quantization for Deployment",
                    check_path=gguf_path
                ):
                    if not self.should_exit:
                        logger.error("❌ Pipeline failed at Step 4: Quantization")
                    return False
            
            # Step 5: Launch GUI (ONLY if GGUF exists and time permits)
            if not self.should_exit:
                logger.info("\n📋 STEP 5: Launching GUI Application")
                gguf_path = self.project_path / "models" / "Final_Gemini3_Coder_8B.gguf"
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
            
            # Pipeline Complete (or time limit reached)
            end_time = datetime.now()
            duration = end_time - start_time_dt
            
            logger.info("\n" + "=" * 80)
            if self.should_exit:
                logger.warning("⏰ PIPELINE PAUSED DUE TO TIME LIMIT")
                logger.info("   Checkpoints saved. Resume by running again.")
            else:
                logger.info("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info(f"   Total Duration: {duration}")
            logger.info(f"   Project Path: {self.project_path}")
            logger.info("=" * 80)
            
            return not self.should_exit
            
        finally:
            # ALWAYS save checkpoints on exit, no matter what
            logger.info("\n📋 Executing safety checkpoint save...")
            self.force_save_checkpoints()
            
            elapsed_hours = (time.time() - self.start_time) / 3600
            logger.info(f"⏱️ Total runtime: {elapsed_hours:.2f} hours")
            
            if self.should_exit:
                logger.info("💾 Safe shutdown complete. All progress saved.")
            
            # Free GPU memory if torch is loaded
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    logger.info("🧹 GPU memory cleared")
            except:
                pass


def main():
    """Main entry point"""
    # Allow customizing time limit via command line argument
    # Usage: python 0_master_controller.py [hours]
    # Default: 4 hours
    max_hours = 4
    if len(sys.argv) > 1:
        try:
            max_hours = float(sys.argv[1])
            logger.info(f"⏰ Using custom time limit: {max_hours} hours")
        except ValueError:
            logger.warning(f"⚠️ Invalid time limit '{sys.argv[1]}', using default: 4 hours")
    
    controller = MasterController(max_runtime_hours=max_hours)
    
    try:
        success = controller.run_pipeline()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️ Pipeline interrupted by user")
        # Still save checkpoints on keyboard interrupt
        logger.info("📋 Saving checkpoints before exit...")
        controller.force_save_checkpoints()
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        # Still save checkpoints on error
        logger.info("📋 Saving checkpoints before exit...")
        controller.force_save_checkpoints()
        sys.exit(1)


if __name__ == "__main__":
    main()
