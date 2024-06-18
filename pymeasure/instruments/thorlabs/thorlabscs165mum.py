#Author: Amelie Deshazer 
#Date: 6/18/24 
#Address:
#Purpose: Communicate with the ThorLabs CS165MU/M color camera

import logging 
from dlls.tl_camera_enums import SENSOR_TYPE
from dlls.tl_camera import TLCameraSDK, TLCamera, Frame 
from dlls.tl_mono_to_color_processor import MonoToColorProcessorSDK
from pymeasure.instruments import Instrument


class CS165MUM(Instrument):
    
    def __init__(self, adapter, name="CS165MU/M", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.camera_sdk = TLCameraSDK()
    exposure_time = Instrument.control(
         "exposure_time_us",
         """Sets and reads the exposure time in microseconds""",

    )
    def set_upcamera(self):
        exposure = 199


    def exposure_time1(self):
        try:
            exposure_time = 100
        except Exception as e: 
            logging.error(f"Error in setting exposure time: {e}")
            # Add your indented block here