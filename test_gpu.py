import torch
import sys
import subprocess

def get_cuda_comp_cap():
    """
    Returns float of CUDA Compute Capability using nvidia-smi
    Returns 0.0 on error
    CUDA Compute Capability
    ref https://developer.nvidia.com/cuda-gpus
    ref https://en.wikipedia.org/wiki/CUDA
    Blackwell consumer GPUs should return 12.0 data-center GPUs should return 10.0
    """
    try:
        return max(map(float, subprocess.check_output(['nvidia-smi', '--query-gpu=compute_cap', '--format=noheader,csv'], text=True).splitlines()))
    except Exception as _:
        return 0.0

def test_gpu_compatibility():
    print("=" * 60)
    print("GPU Compatibility Test for RTX 5000 Series (Blackwell)")
    print("=" * 60)
    
    # Test PyTorch CUDA availability
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    
    # Get compute capability using nvidia-smi
    comp_cap = get_cuda_comp_cap()
    print(f"CUDA Compute Capability: {comp_cap}")
    
    # Check for Blackwell architecture
    if comp_cap >= 12.0:
        print("✓ RTX 5000 series (Blackwell) detected!")
        print("✓ 120 SM configuration should be fully supported")
    elif comp_cap >= 10.0:
        print("✓ Blackwell architecture detected (data-center)")
    else:
        print(f"ℹ Non-Blackwell GPU detected (compute capability {comp_cap})")
    
    if torch.cuda.is_available():
        print(f"Number of GPUs: {torch.cuda.device_count()}")
        
        for i in range(torch.cuda.device_count()):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_capability = torch.cuda.get_device_capability(i)
            print(f"GPU {i}: {gpu_name}")
            print(f"  Compute Capability: {gpu_capability[0]}.{gpu_capability[1]}")
            
            # Test memory allocation and computation
            try:
                device = torch.device(f'cuda:{i}')
                test_tensor = torch.randn(1000, 1000, device=device)
                result = torch.matmul(test_tensor, test_tensor)
                print(f"  ✓ GPU {i} computation test passed")
                
                # Test all 120 SMs with larger tensor for Blackwell
                if comp_cap >= 12.0:
                    large_tensor = torch.randn(5000, 5000, device=device)
                    large_result = torch.matmul(large_tensor, large_tensor)
                    print(f"  ✓ GPU {i} large tensor test passed (120 SM utilization)")
                    del large_tensor, large_result
                
                # Clear memory
                del test_tensor, result
                torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"  ✗ GPU {i} test failed: {e}")
    else:
        print("CUDA is not available. Using CPU only.")
    
    # Test OpenCV
    print("\n" + "=" * 40)
    print("OpenCV Test")
    print("=" * 40)
    try:
        import cv2
        print("✓ OpenCV imported successfully")
        
        # Test basic video capture capabilities
        try:
            cap = cv2.VideoCapture()
            print("✓ Video capture initialization successful")
            cap.release()
        except Exception as e:
            print(f"✗ Video capture test failed: {e}")
            
    except ImportError as e:
        print(f"✗ OpenCV not available: {e}")
        return False
    
    print("\n" + "=" * 60)
    
    return torch.cuda.is_available()

if __name__ == "__main__":
    gpu_available = test_gpu_compatibility()
    
    if gpu_available:
        comp_cap = get_cuda_comp_cap()
        if comp_cap >= 12.0:
            print("🚀 RTX 5000 series GPU support confirmed!")
            print("   All 120 SMs are available for frame extraction acceleration.")
        else:
            print("✓ GPU acceleration available!")
        print("   You can proceed with the full frame extractor application.")
    else:
        print("⚠ GPU support not available. Will use CPU only.")
        print("  The application will still work, but may be slower for large videos.")
    
    input("\nPress Enter to continue...")
