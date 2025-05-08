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

import logging

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (truncated_range,
                                              strict_discrete_set)


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ROD4Channel(Channel):
    """Implementation of a ROD-4 MFC channel."""

    actual_flow = Channel.measurement(
        "\x020{ch}RFX",
        """Measure the actual flow in %."""
    )

    setpoint = Channel.control(
        "\x020{ch}RFD", "\x020{ch}SFD%.1f",
        """Control the setpoint in % of MFC range.""",
        validator=truncated_range,
        values=[0, 100],
        check_set_errors=True
    )

    mfc_range = Channel.control(
        "\x020{ch}RFK", "\x020{ch}SFK%d",
        """Control the MFC range in sccm.
        Upper limit is 200 slm.""",
        validator=truncated_range,
        values=[0, 200000],
        check_set_errors=True
    )

    ramp_time = Channel.control(
        "\x020{ch}RRT", "\x020{ch}SRT%.1f",
        """Control the MFC setpoint ramping time in seconds.""",
        validator=truncated_range,
        values=[0, 200000],
        check_set_errors=True
    )

    valve_mode = Channel.control(
        "\x020{ch}RVM", "\x020{ch}SVM%d",
        """Control the MFC valve mode.
        Valid options are `flow`, `close`, and `open`. """,
        validator=strict_discrete_set,
        values={'flow': 0, 'close': 1, 'open': 2},
        map_values=True,
        check_set_errors=True
    )

    flow_unit_display = Channel.setting(
        "\x020{ch}SFU%d",
        """Set the flow units on the front display.
        Valid options are %, sccm, or slm.
        Display in absolute units is in sccm for control range < 10 slm.""",
        validator=strict_discrete_set,
        values={'%': 0, 'sccm': 1, 'slm': 1},
        map_values=True,
        check_set_errors=True
        )


class ROD4(Instrument):
    """Represents the Proterial ROD-4(A) operator for mass flow controllers
    and provides a high-level interface for interacting with the instrument.
    User must specify which channel to control (1-4).

    .. code-block:: python

        rod4 = ROD4("ASRL1::INSTR")

        print(rod4.version)             # Print version and series number
        rod4.ch_1.mfc_range = 500       # Sets Channel 1 MFC range to 500 sccm
        rod4.ch_2.valve_mode = 'flow'   # Sets Channel 2 MFC to flow control
        rod4.ch_3.setpoint = 50         # Sets Channel 3 MFC to flow at 50% of full range
        print(rod4.ch_4.actual_flow)    # Prints Channel 4 actual MFC flow in %

    """

    def __init__(self, adapter, name="ROD-4 MFC Controller", **kwargs):
        super().__init__(
            adapter, name, read_termination='\r', write_termination='\r',
            includeSCPI=False, **kwargs
        )

    ch_1 = Instrument.ChannelCreator(ROD4Channel, 1)
    ch_2 = Instrument.ChannelCreator(ROD4Channel, 2)
    ch_3 = Instrument.ChannelCreator(ROD4Channel, 3)
    ch_4 = Instrument.ChannelCreator(ROD4Channel, 4)

    version = Instrument.measurement(
        "\x0201RVN",
        """Get the version and series number. Returns x.xx<TAB>S/N """
    )

    keyboard_locked = Instrument.setting(
        "\x0201SKO%d",
        """Set the front keyboard lock status.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True,
        check_set_errors=True
        )

    def check_set_errors(self):
        """Read 'OK' from ROD-4 after setting."""
        response = self.read()
        if response != 'OK':
            errors = ["Error setting ROD-4.",]
        else:
            errors = []
        return errors
