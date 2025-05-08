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

from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class PLChannel(Channel):
    """A channel of AimTTI PL series power supplies.

    Channels of the power supply. The channels are number from right-to-left, starting at 1.
    """

    def __init__(self, parent, id, voltage_range: list = None, current_range: list = None):
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
        get_process=lambda x: float(x[3:]),
    )

    current_limit = Channel.control(
        "I{ch}?", "I{ch} %g",
        """ Control the current limit in Amps.""",
        validator=strict_range,
        values=[0, 1.5],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    voltage = Channel.measurement(
        "V{ch}O?",
        """ Measure the output readback voltage for this output channel in Volts.""",
        get_process=lambda x: float(x[:-1]),
    )

    current = Channel.measurement(
        "I{ch}O?",
        """ Measure the output readback current for this output channel in Amps.""",
        get_process=lambda x: float(x[:-1]),
    )

    current_range = Channel.control(
        "IRANGE{ch}?", "IRANGE{ch} %g",
        """ Control the current range of the channel.
        Low (500/800mA) range, or High range.
        Output must be switched off before changing range.""",
        validator=strict_discrete_set,
        values={"LOW": 1, "HIGH": 2},
        map_values=True,
    )

    output_enabled = Channel.control(
        "OP{ch}?", "OP{ch} %i",
        """ Control whether the source is enabled, takes values True or False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class PLBase(SCPIUnknownMixin, Instrument):
    """Control AimTTI PL series power supplies.
    Model number ending with -P or P(G) support this remote interface.

    Documentation:
        https://resources.aimtti.com/manuals/New_PL+PL-P_Series_Instruction_Manual-Iss18.pdf
    PL-series devices:
        https://www.aimtti.com/product-category/dc-power-supplies/aim-plseries

    The default value for the timeout argument is set to 5000ms.

    .. code-block:: python

        psu = PL303QMDP("ASRL7::INSTR")
        psu.reset()
        psu.ch_2.voltage = 1.2
        psu.ch_2.output_enabled = True
        ...
        psu.ch_2.output_enabled = False
        psu.local()

    """

    def __init__(self, adapter, name="AimTTI PL", **kwargs):
        kwargs.setdefault("timeout", 5000)
        super().__init__(adapter, name, **kwargs)

    all_outputs_enabled = Instrument.setting(
        "OPALL %d",
        """ Control whether all sources are enabled simultaneously, takes
        values True or False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def local(self):
        """Go to local. Make sure all output are disabled first."""
        self.write("LOCAL")


class PL068P(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 6], current_range=[0, 8]
    )

    def __init__(self, adapter, name="AimTTI PL068-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL155P(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 15], current_range=[0, 5]
    )

    def __init__(self, adapter, name="AimTTI PL155-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303P(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 30], current_range=[0, 3]
    )

    def __init__(self, adapter, name="AimTTI PL303-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL601P(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 60], current_range=[0, 1.5]
    )

    def __init__(self, adapter, name="AimTTI PL601-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303QMDP(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 30], current_range=[0, 3]
    )
    ch_2: PLChannel = Instrument.ChannelCreator(
        PLChannel, "2", voltage_range=[0, 30], current_range=[0, 3]
    )

    def __init__(self, adapter, name="AimTTI PL303QMD-P", **kwargs):
        super().__init__(adapter, name, **kwargs)


class PL303QMTP(PLBase):
    ch_1: PLChannel = Instrument.ChannelCreator(
        PLChannel, "1", voltage_range=[0, 30], current_range=[0, 3]
    )
    ch_2: PLChannel = Instrument.ChannelCreator(
        PLChannel, "2", voltage_range=[0, 30], current_range=[0, 3]
    )
    ch_3: PLChannel = Instrument.ChannelCreator(
        PLChannel, "3", voltage_range=[0, 30], current_range=[0, 3]
    )

    def __init__(self, adapter, name="AimTTI PL303QMT-P", **kwargs):
        super().__init__(adapter, name, **kwargs)
