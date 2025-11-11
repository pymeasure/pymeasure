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

from pymeasure.instruments import Instrument, SCPIMixin, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


import logging
from warnings import warn

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

_VOLTAGE_RANGE = [0.0, 30]
_CURRENT_RANGE = [0.0, 3]
_TRACK_MODES = [0, 1, 2]


class GWInstekGPD2303SStatusRegister(enum.Enum):
    CH1 = {"flag": 0b10000000,
            "states": {0b0: "CC", 0b1: "CV"}}
    CH2 = {"flag": 0b01000000,
            "states": {0b0: "CC", 0b1: "CV"}}
    TRACKING = {
        "flag": 0b00110000,
            "states": {0b01: "Independent", 0b11: "Series", 0b10: "Parallel"},
    }
    BEEP = {"flag": 0b00001000,
            "states": {0b0: "Off", 0b1: "On"}}
    OUTPUT = {"flag": 0b00000100,
            "states": {0b0: "Off", 0b1: "On"}}
    BAUD = {"flag": 0b00000011,
            "states": {0b00: 115200, 0b01: 57600, 0b10: 9600}}


class GWInstekGPD230SChannel(Channel):
    current_limit = Channel.control(
        "ISET{ch}?",
        "ISET{ch}:%g",
        """Control maximum current of the power supply.""",
        get_process=lambda v: float(v.replace("A", "")),
        validator=truncated_range,
        values=_CURRENT_RANGE,
    )
    voltage_limit = Channel.control(
        "VSET{ch}?",
        "VSET{ch}:%g",
        """Control maximum voltage of the power supply.""",
        get_process=lambda v: float(v.replace("V", "")),
        validator=truncated_range,
        values=_VOLTAGE_RANGE,
    )
    current = Channel.measurement(
        "IOUT{ch}?",
        """Get the actual output current.""",
        get_process=lambda v: float(v.replace("A", "")),
    )

    voltage = Channel.measurement(
        "VOUT{ch}?",
        """Get the actual output voltage.""",
        get_process=lambda v: float(v.replace("V", "")),
    )


class GWInstekGPD230S(SCPIMixin, Instrument):
    """
    Represents the GW Instek two channel Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    The device only has a serial USB interface that is ususally set at
    a baud rate of 9600. \n

    the GPD-230s series only has two channels.

    Supported commands (as per the manual):

      - VSET<CH>:<volts>
      - VSET<CH>?
      - ISET<CH>:<amps>
      - ISET<CH>?

      - VOUT<CH>?
      - IOUT<CH>?
      - TRACK<NR1> (0=Independent, 1=Series, 2=Parallel)

      - OUT<BOOLEAN> (0=Off, 1=On)
      - LOCAL / REMOTE

      - BEEP<BOOLEAN>
      - SAV<NR1> / RCL<NR1> (memory save/recall)

      - BAUD<NR1> (0:115200, 1:57600, 2:9600)
      - *IDN? / STATUS? / ERR? / HELP?

      - SAV/RCL do not affect output state; OUT may be turned off on save/recall as safety

    .. code-block:: python

    ps.output_enabled = 1
    ps.channel_1.voltage_limit=5
    ps.channel_1.current_limit=1
    print(ps.error)
    print(ps.status)
    print(ps.channel_1.voltage)
    print(ps.channel_1.current)
    """

    channel_1 = Instrument.ChannelCreator(GWInstekGPD230SChannel, 1)
    channel_2 = Instrument.ChannelCreator(GWInstekGPD230SChannel, 2)

    def __init__(
        self,
        adapter,
        name="GW Instek GPD-2303S DC Power Supply",
        read_termination="\n",
        baud_rate=9600,
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            baud_rate=baud_rate,
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

            trailing_zeors = (flag & -flag).bit_length() - 1
            state = (flag & status_byte) >> trailing_zeors

            return_dict[name] = states.get(state, "Error")

        return return_dict

    @property
    def status(self) -> dict:
        """Get the status byte and and decode it."""
        status_byte = int(self.ask("STATUS?").strip(), 2)
        return self.decode_status_byte(status_byte)

    # remote = Instrument.setting(
    #     "REMOTE",
    #     """ Exits local mode and sets the instrument to remote mode""",
    # )

    tracking_mode = Instrument.setting(
        "TRACK%d",
        """Set the operation mode: independent, tracking series, or tracking parallel.
        NR1 0: Independent, 1: Series, 2: Parallel""",
        validator=strict_discrete_set,
        values=_TRACK_MODES,
    )

    beep_enabled = Instrument.setting(
        "BEEP%d",
        """Set beep on or off.""",
        validator=strict_discrete_set,
        values=_TRACK_MODES,
    )

    output_enabled = Instrument.setting(
        "OUT%d",
        """Control whether the source is enabled, takes values True or False. (bool)""",
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
        values=[0, 1, 2],
    )

    local = Instrument.setting(
        "LOCAL",
        """Set to exit remote mode and sets the instrument ot local mode.
        Beware, remote operation is not possible afterwards.""",
    )

    error = Instrument.measurement(
        "ERR?", """Get the error status of the instrument and returns the last error message."""
    )

    help = Instrument.measurement("HELP?", """Get the command list.""")
