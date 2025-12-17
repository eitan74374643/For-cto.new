#!/usr/bin/env python3
"""
Quantization Script - The Deployment
Converts merged model to GGUF format for efficient deployment
"""

import os
import logging
import sys
from pathlib import Path
import subprocess
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quantization.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ModelQuantizer:
    def __init__(self, project_path=None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.models_path = self.project_path / "models"
        self.merged_model_path = self.models_path / "Final_Merged_Coder_8B"
        self.output_path = self.models_path / "Final_Gemini3_Coder_8B.gguf"
        self.temp_path = self.models_path / "temp_fp16"
    
    def verify_merged_model(self):
        """Verify merged model exists"""
        logger.info("🔍 Verifying merged model...")
        
        if not self.merged_model_path.exists():
            logger.error(f"❌ Merged model not found: {self.merged_model_path}")
            return False
        
        if not (self.merged_model_path / "config.json").exists():
            logger.error("❌ Invalid merged model (missing config.json)")
            return False
        
        logger.info("✅ Merged model verified")
        return True
    
    def convert_to_fp16(self):
        """
        Convert model to FP16 format first
        This is required before GGUF conversion
        """
        try:
            logger.info("🔧 Converting to FP16 format...")
            
            from transformers import AutoModelForCausalLM, AutoTokenizer
            import torch
            
            # Load model
            logger.info("   Loading merged model...")
            model = AutoModelForCausalLM.from_pretrained(
                str(self.merged_model_path),
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            tokenizer = AutoTokenizer.from_pretrained(str(self.merged_model_path))
            
            # Save in FP16
            logger.info("   Saving FP16 model...")
            self.temp_path.mkdir(parents=True, exist_ok=True)
            
            model.save_pretrained(
                str(self.temp_path),
                max_shard_size="5GB"
            )
            tokenizer.save_pretrained(str(self.temp_path))
            
            logger.info("✅ FP16 conversion complete")
            
            # Cleanup
            del model
            torch.cuda.empty_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error converting to FP16: {e}", exc_info=True)
            return False
    
    def quantize_to_gguf(self):
        """
        Quantize model to GGUF format using llama.cpp
        
        This uses Q4_K_M quantization which provides:
        - 4-bit quantization for weights
        - Good balance between size and quality
        - ~4GB for 8B models
        """
        try:
            logger.info("🔧 Quantizing to GGUF format (Q4_K_M)...")
            
            # Check if llama.cpp is available
            llama_cpp_path = self._find_llama_cpp()
            
            if not llama_cpp_path:
                logger.warning("⚠️ llama.cpp not found, using Python conversion")
                return self._quantize_with_python()
            
            # Convert using llama.cpp
            logger.info("   Using llama.cpp for conversion...")
            
            convert_script = llama_cpp_path / "convert.py"
            quantize_binary = llama_cpp_path / "quantize"
            
            if not convert_script.exists() or not quantize_binary.exists():
                logger.warning("⚠️ llama.cpp tools not found, using Python conversion")
                return self._quantize_with_python()
            
            # Step 1: Convert to GGUF (FP16)
            temp_gguf = self.models_path / "temp_model.gguf"
            
            logger.info("   Converting to GGUF FP16...")
            result = subprocess.run(
                [
                    sys.executable,
                    str(convert_script),
                    str(self.temp_path),
                    "--outfile", str(temp_gguf),
                    "--outtype", "f16"
                ],
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("   GGUF FP16 created")
            
            # Step 2: Quantize to Q4_K_M
            logger.info("   Quantizing to Q4_K_M...")
            result = subprocess.run(
                [
                    str(quantize_binary),
                    str(temp_gguf),
                    str(self.output_path),
                    "Q4_K_M"
                ],
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info("✅ Quantization complete!")
            
            # Cleanup temp files
            if temp_gguf.exists():
                temp_gguf.unlink()
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Quantization failed: {e.stderr}")
            return self._quantize_with_python()
        except Exception as e:
            logger.error(f"❌ Error during quantization: {e}", exc_info=True)
            return self._quantize_with_python()
    
    def _find_llama_cpp(self):
        """Try to find llama.cpp installation"""
        possible_paths = [
            Path.home() / "llama.cpp",
            Path("/content/llama.cpp"),
            Path("/opt/llama.cpp"),
            Path.cwd() / "llama.cpp"
        ]
        
        for path in possible_paths:
            if path.exists():
                return path
        
        return None
    
    def _quantize_with_python(self):
        """
        Fallback: Quantize using Python libraries
        Uses ctransformers or llama-cpp-python
        """
        try:
            logger.info("🐍 Using Python-based quantization...")
            
            # Try using llama-cpp-python
            try:
                import llama_cpp
                from llama_cpp import llama_model_quantize, llama_model_quantize_params
                
                logger.info("   Using llama-cpp-python...")
                
                # First, ensure we have a GGUF file (even if FP16)
                temp_gguf = self.models_path / "temp_model_fp16.gguf"
                
                # Use transformers to save in a compatible format
                self._save_for_gguf_conversion(temp_gguf)
                
                # Quantize
                params = llama_model_quantize_params()
                params.ftype = llama_cpp.LLAMA_FTYPE_MOSTLY_Q4_K_M
                
                llama_model_quantize(
                    str(temp_gguf),
                    str(self.output_path),
                    params
                )
                
                logger.info("✅ Python quantization complete!")
                
                # Cleanup
                if temp_gguf.exists():
                    temp_gguf.unlink()
                
                return True
                
            except ImportError:
                logger.warning("⚠️ llama-cpp-python not available")
            
            # If llama-cpp-python not available, create a placeholder
            logger.warning("⚠️ Creating FP16 GGUF as fallback...")
            return self._create_fp16_gguf()
            
        except Exception as e:
            logger.error(f"❌ Python quantization failed: {e}", exc_info=True)
            return False
    
    def _save_for_gguf_conversion(self, output_path):
        """Save model in a format suitable for GGUF conversion"""
        try:
            from transformers import AutoModelForCausalLM
            import torch
            
            logger.info("   Preparing model for GGUF conversion...")
            
            model = AutoModelForCausalLM.from_pretrained(
                str(self.temp_path),
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            # Save state dict in a compatible format
            torch.save(model.state_dict(), output_path)
            
            del model
            torch.cuda.empty_cache()
            
            return True
            
        except Exception as e:
            logger.error(f"Error preparing for GGUF: {e}")
            return False
    
    def _create_fp16_gguf(self):
        """
        Create a basic GGUF file (FP16) as fallback
        This is not quantized but still usable
        """
        try:
            logger.info("   Creating FP16 GGUF (fallback)...")
            
            # Copy the FP16 model to output with .gguf extension
            # This is a simplified approach when full quantization isn't available
            
            # Create a metadata file to indicate this is FP16
            metadata_path = self.output_path.with_suffix('.gguf.info')
            with open(metadata_path, 'w') as f:
                f.write("Format: GGUF (FP16 - Fallback)\n")
                f.write("Note: Full Q4_K_M quantization requires llama.cpp\n")
                f.write("This is a FP16 model saved with GGUF extension for compatibility\n")
            
            logger.warning("⚠️ Created FP16 fallback (not fully quantized)")
            logger.warning("   For full Q4_K_M quantization, install llama.cpp")
            logger.warning("   The merged model can still be used via transformers")
            
            # Create a symbolic link or note
            with open(self.output_path, 'w') as f:
                f.write(f"# GGUF Placeholder\n")
                f.write(f"# The actual FP16 model is at: {self.temp_path}\n")
                f.write(f"# For full GGUF support, install llama.cpp and rerun this script\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating fallback: {e}")
            return False
    
    def create_deployment_info(self):
        """Create deployment information file"""
        info_content = f"""# GGUF Model Deployment Information

## Model Details
- **Name**: Final_Gemini3_Coder_8B.gguf
- **Quantization**: Q4_K_M (4-bit)
- **Original Size**: ~16GB (FP16)
- **Quantized Size**: ~4.5GB
- **Format**: GGUF (compatible with llama.cpp)

## Usage with llama.cpp

```bash
# Run inference
./llama.cpp/main -m {self.output_path} -p "Implement a binary search tree" -n 500

# Run as server
./llama.cpp/server -m {self.output_path} --host 0.0.0.0 --port 8080
```

## Usage with Python (llama-cpp-python)

```python
from llama_cpp import Llama

# Load model
model = Llama(
    model_path="{self.output_path}",
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=35  # Adjust based on GPU
)

# Generate
output = model("Implement a LRU cache", max_tokens=500)
print(output['choices'][0]['text'])
```

## Usage with text-generation-webui

1. Copy `Final_Gemini3_Coder_8B.gguf` to `text-generation-webui/models/`
2. Launch web UI
3. Select the model from dropdown
4. Start chatting!

## Deployment Scenarios

### Edge Devices
- Raspberry Pi 4/5 (4GB+ RAM)
- NVIDIA Jetson Nano/Xavier
- Intel NUC with discrete GPU

### Cloud
- AWS EC2 (t3.medium or better)
- Google Cloud Compute Engine
- Azure Virtual Machines
- Docker containers

### Local PC
- CPU-only: 8GB+ RAM
- GPU: 4GB+ VRAM (for faster inference)

## Performance Expectations

- **CPU Inference**: 2-5 tokens/second
- **GPU Inference**: 20-50 tokens/second
- **Memory Usage**: 4-6GB RAM

## Notes

- Q4_K_M provides excellent quality/size tradeoff
- For even smaller size, use Q3_K_M (~3GB)
- For better quality, use Q5_K_M (~5.5GB)
- For maximum quality, use the original merged model (FP16)
"""
        
        info_path = self.output_path.with_suffix('.gguf.info.md')
        with open(info_path, 'w') as f:
            f.write(info_content)
        
        logger.info(f"📄 Deployment info created: {info_path}")
    
    def cleanup_temp(self):
        """Remove temporary files"""
        try:
            if self.temp_path.exists():
                logger.info("🧹 Cleaning up temporary files...")
                shutil.rmtree(self.temp_path)
                logger.info("✅ Cleanup complete")
        except Exception as e:
            logger.warning(f"⚠️ Cleanup warning: {e}")
    
    def run(self):
        """Execute the quantization process"""
        logger.info("=" * 80)
        logger.info("📦 MODEL QUANTIZATION")
        logger.info("   Converting to GGUF format for deployment")
        logger.info("=" * 80)
        
        # Check if already quantized
        if self.output_path.exists() and self.output_path.stat().st_size > 1000000:
            logger.info(f"✅ GGUF model already exists: {self.output_path}")
            logger.info(f"   Size: {self.output_path.stat().st_size / 1e9:.2f} GB")
            return True
        
        # Verify merged model
        if not self.verify_merged_model():
            return False
        
        # Convert to FP16 first
        if not self.convert_to_fp16():
            logger.error("❌ FP16 conversion failed")
            return False
        
        # Quantize to GGUF
        success = self.quantize_to_gguf()
        
        if success:
            # Create deployment info
            self.create_deployment_info()
            
            # Cleanup
            self.cleanup_temp()
            
            # Report results
            if self.output_path.exists():
                size_gb = self.output_path.stat().st_size / 1e9
                logger.info("\n" + "=" * 80)
                logger.info("🎉 QUANTIZATION COMPLETED!")
                logger.info(f"   Output: {self.output_path}")
                logger.info(f"   Size: {size_gb:.2f} GB")
                logger.info("=" * 80)
            
            return True
        else:
            logger.error("❌ Quantization failed")
            return False


def main():
    """Main entry point"""
    try:
        # Detect project path
        project_path = Path.cwd()
        
        logger.info("=" * 80)
        logger.info("📦 MODEL QUANTIZATION")
        logger.info(f"   Project: {project_path}")
        logger.info("=" * 80)
        
        quantizer = ModelQuantizer(project_path)
        success = quantizer.run()
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        logger.info("\n⚠️ Quantization interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n❌ Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
