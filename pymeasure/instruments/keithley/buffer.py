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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range
from pymeasure.adapters import PrologixAdapter

import numpy as np
from time import sleep, time


class KeithleyBuffer(object):
    """ Implements the basic buffering capability found in
    many Keithley instruments. """

    buffer_points = Instrument.control(
        ":TRAC:POIN?", ":TRAC:POIN %d",
        """ An integer property that controls the number of buffer points. This
        does not represent actual points in the buffer, but the configuration
        value instead. """,
        validator=truncated_range,
        values=[2, 1024],
        cast=int
    )

    def config_buffer(self, points=64, delay=0):
        """ Configures the measurement buffer for a number of points, to be
        taken with a specified delay.

        :param points: The number of points in the buffer.
        :param delay: The delay time in seconds.
        """
        # Enable measurement status bit
        # Enable buffer full measurement bit
        self.write(":STAT:PRES;*CLS;*SRE 1;:STAT:MEAS:ENAB 512;")
        self.write(":TRAC:CLEAR;")
        self.buffer_points = points
        self.trigger_count = points
        self.trigger_delay = delay
        self.write(":TRAC:FEED SENSE;:TRAC:FEED:CONT NEXT;")
        self.check_errors()

    def is_buffer_full(self):
        """ Returns True if the buffer is full of measurements. """
        status_bit = int(self.ask("*STB?"))
        return status_bit == 65

    def wait_for_buffer(self, should_stop=lambda: False,
                        timeout=60, interval=0.1):
        """ Blocks the program, waiting for a full buffer. This function 
        returns early if the :code:`should_stop` function returns True or
        the timeout is reached before the buffer is full.

        :param should_stop: A function that returns True when this function should return early
        :param timeout: A time in seconds after which this function should return early
        :param interval: A time in seconds for how often to check if the buffer is full
        """
        # TODO: Use SRQ initially instead of constant polling
        #self.adapter.wait_for_srq()
        t = time()
        while not self.is_buffer_full():
            sleep(interval)
            if should_stop():
                return
            if (time()-t)>timeout:
                raise Exception("Timed out waiting for Keithley buffer to fill.")

    @property
    def buffer_data(self):
        """ Returns a numpy array of values from the buffer. """
        self.write(":FORM:DATA ASCII")
        return np.array(self.values(":TRAC:DATA?"), dtype=np.float64)

    def start_buffer(self):
        """ Starts the buffer. """
        self.write(":INIT")

    def reset_buffer(self):
        """ Resets the buffer. """
        self.write(":STAT:PRES;*CLS;:TRAC:CLEAR;:TRAC:FEED:CONT NEXT;")

    def stop_buffer(self):
        """ Aborts the buffering measurement, by stopping the measurement
        arming and triggering sequence. If possible, a Selected Device 
        Clear (SDC) is used. """
        if type(self.adapter) is PrologixAdapter:
            self.write("++clr")
        else:
            self.write(":ABOR")

    def disable_buffer(self):
        """ Disables the connection between measurements and the
        buffer, but does not abort the measurement process.
        """
        self.write(":TRAC:FEED:CONT NEV")
