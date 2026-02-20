#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.adapters.adapter import Adapter
from pymeasure.instruments.korad.ka_base import KoradKABase, KoradKAChannel

class KoradKA3005Channel(KoradKAChannel):
    def __init__(self, parent: "KoradKA3005P", channel: int):
        super().__init__(parent, channel)
        assert channel in [1, 2], "Channel must be either 1 or 2."
    
    voltage_setpoint_values = (0, 31.0)
    current_setpoint_values = (0, 5.1)

class KoradKA3005P(KoradKABase):
    """Represents a Korad KA3005P power supply
    and provides a high-level for interacting with the instrument
    """

    last_write_timestamp: float  # hold timestamp fo the last write for enforcing write_delay
    write_delay: float  # minimum time between writes
    ch1: KoradKA3005Channel

    def __init__(self, adapter: Adapter, name: str ="KA3005P", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ch1 = KoradKA3005Channel(self, 1)
        # assert "KORADKA3005P" in self.id
