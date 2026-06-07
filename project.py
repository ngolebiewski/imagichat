import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass
from image_lib import image_lib_shoutout
import os
from pathlib import Path
from constants import RAW_EXTENSIONS, GUI_RESAMPLE_OPTIONS

from PIL import Image
import rawpy
from pillow_heif import register_heif_opener


# Register the HEIF opener with Pillow
register_heif_opener()

def main():
    print("IMAGIC HAT 📸")
    image_lib_shoutout()
    app = GUI()
    app.mainloop()
    
    
# Main Functionality of app
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
    
def save_image():
    ...

def color_space():
    ...
    
# Settings, config and specs for images
@dataclass
class ImageSettings():
    ...
    
@dataclass
class ImageSpecs():
    ...
    
@dataclass
class ImagicImage():
    ...


# tkinter setup and layout/GUI
class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Imagic Hat")

        # 1. Text Label
        self.label = ttk.Label(self, text="IMAGIC HAT")
        self.label.pack()

        # 2. Load and store BOTH images in memory
        self.image_full = tk.PhotoImage(file="art/magic_hat_x5.gif")
        self.image_empty = tk.PhotoImage(file="art/magic_hat_emptyx5.gif")
        
        # Track the current state (True means full, False means empty)
        self.is_hat_full = True

        # Display the starting image (full hat)
        self.image_label = ttk.Label(self, image=self.image_full)
        self.image_label.pack()

        # 3. Button
        ttk.Button(
            self,
            text="Click Me",
            command=self.update_text
        ).pack()

    def update_text(self):
        self.is_hat_full = not self.is_hat_full
        
        if self.is_hat_full:
            print("MAGIC")
            self.label.config(text="Magic")
            self.image_label.config(image=self.image_full)
        else:
            print("HAT")
            self.label.config(text="Hat!")
            self.image_label.config(image=self.image_empty)

        
if __name__ == "__main__":
    main()





