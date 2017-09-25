#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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

import numpy
import time

from pymeasure.adapters import FakeAdapter
from pymeasure.instruments import Instrument

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument, RangeException
from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

from .buffer import KeithleyBuffer

import numpy as np
import time


class Keithley2600AB(Instrument):
    """Represents the Keithley 26XX Series SourceMeters and provides a
    high-level interface for interacting with the instrument.

    Commands are either sent to the instrument when they are called (start_on_call = True) or appended to TSP_script (start_on_call = False).
    The generated TSP script can then be sent to the instrument via execute_script()

    #Todo: Define and implement the required functions using TSP commands sent over the adapter
    #Todo: Give a minimal code example: Set up instrument, Set up Buffer, Perform measurement

    .. code-block:: python

        keithley = Keithley2600("GPIB::1")

        keithley.apply_current()                # Sets up to source current

        """

    def __init__(self, adapter, **kwargs):

        super().__init__(
            adapter,
            "Keithley2600AB SourceMeter",
            includeSCPI=False,
            **kwargs
        )

        #TSP script commands can be directly sent and executed or appended to a string and send as one. Having self.TSP_script also allows to use already implemented TSP scripts (has to be tested!)
        self.start_on_call = True
        self.TSP_script = ""

################################
# TSP script related functions #
################################
    def write_command(self, new_command):
        """Writes the TSP command either directly to the instrument or to the TSP_script, depending on the choice of start_on_call"""
        if self.start_on_call:
            self.write(new_command)
        else if not start_on_call:
            self.TSP_script = self.TSP_script + "\n" + new_command  # TODO: Check whether the command is a valid TSP command?!

    def execute_script(self):
        """Executes the TSP_script, i.e. sends the string with the commands to the instrument."""
        self.write(TSP_script)

    def clear_script(self):
        """clears the script so it can be redefined"""
        self.TSP_script = ""
#todo: add load_TSP function that allows to load external TSP scripts (load --> execute makes them usable)
#####################
# general functions #
#####################
    def reset(self, smux = 'smua'):
            """Resets the SMU
            :param smux: SMU to be reset"""
            self.write_command(f'{smux}.reset()')

    def set_output(self, smux = 'smua', state):
        """Turn the output on or off. State of the output can also be changed with :code enable_source or :code disable_source"""
        #Turn it into  allcaps
        state.upper()
        if state == "ON" or state == "OFF"
            self.write_command(f'{smua}.source.output = OUTPUT_{state}')

    def enable_source(self, smux='smua'):
        self.write_command(f'{smua}.source.output = OUTPUT_ON')

    def disable_source(self, smux='smua'):
        self.write_command(f'{smua}.source.output = OUTPUT_OFF')

    def set_autorange(self, smux = 'smua', state='ON', measurefunction):
        """Sets the auto-range value of the smu channel
        :param smux:    SMU channel to be used
        :param state:   auto-range channel to be set. can be OFF: Disabled, ON: Enabled or FOLLOW_LIMIT: Measure range automatically set to the limit range
        :param measurefunction: The measurement function for which the autorange property is changed."""
        voltages = {'voltage','voltages','v','V'}
        currents = {'current''currents','i','I'}
        measurefunction.lower()

        if measurefunction in voltages:
            measurefunction = 'v'
        else:
            if measurefunction in currents:
                measurefunction = 'i'

        self.write_command(f'{smux}.measure.autorange{measurefunction} = AUTORANGE_{state}')

    def set_delay(self, mdelay, smux = 'smua'):
        """This attribute allows for additional delay (settling time) before taking a measurement.
        If more than one measurement per sourced value is performed, the measurement delay is only inserted before the first measurement.
        :param mdelay: the time in seconds after sourcing before the first measurement is performed.
        :param smux: The channel of the SMU that is used"""
        self.write_command(f'{smux}.measure.delay = {mdelay}')

    def set_output_fcn (self, smux = 'smua', keyword):
        """Set the source function to be used .
        :param smux:    SMU to be used. Commonly smua
        :param keyword: Defines whether the source function is set to voltage or current"""""
        if keyword == 'voltage':
             self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCVOLTS')
        else:
                if keyword == 'current':
                    self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCAMPS')
###########
# buffer  #
###########

    def clear_buffer(self, smux = 'smua', id = '1'):
        """Clears the dedicaded reading buffer
        :param smux:    The SMU which buffer should be cleared.
        :param id:      The id of the buffer to be cleared. Each smu has two dedicaded reading buffers. use id ='all' to clear all reading buffers
        """
        if id <> 'all':
            self.write_command(f'{smux}.nvbuffer{id}.clear()')
        else:
            for i = 1 to 2:
                self.write_command(f'{smux}.nvbuffer{i}.clear()')

    def set_buffer_ascii(self, precision = 6):
        """This function set the data format to ASCII with the given precision
        :param precision:   Precision used for all data received fromt he buffer"""

        self.write_command(f'format.data = format.ASCII\n format.asciiprecision = {precision}')

    def get_buffer_data(self, buffer='smua.nvbuffer1'):
        """Returns the Data from a buffer as numpy array
        :param buffer:  The instrument buffer to be read."""
        #todo: Check whether it is that simple to get data into np array
        return np.array(self.write(f'printbuffer(1, {buffer}.n,{buffer})'))
        return np.array(self.write(f'printbuffer(1, {buffer}.n,{buffer})'))
###########
# voltage #
###########

    def sweep(self, start, stop, stime, points, smux = 'smua', keyword='lin',source='V'):
        """ This method uses the Keithley built-in TSP scripts to execute linear or logarithmic sweeps
        :param start:   Start value of the sweep parameter
        :param stop:    End value of the sweep parameter
        :param stime:   Settling time - i.e. time after sourcing before first measurement
        :param smux.:   SMU to be used
        :param keyword: Sweeping method. Can be either 'lin' for linear or 'log' for logarithmic
        :param source:  Sourced quantity (i.e. 'V' or 'I')
        """

        if source == 'V':
            if keyword == 'lin':
                self.write_command(f'SweepVLinMeasureI({smux}, {start}, {stop}, {stime}, {points}')
            elif keyword == 'log':
                self.write_command(f'SweepVLogMeasureI({smux}, {start}, {stop}, {stime}, {points})')
            else:
                print("Invalid choice of keyword in sweep(source='V')")
        elif source == 'I':
            if keyword == 'lin':
                self.write_command(f'SweepILinMeasureV({smux}, {start}, {stop}, {stime}, {points}')
            elif keyword == 'log':
                self.write_command(f'SweepILogMeasureV({smux}, {start}, {stop}, {stime}, {points})')
            else:
                print("Invalid choice of keyword in sweep(source='I')")
        else:
            print("Invalid choice of method in sweep()")








###########
#   beep  #
###########

    def read_buffer(self, smux='smua', buffer = 'nvbuffer1'):

        np.array(self.write_command('printbuffer(1, {smux}.{buffer}.n, {smux}.{buffer})'))
        #todo: write read_buffer method

    def beep(self, frequency, duration):
       """Sounds a system beep.
       :param frequency: the frequency of the beep
       :param duration: the duration of the beep"""
       self.write_command(f'beeper.beep({duration}, {frequency})')

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep. Can for instance be used to indicate a finished measurement.

        :param base_frequency: Frequency of the base tone in Hz (between 65 Hz and 1.3 MHz)
        :param duration: A time in seconds per beep (between 0 and 7.9 seconds)
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency*5.0/4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency*6.0/4.0, duration)
        #todo: change function so sleep gets executed within the instrument and not on PC
###############
# Current (A) #
###############
    def set_current (self, smux = 'smua', current):
        """Sets the current
        :param smux:    SMU to be used. Commonly smua
        :param current: current that is to be set"""
        self.write_command(f'{smux}.source.levelv = {current}') #todo: Use validator for current

###############
# Voltage (V) #
###############
    def set_voltage(self, smux='smua', voltage):
            """Sets the voltage
            :param smux:    SMU to be used. Commonly smua
            :param voltage: voltage that is to be set"""
            self.write_command(f'{smux}.source.levelv = {voltage}')  # todo: Use validator for voltage

    def read_voltage(self, smux='smua', buffer='nvbuffer1', datapoints=10):
            """Measures the voltage and saves data to internal buffer, then returns ....
            :param smux:        SMU to be used. Commonly smua
            :param buffer:      The Keithley 26XX series offers two dedicated buffers per SMU channel. This parameter defines which one is used to buffer measurement data
            :param datapoints:  number of measurements performed"""
            # clear buffer
            self.write_command(f'{smux}.{buffer}.clear() smua.nvbuffer1.appendmode = 1')
            # set number of points and fill buffer
            self.write_command(f'{smux}.measure.count = {datapoints})
            self.write_command(f'{smux}.measure.v({smux}.{buffer})

            if self.start_on_call:
            # read and return buffer
                else:
            #todo: write measure_voltage method that reads the buffer


