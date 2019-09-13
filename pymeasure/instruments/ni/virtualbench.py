#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

import logging
import re
from ctypes import c_bool, c_size_t, c_double, c_uint8, c_int32, c_uint32, c_int64, c_uint64, c_wchar, c_wchar_p, Structure, c_int, cdll, byref
import pyvirtualbench as pyvb
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_discrete_set,
                                              strict_range)


class NIVirtualBench_Direct(pyvb.PyVirtualBench):
    """ Represents National Instruments Virtual Bench main frame. -> not all methods wrapped so far
        Subclasses implement the functionalities of the different modules:
            - Digital Input Output (DIO) -> all methods wrapped
            - Mixed-Signal-Oscilloscope (MSO)
                * Calibration
            - Function Generator (FGEN)
                * Calibration
            - Digital Mulitmeter (DMM)
                * Calibration #ToDo
            - Power Supply (PS)
                * Calibration #ToDo
            - Serial Peripheral Interface (SPI) #ToDo
            - Inter Integrated Circuit (I2C) #ToDo
        
    """

    def __init__(self, device_name = '', name='VirtualBench'):
        ''' Initialize the VirtualBench library.  This must be called at least
            once for the application. The 'version' parameter must be set to the
            NIVB_LIBRARY_VERSION constant.
        '''
        self.device_name = device_name
        self.name = name
        self.nilcicapi = cdll.LoadLibrary("nilcicapi")
        self.library_handle = c_int(0)
        status = self.nilcicapi.niVB_Initialize(pyvb.NIVB_LIBRARY_VERSION, byref(self.library_handle))
        if (status != pyvb.Status.SUCCESS):
            raise pyvb.PyVirtualBenchException(status, self.nilcicapi, self.library_handle)
        log.info("Initializing %s." % self.name)
    
    def __del__(self):
        """ Ensures the connection is closed upon deletion
        """
        self.release()

class NIVirtualBench(Instrument):
    """ Represents National Instruments Virtual Bench main frame. -> not all methods wrapped so far
        Subclasses implement the functionalities of the different modules:
            - Digital Input Output (DIO) -> all methods wrapped
            - Mixed-Signal-Oscilloscope (MSO)
                * Calibration
            - Function Generator (FGEN) -> all methods wrapped
                * Calibration
            - Digital Mulitmeter (DMM)
                * Calibration #ToDo
            - Power Supply (PS) -> all methods wrapped
                * Calibration #ToDo
            - Serial Peripheral Interface (SPI) #ToDo
            - Inter Integrated Circuit (I2C) #ToDo
        
    """

    def __init__(self, device_name = '', name='VirtualBench'):
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
        self.vb.release()

    def acquire_digital_input_output(self, lines, reset=False):
        reset = strict_discrete_set(reset, [True,False])
        if not (self.device_name + '/dig/') in lines:
            raise ValueError("Lines has to be of form 'device_name/dig/0:7'")
        self.dio = self.DigitalInputOutput(self.vb, lines, reset)

    def acquire_power_supply(self, reset=False):
        reset = strict_discrete_set(reset, [True,False])
        self.ps = self.PowerSupply(self.vb, reset)

    def acquire_function_generator(self, reset=False):
        self.fgen = self.FunctionGenerator(self.vb, reset)
    
    class DigitalInputOutput(object):
        """ Represents Digital Input Output (DIO) Module of Virtual Bench device
            Allows to read/write digital channels and/or set channels to export
            the start signal of FGEN module or trigger of MSO module.
            This class wraps ALL DIO methods available in PyVirtualBench.
        """
        def __init__(self, virtualbench, lines, reset):
            # Parameters & Handle of VirtualBench Instance
            self._device_name = virtualbench.device_name
            self._vb_handle = virtualbench
            # Validate lines argument, store line names & numbers for future reference
            (self._line_names, self._lines_numbers) = self.validate_lines(lines, add_device_name=True,return_single_lines=True,validate_init=False)
            # Create DIO Instance
            self.dio = self._vb_handle.acquire_digital_input_output(self._line_names, reset)

        def validate_lines(self, lines, add_device_name=True,return_single_lines=False,validate_init=False):
            """ Validate lines string. 
                Allowed: 'VB8012-xxxxxxx/dig/0:7', 'VB8012-xxxxxxx/dig/0' or 'dig/0'
                Allowed Line Numbers: 0-7
                :param add_device_name: Add device name to returned line names string.
                :param return_single_lines: Also return list of line numbers.
                :param validate_init: Check if lines are initialized (in :code:`self._line_numbers`).
            """ 
            def error(lines=lines):
                raise ValueError("Line specification {0} is not valid!".format(lines))
            # split off lines by last '/'
            try:
                (device, lines) = re.match(r'(.*)(?:/)(.+)', lines).groups()
            except:
                error()
            # validate numbers in range 0-7
            if len(lines) == 1: # assume single line
                if not int(lines) in range(0,8):
                    error()
                else:
                    single_lines = list(int(lines))
            else: # assume line range i:j
                try:
                    (line1, line2) = re.match(r'([0-9])(?:\:)([0-9])',lines).groups() #split by :
                except:
                    error()
                line1 = int(line1)
                line2 = int(line2)
                if (line1 < line2) and (line1 in range(0,8)) and (line2 in range(0,8)):
                    single_lines = list(range(line1, line2 + 1))
                else:
                    error()
            # validate device name: either 'dig' or 'device_name/dig'
            if device == 'dig':
                pass
            else:
                try:
                    device = re.match(r'(VB[0-9]{4}-[0-9a-zA-Z]{7})(?:/)(.+)',device).groups()[0]
                except:
                    error()
                # device_name has to match
                if not device == self._device_name:
                    error()
            # check if lines are initialized
            if validate_init == True:
                for line in single_lines:
                    if not line in self._lines_numbers:
                        raise ValueError("Digital Line {0} is not initialized".format(line))
            # constructing line references for output
            return_value = ''
            if add_device_name == True:
                return_value = self._device_name + '/dig/' + lines
            else:
                return_value = 'dig/' + lines
            if return_single_lines == True:
                return return_value, single_lines
            else:
                return return_value

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            self.dio.release()

        def tristate_lines(self, lines):
            ''' Sets all specified lines to a high-impedance state. (Default)
            '''
            lines = self.validate_lines(lines, validate_init=True)
            self.dio.tristate_lines(lines)

        def export_signal(self, line, digitalSignalSource):
            ''' Exports a signal to the specified line.
                digitalSignalSource: 0 for FGEN Start or 1 for MSO trigger.
            '''
            line = self.validate_lines(line, validate_init=True)
            digitalSignalSource_values = {"FGEN START":0,"MSO TRIGGER":1}
            digitalSignalSource = strict_discrete_set(digitalSignalSource.upper(),digitalSignalSource_values)
            digitalSignalSource = digitalSignalSource_values[digitalSignalSource.upper()]
            self.dio.export_signal(line, digitalSignalSource)

        def query_line_configuration(self):
            ''' Indicates the current line configurations. Tristate Lines,
                Static Lines, and Export Lines contain comma-separated range_data
                and/or colon-delimited lists of all lines specified in Dig
                Initialize
            '''
            return self.dio.query_line_configuration()

        def query_export_signal(self, line):
            ''' Indicates the signal being exported on the specified line. Use
                Dig Query Line Configuration to check the state of a line.
            '''
            line = self.validate_lines(line, validate_init=True)
            return self.dio.query_export_signal(line)

        def write(self, lines, data):
            ''' Writes data (True = High, False = Low) to the specified lines.
            '''
            lines = self.validate_lines(lines, validate_init=True)
            try:
                for value in data:
                    strict_discrete_set(value,[True,False])
            except:
                raise ValueError("Data {} is not iterable (list or tuple).".format(data))
            self.dio.write(lines,data)

        def read(self, lines):
            ''' Reads the current state of the specified lines.
                lines requires full name specification e.g. 'VB8012-xxxxxxx/dig/0:7'
                since instrument_handle is not required (only library_handle)
            '''
            lines = self.validate_lines(lines, add_device_name=True, validate_init=False) # init not necessary for readout
            return self.dio.read(lines)

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            self.dio.reset_instrument()

    class PowerSupply(object):
        """ Represents Power Supply (PS) Module of Virtual Bench device.
            This class wraps ALL PS methods available in PyVirtualBench,
            except Import/Export of configuration files.
        """
        def __init__(self, virtualbench, reset):
            # Parameters & Handle of VirtualBench Instance
            self._device_name = virtualbench.device_name
            self._vb_handle = virtualbench
            # Create DIO Instance
            reset = strict_discrete_set(reset,[True,False])
            self.ps = self._vb_handle.acquire_power_supply(self._device_name, reset)

        def validate_channel(self, channel, current=False, voltage=False):
            if current == False and voltage == False:
                return strict_discrete_set(channel, ["ps/+6V","ps/+25V","ps/-25V"])
            else:
                channel = strict_discrete_set(channel, ["ps/+6V","ps/+25V","ps/-25V"])
                if channel == "ps/+6V":
                    current_range = range(0,1001)
                    voltage_range = range(0,6001)
                else:
                    current_range = range(0,501)
                    voltage_range = range(0,25001)
                    if channel == "ps/-25V":
                        voltage_range = map(lambda x: -x, voltage_range)
                current_range = map(lambda x: x/1000, current_range)
                voltage_range = map(lambda x: x/1000, voltage_range)
                current = strict_range(current, current_range)
                voltage = strict_range(voltage, voltage_range)
                return (channel, current, voltage)

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            self.ps.release()

        def configure_voltage_output(self, channel, voltage_level, current_limit):
            ''' Configures a voltage output on the specified channel. This
                method should be called once for every channel you want to
                configure to output voltage.
            '''
            (channel, current_limit, voltage_level) = self.validate_channel(channel, current_limit, voltage_level)
            self.ps.configure_voltage_output(channel, voltage_level, current_limit)

        def configure_current_output(self, channel, current_level, voltage_limit):
            ''' Configures a current output on the specified channel. This
                method should be called once for every channel you want to
                configure to output current.
            '''
            (channel, current_level, voltage_limit) = self.validate_channel(channel, current_level, voltage_limit)
            self.ps.configure_current_output(channel, current_level, voltage_limit)

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
            '''
            return self.ps.query_outputs_enabled()

        @outputs_enabled.setter
        def outputs_enabled(self, enable_outputs):
            enable_outputs = strict_discrete_set(enable_outputs, [True,False])
            self.ps.enable_all_outputs(enable_outputs)

        # def enable_all_outputs(self, enable_outputs):
        #     ''' Enables or disables all outputs on all channels of the
        #         instrument.
        #     '''
        #     enable_outputs = strict_discrete_set(enable_outputs, [True,False])
        #     self.ps.enable_all_outputs(enable_outputs)

        # def query_outputs_enabled(self):
        #     ''' Indicates whether the outputs are enabled for the instrument.
        #     '''
        #     self.ps.query_outputs_enabled()

        @property
        def tracking(self):
            ''' Enables or disables tracking between the positive and negative
                25V channels. If enabled, any configuration change on the
                positive 25V channel is mirrored to the negative 25V channel,
                and any writes to the negative 25V channel are ignored.
            '''
            return self.ps.query_tracking()
        
        @tracking.setter
        def tracking(self, enable_tracking):
            enable_tracking = strict_discrete_set(enable_tracking,[True,False])
            self.ps.enable_tracking(enable_tracking)
        
        # def query_tracking(self):
        #     ''' Indicates whether voltage tracking is enabled on the instrument.
        #     '''
        #     self.ps.query_tracking()

        # def enable_tracking(self, enable_tracking):
        #     ''' Enables or disables tracking between the positive and negative
        #         25V channels. If enabled, any configuration change on the
        #         positive 25V channel is mirrored to the negative 25V channel,
        #         and any writes to the negative 25V channel are ignored.
        #     '''
        #     enable_tracking = strict_discrete_set(enable_tracking,[True,False])
        #     self.ps.enable_tracking(enable_tracking)

        def read_output(self, channel):
            ''' Reads the voltage and current levels and outout mode of the specified channel.
            '''
            channel = self.validate_channel(channel)
            return self.ps.read_output()

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            self.ps.reset_instrument()

    class FunctionGenerator(object):
        """ Represents Function Generator (FGEN) Module of Virtual Bench device.
            This class wraps ALL FGEN methods available in PyVirtualBench,
            except Import/Export of configuration files.
        """
        def __init__(self, virtualbench, reset):
            # Parameters & Handle of VirtualBench Instance
            self._device_name = virtualbench.device_name
            self._vb_handle = virtualbench
            self.fgen = self._vb_handle.acquire_function_generator(self._device_name, reset)
            
            self._waveform_functions = {"SINE":0,"SQUARE":1,"TRIANGLE/RAMP":2,"DC":3}
            #self._waveform_functions_index = {v: k for k, v in self._waveform_functions.items()}
            self._max_frequency = {"SINE":20000000,"SQUARE":5000000,"TRIANGLE/RAMP":1000000,"DC":20000000}

        def release(self):
            ''' Stops the session and deallocates any resources acquired during
                the session. If output is enabled on any channels, they remain
                in their current state and continue to output data.
            '''
            self.fgen.release()

        def configure_standard_waveform(self, waveform_function, amplitude, dc_offset, frequency, duty_cycle):
            ''' Configures the instrument to output a standard waveform.
            '''
            waveform_function = strict_discrete_set(waveform_function.upper(),self._waveform_functions)
            max_frequency = self._max_frequency[waveform_function.upper()]
            waveform_function = self._waveform_functions[waveform_function.upper()]
            amplitude = strict_range(amplitude,[x/100 for x in range(0,2401)])
            dc_offset = strict_range(dc_offset, [x/100 for x in range(-1201,1201)])
            if (amplitude/2 + abs(dc_offset)) > 12:
                raise ValueError("Amplitude and DC Offset may not exceed +/-12V")
            duty_cycle = strict_range(duty_cycle,range(0,101))
            frequency = strict_range(frequency, [x/1000 for x in range(0,max_frequency*1000 + 1)])
            self.fgen.configure_standard_waveform(waveform_function, amplitude, dc_offset, frequency, duty_cycle)

        def configure_arbitrary_waveform(self, waveform, sample_period):
            ''' Configures the instrument to output a waveform. The waveform is
                output either after the end of the current waveform if output
                is enabled, or immediately after output is enabled.
            '''
            strict_range(len(waveform),range(1,1000001)) #1MS
            if not ((sample_period >= 8e-8) and (sample_period <=1)):
                raise ValueError("Sample Period allows a maximum of 125MS/s (80ns)")
            self.fgen.configure_arbitrary_waveform(waveform, sample_period)

        def configure_arbitrary_waveform_gain_and_offset(self, gain, dc_offset):
            ''' Configures the instrument to output an arbitrary waveform with a
                specified gain and offset value. The waveform is output either
                after the end of the current waveform if output is enabled, or
                immediately after output is enabled.
            '''
            dc_offset = strict_range(dc_offset, [x/100 for x in range(-1201,1201)])
            self.fgen.configure_arbitrary_waveform_gain_and_offset(gain, dc_offset)

        @property
        def filter(self):
            ''' Enables or disables the filter on the instrument.
            '''
            return self.fgen.query_filter

        @filter.setter
        def filter(self, enable_filter):
            enable_filter = strict_discrete_set(enable_filter,[True,False])
            self.fgen.enable_filter(enable_filter)

        # def enable_filter(self, enable_filter):
        #     ''' Enables or disables the filter on the instrument.
        #     '''
        #     enable_filter = strict_discrete_set(enable_filter,[True,False])
        #     self.fgen.enable_filter(enable_filter)

        # def query_filter(self):
        #     ''' Indicates whether the filter is enabled on the instrument.
        #     '''
        #     self.fgen.query_filter()

        def query_waveform_mode(self):
            ''' Indicates whether the waveform output by the instrument is a
                standard or arbitrary waveform.
            '''
            return self.fgen.query_waveform_mode()

        def query_standard_waveform(self):
            ''' Returns the settings for a standard waveform generation.
                (waveform_function enum, amplitude, dc_offset, frequency, duty_cycle)
            '''
            return self.fgen.query_standard_waveform()

        def query_arbitrary_waveform(self):
            ''' Returns the samples per second for arbitrary waveform generation.
            '''
            return self.fgen.query_arbitrary_waveform()

        def query_arbitrary_waveform_gain_and_offset(self):
            ''' Returns the settings for arbitrary waveform generation that
                includes gain and offset settings.
            '''
            return self.fgen.query_arbitrary_waveform_gain_and_offset()

        def query_generation_status(self):
            ''' Returns the status of waveform generation on the instrument.
            '''
            return self.fgen.query_generation_status() #enum

        def run(self):
            ''' Transitions the session from the Stopped state to the Running
                state.
            '''
            self.fgen.run()

        def self_calibrate(self):
            '''Performs offset nulling calibration on the device. You must run FGEN
               Initialize prior to running this method.
            '''
            self.fgen.self_calibrate()
        
        def stop(self):
            ''' Transitions the acquisition from either the Triggered or Running
                state to the Stopped state.
            '''
            self.fgen.stop()

        def reset_instrument(self):
            ''' Resets the session configuration to default values, and resets
                the device and driver software to a known state.
            '''
            self.fgen.reset_instrument()
 