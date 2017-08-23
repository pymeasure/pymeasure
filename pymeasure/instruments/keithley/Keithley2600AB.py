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
    Keithley 2600 before 'A' use a different kind of triggering and buffering

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

        #define startup and local variables here

        self._wait = wait
        self._tstart = 0
        self._voltage = 10
        self._output_voltage = 0
        self._time = 0
        self._wave = self.wave
        self._units = {'voltage': 'V',
                       'output_voltage': 'V',
                       'time': 's',
                       'wave': 'a.u.'}



###########
#beepmania#
###########

    #time of full note in ms
    _fullnotetime = 800

    # the notes
    P = 0   # pause
    C = 1
    CS = 2  # C sharp
    D = 3
    DS = 4
    E = 5
    F = 6
    FS = 7
    G = 8
    GS = 9
    A = 10
    AS = 11
    B = 12
    # enharmonics
    CF = B
    DF = CS
    EF = DS
    FF = E
    GF = FS
    AF = GS
    BF = AS
    #durations
    FN = _fullnotetime   #full note
    EN = FN/8   #eighth note
    QN = FN/4   #quarter note
    HN = FN/2   #half note



def play(self, octave, note, duration):
        """Plays a note on the beeper
        :param octave: the octave of the note(1-8)
        :param note: the name of the note within the octave (C-B). Only sharped notes are recognized"""
        if note == 0:    # a pause
            time.sleep(duration/1000)
            return
        frequency = 32.7032           # C1
        for k in range(0, octave):    # compute C in given octave
            frequency *= 2
        for k in range(0, note):      # compute frequency of given note
            frequency *= 1.059463094  # 1.059463094 = 12th root of 2
        time.sleep(0.0001*_fullnotetime)             # delay between keys
        self.write(f'beeper.beep({duration}, {frequency})')

    def bigben():
        self.play(4,E,HN)
        self.play(4,C,HN)
        self.play(4,D,HN)
        self.play(3,G,HN+QN); play(3,P,QN)
        self.play(3,G,HN)
        self.play(4,D,HN)
        self.play(4,E,HN)
        self.play(4,C,HN+QN)

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