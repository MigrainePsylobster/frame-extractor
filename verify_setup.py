#!/usr/bin/env python3
"""
Frame Extractor Setup Verification
Quick verification that all components are working correctly
"""

import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)")
        return False

def check_virtual_environment():
    """Check if virtual environment exists"""
    venv_path = Path("venv")
    if venv_path.exists():
        print("✅ Virtual environment found")
        return True
    else:
        print("❌ Virtual environment not found - run setup.bat")
        return False

def check_dependencies():
    """Check if key dependencies can be imported"""
    deps = {
        'torch': 'PyTorch',
        'cv2': 'OpenCV',
        'tkinter': 'Tkinter (GUI)',
        'numpy': 'NumPy',
        'PIL': 'Pillow'
    }
    
    all_good = True
    for module, name in deps.items():
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - run setup.bat")
            all_good = False
    
    return all_good

def check_gpu_availability():
    """Check GPU availability"""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"✅ GPU: {gpu_name}")
            return True
        else:
            print("⚠️  GPU: Not available (CPU fallback will be used)")
            return True
    except ImportError:
        print("❌ Cannot check GPU - PyTorch not installed")
        return False

def check_file_structure():
    """Check if essential files exist"""
    files = [
        'main.py',
        'requirements.txt',
        'setup.bat',
        'run.bat',
        'test_gpu.py',
        'README.md'
    ]
    
    all_good = True
    for file in files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            all_good = False
    
    return all_good

def main():
    print("🔍 Frame Extractor Setup Verification")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("Virtual Environment", check_virtual_environment),
        ("Dependencies", check_dependencies),
        ("GPU Support", check_gpu_availability),
        ("File Structure", check_file_structure)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n{name}:")
        if not check_func():
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 All checks passed! Ready to use Frame Extractor.")
        print("   Run: .\\run.bat")
    else:
        print("❌ Some checks failed. Please:")
        print("   1. Run: .\\setup.bat")
        print("   2. Run this verification again")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
