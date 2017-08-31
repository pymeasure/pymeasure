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
    """Represents the Keithley 2600A and 2600B Series SourceMeters and provides a
    high-level interface for interacting with the instrument.

    Commands are either sent to the instrument when they are called (start_on_call = True) or appended to TSP_script (start_on_call = False).
    The generated TSP script can then be sent to the instrument vie send_script()

    #Todo: Define and implement the required functions using TSP commands sent over the adapter
    #Idea: Define TSP_string and append commands to the script. Start, i.e. send to the instrument, with start_measurement ??

    .. code-block:: python

        keithley = Keithley2600("GPIB::1")

        keithley.apply_current()                # Sets up to source current
        keithley.source_current_range = 10e-3   # Sets the source current range to 10 mA
        keithley.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        keithley.source_current = 0             # Sets the source current to 0 mA
        keithley.enable_source()                # Enables the source output

        keithley.measure_voltage()              # Sets up to measure voltage

        keithley.ramp_to_current(5e-3)          # Ramps the current to 5 mA
        print(keithley.voltage)                 # Prints the voltage in Volts

        keithley.shutdown()                     # Ramps the current to 0 mA and disables output
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



    def write_command(self, new_command):
        """Writes the TSP command either directly to the instrument or to the TSP_script, depending on the choice of start_on_call"""
        if self.start_on_call:
            self.write(new_command)
        else if not start_on_call:
            self.TSP_script = self.TSP_script + " " + new_command  # TODO: Check whether the command is a valid TSP command?!

    def execute_script(self):
        """Executes the TSP_script, i.e. sends the string with the commands to the instrument."""
        self.write(TSP_script)

    def clear_script(self):
        """clears the script so it can be redefined"""
        self.TSP_script = ""

    def reset(self):
            """Resets the SMU"""
            self.write_command('reset()')

    def set_output(self, smux = 'smua', state):
        """Turn the output on or off"""
        #Turn it into  allcaps
        state.upper()
        if state == "ON" or state == "OFF"
            self.write_command(f'{smua}.source.output = OUTPUT_{state}')
###########
# voltage #
###########

    def set_output_fcn (self, smux = 'smua', keyword):
    """Set the source function to be used .
    :param smux:    SMU to be used. Commonly smua
    :param keyword: Defines whether the source function is set to voltage or current

"""
        if keyword == 'voltage':
            self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCVOLTS')
        else:
            if keyword == 'current':
                self.write_command(f'{smux}.source.func = {smux}.OUTPUT_DCAMPS')
    def set_voltage (self, smux = 'smua', voltage):
        """Sets the voltage
        :param smux:    SMU to be used. Commonly smua
        :param voltage: voltage that is to be set"""
        self.write_command(f'{smux}.source.levelv = {voltage}') #todo: Use validator for voltage
        
    def read_voltage(self, smux = 'smua', buffer = 'nvbuffer1', datapoints = 10):
        """Measures the voltage and saves data to internal buffer, then returns ....
        :param smux:        SMU to be used. Commonly smua
        :param buffer:      The Keithley 26XX series offers two dedicated buffers per SMU channel. This parameter defines which one is used to buffer measurement data
        :param datapoints:  number of measurements performed"""
        self.write_command(f'{smux}.measure.count = {datapoints})
        self.write_command(f'{smux}.measure.v({smux}.{buffer})

        if self.start_on_call:


###########
# current #
###########

   def set_current (self, smux = 'smua', current):
        """Sets the current
        :param smux:    SMU to be used. Commonly smua
        :param current: current that is to be set"""
        self.write_command(f'{smux}.source.levelv = {current}') #todo: Use validator for current




###########
#   beep  #
###########



    def beep(self, frequency, duration)
       """Sounds a system beep.
       :param frequency: the frequency of the beep
       :param duration: the duration of the beep
       """
       self.write(f'beeper.beep({duration}, {frequency})')

    def triad(self, base_frequency, duration):
        """ Sounds a musical triad using the system beep.

        :param base_frequency: A frequency in Hz between 65 Hz and 1.3 MHz
        :param duration: A time in seconds between 0 and 7.9 seconds
        """
        self.beep(base_frequency, duration)
        time.sleep(duration)
        self.beep(base_frequency*5.0/4.0, duration)
        time.sleep(duration)
        self.beep(base_frequency*6.0/4.0, duration)

    ###############
    # Current (A) #
    ###############




    ###############
    # Voltage (V) #
    ###############


    ###############
    #   Buffer    #
    ###############


    ###############
    # Time/Trigger#
    ###############






#############FROM MOCK INSTRUMENT #############################

    def get_time(self):
        """Get elapsed time"""
        if self._tstart == 0:
            self._tstart = time.time()
        self._time = time.time() - self._tstart
        return self._time

    def set_time(self, value):
        """
        Wait for the timer to reach the specified time.
        If value = 0, reset.
        """
        if value == 0:
            self._tstart = 0
        else:
            while self.time < value:
                time.sleep(0.001)

    def reset_time(self):
        """Reset the timer to 0 s."""
        self.time = 0
        self.get_time()

    time = property(fget=get_time, fset=set_time)

    def get_wave(self):
        """Get wave."""
        return float(numpy.sin(self.time))

    wave = property(fget=get_wave)

    def get_voltage(self):
        """Get the voltage."""
        time.sleep(self._wait)
        return self._voltage

    def __getitem__(self, keys):
        return keys

    voltage = property(fget=get_voltage)

    def get_output_voltage(self):
        return self._output_voltage

    def set_output_voltage(self, value):
        """Set the voltage."""
        time.sleep(self._wait)
        self._output_voltage = value

    output_voltage = property(fget=get_output_voltage, fset=set_output_voltage)