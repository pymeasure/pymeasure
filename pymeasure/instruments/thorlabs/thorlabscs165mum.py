#Author: Amelie Deshazer 
#Date: 6/18/24 
#Address:
#Purpose: Communicate with the ThorLabs CS165MU/M color camera

import logging 
import tifffile
import os
import threading
import queue
from PIL import Image
from ctypes import cdll
get_directory = os.getcwd()
print(get_directory, "= get directory")

sdk = cdll.LoadLibrary(r"C:\Users\desha\Codes\pymeasure\pymeasure\instruments\thorlabs\dlls\thorlabs_tsi_camera_sdk.dll")
# from pymeasure.instruments.thorlabs.dlls.tl_camera import TLCameraSDK, TLCamera, Frame, TLCameraError
# from pymeasure.instruments.thorlabs.dlls.tl_mono_to_color_processor import MonoToColorProcessorSDK
# from pymeasure.instruments import Instrument
# from ctypes import c_longlong


# # Sets the number of images to be taken and the output directory
# NUMBER_OF_IMAGES = 10
# OUTPUT_DIRECTORY = os.path.abspath(r'.')
# FILE_NAME = "image.tif"

# # Deletes images if already existed 
# if os.path.exists(OUTPUT_DIRECTORY + os.sep + FILE_NAME):
#     os.remove(OUTPUT_DIRECTORY + os.sep + FILE_NAME)

# class ImageAcquisitionThread(threading.Thread):
#     """This class derives from threading.Thread and is given a TLCamera instance. Focus is on initializing the mono to color camera data. 
#     When started, the camera will acquire images and place them into a queue. It will convert the data into 24-bit per pixel color images. 
#     """
#     def __init__(self, camera):
#         # type: (TLCamera) -> ImageAcquisitionThread
#         super(ImageAcquisitionThread, self).__init__()
#         self._camera = camera
#         self._previous_timestamp = 0

#         # setup color processing if necessary
#         if self._camera.camera_sensor_type != SENSOR_TYPE.BAYER:
#             # Sensor type is not compatible with the color processing library
#             self._is_color = False
#         else:
#             self._mono_to_color_sdk = MonoToColorProcessorSDK()
#             self._image_width = self._camera.image_width_pixels
#             self._image_height = self._camera.image_height_pixels
#             self._mono_to_color_processor = self._mono_to_color_sdk.create_mono_to_color_processor(
#                 SENSOR_TYPE.BAYER,
#                 self._camera.color_filter_array_phase,
#                 self._camera.get_color_correction_matrix(),
#                 self._camera.get_default_white_balance_matrix(),
#                 self._camera.bit_depth
#             )
#             self._is_color = True

#         self._bit_depth = camera.bit_depth
#         self._camera.image_poll_timeout_ms = 0  # Do not want to block for long periods of time
#         self._image_queue = queue.Queue(maxsize=2)
#         self._stop_event = threading.Event()

#     def get_output_queue(self):
#         # type: (type(None)) -> queue.Queue
#         return self._image_queue

#     def stop(self):
#         self._stop_event.set()

#     def _get_color_image(self, frame):
#         # type: (Frame) -> Image
#         # verify the image size
#         width = frame.image_buffer.shape[1]
#         height = frame.image_buffer.shape[0]
#         if (width != self._image_width) or (height != self._image_height):
#             self._image_width = width
#             self._image_height = height
#             print("Image dimension change detected, image acquisition thread was updated")
#         # color the image. transform_to_24 will scale to 8 bits per channel
#         color_image_data = self._mono_to_color_processor.transform_to_24(frame.image_buffer,
#                                                                          self._image_width,
#                                                                          self._image_height)
#         color_image_data = color_image_data.reshape(self._image_height, self._image_width, 3)
#         # return PIL Image object
#         return Image.fromarray(color_image_data, mode='RGB')

#     def _get_image(self, frame):
#         # type: (Frame) -> Image
#         # no coloring, just scale down image to 8 bpp and place into PIL Image object
#         scaled_image = frame.image_buffer >> (self._bit_depth - 8)
#         return Image.fromarray(scaled_image)

#     def run(self):
#         while not self._stop_event.is_set():
#             try:
#                 frame = self._camera.get_pending_frame_or_null()
#                 if frame is not None:
#                     if self._is_color:
#                         pil_image = self._get_color_image(frame)
#                     else:
#                         pil_image = self._get_image(frame)
#                     self._image_queue.put_nowait(pil_image)
#             except queue.Full:
#                 # No point in keeping this image around when the queue is full, let's skip to the next one
#                 pass
#             except Exception as error:
#                 print("Encountered error: {error}, image acquisition will stop.".format(error=error))
#                 break
#         print("Image acquisition has stopped")
#         if self._is_color:
#             self._mono_to_color_processor.dispose()
#             self._mono_to_color_sdk.dispose()

# class CS165MUM(Instrument):
#     """This class is a wrapper around the TLCamera class. It is used to acquire images from the camera and place them into a queue. 
#     The class ImageAcquistionThread is accessed through the class with accessing an array of data to be saved into a TIFF file."""
#     def __init__(self, parent, image_queue, image_acquisition_thread):
#         # type: (typing.Any, queue.Queue, ImageAcquisitionThread) -> None
#         self.image_queue = image_queue
#         self.image_acquisition_thread = image_acquisition_thread
#         self._image_width = 0
#         self._image_height = 0
#         Instrument.__init__(self, parent)
#         self.pack()
#         self._get_image()

#     @property
#     def exposure_time_us(self):
#         """Sets and gets the exposure time in microseconds. It is advised to 
#         wait 300ms before settings the exposure time."""

#         exposure_time_us = c_longlong() #64-bit integer
#         error = self._sdk.tl_get_exposure_time_us(self._camera, exposure_time_us)
#         if error !=0: 
#             return int(exposure_time_us.value) 
#         else: 
#             raise ValueError(f"Error in getting exposure time: {error}")
        
#     @exposure_time_us.setter
#     def exposure_time_us(self, exposure_time_us):
#         try:
#             c_value = c_longlong(exposure_time_us)
#             error = self._sdk.tl_set_exposure_time_us(self._camera, c_value)
#         except TLCameraError as e:
#             raise ValueError(f"Error in setting exposure time: {error}")


# #Lines of code will be disarming and saving file into a TIFF. Make sure to add this after setting up the directory 

#     with TLCameraSDK() as sdk:
#         cameras = sdk.discover_available_cameras()
#         if len(cameras) == 0:
#             print("Error: no cameras detected!")

#         with sdk.open_camera(cameras[0]) as camera:
#             camera.frames_per_trigger_zero_for_unlimited = 0 
#             camera.image_poll_timeout_ms = 2000
#             camera.arm(2)
#             camera.exposure_time_us = 1000 # create a method with set and get exposure time 

#             camera = ImageAcquisitionThread() #calls method for converting mono to color images. Takes frames and now needs to be saved. 
            
#         def save_image(self):
#             color_data_image = self.image_acquisition_thread.color_data_image #Accesses color_data_image
#             with tifffile.TiffWriter(OUTPUT_DIRECTORY + os.sep + FILE_NAME, append = True) as tiff:
#                 tiff.save(data = color_data_image, 
#                         compress = 0)




#         # camera is acquiring frames
#         # camera.issue_software_trigger()
#         # frames_counted = 0
#         # while frames_counted < NUMBER_OF_IMAGES:
#         #     frame = camera.get_pending_frame_or_null()
#         #     if frame is None: 
#         #         raise TimeoutError("Timeout error: no frame was received") 

#         # frames_counted += 1

