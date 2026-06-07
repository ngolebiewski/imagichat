import tkinter as tk
from tkinter import ttk
from dataclasses import dataclass

def main():
    print("IMAGIC HAT")
    app = GUI()
    app.mainloop()
    
# Main Functionality of app
def save_for_web():
    print('saved :)')
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
    
def resize_image():
    ...

def open_image():
    ...
    
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





