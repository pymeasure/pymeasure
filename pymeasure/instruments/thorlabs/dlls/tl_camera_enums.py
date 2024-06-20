"""
tl_camera_enums.py
"""

from enum import IntEnum


class _CTypesEnum(IntEnum):
    @classmethod
    def from_param(cls, obj):
        return int(obj)


class OPERATION_MODE(_CTypesEnum):
    """
    The OPERATION_MODE enumeration defines the available modes for a camera.

    """
    SOFTWARE_TRIGGERED = 0
    """
    Use software operation mode to generate one or more frames per trigger or to run continuous video mode.
    
    """
    HARDWARE_TRIGGERED = 1
    """
    Use hardware triggering to generate one or more frames per trigger by issuing hardware signals.
    
    """
    BULB = 2
    """
    Use bulb-mode triggering to generate one or more frames per trigger by issuing hardware signals. Please refer to 
    the camera manual for signaling details.
    
    """
    RESERVED1 = 3  # Reserved for internal use.
    RESERVED2 = 4  # Reserved for internal use.


class SENSOR_TYPE(_CTypesEnum):
    """
    This describes the physical capabilities of the camera sensor.

    """
    MONOCHROME = 0
    """
    Each pixel of the sensor indicates an intensity.
    
    """
    BAYER = 1
    """
    The sensor has a bayer-patterned filter overlaying it, allowing the camera SDK to distinguish red, green, and blue 
    values.
    
    """
    MONOCHROME_POLARIZED = 2
    """
     The sensor has a polarization filter overlaying it allowing the camera to capture polarization information from 
     the incoming light.

    """


class TRIGGER_POLARITY(_CTypesEnum):
    """
    The TRIGGER_POLARITY enumeration defines the options available for specifying the hardware trigger polarity. These
    values specify which edge of the input trigger pulse that will initiate image acquisition.

    """
    ACTIVE_HIGH = 0
    """
    Acquire an image on the RISING edge of the trigger pulse.
    
    """
    ACTIVE_LOW = 1
    """
    Acquire an image on the FALLING edge of the trigger pulse.

    """


class EEP_STATUS(_CTypesEnum):
    """
    The EEP_STATUS enumeration defines the options available for specifying the device's EEP mode. Equal Exposure Pulse
    (EEP) mode is an LVTTL-level signal that is active during the time when all rows have been reset during rolling
    reset, and the end of the exposure time (and the beginning of rolling readout). The signal can be used to control
    an external light source that will be on only during the equal exposure period, providing the same amount of
    exposure for all pixels in the ROI. EEP mode can be enabled, but may be active or inactive depending on the
    current exposure value. If EEP is enabled in bulb mode, it will always give a status of Bulb.

    """
    DISABLED = 0
    """
    EEP mode is disabled.
    
    """
    ENABLED_ACTIVE = 1
    """
    EEP mode is enabled and currently active.
    
    """
    ENABLED_INACTIVE = 2
    """
    EEP mode is enabled, but due to an unsupported exposure value, currently inactive.
    
    """
    ENABLED_BULB = 3
    """
    EEP mode is enabled in bulb mode.
    
    """


class DATA_RATE(_CTypesEnum):
    """
    The DATA_RATE enumeration defines the options for setting the desired image data delivery rate.

    """
    RESERVED1 = 0  # A RESERVED value (DO NOT USE).
    RESERVED2 = 1  # A RESERVED value (DO NOT USE).
    FPS_30 = 2
    """
    Sets the device to deliver images at 30 frames per second.
    
    """
    FPS_50 = 3
    """
    Sets the device to deliver images at 50 frames per second.
    
    """


class USB_PORT_TYPE(_CTypesEnum):
    """
    The USB_PORT_TYPE enumeration defines the values the SDK uses for specifying the USB bus speed. These values are
    returned by SDK API functions and callbacks based on the type of physical USB port that the device is connected to.

    """
    USB1_0 = 0
    """
    The device is connected to a USB 1.0/1.1 port (1.5 Mbits/sec or 12 Mbits/sec).
    
    """
    USB2_0 = 1
    """
    The device is connected to a USB 2.0 port (480 Mbits/sec).
    
    """
    USB3_0 = 2
    """
    The device is connected to a USB 3.0 port (5000 Mbits/sec).
    
    """


class TAPS(_CTypesEnum):
    """
    Scientific CCD cameras support one or more taps. After exposure is complete, a CCD pixel array holds the charges
    corresponding to the amount of light collected at beach pixel location. The data is then read out through 1, 2,
    or 4 channels at a time.

    """
    SINGLE_TAP = 0
    """
    Charges are read out through a single analog-to-digital converter.
    
    """
    DUAL_TAP = 1
    """
    Charges are read out through two analog-to-digital converters.
    
    """
    QUAD_TAP = 2
    """
    Charges are read out through four analog-to-digital converters.
    
    """


class COMMUNICATION_INTERFACE(_CTypesEnum):
    """
    Used to identify what interface the camera is currently using. If using USB, the specific USB version can also be
    identified using USB_PORT_TYPE.

    """
    GIG_E = 0
    """
    The camera uses the GigE Vision (GigE) interface standard.
    
    """
    LINK = 1
    """
    The camera uses the CameraLink serial-communication-protocol standard.
    
    """
    USB = 2
    """
    The camera uses a USB interface.
    
    """
