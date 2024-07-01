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

from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class CPXChannel(Channel):
    """A channel of AimTTI CPX series power supplies.

    Channels of the power supply. The channels are number from right-to-left, starting at 1.
    """

    def __init__(self, parent, id, voltage_range: list = None, current_range: list = None):
        super().__init__(parent, id)
        self.voltage_setpoint_values = voltage_range
        self.current_limit_values = current_range

    # Set points
    voltage_setpoint = Channel.control(
        "V{ch}?", "V{ch}V %g",
        """ Control the output voltage of this channel.
        With verify: the operation is completed when the parameter being adjusted
        reaches the required value to within ±5% or ±10 counts.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    current_limit = Channel.control(
        "I{ch}?", "I{ch} %g",
        """ Control the current limit in Amps.""",
        validator=strict_range,
        values=[0, 20],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    # Protections
    overvoltage_protection = Channel.control(
        "OVP{ch}?", "OVP{ch} %g",
        """ Control the overvoltage of this channel.
        With verify: the operation is completed when the parameter being adjusted
        reaches the required value to within ±5% or ±10 counts.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    overcurrent_protection = Channel.control(
        "OCP{ch}?", "OCP{ch} %g",
        """ Control the overvoltage of this channel.
        With verify: the operation is completed when the parameter being adjusted
        reaches the required value to within ±5% or ±10 counts.""",
        validator=strict_range,
        values=[0, 20],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    # Steps
    voltage_step = Channel.control(
        "DELTAV{ch}?", "DELTAV{ch} %g",
        """ Control the voltage step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    inc_voltage_step = Channel.control(
        "INCV{ch}?", "INCV{ch} %g",
        """ Increment the voltage step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    dec_voltage_step = Channel.control(
        "DECV{ch}?", "DECV{ch} %g",
        """ Decrement the voltage step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    current_step = Channel.control(
        "DELTAI{ch}?", "DELTAI{ch} %g",
        """ Control the current step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    inc_current_step = Channel.control(
        "INCI{ch}?", "INCI{ch} %g",
        """ Increment the current step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    dec_current_step = Channel.control(
        "DECI{ch}?", "DECI{ch} %g",
        """ Decrement the current step of this channel.""",
        validator=strict_range,
        values=[0, 60],
        dynamic=True,
        get_process=lambda x: float(x[3:]),
    )

    # Actual mesurements
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

    # Output control
    output_enabled = Channel.control(
        "OP{ch}?", "OP{ch} %i",
        """ Control whether the source is enabled, takes values True or False.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class CPXBase(SCPIUnknownMixin, Instrument):
    """Control AimTTI CPX series power supplies.
    Model number ending with P support this remote interface.

    Documentation:
        https://resources.aimtti.com/manuals/CPX400D+DP_Instruction_Manual_EN_48511-1480_14.pdf
    CPX-series devices:
        https://www.aimtti.com/product-category/dc-power-supplies/aim-cpxseries

    The default value for the timeout argument is set to 5000ms.

    .. code-block:: python

        psu = CPX400DP("ASRL4::INSTR")
        psu.reset()
        psu.ch_2.voltage_setpoint = 1.2
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

    query_and_clear_errors = Instrument.measurement(
        "QER?",
        """Query and clear Query Error Register. The response format is nr1<RMT>""",
        cast=str,
    )

    def trip_reset(self):
        """Trip reset."""
        self.write("TRIPRST")

    def local(self):
        """Go to local. Make sure all output are disabled first."""
        self.write("LOCAL")

class CPX400DP(CPXBase):
    ch_1: CPXChannel = Instrument.ChannelCreator(
        CPXChannel, "1", voltage_range=[0, 60], current_range=[0, 20]
    )
    ch_2: CPXChannel = Instrument.ChannelCreator(
        CPXChannel, "2", voltage_range=[0, 60], current_range=[0, 20]
    )

    def __init__(self, adapter, name="AimTTI CPX400DP", **kwargs):
        super().__init__(adapter, name, **kwargs)

