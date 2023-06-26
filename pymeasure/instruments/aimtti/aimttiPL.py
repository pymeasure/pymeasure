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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class PLChannel(Channel):
    """ A channel of AimTTI PL series power supplies. """

    CURRENT_RANGE = {
        "LOW": 1,
        "HIGH": 2
    }

    def __init__(self, parent, id,
                 voltage_range: list = None,
                 current_range: list = None):
        super().__init__(parent, id)
        self.voltage_setpoint_values = voltage_range
        self.current_limit_values = current_range

    voltage_setpoint = Channel.control(
        "V{ch}?", "V{ch}V %g",
        """ Control the output voltage of this channel.
        With verify: the operation is completed when the parameter being adjusted 
        reaches the required value to within ±5% or ±10 counts.""",
        validator=strict_range,
        values=[0, 6],
        dynamic=True,
        get_process=lambda x: float(x[3:])
        )

    current_limit = Channel.control(
        "I{ch}?", "I{ch} %g",
        """ A floating point property that controls the current limit in Amps.""",
        validator=strict_range,
        values=[0, 1.5],
        dynamic=True,
        get_process=lambda x: float(x[3:])
        )

    voltage = Channel.measurement(
        "V{ch}O?",
        """ Read the output readback voltage for this output channel in Volts.""",
        get_process=lambda x: float(x[:-1])
        )

    current = Channel.measurement(
        "I{ch}O?",
        """ Read the output readback current for this output channel in Amps.""",
        get_process=lambda x: float(x[:-1])
        )

    current_range = Channel.control(
        "IRANGE{ch}?", "IRANGE{ch} %g",
        """ A string property that sets the current range of the channel. 
        Low (500/800mA) range, or High range. 
        Output must be switched off before changing range.""",
        validator=strict_discrete_set,
        values=CURRENT_RANGE,
        map_values=True
        )

    def enable(self):
        """ Enables the output."""
        self.write("OP{ch} 1")

    def disable(self):
        """ Disables the output."""
        self.write("OP{ch} 0")

    def voltage_range(self):
        return self.voltage_range


class PLBase(Instrument):
    """ Control AimTTI PL series power supplies. Model number ending with -P or P(G) support this remote interface."""

    chs = Instrument.ChannelCreator(PLChannel, ("1", "2"), prefix="ch", voltage_range=[0, 30], current_range=[0, 3])
    """ Channels of the power supply. The channels are number from right-to-left, starting at 1. 
    Default values are for the voltage and current range are for the PL303MQD-P."""

    def __init__(self, adapter, name="AimTTI PL", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def enable(self):
        """ Simultaneously sets all outputs on."""
        self.write("OPALL 1")

    def disable(self):
        """ Simultaneously sets all outputs off."""
        self.write("OPALL 0")

    def local(self):
        """ Go to local."""
        self.write("LOCAL")


class PL068P(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, "1", prefix="ch", voltage_range=[0, 6], current_range=[0, 8])

    def __init__(self, adapter, name="AimTTI PL068-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL155P(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, "1", prefix="ch", voltage_range=[0, 15], current_range=[0, 5])

    def __init__(self, adapter, name="AimTTI PL145-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303P(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, "1", prefix="ch", voltage_range=[0, 30], current_range=[0, 3])

    def __init__(self, adapter, name="AimTTI PL303-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL601P(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, "1", prefix="ch", voltage_range=[0, 60], current_range=[0, 1.5])

    def __init__(self, adapter, name="AimTTI PL303MQT-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303MQDP(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, ("1", "2"), prefix="ch", voltage_range=[0, 30], current_range=[0, 3])

    def __init__(self, adapter, name="AimTTI PL303MQD-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303MQTP(PLBase):

    chs = Instrument.ChannelCreator(PLChannel, ("1", "2", "3"), prefix="ch", voltage_range=[0, 30], current_range=[0, 3])

    def __init__(self, adapter, name="AimTTI PL303MQT-P", **kwargs):
        super().__init__(adapter, name, **kwargs)
