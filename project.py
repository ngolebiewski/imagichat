# Python Built-ins
import tkinter as tk
from tkinter import ttk, filedialog
from dataclasses import dataclass
from pathlib import Path

# Project Packages
from constants import RAW_EXTENSIONS, GUI_RESAMPLE_OPTIONS
from image_lib import image_lib_shoutout

# External Libraries
from PIL import Image, ImageTk
import rawpy
from pillow_heif import register_heif_opener

# Essential setup code
# Register the HEIF opener with Pillow
register_heif_opener()

# ---------------------------------------

def main():
    print("IMAGIC HAT 📸")
    image_lib_shoutout()
    app = GUI()
    app.mainloop()
    
    
# Main Functionality of app

def process_image(src_path):
    # open the file and make a pillow image to work with
    src = open_image(src_path)
    src_copy = src # with src we can revert back to the original
    # get original stats of image?
    while True:
        # listen for adjustments to settings, process when 'saved' OR process when 'adjusted' and show preview
        # do settings update
        # should we have a timeout, so this doesn't run like a million times a microsecond?
        
        # like a game loop? Let's set to 20fps or something. Can Tkinter handle that?
        
        # GET INPUTS -> adjustments from GUI
        # UPDATE IMAGE -> Process image
        # DRAW IMAGE # -> Preview image on screen if changed. src_copy is the ever changing NEW pillow image. perhaps it needs to be an object (it already is?)
        break
    
    # save_image(src_copy, out_path)
    return True #success?
    
    
def image_workflow(src_path, ops):
      # open the file and make a pillow image to work with
    src = open_image(src_path)
    img = src
    
    # apply settings
    if ops.rotate:
        print("rotate or flip",ops.rotate)
        img = rotate_or_flip(img, ops.rotate)
    
    
    
    
    
    
def save_for_web():
    """
    Save and Optimize for Web
    Takes in an ImagicImage object?
    - file
    
    """    
    ...
    
def make_gif_animation():
    ...
    
def magic_mode():
    ...
    
# Helper Functions for image manipulation
def generate_output_path():
    ...

def flatten_alpha_channel():
    ...

def convert_to_rgb():
    ...
    
def get_resampling_filter():
    ...
    
def resize_image(img, new_size=(-1, -1), resample="LANCZOS"):
    """
    Resizes a Pillow Image while intelligently maintaining its original aspect ratio.
    If the aspect ratio of new_size doesn't match, it clamps to the larger dimension 
    and scales the other dimension proportionally.
    """
    # If no valid size is passed, return the original image untouched
    if new_size == (-1, -1):
        return img
    
    # Make sure we have a valid resample filter. if not default to Lanczos, it's smooth:)
    resample_upper = str(resample).upper()
    if resample_upper not in GUI_RESAMPLE_OPTIONS:
        print(f"Warning: '{resample}' is not a valid filter. Falling back to LANCZOS.")
        resample_upper = "LANCZOS"

    og_w, og_h = img.width, img.height
    new_w, new_h = new_size
    print(f"Target size requested: Width={new_w}, Height={new_h}")
    
    # Calculate aspect ratios
    og_ratio = og_w / og_h
    new_ratio = new_w / new_h
    
    # Check if the target ratio deviates from the original ratio
    diff = 0.01
    if abs(og_ratio - new_ratio) > diff:
        print(f"Image ratio mismatch! OG: {og_ratio:.2f}, New target: {new_ratio:.2f}")
        
        # Do the math to clamp and adjust proportionally
        if og_ratio > new_ratio:
            new_h = int(new_w / og_ratio)
        else:
            new_w = int(new_h * og_ratio)
        print(f"Adjusted dimensions to maintain aspect ratio: Width={new_w}, Height={new_h}")

    # Convert the string filter name (like "LANCZOS") into the Pillow enum
    filter_enum = getattr(Image.Resampling, resample_upper)
    
    # Perform the actual resize and return the new image object
    return img.resize((new_w, new_h), resample=filter_enum)

def verify_input_path(in_file_path):
    """
    Converts a string path into a pathlib.Path object and verifies it exists.
    Raises FileNotFoundError if it doesn't.
    """
    path = Path(in_file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path.resolve()}")
    return path

    
def open_image(in_file_path):
    '''
    A function for opening ANY format image file, so that the our code can work with it.
    Works with jpg, png, gif, TIFF, webp, RAW files (via rawpy) and HEIF (iPhone format)
    returns a Pillow image
    '''
    path = verify_input_path(in_file_path)
    file_extension = path.suffix.lower()
    
    # Use Rawpy library to open the raw image as a Pillow Image
    # We check the extension and compare it to our list of raw files in constants.py
    if file_extension in RAW_EXTENSIONS:
        print(f"Processing RAW file: {path}")
        with rawpy.imread(path) as raw: 
            rgb_array = raw.postprocess()
            return Image.fromarray(rgb_array)
    # Open all other file types as a Pillow Image
    else:
        print(f"Opening standard/HEIC image via Pillow: {path}")
        img = Image.open(path)
        img.load() 
        return img
    
def save_image(img):
    '''
    Needs a Pillow Image, path to save the file to, finename and format type.
    Should make a directory if not there
    Should warn if overwriting a file? (add later)
    return True if successful
    
    SHOULD it take in the ImageSettings Object ? then all the specs can be pulled off of that!
    '''
    # outfile = path + name
    # img.save(outfile, specs )
    ...

def color_space():
    ...

def rotate_or_flip(img, deg):
    print(f"Image transposed (rotated) {deg} degrees")
    match deg:
        
        case "90":
            return img.transpose(Image.ROTATE90)
        case "180":
            return img.transpose(Image.ROTATE180)
        case "270":
            return img.transpose(Image.ROTATE270)
        case "FLIP_LEFT_RIGHT":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        case "FLIP_TOP_BOTTOM":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        case _:
            return img
    
    
# Settings, config and specs for images
@dataclass
class ImageSettings():
    """
    5. Settings -> A few defaults / Save your defaults / adjust...
    - size
    - crop
    - ratio
    - format (defaults to same)
    - keep transparency? 
        - set background color
    - animation?
        - speed
        - is infinite?
    - quality
    """
    
   
    width: int
    height: int
    ratio: float
    filetype: str
    rotate: str #can be 90,180,270, FLIP_LEFT_RIGHT, FLIP_TOP_DOWN # make as an enum?
    isTransparent: bool = False
    isAnimation: bool = False
    animation_speed: int = 4
    isInfinite: bool = True
    preset: str = ""
    quality: int = 12
    progressive: bool = True
    
    
    
    
    
@dataclass
class ImageSpecs():
    ...
    
@dataclass
class ImagicImage():
    ...


# tkinter setup and layout/GUI

# This was the original demo GUI, just made a rabbit pop in and out of a magic hat.
# class GUI(tk.Tk):
#     def __init__(self):
#         super().__init__()
        
#         self.title("Imagic Hat")

#         # 1. Text Label
#         self.label = ttk.Label(self, text="IMAGIC HAT")
#         self.label.pack()

#         # 2. Load and store BOTH images in memory
#         self.image_full = tk.PhotoImage(file="art/magic_hat_x5.gif")
#         self.image_empty = tk.PhotoImage(file="art/magic_hat_emptyx5.gif")
        
#         # Track the current state (True means full, False means empty)
#         self.is_hat_full = True

#         # Display the starting image (full hat)
#         self.image_label = ttk.Label(self, image=self.image_full)
#         self.image_label.pack()

#         # 3. Button
#         ttk.Button(
#             self,
#             text="Click Me",
#             command=self.update_text
#         ).pack()

#     def update_text(self):
#         self.is_hat_full = not self.is_hat_full
        
#         if self.is_hat_full:
#             print("MAGIC")
#             self.label.config(text="Magic")
#             self.image_label.config(image=self.image_full)
#         else:
#             print("HAT")
#             self.label.config(text="Hat!")
#             self.image_label.config(image=self.image_empty)

      
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Imagic Hat 📸")
        self.geometry("1200x650")
        
        # State Tracking Variables
        self.current_src_path = None
        self.original_pil_img = None
        self.processed_pil_img = None
        
        # Configure Grid Layout (3 Columns)
        self.columnconfigure(0, weight=1, minsize=280) # Left Column
        self.columnconfigure(1, weight=2, minsize=450) # Middle Column
        self.columnconfigure(2, weight=2, minsize=450) # Right Column
        self.rowconfigure(0, weight=1)

        # ----------------------------------------------------
        # COLUMN 1: LEFT SIDE (3 Vertical Sub-sections)
        # ----------------------------------------------------
        self.left_col = ttk.Frame(self, padding=10)
        self.left_col.grid(row=0, column=0, sticky="nsew")
        
        # --- SECTION 1: File Picker ---
        sec_file = ttk.LabelFrame(self.left_col, text=" 1. File Section ", padding=10)
        sec_file.pack(fill="x", pady=(0, 10))
        
        # This now points to the fixed filedialog module
        self.btn_browse = ttk.Button(sec_file, text="Load Image File", command=self.load_image_action)
        self.btn_browse.pack(fill="x", pady=5)
        
        self.lbl_file_name = ttk.Label(sec_file, text="No file loaded", font=("Arial", 9, "italic"), wraplength=240)
        self.lbl_file_name.pack(fill="x")

        # --- SECTION 2: Magic Hat Visual Status ---
        sec_hat = ttk.LabelFrame(self.left_col, text=" 2. Magic Hat Status ", padding=10)
        sec_hat.pack(fill="x", pady=(0, 10))
        
        # Load your actual graphics assets safely using Pillow
        try:
            self.img_empty_hat = ImageTk.PhotoImage(Image.open("art/magic_hat_emptyx5.gif").resize((120, 120)))
            self.img_rabbit_hat = ImageTk.PhotoImage(Image.open("art/magic_hat_x5.gif").resize((120, 120)))
        except Exception:
            print("Warning: Art assets missing. Using text placeholders.")
            self.img_empty_hat = None
            self.img_rabbit_hat = None

        # Display the starting empty hat graphic
        self.hat_visual_label = ttk.Label(sec_hat, image=self.img_empty_hat, text="🎩 Hat is Empty...", compound="top", font=("Arial", 10, "bold"))
        self.hat_visual_label.pack(pady=5)

        # --- SECTION 3: Image Settings Panel ---
        sec_settings = ttk.LabelFrame(self.left_col, text=" 3. Image Settings ", padding=10)
        sec_settings.pack(fill="both", expand=True)
        
        ttk.Label(sec_settings, text="Rotation Matrix:").pack(anchor="w", pady=(5, 2))
        self.rotate_var = tk.StringVar(value="0")
        rotation_options = ["0", "90", "180", "270", "FLIP_LEFT_RIGHT", "FLIP_TOP_BOTTOM"]
        self.dropdown_rotate = ttk.Combobox(sec_settings, textvariable=self.rotate_var, values=rotation_options, state="readonly")
        self.dropdown_rotate.pack(fill="x", pady=(0, 15))
        self.dropdown_rotate.bind("<<ComboboxSelected>>", self.apply_transformations)
        
        # Revert Button: Instantly resets settings back to original source state
        self.btn_revert = ttk.Button(sec_settings, text="🔄 Reset Settings", state="disabled", command=self.revert_settings_action)
        self.btn_revert.pack(fill="x", side="bottom", pady=5)

        # ----------------------------------------------------
        # COLUMN 2: MIDDLE (Original Source Frame)
        # ----------------------------------------------------
        self.mid_col = ttk.LabelFrame(self, text=" Original Source View ", padding=10)
        self.mid_col.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        
        self.lbl_orig_view = ttk.Label(self.mid_col, text="Awaiting File Input...", anchor="center")
        self.lbl_orig_view.pack(expand=True, fill="both")

        # ----------------------------------------------------
        # COLUMN 3: RIGHT (Preview Output Panel & Save Actions)
        # ----------------------------------------------------
        self.right_col = ttk.LabelFrame(self, text=" Live Output Preview ", padding=10)
        self.right_col.grid(row=0, column=2, sticky="nsew", padx=5, pady=10)
        
        self.lbl_prev_view = ttk.Label(self.right_col, text="No modifications yet", anchor="center")
        self.lbl_prev_view.pack(expand=True, fill="both")
        
        # Save Optimized Button
        self.btn_save = ttk.Button(self.right_col, text="💾 Save Optimized Image", state="disabled", command=self.save_action)
        self.btn_save.pack(fill="x", pady=5)

    # ----------------------------------------------------
    # CORE CONTROLLER LOGIC
    # ----------------------------------------------------
    def load_image_action(self):
        # Pops up the interactive OS file window
        file_path = filedialog.askopenfilename(
            filetypes=[("All Image Files", "*.jpg *.jpeg *.png *.heic *.gif *.tiff"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            # 1. Open file using your back-end open_image logic
            self.original_pil_img = open_image(file_path)
            self.current_src_path = file_path
            self.lbl_file_name.config(text=Path(file_path).name)

            # 2. Swap to the rabbit visual graphic asset
            if self.img_rabbit_hat:
                self.hat_visual_label.config(image=self.img_rabbit_hat, text="✨ 🐇 Ta-da! Rabbit Out!")

            # 3. Fit original image into the center view column container
            scaled_orig = resize_image(self.original_pil_img, (400, 400))
            self.tk_orig_reference = ImageTk.PhotoImage(scaled_orig)
            self.lbl_orig_view.config(image=self.tk_orig_reference, text="")

            # 4. Turn on UI interactions
            self.btn_save.config(state="normal")
            self.btn_revert.config(state="normal")

            # 5. Process downstream pipeline
            self.apply_transformations()

        except Exception as e:
            self.lbl_file_name.config(text=f"❌ Error Loading: {str(e)}")

    def apply_transformations(self, event=None):
        if not self.original_pil_img:
            return

        # Read rotation widget setup value
        angle_selection = self.rotate_var.get()
        if angle_selection.isdigit():
            angle_selection = int(angle_selection)

        # Process image changes using your backend rotate_or_flip logic
        self.processed_pil_img = rotate_or_flip(self.original_pil_img, angle_selection)

        # Downscale copy frame cleanly to fit column 3 box frame
        scaled_preview = resize_image(self.processed_pil_img, (400, 400))
        self.tk_preview_reference = ImageTk.PhotoImage(scaled_preview)
        self.lbl_prev_view.config(image=self.tk_preview_reference, text="")

    def revert_settings_action(self):
        """ Resets widgets and drops values back to matching original state """
        if not self.original_pil_img:
            return
        
        # Set dropdown pointer configuration state back to 0
        self.rotate_var.set("0")
        
        # Re-trigger pipeline to update preview canvas automatically
        self.apply_transformations()
        print("Settings restored to factory defaults.")

    def save_action(self):
        if not self.processed_pil_img:
            return
            
        # File selector window preset for writing file path data back to disk storage
        out_file = filedialog.asksaveasfilename(
            defaultextension=".jpg", 
            filetypes=[("JPEG Image", "*.jpg"), ("PNG Image", "*.png"), ("All Files", "*.*")]
        )
        if out_file:
            self.processed_pil_img.save(out_file)
            print(f"File successfully committed to storage path: {out_file}")

if __name__ == "__main__":
    main()





