# Contributing to Frame Extractor

Thank you for your interest in contributing to the Frame Extractor project! This guide will help you get started.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/frame-extractor.git
   cd frame-extractor
   ```

2. **Set up the development environment:**
   ```bash
   .\setup.bat
   ```

3. **Test GPU compatibility:**
   ```bash
   .\test_gpu.bat
   ```

## GPU Support

This project is optimized for NVIDIA RTX 5000 series (Blackwell architecture) but supports any CUDA-compatible GPU:

- **RTX 5000 series**: Full 120 SM utilization with PyTorch 2.7.0+cu128
- **Other NVIDIA GPUs**: Automatic detection and optimization
- **CPU fallback**: Automatic fallback if GPU unavailable

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Include docstrings for functions and classes
- Keep GPU memory management clean with proper `torch.cuda.empty_cache()` calls

## Testing

Before submitting changes:

1. **Test GPU functionality:**
   ```bash
   .\test_gpu.bat
   ```

2. **Test the main application:**
   ```bash
   .\run.bat
   ```

3. **Test with different video formats:** MP4, AVI, MOV, MKV

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Reporting Issues

When reporting issues, please include:

- Operating system and version
- GPU model and driver version
- Python version
- PyTorch version
- Error messages and stack traces
- Steps to reproduce the issue

## Feature Requests

We welcome feature requests! Please:

- Check existing issues first
- Describe the use case clearly
- Explain how it would benefit users
- Consider GPU performance implications

## GPU-Specific Contributions

If contributing GPU-related features:

- Test on multiple GPU architectures if possible
- Include proper error handling for GPU failures
- Use `torch.cuda.is_available()` checks
- Implement CPU fallbacks
- Consider memory usage optimization

Thank you for contributing! 🚀
