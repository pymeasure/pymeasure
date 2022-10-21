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

import re

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_string


class DCXS(Instrument):
    """ AJA DCXS-750 or 1500 DC magnetron sputtering power supply with multiple outputs

    Connection to the device is made through an RS232 serial connection.
    The communication settings are fixed in the device at 38400, stopbit one, parity none.
    The communication protocol of the device uses single character commands and fixed length replys,
    both without any terminator.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param kwargs: Any valid key-word argument for Instrument
    """

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault("write_termination", "")
        kwargs.setdefault("read_termination", "")
        kwargs.setdefault("asrl", dict(baud_rate=38400))
        super().__init__(
            adapter,
            "AJA DCXS sputtering power supply",
            includeSCPI=False,
            **kwargs
        )

    def ask(self, command, query_delay=0, reply_length=None):
        """ Writes the command to the instrument through the adapter
        and returns the read response.
        :param command: Command string to be sent to the instrument.
        :param query_delay: Delay between writing and reading in seconds.
        :param reply_length: number of bytes to expect in the reply. If set
            self.read_bytes is used instead of self.read.
        :returns: String returned by the device without read_termination.
        """
        self.write(command)
        self.wait_for(query_delay)
        if reply_length:
            return self.read_bytes(reply_length).decode()
        return self.read()

    def values(self, command, separator=',', cast=float, preprocess_reply=None,
               reply_length=None):
        """ Writes a command to the instrument and returns a list of formatted
        values from the result.
        :param command: SCPI command to be sent to the instrument
        :param separator: A separator character to split the string into a list
        :param cast: A type to cast the result
        :param preprocess_reply: optional callable used to preprocess values
            received from the instrument. The callable returns the processed
            string.
        :param reply_length: number of bytes to expect in the reply. If set
            self.read_bytes is used instead of self.read.
        :returns: A list of the desired type, or strings where the casting fails
        """        
        results = str(self.ask(command, reply_length=reply_length)).strip()
        if callable(preprocess_reply):
            results = preprocess_reply(results)
        results = results.split(separator)
        for i, result in enumerate(results):
            try:
                if cast == bool:
                    # Need to cast to float first since results are usually
                    # strings and bool of a non-empty string is always True
                    results[i] = bool(float(result))
                else:
                    results[i] = cast(result)
            except Exception:
                pass  # Keep as string
        return results

    id = Instrument.measurement(
        "?", """Power supply type identifier""",
        cast=str,
        reply_length=9,
    )

    software_version = Instrument.measurement(
        "z", """Software revision of the power supply firmware""",
        cast=str,
        reply_length=5,
    )

    power = Instrument.measurement(
        "d", """Actual output power in W""",
        cast=int,
        reply_length=4,
    )

    voltage = Instrument.measurement(
        "e", """Actual output voltage in V""",
        cast=int,
        reply_length=4,
    )

    current = Instrument.measurement(
        "f", """Actual output current in mA""",
        cast=int,
        reply_length=4,
    )

    remaining_deposition_time_min = Instrument.measurement(
        "k", """minutes part of remaining deposition time""",
        cast=int,
        reply_length=3,
    )

    remaining_deposition_time_sec = Instrument.measurement(
        "l", """seconds part of remaining deposition time""",
        cast=int,
        reply_length=2,
    )

    fault_code = Instrument.measurement(
        "o", """error code from the power supply""",
        reply_length=1,
    )

    shutter_state = Instrument.measurement(
        "p", """status of the gun shutters, returns 0 for closed and 1 for open shutters""",
        reply_length=1,
        cast=lambda x: int.from_bytes(x.encode(), "big"),
        get_process=lambda x: [x & 1, x & 2, x & 4, x & 8, x & 16],
    )

    enabled = Instrument.control(
        "a", "%s", """on/off state of the power supply""",
        reply_length=1,
        validator=strict_discrete_set,
        map_values=True,
        cast=int,
        get_process=lambda c: "A" if c == 1 else "B",
        values={True: "A", False: "B"},
    )

    setpoint = Instrument.control(
        "b", "C%04d", """setpoint value, units determined by regulation mode
                         (power -> W, voltage -> V, current -> mA)""",
        reply_length=4,
        validator=strict_range,
        map_values=True,
        values=range(0, 1001),
    )

    regulation_mode = Instrument.control(
        "c", "D%d", """Regulation mode of the power supply""",
        reply_length=1,
        validator=strict_discrete_set,
        map_values=True,
        values={"power": 0,
                "voltage": 1,
                "current": 2,
                },
    )

    ramp_time = Instrument.control(
        "g", "E%02d", """Ramp time in seconds, can be set only when state is False""",
        reply_length=2,
        cast=int,
        validator=strict_range,
        values=range(100),
    )

    shutter_delay = Instrument.control(
        "h", "F%02d", """shutter delay in seconds, can be set only when state is False""",
        reply_length=2,
        cast=int,
        validator=strict_range,
        values=range(100),
    )

    deposition_time_min = Instrument.control(
        "i", "G%03d", """minutes part of deposition time, can be set only when state is False""",
        reply_length=3,
        cast=int,
        validator=strict_range,
        values=range(1000),
    )

    deposition_time_sec = Instrument.control(
        "j", "H%02d", """seconds part of deposition time, can be set only when state is False""",
        reply_length=2,
        cast=int,
        validator=strict_range,
        values=range(60),
    )

    material = Instrument.control(
        "n", "I%08s", """material name of the sputter target""",
        cast=str,
        reply_length=8,
        validator=truncated_string,
        values=8,
    )

    active_gun = Instrument.control(
        "y", "Z%d", """select active gun number""",
        cast=int,
        reply_length=1,
        validator=strict_range,
        values=range(1, 6),
    )