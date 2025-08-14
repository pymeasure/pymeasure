#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.errors import Error, RangeError
from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Thurlby1905a(Instrument):
    """Represents the Thurlby 1905a intelligent digital multimeter

    .. code-block python

        from pymeasure.instruments.tti import Thurlby1905a

        dmm = Thurlby1905a("ASRL/dev/ttyACM0::INSTR", baud_rate=2400)
        output = dmm.read_measurement

    """

    def __init__(self, adapter, name="Thurlby 1905a", **kwargs):
        kwargs.setdefault("read_termination", "\r")
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs,
        )

    @staticmethod
    def _translate(measurement):
        # Easier to test if a static method
        #
        # There are two types of measurements. A valid reading 'R' or a message 'M'.
        # All measurements, excluding termination characters, are 10 bytes long.
        #
        # Examples:
        #  Valid reading of -0.0
        #   'R- 000.00 '
        #
        #  Valid reading of 997.628
        #   'R  997.628'
        #
        # A message is anything other than a reading:
        #
        #  Over Range
        #   'M   OR    '
        #
        #  An error
        #   'M   ERROR '
        #
        # The instruments software version, issued, briefly, at power-up:
        #   'M  Cd  00 '

        if len(measurement) != 10:
            raise ValueError("Measurement '%s' is not expected 10 bytes long." % measurement)

        measurement_type = measurement[0]
        body = measurement[1:].replace(" ", "")

        if measurement_type == "R":
            return float(body)

        if measurement_type == "M":
            if body == "OR":
                raise RangeError("Over Range: increase range on instrument.")
            if body == "ERROR":
                raise Error("Error on instrument.")
            else:
                raise Error(body)

        raise Error("Unknown type of measurement '%s'." % measurement)

    @property
    def read_measurement(self):
        """Get the output from the instrument

        :returns: the reading from the instrument
        :rtype: float

        :rasies ValueError: If measurement not expected length
        :raises RangeError: If input exceeds selected measurement range of instrument
        :raises Error: If unknown message or measurement type
        """
        return Thurlby1905a._translate(self.read())
