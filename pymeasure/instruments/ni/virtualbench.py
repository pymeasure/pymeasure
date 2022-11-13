#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
# pyvirtualbench library: Copyright (c) 2015 Charles Armstrap <charles@armstrap.org>
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
# Requires 'pyvirtualbench' package:
# https://github.com/armstrap/armstrap-pyvirtualbench

import logging
import re
# ctypes only required for VirtualBench_Direct class
from ctypes import (c_int, cdll, byref)
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd

from pymeasure.instruments.validators import (
    strict_discrete_set, strict_discrete_range,
    truncated_discrete_set, strict_range
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    # Requires 'pyvirtualbench' package:
    # https://github.com/armstrap/armstrap-pyvirtualbench
    import pyvirtualbench as pyvb
except ModuleNotFoundError as err:
    log.info('Failed loading the pyvirtualbench package. '
             + 'Check the NI VirtualBench documentation on how to '
             + 'install this external dependency. '
             + f'ImportError: {err}')
    raise


class VirtualBench_Direct(pyvb.PyVirtualBench):
    """ Represents National Instruments Virtual Bench main frame.
    This class provides direct access to the armstrap/pyvirtualbench
    Python wrapper.
    """

    def __init__(self, device_name='', name='VirtualBench'):
        ''' Initialize the VirtualBench library.  This must be called at least
            once for the application. The 'version' parameter must be set to
            the NIVB_LIBRARY_VERSION constant.
        '''
        self.device_name = device_name
        self.name = name
        self.nilcicapi = cdll.LoadLibrary("nilcicapi")
        self.library_handle = c_int(0)
        status = self.nilcicapi.niVB_Initialize(pyvb.NIVB_LIBRARY_VERSION,
                                                byref(self.library_handle))
        if (status != pyvb.Status.SUCCESS):
            raise pyvb.PyVirtualBenchException(status, self.nilcicapi,
                                               self.library_handle)
        log.info("Initializing %s." % self.name)

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.release()


class VirtualBench():
    """ Represents National Instruments Virtual Bench main frame.

    Subclasses implement the functionalities of the different modules:

        - Mixed-Signal-Oscilloscope (MSO)
        - Digital Input Output (DIO)
        - Function Generator (FGEN)
        - Power Supply (PS)
        - Serial Peripheral Interface (SPI) -> not implemented
          for pymeasure yet
        - Inter Integrated Circuit (I2C) -> not implemented for pymeasure yet

    For every module exist methods to save/load the configuration to file.
    These methods are not wrapped so far, checkout the pyvirtualbench file.

    All calibration methods and classes are not wrapped so far, since these
    are not required on a very regular basis. Also the connections via network
    are not yet implemented.
    Check the pyvirtualbench file, if you need the functionality.

    :param str device_name: Full unique device name
    :param str name: Name for display in pymeasure
    """

    def __init__(self, device_name='', name='VirtualBench'):
        ''' Initialize the VirtualBench library.  This must be called at least
        once for the application. The 'version' parameter must be set to the
        NIVB_LIBRARY_VERSION constant.
        '''
        self.device_name = device_name
        self.name = name
        self.vb = pyvb.PyVirtualBench(self.device_name)
        log.info("Initializing %s." % self.name)

    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        if self.vb.library_handle is not None:
            self.vb.release()

    def shutdown(self):
        ''' Finalize the VirtualBench library.
        '''
        log.info("Shutting down %s" % self.name)
        self.vb.release()
        self.isShutdown = True

    def get_library_version(self):
        ''' Return the version of the VirtualBench runtime library
        '''
        return self.vb.get_library_version()

    def convert_timestamp_to_values(self, timestamp):
        """ Converts a timestamp to seconds and fractional seconds

        :param timestamp: VirtualBench timestamp
        :type timestamp: pyvb.Timestamp
        :return: (seconds_since_1970, fractional seconds)
        :rtype: (int, float)
        """
        if not isinstance(timestamp, pyvb.Timestamp):
            raise ValueError("{} is not a VirtualBench Timestamp object"
                             .format(timestamp))
        return self.vb.convert_timestamp_to_values(timestamp)

    def convert_values_to_timestamp(self, seconds_since_1970,
                                    fractional_seconds):
        """ Converts seconds and fractional seconds to a timestamp

        :param seconds_since_1970: Date/Time in seconds since 1970
        :type seconds_since_1970: int
        :param fractional_seconds: Fractional seconds
        :type fractional_seconds: float
        :return: VirtualBench timestamp
        :rtype: pyvb.Timestamp
        """
        return self.vb.convert_values_to_timestamp(seconds_since_1970,
                                                   fractional_seconds)

    def convert_values_to_datetime(self, timestamp):
        """ Converts timestamp to datetime object

        :param timestamp: VirtualBench timestamp
        :type timestamp: pyvb.Timestamp
        :return: Timestamp as DateTime object
        :rtype: DateTime
        """
        (seconds_since_1970,
         fractional_seconds) = self.convert_timestamp_to_values(timestamp)
        fractional_seconds = timedelta(seconds=fractional_seconds)
        return (datetime.fromtimestamp(seconds_since_1970, timezone.utc) +
                fractional_seconds)

    def collapse_channel_string(self, names_in):
        """ Collapses a channel string into a comma and colon-delimited
        equivalent. Last element is the number of channels.

        :param names_in: Channel string
        :type names_in: str
        :return: Channel string with colon notation where possible,
                 number of channels
        :rtype: (str, int)
        """
        if not isinstance(names_in, str):
            raise ValueError(f"{names_in} is not a string")
        return self.vb.collapse_channel_string(names_in)

    def expand_channel_string(self, names_in):
        """ Expands a channel string into a comma-delimited (no colon)
        equivalent. Last element is the number of channels.
        ``'dig/0:2'`` -> ``('dig/0, dig/1, dig/2',3)``

        :param names_in: Channel string
        :type names_in: str
        :return: Channel string with all channels separated by comma,
                 number of channels
        :rtype: (str, int)
        """
        return self.vb.expand_channel_string(names_in)

    def get_calibration_information(self):
        """ Returns calibration information for the specified device,
        including the last calibration date and calibration interval.

        :return: Calibration date, recommended calibration interval in months,
                 calibration interval in months
        :rtype: (pyvb.Timestamp, int, int)
        """
        return self.vb.get_calibration_information(self.device_name)

    def acquire_digital_input_output(self, lines, reset=False):
        """ Establishes communication with the DIO module. This method should
        be called once per session.

        :param lines: Lines to acquire, reading is possible on all lines
        :type lines: str
        :param reset: Reset DIO module, defaults to False
        :type reset: bool, optional
        """
        reset = strict_discrete_set(reset, [True, False])
        self.dio = self.DigitalInputOutput(self.vb, lines, reset,
                                           vb_name=self.name)

    def acquire_power_supply(self, reset=False):
        """ Establishes communication with the PS module. This method should be
        called once per session.

        :param reset: Reset the PS module, defaults to False
        :type reset: bool, optional
        """
        reset = strict_discrete_set(reset, [True, False])
        self.ps = self.PowerSupply(self.vb, reset, vb_name=self.name)

    def acquire_function_generator(self, reset=False):
        """ Establishes communication with the FGEN module. This method should
        be called once per session.

        :param reset: Reset the FGEN module, defaults to False
        :type reset: bool, optional
        """
        reset = strict_discrete_set(reset, [True, False])
        self.fgen = self.FunctionGenerator(self.vb, reset, vb_name=self.name)

    def acquire_mixed_signal_oscilloscope(self, reset=False):
        """ Establishes communication with the MSO module. This method should
        be called once per session.

        :param reset: Reset the MSO module, defaults to False
        :type reset: bool, optional
        """
        reset = strict_discrete_set(reset, [True, False])
        self.mso = self.MixedSignalOscilloscope(self.vb, reset,
                                                vb_name=self.name)

    def acquire_digital_multimeter(self, reset=False):
        """ Establishes communication with the DMM module. This method should
        be called once per session.

        :param reset: Reset the DMM module, defaults to False
        :type reset: bool, optional
        """
        reset = strict_discrete_set(reset, [True, False])
        self.dmm = self.DigitalMultimeter(self.vb, reset=reset,
                                          vb_name=self.name)

    class VirtualBenchInstrument():
        def __init__(self, acquire_instr, reset,
                     instr_identifier, vb_name=''):
            """Initialize instrument of VirtualBench device.
            Sets class variables and provides basic methods
            common to all VB instruments.

            :param acquire_instr: Method to acquire the instrument
            :type acquire_instr: method
            :param reset: Resets the instrument
            :type reset: bool
            :param instr_identifier: Shorthand identifier, e.g. mso or fgen
            :type instr_identifier: str
            :param vb_name: Name of VB device for logging, defaults to ''
            :type vb_name: str, optional
            """
            # Parameters & Handle of VirtualBench Instance
            self._vb_handle = acquire_instr.__self__
            self._device_name = self._vb_handle.device_name
            self.name = (vb_name + " " + instr_identifier.upper()).strip()
            log.info("Initializing %s." % self.name)
            self._instrument_handle = acquire_instr(self._device_name, reset)
            self.isShutdown = False

        def __del__(self):
            """ Ensures the connection is closed upon deletion
            """
            if self.isShutdown is not True:
                self._instrument_handle.release()

        def shutdown(self):
            ''' Removes the session and deallocates any resources acquired
            during the session. If output is enabled on any channels, they
            remain in their current state.
            '''
            log.info("Shutting down %s" % self.name)
            self._instrument_handle.release()
            self.isShutdown = True

    class DigitalInputOutput(VirtualBenchInstrument):
        """ Represents Digital Input Output (DIO) Module of Virtual Bench
        device. Allows to read/write digital channels and/or set channels
        to export the start signal of FGEN module or trigger of MSO module.
        """

        def __init__(self, virtualbench, lines, reset, vb_name=''):
            """ Acquire DIO module

            :param virtualbench: VirtualBench Instance
            :type virtualbench: VirtualBench
            :param lines: Lines to acquire
            :type lines: str
            :param reset: Rest DIO module
            :type reset: bool
            """
            # Parameters & Handle of VirtualBench Instance
            self._device_name = virtualbench.device_name
            self._vb_handle = virtualbench
            self.name = vb_name + " DIO"
            # Validate lines argument
            # store line names & numbers for future reference
            (self._line_names, self._line_numbers) = self.validate_lines(
                lines, return_single_lines=True, validate_init=False)
            # Create DIO Instance
            log.info("Initializing %s." % self.name)
            self.dio = self._vb_handle.acquire_digital_input_output(
                self._line_names, reset)
            # for methods provided by super class
            self._instrument_handle = self.dio
            self.isShutdown = False

        def validate_lines(self, lines, return_single_lines=False,
                           validate_init=False):
            """Validate lines string
            Allowed patterns (case sensitive):

                - ``'VBxxxx-xxxxxxx/dig/0:7'``
                - ``'VBxxxx-xxxxxxx/dig/0'``
                - ``'dig/0'``
                - ``'VBxxxx-xxxxxxx/trig'``
                - ``'trig'``

                Allowed Line Numbers: 0-7 or trig

            :param lines: Line string to test
            :type lines: str
            :param return_single_lines: Return list of line numbers as well,
                                        defaults to False
            :type return_single_lines: bool, optional
            :param validate_init: Check if lines are initialized (in
                                  :code:`self._line_numbers`),
                                  defaults to False
            :type validate_init: bool, optional
            :return: Line string, optional list of single line numbers
            :rtype: str, optional (str, list)
            """

            def error(lines=lines):
                raise ValueError(
                    f"Line specification {lines} is not valid!")

            lines = self._vb_handle.expand_channel_string(lines)[0]
            lines = lines.split(', ')
            return_lines = []
            single_lines = []
            for line in lines:
                if line == 'trig':
                    device = self._device_name
                # otherwise (device_name/)dig/line or device_name/trig
                else:
                    # split off line number by last '/'
                    try:
                        (device, line) = re.match(
                            r'(.*)(?:/)(.+)',
                            line).groups()
                    except IndexError:
                        error()
                if (line == 'trig') and (device == self._device_name):
                    single_lines.append('trig')
                    return_lines.append(self._device_name + '/' + line)
                elif int(line) in range(0, 8):
                    line = int(line)
                    single_lines.append(line)
                    # validate device name: either 'dig' or 'device_name/dig'
                    if device == 'dig':
                        pass
                    else:
                        try:
                            device = re.match(
                                r'(VB[0-9]{4}-[0-9a-zA-Z]{7})(?:/dig)',
                                device).groups()[0]
                        except (IndexError, KeyError):
                            error()
                        # device_name has to match
                        if not device == self._device_name:
                            error()
                    # constructing line references for output
                    return_lines.append((self._device_name + '/dig/%d') % line)
                else:
                    error()
                # check if lines are initialized
                if validate_init is True:
                    if line not in self._line_numbers:
                        raise ValueError(
                            f"Digital Line {line} is not initialized")

            # create comma separated channel string
            return_lines = ', '.join(return_lines)
            # collapse string if possible
            return_lines = self._vb_handle.collapse_channel_string(
                return_lines)[0]  # drop number of lines
            if return_single_lines is True:
                return return_lines, single_lines
            else:
                return return_lines

        def tristate_lines(self, lines):
            ''' Sets all specified lines to a high-impedance state. (Default)
            '''
            lines = self.validate_lines(lines, validate_init=True)
            self.dio.tristate_lines(lines)

        def export_signal(self, line, digitalSignalSource):
            """ Exports a signal to the specified line.

            :param line: Line string
            :type line: str
            :param digitalSignalSource: ``0`` for FGEN start or ``1``
                                        for MSO trigger
            :type digitalSignalSource: int
            """
            line = self.validate_lines(line, validate_init=True)
            digitalSignalSource_values = {"FGEN START": 0, "MSO TRIGGER": 1}
            digitalSignalSource = strict_discrete_set(
                digitalSignalSource.upper(), digitalSignalSource_values)
            digitalSignalSource = digitalSignalSource_values[
                digitalSignalSource.upper()]
            self.dio.export_signal(line, digitalSignalSource)

        def query_line_configuration(self):
            ''' Indicates the current line configurations. Tristate Lines,
            Static Lines, and Export Lines contain comma-separated
            range_data and/or colon-delimited lists of all acquired lines
            '''
            return self.dio.query_line_configuration()

        def query_export_signal(self, line):
            """ Indicates the signal being exported on the specified line.

            :param line: Line string
            :type line: str
            :return: Exported signal (FGEN start or MSO trigger)
            :rtype: enum
            """
            line = self.validate_lines(line, validate_init=True)
            return self.dio.query_export_signal(line)

        def write(self, lines, data):
            """ Writes data to the specified lines.

            :param lines: Line string
            :type lines: str
            :param data: List of data, (``True`` = High, ``False`` = Low)
            :type data: list or tuple
            """
            lines = self.validate_lines(lines, validate_init=True)
            try:
                for value in data:
                    strict_discrete_set(value, [True, False])
            except Exception:
                raise ValueError(
                    f"Data {data} is not iterable (list or tuple).")
            log.debug(f"{self.name}: {lines} output {data}.")
            self.dio.write(lines, data)

        def read(self, lines):
            """ Reads the current state of the specified lines.

            :param lines: Line string,  requires full name specification e.g.
                          ``'VB8012-xxxxxxx/dig/0:7'`` since instrument_handle
                          is not required (only library_handle)
            :type lines: str
            :return: List of line states (HIGH/LOW)
            :rtype: list
            """
            lines = self.validate_lines(lines, validate_init=False)
            # init not necessary for readout
            return self.dio.read(lines)

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and
            resets the device and driver software to a known state.
            '''
            self.dio.reset_instrument()

    class DigitalMultimeter(VirtualBenchInstrument):
        """ Represents Digital Multimeter (DMM) Module of Virtual Bench
        device. Allows to measure either DC/AC voltage or current,
        Resistance or Diodes.
        """

        def __init__(self, virtualbench, reset, vb_name=''):
            """ Acquire DMM module

            :param virtualbench: Instance of the VirtualBench class
            :type virtualbench: VirtualBench
            :param reset: Resets the instrument
            :type reset: bool
            """
            super().__init__(
                virtualbench.acquire_digital_multimeter,
                reset, 'dmm', vb_name)
            self.dmm = self._instrument_handle

        @staticmethod
        def validate_range(dmm_function, range):
            """ Checks if ``range`` is valid for the chosen ``dmm_function``

            :param int dmm_function: DMM Function
            :param range: Range value, e.g. maximum value to measure
            :type range: int or float
            :return: Range value to pass to instrument
            :rtype: int
            """
            ref_ranges = {
                0: [0.1, 1, 10, 100, 300],
                1: [0.1, 1, 10, 100, 265],
                2: [0.01, 0.1, 1, 10],
                3: [0.005, 0.05, 0.5, 5],
                4: [100, 1000, 10000, 100000, 1000000,
                    10000000, 100000000],
            }
            range = truncated_discrete_set(range, ref_ranges[dmm_function])
            return range

        def validate_dmm_function(self, dmm_function):
            """ Check if DMM function *dmm_function* exists

            :param dmm_function: DMM function index or name:

                - ``'DC_VOLTS'``, ``'AC_VOLTS'``
                - ``'DC_CURRENT'``, ``'AC_CURRENT'``
                - ``'RESISTANCE'``
                - ``'DIODE'``

            :type dmm_function: int or str
            :return: DMM function index to pass to the instrument
            :rtype: int
            """
            try:
                pyvb.DmmFunction(dmm_function)
            except Exception:
                try:
                    dmm_function = pyvb.DmmFunction[dmm_function.upper()]
                except Exception:
                    raise ValueError(
                        "DMM Function may be 0-5, 'DC_VOLTS'," +
                        " 'AC_VOLTS', 'DC_CURRENT', 'AC_CURRENT'," +
                        " 'RESISTANCE' or 'DIODE'")
            return dmm_function

        def validate_auto_range_terminal(self, auto_range_terminal):
            """ Check value for choosing the auto range terminal for
            DC current measurement

            :param auto_range_terminal: Terminal to perform
                                        auto ranging (``'LOW'``
                                        or ``'HIGH'``)
            :type auto_range_terminal: int or str
            :return: Auto range terminal to pass to the instrument
            :rtype: int
            """
            try:
                pyvb.DmmCurrentTerminal(auto_range_terminal)
            except Exception:
                try:
                    auto_range_terminal = pyvb.DmmCurrentTerminal[
                        auto_range_terminal.upper()]
                except Exception:
                    raise ValueError(
                        "Current Auto Range Terminal may be 0, 1," +
                        " 'LOW' or 'HIGH'")
            return auto_range_terminal

        def configure_measurement(self, dmm_function, auto_range=True,
                                  manual_range=1.0):
            """ Configure Instrument to take a DMM measurement

            :param dmm_function:DMM function index or name:

                - ``'DC_VOLTS'``, ``'AC_VOLTS'``
                - ``'DC_CURRENT'``, ``'AC_CURRENT'``
                - ``'RESISTANCE'``
                - ``'DIODE'``

            :type dmm_function: int or str
            :param bool auto_range: Enable/Disable auto ranging
            :param float manual_range: Manually set measurement range
            """
            dmm_function = self.validate_dmm_function(dmm_function)
            auto_range = strict_discrete_set(auto_range, [True, False])
            if auto_range is False:
                manual_range = self.validate_range(dmm_function, range)
            self.dmm.configure_measurement(
                dmm_function, auto_range=auto_range, manual_range=manual_range)

        def configure_dc_voltage(self, dmm_input_resistance):
            """ Configure DC voltage input resistance

            :param dmm_input_resistance: Input resistance (``'TEN_MEGA_OHM'``
                                         or ``'TEN_GIGA_OHM'``)
            :type dmm_input_resistance: int or str
            """
            try:
                pyvb.DmmInputResistance(dmm_input_resistance)
            except Exception:
                try:
                    dmm_input_resistance = pyvb.DmmInputResistance[
                        dmm_input_resistance.upper()]
                except Exception:
                    raise ValueError(
                        "Input Resistance may be 0, 1," +
                        " 'TEN_MEGA_OHM' or 'TEN_GIGA_OHM'")
            self.dmm.configure_dc_voltage(dmm_input_resistance)

        def configure_dc_current(self, auto_range_terminal):
            """ Configure auto rage terminal for DC current measurement

            :param auto_range_terminal: Terminal to perform auto ranging
                                        (``'LOW'`` or ``'HIGH'``)
            """
            auto_range_terminal = self.validate_auto_range_terminal(
                auto_range_terminal)
            self.dmm.configure_dc_current(auto_range_terminal)

        def configure_ac_current(self, auto_range_terminal):
            """ Configure auto rage terminal for AC current measurement

            :param auto_range_terminal: Terminal to perform auto ranging
                                        (``'LOW'`` or ``'HIGH'``)
            """
            auto_range_terminal = self.validate_auto_range_terminal(
                auto_range_terminal)
            self.dmm.configure_ac_current(auto_range_terminal)

        def query_measurement(self):
            """ Query DMM measurement settings from the instrument

            :return: Auto range, range data
            :rtype: (bool, float)
            """
            return self.dmm.query_measurement(0)

        def query_dc_voltage(self):
            """ Indicates input resistance setting for DC voltage measurement
            """
            self.dmm.query_dc_voltage()

        def query_dc_current(self):
            """ Indicates auto range terminal for DC current measurement
            """
            self.dmm.query_dc_current()

        def query_ac_current(self):
            """ Indicates auto range terminal for AC current measurement
            """
            self.dmm.query_ac_current()

        def read(self):
            """ Read measurement value from the instrument

            :return: Measurement value
            :rtype: float
            """
            self.dmm.read()

        def reset_instrument(self):
            """ Reset the DMM module to defaults
            """
            self.dmm.reset_instrument()

    class FunctionGenerator(VirtualBenchInstrument):
        """ Represents Function Generator (FGEN) Module of Virtual
        Bench device.
        """

        def __init__(self, virtualbench, reset, vb_name=''):
            """ Acquire FGEN module

            :param virtualbench: Instance of the VirtualBench class
            :type virtualbench: VirtualBench
            :param reset: Resets the instrument
            :type reset: bool
            """
            super().__init__(
                virtualbench.acquire_function_generator,
                reset, 'fgen', vb_name)
            self.fgen = self._instrument_handle

            self._waveform_functions = {"SINE": 0, "SQUARE": 1,
                                        "TRIANGLE/RAMP": 2, "DC": 3}
            # self._waveform_functions_index = {
            # v: k for k, v in self._waveform_functions.items()}
            self._max_frequency = {"SINE": 20000000, "SQUARE": 5000000,
                                   "TRIANGLE/RAMP": 1000000, "DC": 20000000}

        def configure_standard_waveform(self, waveform_function, amplitude,
                                        dc_offset, frequency, duty_cycle):
            """ Configures the instrument to output a standard waveform.
            Check instrument manual for maximum ratings which depend on load.

            :param waveform_function: Waveform function (``"SINE", "SQUARE",
                                      "TRIANGLE/RAMP", "DC"``)
            :type waveform_function: int or str
            :param amplitude: Amplitude in volts
            :type amplitude: float
            :param dc_offset: DC offset in volts
            :type dc_offset: float
            :param frequency: Frequency in Hz
            :type frequency: float
            :param duty_cycle: Duty cycle in %
            :type duty_cycle: int
            """
            waveform_function = strict_discrete_set(
                waveform_function.upper(), self._waveform_functions)
            max_frequency = self._max_frequency[waveform_function.upper()]
            waveform_function = self._waveform_functions[
                waveform_function.upper()]
            amplitude = strict_range(amplitude, (0, 24))
            dc_offset = strict_range(dc_offset, (-12, 12))
            if (amplitude / 2 + abs(dc_offset)) > 12:
                raise ValueError(
                    "Amplitude and DC Offset may not exceed +/-12V")
            duty_cycle = strict_range(duty_cycle, (0, 100))
            frequency = strict_range(frequency, (0, max_frequency))
            self.fgen.configure_standard_waveform(
                waveform_function, amplitude, dc_offset, frequency, duty_cycle)

        def configure_arbitrary_waveform(self, waveform, sample_period):
            """ Configures the instrument to output a waveform. The waveform is
            output either after the end of the current waveform if output
            is enabled, or immediately after output is enabled.

            :param waveform: Waveform as list of values
            :type waveform: list
            :param sample_period: Time between two waveform points
                                  (maximum of 125MS/s, which equals 80ns)
            :type sample_period: float
            """
            strict_range(len(waveform), (1, 1e6))  # 1MS
            sample_period = strict_range(sample_period, (8e-8, 1))
            self.fgen.configure_arbitrary_waveform(waveform, sample_period)

        def configure_arbitrary_waveform_gain_and_offset(self, gain,
                                                         dc_offset):
            """ Configures the instrument to output an arbitrary waveform with
            a specified gain and offset value. The waveform is output either
            after the end of the current waveform if output is enabled, or
            immediately after output is enabled.

            :param gain: Gain, multiplier of waveform values
            :type gain: float
            :param dc_offset: DC offset in volts
            :type dc_offset: float
            """
            dc_offset = strict_range(dc_offset, (-12, 12))
            self.fgen.configure_arbitrary_waveform_gain_and_offset(
                gain, dc_offset)

        @property
        def filter(self):
            ''' Enables or disables the filter on the instrument.

            :param bool enable_filter: Enable/Disable filter
            '''
            return self.fgen.query_filter

        @filter.setter
        def filter(self, enable_filter):
            enable_filter = strict_discrete_set(enable_filter, [True, False])
            self.fgen.enable_filter(enable_filter)

        def query_waveform_mode(self):
            """ Indicates whether the waveform output by the instrument is a
            standard or arbitrary waveform.

            :return: Waveform mode
            :rtype: enum
            """
            return self.fgen.query_waveform_mode()

        def query_standard_waveform(self):
            """ Returns the settings for a standard waveform generation.

            :return: Waveform function, amplitude, dc_offset, frequency,
                     duty_cycle
            :rtype: (enum, float, float, float, int)
            """
            return self.fgen.query_standard_waveform()

        def query_arbitrary_waveform(self):
            """ Returns the samples per second for arbitrary waveform
            generation.

            :return: Samples per second
            :rtype: int
            """
            return self.fgen.query_arbitrary_waveform()

        def query_arbitrary_waveform_gain_and_offset(self):
            """ Returns the settings for arbitrary waveform generation that
            includes gain and offset settings.

            :return: Gain, DC offset
            :rtype: (float, float)
            """
            return self.fgen.query_arbitrary_waveform_gain_and_offset()

        def query_generation_status(self):
            """ Returns the status of waveform generation on the instrument.

            :return: Status
            :rtype: enum
            """
            return self.fgen.query_generation_status()

        def run(self):
            ''' Transitions the session from the Stopped state to the Running
            state.
            '''
            log.info("%s START" % self.name)
            self.fgen.run()

        def self_calibrate(self):
            '''Performs offset nulling calibration on the device. You must run
            FGEN Initialize prior to running this method.
            '''
            self.fgen.self_calibrate()

        def stop(self):
            ''' Transitions the acquisition from either the Triggered or
            Running state to the Stopped state.
            '''
            log.info("%s STOP" % self.name)
            self.fgen.stop()

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
            the device and driver software to a known state.
            '''
            self.fgen.reset_instrument()

    class MixedSignalOscilloscope(VirtualBenchInstrument):
        """ Represents Mixed Signal Oscilloscope (MSO) Module of Virtual Bench
        device. Allows to measure oscilloscope data from analog and digital
        channels.

        Methods from pyvirtualbench not implemented in pymeasure yet:

            - ``enable_digital_channels``
            - ``configure_digital_threshold``
            - ``configure_advanced_digital_timing``
            - ``configure_state_mode``
            - ``configure_digital_edge_trigger``
            - ``configure_digital_pattern_trigger``
            - ``configure_digital_glitch_trigger``
            - ``configure_digital_pulse_width_trigger``
            - ``query_digital_channel``
            - ``query_enabled_digital_channels``
            - ``query_digital_threshold``
            - ``query_advanced_digital_timing``
            - ``query_state_mode``
            - ``query_digital_edge_trigger``
            - ``query_digital_pattern_trigger``
            - ``query_digital_glitch_trigger``
            - ``query_digital_pulse_width_trigger``
            - ``read_digital_u64``
        """

        def __init__(self, virtualbench, reset, vb_name=''):
            """ Acquire MSO module

            :param virtualbench: Instance of the VirtualBench class
            :type virtualbench: VirtualBench
            :param reset: Resets the instrument
            :type reset: bool
            """
            super().__init__(
                virtualbench.acquire_mixed_signal_oscilloscope,
                reset, 'mso', vb_name)
            self.mso = self._instrument_handle

        @staticmethod
        def validate_trigger_instance(trigger_instance):
            """ Check if ``trigger_instance`` is a valid choice

            :param trigger_instance: Trigger instance (``'A'`` or ``'B'``)
            :type trigger_instance: int or str
            :return: Trigger instance
            :rtype: int
            """
            try:
                pyvb.MsoTriggerInstance(trigger_instance)
            except Exception:
                try:
                    trigger_instance = pyvb.MsoTriggerInstance[
                        trigger_instance.upper()]
                except Exception:
                    raise ValueError(
                        "Trigger Instance may be 0, 1, 'A' or 'B'")
            return trigger_instance

        def validate_channel(self, channel):
            """ Check if ``channel`` is a correct specification

            :param str channel: Channel string
            :return: Channel string
            :rtype: str
            """
            def error(channel=channel):
                raise ValueError(
                    f"Channel specification {channel} is not valid!")
            channels = self._vb_handle.expand_channel_string(channel)[0]
            channels = channels.split(', ')
            return_value = []
            for channel in channels:
                # split off lines by last '/'
                try:
                    (device, channel) = re.match(
                        r'(.*)(?:/)(.+)', channel).groups()
                except Exception:
                    error()
                # validate numbers in range 1-2
                if not int(channel) in range(1, 3):
                    error()
                # validate device name: either 'mso' or 'device_name/mso'
                if device == 'mso':
                    pass
                else:
                    try:
                        device = re.match(
                            r'(VB[0-9]{4}-[0-9a-zA-Z]{7})(?:/)(.+)',
                            device).groups()[0]
                    except Exception:
                        error()
                    # device_name has to match
                    if not device == self._device_name:
                        error()
                # constructing line references for output
                return_value.append('mso/' + channel)

            return_value = ', '.join(return_value)
            return_value = self._vb_handle.collapse_channel_string(
                return_value)[0]  # drop number of channels
            return return_value

        # --------------------------
        # Configure Instrument
        # --------------------------

        def auto_setup(self):
            """ Automatically configure the instrument
            """
            self.mso.auto_setup()

        def configure_analog_channel(self, channel, enable_channel,
                                     vertical_range, vertical_offset,
                                     probe_attenuation, vertical_coupling):
            """ Configure analog measurement channel

            :param str channel: Channel string
            :param bool enable_channel: Enable/Disable channel
            :param float vertical_range: Vertical measurement range (0V - 20V),
                the instrument discretizes to these ranges:
                ``[20, 10, 5, 2, 1, 0.5, 0.2, 0.1, 0.05]``
                which are 5x the values shown in the native UI.
            :param float vertical_offset: Vertical offset to correct for
                                          (inverted compared to VB native UI,
                                          -20V - +20V, resolution 0.1mV)
            :param probe_attenuation: Probe attenuation (``'ATTENUATION_10X'``
                                      or ``'ATTENUATION_1X'``)
            :type probe_attenuation: int or str
            :param vertical_coupling: Vertical coupling (``'AC'`` or ``'DC'``)
            :type vertical_coupling: int or str
            """
            channel = self.validate_channel(channel)
            enable_channel = strict_discrete_set(
                enable_channel, [True, False])
            vertical_range = strict_range(vertical_range, (0, 20))
            vertical_offset = strict_discrete_range(
                vertical_offset, [-20, 20], 1e-4
            )
            try:
                pyvb.MsoProbeAttenuation(probe_attenuation)
            except Exception:
                try:
                    probe_attenuation = pyvb.MsoProbeAttenuation[
                        probe_attenuation.upper()]
                except Exception:
                    raise ValueError(
                        "Probe Attenuation may be 1, 10," +
                        " 'ATTENUATION_10X' or 'ATTENUATION_1X'")
            try:
                pyvb.MsoCoupling(vertical_coupling)
            except Exception:
                try:
                    vertical_coupling = pyvb.MsoCoupling[
                        vertical_coupling.upper()]
                except Exception:
                    raise ValueError(
                        "Probe Attenuation may be 0, 1, 'AC' or 'DC'")

            self.mso.configure_analog_channel(
                channel, enable_channel, vertical_range, vertical_offset,
                probe_attenuation, vertical_coupling)

        def configure_analog_channel_characteristics(self, channel,
                                                     input_impedance,
                                                     bandwidth_limit):
            """ Configure electrical characteristics of the specified channel

            :param str channel: Channel string
            :param input_impedance: Input Impedance (``'ONE_MEGA_OHM'`` or
                                    ``'FIFTY_OHMS'``)
            :type input_impedance: int or str
            :param int bandwidth_limit: Bandwidth limit (100MHz or 20MHz)
            """
            channel = self.validate_channel(channel)
            try:
                pyvb.MsoInputImpedance(input_impedance)
            except Exception:
                try:
                    input_impedance = pyvb.MsoInputImpedance[
                        input_impedance.upper()]
                except Exception:
                    raise ValueError(
                        "Probe Attenuation may be 0, 1," +
                        " 'ONE_MEGA_OHM' or 'FIFTY_OHMS'")
            bandwidth_limit = strict_discrete_set(
                bandwidth_limit, [100000000, 20000000])  # 100 Mhz or 20Mhz
            self.mso.configure_analog_channel_characteristics(
                channel, input_impedance, bandwidth_limit)

        def configure_timing(self, sample_rate, acquisition_time,
                             pretrigger_time, sampling_mode):
            """ Configure timing settings of the MSO

            :param int sample_rate: Sample rate (15.26kS - 1GS)
            :param float acquisition_time: Acquisition time (1ns - 68.711s)
            :param float pretrigger_time: Pretrigger time (0s - 10s)
            :param sampling_mode: Sampling mode (``'SAMPLE'`` or
                                  ``'PEAK_DETECT'``)
            """
            sample_rate = strict_range(sample_rate, (15260, 1e9))
            acquisition_time = strict_discrete_range(
                acquisition_time, (1e-09, 68.711), 1e-09)
            # acquisition is also limited by buffer size,
            # which depends on sample rate as well as acquisition time
            pretrigger_time = strict_range(pretrigger_time, (0, 10))
            try:
                pyvb.MsoSamplingMode(sampling_mode)
            except Exception:
                try:
                    sampling_mode = pyvb.MsoSamplingMode[sampling_mode.upper()]
                except Exception:
                    raise ValueError(
                        "Sampling Mode may be 0, 1, 'SAMPLE' or 'PEAK_DETECT'")

            self.mso.configure_timing(
                sample_rate, acquisition_time, pretrigger_time, sampling_mode)

        def configure_immediate_trigger(self):
            """ Configures a trigger to immediately activate on the specified
            channels after the pretrigger time has expired.
            """
            self.mso.configure_immediate_trigger()

        def configure_analog_edge_trigger(self, trigger_source, trigger_slope,
                                          trigger_level, trigger_hysteresis,
                                          trigger_instance):
            """ Configures a trigger to activate on the specified source when
            the analog edge reaches the specified levels.

            :param str trigger_source: Channel string
            :param trigger_slope: Trigger slope (``'RISING'``, ``'FALLING'``
                                  or ``'EITHER'``)
            :type trigger_slope: int or str
            :param float trigger_level: Trigger level
            :param float trigger_hysteresis: Trigger hysteresis
            :param trigger_instance: Trigger instance
            :type trigger_instance: int or str
            """
            trigger_source = self.validate_channel(trigger_source)
            try:
                pyvb.EdgeWithEither(trigger_slope)
            except Exception:
                try:
                    trigger_slope = pyvb.EdgeWithEither[trigger_slope.upper()]
                except Exception:
                    raise ValueError(
                        "Trigger Slope may be 0, 1, 2, 'RISING'," +
                        " 'FALLING' or 'EITHER'")
            trigger_instance = self.validate_trigger_instance(trigger_instance)
            self.mso.configure_analog_edge_trigger(
                trigger_source, trigger_slope, trigger_level,
                trigger_hysteresis, trigger_instance)

        def configure_analog_pulse_width_trigger(self, trigger_source,
                                                 trigger_polarity,
                                                 trigger_level,
                                                 comparison_mode, lower_limit,
                                                 upper_limit,
                                                 trigger_instance):
            """ Configures a trigger to activate on the specified source when
            the analog edge reaches the specified levels within a specified
            window of time.

            :param str trigger_source: Channel string
            :param trigger_polarity: Trigger slope (``'POSITIVE'`` or
                                     ``'NEGATIVE'``)
            :type trigger_polarity: int or str
            :param float trigger_level: Trigger level
            :param comparison_mode: Mode of compariosn (
                                    ``'GREATER_THAN_UPPER_LIMIT'``,
                                    ``'LESS_THAN_LOWER_LIMIT'``,
                                    ``'INSIDE_LIMITS'`` or
                                    ``'OUTSIDE_LIMITS'``)
            :type comparison_mode: int or str
            :param float lower_limit: Lower limit
            :param float upper_limit: Upper limit
            :param trigger_instance: Trigger instance
            :type trigger_instance: int or str
            """
            trigger_source = self.validate_channel(trigger_source)
            try:
                pyvb.MsoTriggerPolarity(trigger_polarity)
            except Exception:
                try:
                    trigger_polarity = pyvb.MsoTriggerPolarity[
                        trigger_polarity.upper()]
                except Exception:
                    raise ValueError(
                        "Comparison Mode may be 0, 1, 2, 3," +
                        " 'GREATER_THAN_UPPER_LIMIT'," +
                        " 'LESS_THAN_LOWER_LIMIT'," +
                        " 'INSIDE_LIMITS' or 'OUTSIDE_LIMITS'")
            try:
                pyvb.MsoComparisonMode(comparison_mode)
            except Exception:
                try:
                    comparison_mode = pyvb.MsoComparisonMode[
                        comparison_mode.upper()]
                except Exception:
                    raise ValueError(
                        "Trigger Polarity may be 0, 1," +
                        " 'POSITIVE' or 'NEGATIVE'")
            trigger_instance = self.validate_trigger_instance(trigger_instance)
            self.mso.configure_analog_pulse_width_trigger(
                trigger_source, trigger_polarity, trigger_level,
                comparison_mode, lower_limit, upper_limit, trigger_instance)

        def configure_trigger_delay(self, trigger_delay):
            """ Configures the amount of time to wait after a trigger condition
            is met before triggering.

                :param float trigger_delay: Trigger delay (0s - 17.1799s)
            """
            self.mso.configure_trigger_delay(trigger_delay)

        def query_analog_channel(self, channel):
            """ Indicates the vertical configuration of the specified channel.

            :return: Channel enabled, vertical range, vertical offset,
                     probe attenuation, vertical coupling
            :rtype: (bool, float, float, enum, enum)
            """
            channel = self.validate_channel(channel)
            return self.mso.query_analog_channel(channel)

        def query_enabled_analog_channels(self):
            """ Returns String of enabled analog channels.

            :return: Enabled analog channels
            :rtype: str
            """
            return self.mso.query_enabled_analog_channels()

        def query_analog_channel_characteristics(self, channel):
            """ Indicates the properties that control the electrical
            characteristics of the specified channel.
            This method returns an error if too much power is
            applied to the channel.

                :return: Input impedance, bandwidth limit
                :rtype: (enum, float)
            """
            return self.mso.query_analog_channel_characteristics(channel)

        def query_timing(self):
            """ Indicates the timing configuration of the MSO.
            Call directly before measurement to read the actual timing
            configuration and write it to the corresponding class variables.
            Necessary to interpret the measurement data, since it contains no
            time information.

            :return: Sample rate, acquisition time, pretrigger time,
                     sampling mode
            :rtype: (float, float, float, enum)
            """
            (self.sample_rate, self.acquisition_time,
             self.pretrigger_time,
             self.sampling_mode) = self.mso.query_timing()
            return (self.sample_rate, self.acquisition_time,
                    self.pretrigger_time, self.sampling_mode)

        def query_trigger_type(self, trigger_instance):
            """ Indicates the trigger type of the specified instance.

            :param trigger_instance: Trigger instance (``'A'`` or ``'B'``)
            :return: Trigger type
            :rtype: str
            """
            return self.mso.query_trigger_type()

        def query_analog_edge_trigger(self, trigger_instance):
            """ Indicates the analog edge trigger configuration of the
            specified instance.

            :return: Trigger source, trigger slope, trigger level, trigger
                     hysteresis
            :rtype: (str, enum, float, float)
            """
            trigger_instance = self.validate_trigger_instance(trigger_instance)
            return self.mso.query_analog_edge_trigger(trigger_instance)

        def query_trigger_delay(self):
            """ Indicates the trigger delay setting of the MSO.

            :return: Trigger delay
            :rtype: float
            """
            return self.mso.query_trigger_delay()

        def query_analog_pulse_width_trigger(self, trigger_instance):
            """ Indicates the analog pulse width trigger configuration of the
            specified instance.

            :return: Trigger source, trigger polarity, trigger level,
                     comparison mode, lower limit, upper limit
            :rtype: (str, enum, float, enum, float, float)
            """
            trigger_instance = self.validate_trigger_instance(trigger_instance)
            return self.mso.query_analog_pulse_width_trigger(trigger_instance)

        def query_acquisition_status(self):
            """ Returns the status of a completed or ongoing acquisition.
            """
            return self.mso.query_acquisition_status()

        # --------------------------
        # Measurement Control
        # --------------------------

        def run(self, autoTrigger=True):
            """ Transitions the acquisition from the Stopped state to the
            Running state. If the current state is Triggered, the
            acquisition is first transitioned to the Stopped state before
            transitioning to the Running state. This method returns an
            error if too much power is applied to any enabled channel.

            :param bool autoTrigger: Enable/Disable auto triggering
            """
            self.mso.run(autoTrigger)

        def force_trigger(self):
            """ Causes a software-timed trigger to occur after the pretrigger
            time has expired.
            """
            self.mso.force_trigger()

        def stop(self):
            """ Transitions the acquisition from either the Triggered or
            Running state to the Stopped state.
            """
            self.mso.stop()

        def read_analog_digital_u64(self):
            """ Transfers data from the instrument as long as the acquisition
            state is Acquisition Complete. If the state is either Running or
            Triggered, this method will wait until the state transitions to
            Acquisition Complete. If the state is Stopped, this method
            returns an error.

            :return: Analog data out, analog data stride, analog t0,
                     digital data out, digital timestamps out, digital t0,
                     trigger timestamp, trigger reason
            :rtype: (list, int, pyvb.Timestamp, list, list, pyvb.Timestamp,
                    pyvb.Timestamp, enum)
            """
            return self.mso.read_analog_digital_u64()

        def read_analog_digital_dataframe(self):
            """ Transfers data from the instrument and returns a pandas
            dataframe of the analog measurement data, including time
            coordinates

            :return: Dataframe with time and measurement data
            :rtype: pd.DataFrame
            """
            (analog_data_out, analog_data_stride
             # , analog_t0, digital_data_out, digital_timestamps_out,
             # digital_t0, trigger_timestamp, trigger_reason
             ) = self.read_analog_digital_u64()[0:2]

            number_of_samples = int(self.sample_rate *
                                    self.acquisition_time) + 1
            if not number_of_samples == (len(analog_data_out) /
                                         analog_data_stride):
                # try updating timing parameters
                self.query_timing()
                number_of_samples = int(self.sample_rate *
                                        self.acquisition_time) + 1
                if not number_of_samples == (len(analog_data_out) /
                                             analog_data_stride):
                    raise ValueError(
                        "Length of Analog Data does not match" +
                        " Timing Parameters")

            pretrigger_samples = int(self.sample_rate * self.pretrigger_time)
            times = (
                list(range(-pretrigger_samples, 0))
                + list(range(0, number_of_samples - pretrigger_samples)))
            times = [list(map(lambda x: x * 1 / self.sample_rate, times))]

            np_array = np.array(analog_data_out)
            np_array = np.split(np_array, analog_data_stride)
            np_array = np.append(np.array(times), np_array, axis=0)
            np_array = np.transpose(np_array)
            return pd.DataFrame(data=np_array)

        def reset_instrument(self):
            """ Resets the session configuration to default values, and resets
            the device and driver software to a known state.
            """
            self.mso.reset()

    class PowerSupply(VirtualBenchInstrument):
        """ Represents Power Supply (PS) Module of Virtual Bench device
        """

        def __init__(self, virtualbench, reset, vb_name=''):
            """ Acquire PS module

            :param virtualbench: Instance of the VirtualBench class
            :type virtualbench: VirtualBench
            :param reset: Resets the instrument
            :type reset: bool
            """
            super().__init__(
                virtualbench.acquire_power_supply,
                reset, 'ps', vb_name)
            self.ps = self._instrument_handle

        def validate_channel(self, channel, current=False, voltage=False):
            """ Check if channel string is valid and if output current/voltage
            are within the output ranges of the channel

            :param channel: Channel string (``"ps/+6V","ps/+25V","ps/-25V"``)
            :type channel: str
            :param current: Current output, defaults to False
            :type current: bool, optional
            :param voltage: Voltage output, defaults to False
            :type voltage: bool, optional
            :return: channel or channel, current & voltage
            :rtype: str or (str, float, float)
            """
            if current is False and voltage is False:
                return strict_discrete_set(
                    channel, ["ps/+6V", "ps/+25V", "ps/-25V"])
            else:
                channel = strict_discrete_set(
                    channel, ["ps/+6V", "ps/+25V", "ps/-25V"])
                if channel == "ps/+6V":
                    current_range = (0, 1)
                    voltage_range = (0, 6)
                else:
                    current_range = (0, 5)
                    voltage_range = (0, 25)
                    if channel == "ps/-25V":
                        voltage_range = (0, -25)
                current = strict_discrete_range(current, current_range, 1e-3)
                voltage = strict_discrete_range(voltage, voltage_range, 1e-3)
                return (channel, current, voltage)

        def configure_voltage_output(self, channel, voltage_level,
                                     current_limit):
            ''' Configures a voltage output on the specified channel. This
            method should be called once for every channel you want to
            configure to output voltage.
            '''
            (channel, current_limit, voltage_level) = self.validate_channel(
                channel, current_limit, voltage_level)
            self.ps.configure_voltage_output(
                channel, voltage_level, current_limit)

        def configure_current_output(self, channel, current_level,
                                     voltage_limit):
            ''' Configures a current output on the specified channel. This
            method should be called once for every channel you want to
            configure to output current.
            '''
            (channel, current_level, voltage_limit) = self.validate_channel(
                channel, current_level, voltage_limit)
            self.ps.configure_current_output(
                channel, current_level, voltage_limit)

        def query_voltage_output(self, channel):
            ''' Indicates the voltage output settings on the specified channel.
            '''
            channel = self.validate_channel(channel)
            return self.ps.query_voltage_output(channel)

        def query_current_output(self, channel):
            ''' Indicates the current output settings on the specified channel.
            '''
            channel = self.validate_channel(channel)
            return self.ps.query_current_output(channel)

        @property
        def outputs_enabled(self):
            ''' Enables or disables all outputs on all channels of the
            instrument.

            :param bool enable_outputs: Enable/Disable outputs
            '''
            return self.ps.query_outputs_enabled()

        @outputs_enabled.setter
        def outputs_enabled(self, enable_outputs):
            enable_outputs = strict_discrete_set(
                enable_outputs, [True, False])
            log.info(f"{self.name} Output {enable_outputs}.")
            self.ps.enable_all_outputs(enable_outputs)

        @property
        def tracking(self):
            ''' Enables or disables tracking between the positive and negative
            25V channels. If enabled, any configuration change on the
            positive 25V channel is mirrored to the negative 25V channel,
            and any writes to the negative 25V channel are ignored.

            :param bool enable_tracking: Enable/Disable tracking
            '''
            return self.ps.query_tracking()

        @tracking.setter
        def tracking(self, enable_tracking):
            enable_tracking = strict_discrete_set(
                enable_tracking, [True, False])
            self.ps.enable_tracking(enable_tracking)

        def read_output(self, channel):
            ''' Reads the voltage and current levels and outout mode of the
            specified channel.
            '''
            channel = self.validate_channel(channel)
            return self.ps.read_output()

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
            the device and driver software to a known state.
            '''
            self.ps.reset_instrument()
