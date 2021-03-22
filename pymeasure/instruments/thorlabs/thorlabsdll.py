#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import os
import sys
import logging
from ctypes import (cdll, create_string_buffer, c_uint16, c_uint32,
                    c_int16, c_int32, c_char_p, c_wchar_p, c_bool, c_double,
                    byref)
from pyvisa.errors import completion_and_error_messages, VisaIOError
from pyvisa.constants import _to_int
from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ThorlabsDLLAdapter():
    r"""Adapter to interface the DLL based drivers from Thorlabs.

    Usually these drivers are installed to the systems
    `VXIPNPPATH` and `VXIPNPPATH64`.

    On Windows typical locations are:

        - ``C:\Program Files\IVI Foundation\VISA\Win64\Bin\``
        - ``C:\Program Files (x86)\IVI Foundation\VISA\WinNT\Bin\``

    Depending on the executing python architecture the 32bit or
    64bit version is required. The default behaviour of this adapter
    is to look in the according `VXIPNPPATH`. But the path can be
    overwritten by passing the `dll_path` argument.

    An instance of this adapter provides the interface to the DLL
    and methods to find connected devices and retrieve information
    about them.

    :param dll_name: name of driver
    :type dll_name: str
    :param dll_path: path to driver DLL, defaults to None
    :type dll_path: str, optional
    """
    def __init__(self, dll_name, dll_path=None):
        if dll_path is None:
            if sys.maxsize > 2**32:
                # 64bit python
                dll_path = os.environ['VXIPNPPATH64']
                dll_path = os.path.join(
                    dll_path, 'Win64', 'Bin', f'{dll_name}_64.dll')
            else:
                # 32bit python
                dll_path = os.environ['VXIPNPPATH']
                dll_path = os.path.join(
                    dll_path, 'WinNT', 'Bin',  f'{dll_name}_32.dll')
        try:
            self._dll = cdll.LoadLibrary(dll_path)
        except Exception as err:
            log.warning(
                "Error loading Thorlabs driver DLL from {}: {}"
                .format(dll_path, err))
            raise
        self._dll_name = dll_name

    def dll(self, command, *args, instrument_handle=c_uint32(0)):
        """Method to interface the driver as provided by ``cdll.LoadLibrary``.
        Status returned by instrument is checked.

        :param command: command to be issued
        :type command: str
        :param instrument_handle: if connection exists already,
                                  defaults to ``c_uint32(0)``
        :type instrument_handle: c_uint32, optional
        """
        command = '{}_{}'.format(self._dll_name, command)
        status = getattr(self._dll, command)(*args)
        if (status != 0):
            self.process_status(status, instrument_handle)

    @property
    def device_count(self):
        """Get the number of connected devices available that can
        be controlled with this driver.
        """
        instrument_handle = c_uint32(0)
        deviceCount = c_uint32(0)
        self.dll(
            'findRsrc', byref(instrument_handle), byref(deviceCount))
        return deviceCount.value

    def get_resource_name(self, index):
        """Get resource name of device with given index.
        Needed to initialize instrument instance.

        :param index: index of connected device (starting at 0)
        :type index: int
        :return: resource name
        :rtype: str
        """
        instrument_handle = c_uint32(0)
        resourceName = create_string_buffer(256)
        self.dll(
            'getRsrcName', byref(instrument_handle),
            c_uint32(index), byref(resourceName))
        return resourceName.value.decode('ascii')

    def get_resource_info(self, index):
        """Read basic information of device with given index.

        :param index: index of connected device (starting at 0)
        :type index: int
        :return: device name, serial number, manufacturer date
        :rtype: tuple of str
        """
        instrument_handle = c_uint32(0)
        deviceName = create_string_buffer(256)
        serialNumber = create_string_buffer(256)
        manufacturerName = create_string_buffer(256)
        resourceInUse = c_bool(0)
        self.dll(
            'getRsrcInfo', byref(instrument_handle), c_uint32(index),
            byref(deviceName), byref(serialNumber), byref(manufacturerName),
            byref(resourceInUse))
        ret = (deviceName, serialNumber, manufacturerName)
        ret = tuple([lambda x: x.value.decode('ascii').strip() for x in ret])
        ret = ret + (resourceInUse.value,)
        return ret

    def _update_devices(self):
        """Get number of connected devices and read
        name for every device. Store as attributes.
        """
        index_dict = {}
        name_dict = {}
        for index in range(self.device_count):
            name = self.get_resource_name(index)
            index_dict[index] = name
            name_dict[name] = index
        self._index_dict = index_dict
        self._name_dict = name_dict

    @property
    def devices_by_index(self):
        """Get dict of devices indices and their names.

        :return: dict of index:name
        :rtype: dict
        """
        self._update_devices()
        return self._index_dict

    @property
    def devices_by_name(self):
        """Get dict of device names and their indices

        :return: dict of name:index
        :rtype: dict
        """
        self._update_devices()
        return self._name_dict

    def process_status(self, status, instrument_handle=c_uint32(0)):
        """Interpret status code returned by the instrument.
        Possible errors of the instrument are poorly documented so far.

        :param status: status code
        :type status: int
        :param instrument_handle: if connection exists already,
                                  defaults to ``c_uint32(0)``
        :type instrument_handle: c_uint32, optional
        """
        error = ("ERROR", "Unknown error code {}".format(status))
        # check instrument specific errors
        try:
            error = ERRORS[status]
        except KeyError:
            # check general VISA error codes
            try:
                error = completion_and_error_messages[status]
            except KeyError:
                pass
        if "SUCCESS" in error[0]:
            # operation was possible, only information passed
            log.info("{}: {}".format(*error))
        elif "WARN" in error[0]:
            # warning, but no exception
            log.warning("{}: {}".format(*error))
        elif status in completion_and_error_messages.keys() and status < 0:
            # if appropriate raise VISA error
            raise VisaIOError(status)
        else:
            # in other cases raise general exception
            raise Exception("{0} ({2}): {1}".format(*error, status))


ERRORS = {
    # use _to_int() from pyvisa, since VISA specification defines
    # VISA codes with values <0 as positive. using _to_int() the
    # VISA codes are compatible with the values returned by ctypes

    # Instrument Driver Errors and Warnings
    0: ("VI_SUCCESS", "Operation completed successfully."),
    _to_int(0x3FFF0085): (
        "VI_WARN_UNKNOWN_STATUS",
        "The status code passed to the operation could not be interpreted."),
    # up to here also included in VISA errors
    # these error codes are not in deafult VISA library
    _to_int(0x3FFC0901): ("VI_INSTR_WARN_OVERFLOW", "Value overflow."),
    _to_int(0x3FFC0902): ("VI_INSTR_WARN_UNDERRUN", "Value underrun."),
    _to_int(0x3FFC0903): ("VI_INSTR_WARN_NAN", "Value is NaN."),
    _to_int(0xBFFC0001): ("", "Parameter 1 out of range."),
    _to_int(0xBFFC0002): ("", "Parameter 2 out of range."),
    _to_int(0xBFFC0003): ("", "Parameter 3 out of range."),
    _to_int(0xBFFC0004): ("", "Parameter 4 out of range."),
    _to_int(0xBFFC0005): ("", "Parameter 5 out of range."),
    _to_int(0xBFFC0006): ("", "Parameter 6 out of range."),
    _to_int(0xBFFC0007): ("", "Parameter 7 out of range."),
    _to_int(0xBFFC0008): ("", "Parameter 8 out of range."),
    _to_int(0xBFFC0012): ("", "Error interpreting instrument response."),

    # Instrument Errors
    # Range: 0xBFFC0700 .. 0xBFFC0CFF.
    # Calculation: Device error code + 0xBFFC0900.
    # Please see your device documentation for details.
    _to_int(0xBFFC0900): ("INSTR_RUNTIME_ERROR", ""),
    _to_int(0xBFFC08FF): ("INSTR_REM_INTER_ERROR", ""),
    _to_int(0xBFFC08FE): ("INSTR_AUTHENTICATION_ERROR", ""),
    _to_int(0xBFFC08FD): ("INSTR_PARAM_ERROR", ""),
    _to_int(0xBFFC08FC): ("INSTR_HW_ERROR", ""),
    _to_int(0xBFFC08FB): ("INSTR_PARAM_CHNG_ERROR", ""),
    _to_int(0xBFFC08FA): ("INSTR_INTERNAL_TX_ERR", ""),
    _to_int(0xBFFC08F9): ("INSTR_INTERNAL_RX_ERR", ""),
    _to_int(0xBFFC08F8): ("INSTR_INVAL_MODE_ERR", ""),
    _to_int(0xBFFC08F7): ("INSTR_SERVICE_ERR", ""),
    _to_int(0xBFFC08F6): ("INSTR_NOT_YET_IMPL_ERR", ""),
    _to_int(0xBFFC08F5): ("INSTR_LED_ADAPT_IN_PROG", ""),
    _to_int(0xBFFC08F4): ("INSTR_LED_ADAPT_STP_REQ", ""),

    # user defined driver error codes from TL6WL.h
    _to_int(0xBFFC0500): ("VI_DRIVER_USB_ERROR", ""),
    _to_int(0xBFFC04FF): ("VI_DRIVER_FRAME_SERV_ERROR", ""),
    _to_int(0xBFFC04FE): ("VI_DRIVER_DEV_INTER_BROKEN", ""),

    }


class ThorlabsDLLInstrument():
    """Base class for instruments connected with the
    :class:`~pymeasure.instruments.thorlabs.ThorlabsDLLAdapter`.

    :param adapter: dll driver instance
    :type adapter: :class:`~pymeasure.instruments.thorlabs.ThorlabsDLLAdapter`
    :param resourceName: resource name of the instrument
    :type resourceName: str
    :param name: name of the instrument for logging etc.
    :type name: str
    :param id_query: perform ID query during initialization,
                     defaults to True
    :type id_query: bool, optional
    :param reset: reset instrument during initialization,
                  defaults to False
    :type reset: bool, optional
    """
    def __init__(self, adapter, resourceName, name,
                 id_query=True, reset=False):
        self.adapter = adapter
        self.resourceName = resourceName
        self.index = self.adapter.devices_by_name[self.resourceName]
        self.name = name  # for logging etc.
        self.instrument_handle = c_uint32(0)
        self.adapter.dll(
            'init', c_char_p(self.resourceName.encode('ascii')),
            c_bool(id_query), c_bool(reset), byref(self.instrument_handle))

        # # add properties for individual LEDs via e.g. .LED365 attribute
        # names = self.LED_names
        # for index in range(6):
        #     setattr(
        #         self, names[index].rstrip(' nm').replace(' ', ''),
        #         # results e.g. in LED365
        #         ChrolisLED(self, index + 1, names[index]))

        # # add Timing Unit
        # self.TU = ChrolisTU(self)

    def __del__(self):
        # make sure connection is released upon deletion
        self.dll('close', self.instrument_handle)

    def dll(self, command, *args):
        """Method to interface the driver as provided by
        :class:`cdll.LoadLibrary`.
        Status returned by instrument is checked.

        :param command: command to be issued
        :type command: str
        """
        self.adapter.dll(
            command, self.instrument_handle, *args,
            instrument_handle=self.instrument_handle)

    def check_errors(self):
        """Manually query the error queue."""
        error_number = c_int32(0)
        error_message = create_string_buffer(512)
        # TL6WL: at least 256
        # TLPM: at least 512
        self.adapter.dll(
            'errorQuery', byref(error_number), byref(error_message),
            instrument_handle=self.instrument_handle)
        return (error_number.value, error_message.value)

    def reset(self):
        """Reset instrument to known state."""
        self.dll('reset')

    @property
    def revision(self):
        """Revision numbers of driver and firmware."""
        instr_drv = create_string_buffer(256)
        FW = create_string_buffer(256)
        self.dll(
            'revisionQuery', byref(instr_drv), byref(FW))
        (instr_drv, FW) = tuple(
            x.value.decode('ascii').strip()
            for x in (instr_drv, FW))
        return {
            "Instrument Driver Revision": instr_drv,
            "Firmware Revision": FW}
