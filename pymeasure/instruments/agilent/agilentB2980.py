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

from pymeasure.instruments import Instrument, SCPIUnknownMixin


class AgilentB2980(SCPIUnknownMixin, Instrument):
    """
    Represent the Agilent/Keysight B2980A/B series, Femto/Picoammeter Electrometer/High Resistance Meter.

    TODO: fix all code bellow
    
    Implemented measurements: voltage_dc, voltage_ac, current_dc, current_ac, resistance,
    resistance_4w
    """
    def __init__(self, adapter, name="Agilent/Keysight B2980 Electrometer", **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    # only the most simple functions are implemented
    voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "Get DC voltage, in Volts")

    voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "Get AC voltage, in Volts")

    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "Get DC current, in Amps")

    current_ac = Instrument.measurement("MEAS:CURR:AC? DEF,DEF", "Get AC current, in Amps")

    resistance = Instrument.measurement("MEAS:RES? DEF,DEF", "Get Resistance, in Ohms")

    resistance_4w = Instrument.measurement(
        "MEAS:FRES? DEF,DEF", "Get Four-wires (remote sensing) resistance, in Ohms")
