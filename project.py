# Python Built-ins
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
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
            return img.transpose(Image.ROTATE_90)
        case "180":
            return img.transpose(Image.ROTATE_180)
        case "270":
            return img.transpose(Image.ROTATE_270)
        case "FLIP_LEFT_RIGHT":
            return img.transpose(Image.FLIP_LEFT_RIGHT)
        case "FLIP_TOP_BOTTOM":
            return img.transpose(Image.FLIP_TOP_BOTTOM)
        case _:
            return img
    
    
# Settings, config and specs for images
@dataclass
class ImageSettings():
    """ Holds the live image settings matching the user's GUI choices/CLI prompts """
    width: int = -1
    height: int = -1
    ratio: float = 1.0
    filetype: str = "JPG"
    isTransparent: bool = False
    isAnimation: bool = False
    animation_speed: int = 4
    rotate: int | str = "0"  # Can be 0, 90, 180, 270, FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM
    isInfinite: bool = True
    preset: str = ""
    quality: int = 12       # Scaled 1 to 12
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

      

            
if __name__ == "__main__":
    main()





