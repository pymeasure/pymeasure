"""
tl_mono_to_color_processor.py
"""

from ctypes import cdll, POINTER, c_int, c_ushort, c_void_p, c_char_p, c_float, c_ubyte
from typing import Any
from traceback import format_exception
import logging
import platform

import numpy as np

from .tl_color_enums import FORMAT, FILTER_ARRAY_PHASE
from .tl_camera_enums import SENSOR_TYPE
from .tl_mono_to_color_enums import COLOR_SPACE

""" Setup logger """
_logger = logging.getLogger('thorlabs_tsi_sdk.tl_mono_to_color_processor')

""" error-handling methods """


def _get_last_error(sdk):
    try:
        error_pointer = sdk.tl_mono_to_color_get_last_error()
        if error_pointer is None:
            return None
        return str(error_pointer.decode("utf-8"))
    except Exception as exception:
        _logger.error("unable to get last error; " + str(exception))


def _create_c_failure_message(sdk, function_name, error_code):
    last_error = _get_last_error(sdk)
    failure_message = "{function_name}() returned non-zero error code: {error_code}; " \
                      "error message: {last_error}" \
        .format(function_name=function_name, error_code=error_code, last_error=last_error)
    return failure_message


""" Other ctypes types """

# noinspection PyTypeChecker
_3x3Matrix_float = c_float * 9

""" Classes """


class MonoToColorProcessorSDK(object):

    """
    MonoToColorProcessorSDK

    The SDK object that is used to create MonoToColorProcessor objects. There must be only one instance of this class
    active at a time. Use the :meth:`dispose()<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessorSDK.dispose>` method to destroy an SDK instance before
    creating another instance. *with* statements can also be used with this class to automatically dispose the SDK.

    """

    _is_sdk_open = False  # is SDK DLL currently being accessed by a MonoToColorSDK instance

    def __init__(self):
        # type: (type(None)) -> None
        self._disposed = True

        if MonoToColorProcessorSDK._is_sdk_open:
            raise MonoToColorError("MonoToColorProcessorSDK is already in use. Please dispose of the current instance "
                                   "before trying to create another instance.")

        try:
            if platform.system() == 'Windows':
                self._sdk = cdll.LoadLibrary(r"thorlabs_tsi_mono_to_color_processing.dll")
            elif platform.system() == 'Linux':
                try:
                    self._sdk = cdll.LoadLibrary(r"./libthorlabs_tsi_mono_to_color_processing.so")
                except OSError:
                    self._sdk = cdll.LoadLibrary(r"libthorlabs_tsi_mono_to_color_processing.so")
            else:
                raise MonoToColorError("{system} is not a supported platform.".format(system=platform.system()))
            self._disposed = False
        except OSError as os_error:
            raise MonoToColorError(str(os_error) +
                                   "\nUnable to load library - are the thorlabs tsi mono to color sdk libraries "
                                   "discoverable from the application directory? Try placing them in the same "
                                   "directory as your program, or adding the directory with the libraries to the "
                                   "PATH. Make sure to use 32-bit libraries when using a 32-bit python interpreter "
                                   "and 64-bit libraries when using a 64-bit interpreter.\n")

        error_code = self._sdk.tl_mono_to_color_processing_module_initialize()
        if error_code != 0:
            raise MonoToColorError("tl_mono_to_color_processing_module_initialize() returned error code: {error_code}\n"
                                   .format(error_code=error_code))
        MonoToColorProcessorSDK._is_sdk_open = True

        try:
            """ set C function argument types """
            self._sdk.tl_mono_to_color_create_mono_to_color_processor.argtypes = [c_int, c_int,
                                                                                  POINTER(_3x3Matrix_float),
                                                                                  POINTER(_3x3Matrix_float), c_int,
                                                                                  POINTER(c_void_p)]
            self._sdk.tl_mono_to_color_destroy_mono_to_color_processor.argtypes = [c_void_p]
            self._sdk.tl_mono_to_color_get_color_space.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_mono_to_color_set_color_space.argtypes = [c_void_p, c_int]
            self._sdk.tl_mono_to_color_get_output_format.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_mono_to_color_set_output_format.argtypes = [c_void_p, c_int]
            self._sdk.tl_mono_to_color_get_red_gain.argtypes = [c_void_p, POINTER(c_float)]
            self._sdk.tl_mono_to_color_set_red_gain.argtypes = [c_void_p, c_float]
            self._sdk.tl_mono_to_color_get_green_gain.argtypes = [c_void_p, POINTER(c_float)]
            self._sdk.tl_mono_to_color_set_green_gain.argtypes = [c_void_p, c_float]
            self._sdk.tl_mono_to_color_get_blue_gain.argtypes = [c_void_p, POINTER(c_float)]
            self._sdk.tl_mono_to_color_set_blue_gain.argtypes = [c_void_p, c_float]
            self._sdk.tl_mono_to_color_transform_to_48.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_int,
                                                                   POINTER(c_ushort)]
            self._sdk.tl_mono_to_color_transform_to_32.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_int,
                                                                   POINTER(c_ubyte)]
            self._sdk.tl_mono_to_color_transform_to_24.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_int,
                                                                   POINTER(c_ubyte)]
            self._sdk.tl_mono_to_color_processing_module_terminate.argtypes = []
            self._sdk.tl_mono_to_color_get_last_error.restype = c_char_p
            self._sdk.tl_mono_to_color_get_camera_sensor_type.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_mono_to_color_get_color_filter_array_phase.argtypes = [c_void_p, POINTER(c_int)]
            self._sdk.tl_mono_to_color_get_color_correction_matrix.argtypes = [c_void_p,
                                                                               POINTER(POINTER(_3x3Matrix_float))]
            self._sdk.tl_mono_to_color_get_default_white_balance_matrix.argtypes = [c_void_p,
                                                                                    POINTER(POINTER(_3x3Matrix_float))]
            self._sdk.tl_mono_to_color_get_bit_depth = [c_void_p, POINTER(c_int)]
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
        Cleans up the MonoToColorProcessorSDK instance - make sure to call this when you are done with the
        MonoToColorProcessorSDK instance. If using the *with* statement, dispose is called automatically upon exit.

        """
        try:
            if self._disposed:
                return
            error_code = self._sdk.tl_mono_to_color_processing_module_terminate()
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_processing_module_terminate", error_code))
            MonoToColorProcessorSDK._is_sdk_open = False
            self._disposed = True
        except Exception as exception:
            _logger.error("Mono To Color SDK destruction failed; " + str(exception))
            raise exception

    def create_mono_to_color_processor(self, camera_sensor_type, color_filter_array_phase, color_correction_matrix,
                                       default_white_balance_matrix, bit_depth):
        # type: (SENSOR_TYPE, FILTER_ARRAY_PHASE, np.array, np.array, int) -> MonoToColorProcessor
        """
        Creates a MonoToColorProcessor object using the given parameters.

        :parameter: - **camera_sensor_type** (:class:`SENSOR_TYPE<thorlabs_tsi_sdk.tl_camera_enums.SENSOR_TYPE>`) - The sensor type used by the camera. Use the property :attr:`TLCamera.camera_sensor_type<thorlabs_tsi_sdk.tl_camera.TLCamera.camera_sensor_type>` to get this information from a camera.
        :parameter: - **color_filter_array_phase** (:class:`FILTER_ARRAY_PHASE<thorlabs_tsi_sdk.tl_color.FILTER_ARRAY_PHASE>`) - The array phase of the camera's color filter. Use :attr:`TLCamera.color_filter_array_phase<thorlabs_tsi_sdk.tl_camera.TLCamera.color_filter_array_phase>` to get this information from a camera.
        :parameter: - **color_correction_matrix** (np.array) - A 3x3 correction matrix specific to a camera model that is used during color processing to achieve accurate coloration. use :meth:`TLCamera.get_color_correction_matrix<thorlabs_tsi_sdk.tl_camera.TLCamera.get_color_correction_matrix>` to get this information from a camera.
        :parameter: - **default_white_balance_matrix** (np.array) - A 3x3 correction matrix specific to a camera model that is used during color processing to white balance images under typical lighting conditions. Use :meth:`TLCamera.get_default_white_balance_matrix<thorlabs_tsi_sdk.tl_camera.TLCamera.get_default_white_balance_matrix>` to get this information from a camera.
        :parameter: - **bit_depth** (int) - The bit depth that will be used during color processing. To get the bit depth of a camera, use :attr:`TLCamera.bit_depth<thorlabs_tsi_sdk.tl_camera.TLCamera.bit_depth>`

        :returns: :class:`MonoToColorProcessor<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor>`

        """
        try:
            c_mono_to_color_handle = c_void_p()
            c_camera_sensor_type = c_int(camera_sensor_type)
            c_color_filter_array_phase = c_int(color_filter_array_phase)
            c_color_correction_matrix = _3x3Matrix_float(*color_correction_matrix)
            c_default_white_balance_matrix = _3x3Matrix_float(*default_white_balance_matrix)
            c_bit_depth = c_int(bit_depth)
            error_code = self._sdk.tl_mono_to_color_create_mono_to_color_processor(c_camera_sensor_type,
                                                                                   c_color_filter_array_phase,
                                                                                   c_color_correction_matrix,
                                                                                   c_default_white_balance_matrix,
                                                                                   c_bit_depth,
                                                                                   c_mono_to_color_handle)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_create_mono_to_color_processor", error_code))
            # noinspection PyProtectedMember
            return MonoToColorProcessor._create(self._sdk, c_mono_to_color_handle)
        except Exception as exception:
            _logger.error("Failed to create mono to color processor; " + str(exception))
            raise exception


class MonoToColorProcessor(object):

    """
    MonoToColorProcessor

    These objects are used to quickly convert monochrome image data to colored image data. When finished with a MonoToColorProcessor,
    call its :meth:`dispose<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.dispose>` method to clean up any opened resources. These object can
    be managed using *with* statements for automatic resource clean up. These objects can only be created by calls to
    :meth:`MonoToColorProcessorSDK.create_mono_to_color_processor()<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessorSDK.create_mono_to_color_processor>`

    """

    __key = object()

    @classmethod
    def _create(cls, sdk, mono_to_color_processor_handle):
        # type: (Any, Any) -> MonoToColorProcessor
        return MonoToColorProcessor(cls.__key, sdk, mono_to_color_processor_handle)

    def __init__(self, key, sdk, mono_to_color_processor_handle):
        # type: (type(object), Any, Any) -> None
        try:
            self._disposed = True
            assert (key == MonoToColorProcessor.__key), \
                "MonoToColorProcessor objects cannot be created manually. Please use " \
                "MonoToColorProcessorSDK.create_mono_to_color_processor to acquire new MonoToColorProcessor objects."
            self._sdk = sdk
            self._mono_to_color_processor_handle = mono_to_color_processor_handle
            self._disposed = False
        except Exception as exception:
            _logger.error("MonoToColorProcessor initialization failed; " + str(exception))
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
        Cleans up the MonoToColorProcessor instance - make sure to call this when you are done with the MonoToColor
        processor. If using the *with* statement, dispose is called automatically upon exit.

        """
        try:
            if self._disposed:
                return
            error_code = self._sdk.tl_mono_to_color_destroy_mono_to_color_processor(
                self._mono_to_color_processor_handle)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_destroy_mono_to_color_processor", error_code))
            self._disposed = True
        except Exception as exception:
            _logger.error("Could not dispose MonoToColorProcessor instance; " + str(exception))
            raise exception

    def transform_to_48(self, input_buffer, image_width_pixels, image_height_pixels):
        # type: (np.array, int, int) -> np.array
        """
        Convert monochrome image data into a 3-channel colored image with 16 bits per channel, resulting in 48 bits per
        pixel. The pixel data will be ordered according to the current value of
        :attr:`output_format<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.output_format>`.

        :param np.array input_buffer: Single channel monochrome image data. The size of this array should be image_width * image_height. The dtype of the array should be ctypes.c_ushort or a type of equivalent size, the image buffer that comes directly from the camera is compatible (see: :meth:`TLCamera.get_pending_frame_or_null()<thorlabs_tsi_sdk.tl_camera.TLCamera.get_pending_frame_or_null>`).
        :param int image_width_pixels: The width of the image in the image_buffer.
        :param int image_height_pixels: The height of the image in the image_buffer.
        :return np.array: 3-channel colored output image, *dtype* = ctypes.c_ushort.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels*image_height_pixels*3,), dtype=c_ushort)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))
            input_buffer_pointer = input_buffer.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            error_code = self._sdk.tl_mono_to_color_transform_to_48(self._mono_to_color_processor_handle,
                                                                    input_buffer_pointer,
                                                                    c_image_width,
                                                                    c_image_height,
                                                                    output_buffer_pointer)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_transform_to_48",
                                                                 error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform image to 48bpp; " + str(exception))
            raise exception

    def transform_to_32(self, input_buffer, image_width_pixels, image_height_pixels):
        # type: (np.array, int, int) -> np.array
        """
        Convert monochrome image data into a 4-channel colored image with 8 bits per channel, resulting in 32 bits per
        pixel. The pixel data will be ordered according to the current value of
        :attr:`output_format<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.output_format>`.

        :param np.array input_buffer: Single channel monochrome image data. The size of this array should be image_width * image_height. The dtype of the array should be ctypes.c_ushort or a type of equivalent size, the image buffer that comes directly from the camera is compatible (see: :meth:`TLCamera.get_pending_frame_or_null()<thorlabs_tsi_sdk.tl_camera.TLCamera.get_pending_frame_or_null>`).
        :param int image_width_pixels: The width of the image in the image_buffer.
        :param int image_height_pixels: The height of the image in the image_buffer.
        :return np.array: 4-channel colored output image, *dtype* = ctypes.c_ubyte.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels*image_height_pixels*4,), dtype=c_ubyte)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ubyte))
            input_buffer_pointer = input_buffer.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            error_code = self._sdk.tl_mono_to_color_transform_to_32(self._mono_to_color_processor_handle,
                                                                    input_buffer_pointer,
                                                                    c_image_width,
                                                                    c_image_height,
                                                                    output_buffer_pointer)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_transform_to_32",
                                                                 error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform image to 32bpp; " + str(exception))
            raise exception

    def transform_to_24(self, input_buffer, image_width_pixels, image_height_pixels):
        # type: (np.array, int, int) -> np.array
        """
        Convert monochrome image data into a 3-channel colored image with 8 bits per channel, resulting in 24 bits per
        pixel. The pixel data will be ordered according to the current value of
        :attr:`output_format<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.output_format>`.

        :param np.array input_buffer: Single channel monochrome image data. The size of this array should be image_width * image_height. The dtype of the array should be ctypes.c_ushort or a type of equivalent size, the image buffer that comes directly from the camera is compatible (see: :meth:`TLCamera.get_pending_frame_or_null()<thorlabs_tsi_sdk.tl_camera.TLCamera.get_pending_frame_or_null>`).
        :param int image_width_pixels: The width of the image in the input_buffer.
        :param int image_height_pixels: The height of the image in the input_buffer.
        :return np.array: 3-channel colored output image, *dtype* = ctypes.c_ubyte.
        """
        try:
            output_buffer = np.zeros(shape=(image_width_pixels*image_height_pixels*3,), dtype=c_ubyte)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ubyte))
            input_buffer_pointer = input_buffer.ctypes.data_as(POINTER(c_ushort))
            c_image_width = c_int(image_width_pixels)
            c_image_height = c_int(image_height_pixels)
            error_code = self._sdk.tl_mono_to_color_transform_to_24(self._mono_to_color_processor_handle,
                                                                    input_buffer_pointer,
                                                                    c_image_width,
                                                                    c_image_height,
                                                                    output_buffer_pointer)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_transform_to_24",
                                                                 error_code))
            return output_buffer
        except Exception as exception:
            _logger.error("Could not transform image to 24bpp; " + str(exception))
            raise exception

    """ Properties """

    @property
    def color_space(self):
        """
        The color space of the mono to color processor. See :class:`COLOR_SPACE<thorlabs_tsi_sdk.tl_mono_to_color_enums.COLOR_SPACE>` for what color spaces
        are available.

        :type: :class:`COLOR_SPACE<thorlabs_tsi_sdk.tl_mono_to_color_enums.COLOR_SPACE>`
        """
        try:
            color_space = c_int()
            error_code = self._sdk.tl_mono_to_color_get_color_space(self._mono_to_color_processor_handle, color_space)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_color_space",
                                                                 error_code))
            return COLOR_SPACE(int(color_space.value))
        except Exception as exception:
            _logger.error("Could not get color space; " + str(exception))
            raise exception

    @color_space.setter
    def color_space(self, color_space):
        try:
            c_value = c_int(color_space)
            error_code = self._sdk.tl_mono_to_color_set_color_space(self._mono_to_color_processor_handle, c_value)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_set_color_space",
                                                                 error_code))
        except Exception as exception:
            _logger.error("Could not set color space; " + str(exception))
            raise exception

    @property
    def output_format(self):
        """
        The format of the colored output image. This describes how the data is ordered in the returned buffer from the
        transform functions. By default it is RGB_PIXEL. See :class:`FORMAT<thorlabs_tsi_sdk.tl_color_enums.FORMAT>`.

        :type: :class:`FORMAT<thorlabs_tsi_sdk.tl_mono_to_color_enums.FORMAT>`
        """
        try:
            output_format = c_int()
            error_code = self._sdk.tl_mono_to_color_get_output_format(self._mono_to_color_processor_handle,
                                                                      output_format)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_output_format",
                                                                 error_code))
            return FORMAT(int(output_format.value))
        except Exception as exception:
            _logger.error("Could not get output format; " + str(exception))
            raise exception

    @output_format.setter
    def output_format(self, output_format):
        try:
            c_value = c_int(output_format)
            error_code = self._sdk.tl_mono_to_color_set_output_format(self._mono_to_color_processor_handle, c_value)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_set_output_format",
                                                                 error_code))
        except Exception as exception:
            _logger.error("Could not set output format; " + str(exception))
            raise exception

    @property
    def red_gain(self):
        """
        The gain factor that will be applied to the red pixel values in the image. The red intensities will be
        multiplied by this gain value in the final colored image. The default red gain is
        taken from the :attr:`default_white_balance_matrix<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.default_white_balance_matrix>` that
        is passed in when constructing a
        :meth:`MonoToColorProcessor<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessorSDK.create_mono_to_color_processor>`.

        :type: float
        """
        try:
            red_gain = c_float()
            error_code = self._sdk.tl_mono_to_color_get_red_gain(self._mono_to_color_processor_handle, red_gain)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_red_gain",
                                                                 error_code))
            return float(red_gain.value)
        except Exception as exception:
            _logger.error("Could not get red gain value; " + str(exception))
            raise exception

    @red_gain.setter
    def red_gain(self, red_gain):
        try:
            c_value = c_float(red_gain)
            error_code = self._sdk.tl_mono_to_color_set_red_gain(self._mono_to_color_processor_handle, c_value)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_set_red_gain",
                                                                 error_code))
        except Exception as exception:
            _logger.error("Could not set red gain value; " + str(exception))
            raise exception

    @property
    def blue_gain(self):
        """
        The gain factor that will be applied to the red pixel values in the image. The blue intensities will be
        multiplied by this gain value in the final colored image. The default blue gain is
        taken from the :attr:`default_white_balance_matrix<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.default_white_balance_matrix>` that
        is passed in when constructing a
        :meth:`MonoToColorProcessor<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessorSDK.create_mono_to_color_processor>`.

        :type: float
        """
        try:
            blue_gain = c_float()
            error_code = self._sdk.tl_mono_to_color_get_blue_gain(self._mono_to_color_processor_handle, blue_gain)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_blue_gain",
                                                                 error_code))
            return float(blue_gain.value)
        except Exception as exception:
            _logger.error("Could not get blue gain value; " + str(exception))
            raise exception

    @blue_gain.setter
    def blue_gain(self, blue_gain):
        try:
            c_value = c_float(blue_gain)
            error_code = self._sdk.tl_mono_to_color_set_blue_gain(self._mono_to_color_processor_handle, c_value)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_set_blue_gain",
                                                                 error_code))
        except Exception as exception:
            _logger.error("Could not set blue gain value; " + str(exception))
            raise exception

    @property
    def green_gain(self):
        """
        The gain factor that will be applied to the red pixel values in the image. The green intensities will be
        multiplied by this gain value in the final colored image. The default green gain is
        taken from the :attr:`default_white_balance_matrix<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessor.default_white_balance_matrix>` that
        is passed in when constructing a
        :meth:`MonoToColorProcessor<thorlabs_tsi_sdk.tl_mono_to_color_processor.MonoToColorProcessorSDK.create_mono_to_color_processor>`.

        :type: float
        """
        try:
            green_gain = c_float()
            error_code = self._sdk.tl_mono_to_color_get_green_gain(self._mono_to_color_processor_handle, green_gain)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_green_gain",
                                                                 error_code))
            return float(green_gain.value)
        except Exception as exception:
            _logger.error("Could not get green gain value; " + str(exception))
            raise exception

    @green_gain.setter
    def green_gain(self, green_gain):
        try:
            c_value = c_float(green_gain)
            error_code = self._sdk.tl_mono_to_color_set_green_gain(self._mono_to_color_processor_handle, c_value)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_set_green_gain",
                                                                 error_code))
        except Exception as exception:
            _logger.error("Could not set green gain value; " + str(exception))
            raise exception

    @property
    def camera_sensor_type(self):
        """
        The sensor type of the camera (monochrome, bayer, etc...). This value is passed in during construction and may
        be read back using this property.

        :type: :class:`SENSOR_TYPE<thorlabs_tsi_sdk.tl_camera_enums.SENSOR_TYPE>`
        """
        try:
            camera_sensor_type = c_int()
            error_code = self._sdk.tl_mono_to_color_get_camera_sensor_type(self._mono_to_color_processor_handle,
                                                                           camera_sensor_type)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_camera_sensor_type",
                                                                 error_code))
            return SENSOR_TYPE(int(camera_sensor_type.value))
        except Exception as exception:
            _logger.error("Could not get camera sensor type; " + str(exception))
            raise exception

    @property
    def color_filter_array_phase(self):
        """
        The color filter array phase used in this mono to color processor. This value is passed in during construction
        and may be read back using this property.

        :type: :class:`FILTER_ARRAY_PHASE<thorlabs_tsi_sdk.tl_color.FILTER_ARRAY_PHASE>`
        """
        try:
            color_filter_array_phase = c_int()
            error_code = self._sdk.tl_mono_to_color_get_color_filter_array_phase(self._mono_to_color_processor_handle,
                                                                                 color_filter_array_phase)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_get_color_filter_array_phase", error_code))
            return FILTER_ARRAY_PHASE(int(color_filter_array_phase.value))
        except Exception as exception:
            _logger.error("Could not get color filter array phase; " + str(exception))
            raise exception

    @property
    def color_correction_matrix(self):
        """
        The default color correction matrix associated with the mono to color processor. This value is passed in during
        construction and may be read back using this property.

        :type: np.array
        """
        try:
            color_correction_matrix = _3x3Matrix_float()
            error_code = self._sdk.tl_mono_to_color_get_color_correction_matrix(self._mono_to_color_processor_handle,
                                                                                color_correction_matrix)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_get_color_correction_matrix", error_code))
            color_correction_matrix_as_np_array = np.array([float(color_correction_matrix[0]),
                                                            float(color_correction_matrix[1]),
                                                            float(color_correction_matrix[2]),
                                                            float(color_correction_matrix[3]),
                                                            float(color_correction_matrix[4]),
                                                            float(color_correction_matrix[5]),
                                                            float(color_correction_matrix[6]),
                                                            float(color_correction_matrix[7]),
                                                            float(color_correction_matrix[8])])
            return color_correction_matrix_as_np_array
        except Exception as exception:
            _logger.error("Could not get color correction matrix; " + str(exception))
            raise exception

    @property
    def default_white_balance_matrix(self):
        """
        The default white balance matrix associated with the mono to color processor. This value is passed in during
        construction and may be read back using this property.

        :type: np.array
        """
        try:
            default_white_balance_matrix = _3x3Matrix_float()
            error_code = self._sdk.tl_mono_to_color_get_default_white_balance_matrix(
                self._mono_to_color_processor_handle, default_white_balance_matrix)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(
                    self._sdk, "tl_mono_to_color_get_default_white_balance_matrix", error_code))
            default_white_balance_matrix_as_np_array = np.array([float(default_white_balance_matrix[0]),
                                                                float(default_white_balance_matrix[1]),
                                                                float(default_white_balance_matrix[2]),
                                                                float(default_white_balance_matrix[3]),
                                                                float(default_white_balance_matrix[4]),
                                                                float(default_white_balance_matrix[5]),
                                                                float(default_white_balance_matrix[6]),
                                                                float(default_white_balance_matrix[7]),
                                                                float(default_white_balance_matrix[8])])
            return default_white_balance_matrix_as_np_array
        except Exception as exception:
            _logger.error("Could not get default white balance matrix; " + str(exception))
            raise exception

    @property
    def bit_depth(self):
        """
        The bit depth associated with the mono to color processor. This value is passed in during construction and may
        be read back using this property.

        :type: int
        """
        try:
            bit_depth = c_int()
            error_code = self._sdk.tl_mono_to_color_get_bit_depth(self._mono_to_color_processor_handle, bit_depth)
            if error_code != 0:
                raise MonoToColorError(_create_c_failure_message(self._sdk, "tl_mono_to_color_get_bit_depth",
                                                                 error_code))
            return int(bit_depth.value)
        except Exception as exception:
            _logger.error("Could not get bit depth; " + str(exception))
            raise exception


""" Error handling """


class MonoToColorError(Exception):
    def __init__(self, message):
        _logger.debug(message)
        super(MonoToColorError, self).__init__(message)
