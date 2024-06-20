"""
tl_polarization_enums.py
"""

from enum import IntEnum


class _CTypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class POLAR_PHASE(_CTypesEnum):
    """
    The possible polarization angle values (in degrees) for a pixel in a polarization sensor. The polarization phase
    pattern of the sensor is::

        -------------
        | + 0 | -45 |
        -------------
        | +45 | +90 |
        -------------

    The primitive pattern shown above represents the fundamental polarization phase arrangement in a polarization
    sensor. The basic pattern would extend in the X and Y directions in a real polarization sensor containing millions
    of pixels. Notice that the phase of the origin (0, 0) pixel logically determines the phase of every other pixel.
    It is for this reason that the phase of this origin pixel is termed the polarization "phase" because it represents
    the reference point for the phase determination of all other pixels.


    """
    PolarPhase0 = 0
    """
    0 degrees polarization phase 
    
    """
    PolarPhase45 = 1
    """
    45 degrees polarization phase 

    """
    PolarPhase90 = 2
    """
    90 degrees polarization phase 

    """
    PolarPhase135 = 3
    """
    135 (-45) degrees polarization phase 

    """
