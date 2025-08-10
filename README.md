# Frame Extractor - RTX 5000 Series Ready

[![Pyth- **Windows 10/11** (primarypython main.py
```
- **PNG```
frame-extractor/
├── main.py              # Main GUI application
├── setup.bat            # Virtual environment setup
├── run.bat              # Application launcher  
├── test_gpu.py          # GPU compatibility test
├── test_gpu.bat         # GPU test launcher
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── CONTRIBUTING.md      # Contribution guidelines
├── LICENSE              # MIT License
├── .gitignore           # Git ignore file
└── Extraction/          # Output folder (created automatically)
    └── [video_name]/    # Individual video folders
```

## Performancegit zero-padding
- **Example**: `my_video_000001.png`, `my_video_000002.png`

## Project Structure Usageport)

## Installation3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.7.0-red.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-12.8-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional video frame extraction application optimized for NVIDIA RTX 5000 series (Blackwell architecture) GPUs with 120 streaming multiprocessor support.

## Features

### Frame Extractor
- **RTX 5000 Series Optimized** - Full 120 SM utilization for maximum performance
- **Lossless PNG Output** - High-quality frame preservation
- **GPU Acceleration** - CUDA-powered processing with automatic CPU fallback
- **Smart Organization** - Automatic folder creation based on video names
- **Flexible Extraction** - Custom intervals or complete frame extraction
- **Real-time Progress** - Live progress tracking with GPU status
- **Robust Error Handling** - Graceful fallbacks and user-friendly messages

### 🆕 Video Cropper (New Feature!)
- **Video Editing Interface** - Click and drag crop selection
- **Real-time Preview** - Frame-by-frame navigation with timeline
- **Lossless Export** - High-quality H.264/H.265 cropped video output
- **Dark Mode Support** - Toggle between light and dark themes
- **"framed_" Prefix** - Automatic output naming (e.g., framed_video.mp4)

## Quick Start

### Frame Extractor (Original)
```bash
# 1. Run setup (first time only)
.\setup.bat

# 2. Launch frame extractor
.\run.bat
```

### Video Cropper (New Feature)
```bash
# 1. Same setup as above (shared environment)

# 2. Launch video cropper
.\run_cropper.bat
```

## Supported Hardware

### Optimal Performance
- **NVIDIA RTX 5090/5080/5070** (Blackwell - 120 SM)
- **PyTorch 2.7.0+cu128** with CUDA 12.8

### Fully Supported
- Any CUDA-compatible NVIDIA GPU
- CPU-only processing (automatic fallback)

## Requirements

- **Python 3.10+**
- **NVIDIA GPU** with CUDA support (optional, CPU fallback available)  
- **Windows 10/11** (primary support)

## �️ Installation

### Automated Setup (Recommended)
```bash
# 1. Run setup script
.\setup.bat

# 2a. Launch frame extractor (original)
.\run.bat

# 2b. Launch video cropper (new feature)
.\run_cropper.bat
```

### Manual Setup
```bash
# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3a. Run frame extractor
python main.py

# 3b. Run video cropper
python video_cropper.py
```

## � Usage

1. **Launch the application** using `.\run.bat` or `python main.py`
2. **Select video file** using the Browse button
3. **Choose extraction mode:**
   - **Interval mode**: Extract frames every X seconds
   - **All frames**: Extract every single frame
4. **Configure GPU acceleration** (automatically detected)
5. **Click "Start Extraction"** and monitor progress
6. **Find extracted frames** in `Extraction/[video_name]/` folder

### Supported Video Formats
- MP4, AVI, MOV, MKV, WMV, FLV, WEBM

### Output Format
- **PNG files** with 6-digit zero-padding
- **Example**: `my_video_000001.png`, `my_video_000002.png`

## �️ Project Structure

```
frame-extractor/
├── 📄 main.py              # Main GUI application (frame extractor)
├── � video_cropper.py     # Video cropper application (NEW!)
├── �🔧 setup.bat            # Virtual environment setup
├── 🚀 run.bat              # Frame extractor launcher  
├── 🚀 run_cropper.bat      # Video cropper launcher (NEW!)
├── 🧪 test_gpu.py          # GPU compatibility test
├── 🧪 test_gpu.bat         # GPU test launcher
├── 📋 requirements.txt     # Python dependencies
├── 📚 README.md            # This file
├── 📚 VIDEO_CROPPER_README.md  # Video cropper documentation (NEW!)
├── � pytorch_setup.md     # PyTorch setup guide
├── � CONTRIBUTING.md      # Contribution guidelines
├── 📄 LICENSE              # MIT License
├── 🚫 .gitignore           # Git ignore file
└── 📁 Extraction/          # Output folder (created automatically)
    ├── [video_name]/       # Individual video folders (frames)
    └── framed_*.mp4        # Cropped video files (NEW!)
```

## ⚡ Performance

### RTX 5000 Series (Blackwell)
- **120 SM utilization** for maximum throughput
- **PyTorch 2.7.0+cu128** optimized kernels
- **Memory efficient** batch processing
- **Automatic optimization** detection

### Other NVIDIA GPUs  
- **Automatic detection** and optimization
- **CUDA acceleration** where available
- **Graceful CPU fallback** if needed

### Benchmarks
- **4K Video**: ~50% faster with RTX 5080 vs CPU-only
- **1080p Video**: ~30% faster with GPU acceleration
- **Memory usage**: <2GB VRAM for typical operations

## Technical Details

### GPU Support
- **PyTorch tensors** for GPU processing
- **Automatic memory management** 
- **CUDA cache optimization**
- **Blackwell architecture recognition**

### Error Handling
- **Robust error handling** with user-friendly messages
- **Automatic CPU fallback** if GPU processing fails
- **Progress preservation** during cancellation
- **Memory cleanup** after processing

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
```bash
git clone https://github.com/yourusername/frame-extractor.git
cd frame-extractor
.\setup.bat
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **NVIDIA** for Blackwell architecture documentation
- **PyTorch team** for RTX 5000 series support
- **OpenCV community** for video processing capabilities

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/frame-extractor/issues)
- **Documentation**: See documentation files for GPU setup details
- **Contributing**: See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Made with care for the video processing community**
