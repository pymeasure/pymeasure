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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class Keithley2306(Instrument):
    """
     Represents the Keithley 2306 battery simulator.

     .. code-block:: python

        battery_sim = Keithley2306("GPIB::...")
        battery_sim.reset()
        battery_sim.voltage = 4.2
        battery_sim.sense1_function = "CURR"
        battery_sim.current_limit1 = 0.08
        battery_sim.current_limit1_type = "TRIP"
        battery_sim.output1 = "ON"
        print(battery_sim.measure1)

    """
    voltage1 = Instrument.control(
        "SOURce1:VOLTage?",
        "SOURce1:VOLTage %g",
        "DC output voltage of Source 1 (Battery), in Volts",
        validator=strict_range,
        values=[0, 15]
    )

    voltage1_protection = Instrument.control(
        "SOURce1:VOLTage:PROTection?",
        "SOURce1:VOLTage:PROTection %g",
        """
         Keithley 2306 uses Sense +/- terminals to detect voltage. This 4-wire
         configuration allows correction for loss in test leads. However, loss
         of Sense +/- wires will result in unreglated supply. Source
         protection prevents loss of regulation from exceeding specified
         values. For example, if an output voltage of 5 is set, a protection
         voltage of 2 will limit supply output without feedback to between
         3 and 7 volts.
        """,
        validator=strict_range,
        values=[0, 8]
    )

    voltage1_protection_state = Instrument.measurement(
        "SOURce1:VOLTage:PROTection:STATe?",
        """
         Reads voltage protection state. Whether triggered or not.
        """,
        map_values=True,
        values={'ON': 1, 'OFF': 0}
    )

    voltage1_protection_clamp = Instrument.control(
        "SOURce1:VOLTage:PROTection:CLAMp?",
        "SOURce1:VOLTage:PROTection:CLAMp %s",
        """
         Clamp mode prevents outputted voltage from going below -0.6V relative
         to instrument ground. This is irrespective of measured "sense"
         voltage. See `voltage1_protection` for more information.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0}
    )

    current_limit1 = Instrument.control(
        "SOURce1:CURRent?",
        "SOURce1:CURRent %g",
        "DC current limit for Source 1 (Battery), in Amps",
        validator=strict_range,
        values=[0.006, 5]
    )

    current_limit1_type = Instrument.control(
        "SOURce1:CURRent:TYPe?",
        "SOURce1:CURRent:TYPe %s",
        """
         Current limit mode. `TRIP` will shut off source if current limit is
         reached. `LIMit` will limit max current available to load.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={
            "LIMit": "LIM",
            "LIM": "LIM",
            "TRIP": "TRIP"
        }
    )

    output1 = Instrument.control(
        "OUTPut1?",
        "OUTPut1 %s",
        """
         Output state of Source 1 (Battery).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0}
    )

    output1_impedance = Instrument.control(
        "OUTPut1:IMPedance?",
        "OUTPut1:IMPedance %g",
        "Simulated output impedance of battery 0 to 1 Ohms",
        validator=strict_range,
        values=[0, 1]
    )

    sense1_current_range = Instrument.control(
        "SENSe1:CURRent:RANGe?",
        "SENSe1:CURRent:RANGe %g",
        """
         Upper limit of sense range, in Amps. Limited to HIGH and LOW modes
         of 0.005 A and 5.0 A in Keithley 2306.
        """,
        validator=strict_discrete_set,
        values={0.005, 5.0}
    )

    sense1_current_range_auto = Instrument.control(
        "SENSe1:CURRent:RANGe:AUTO?",
        "SENSe1:CURRent:RANGe:AUTO %g",
        "Sense range auto, ON or OFF",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0},
    )

    sense1_function = Instrument.control(
        "SENSe1:FUNCtion?",
        "SENSe1:FUNCtion  %s",
        """
         Sense function. Basic functions are CURRent and VOLTage. DVMeter
         is also supported for measuring external voltages.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={
            "\"CURR\"": "\"CURR\"",
            "\"VOLT\"": "\"VOLT\"",
            "CURR": "\"CURR\"",
            "VOLT": "\"VOLT\"",
            "DVMeter": "\"DVM\""
        }
    )

    sense1_avg = Instrument.control(
        "SENSe1:AVERage?",
        "SENSe1:AVERage  %d",
        "The number of samples to average for voltage, current, and DVM",
        validator=strict_discrete_set,
        values=range(1, 11)
    )
    measure1 = Instrument.measurement(
        ":READ1?",
        """
         Reads the configured sense function on SENSe1 (Battery), see
         `sense1_function` for more information and current configuration.

        """
    )

    error = Instrument.measurement(
        "SYSTem:ERRor?",
        """
         Reads and clears oldest message in error queue.
        """
    )

    display = Instrument.control(
        "DISPlay:WINDow1:TEXT:DATA?",
        "DISPlay:WINDow1:TEXT:DATA \"%s\"",
        """
         Displays text on screen. Strings up to 32 characters are supported.
        """
    )

    display_state = Instrument.control(
        "DISPlay:WINDow1:TEXT:STATE?",
        "DISPlay:WINDow1:TEXT:STATE %g",
        """
         Display configuration, switches between instrument mode (OFF) and user
         configurable string (set using display command). NOTE: this state will
         persist over soft resets. It will be reset during Power-on-Reset (PoR).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0},
    )

    def __init__(self, adapter, **kwargs):
        super(Keithley2306, self).__init__(
            adapter, "Keithley 2306 Battery Simulator", **kwargs
        )
