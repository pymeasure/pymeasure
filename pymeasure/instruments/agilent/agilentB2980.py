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

from pymeasure.instruments import SCPIMixin, Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class AgilentB298xBattery(Instrument):
    """
    Support for the Battery option of the B2983/7 models.
    """
    
    battery_level =  Instrument.measurement(
        ":SYST:BATT?",
        """Return the percentage of the remaining battery capacity.""",
    )
    
    battery_cycles =  Instrument.measurement(
        ":SYST:BATT:CYCL?",
        """Returns the battery cycle count.""",
    )
    
    battery_selftest =  Instrument.measurement(
        ":SYST:BATT:TEST?",
        """Performs self-test on the battery and returns the result.
            0: test passed
            1: test failed
           If battery self-test fail, a 1 is returned and an error is stored in the error queue.""",
        )

class AgilentB2981(Instrument):
    """
    Represent the Agilent/Keysight B2981A/B series, Femto/Picoammeter.
    Implemented measurements: current
    TODO: add more measurement modes
    """
    def __init__(self, adapter, name="Agilent/Keysight B2980A/B Femto/Picoammeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    # current measurement 
    current_dc = Instrument.measurement(":MEAS:CURR:DC?", "Get DC current, in Amps")


class AgilentB2983(AgilentB2981, AgilentB298xBattery):
    """
    Represent the Agilent/Keysight B2983A/B series, Femto/Picoammeter.
    Battery operation is possible.
    """
    def __init__(self, adapter, name="Agilent/Keysight B2981A/B Femto/Picoammeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class AgilentB2985(AgilentB2981):
    """
    Represent the Agilent/Keysight B2985A/B series Femto/Picoammeter Electrometer/High Resistance Meter.
    """
    output_enabled =  Instrument.control(
        ":OUTP:STAT?", ":OUTP:STAT %s",
        """Enables or disables the source output (string strictly in '0', '1', 'ON', 'OFF').""",
        
        validator=strict_discrete_set,
        values={'ON':1, 'OFF':0, '1':1, '0':0, 0:0, 1:1}
        )


class AgilentB2987(AgilentB2985, AgilentB298xBattery):
    """
    Represent the Agilent/Keysight B2987A/B series Femto/Picoammeter Electrometer/High Resistance Meter.
    Battery operation is possible.
    """
    
    def __init__(self, adapter, name="Agilent/Keysight B2987A/B Electrometer/High Resistance Meter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
    
