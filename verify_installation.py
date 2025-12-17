#!/usr/bin/env python3
"""
Installation Verification Script
Checks that all files are present and dependencies are available
"""

import sys
from pathlib import Path
import importlib.util


def check_file(filepath, description):
    """Check if a file exists"""
    path = Path(filepath)
    if path.exists():
        size = path.stat().st_size
        print(f"✅ {description}: {filepath} ({size:,} bytes)")
        return True
    else:
        print(f"❌ {description}: {filepath} NOT FOUND")
        return False


def check_dependency(module_name, package_name=None):
    """Check if a Python module is available"""
    if package_name is None:
        package_name = module_name
    
    spec = importlib.util.find_spec(module_name)
    if spec is not None:
        print(f"✅ {package_name} is installed")
        return True
    else:
        print(f"❌ {package_name} is NOT installed")
        return False


def check_python_syntax(filepath):
    """Check if a Python file has valid syntax"""
    import py_compile
    try:
        py_compile.compile(filepath, doraise=True)
        return True
    except py_compile.PyCompileError:
        print(f"❌ Syntax error in {filepath}")
        return False


def main():
    print("=" * 80)
    print("🔍 INSTALLATION VERIFICATION")
    print("=" * 80)
    
    all_good = True
    
    # Check Python version
    print("\n📋 Python Version")
    version = sys.version_info
    print(f"   Python {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python version is compatible (3.8+)")
    else:
        print("❌ Python version too old (need 3.8+)")
        all_good = False
    
    # Check core scripts
    print("\n📋 Core Scripts")
    scripts = [
        ("0_master_controller.py", "Master Controller"),
        ("1_generate_massive_dataset.py", "Dataset Generator"),
        ("2_train_three_adapters.py", "Adapter Trainer"),
        ("3_merge_final_product.py", "Model Merger"),
        ("4_run_multi_agent.py", "Multi-Agent Pipeline"),
        ("5_gui_app.py", "GUI Application"),
        ("6_quantize_for_deployment.py", "Quantization Script"),
    ]
    
    for script, description in scripts:
        if not check_file(script, description):
            all_good = False
        else:
            # Check syntax
            if not check_python_syntax(script):
                all_good = False
    
    # Check supporting files
    print("\n📋 Supporting Files")
    supporting = [
        ("requirements.txt", "Dependencies List"),
        ("README.md", "Main Documentation"),
        ("QUICKSTART.md", "Quick Start Guide"),
        ("PROJECT_STRUCTURE.md", "Project Structure"),
        ("LICENSE", "License File"),
        (".gitignore", "Git Ignore File"),
    ]
    
    for file, description in supporting:
        if not check_file(file, description):
            all_good = False
    
    # Check dependencies
    print("\n📋 Python Dependencies")
    dependencies = [
        ("torch", "PyTorch"),
        ("transformers", "Transformers"),
        ("gradio", "Gradio"),
        ("datasets", "Datasets"),
        ("tqdm", "Progress Bar"),
    ]
    
    # Note: Some dependencies might not be installed yet
    print("   (Install with: pip install -r requirements.txt)")
    for module, package in dependencies:
        check_dependency(module, package)
    
    # Check optional dependencies
    print("\n📋 Optional Dependencies")
    optional = [
        ("unsloth", "Unsloth"),
        ("peft", "PEFT"),
        ("bitsandbytes", "BitsAndBytes"),
    ]
    
    for module, package in optional:
        check_dependency(module, package)
    
    # Check GPU availability
    print("\n📋 GPU Availability")
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"✅ GPU Available: {gpu_name}")
            print(f"   Memory: {gpu_memory:.2f} GB")
            
            if gpu_memory < 10:
                print("⚠️  Warning: GPU has less than 10GB VRAM")
                print("   Training may be slow or fail")
        else:
            print("⚠️  No GPU detected (will use CPU)")
            print("   Training will be VERY slow")
    except ImportError:
        print("⚠️  PyTorch not installed, cannot check GPU")
    
    # Final summary
    print("\n" + "=" * 80)
    if all_good:
        print("🎉 ALL CORE FILES VERIFIED!")
        print("\n✅ You're ready to start training!")
        print("\n📝 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run master controller: python 0_master_controller.py")
        print("\n📚 Read QUICKSTART.md for detailed instructions")
    else:
        print("❌ VERIFICATION FAILED!")
        print("\n⚠️  Some files are missing or have errors")
        print("   Please ensure all files are present")
    print("=" * 80)
    
    return 0 if all_good else 1


if __name__ == "__main__":
    sys.exit(main())
