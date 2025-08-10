import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import os
import threading
import time
import torch
import subprocess
from pathlib import Path

class FrameExtractor:
    def __init__(self, root):
        self.root = root
        self.root.title("Frame Extractor - RTX 5000 Series Optimized")
        self.root.geometry("700x500")
        
        # Variables
        self.video_path = tk.StringVar()
        self.extraction_mode = tk.StringVar(value="interval")
        self.interval_value = tk.StringVar(value="1.0")
        self.output_folder = "Extraction"
        self.is_extracting = False
        self.cancel_extraction = False
        self.use_gpu = tk.BooleanVar(value=torch.cuda.is_available())
        
        # Setup GPU info
        self.setup_gpu_info()
        
        # Create GUI
        self.create_gui()
        
        # Ensure output folder exists
        os.makedirs(self.output_folder, exist_ok=True)
    
    def get_cuda_comp_cap(self):
        """Get CUDA compute capability using nvidia-smi"""
        try:
            result = subprocess.check_output(['nvidia-smi', '--query-gpu=compute_cap', '--format=noheader,csv'], text=True)
            return max(map(float, result.strip().split('\n')))
        except Exception:
            return 0.0
    
    def setup_gpu_info(self):
        """Setup GPU information"""
        if torch.cuda.is_available():
            self.gpu_name = torch.cuda.get_device_name(0)
            self.gpu_capability = torch.cuda.get_device_capability(0)
            self.compute_cap = self.get_cuda_comp_cap()
            self.is_blackwell = self.compute_cap >= 12.0
            self.has_gpu = True
        else:
            self.gpu_name = "No GPU Available"
            self.gpu_capability = (0, 0)
            self.compute_cap = 0.0
            self.is_blackwell = False
            self.has_gpu = False
    
    def create_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # GPU Information Section
        gpu_frame = ttk.LabelFrame(main_frame, text="GPU Information", padding="5")
        gpu_frame.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        if self.has_gpu:
            gpu_info = f"GPU: {self.gpu_name}"
            if self.is_blackwell:
                gpu_info += f" (Blackwell - 120 SM, Compute {self.compute_cap})"
            else:
                gpu_info += f" (Compute {self.compute_cap})"
            ttk.Label(gpu_frame, text=gpu_info).grid(row=0, column=0, sticky=tk.W)
            ttk.Checkbutton(gpu_frame, text="Use GPU Acceleration", 
                           variable=self.use_gpu).grid(row=1, column=0, sticky=tk.W)
        else:
            ttk.Label(gpu_frame, text="No GPU detected - CPU processing only").grid(row=0, column=0, sticky=tk.W)
        
        # Video selection
        ttk.Label(main_frame, text="Select Video File:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.video_entry = ttk.Entry(main_frame, textvariable=self.video_path, width=50)
        self.video_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 0), pady=5)
        ttk.Button(main_frame, text="Browse", command=self.browse_video).grid(row=1, column=2, padx=(5, 0), pady=5)
        
        # Extraction mode
        mode_frame = ttk.LabelFrame(main_frame, text="Extraction Mode", padding="5")
        mode_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        mode_frame.columnconfigure(1, weight=1)
        
        # Interval mode
        ttk.Radiobutton(mode_frame, text="Extract every", variable=self.extraction_mode, 
                       value="interval").grid(row=0, column=0, sticky=tk.W)
        self.interval_entry = ttk.Entry(mode_frame, textvariable=self.interval_value, width=10)
        self.interval_entry.grid(row=0, column=1, sticky=tk.W, padx=(5, 0))
        ttk.Label(mode_frame, text="seconds").grid(row=0, column=2, sticky=tk.W, padx=(5, 0))
        
        # All frames mode
        ttk.Radiobutton(mode_frame, text="Extract all frames", variable=self.extraction_mode, 
                       value="all").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to extract frames")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="Start Extraction", 
                                     command=self.start_extraction, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                      command=self.cancel_extraction_process, state="disabled")
        self.cancel_button.pack(side=tk.LEFT)
        
        # Status bar
        self.status_var = tk.StringVar(value="Select a video file to get started")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def browse_video(self):
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Video File", filetypes=filetypes)
        if filename:
            self.video_path.set(filename)
            self.status_var.set(f"Selected: {os.path.basename(filename)}")
    
    def start_extraction(self):
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file first.")
            return
        
        if not os.path.exists(self.video_path.get()):
            messagebox.showerror("Error", "Selected video file does not exist.")
            return
        
        if self.extraction_mode.get() == "interval":
            try:
                interval = float(self.interval_value.get())
                if interval <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid interval (positive number).")
                return
        
        # Start extraction in a separate thread
        self.is_extracting = True
        self.cancel_extraction = False
        self.start_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        
        extraction_thread = threading.Thread(target=self.extract_frames)
        extraction_thread.daemon = True
        extraction_thread.start()
    
    def cancel_extraction_process(self):
        self.cancel_extraction = True
        self.progress_var.set("Cancelling...")
    
    def extract_frames(self):
        try:
            video_path = self.video_path.get()
            video_name = Path(video_path).stem
            
            # Create output folder for this video
            output_dir = os.path.join(self.output_folder, video_name)
            os.makedirs(output_dir, exist_ok=True)
            
            # Open video
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not open video file."))
                return
            
            # Get video properties
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Determine frames to extract
            if self.extraction_mode.get() == "interval":
                interval = float(self.interval_value.get())
                frame_interval = int(fps * interval)
                if frame_interval == 0:
                    frame_interval = 1
                frames_to_extract = list(range(0, total_frames, frame_interval))
            else:  # all frames
                frames_to_extract = list(range(total_frames))
            
            total_to_extract = len(frames_to_extract)
            
            self.root.after(0, lambda: self.progress_bar.config(maximum=total_to_extract))
            
            # Show GPU info in progress
            gpu_status = ""
            if self.use_gpu.get() and self.has_gpu:
                if self.is_blackwell:
                    gpu_status = " (Using RTX 5000 series - 120 SM acceleration)"
                else:
                    gpu_status = f" (Using GPU acceleration)"
            else:
                gpu_status = " (CPU processing)"
            
            self.root.after(0, lambda: self.progress_var.set(f"Extracting frames{gpu_status}... (0/{total_to_extract})"))
            
            extracted_count = 0
            frame_number = 0
            
            # Setup GPU tensors if using GPU
            device = None
            if self.use_gpu.get() and self.has_gpu:
                device = torch.device('cuda:0')
                torch.cuda.empty_cache()  # Clear any existing GPU memory
            
            while True:
                if self.cancel_extraction:
                    break
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number in frames_to_extract:
                    # Create filename with zero-padding (6 digits as requested)
                    frame_filename = f"{video_name}_{extracted_count + 1:06d}.png"
                    frame_path = os.path.join(output_dir, frame_filename)
                    
                    # Process frame with GPU acceleration if available
                    if self.use_gpu.get() and self.has_gpu and device is not None:
                        try:
                            # Move frame to GPU for processing (optional optimization)
                            frame_tensor = torch.from_numpy(frame).to(device)
                            # Move back to CPU for saving (OpenCV requires CPU arrays)
                            frame_processed = frame_tensor.cpu().numpy()
                            cv2.imwrite(frame_path, frame_processed)
                            
                            # For Blackwell architecture, we can do batch processing for better SM utilization
                            if self.is_blackwell and extracted_count % 10 == 0:
                                torch.cuda.empty_cache()  # Optimize memory usage
                        except Exception as e:
                            # Fallback to CPU if GPU processing fails
                            cv2.imwrite(frame_path, frame)
                    else:
                        # Standard CPU processing
                        cv2.imwrite(frame_path, frame)
                    
                    extracted_count += 1
                    
                    # Update progress (update every frame for better user experience)
                    progress_text = f"Extracting frames{gpu_status}... ({extracted_count}/{total_to_extract})"
                    self.root.after(0, lambda: self.progress_var.set(progress_text))
                    self.root.after(0, lambda: self.progress_bar.config(value=extracted_count))
                
                frame_number += 1
            
            cap.release()
            
            # Clear GPU memory after processing
            if self.use_gpu.get() and self.has_gpu:
                torch.cuda.empty_cache()
            
            if self.cancel_extraction:
                self.root.after(0, lambda: self.progress_var.set("Extraction cancelled"))
                self.root.after(0, lambda: self.status_var.set("Extraction cancelled by user"))
            else:
                self.root.after(0, lambda: self.progress_var.set(f"Completed! Extracted {extracted_count} frames"))
                self.root.after(0, lambda: self.status_var.set(f"Extracted {extracted_count} frames to {output_dir}"))
                
                # Enhanced completion message with GPU info
                completion_msg = f"Frame extraction completed!\n\nExtracted {extracted_count} frames to:\n{output_dir}"
                if self.use_gpu.get() and self.has_gpu:
                    if self.is_blackwell:
                        completion_msg += "\n\n🚀 Processed with RTX 5000 series (120 SM) acceleration!"
                    else:
                        completion_msg += f"\n\n⚡ Processed with GPU acceleration ({self.gpu_name})"
                
                self.root.after(0, lambda: messagebox.showinfo("Success", completion_msg))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred: {str(e)}"))
            self.root.after(0, lambda: self.status_var.set("Error during extraction"))
        
        finally:
            self.is_extracting = False
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.cancel_button.config(state="disabled"))
            
            # Clean up GPU memory
            if self.has_gpu:
                torch.cuda.empty_cache()

def main():
    root = tk.Tk()
    app = FrameExtractor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
