"""
tl_mono_to_color_processor.py ***BETA***
"""

from ctypes import cdll, POINTER, c_int, c_ushort, c_void_p, c_char_p, c_float, c_ubyte
from typing import Any
from traceback import format_exception
import logging
import platform

import numpy as np

from .tl_polarization_enums import POLAR_PHASE

""" Setup logger """
logging.basicConfig(level=logging.ERROR,
                    format='%(module)s %(asctime)s %(levelname)s: %(message)s')
_logger = logging.getLogger('thorlabs_tsi_sdk.tl_polarization_processor')

""" error-handling methods """


def _get_last_error(sdk):
    return ""  # tl_polarization_processor_get_last_error()


def _create_c_failure_message(sdk, function_name, error_code):
    last_error = _get_last_error(sdk)
    failure_message = "{function_name}() returned non-zero error code: {error_code}; " \
                      "error message: {last_error}" \
        .format(function_name=function_name, error_code=error_code, last_error=last_error)
    return failure_message


""" Other ctypes types """

_4x4Matrix_float = c_float * 16

""" Classes """


class PolarizationProcessorSDK(object):

    """
    PolarizationProcessorSDK

    The polarization processor SDK loads DLLs into memory and provides functions to polarization processor instances.
    Be sure to dispose all PolarizationProcessor objects and then dispose the PolarizationProcessorSDK before exiting
    the application. *with* statements can also be used with this class to automatically dispose the SDK.

    """

    _is_sdk_open = False  # is SDK DLL currently being accessed by a MonoToColorSDK instance

    def __init__(self):
        # type: (type(None)) -> None
        self._disposed = True

        if PolarizationProcessorSDK._is_sdk_open:
            raise PolarizationError("PolarizationProcessorSDK is already in use. Please dispose of the current "
                                    "instance before trying to create another instance.")

        try:
            if platform.system() == 'Windows':
                self._sdk = cdll.LoadLibrary(r"thorlabs_tsi_polarization_processor.dll")
            elif platform.system() == 'Linux':
                try:
                    self._sdk = cdll.LoadLibrary(r"./libthorlabs_tsi_polarization_processor.so")
                except OSError:
                    self._sdk = cdll.LoadLibrary(r"libthorlabs_tsi_polarization_processor.so")
            else:
                raise PolarizationError("{system} is not a supported platform.".format(system=platform.system()))
            self._disposed = False
        except OSError as os_error:
            raise PolarizationError(str(os_error) +
                                    "\nUnable to load library - are the thorlabs tsi polarization libraries "
                                    "discoverable from the application directory? Try placing them in the same "
                                    "directory as your program, or adding the directory with the libraries to the "
                                    "PATH. Make sure to use 32-bit libraries when using a 32-bit python interpreter "
                                    "and 64-bit libraries when using a 64-bit interpreter.\n")

        error_code = self._sdk.tl_polarization_processor_module_initialize()
        if error_code != 0:
            raise PolarizationError("tl_polarization_processing_module_initialize() returned error code: {error_code}\n"
                                    .format(error_code=error_code))
        PolarizationProcessorSDK._is_sdk_open = True

        try:
            """ set C function argument types """
            self._sdk.tl_polarization_processor_create_polarization_processor.argtypes = [POINTER(c_void_p)]
            self._sdk.tl_polarization_processor_destroy_polarization_processor.argtypes = [c_void_p]
            self._sdk.tl_polarization_processor_set_custom_calibration_coefficients.argtypes = \
                [c_void_p,
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float)]
            self._sdk.tl_polarization_processor_get_custom_calibration_coefficients.argtypes = \
                [c_void_p,
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float),
                 POINTER(_4x4Matrix_float)]
            self._sdk.tl_polarization_processor_transform.argtypes = [c_void_p,
                                                                      c_int,
                                                                      POINTER(c_ushort),
                                                                      c_int,
                                                                      c_int,
                                                                      c_int,
                                                                      c_int,
                                                                      c_int,
                                                                      c_ushort,
                                                                      POINTER(c_float),
                                                                      POINTER(c_ushort),
                                                                      POINTER(c_ushort),
                                                                      POINTER(c_ushort),
                                                                      POINTER(c_ushort),
                                                                      POINTER(c_ushort),
                                                                      ]
            self._sdk.tl_polarization_processor_destroy_polarization_processor.argtypes = [c_void_p]
        except Exception as exception:
            _logger.error("SDK initialization failed; " + str(exception))
            raise exception

    def __del__(self):
        self.dispose()

    """ with statement functionality """

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            _logger.debug("".join(format_exception(exception_type, exception_value, exception_traceback)))
        self.dispose()
        return True if exception_type is None else False

    """ methods """

    def dispose(self):
        # type: (type(None)) -> None
        """
        Cleans up the PolarizationProcessorSDK instance - make sure to call this when you are done with the
        PolarizationProcessorSDK instance. If using the *with* statement, dispose is called automatically upon exit.

        """
        try:
            if self._disposed:
                return
            error_code = self._sdk.tl_polarization_processor_module_terminate()
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(
                    self._sdk, "tl_polarization_processor_module_terminate", error_code))
            PolarizationProcessorSDK._is_sdk_open = False
            self._disposed = True
        except Exception as exception:
            _logger.error("Polarization SDK destruction failed; " + str(exception))
            raise exception

    def create_polarization_processor(self):
        # type: (type(None)) -> PolarizationProcessor
        """
        Creates a Polarization Processor object.

        :returns: :class:`PolarizationProcessor<thorlabs_tsi_sdk.tl_polarization_processor.PolarizationProcessor>`

        """
        try:
            c_polarization_handle = c_void_p()
            error_code = self._sdk.tl_polarization_processor_create_polarization_processor(c_polarization_handle)
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(
                    self._sdk, "tl_polarization_processor_create_polarization_processor", error_code))
            # noinspection PyProtectedMember
            return PolarizationProcessor._create(self._sdk, c_polarization_handle)
        except Exception as exception:
            _logger.error("Failed to create polarization processor; " + str(exception))
            raise exception


class PolarizationProcessor(object):

    """
    PolarizationProcessor

    These objects are used to convert raw sensor data to polarized data. When finished with a PolarizationProcessor,
    call its :meth:`dispose<thorlabs_tsi_sdk.tl_polarization_processor.PolarizationProcessor.dispose>` method to clean up any opened resources. These object can
    be managed using *with* statements for automatic resource clean up. These objects can only be created by calls to
    :meth:`PolarizationProcessorSDK.create_polarization_processor()<thorlabs_tsi_sdk.tl_polarization_processor.PolarizationProcessorSDK.create_polarization_processor>`

    The transform functions return an output image with values from 0 to max value for each pixel. To calculate
    scaled values for each pixel, you may use the following equation:

    • polarization_parameter_value = pixel_integer_value * (max_parameter_value / (2^bit_depth - 1)) + min_parameter_value

    The suggested min and max for each type are as follows:

    • Azimuth: (range from -90° to 90°)
        ◦ min_parameter_value = -90
        ◦ max_parameter_value = 180

    • DoLP: (range from 0 to 100%)
        ◦ min_parameter_value = 0
        ◦ max_parameter_value = 100

    • Intensity: (range from 0 to 100)
        ◦ min_parameter_value = 0
        ◦ max_parameter_value = 100

    """

    __key = object()

    @classmethod
    def _create(cls, sdk, polarization_processor_handle):
        # type: (Any, Any) -> PolarizationProcessor
        return PolarizationProcessor(cls.__key, sdk, polarization_processor_handle)

    def __init__(self, key, sdk, polarization_processor_handle):
        # type: (type(object), Any, Any) -> None
        try:
            self._disposed = True
            assert (key == PolarizationProcessor.__key), \
                "PolarizationProcessor objects cannot be created manually. Please use " \
                "PolarizationProcessorSDK.create_polarization_processor to acquire new PolarizationProcessor objects."
            self._sdk = sdk
            self._polarization_processor_handle = polarization_processor_handle
            self._disposed = False
        except Exception as exception:
            _logger.error("PolarizationProcessor initialization failed; " + str(exception))
            raise exception

    def __del__(self):
        self.dispose()

    """ with statement functionality """
    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type is not None:
            _logger.debug("".join(format_exception(exception_type, exception_value, exception_traceback)))
        self.dispose()
        return True if exception_type is None else False

    def dispose(self):
        # type: (type(None)) -> None
        """
        Cleans up the PolarizationProcessor instance - make sure to call this when you are done with the polarization
        processor. If using the *with* statement, dispose is called automatically upon exit.

        """
        try:
            if self._disposed:
                return
            error_code = self._sdk.tl_polarization_processor_destroy_polarization_processor(
                self._polarization_processor_handle)
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(
                    self._sdk, "tl_polarization_processor_destroy_polarization_processor", error_code))
            self._disposed = True
        except Exception as exception:
            _logger.error("Could not dispose PolarizationProcessor instance; " + str(exception))
            raise exception

    def transform_to_intensity(self,
                               sensor_polar_phase,
                               input_image,
                               image_origin_x_pixels,
                               image_origin_y_pixels,
                               image_width_pixels,
                               image_height_pixels,
                               input_image_bit_depth,
                               output_max_value):
        # type: (POLAR_PHASE, np.array, int, int, int, int, int, int) -> np.array
        """
        Transforms raw-image data into the intensity-output buffer, which shows the brightness of the light at each pixel.

        :param sensor_polar_phase: The polar phase (in degrees) of the origin (top-left) pixel of the camera sensor.
        :param input_image: Unprocessed input image delivered by the camera.
        :param image_origin_x_pixels: The X position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_origin_y_pixels: The Y position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_width_pixels: Width of input image in pixels
        :param image_height_pixels: Height of input image in pixels
        :param input_image_bit_depth: Bit depth of input image pixels
        :param output_max_value: The maximum possible pixel value in the output images. Must be between 1 and 65535.
        :return np.array: Array containing the total optical power (intensity) output, *dtype* = ctypes.c_ushort.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels * image_height_pixels,), dtype=c_ushort)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))
            input_buffer_pointer = input_image.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            c_image_origin_x_pixels = c_int(image_origin_x_pixels)
            c_image_origin_y_pixels = c_int(image_origin_y_pixels)
            c_input_image_bit_depth = c_int(input_image_bit_depth)
            c_output_max_value = c_ushort(output_max_value)
            c_sensor_polar_phase = c_int(sensor_polar_phase)
            error_code = self._sdk.tl_polarization_processor_transform(self._polarization_processor_handle,
                                                                       c_sensor_polar_phase,
                                                                       input_buffer_pointer,
                                                                       c_image_origin_x_pixels,
                                                                       c_image_origin_y_pixels,
                                                                       c_image_width,
                                                                       c_image_height,
                                                                       c_input_image_bit_depth,
                                                                       c_output_max_value,
                                                                       None,  # normalized_stokes_vector_coefficients_x2
                                                                       output_buffer_pointer,  # total_optical_power
                                                                       None,  # horizontal_vertical_linear_polarization
                                                                       None,  # diagonal_linear_polarization
                                                                       None,  # azimuth
                                                                       None)  # DOLP
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(self._sdk, "tl_polarization_processor_transform",
                                                                  error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform to intensity; " + str(exception))
            raise exception

    def transform_to_dolp(self,
                          sensor_polar_phase,
                          input_image,
                          image_origin_x_pixels,
                          image_origin_y_pixels,
                          image_width_pixels,
                          image_height_pixels,
                          input_image_bit_depth,
                          output_max_value):
        # type: (POLAR_PHASE, np.array, int, int, int, int, int, int) -> np.array
        """
        Transforms raw-image data into a DoLP (degree of linear polarization) output buffer, which is a measure of how polarized the light is from none to totally polarized.

        :param sensor_polar_phase: The polar phase (in degrees) of the origin (top-left) pixel of the camera sensor.
        :param input_image: Unprocessed input image delivered by the camera.
        :param image_origin_x_pixels: The X position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_origin_y_pixels: The Y position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_width_pixels: Width of input image in pixels
        :param image_height_pixels: Height of input image in pixels
        :param input_image_bit_depth: Bit depth of input image pixels
        :param output_max_value: The maximum possible pixel value in the output images. Must be between 1 and 65535.
        :return np.array: Array containing the DoLP (degree of linear polarization) output, *dtype* = ctypes.c_ushort.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels * image_height_pixels,), dtype=c_ushort)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))
            input_buffer_pointer = input_image.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            c_image_origin_x_pixels = c_int(image_origin_x_pixels)
            c_image_origin_y_pixels = c_int(image_origin_y_pixels)
            c_input_image_bit_depth = c_int(input_image_bit_depth)
            c_output_max_value = c_ushort(output_max_value)
            c_sensor_polar_phase = c_int(sensor_polar_phase)
            error_code = self._sdk.tl_polarization_processor_transform(self._polarization_processor_handle,
                                                                       c_sensor_polar_phase,
                                                                       input_buffer_pointer,
                                                                       c_image_origin_x_pixels,
                                                                       c_image_origin_y_pixels,
                                                                       c_image_width,
                                                                       c_image_height,
                                                                       c_input_image_bit_depth,
                                                                       c_output_max_value,
                                                                       None,  # normalized_stokes_vector_coefficients_x2
                                                                       None,  # total_optical_power
                                                                       None,  # horizontal_vertical_linear_polarization
                                                                       None,  # diagonal_linear_polarization
                                                                       None,  # azimuth
                                                                       output_buffer_pointer)  # DoLP
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(self._sdk, "tl_polarization_processor_transform",
                                                                  error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform to DoLP; " + str(exception))
            raise exception

    def transform_to_azimuth(self,
                             sensor_polar_phase,
                             input_image,
                             image_origin_x_pixels,
                             image_origin_y_pixels,
                             image_width_pixels,
                             image_height_pixels,
                             input_image_bit_depth,
                             output_max_value):
        # type: (POLAR_PHASE, np.array, int, int, int, int, int, int) -> np.array
        """
        Transforms raw-image data into an azimuth-output buffer, which shows the angle of polarized light at each pixel.

        :param sensor_polar_phase: The polar phase (in degrees) of the origin (top-left) pixel of the camera sensor.
        :param input_image: Unprocessed input image delivered by the camera.
        :param image_origin_x_pixels: The X position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_origin_y_pixels: The Y position of the origin (top-left) of the input image on the sensor. Warning: Some camera models may nudge input ROI values. Please read values back from camera. See :attr:`TLCamera.roi<thorlabs_tsi_sdk.tl_camera.TLCamera.roi>`.
        :param image_width_pixels: Width of input image in pixels
        :param image_height_pixels: Height of input image in pixels
        :param input_image_bit_depth: Bit depth of input image pixels
        :param output_max_value: The maximum possible pixel value in the output images. Must be between 1 and 65535.
        :return np.array: Array containing the azimuth (polar angle) output, *dtype* = ctypes.c_ushort.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels * image_height_pixels,), dtype=c_ushort)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))
            input_buffer_pointer = input_image.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            c_image_origin_x_pixels = c_int(image_origin_x_pixels)
            c_image_origin_y_pixels = c_int(image_origin_y_pixels)
            c_input_image_bit_depth = c_int(input_image_bit_depth)
            c_output_max_value = c_ushort(output_max_value)
            c_sensor_polar_phase = c_int(sensor_polar_phase)
            error_code = self._sdk.tl_polarization_processor_transform(self._polarization_processor_handle,
                                                                       c_sensor_polar_phase,
                                                                       input_buffer_pointer,
                                                                       c_image_origin_x_pixels,
                                                                       c_image_origin_y_pixels,
                                                                       c_image_width,
                                                                       c_image_height,
                                                                       c_input_image_bit_depth,
                                                                       c_output_max_value,
                                                                       None,  # normalized_stokes_vector_coefficients_x2
                                                                       None,  # total_optical_power
                                                                       None,  # horizontal_vertical_linear_polarization
                                                                       None,  # diagonal_linear_polarization
                                                                       output_buffer_pointer,  # azimuth
                                                                       None)  # DoLP
            if error_code != 0:
                raise PolarizationError(_create_c_failure_message(self._sdk, "tl_polarization_processor_transform",
                                                                  error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform to azimuth; " + str(exception))
            raise exception

    """ Properties """


""" Error handling """


class PolarizationError(Exception):
    def __init__(self, message):
        _logger.debug(message)
        super(PolarizationError, self).__init__(message)
