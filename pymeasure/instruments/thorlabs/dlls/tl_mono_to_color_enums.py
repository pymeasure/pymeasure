"""
tl_mono_to_color_enums.py
"""

from enum import IntEnum


class _CTypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class COLOR_SPACE(_CTypesEnum):
    """
    A color space describes how the colors in an image are going to be specified. Some commonly used color spaces are those derived from the
    RGB color model, in which each pixel has a Red, Blue, and Green component. This means the amount of color that can expressed in a single
    pixel is all the possible combinations of Red, Blue, and Green. If we assume the image data is in bytes, each component can take any value
    from 0 to 255. The total number of colors that a pixel could express can be calculated as 256 * 256 * 256 = 16777216 different colors.

    There are many different color spaces that are used for different purposes. The mono to color processor supports two color spaces that
    are both derived from the RGB color model: sRGB and Linear sRGB.

    """
    SRGB = 0
    """
    sRGB or standard RGB is a common color space used for displaying images on computer monitors or for sending images over the internet. 
    In addition to the Red, Blue, and Green components combining to define the color of a pixel, the final RGB values undergo a nonlinear transformation 
    to be put in the sRGB color space. The exact transfer function can be found online by searching for the sRGB specification. The purpose of this 
    transformation is to represent the colors in a way that looks more accurate to humans.
    
    """
    LINEAR_SRGB = 1
    """
    Linear sRGB is very similar to sRGB, but does not perform the non linear transformation. The transformation of the data in sRGB changes the RGB intensities, 
    whereas this color space is much more representative of the raw image data coming off the sensor. Without the transformation, however, images in the Linear 
    sRGB color space do not look as accurate as those in sRGB. When deciding between Linear sRGB and sRGB, use Linear sRGB when the actual intensities of the raw 
    image data are important and use sRGB when the image needs to look accurate to the human eye.
    
    """
