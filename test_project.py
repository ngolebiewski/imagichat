from PIL import Image
from project import resize_image, open_image

def test_resize_image_maintains_aspect_ratio():
    # Create a fake image for testing
    test_img = Image.new("RGB", (100, 50))
    
    # Give the image a width and a height to fit it to
    resized_img = resize_image(test_img, new_size=(500, 500))
    
    # The math should clamp it to 500x250 to keep the original2:1 ratio.
    assert resized_img.width == 500
    assert resized_img.height == 250

def test_open_image():
    # Test that a Pillow Image instance is returned when we try to open a file
    filepath = 'art/magic_hat_emptyx5.gif'
    assert isinstance(open_image(filepath), Image.Image)
    


