#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from enum import IntEnum

from pymeasure.instruments import Instrument

#%%
class DG645(Instrument):
    """
    Communicates with a Stanford Research Systems DG645 digital delay generator,
    using the SCPI commands documented in the `user's guide`.

    """
    
    def __init__(self, adapter, name="DG", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.address = adapter
        self.name = name
        
    #%% ENUMS

    class LevelPolarity(IntEnum):
        """
        Polarities for output levels.
        """

        positive = 1
        negative = 0

    class Outputs(IntEnum):
        """
        Enumeration of valid outputs from the DG.
        """

        T0 = 0
        AB = 1
        CD = 2
        EF = 3
        GH = 4

    class Channels(IntEnum):
        """
        Enumeration of valid delay channels for the DG.
        """

        T0 = 0
        T1 = 1
        A = 2
        B = 3
        C = 4
        D = 5
        E = 6
        F = 7
        G = 8
        H = 9

    class DisplayMode(IntEnum):
        """
        Enumeration of possible modes for the physical front-panel display.
        """

        trigger_rate = 0
        trigger_threshold = 1
        trigger_single_shot = 2
        trigger_line = 3
        adv_triggering_enable = 4
        trigger_holdoff = 5
        prescale_config = 6
        burst_mode = 7
        burst_delay = 8
        burst_count = 9
        burst_period = 10
        channel_delay = 11
        channel_levels = 12
        channel_polarity = 13
        burst_T0_config = 14

    class TriggerSource(IntEnum):
        """
        Enumeration of the different allowed trigger sources and modes.
        """

        internal = 0
        external_rising = 1
        external_falling = 2
        ss_external_rising = 3
        ss_external_falling = 4
        single_shot = 5
        line = 6
        Class representing a sensor attached to the SRS DG644.

        .. warning:: This class should NOT be manually created by the user. It is
            designed to be initialized by the `DG644` class.
        """

        # Initializer
        def __init__(self, parent, chan):
            if not isinstance(parent, DG645):
                raise TypeError("Don't do that.")

            if isinstance(chan, parent.Channels):
                self._chan = chan.value
            else:
                self._chan = chan

            self._ddg = parent

        # PROPERTIES #

        @property
        def idx(self):
            """
            Gets the channel identifier number as used for communication

            :return: The communication identification number for the specified
                channel
            :rtype: `int`
            """
            return self._chan

        @property
        def delay(self):
            """
            Gets/sets the delay of this channel.
            Formatted as a two-tuple of the reference and the delay time.
            For example, ``(SRSDG644.Channels.A, u.Quantity(10, "ps"))``
            indicates a delay of 9 picoseconds from delay channel A.

            :units: Assume seconds if no units given.
            """
            resp = self._ddg.query(f"DLAY?{int(self._chan)}").split(",")
            return self._ddg.Channels(int(resp[0])), float(resp[1])

        @delay.setter
        def delay(self, newval):
            newval = (newval[0], assume_units(newval[1], u.s))
            self._ddg.sendcmd(
                "DLAY {},{},{}".format(
                    int(self._chan), int(newval[0].idx), newval[1].to("s").magnitude
                )
            )