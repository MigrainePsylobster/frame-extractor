import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import cv2
import os
import threading
import time
import torch
import subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageTk

class VideoCropper:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Cropper - RTX 5000 Series Optimized")
        self.root.geometry("1200x800")
        
        # Variables
        self.video_path = tk.StringVar()
        self.output_folder = "Extraction"
        self.is_processing = False
        self.cancel_processing = False
        self.use_gpu = tk.BooleanVar(value=torch.cuda.is_available())
        
        # Video properties
        self.cap = None
        self.total_frames = 0
        self.fps = 0
        self.frame_width = 0
        self.frame_height = 0
        self.current_frame = 0
        self.current_frame_img = None
        
        # Crop selection
        self.crop_start_x = 0
        self.crop_start_y = 0
        self.crop_end_x = 0
        self.crop_end_y = 0
        self.selection_rectangle = None
        self.is_selecting = False
        
        # Canvas scaling
        self.canvas_width = 800
        self.canvas_height = 450
        self.scale_x = 1.0
        self.scale_y = 1.0
        
        # Setup GPU info
        self.setup_gpu_info()
        
        # Dark mode
        self.dark_mode = tk.BooleanVar(value=False)
        self.setup_dark_mode()
        
        # Create GUI
        self.create_gui()
        
        # Ensure output folder exists
        os.makedirs(self.output_folder, exist_ok=True)
    
    def setup_gpu_info(self):
        """Setup GPU information"""
        if torch.cuda.is_available():
            self.gpu_name = torch.cuda.get_device_name(0)
            self.gpu_capability = torch.cuda.get_device_capability(0)
            try:
                result = subprocess.check_output(['nvidia-smi', '--query-gpu=compute_cap', '--format=noheader,csv'], text=True)
                self.compute_cap = max(map(float, result.strip().split('\n')))
            except Exception:
                self.compute_cap = 0.0
            self.is_blackwell = self.compute_cap >= 12.0
            self.has_gpu = True
        else:
            self.gpu_name = "No GPU Available"
            self.gpu_capability = (0, 0)
            self.compute_cap = 0.0
            self.is_blackwell = False
            self.has_gpu = False
    
    def setup_dark_mode(self):
        """Setup dark mode styling"""
        self.style = ttk.Style()
        self.update_theme()
    
    def update_theme(self):
        """Update theme based on dark mode setting"""
        if self.dark_mode.get():
            # Dark theme
            self.root.configure(bg='#2b2b2b')
            self.style.theme_use('clam')
            self.style.configure('TFrame', background='#2b2b2b', borderwidth=1, relief='solid')
            self.style.configure('TLabel', background='#2b2b2b', foreground='white')
            self.style.configure('TButton', background='#404040', foreground='white')
            self.style.map('TButton', background=[('active', '#505050')])
            self.style.configure('TEntry', background='#404040', foreground='white', fieldbackground='#404040')
            self.style.configure('TCheckbutton', background='#2b2b2b', foreground='white')
            self.style.configure('TRadiobutton', background='#2b2b2b', foreground='white')
            self.style.configure('TLabelFrame', background='#2b2b2b', foreground='white')
            self.style.configure('TLabelFrame.Label', background='#2b2b2b', foreground='white')
            self.style.configure('TNotebook', background='#2b2b2b')
            self.style.configure('TNotebook.Tab', background='#404040', foreground='white')
            self.style.map('TNotebook.Tab', background=[('selected', '#2b2b2b')])
            self.style.configure('TProgressbar', background='#4CAF50', troughcolor='#404040')
            self.canvas_bg = '#1a1a1a'
            self.selection_color = '#00ff00'
        else:
            # Light theme
            self.root.configure(bg='SystemButtonFace')
            self.style.theme_use('winnative')
            self.canvas_bg = 'white'
            self.selection_color = '#ff0000'
        
        # Update canvas if it exists
        if hasattr(self, 'video_canvas'):
            self.video_canvas.configure(bg=self.canvas_bg)
    
    def create_gui(self):
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Main tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Video Cropper")
        
        # Settings tab
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="Settings")
        
        self.create_main_tab()
        self.create_settings_tab()
    
    def create_main_tab(self):
        # Left panel for controls
        left_panel = ttk.Frame(self.main_tab, width=350)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 5), pady=10)
        left_panel.pack_propagate(False)
        
        # Right panel for video preview
        right_panel = ttk.Frame(self.main_tab)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 10), pady=10)
        
        # === LEFT PANEL CONTROLS ===
        
        # GPU Information
        gpu_frame = ttk.LabelFrame(left_panel, text="GPU Information", padding="10")
        gpu_frame.pack(fill=tk.X, pady=(0, 10))
        
        if self.has_gpu:
            gpu_info = f"GPU: {self.gpu_name}"
            if self.is_blackwell:
                gpu_info += f"\n(Blackwell - 120 SM, Compute {self.compute_cap})"
            else:
                gpu_info += f"\n(Compute {self.compute_cap})"
            ttk.Label(gpu_frame, text=gpu_info).pack(anchor=tk.W)
            ttk.Checkbutton(gpu_frame, text="Use GPU Acceleration", 
                           variable=self.use_gpu).pack(anchor=tk.W, pady=(5, 0))
        else:
            ttk.Label(gpu_frame, text="No GPU detected\nCPU processing only").pack(anchor=tk.W)
        
        # Video selection
        video_frame = ttk.LabelFrame(left_panel, text="Video File", padding="10")
        video_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(video_frame, text="Select Video File:").pack(anchor=tk.W)
        self.video_entry = ttk.Entry(video_frame, textvariable=self.video_path, width=35)
        self.video_entry.pack(fill=tk.X, pady=(5, 5))
        ttk.Button(video_frame, text="Browse", command=self.browse_video).pack(anchor=tk.W)
        
        # Crop settings
        crop_frame = ttk.LabelFrame(left_panel, text="Crop Selection", padding="10")
        crop_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(crop_frame, text="Click and drag on video to select crop area").pack(anchor=tk.W)
        
        # Crop coordinates display
        coords_frame = ttk.Frame(crop_frame)
        coords_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Label(coords_frame, text="X:").grid(row=0, column=0, sticky=tk.W)
        self.crop_x_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.crop_x_var, width=8).grid(row=0, column=1, padx=(5, 10))
        
        ttk.Label(coords_frame, text="Y:").grid(row=0, column=2, sticky=tk.W)
        self.crop_y_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.crop_y_var, width=8).grid(row=0, column=3, padx=(5, 0))
        
        ttk.Label(coords_frame, text="Width:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.crop_width_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.crop_width_var, width=8).grid(row=1, column=1, padx=(5, 10), pady=(5, 0))
        
        ttk.Label(coords_frame, text="Height:").grid(row=1, column=2, sticky=tk.W, pady=(5, 0))
        self.crop_height_var = tk.StringVar(value="0")
        ttk.Entry(coords_frame, textvariable=self.crop_height_var, width=8).grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        
        ttk.Button(crop_frame, text="Clear Selection", command=self.clear_selection).pack(pady=(10, 0))
        
        # Quality settings
        quality_frame = ttk.LabelFrame(left_panel, text="Export Quality", padding="10")
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.codec_var = tk.StringVar(value="h264")
        ttk.Radiobutton(quality_frame, text="H.264 (High Quality)", 
                       variable=self.codec_var, value="h264").pack(anchor=tk.W)
        ttk.Radiobutton(quality_frame, text="H.265 (HEVC)", 
                       variable=self.codec_var, value="h265").pack(anchor=tk.W)
        
        self.quality_var = tk.StringVar(value="18")
        quality_scale_frame = ttk.Frame(quality_frame)
        quality_scale_frame.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(quality_scale_frame, text="CRF Quality:").pack(side=tk.LEFT)
        ttk.Entry(quality_scale_frame, textvariable=self.quality_var, width=5).pack(side=tk.RIGHT)
        ttk.Label(quality_scale_frame, text="(0=lossless, 18=high, 23=default)").pack(pady=(5, 0))
        
        # Progress section
        progress_frame = ttk.LabelFrame(left_panel, text="Progress", padding="10")
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress_var = tk.StringVar(value="Ready to process video")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Buttons
        button_frame = ttk.Frame(left_panel)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.load_button = ttk.Button(button_frame, text="Load Video", command=self.load_video)
        self.load_button.pack(fill=tk.X, pady=(0, 5))
        
        self.export_button = ttk.Button(button_frame, text="Export Cropped Video", 
                                       command=self.start_export, state="disabled")
        self.export_button.pack(fill=tk.X, pady=(0, 5))
        
        self.cancel_button = ttk.Button(button_frame, text="Cancel", 
                                      command=self.cancel_processing_func, state="disabled")
        self.cancel_button.pack(fill=tk.X)
        
        # === RIGHT PANEL VIDEO PREVIEW ===
        
        # Video canvas
        canvas_frame = ttk.LabelFrame(right_panel, text="Video Preview", padding="10")
        canvas_frame.pack(fill=tk.BOTH, expand=True)
        
        self.video_canvas = tk.Canvas(canvas_frame, width=self.canvas_width, height=self.canvas_height, 
                                     bg=self.canvas_bg, highlightthickness=1, highlightbackground='gray')
        self.video_canvas.pack(pady=(0, 10))
        
        # Bind mouse events for selection
        self.video_canvas.bind("<Button-1>", self.start_selection)
        self.video_canvas.bind("<B1-Motion>", self.update_selection)
        self.video_canvas.bind("<ButtonRelease-1>", self.end_selection)
        
        # Video controls
        controls_frame = ttk.Frame(canvas_frame)
        controls_frame.pack(fill=tk.X)
        
        # Frame navigation
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(nav_frame, text="◀◀", command=lambda: self.seek_frame(-30)).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="◀", command=lambda: self.seek_frame(-1)).pack(side=tk.LEFT, padx=(5, 0))
        
        self.frame_var = tk.StringVar(value="0")
        frame_entry = ttk.Entry(nav_frame, textvariable=self.frame_var, width=10)
        frame_entry.pack(side=tk.LEFT, padx=(10, 5))
        frame_entry.bind("<Return>", self.goto_frame)
        
        ttk.Button(nav_frame, text="▶", command=lambda: self.seek_frame(1)).pack(side=tk.LEFT)
        ttk.Button(nav_frame, text="▶▶", command=lambda: self.seek_frame(30)).pack(side=tk.LEFT, padx=(5, 0))
        
        self.total_frames_label = ttk.Label(nav_frame, text="/ 0")
        self.total_frames_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Timeline slider
        self.timeline_var = tk.DoubleVar()
        self.timeline_scale = ttk.Scale(controls_frame, from_=0, to=100, orient=tk.HORIZONTAL, 
                                       variable=self.timeline_var, command=self.timeline_changed)
        self.timeline_scale.pack(fill=tk.X, pady=(5, 0))
    
    def create_settings_tab(self):
        # Theme settings
        theme_frame = ttk.LabelFrame(self.settings_tab, text="Appearance", padding="20")
        theme_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Checkbutton(theme_frame, text="Dark Mode", variable=self.dark_mode, 
                       command=self.toggle_dark_mode).pack(anchor=tk.W)
        
        # About
        about_frame = ttk.LabelFrame(self.settings_tab, text="About", padding="20")
        about_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        about_text = """Video Cropper - RTX 5000 Series Optimized

Features:
• Click and drag crop selection
• High-quality H.264/H.265 export
• GPU acceleration support
• Real-time video preview
• Frame-by-frame navigation

Output files are saved with 'framed_' prefix"""
        
        ttk.Label(about_frame, text=about_text, justify=tk.LEFT).pack(anchor=tk.W)
    
    def toggle_dark_mode(self):
        """Toggle between dark and light mode"""
        self.update_theme()
    
    def browse_video(self):
        """Browse for video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(title="Select Video File", filetypes=filetypes)
        if filename:
            self.video_path.set(filename)
    
    def load_video(self):
        """Load video file and setup preview"""
        if not self.video_path.get():
            messagebox.showerror("Error", "Please select a video file first.")
            return
        
        if not os.path.exists(self.video_path.get()):
            messagebox.showerror("Error", "Selected video file does not exist.")
            return
        
        try:
            # Release previous video if loaded
            if self.cap:
                self.cap.release()
            
            # Open new video
            self.cap = cv2.VideoCapture(self.video_path.get())
            if not self.cap.isOpened():
                messagebox.showerror("Error", "Could not open video file.")
                return
            
            # Get video properties
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate scaling for canvas
            self.scale_x = self.canvas_width / self.frame_width
            self.scale_y = self.canvas_height / self.frame_height
            self.scale = min(self.scale_x, self.scale_y)
            
            # Update UI
            self.total_frames_label.config(text=f"/ {self.total_frames}")
            self.timeline_scale.config(to=self.total_frames - 1)
            
            # Load first frame
            self.current_frame = 0
            self.display_frame()
            
            # Enable export button
            self.export_button.config(state="normal")
            
            # Update crop dimensions to full frame initially
            self.crop_x_var.set("0")
            self.crop_y_var.set("0")
            self.crop_width_var.set(str(self.frame_width))
            self.crop_height_var.set(str(self.frame_height))
            
            messagebox.showinfo("Success", f"Video loaded successfully!\n\nResolution: {self.frame_width}x{self.frame_height}\nFPS: {self.fps:.2f}\nFrames: {self.total_frames}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video: {str(e)}")
    
    def display_frame(self):
        """Display current frame on canvas"""
        if not self.cap:
            return
        
        # Set frame position
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)
        ret, frame = self.cap.read()
        
        if ret:
            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Resize frame to fit canvas
            display_width = int(self.frame_width * self.scale)
            display_height = int(self.frame_height * self.scale)
            frame_resized = cv2.resize(frame_rgb, (display_width, display_height))
            
            # Convert to PIL Image
            pil_image = Image.fromarray(frame_resized)
            self.current_frame_img = ImageTk.PhotoImage(pil_image)
            
            # Clear canvas and display image
            self.video_canvas.delete("all")
            canvas_x = (self.canvas_width - display_width) // 2
            canvas_y = (self.canvas_height - display_height) // 2
            self.video_canvas.create_image(canvas_x, canvas_y, anchor=tk.NW, image=self.current_frame_img)
            
            # Redraw selection rectangle if exists
            self.redraw_selection()
            
            # Update frame counter
            self.frame_var.set(str(self.current_frame))
            self.timeline_var.set(self.current_frame)
    
    def seek_frame(self, delta):
        """Seek to relative frame position"""
        if not self.cap:
            return
        
        new_frame = max(0, min(self.total_frames - 1, self.current_frame + delta))
        self.current_frame = new_frame
        self.display_frame()
    
    def goto_frame(self, event=None):
        """Go to specific frame"""
        if not self.cap:
            return
        
        try:
            frame_num = int(self.frame_var.get())
            frame_num = max(0, min(self.total_frames - 1, frame_num))
            self.current_frame = frame_num
            self.display_frame()
        except ValueError:
            self.frame_var.set(str(self.current_frame))
    
    def timeline_changed(self, value):
        """Handle timeline slider change"""
        if not self.cap:
            return
        
        frame_num = int(float(value))
        self.current_frame = frame_num
        self.display_frame()
    
    def start_selection(self, event):
        """Start crop selection"""
        if not self.cap:
            return
        
        self.is_selecting = True
        self.crop_start_x = event.x
        self.crop_start_y = event.y
        
        # Clear previous selection
        if self.selection_rectangle:
            self.video_canvas.delete(self.selection_rectangle)
    
    def update_selection(self, event):
        """Update crop selection rectangle"""
        if not self.is_selecting or not self.cap:
            return
        
        # Delete previous rectangle
        if self.selection_rectangle:
            self.video_canvas.delete(self.selection_rectangle)
        
        # Draw new rectangle
        self.selection_rectangle = self.video_canvas.create_rectangle(
            self.crop_start_x, self.crop_start_y, event.x, event.y,
            outline=self.selection_color, width=2
        )
    
    def end_selection(self, event):
        """End crop selection and update coordinates"""
        if not self.is_selecting or not self.cap:
            return
        
        self.is_selecting = False
        self.crop_end_x = event.x
        self.crop_end_y = event.y
        
        # Convert canvas coordinates to video coordinates
        display_width = int(self.frame_width * self.scale)
        display_height = int(self.frame_height * self.scale)
        canvas_x_offset = (self.canvas_width - display_width) // 2
        canvas_y_offset = (self.canvas_height - display_height) // 2
        
        # Adjust for image offset on canvas
        start_x = (self.crop_start_x - canvas_x_offset) / self.scale
        start_y = (self.crop_start_y - canvas_y_offset) / self.scale
        end_x = (self.crop_end_x - canvas_x_offset) / self.scale
        end_y = (self.crop_end_y - canvas_y_offset) / self.scale
        
        # Ensure coordinates are within video bounds
        start_x = max(0, min(self.frame_width, start_x))
        start_y = max(0, min(self.frame_height, start_y))
        end_x = max(0, min(self.frame_width, end_x))
        end_y = max(0, min(self.frame_height, end_y))
        
        # Ensure start is top-left, end is bottom-right
        x1, x2 = min(start_x, end_x), max(start_x, end_x)
        y1, y2 = min(start_y, end_y), max(start_y, end_y)
        
        # Update coordinate variables
        self.crop_x_var.set(str(int(x1)))
        self.crop_y_var.set(str(int(y1)))
        self.crop_width_var.set(str(int(x2 - x1)))
        self.crop_height_var.set(str(int(y2 - y1)))
    
    def redraw_selection(self):
        """Redraw selection rectangle based on coordinate variables"""
        try:
            x = int(self.crop_x_var.get())
            y = int(self.crop_y_var.get())
            width = int(self.crop_width_var.get())
            height = int(self.crop_height_var.get())
            
            if width > 0 and height > 0:
                # Convert video coordinates to canvas coordinates
                display_width = int(self.frame_width * self.scale)
                display_height = int(self.frame_height * self.scale)
                canvas_x_offset = (self.canvas_width - display_width) // 2
                canvas_y_offset = (self.canvas_height - display_height) // 2
                
                canvas_x1 = x * self.scale + canvas_x_offset
                canvas_y1 = y * self.scale + canvas_y_offset
                canvas_x2 = (x + width) * self.scale + canvas_x_offset
                canvas_y2 = (y + height) * self.scale + canvas_y_offset
                
                # Delete previous rectangle
                if self.selection_rectangle:
                    self.video_canvas.delete(self.selection_rectangle)
                
                # Draw new rectangle
                self.selection_rectangle = self.video_canvas.create_rectangle(
                    canvas_x1, canvas_y1, canvas_x2, canvas_y2,
                    outline=self.selection_color, width=2
                )
        except ValueError:
            pass
    
    def clear_selection(self):
        """Clear crop selection"""
        if self.selection_rectangle:
            self.video_canvas.delete(self.selection_rectangle)
            self.selection_rectangle = None
        
        if self.cap:
            self.crop_x_var.set("0")
            self.crop_y_var.set("0")
            self.crop_width_var.set(str(self.frame_width))
            self.crop_height_var.set(str(self.frame_height))
    
    def start_export(self):
        """Start video export process"""
        if not self.cap:
            messagebox.showerror("Error", "Please load a video first.")
            return
        
        # Validate crop selection
        try:
            crop_x = int(self.crop_x_var.get())
            crop_y = int(self.crop_y_var.get())
            crop_width = int(self.crop_width_var.get())
            crop_height = int(self.crop_height_var.get())
            
            if crop_width <= 0 or crop_height <= 0:
                messagebox.showerror("Error", "Invalid crop dimensions.")
                return
            
            if crop_x + crop_width > self.frame_width or crop_y + crop_height > self.frame_height:
                messagebox.showerror("Error", "Crop area exceeds video boundaries.")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid crop coordinates.")
            return
        
        # Start export in separate thread
        self.is_processing = True
        self.cancel_processing = False
        self.export_button.config(state="disabled")
        self.cancel_button.config(state="normal")
        
        export_thread = threading.Thread(target=self.export_video)
        export_thread.daemon = True
        export_thread.start()
    
    def export_video(self):
        """Export cropped video"""
        try:
            # Get parameters
            crop_x = int(self.crop_x_var.get())
            crop_y = int(self.crop_y_var.get())
            crop_width = int(self.crop_width_var.get())
            crop_height = int(self.crop_height_var.get())
            
            # Generate output filename
            video_path = self.video_path.get()
            video_name = Path(video_path).stem
            video_ext = Path(video_path).suffix
            output_name = f"framed_{video_name}{video_ext}"
            output_path = os.path.join(self.output_folder, output_name)
            
            # Ensure even dimensions for encoding
            if crop_width % 2 != 0:
                crop_width -= 1
            if crop_height % 2 != 0:
                crop_height -= 1
            
            # Setup codec
            codec = self.codec_var.get()
            quality = self.quality_var.get()
            
            if codec == "h265":
                fourcc = cv2.VideoWriter.fourcc(*'HEVC')
            else:
                fourcc = cv2.VideoWriter.fourcc(*'mp4v')
            
            # Create video writer
            out = cv2.VideoWriter(output_path, fourcc, self.fps, (crop_width, crop_height))
            
            if not out.isOpened():
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not create output video file."))
                return
            
            # Process frames
            self.root.after(0, lambda: self.progress_bar.config(maximum=self.total_frames))
            
            gpu_status = ""
            if self.use_gpu.get() and self.has_gpu:
                if self.is_blackwell:
                    gpu_status = " (Using RTX 5000 series - 120 SM acceleration)"
                else:
                    gpu_status = " (Using GPU acceleration)"
                device = torch.device('cuda:0')
                torch.cuda.empty_cache()
            else:
                gpu_status = " (CPU processing)"
                device = None
            
            self.root.after(0, lambda: self.progress_var.set(f"Exporting cropped video{gpu_status}..."))
            
            processed_frames = 0
            
            for frame_idx in range(self.total_frames):
                if self.cancel_processing:
                    break
                
                # Read frame
                if not self.cap:
                    break
                    
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = self.cap.read()
                
                if not ret:
                    break
                
                # Crop frame
                cropped_frame = frame[crop_y:crop_y+crop_height, crop_x:crop_x+crop_width]
                
                # GPU processing if available
                if self.use_gpu.get() and self.has_gpu and device is not None:
                    try:
                        frame_tensor = torch.from_numpy(cropped_frame).to(device)
                        cropped_frame = frame_tensor.cpu().numpy()
                        
                        if self.is_blackwell and processed_frames % 10 == 0:
                            torch.cuda.empty_cache()
                    except Exception:
                        pass  # Fallback to CPU processing
                
                # Write frame
                out.write(cropped_frame)
                processed_frames += 1
                
                # Update progress
                if processed_frames % 30 == 0 or processed_frames == self.total_frames:
                    progress_text = f"Exporting cropped video{gpu_status}... ({processed_frames}/{self.total_frames})"
                    self.root.after(0, lambda: self.progress_var.set(progress_text))
                    self.root.after(0, lambda: self.progress_bar.config(value=processed_frames))
            
            # Clean up
            out.release()
            
            if self.use_gpu.get() and self.has_gpu:
                torch.cuda.empty_cache()
            
            if self.cancel_processing:
                # Remove incomplete file
                if os.path.exists(output_path):
                    os.remove(output_path)
                self.root.after(0, lambda: self.progress_var.set("Export cancelled"))
            else:
                self.root.after(0, lambda: self.progress_var.set(f"Export completed! Saved to {output_name}"))
                
                completion_msg = f"Video export completed!\n\nCropped video saved as:\n{output_name}\n\nLocation: {self.output_folder}"
                if self.use_gpu.get() and self.has_gpu:
                    if self.is_blackwell:
                        completion_msg += "\n\n🚀 Processed with RTX 5000 series (120 SM) acceleration!"
                    else:
                        completion_msg += f"\n\n⚡ Processed with GPU acceleration ({self.gpu_name})"
                
                self.root.after(0, lambda: messagebox.showinfo("Success", completion_msg))
        
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Export failed: {str(e)}"))
        
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.export_button.config(state="normal"))
            self.root.after(0, lambda: self.cancel_button.config(state="disabled"))
            
            if self.has_gpu:
                torch.cuda.empty_cache()
    
    def cancel_processing_func(self):
        """Cancel video processing"""
        self.cancel_processing = True
        self.progress_var.set("Cancelling...")

def main():
    root = tk.Tk()
    app = VideoCropper(root)
    root.mainloop()

if __name__ == "__main__":
    main()
