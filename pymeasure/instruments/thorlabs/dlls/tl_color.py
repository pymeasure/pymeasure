"""
tl_color.py
"""
from ctypes import cdll, POINTER, c_int, c_ushort, c_void_p, c_float, c_ubyte
from traceback import format_exception
import logging

import numpy as np

from .tl_color_enums import FORMAT, FILTER_ARRAY_PHASE, FILTER_TYPE

_logger = logging.getLogger(__name__)

""" Config constants """
_STRING_MAX = 4096

""" Other ctypes types """
_3x3Matrix = c_float * 9

""" ColorProcessorSDK """


class ColorProcessorSDK(object):

    _is_sdk_open = False  # is SDK DLL currently being accessed by a ColorProcessorSDK instance

    def __init__(self):
        # type: (type(None)) -> None
        if ColorProcessorSDK._is_sdk_open:
            self._disposed = True
            _logger.error("Error: ColorProcessorSDK is already in use. Please dispose of the current instance "
                          "before trying to create another")
        try:
            try:
                self._sdk = cdll.LoadLibrary(r"thorlabs_tsi_color_processing.dll")
            except OSError:
                self._sdk = cdll.LoadLibrary(r"thorlabs_tsi_color_processing.dll")
        except OSError as ose:
            _logger.error(str(ose) + "\n\nUnable to load library - are the thorlabs_tsi_color_processing DLLs "
                                     "discoverable from the application directory? Try placing them in the same "
                                     "directory as tl_color.py, or adding the directory with the DLLs to the "
                                     "PATH. Make sure to use x86 DLLs when using 32-bit python and x64 DLLs when "
                                     "using 64-bit.")
        try:
            err = self._sdk.tl_color_processing_module_initialize()
            if err != 0:
                _logger.error("tl_color_processing_initialize failed with error code " + str(err) + "\n")
            ColorProcessorSDK._is_sdk_open = True
            self._disposed = False

            """ set any C function argument types that need specification """

            self._sdk.tl_color_get_blue_input_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_blue_input_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_get_red_input_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_red_input_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_get_green_input_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_green_input_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_enable_input_LUTs.argtypes = [c_int, c_int, c_int]
            self._sdk.tl_color_get_blue_output_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_blue_output_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_get_red_output_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_red_output_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_get_green_output_LUT.argtpyes = [c_void_p]
            self._sdk.tl_color_get_green_output_LUT.restype = POINTER(c_int)
            self._sdk.tl_color_enable_output_LUTs.argtypes = [c_int, c_int, c_int]
            self._sdk.tl_color_append_matrix.argtypes = [c_void_p, POINTER(c_float)]
            self._sdk.tl_color_clear_matrix.argtypes = [c_void_p]
            self._sdk.tl_color_transform_48_to_48.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_ushort, c_ushort,
                                                              c_ushort, c_ushort, c_ushort, c_ushort, c_int, c_int,
                                                              c_int, POINTER(c_ushort), c_int, c_int]
            self._sdk.tl_color_transform_48_to_32.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_ushort, c_ushort,
                                                              c_ushort, c_ushort, c_ushort, c_ushort, c_int, c_int,
                                                              c_int, POINTER(c_ubyte), c_int, c_int]
            self._sdk.tl_color_transform_48_to_24.argtypes = [c_void_p, POINTER(c_ushort), c_int, c_ushort, c_ushort,
                                                              c_ushort, c_ushort, c_ushort, c_ushort, c_int, c_int,
                                                              c_int, POINTER(c_ubyte), c_int, c_int]
        except Exception as error:
            _logger.error("Error: sdk initialization failed\n")
            raise error

    def __del__(self):
        self.dispose()

    """ with statement functionality """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            _logger.debug("".join(format_exception(exc_type, exc_val, exc_tb)))
        self.dispose()
        return True if exc_type is None else False

    """ public methods """

    def dispose(self):
        # type: (type(None)) -> None
        try:
            if self._disposed:
                return
            err = self._sdk.tl_color_processing_module_terminate()
            if err != 0:
                raise TLColorError(ColorProcessorSDK._create_c_failure_message(
                    "tl_color_processing_module_terminate", err))
            ColorProcessorSDK._is_sdk_open = False
            self._disposed = True
        except Exception as error:
            _logger.error("Error: sdk destruction failed\n")
            raise error

    def create_color_processor(self, input_lut_size_bits, output_lut_size_bits):
        # type: (int, int) -> ColorProcessor
        return ColorProcessor(self._sdk, input_lut_size_bits, output_lut_size_bits, self._create_c_failure_message)

    """ error-handling methods """

    _tl_color_error = {
            'Error code is unknown': -1,
            'No error': 0,
            'Color module has not been initialized': 1,
            'The specified module instance handle is NULL': 2,
            'The specified input buffer pointer is NULL': 3,
            'The specified output buffer pointer is NULL': 4,
            'The same buffer was specified for input and output buffers': 5,
            'The specified color filter array phase is invalid': 6,
            'The specified color filter type is unknown': 7,
            'The specified pixel bit depth is invalid': 8,
            'The specified input color format is unknown': 9,
            'The specified output color format is unknown': 10,
            'The specified bit shift distance is invalid': 11,
            'The specified pixel clamp value is invalid': 12
        }

    @staticmethod
    def _create_c_failure_message(function_name, error_code):
        error_message = ColorProcessorSDK._tl_color_error.get(error_code, -1)
        failure_message = "{function_name}() returned non-zero error code: {error_code}; " \
                          "error message: {error_message}\n"\
            .format(function_name=function_name, error_code=error_code, error_message=error_message)
        return failure_message


""" ColorProcessor """


class ColorProcessor(object):

    """ Methods """

    def __init__(self, sdk, input_lut_size_bits, output_lut_size_bits, error_string_generator):
        try:
            self._sdk = sdk
            self._input_lut_size_bits = input_lut_size_bits
            self._output_lut_size_bits = output_lut_size_bits
            self._create_c_failure_message = error_string_generator

            self._color_processor = self._sdk.tl_color_create_color_processor(self._input_lut_size_bits,
                                                                              self._output_lut_size_bits)
            if self._color_processor == 0:
                raise TLColorError("tl_color_create_color_processor() returned a NULL color processor\n")

            self._disposed = False

        except Exception as error:
            _logger.error("ColorProcessor initialization failed. ")
            raise error

    def __del__(self):
        self.dispose()

    """ with statement functionality """
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            _logger.debug("".join(format_exception(exc_type, exc_val, exc_tb)))
        self.dispose()
        return True if exc_type is None else False

    """ Public Methods """

    def dispose(self):
        # type: (type(None)) -> None
        try:
            if self._disposed:
                return
            err = self._sdk.tl_color_destroy_color_processor(self._color_processor)
            if err != 0:
                raise TLColorError(self._create_c_failure_message("tl_color_destroy_color_processor", err))
            self._disposed = True
        except Exception as error:
            _logger.error("Could not cleanly dispose Color Processor instance. ")
            raise error

#  getters will return a copy of lut. setters will copy values from the given lut to the shared lut.

    def get_blue_input_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_blue_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_blue_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._input_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Could not get blue input lut. ")
            raise error

    def get_green_input_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_green_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_green_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._input_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Error: could not get green input lut\n")
            raise error

    def get_red_input_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_red_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_red_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._input_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Could not get red input lut. ")
            raise error

    def set_blue_input_lut(self, blue_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_blue_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_blue_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._input_lut_size_bits,))
            lut_shared[:] = blue_lut
        except Exception as error:
            _logger.error("Could not set blue input lut. ")
            raise error

    def set_green_input_lut(self, green_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_green_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_green_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._input_lut_size_bits,))
            lut_shared[:] = green_lut
        except Exception as error:
            _logger.error("Could not set green input lut. ")
            raise error

    def set_red_input_lut(self, red_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_red_input_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_red_input_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._input_lut_size_bits,))
            lut_shared[:] = red_lut
        except Exception as error:
            _logger.error("Could not set red input lut. ")
            raise error

    def enable_input_luts(self, blue_LUT_enable, green_LUT_enable, red_LUT_enable):
        # type: (int, int, int) -> None
        try:
            err = self._sdk.tl_color_enable_input_LUTs(self._color_processor,
                                                       c_int(blue_LUT_enable),
                                                       c_int(green_LUT_enable),
                                                       c_int(red_LUT_enable))
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_enable_input_LUTs", err))
        except Exception as error:
            _logger.error("Could not enable input luts. ")
            raise error

    def append_matrix(self, matrix):
        # type: (np.array) -> None
        try:
            arr = _3x3Matrix(*matrix)
            err = self._sdk.tl_color_append_matrix(self._color_processor, arr)
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_append_matrix", err))
        except Exception as error:
            _logger.error("Could not append matrix. ")
            raise error

    def clear_matrix(self):
        # type: (type(None)) -> None
        try:
            err = self._sdk.tl_color_clear_matrix(self._color_processor)
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_clear_matrix", err))
        except Exception as error:
            _logger.error("Could not clear matrix. ")
            raise error

    def get_blue_output_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_blue_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_blue_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._output_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Could not get blue output lut. ")
            raise error

    def get_green_output_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_green_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_green_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._output_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Could not get green output lut. ")
            raise error

    def get_red_output_lut(self):
        # type: (type(None)) -> np.array
        try:
            lut_pointer = self._sdk.tl_color_get_red_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_red_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2**self._output_lut_size_bits,))
            lut_copy = np.empty_like(lut_shared)
            lut_copy[:] = lut_shared
            return lut_copy
        except Exception as error:
            _logger.error("Could not get red output lut. ")
            raise error

    def set_blue_output_lut(self, blue_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_blue_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_blue_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._output_lut_size_bits,))
            lut_shared[:] = blue_lut
        except Exception as error:
            _logger.error("Could not set blue output lut. ")
            raise error

    def set_green_output_lut(self, green_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_green_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_green_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._output_lut_size_bits,))
            lut_shared[:] = green_lut
        except Exception as error:
            _logger.error("Could not set green output lut. ")
            raise error

    def set_red_output_lut(self, red_lut):
        # type: (np.array) -> None
        try:
            lut_pointer = self._sdk.tl_color_get_red_output_LUT(self._color_processor)
            if not lut_pointer:
                raise TLColorError("tl_color_get_red_output_lut() returned NULL\n")
            lut_shared = np.ctypeslib.as_array(lut_pointer, shape=(2 ** self._output_lut_size_bits,))
            lut_shared[:] = red_lut
        except Exception as error:
            _logger.error("Could not set red output lut. ")
            raise error

    def enable_output_luts(self, blue_LUT_enable, green_LUT_enable, red_LUT_enable):
        # type: (int, int, int) -> None
        try:
            err = self._sdk.tl_color_enable_output_LUTs(self._color_processor,
                                                        c_int(blue_LUT_enable),
                                                        c_int(green_LUT_enable),
                                                        c_int(red_LUT_enable))
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_enable_output_luts", err))
        except Exception as error:
            _logger.error("Could not enable output luts. ")
            raise error

    def transform_48_to_48(self, input_buffer, input_buffer_format, blue_output_min_value, blue_output_max_value,
                           green_output_min_value, green_output_max_value, red_output_min_value, red_output_max_value,
                           output_blue_shift_distance, output_green_shift_distance, output_red_shift_distance,
                           output_buffer_format, number_of_bgr_tuples
                           ):
        # type: (np.array, FORMAT, int, int, int, int, int, int, int, int, int, FORMAT, int) -> np.array
        try:
            input_buffer_format_value = c_int(input_buffer_format)
            output_buffer_format_value = c_int(output_buffer_format)

            input_buffer_as_ushort = input_buffer.view(np.ushort)
            input_pointer = input_buffer_as_ushort.ctypes.data_as(POINTER(c_ushort))

            # number of elements stays the same (RGB -> RGB) size per element stays the same (16-bit -> 16-bit)
            output_buffer = np.empty(shape=(input_buffer.size,), dtype=np.ushort)
            output_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))

            err = self._sdk.tl_color_transform_48_to_48(self._color_processor,
                                                        input_pointer, input_buffer_format_value,
                                                        blue_output_min_value, blue_output_max_value,
                                                        green_output_min_value, green_output_max_value,
                                                        red_output_min_value, red_output_max_value,
                                                        output_blue_shift_distance, output_green_shift_distance,
                                                        output_red_shift_distance, output_pointer,
                                                        output_buffer_format_value, number_of_bgr_tuples)
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_transform_48_to_48", err))
            return output_buffer
        except Exception as error:
            _logger.error("Could not transform image (48 to 48). ")
            raise error

    def transform_48_to_32(self, input_buffer, input_buffer_format, blue_output_min_value, blue_output_max_value,
                           green_output_min_value, green_output_max_value, red_output_min_value, red_output_max_value,
                           output_blue_shift_distance, output_green_shift_distance, output_red_shift_distance,
                           output_buffer_format, number_of_bgr_tuples
                           ):
        # type: (np.array, FORMAT, int, int, int, int, int, int, int, int, int, FORMAT, int) -> np.array
        try:
            input_buffer_format_value = c_int(input_buffer_format)
            output_buffer_format_value = c_int(output_buffer_format)

            input_buffer_as_ushort = input_buffer.view(np.ushort)
            input_buffer_pointer = input_buffer_as_ushort.ctypes.data_as(POINTER(c_ushort))

            # number of elements goes up (RGB -> RGBA) but size per element goes down (16-bit -> 8-bit)
            output_buffer = np.empty(shape=(int(input_buffer.size + (input_buffer.size / 4)),), dtype=np.ubyte)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ubyte))

            err = self._sdk.tl_color_transform_48_to_32(self._color_processor,
                                                        input_buffer_pointer, input_buffer_format_value,
                                                        blue_output_min_value, blue_output_max_value,
                                                        green_output_min_value, green_output_max_value,
                                                        red_output_min_value, red_output_max_value,
                                                        output_red_shift_distance, output_green_shift_distance,
                                                        output_blue_shift_distance, output_buffer_pointer,
                                                        output_buffer_format_value, number_of_bgr_tuples)
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_transform_48_to_32", err))
            return output_buffer
        except Exception as error:
            _logger.error("Could not transform image (48 to 32). ")
            raise error

    def transform_48_to_24(self, input_buffer, input_buffer_format, blue_output_min_value, blue_output_max_value,
                           green_output_min_value, green_output_max_value, red_output_min_value, red_output_max_value,
                           output_blue_shift_distance, output_green_shift_distance, output_red_shift_distance,
                           output_buffer_format, number_of_bgr_tuples
                           ):
        # type: (np.array, FORMAT, int, int, int, int, int, int, int, int, int, FORMAT, int) -> np.array
        try:
            input_buffer_format_value = c_int(input_buffer_format)
            output_buffer_format_value = c_int(output_buffer_format)

            input_buffer_as_ushort = input_buffer.view(np.ushort)
            input_buffer_pointer = input_buffer_as_ushort.ctypes.data_as(POINTER(c_ushort))

            # number of elements stays the same (RGB -> RGB), size per element goes down (16-bit -> 8-bit)
            output_buffer = np.empty(shape=(input_buffer.size,), dtype=np.ubyte)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ubyte))

            err = self._sdk.tl_color_transform_48_to_24(self._color_processor,
                                                        input_buffer_pointer, input_buffer_format_value,
                                                        blue_output_min_value, blue_output_max_value,
                                                        green_output_min_value, green_output_max_value,
                                                        red_output_min_value, red_output_max_value,
                                                        output_red_shift_distance, output_green_shift_distance,
                                                        output_blue_shift_distance, output_buffer_pointer,
                                                        output_buffer_format_value, number_of_bgr_tuples)
            if err:
                raise TLColorError(self._create_c_failure_message("tl_color_transform_48_to_24", err))
            return output_buffer
        except Exception as error:
            _logger.error("Could not transform image (48 to 24). ")
            raise error


""" Demosaicker """


class Demosaicker(object):

    _is_sdk_open = False  # is SDK DLL currently being accessed by a Demosaicker instance

    def __init__(self):
        # type: (type(None)) -> None
        self._disposed = True
        if Demosaicker._is_sdk_open:
            _logger.error("Error: Demosaicker is already in use. Please dispose of the current instance before "
                          "trying to create another")
        try:
            self._sdk = cdll.LoadLibrary(r"thorlabs_tsi_demosaic.dll")
        except OSError as ose:
            _logger.error(str(ose) + "\n\nUnable to load library - are the thorlabs_tsi_demosaic DLLs "
                                     "discoverable from the application directory? Try placing them in the same "
                                     "directory as tl_color.py, or adding the directory with the DLLs to the "
                                     "PATH. Make sure to use x86 DLLs when using 32-bit python and x64 DLLs when "
                                     "using 64-bit.")
        try:
            err = self._sdk.tl_demosaic_module_initialize()
            if err != 0:
                raise TLColorError("tl_demosaic_module_initialize failed with error code " + str(err) + "\n")
            Demosaicker._is_sdk_open = True
            self._disposed = False

            """ set C function argument types """

            self._sdk.tl_demosaic_transform_16_to_48.argtypes = [c_int, c_int, c_int, c_int, c_int, c_int,
                                                                 c_int, c_int, POINTER(c_ushort), POINTER(c_ushort)]

        except Exception as error:
            _logger.error("Error: sdk initialization failed\n")
            raise error

    def __del__(self):
        self.dispose()

    """ with statement functionality """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.dispose()
        return isinstance(exc_val, TLColorError)

    """ public methods """

    def dispose(self):
        # type: (type(None)) -> None
        try:
            if self._disposed:
                return
            err = self._sdk.tl_demosaic_module_terminate()
            if err != 0:
                raise TLColorError("tl_demosaic_module_terminate failed with error code " + str(err) + "\n")
            Demosaicker._is_sdk_open = False
            self._disposed = True
        except Exception as error:
            _logger.error("Error: sdk destruction failed\n")
            raise error

    def transform_16_to_48(self, width, height, x_origin, y_origin, color_phase, output_color_format,
                           color_filter_type, bit_depth, input_buffer):
        # type: (int, int, int, int, FILTER_ARRAY_PHASE, FORMAT, FILTER_TYPE, int, np.array) -> np.array

        try:
            input_buffer_as_ushort = input_buffer.view(np.ushort)
            input_buffer_pointer = input_buffer_as_ushort.ctypes.data_as(POINTER(c_ushort))

            color_phase_value = c_int(color_phase)
            output_color_format_value = c_int(output_color_format)
            color_filter_type_value = c_int(color_filter_type)

            # number of elements goes up (Mono -> RGB), size per element stays the same (16-bit -> 16-bit)
            output_buffer = np.empty(shape=(input_buffer.size * 3,), dtype=np.ushort)
            output_buffer_pointer = output_buffer.ctypes.data_as(POINTER(c_ushort))

            err = self._sdk.tl_demosaic_transform_16_to_48(width, height, x_origin, y_origin, color_phase_value,
                                                           output_color_format_value, color_filter_type_value,
                                                           bit_depth, input_buffer_pointer, output_buffer_pointer)
            if err:
                raise TLColorError("tl_color_transform_48_to_24 returned error code " + str(err) + "\n")
            return output_buffer
        except Exception as error:
            _logger.error("Error: could not demosaic the image (16 to 48)\n")
            raise error


""" Error handling """


class TLColorError(Exception):
    def __init__(self, message):
        _logger.debug(message)
        super(TLColorError, self).__init__(message)
