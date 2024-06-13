#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class DCXS(Instrument):
    """ AJA DCXS-750 or 1500 DC magnetron sputtering power supply with multiple outputs

    Connection to the device is made through an RS232 serial connection.
    The communication settings are fixed in the device at 38400, one stopbit, no parity.
    The device's communication protocol uses single character commands and fixed length replies,
    both without any terminator.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: The name of the instrument.
    :param kwargs: Any valid key-word argument for Instrument
    """

    def __init__(self, adapter, name="AJA DCXS sputtering power supply", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            write_termination="",
            read_termination="",
            asrl={"baud_rate": 38400},
            **kwargs
        )
        # here we want to flush the read buffer since the device upon power up sends some '>'
        # characters.
        self.adapter.flush_read_buffer()

    def ask(self, command, query_delay=None, **kwargs):
        """Write a command to the instrument and return the read response.

        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :param \\**kwargs: Keyword arguments passed to the read method.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        return self.read(**kwargs)

    def read(self, reply_length=-1, **kwargs):
        return self.read_bytes(reply_length, **kwargs).decode()

    id = Instrument.measurement(
        "?", """Get the power supply type identifier.""",
        cast=str,
        values_kwargs={'reply_length': 9},
    )

    software_version = Instrument.measurement(
        "z", """Get the software revision of the power supply firmware.""",
        cast=str,
        values_kwargs={'reply_length': 5},
    )

    power = Instrument.measurement(
        "d", """Measure the actual output power in W.""",
        cast=int,
        values_kwargs={'reply_length': 4},
    )

    voltage = Instrument.measurement(
        "e", """Measure the output voltage in V.""",
        cast=int,
        values_kwargs={'reply_length': 4},
    )

    current = Instrument.measurement(
        "f", """Measure the output current in mA.""",
        cast=int,
        values_kwargs={'reply_length': 4},
    )

    remaining_deposition_time_min = Instrument.measurement(
        "k", """Get the minutes part of remaining deposition time.""",
        cast=int,
        values_kwargs={'reply_length': 3},
    )

    remaining_deposition_time_sec = Instrument.measurement(
        "l", """Get the seconds part of remaining deposition time.""",
        cast=int,
        values_kwargs={'reply_length': 2},
    )

    fault_code = Instrument.measurement(
        "o", """Get the error code from the power supply.""",
        values_kwargs={'reply_length': 1},
    )

    shutter_state = Instrument.measurement(
        "p", """Get the status of the gun shutters. 0 for closed and 1 for open shutters.""",
        values_kwargs={'reply_length': 1},
        cast=lambda x: int.from_bytes(x.encode(), "big"),
        get_process=lambda x: [x & 1, x & 2, x & 4, x & 8, x & 16],
    )

    enabled = Instrument.control(
        "a", "%s", """Control the on/off state of the power supply""",
        values_kwargs={'reply_length': 1},
        validator=strict_discrete_set,
        map_values=True,
        cast=int,
        get_process=lambda c: "A" if c == 1 else "B",
        values={True: "A", False: "B"},
    )

    setpoint = Instrument.control(
        "b", "C%04d",
        """Control the setpoint value. Units are determined by regulation mode
           (power -> W, voltage -> V, current -> mA).""",
        values_kwargs={'reply_length': 4},
        validator=strict_range,
        map_values=True,
        values=range(0, 1001),
    )

    regulation_mode = Instrument.control(
        "c", "D%d",
        """Control the regulation mode of the power supply.""",
        values_kwargs={'reply_length': 1},
        validator=strict_discrete_set,
        map_values=True,
        values={"power": 0,
                "voltage": 1,
                "current": 2,
                },
    )

    ramp_time = Instrument.control(
        "g", "E%02d",
        """Control the ramp time in seconds. Can be set only when 'enabled' is False.""",
        values_kwargs={'reply_length': 2},
        cast=int,
        validator=strict_range,
        values=range(100),
    )

    shutter_delay = Instrument.control(
        "h", "F%02d",
        """Control the shutter delay in seconds. Can be set only when 'enabled' is False.""",
        values_kwargs={'reply_length': 2},
        cast=int,
        validator=strict_range,
        values=range(100),
    )

    deposition_time_min = Instrument.control(
        "i", "G%03d",
        """Control the minutes part of deposition time. Can be set only when 'enabled' is False.""",
        values_kwargs={'reply_length': 3},
        cast=int,
        validator=strict_range,
        values=range(1000),
    )

    deposition_time_sec = Instrument.control(
        "j", "H%02d",
        """Control the seconds part of deposition time. Can be set only when 'enabled' is False.""",
        values_kwargs={'reply_length': 2},
        cast=int,
        validator=strict_range,
        values=range(60),
    )

    material = Instrument.control(
        "n", "I%08s", """Control the material name of the sputter target.""",
        cast=str,
        values_kwargs={'reply_length': 8},
        validator=lambda value, maxlength: value[:maxlength],
        values=8,
    )

    active_gun = Instrument.control(
        "y", "Z%d", """Control the active gun number.""",
        cast=int,
        values_kwargs={'reply_length': 1},
        validator=strict_range,
        values=range(1, 6),
    )
