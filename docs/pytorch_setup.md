# PyTorch Setup for RTX 5000 Series (Blackwell Architecture)

## Important Notes for RTX 5000 Series

Your RTX 5000 series card uses the Blackwell architecture, which requires specific PyTorch versions for optimal compatibility.

## Installation Steps

### Option 1: Latest PyTorch (Recommended)
The current requirements.txt includes the latest PyTorch, which should support RTX 5000 series:

```bash
pip install torch torchvision torchaudio
```

### Option 2: CUDA-specific Installation
If you encounter issues, you can install PyTorch with a specific CUDA version:

```bash
# For CUDA 12.1
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# For CUDA 11.8 (if you have an older CUDA installation)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Option 3: Nightly Build (if stable doesn't work)
If the stable version doesn't support your RTX 5000 series yet:

```bash
pip install --pre torch torchvision torchaudio --index-url https://download.pytorch.org/whl/nightly/cu121
```

## Testing Your Setup

1. Run `setup.bat` to create the virtual environment and install dependencies
2. Run `test_gpu.bat` to test GPU compatibility
3. The test will show if your RTX 5000 series card is detected and working

## Expected Output

If everything works correctly, you should see:
- PyTorch version
- CUDA available: True
- GPU 0: NVIDIA GeForce RTX 50XX (or similar)
- GPU test passed

## Troubleshooting

### If CUDA is not detected:
1. Make sure you have the latest NVIDIA drivers installed
2. Install CUDA Toolkit if not already installed
3. Try installing PyTorch with a specific CUDA version (see Option 2 above)

### If you get memory errors:
- Your RTX 5000 series has plenty of VRAM, but ensure no other GPU-intensive applications are running
- The test uses a small tensor (1000x1000), so memory shouldn't be an issue

### For older CUDA versions:
If you have CUDA 11.x installed, use the cu118 wheel instead of cu121.

## Performance Notes

RTX 5000 series cards are very powerful and should provide excellent performance for frame extraction tasks. The GPU acceleration will be most noticeable with:
- Large video files
- High-resolution videos (4K+)
- When extracting many frames

## Next Steps

After confirming GPU compatibility works, the frame extractor application will automatically use GPU acceleration when available, falling back to CPU processing if needed.
