# Purpose: To create an array of visual data for camera images 
# Lines 47-65 is the code for developing an array of 3x1000x1000
# Code was directly modified from Thorlabs tkinter_camera_live_view.py
# This code is purely for testing purposes. This is not the final product for CS165MUM


import sys 
import os
import queue
from ctypes import c_longlong
from pymeasure import Instrument
from thorlabs_tsi_sdk.tl_camera import TLCameraSDK, TLCameraError
from thorlabs_tsi_sdk.tl_camera_enums import SENSOR_TYPE
from thorlabs_tsi_sdk.tl_mono_to_color_processor import MonoToColorProcessorSDK
from PIL import Image, ImageTk
from tkinter import tk

try:
    # if on Windows, use the provided setup script to add the DLLs folder to the PATH
    from windows_setup import configure_path
    configure_path()
except ImportError:
    configure_path = None

class Initiate_Camera(): 
    def discover_cameras(self):
        with TLCameraSDK() as sdk: 
            camera_avilable = sdk.discover_available_cameras()

            if camera_avilable:
                print("Camera detected")
            else: 
                print("No camera detected") 
    #Lines 35-58 define get and set exposure times before image acquisition. 
    @property
    def exposure_time_us(self): 
        try: 
            exposure_time_us = c_longlong()
            exposure = self._sdk.tl_camera_get_exposure_time(self, exposure_time_us)

            if exposure != 0:
                print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us.value))
                return int(exposure_time_us.value)  
        
        except Exception as error: 
            print("Error: {error}".format(error=error))
            raise error
    
    @exposure_time_us.setter
    def exposure_time_us(self, exposure_time_us): 
        try: 
            value = c_longlong(exposure_time_us)
            exposure = self._sdk.tl_camera__set_exposure_time_us(self, value)
            if exposure != 0: 
                print("Exposure time set to {exposure_time_us} microseconds".format(exposure_time_us=exposure_time_us))

        except Exception as error: 
            print("Could not set exposure time" + str(error))

    def software_trigger(self): 
        try:
            trigger = 

        except Exception as error:
            print("Could not trigger camera" + str(error))



class ImageAcquistionThread(Instrument):

    def __init__(self, camera): 
        self._camera = camera 
        
        #Checks if whether can incorporate color processing
        if self._camera.camera_get_sensor != SENSOR_TYPE.BAYER:
            # Cannot support color
            self._camera = False
        else:
            self._mono_to_color_sdk = MonoToColorProcessorSDK()
            self._image_width = self._camera.image_width_pixels
            self._image_height = self._camera.image_height_pixels
            self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
                SENSOR_TYPE.BAYER,
                self._camera.color_filter_array_phase,
                self._camera.get_color_correction_matrix(),
                self._camera.get_default_white_balance_matrix(),
                self._camera.bit_depth
            )
            self._is_color = True
            
        self._bit_depth = camera.bit_depth
        self._camera.image_poll_timeout_ms = 0  # Do not want to block for long periods of time
        self._camera.exposure_time_us = 1000 # initializes the exposure time in seconds
        self._image_queue = queue.Queue(maxsize=2)

    def get_output_queue(self): 
        return self._image_queue

    def _get_color_image(self, frame):
        # type: (Frame) -> Image
        # verify the image size
        width = frame.image_buffer.shape[1]
        height = frame.image_buffer.shape[0]
        if (width != self._image_width) or (height != self._image_height):
            self._image_width = width
            self._image_height = height
            print("Image dimension change detected, image acquisition thread was updated")
        # color the image. transform_to_24 will scale to 8 bits per channel
        color_image_data = self._mono_to_color_processor.transform_to_24(frame.image_buffer,
                                                                         self._image_width,
                                                                         self._image_height)
        color_image_data = color_image_data.reshape(self._image_height, self._image_width, 3)
        print("color_image_data =", color_image_data)
        # return PIL Image object
        return Image.fromarray(color_image_data, mode='RGB')

    def _get_image(self, frame):
        # type: (Frame) -> Image
        # no coloring, just scale down image to 8 bpp and place into PIL Image object
        scaled_image = frame.image_buffer >> (self._bit_depth - 8)
        return Image.fromarray(scaled_image)
    

    def run(self):
        while not self._stop_event.is_set():
            try:
                frame = self._camera.get_pending_frame_or_null()
                if frame is not None:
                    if self._is_color:
                        pil_image = self._get_color_image(frame)
                    else:
                        pil_image = self._get_image(frame)
                    self._image_queue.put_nowait(pil_image)
            except queue.Full:
                # No point in keeping this image around when the queue is full, let's skip to the next one
                pass
            except Exception as error:
                print("Encountered error: {error}, image acquisition will stop.".format(error=error))
                break
        print("Image acquisition has stopped")
        if self._is_color:
            self._mono_to_color_processor.dispose()
            self._mono_to_color_sdk.dispose()


    def dispose(self):
        # type: (type(None)) -> None
        """
        Cleans up the TLCameraSDK instance - make sure to call this when you are done with the TLCameraSDK instance.
        If using the *with* statement, dispose is called automatically upon exit.

        """
        try:
            if self._disposed:
                return
            error_code = self._sdk.tl_camera_close_sdk()
            if error_code != 0:
                raise TLCameraError(_create_c_failure_message(self._sdk, "tl_camera_close_sdk", error_code))
            TLCameraSDK._is_sdk_open = False
            self._disposed = True
            self._current_camera_connect_callback = None
            self._current_camera_disconnect_callback = None
        except Exception as exception:
            print("Camera SDK destruction failed; " + str(exception))
            raise exception
        


    class CS165MU():
       def __init__(self, parent, image_queue, image_acquisition_thread,):
        # type: (typing.Any, queue.Queue, ImageAcquisitionThread) -> None
        self.image_queue = image_queue
        self.image_acquisition_thread = image_acquisition_thread
        self._image_width = 0
        self._image_height = 0
        # Instrument.__init__(self, parent)
        self.pack()
        self._get_image()





        # Add code method for setting exposure time 
        # Do we need code for 


    