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
import enum

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, truncated_range


_VOLTAGE_RANGE = [0.0, 30]
_CURRENT_RANGE = [0.0, 3]

class TRACK_MODE(enum.Enum):
    INDEPENDENT = 0
    SERIES = 1
    PARALLEL = 2

class BAUD_RATE(enum.Enum):
    BAUD_115200 = 0
    BAUD_57600 = 1
    BAUD_9600 = 2


class GWInstekGPD2303SStatusRegister(enum.Enum):
    CH1 = {"flag": 0b10000000, "states": {0b0: "CC", 0b1: "CV"}}
    CH2 = {"flag": 0b01000000, "states": {0b0: "CC", 0b1: "CV"}}
    TRACKING = {
        "flag": 0b00110000,
        "states": {0b01: "Independent", 0b11: "Series", 0b10: "Parallel"},
    }
    BEEP = {"flag": 0b00001000, "states": {0b0: "Off", 0b1: "On"}}
    OUTPUT = {"flag": 0b00000100, "states": {0b0: "Off", 0b1: "On"}}
    BAUD = {"flag": 0b00000011, "states": {0b00: 115200, 0b01: 57600, 0b10: 9600}}


class GWInstekGPD230SChannel(Channel):
    current_limit = Channel.control(
        "ISET{ch}?",
        "ISET{ch}:%g",
        """Control maximum current [A] of the power supply.""",
        get_process=lambda v: float(v.replace("A", "")),
        set_process=lambda v: round(v, 3),
        validator=truncated_range,
        values=_CURRENT_RANGE,
    )

    voltage_limit = Channel.control(
        "VSET{ch}?",
        "VSET{ch}:%g",
        """Control maximum voltage [V] of the power supply.""",
        get_process=lambda v: float(v.replace("V", "")),
        set_process=lambda v: round(v, 3),
        validator=truncated_range,
        values=_VOLTAGE_RANGE,
    )

    current = Channel.measurement(
        "IOUT{ch}?",
        """Get the actual output current [A].""",
        get_process=lambda v: float(v.replace("A", "")),
    )

    voltage = Channel.measurement(
        "VOUT{ch}?",
        """Get the actual output voltage [V].""",
        get_process=lambda v: float(v.replace("V", "")),
    )


class GWInstekGPD230S(Instrument):
    """
    Represents the GW Instek two channel Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.
    The device only has a serial USB interface that is usually set at
    a baud rate of 9600. The GPD-230s series only has two channels.

    Known issue:
    - When the instrument throws an error, it is best to flush the read buffer with
    `ps.adapter.flush_read_buffer()`.
    -  The`REMOTE` command is not implemented, as it does not have any effect. It
    does not work, when the instrument is already in local mode.
    """

    channel_1 = Instrument.ChannelCreator(GWInstekGPD230SChannel, 1)
    channel_2 = Instrument.ChannelCreator(GWInstekGPD230SChannel, 2)

    def __init__(
        self,
        adapter,
        name="GW Instek GPD-2303S DC Power Supply",
        baud_rate=9600,
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            read_termination="\n",
            baud_rate=baud_rate,
            includeSCPI=False,
            **kwargs,
        )

    @staticmethod
    def decode_status_byte(status_byte: int) -> dict:
        """Decode the status byte according to manual."""
        if type(status_byte) is not int:
            raise (
                ValueError((f"status_byte {status_byte} is not type int but {type(status_byte)}"))
            )
        return_dict = {}
        return_dict["raw"] = bin(status_byte)
        for register in GWInstekGPD2303SStatusRegister:
            name = register.name
            flag = register.value["flag"]
            states = register.value["states"]

            trailing_zeros = (flag & -flag).bit_length() - 1
            state = (flag & status_byte) >> trailing_zeros

            return_dict[name] = states.get(state, "Error")

        return return_dict

    @property
    def status(self) -> dict:
        """Get the status byte and and decode it."""
        status_byte = int(self.ask("STATUS?").strip(), 2)
        return self.decode_status_byte(status_byte)

    tracking_mode = Instrument.setting(
        "TRACK%d",
        """Set the operation mode: independent, tracking series, or tracking parallel.
        NR1 0: Independent, 1: Series, 2: Parallel""",
        validator=strict_discrete_set,
        values=TRACK_MODE,
        map_values=True,
    )

    beep_enabled = Instrument.setting(
        "BEEP%d",
        """Set beep on or off.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    output_enabled = Instrument.setting(
        "OUT%d",
        """Control whether the source is enabled. (bool)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    recall = Instrument.setting(
        "RCL%d",
        """Set to recall a panel setting""",
        validator=strict_discrete_set,
        values=[1, 2, 3, 4],
    )

    baude_rate = Instrument.setting(
        "BAUD%d",
        """Set the baud rate to 2:9600, 1:57600, 0:115200""",
        validator=strict_discrete_set,
        values=BAUD_RATE,
        map_values=True,
    )

    error = Instrument.measurement(
        "ERR?", """Get the error status of the instrument and returns the last error message."""
    )

    help = Instrument.measurement("HELP?", """Get the command list.""")

    def disable_remote(self):
        """Set to exit remote mode and sets the instrument ot local mode.
        Beware, remote operation is not possible afterwards."""
        self.write("LOCAL")