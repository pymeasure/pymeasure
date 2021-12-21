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

import time
import numpy as np

from pymeasure.adapters import FakeAdapter
from pymeasure.instruments import Instrument


class Mock(Instrument):
    """Mock instrument for testing."""

    def __init__(self, wait=.1, **kwargs):
        super().__init__(
            FakeAdapter,
            "Mock instrument",
            includeSCPI=False,
            **kwargs
        )
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
        # mock image attributes # 
        self._w = 1920
        self._h = 1080
        self._image_format = "mono_8"

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
        return float(np.sin(self.time))

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

    def get_frame_width(self):
        """ Image frame width in pixels."""
        time.sleep(self._wait) 
        return self._w

    def set_frame_width(self, w):
        time.sleep(self._wait)
        self._w = w

    frame_width = property(fget=get_frame_width, fset=set_frame_width)

    def get_frame_height(self):
        """ Image frame height in pixels."""
        time.sleep(self._wait) 
        return self._h

    def set_frame_height(self, h):
        time.sleep(self._wait)
        self._h = h

    frame_height = property(fget=get_frame_height, fset=set_frame_height)

    def get_image_format(self):
        """ Format for image data returned from the get_frame() method. Allowed values are:
                mono_8: single channel 8-bit image.
                mono_16: single channel 16-bit image.
        """
        time.sleep(self._wait) 
        return self._image_format 

    def set_image_format(self, format):
        assert format in ["mono_8", "mono_16"], "Unsupported mock image format specified!"
        self._image_format = format

    image_format = property(fget=get_image_format, fset=set_image_format)

    def get_frame(self):
        """ Get a new image frame."""
        im_format_maxval_dict = {"8": 255, "16": 65535} 
        bit_depth = self.image_format.split("_")[1] 
        time.sleep(self._wait)
        return im_format_maxval_dict[bit_depth] * np.random.rand(self.frame_height, self.frame_width)        

    frame = property(fget=get_frame)


