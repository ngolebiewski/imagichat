# Python Built-ins
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from dataclasses import dataclass
from pathlib import Path
import threading    

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
        self.geometry("1200x850")
        
        # State Data & Dataclass Initialization
        self.current_src_path = None
        self.original_pil_img = None
        
        # Viewport Caches (Detached RAM copies for rendering)
        self.orig_view_thumb = None     
        self.preview_view_thumb = None  
        
        # Geometry tracking to prevent infinite resize loop cascades
        self.last_orig_width = 0
        self.last_orig_height = 0
        
        self.settings = ImageSettings()
        self._resize_timer_id = None  
        self._updating_dimensions = False 
        
        # Layout weights (3 Column Architecture Grid)
        self.columnconfigure(0, weight=1, minsize=320)
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

        # Sub-Section B: Magic Hat Status Box
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
        self.dropdown_rotate.pack(fill="x", pady=(0, 10))
        self.dropdown_rotate.bind("<<ComboboxSelected>>", lambda e: self.handle_rotation_change())
        
        # Resize Output Scale Rules Matrix
        self.sec_resize = ttk.LabelFrame(sec_settings, text=" Custom Scaling Overrides ", padding=8)
        self.sec_resize.pack(fill="x", pady=(0, 10))
        
        # Lock Aspect Ratio Constraint Flag
        self.lock_ratio_var = tk.BooleanVar(value=True)
        self.chk_lock = ttk.Checkbutton(self.sec_resize, text="Lock Aspect Scale Proportions", variable=self.lock_ratio_var)
        self.chk_lock.pack(anchor="w", pady=(0, 5))
        
        # Width Dimension Input Block
        dim_frame = ttk.Frame(self.sec_resize)
        dim_frame.pack(fill="x")
        
        ttk.Label(dim_frame, text="Width (px):").pack(side="left")
        self.width_var = tk.StringVar()
        self.entry_width = ttk.Entry(dim_frame, textvariable=self.width_var, width=8)
        self.entry_width.pack(side="left", padx=(5, 15))
        self.entry_width.bind("<FocusOut>", lambda e: self.handle_dimension_input("width"))
        self.entry_width.bind("<Return>", lambda e: self.handle_dimension_input("width"))
        
        # Height Dimension Input Block
        ttk.Label(dim_frame, text="Height (px):").pack(side="left")
        self.height_var = tk.StringVar()
        self.entry_height = ttk.Entry(dim_frame, textvariable=self.height_var, width=8)
        self.entry_height.pack(side="left", padx=5)
        self.entry_height.bind("<FocusOut>", lambda e: self.handle_dimension_input("height"))
        self.entry_height.bind("<Return>", lambda e: self.handle_dimension_input("height"))

        # Export Format Selection Combobox (On-Demand sync)
        ttk.Label(sec_settings, text="Export Format:").pack(anchor="w", pady=(5, 2))
        self.format_var = tk.StringVar(value="JPEG")
        format_options = ["TIFF", "PNG", "JPEG", "WEBP", "GIF"]
        self.dropdown_format = ttk.Combobox(sec_settings, textvariable=self.format_var, values=format_options, state="readonly")
        self.dropdown_format.pack(fill="x", pady=(0, 10))
        self.dropdown_format.bind("<<ComboboxSelected>>", lambda e: self.sync_gui_to_dataclass())
        
        # Compression/Quality Parameter Slider Range Scale (On-Demand sync)
        ttk.Label(sec_settings, text="Quality Level (1-12):").pack(anchor="w")
        self.quality_var = tk.IntVar(value=12)
        self.lbl_quality_val = ttk.Label(sec_settings, text="12")
        self.lbl_quality_val.pack(anchor="e")
        
        self.slider_quality = ttk.Scale(sec_settings, from_=1, to=12, variable=self.quality_var, orient="horizontal", command=self.update_quality_slider)
        self.slider_quality.pack(fill="x", pady=(0, 15))
        
        # Dedicated Manual Refresh Preview Button
        self.btn_refresh = ttk.Button(sec_settings, text="🔄 Refresh Preview Window", state="disabled", command=self.apply_fast_preview_transform)
        self.btn_refresh.pack(fill="x", pady=(5, 15))
        
        # Bottom Utility Buttons Container Frame Layout
        btn_container = ttk.Frame(sec_settings)
        btn_container.pack(fill="x", side="bottom", pady=5)
        
        self.btn_revert = ttk.Button(btn_container, text="🔄 Reset Settings", state="disabled", command=self.revert_settings_action)
        self.btn_revert.pack(fill="x", pady=2)
        
        self.btn_close = ttk.Button(btn_container, text="❌ Close Image", state="disabled", command=self.confirm_close_action)
        self.btn_close.pack(fill="x", pady=2)

        # ----------------------------------------------------
        # COLUMN 2: MIDDLE (Original Source View Frame)
        # ----------------------------------------------------
        self.mid_col = ttk.LabelFrame(self, text=" Original Source View ", padding=10)
        self.mid_col.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        self.mid_col.grid_propagate(False) 
        
        self.lbl_orig_view = ttk.Label(self.mid_col, text="Awaiting File Input...", anchor="center")
        self.lbl_orig_view.grid(row=0, column=0, sticky="nsew")
        self.mid_col.columnconfigure(0, weight=1)
        self.mid_col.rowconfigure(0, weight=1)
        
        # Track resizes on the middle column container frame
        self.mid_col.bind("<Configure>", self.handle_window_resize_event)

        # ----------------------------------------------------
        # COLUMN 3: RIGHT (Live Output Preview)
        # ----------------------------------------------------
        self.right_col = ttk.LabelFrame(self, text=" Live Output Preview ", padding=10)
        self.right_col.grid(row=0, column=2, sticky="nsew", padx=5, pady=10)
        self.right_col.grid_propagate(False)
        
        self.lbl_prev_view = ttk.Label(self.right_col, text="No modifications yet", anchor="center")
        self.lbl_prev_view.grid(row=0, column=0, sticky="nsew")
        self.right_col.columnconfigure(0, weight=1)
        self.right_col.rowconfigure(0, weight=1)
        
        self.btn_save = ttk.Button(self.right_col, text="💾 Save Optimized Image", state="disabled", command=self.save_action)
        self.btn_save.grid(row=1, column=0, sticky="ew", pady=(5, 0))

    # ----------------------------------------------------
    # OPERATIONAL CONTROLLERS & DATA SYNCHRONIZATION
    # ----------------------------------------------------
    def update_quality_slider(self, event=None):
        val = int(float(self.quality_var.get()))
        self.quality_var.set(val)
        self.lbl_quality_val.config(text=str(val))
        self.sync_gui_to_dataclass()

    def sync_gui_to_dataclass(self):
        self.settings.rotate = self.rotate_var.get()
        self.settings.filetype = self.format_var.get()
        self.settings.quality = self.quality_var.get()
        
        try:
            self.settings.width = int(self.width_var.get())
            self.settings.height = int(self.height_var.get())
        except ValueError:
            pass

    def handle_rotation_change(self):
        self.sync_gui_to_dataclass()
        self.apply_fast_preview_transform()

    def handle_dimension_input(self, changed_dimension):
        if not self.original_pil_img or self._updating_dimensions:
            return
            
        try:
            w_val = int(self.width_var.get())
            h_val = int(self.height_var.get())
        except ValueError:
            return  

        self._updating_dimensions = True
        native_ratio = self.original_pil_img.width / self.original_pil_img.height
        
        if self.lock_ratio_var.get():
            if changed_dimension == "width":
                h_val = max(1, int(w_val / native_ratio))
                self.height_var.set(str(h_val))
            else:
                w_val = max(1, int(h_val * native_ratio))
                self.width_var.set(str(w_val))
                
        self._updating_dimensions = False
        self.sync_gui_to_dataclass()

    # --- ASYNCHRONOUS LOAD PIPELINE ---
    def load_image_action(self):
        self.lbl_file_name.config(text="⌛ Opening File Browser...")
        file_path = filedialog.askopenfilename(
            filetypes=[("All Images", "*.jpg *.jpeg *.png *.heic *.gif *.tiff"), ("All Files", "*.*")]
        )
        if file_path:
            self.lbl_file_name.config(text="⌛ Loading image file...")
            threading.Thread(target=self._async_load_worker, args=(file_path,), daemon=True).start()
        else:
            self.lbl_file_name.config(text="No file loaded")

    def _async_load_worker(self, file_path):
        try:
            loaded_img = open_image(file_path)
            loaded_img.load()  # Read full array into RAM immediately
            src_path = Path(file_path)
            self.after(0, self._async_load_callback, loaded_img, src_path)
        except Exception as e:
            self.after(0, lambda: self.lbl_file_name.config(text=f"❌ Error Loading: {str(e)}"))

    def _async_load_callback(self, loaded_img, src_path):
        self.original_pil_img = loaded_img
        self.current_src_path = src_path
        self.lbl_file_name.config(text=self.current_src_path.name)
        
        self.width_var.set(str(self.original_pil_img.width))
        self.height_var.set(str(self.original_pil_img.height))
        
        if self.img_rabbit_hat:
            self.hat_visual_label.config(image=self.img_rabbit_hat, text="✨ 🐇 Ta-da! Rabbit Out!")
            
        self.btn_save.config(state="normal")
        self.btn_revert.config(state="normal")
        self.btn_close.config(state="normal")
        self.btn_refresh.config(state="normal")
        
        # Reset geometry locks to guarantee layout generation
        self.last_orig_width = 0
        self.last_orig_height = 0
        
        self.generate_viewport_caches()

    # ----------------------------------------------------
    # GEOMETRY RECONCILIATION & DEBOUNCED RENDER PIPELINE
    # ----------------------------------------------------
    def handle_window_resize_event(self, event):
        if not self.original_pil_img:
            return
            
        # Ignore layout recalculation if change is less than 5px
        if abs(event.width - self.last_orig_width) < 5 and abs(event.height - self.last_orig_height) < 5:
            return
            
        self.last_orig_width = event.width
        self.last_orig_height = event.height
        
        # Debounce: Cancel pending timer if user is actively dragging window frame
        if self._resize_timer_id:
            self.after_cancel(self._resize_timer_id)
            
        # Execute render 250ms after sizing settles
        self._resize_timer_id = self.after(250, self.generate_viewport_caches)

    def generate_viewport_caches(self):
        if not self.original_pil_img:
            return
        threading.Thread(target=self._build_cache_worker, daemon=True).start()

    def _build_cache_worker(self):
        m_w = max(self.mid_col.winfo_width() - 20, 100)
        m_h = max(self.mid_col.winfo_height() - 40, 100)
        r_w = max(self.right_col.winfo_width() - 20, 100)
        r_h = max(self.right_col.winfo_height() - 40, 100)
        
        t1 = resize_image(self.original_pil_img, (m_w, m_h))
        t2 = resize_image(self.original_pil_img, (r_w, r_h))
        
        self.orig_view_thumb = t1.copy()
        self.preview_view_thumb = t2.copy()
        
        self.after(0, self._render_caches_callback)

    def _render_caches_callback(self):
        if not self.original_pil_img:
            return
        self.tk_orig_reference = ImageTk.PhotoImage(self.orig_view_thumb)
        self.lbl_orig_view.config(image=self.tk_orig_reference, text="")
        
        # Auto-update previews on a resize layout shift
        self.sync_gui_to_dataclass()
        self.apply_fast_preview_transform()

    # --- ULTRA-FAST LIGHTWEIGHT TRANSFORMATION ENGINE ---
    def apply_fast_preview_transform(self):
        if not self.preview_view_thumb:
            return
            
        current_rotation = self.rotate_var.get()
        
        # CRITICAL RE-ALLOCATION BYPASS: Point straight to cache reference if 0 degrees
        if current_rotation == "0":
            self.tk_preview_reference = ImageTk.PhotoImage(self.preview_view_thumb)
            self.lbl_prev_view.config(image=self.tk_preview_reference, text="")
            return

        processed_preview = rotate_or_flip(self.preview_view_thumb, current_rotation)
        self.tk_preview_reference = ImageTk.PhotoImage(processed_preview)
        self.lbl_prev_view.config(image=self.tk_preview_reference, text="")

    # --- UTILITIES ---
    def revert_settings_action(self):
        if not self.original_pil_img:
            return
        self.rotate_var.set("0")
        self.quality_var.set(12)
        self.lbl_quality_val.config(text="12")
        self.format_var.set("JPEG")
        self.width_var.set(str(self.original_pil_img.width))
        self.height_var.set(str(self.original_pil_img.height))
        self.sync_gui_to_dataclass()
        self.apply_fast_preview_transform()

    def confirm_close_action(self):
        if not self.original_pil_img:
            return
        if messagebox.askyesno("Close Image?", "Are you sure you want to close this image?"):
            self.close_image_session()

    def close_image_session(self):
        self.current_src_path = None
        self.original_pil_img = None
        self.orig_view_thumb = None
        self.preview_view_thumb = None
        self.tk_orig_reference = None
        self.tk_preview_reference = None
        self.settings = ImageSettings()
        
        self.lbl_file_name.config(text="No file loaded")
        self.lbl_orig_view.config(image="", text="Awaiting File Input...")
        self.lbl_prev_view.config(image="", text="No modifications yet")
        self.width_var.set("")
        self.height_var.set("")
        
        self.btn_save.config(state="disabled")
        self.btn_revert.config(state="disabled")
        self.btn_close.config(state="disabled")
        self.btn_refresh.config(state="disabled")
        
        if self.img_empty_hat:
            self.hat_visual_label.config(image=self.img_empty_hat, text="🎩 Hat is Empty...")

    # --- COMPILATION & DISK EXPORT PIPELINE ---
    def save_action(self):
        if not self.original_pil_img or not self.current_src_path:
            return
            
        default_dir = self.current_src_path.parent / "magic_hat"
        default_dir.mkdir(exist_ok=True)
        
        target_ext = f".{self.settings.filetype.lower()}"
        default_filename = f"{self.current_src_path.stem}_copy{target_ext}"
        
        out_file_path = filedialog.asksaveasfilename(
            initialdir=default_dir,
            initialfile=default_filename,
            defaultextension=target_ext,
            filetypes=[(f"{self.settings.filetype} Image", f"*{target_ext}"), ("All Files", "*.*")]
        )
        if not out_file_path:
            return
            
        out_path = Path(out_file_path)
        pillow_quality = int((self.settings.quality / 12) * 100)
        self.btn_save.config(state="disabled")
        
        # Heavy processes isolated completely to save operations
        threading.Thread(
            target=self._async_save_worker, 
            args=(out_path, pillow_quality), 
            daemon=True
        ).start()

    def _async_save_worker(self, out_path, pillow_quality):
        try:
            # 1. Always start fresh from the original full-color master
            master_img = rotate_or_flip(self.original_pil_img, self.settings.rotate)
            
            try:
                target_w = int(self.width_var.get())
                target_h = int(self.height_var.get())
                
                master_ratio = master_img.width / master_img.height
                target_ratio = target_w / target_h
                
                if (master_ratio > 1 and target_ratio < 1) or (master_ratio < 1 and target_ratio > 1):
                    target_w, target_h = target_h, target_w
                
                if target_w != master_img.width or target_h != master_img.height:
                    master_img = master_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            except ValueError:
                pass

            # 2. Normalize format strings cleanly
            save_format = self.settings.filetype.upper()
            if save_format == "JPG":
                save_format = "JPEG"

            # 3. Create a local copy for format-specific color mutations
            export_img = master_img.copy()

            # 4. Handle specific format color rules safely
            if save_format == "GIF":
                export_img = export_img.convert("P", palette=Image.Palette.ADAPTIVE)
            elif save_format in ["JPEG", "JPG"] and export_img.mode in ["P", "RGBA"]:
                # If it somehow got stuck in Palette or transparent mode, force it back to standard RGB for JPEG
                export_img = export_img.convert("RGB")

            # 5. Write to disk using the safely isolated copy
            if save_format in ["JPEG", "WEBP"]:
                export_img.save(out_path, format=save_format, quality=pillow_quality)
            else:
                export_img.save(out_path, format=save_format)
                
            self.after(0, self._async_save_callback, True, out_path, None)
        except Exception as e:
            self.after(0, self._async_save_callback, False, out_path, str(e))
        try:
            master_img = rotate_or_flip(self.original_pil_img, self.settings.rotate)
            
            try:
                target_w = int(self.width_var.get())
                target_h = int(self.height_var.get())
                
                master_ratio = master_img.width / master_img.height
                target_ratio = target_w / target_h
                
                if (master_ratio > 1 and target_ratio < 1) or (master_ratio < 1 and target_ratio > 1):
                    target_w, target_h = target_h, target_w
                
                if target_w != master_img.width or target_h != master_img.height:
                    master_img = master_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
            except ValueError:
                pass

            save_format = self.settings.filetype.upper()
            if save_format == "JPG":
                save_format = "JPEG"

            # FIX THE GIF SAVE BUG: Convert full-color RGB to a 256-color palette
            if save_format == "GIF":
                # Convert to palette mode using an adaptive, high-quality dithering palette
                master_img = master_img.convert("P", palette=Image.Palette.ADAPTIVE)

            if save_format in ["JPEG", "WEBP"]:
                master_img.save(out_path, format=save_format, quality=pillow_quality)
            else:
                master_img.save(out_path, format=save_format)
                
            self.after(0, self._async_save_callback, True, out_path, None)
        except Exception as e:
            self.after(0, self._async_save_callback, False, out_path, str(e))
            try:
                # 1. Apply rotation first to get the correct orientation matrix
                master_img = rotate_or_flip(self.original_pil_img, self.settings.rotate)
                
                try:
                    # 2. Parse the desired output dimensions from the entry boxes
                    target_w = int(self.width_var.get())
                    target_h = int(self.height_var.get())
                    
                    # 3. FIX THE WARPING: Check if the current orientation aspect ratio 
                    # matches the text fields. If it flipped, swap them to prevent squashing.
                    master_ratio = master_img.width / master_img.height
                    target_ratio = target_w / target_h
                    
                    # If one is landscape and the other is portrait, flip the target constraints
                    if (master_ratio > 1 and target_ratio < 1) or (master_ratio < 1 and target_ratio > 1):
                        target_w, target_h = target_h, target_w
                    
                    # Only execute resize if the dimensions are actually different from current master state
                    if target_w != master_img.width or target_h != master_img.height:
                        master_img = master_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                except ValueError:
                    # If text fields are empty or invalid, skip custom scaling and keep original size
                    pass

                # 4. Save to disk cleanly
                if self.settings.filetype in ["JPEG", "WEBP"]:
                    master_img.save(out_path, format=self.settings.filetype, quality=pillow_quality)
                else:
                    master_img.save(out_path, format=self.settings.filetype)
                    
                self.after(0, self._async_save_callback, True, out_path, None)
            except Exception as e:
                self.after(0, self._async_save_callback, False, out_path, str(e))
            try:
                master_img = rotate_or_flip(self.original_pil_img, self.settings.rotate)
                
                try:
                    target_w = int(self.width_var.get())
                    target_h = int(self.height_var.get())
                    if target_w != self.original_pil_img.width or target_h != self.original_pil_img.height:
                        master_img = master_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
                except ValueError:
                    pass

                if self.settings.filetype in ["JPEG", "WEBP"]:
                    master_img.save(out_path, format=self.settings.filetype, quality=pillow_quality)
                else:
                    master_img.save(out_path, format=self.settings.filetype)
                    
                self.after(0, self._async_save_callback, True, out_path, None)
            except Exception as e:
                self.after(0, self._async_save_callback, False, out_path, str(e))

    def _async_save_callback(self, success, out_path, error_msg):
        if success:
            self.close_image_session()
        else:
            self.btn_save.config(state="normal")  
            messagebox.showerror("Export Failed", f"An error occurred during compilation:\n{error_msg}")


if __name__ == "__main__":
    main()