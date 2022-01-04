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

VALID_LOAD_MODES_DICT = {
    "CURRent": "CURRent",
    "CURRENT": "CURRent",
    "CURR": "CURRent",
    "VOLTage": "VOLTage",
    "VOLTAGE": "VOLTage",
    "VOLT": "VOLTage",
    "POWer": "POWer",
    "POWER": "POWer",
    "POW": "POWer",
    "RESistance": "RESistance",
    "RESISTANCE": "RESistance",
    "RES": "RESistance",
}
VALID_CURRENT_RANGES = [5, 30]
VALID_VOLTAGE_RANGES = [36, 150]
VALID_RESISTANCE_RANGES = ["LOW", "MIDDLE", "HIGH", "UPPER"]


class Sdl1022X(Instrument):
    """
     Represents the Siglent SDL1000X Electronic Load.

     .. code-block:: python

        load = Sdl1022X("USB0::...")
        load.reset()
        load.load_mode = "RESISTANCE"
        load.constant_resistance_load = 10  # Ohms
        load.set_voltage_range("RESISTANCE", 5)  # Volts
        load.input_state = "ON"
        print(load.voltage)

    """
    voltage = Instrument.measurement(
        "MEASure:VOLT:DC?",
        "Voltage across the load in Volts"
    )

    current = Instrument.measurement(
        "MEASure:CURR:DC?",
        "Current across the load in Amps"
    )

    power = Instrument.measurement(
        "MEASure:POW:DC?",
        "Power across the load in Watts"
    )

    resistance = Instrument.measurement(
        "MEASure:RES:DC?",
        "Resistance across the load in Ohms"
    )

    external = Instrument.measurement(
        "MEASure:EXT?",
        "Voltage across the external inputs in Volts"
    )

    input_state = Instrument.control(
        ":SOURce:INPut:STATe?",
        ":SOURce:INPut:STATe %s",
        "Set or query the load state",
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0}
    )

    short_state = Instrument.control(
        ":SOURce:SHORt:STATe?",
        ":SOURce:SHORt:STATe %s",
        "Set or query the short circuit status",
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0}
    )

    transient_mode = Instrument.control(
        ":SOURce:FUNCtion:TRANsient?",
        "SOURce:FUNCtion:TRANsient %s",
        "Set or query the transient load mode",
        map_values=True,
        validator=strict_discrete_set,
        values=VALID_LOAD_MODES_DICT
    )

    load_mode = Instrument.control(
        ":SOURce:FUNC?",
        ":SOURce:FUNC %s",
        "Which mode the electronic load is in",
        validator=strict_discrete_set,
        values=["CURRENT", "VOLTAGE", "POWER", "RESISTANCE", "LED"]
    )

    constant_current_load = Instrument.control(
        ":SOUR:CURR?",
        ":SOUR:CURR %g",
        "Load current in amps",
        validator=strict_range,
        values=[0, 30]
    )

    constant_voltage_load = Instrument.control(
        ":SOUR:VOLT?",
        ":SOUR:VOLT %g",
        "Load voltage in volts",
        validator=strict_range,
        values=[0, 150]
    )

    constant_resistance_load = Instrument.control(
        ":SOUR:RES?",
        ":SOUR:RES %g",
        "Load resistance in Ohms",
        validator=strict_range,
        values=[0, 10000]
    )
    constant_power_load = Instrument.control(
        ":SOUR:POW?",
        ":SOUR:POW %g",
        "Load power in Watts",
        validator=strict_range,
        values=[0, 200]
    )

    def __init__(self, adapter, **kwargs):
        super(Sdl1022X, self).__init__(
            adapter, "Siglent SDL1022X Electronic Load", **kwargs
        )

    def set_current_range(self, mode, current):
        if current > max(VALID_CURRENT_RANGES):
            raise ValueError
        if mode not in VALID_LOAD_MODES_DICT.keys():
            raise ValueError
        self.write(f":SOUR:{VALID_LOAD_MODES_DICT[mode]}:IRANGe {current}")

    def get_current_range(self, mode):
        if mode not in VALID_LOAD_MODES_DICT.keys():
            raise ValueError
        return float(self.ask(f":SOUR:{VALID_LOAD_MODES_DICT[mode]}:IRANGe?"))

    def set_voltage_range(self, mode, voltage):
        if voltage > max(VALID_VOLTAGE_RANGES):
            raise ValueError
        if mode not in VALID_LOAD_MODES_DICT.keys():
            raise ValueError
        self.write(f":SOUR:{VALID_LOAD_MODES_DICT[mode]}:VRANGe {voltage}")

    def get_voltage_range(self, mode):
        if mode not in VALID_LOAD_MODES_DICT.keys():
            raise ValueError
        return float(self.ask(f":SOUR:{VALID_LOAD_MODES_DICT[mode]}:VRANGe"))

    def get_wavebuffer(self, series, reset_display=None, remove_nulls=False):
        """
        Loads the last 200 samples from the waveform buffer

        NOTE: The wavebuffer in the SDL1000X has a major drawback because it
        does not keep track of what has already been retrieved. Therefore,
        there is no "correct" way of knowing what samples have already been
        read out. The best workaround is to reset the waveform buffer after
        each retrieval and use the null (0.0000) values as a marker of the
        start of real data. This has the noteable drawbacks of resetting the
        instrument display. Additionally, there is the risk of removing real
        and measured null values. Use `remove_nulls` and `reset_display` at
        your own risk!


        :param series: Which measurement to retrieve: CURRent, VOLTage, POWer, RESistance
        :param reset_display: Reset the display with a span of integer seconds
        :param remove_nulls: Utility for only displaying the samples after the last null
        """
        if series not in VALID_LOAD_MODES_DICT.keys():
            raise ValueError
        resp = self.ask(f"MEASure:WAVEdata? {VALID_LOAD_MODES_DICT[series]}")
        if remove_nulls:
            # Removing the first sets of null values
            arr = [float(i) for i in resp.split("\x00")[0].split("0.0000")[-1].split(",") if i]
        else:
            arr = [float(i) for i in resp.split("\x00")[0].split(",") if i]
        if reset_display and int(reset_display) > 4:
            self.write(f":WAVE:TIME {int(reset_display)}")
        elif int(reset_display) < 4:
            raise ValueError
        return arr
