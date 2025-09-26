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

from pymeasure.errors import Error, RangeError
from pymeasure.instruments import Instrument


class Thurlby1905a(Instrument):
    """Represents the Thurlby 1905a intelligent digital multimeter

    This instrument only provides measurement output via an RS-232 serial port.
    The serial port can only be read from, not written to.

    Earlier models had a Baud rate of 2400, later ones 9600.

    .. code-block python

        from pymeasure.instruments.thurlby import Thurlby1905a

        dmm = Thurlby1905a("ASRL/dev/ttyACM0::INSTR")
        output = dmm.measurement

    """

    def __init__(self, adapter, name="Thurlby 1905a", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            read_termination="\r",
            **kwargs,
        )

    @staticmethod
    def _parse(measurement):
        """Get the output reading from the instrument.

        :param measurement: the reading from the serial port
        :type measurement: str

        :return: the interpreted reading
        :rtype: float

        The first byte of a measurement determines what type it is:

        * A valid reading. First byte: 'R'.
        * A message. First byte: 'M'.

        All measurements, excluding termination characters, are 10 bytes long.

        Example readings:

        ============ ===============
        Reading      Returns
        ============ ===============
        'R  000.00 ' 0.0
        'R  997.628' 997.628
        'R- 000.00 ' -0.0
        'R-  01.800' -1.8
        ============ ===============

        Example messages:

        ============ ============================================================
        Message      Meaning
        ============ ============================================================
        'M   OR    ' Over range
        'M   ERROR ' Error
        'M  Cd  00 ' The insruments software version (issued briefly at power-up)

        """

        # Easier to test if a static method

        if len(measurement) != 10:
            raise ValueError(f"Measurement '{measurement}' is not the expected 10 bytes long.")

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

        raise Error(f"Unknown type of measurement '{measurement}'.")

    @property
    def measurement(self):
        """Get the output from the instrument

        :returns: the reading from the instrument
        :rtype: float

        :rasies ValueError: If measurement not expected length
        :raises RangeError: If input exceeds selected measurement range of instrument
        :raises Error: If unknown message or measurement type
        """
        return Thurlby1905a._parse(self.read())
