# Python Built-ins
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dataclasses import dataclass
from pathlib import Path

# Project Packages
from constants import RAW_EXTENSIONS, GUI_RESAMPLE_OPTIONS
from image_lib import image_lib_shoutout
from project import ImageSettings, open_image, rotate_or_flip, resize_image

# External Libraries
from PIL import Image, ImageTk
import rawpy
from pillow_heif import register_heif_opener


def main():
    print("IMAGIC HAT 📸")
    image_lib_shoutout()
    app = GUI()
    app.mainloop()
    
    

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Imagic Hat 📸")
        self.state("zoomed") 
        self.geometry("1200x700")
        
        # State Data & Dataclass Initialization
        self.current_src_path = None
        self.original_pil_img = None
        self.processed_pil_img = None
        self.settings = ImageSettings() # Live dataclass instance
        
        # Layout weights (3 Column Architecture Grid)
        self.columnconfigure(0, weight=1, minsize=300)
        self.columnconfigure(1, weight=3, minsize=400)
        self.columnconfigure(2, weight=3, minsize=400)
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # COLUMN 1: LEFT SIDE (Controls & Settings Layout)
        # ----------------------------------------------------
        self.left_col = ttk.Frame(self, padding=10)
        self.left_col.grid(row=0, column=0, sticky="nsew")
        
        # Sub-Section A: File Picker UI Panel
        sec_file = ttk.LabelFrame(self.left_col, text=" 1. File Section ", padding=10)
        sec_file.pack(fill="x", pady=(0, 10))
        
        self.btn_browse = ttk.Button(sec_file, text="Load Image File", command=self.load_image_action)
        self.btn_browse.pack(fill="x", pady=5)
        
        self.lbl_file_name = ttk.Label(sec_file, text="No file loaded", font=("Arial", 9, "italic"), wraplength=260)
        self.lbl_file_name.pack(fill="x")

        # Sub-Section B: Magic Hat Status Box Asset Box
        sec_hat = ttk.LabelFrame(self.left_col, text=" 2. Magic Hat Status ", padding=10)
        sec_hat.pack(fill="x", pady=(0, 10))
        
        try:
            self.img_empty_hat = ImageTk.PhotoImage(Image.open("art/magic_hat_emptyx5.gif").resize((120, 120)))
            self.img_rabbit_hat = ImageTk.PhotoImage(Image.open("art/magic_hat_x5.gif").resize((120, 120)))
        except Exception:
            self.img_empty_hat = None
            self.img_rabbit_hat = None

        self.hat_visual_label = ttk.Label(sec_hat, image=self.img_empty_hat, text="🎩 Hat is Empty...", compound="top", font=("Arial", 10, "bold"))
        self.hat_visual_label.pack(pady=5)

        # Sub-Section C: Image Adjustments Input Matrix
        sec_settings = ttk.LabelFrame(self.left_col, text=" 3. Image Settings ", padding=10)
        sec_settings.pack(fill="both", expand=True)
        
        # Transformation selector Combobox
        ttk.Label(sec_settings, text="Rotation Matrix:").pack(anchor="w", pady=(5, 2))
        self.rotate_var = tk.StringVar(value="0")
        rotation_options = ["0", "90", "180", "270", "FLIP_LEFT_RIGHT", "FLIP_TOP_BOTTOM"]
        self.dropdown_rotate = ttk.Combobox(sec_settings, textvariable=self.rotate_var, values=rotation_options, state="readonly")
        self.dropdown_rotate.pack(fill="x", pady=(0, 15))
        self.dropdown_rotate.bind("<<ComboboxSelected>>", lambda e: self.sync_gui_to_dataclass())
        
        # Export Format Selection Combobox
        ttk.Label(sec_settings, text="Export Format:").pack(anchor="w", pady=(5, 2))
        self.format_var = tk.StringVar(value="JPEG")
        format_options = ["TIFF", "PNG", "JPEG", "WEBP", "GIF"]
        self.dropdown_format = ttk.Combobox(sec_settings, textvariable=self.format_var, values=format_options, state="readonly")
        self.dropdown_format.pack(fill="x", pady=(0, 15))
        self.dropdown_format.bind("<<ComboboxSelected>>", lambda e: self.sync_gui_to_dataclass())
        
        # Compression/Quality Parameter Slider Range Scale (1 to 12)
        ttk.Label(sec_settings, text="Quality Level (1-12):").pack(anchor="w")
        self.quality_var = tk.IntVar(value=12)
        self.lbl_quality_val = ttk.Label(sec_settings, text="12")
        self.lbl_quality_val.pack(anchor="e")
        
        self.slider_quality = ttk.Scale(sec_settings, from_=1, to=12, variable=self.quality_var, orient="horizontal", command=self.update_quality_slider)
        self.slider_quality.pack(fill="x", pady=(0, 15))
        
        # Bottom Utility Buttons Container Frame Layout
        btn_container = ttk.Frame(sec_settings)
        btn_container.pack(fill="x", side="bottom", pady=5)
        
        self.btn_revert = ttk.Button(btn_container, text="🔄 Reset Settings", state="disabled", command=self.revert_settings_action)
        self.btn_revert.pack(fill="x", pady=2)
        
        self.btn_close = ttk.Button(btn_container, text="❌ Close Image", state="disabled", command=self.confirm_close_action)
        self.btn_close.pack(fill="x", pady=2)

        # ----------------------------------------------------
        # COLUMN 2: MIDDLE (Dynamic Original Canvas View Frame)
        # ----------------------------------------------------
        self.mid_col = ttk.LabelFrame(self, text=" Original Source View ", padding=10)
        self.mid_col.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        
        self.lbl_orig_view = ttk.Label(self.mid_col, text="Awaiting File Input...", anchor="center")
        self.lbl_orig_view.pack(expand=True, fill="both")
        
        # Listen for window resizing properties to expand image matrix automatically
        self.lbl_orig_view.bind("<Configure>", lambda e: self.display_images())

        # ----------------------------------------------------
        # COLUMN 3: RIGHT (Dynamic Preview Frame & Saving Actions)
        # ----------------------------------------------------
        self.right_col = ttk.LabelFrame(self, text=" Live Output Preview ", padding=10)
        self.right_col.grid(row=0, column=2, sticky="nsew", padx=5, pady=10)
        
        self.lbl_prev_view = ttk.Label(self.right_col, text="No modifications yet", anchor="center")
        self.lbl_prev_view.pack(expand=True, fill="both")
        
        # File Save Commitment Trigger Button Component
        self.btn_save = ttk.Button(self.right_col, text="💾 Save Optimized Image", state="disabled", command=self.save_action)
        self.btn_save.pack(fill="x", pady=5)

    # ----------------------------------------------------
    # APPLICATION OPERATIONAL CONTROLLER AND STATE LOGIC
    # ----------------------------------------------------
    def update_quality_slider(self, event=None):
        """ Snaps slider steps to perfect integers and synchronizes workspace state """
        val = int(float(self.quality_var.get()))
        self.quality_var.set(val)
        self.lbl_quality_val.config(text=str(val))
        self.sync_gui_to_dataclass()

    def sync_gui_to_dataclass(self):
        """ Reads all UI input widgets and saves parameters inside the ImageSettings dataclass tracking frame """
        self.settings.rotate = self.rotate_var.get()
        self.settings.filetype = self.format_var.get()
        self.settings.quality = self.quality_var.get()
        
        # Re-trigger processing calculation flow immediately using newly updated variables
        self.apply_transformations()

    def load_image_action(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("All Images", "*.jpg *.jpeg *.png *.heic *.gif *.tiff"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        try:
            self.original_pil_img = open_image(file_path)
            self.current_src_path = Path(file_path)
            self.lbl_file_name.config(text=self.current_src_path.name)
            
            # Store image properties inside tracking object fields
            self.settings.width = self.original_pil_img.width
            self.settings.height = self.original_pil_img.height
            self.settings.ratio = self.original_pil_img.width / self.original_pil_img.height
            
            # Pop the Rabbit out of the Hat! Swapping the visual asset
            if self.img_rabbit_hat:
                self.hat_visual_label.config(image=self.img_rabbit_hat, text="✨ 🐇 Ta-da! Rabbit Out!")
                
            # Unlock structural UI elements to accept user input
            self.btn_save.config(state="normal")
            self.btn_revert.config(state="normal")
            self.btn_close.config(state="normal")
            
            # Match initial view states across data containers
            self.sync_gui_to_dataclass()
        except Exception as e:
            self.lbl_file_name.config(text=f"❌ Error Loading: {str(e)}")

    def apply_transformations(self):
        if not self.original_pil_img:
            return
        # Process changes through backend engine referencing the live dataclass data directly
        self.processed_pil_img = rotate_or_flip(self.original_pil_img, self.settings.rotate)
        self.display_images()

    def display_images(self):
        """ Dynamically rescales tracking preview targets to match the window container size on maximize """
        if not self.original_pil_img:
            return
        # Resize center image viewport safely bounding dimensions
        m_w = max(self.lbl_orig_view.winfo_width(), 100)
        m_h = max(self.lbl_orig_view.winfo_height(), 100)
        scaled_orig = resize_image(self.original_pil_img, (m_w, m_h))
        self.tk_orig_reference = ImageTk.PhotoImage(scaled_orig)
        self.lbl_orig_view.config(image=self.tk_orig_reference, text="")
        
        # Resize right preview image viewport safely bounding dimensions
        r_w = max(self.lbl_prev_view.winfo_width(), 100)
        r_h = max(self.lbl_prev_view.winfo_height(), 100)
        scaled_preview = resize_image(self.processed_pil_img, (r_w, r_h))
        self.tk_preview_reference = ImageTk.PhotoImage(scaled_preview)
        self.lbl_prev_view.config(image=self.tk_preview_reference, text="")

    def revert_settings_action(self):
        if not self.original_pil_img:
            return
        # Set dropdown interactive widgets and labels back to baseline default parameters
        self.rotate_var.set("0")
        self.quality_var.set(12)
        self.lbl_quality_val.config(text="12")
        self.format_var.set("TIFF")
        # Save structural adjustments inside tracking instance context
        self.sync_gui_to_dataclass()

    def confirm_close_action(self):
        if not self.original_pil_img:
            return
        confirm = messagebox.askyesno(
            "Close Image?",
            "Are you sure you want to close this image?\nAny unsaved adjustments will be lost."
        )
        if confirm:
            self.close_image_session()

    def close_image_session(self):
        """ Clears all loaded tracking properties and file pointer references out of application RAM """
        self.current_src_path = None
        self.original_pil_img = None
        self.processed_pil_img = None
        self.tk_orig_reference = None
        self.tk_preview_reference = None
        
        # Re-instantiate an empty baseline dataclass model parameter set
        self.settings = ImageSettings()
        
        # Wipe visual presentation panels back to base textual messages
        self.lbl_file_name.config(text="No file loaded")
        self.lbl_orig_view.config(image="", text="Awaiting File Input...")
        self.lbl_prev_view.config(image="", text="No modifications yet")
        
        # Lock administrative execution switches back down
        self.btn_save.config(state="disabled")
        self.btn_revert.config(state="disabled")
        self.btn_close.config(state="disabled")
        
        # Return the Rabbit back down safely inside the hat structure
        if self.img_empty_hat:
            self.hat_visual_label.config(image=self.img_empty_hat, text="🎩 Hat is Empty...")

    def save_action(self):
        if not self.processed_pil_img or not self.current_src_path:
            return
            
        # Locate source location path bounds, instantiate matching magic_hat sub-directory tree safely
        default_dir = self.current_src_path.parent / "magic_hat"
        default_dir.mkdir(exist_ok=True)
        
        # Build output filename with _copy appended dynamically using tracking file type metadata choices
        target_ext = f".{self.settings.filetype.lower()}"
        default_filename = f"{self.current_src_path.stem}_copy{target_ext}"
        
        # Present directory output management frame to handle file assignment properties
        out_file_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=target_ext,
            filetypes=[(f"{self.settings.filetype} Image", f"*{target_ext}"), ("All Files", "*.*")]
        )
        if not out_file_path:
            return
            
        out_path = Path(out_file_path)
        
        # Security Overwrite protection logic tracking block against original file modification bounds
        if out_path.resolve() == self.current_src_path.resolve():
            messagebox.showerror("Save Aborted", "Overwriting the original source image is forbidden! Please select a unique file name.")
            return
            
        try:
            # Map quality value scale range properties (1-12) to standard Pillow compression spectrum (1-100)
            pillow_quality = int((self.settings.quality / 12) * 100)
            
            # Execute physical export operation saving down to localized hard disk storage paths
            if self.settings.filetype in ["JPEG", "WEBP"]:
                self.processed_pil_img.save(out_path, format=self.settings.filetype, quality=pillow_quality)
            else:
                self.processed_pil_img.save(out_path, format=self.settings.filetype)
                
            print(f"File successfully committed using dataclass configurations: {out_path}")
            
            # Close down workspace sessions completely on file compilation completion events
            self.close_image_session()
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred during image compilation:\n{str(e)}")
            
if __name__ == "__main__":
    main()