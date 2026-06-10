from dataclasses import dataclass
from PIL import Image


"""
Supported Pillow image resampling filters for the GUI dropdown selection.

Available Filters:
    NEAREST  - Nearest Neighbor, fast, Pixel Art
    BOX      - Box Filter, identical pixel weights, simple downscaling
    BILINEAR - Bilinear, smooth interpolation, moderate speed
    HAMMING  - Hamming, sharper than bilinear, reduces local distortions
    BICUBIC  - Bicubic, standard cubic interpolation, default for general use
    LANCZOS  - Lanczos, highest quality truncated sinc filter, best for photos
    
As List: ['NEAREST', 'BOX', 'BILINEAR', 'HAMMING', 'BICUBIC', 'LANCZOS']
"""
GUI_RESAMPLE_OPTIONS = [filter.name for filter in Image.Resampling]


RAW_EXTENSIONS = {
    """
    Types of file extenstions of RAW camera files for import phase
    Major camera brands
    Note: I'll be testing .arw from my Sony DSLR camera.
    """
    '.nef', '.nrw',                  # Nikon
    '.cr2', '.cr3', '.crw',          # Canon
    '.arw', '.srf', '.sr2',          # Sony
    '.raf',                          # Fujifilm
    '.rw2',                          # Panasonic / Lumix
    '.iiq',                          # Phase One
    '.3fr', '.fff',                  # Hasselblad
    '.dng',                          # Adobe Universal Standard (Leica, Ricoh, mobile phones)
    '.orf', '.ori',                  # Olympus / OM System
    '.pef', '.ptx',                  # Pentax
    '.srw',                          # Samsung
    '.rwl',                          # Leica
    '.gpr',                          # GoPro
    '.bay'                           # Casio
}