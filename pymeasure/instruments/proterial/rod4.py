#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ROD4Channel(Channel):
    """ Implementation of a ROD-4 MFC channel """

    actual_flow = Instrument.measurement(
        "\020{ch}RFX",
        """ Read the actual flow in % . """
        )
    setpoint = Instrument.control(
        "\020{ch}RFD", "\020{ch}SFD%.1f",
        """A property that controls the set point in % of control range. """,
        validator=truncated_range,
        values=[0, 100],
        )
    mfc_range = Instrument.control(
        "\020{ch}RFK", "\020{ch}SFK%d",
        """An integer property that controls the MFC range in sccm.
        Upper limit is 200 slm. """,
        validator=truncated_range,
        values=[0, 200000]
        )
    ramp_time = Instrument.control(
        "\020{ch}RRT", "\020{ch}SRT%.1f",
        """A property that controls the MFC set point ramping time in seconds. """,
        validator=truncated_range,
        values=[0, 200000]
        )
    valve_mode = Instrument.control(
        "\020{ch}RVM", "\020{ch}SVM%d",
        """A property that controls the MFC valve mode.
        Valid options are `flow`, `close`, and `open`. """,
        validator=strict_discrete_set,
        values={'flow': 0, 'close': 1, 'open': 2},
        map_values=True
        )

    def __init__(self, *argv):
        self.flow_unit('sccm')
        super().__init__(*argv)

    @property
    def flow_unit(self):
        """Returns flow units for the selected channel.
        Valid options are %, sccm, or slm.
        Display in absolute units is in sccm for control range < 10 slm. """
        return self._flow_unit

    @flow_unit.setter
    def flow_unit(self, units):
        values={'%': 0, 'sccm': 1, 'slm': 1}
        if isinstance(units, str) and units.casefold() in values:
            units = units.casefold()
            self.write("\020{ch}SFU%d" %values[units])
            self._flow_unit = values[units]
        else:
            print('Units must be %, sccm, or slm.')


class ROD4(Instrument):
    """ Represents the Proterial ROD-4(A) operator for mass flow controllers
    and provides a high-level interface for interacting with the instrument.
    User must specify which channel to control (1-4).

    .. code-block:: python

        rod4 = ROD4("ASRL1::INSTR")

        print(rod4.version)                     # Print version and series number
        rod4.ch_1.mfc_range = 500               # Sets Channel 1 MFC range to 500 sccm
        rod4.ch_2.valve_mode = 'flow'           # Sets Channel 2 MFC to flow control
        rod4.ch_3.setpoint = 50                 # Sets Channel 3 MFC to flow at 50% of full range
        print(rod4.ch_4.actual_flow)            # Prints Channel 4 actual MFC flow in %

    """
    ch_1 = Instrument.ChannelCreator(ROD4Channel, 1)
    ch_2 = Instrument.ChannelCreator(ROD4Channel, 2)
    ch_3 = Instrument.ChannelCreator(ROD4Channel, 3)
    ch_4 = Instrument.ChannelCreator(ROD4Channel, 4)

    def __init__(self, adapter, name="ROD-4 MFC Controller", **kwargs):
        super().__init__(
            adapter, name, write_termination='\r', **kwargs
        )
        self.keyboard('unlocked')

    version = Instrument.measurement(
        "\0200RVN",
        """ Read version and series number. Returns x.xx<TAB>S/N """
        )

    @property
    def keyboard(self):
        """Returns front keyboard lock status. 
        Valid options are unlocked or locked. """
        return self._keyboard

    @keyboard.setter
    def keyboard(self, status):
        values={'unlocked': 0, 'locked': 1}
        if isinstance(status, str) and status.casefold() in values:
            status = status.casefold()
            self.write("\0200SKO%d" %values[status])
            self._keyboard = values[status]
        else:
            print('Status must be unlocked or locked.')
