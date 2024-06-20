"""
tl_color_enums.py
"""

from enum import IntEnum


class __CTypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class FILTER_ARRAY_PHASE(__CTypesEnum):
    """
    The FILTER_ARRAY_PHASE enumeration lists all the possible values that a pixel in a Bayer pattern color arrangement 
    could assume.

    The classic Bayer pattern is::

        -----------------------
        |          |          |
        |    R     |    GR    |
        |          |          |
        -----------------------
        |          |          |
        |    GB    |    B     |
        |          |          |
        -----------------------

    where:
    
    - R = a red pixel
    - GR = a green pixel next to a red pixel
    - B = a blue pixel
    - GB = a green pixel next to a blue pixel
   
    The primitive pattern shown above represents the fundamental color pixel arrangement in a Bayer pattern
    color sensor.  The basic pattern would extend in the X and Y directions in a real color sensor containing
    millions of pixels.
   
    Notice that the color of the origin (0, 0) pixel logically determines the color of every other pixel.
   
    It is for this reason that the color of this origin pixel is termed the color "phase" because it represents
    the reference point for the color determination of all other pixels.
   
    Every TSI color camera provides the sensor specific color phase of the full frame origin pixel as a discoverable
    parameter.

    """
    BAYER_RED = 0
    """
    A red pixel.
    
    """
    BAYER_BLUE = 1
    """
    A blue pixel.
    
    """
    GREEN_LEFT_OF_RED = 2
    """
    A green pixel next to a red pixel.
    
    """
    GREEN_LEFT_OF_BLUE = 3
    """
    A green pixel next to a blue pixel.
    
    """


class FORMAT(__CTypesEnum):
    """
    The FORMAT enumeration lists all the possible options for specifying the order of
    color pixels in input and/or output buffers.
   
    Depending on the context, it can specify:

    - the desired pixel order that a module must use when writing color pixel data into an output buffer
    - the pixel order that a module must use to interpret data in an input buffer.
    
    """
    BGR_PLANAR = 0
    """
    The color pixels blue, green, and red are grouped in separate planes in the buffer:\n
    BBBBB... GGGGG... RRRRR....
    
    """
    BGR_PIXEL = 1
    """
    The color pixels blue, green, and red are clustered and stored consecutively in the following pattern:\n 
    BGRBGRBGR...
    
    """
    RGB_PIXEL = 2
    """
    The color pixels blue, green, and red are clustered and stored consecutively in the following pattern:\n
    RGBRGBRGB...
    
    """


class FILTER_TYPE(__CTypesEnum):
    """
    The FILTER_TYPE enumeration lists all the possible filter options for color cameras
    
    """
    BAYER = 0
    """
    A Bayer pattern color sensor.
    
    """
