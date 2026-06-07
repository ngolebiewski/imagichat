from PIL import Image
from project import resize_image
import rawpy

def test_resize_image_maintains_aspect_ratio():
    # Create a fake 100x50 (2:1 ratio) image in memory for testing
    test_img = Image.new("RGB", (100, 50))
    
    # Try to force it into a square (1:1 ratio) 500x500 box
    resized_img = resize_image(test_img, new_size=(500, 500))
    
    # The math should clamp it to 500x250 to keep the 2:1 look!
    assert resized_img.width == 500
    assert resized_img.height == 250