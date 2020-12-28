#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

class HP34401A(Instrument):
    """ Represents the HP 34401A instrument.
    """

    voltage_dc = Instrument.measurement("MEAS:VOLT:DC? DEF,DEF", "DC voltage, in Volts")
    
    voltage_ac = Instrument.measurement("MEAS:VOLT:AC? DEF,DEF", "AC voltage, in Volts")
    
    current_dc = Instrument.measurement("MEAS:CURR:DC? DEF,DEF", "DC current, in Amps")
    
    current_ac = Instrument.measurement("MEAS:CURR:AC? DEF, DEF", "AC current, in Amps")
    
    resistance = Instrument.measurement("MEAS:RES? DEF,DEF", "Resistance, in Ohms")
    
    resistance_4w = Instrument.measurement("MEAS:FRES? DEF,DEF", "Four-wires (remote sensing) resistance, in Ohms")

    trigger_source = Instrument.control(
        ":TRIG:SOUR?", ":TRIG:SOUR %s",
        """ Sets/queries the trigger source.
            Immediate: In the internal trigger mode (remote interface only), the trigger signal is always present. 
                        When you place the multimeter in the wait-for-trigger state, the trigger is issued immediately.
            External: Accept a hardware trigger applied to the Ext Trig terminal
            Bus: This mode is similar to the single trigger mode from the front panel, but you trigger the multimeter 
                by sending a bus trigger command. """,
        validator=strict_discrete_set,
        values={"Immediate": "IMM",
                "External": "EXT",
                "Bus": "BUS"},
        map_values=True
    )
    
    sample_count = Instrument.control(
        "SAMP:COUN?", "SAMP:COUN %g",
        """ Set measurement sample count """,
        validator=truncated_range,
        values=[1, 50000]
    )

    trigger_count = Instrument.control(
        "TRIG:COUN?", "TRIG:COUN %g",
        """ The selected number of triggers is stored in volatile memory;
            The multimeter sets the trigger count to 1 when power has been off or after a remote interface reset.""",
        validator=strict_discrete_set,
        values=[1, 50000]
    )    

    def __init__(self, resourceName, **kwargs):
        super(HP34401A, self).__init__(
            resourceName,
            "HP 34401A",
            **kwargs
        )

    def ac_current_configure(self):
        """ Preset and configure the multimeter for ac current measurements with
            the specified range and resolution.
            This command does not initiate the measurement.
            For ac measurements, resolution is actually fixed at 6(1/2) digits.
            The resolution parameter only affects the front-panel display."""
        self.write("CONF:CURR:AC {range}, {resolution}".format(range="MAX", resolution="MAX"))

    def initiate(self):
        """ Use the INITiate command after you have configured the multimeter for the measurement. 
            This changes the state of the triggering system from the “idle” state to the 
            “wait-for-trigger” state."""

        self.write("INIT")

    def source_tigger(self, source="Immediate"):
        """ Set the trigger source. """
        self.trigger_source = source

