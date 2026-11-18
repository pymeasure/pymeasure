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

from pymeasure.instruments import AdapterType, Instrument

from .eurotherm_base import EurothermBase, enum_control, float_control

BOOLEANS = {False: 0, True: 1}

OPERATING_MODES = {"auto": 0, "manual": 1}


class EurothermEPC3000(EurothermBase):
    """Eurotherm EPC3000 series (EPC3004, EPC3008, EPC3016) programmable controller.

    It communicates via Modbus TCP over Ethernet, or via Modbus RTU over a serial link.
    The register addresses follow the EPC3008 driver of
    `LNicolasOnera/pymodaq_plugins_eurotherm
    <https://github.com/LNicolasOnera/pymodaq_plugins_eurotherm>`__.

    .. code-block:: python

        from pymeasure.instruments.eurotherm import EurothermEPC3000

        controller = EurothermEPC3000("TCPIP::192.168.1.10::502::SOCKET")
        controller.setpoint_rate_limit = 20
        controller.setpoint_rate_limit_down = 20
        controller.target_setpoint = 300
        print(controller.process_value, controller.ramp_done)

    The controller accepts only a few simultaneous Modbus TCP connections:
    call ``controller.adapter.close()`` to release the connection when you are done.
    """

    def __init__(self, adapter: AdapterType, name: str = "Eurotherm EPC3000", **kwargs):
        super().__init__(adapter, name, **kwargs)

    setpoint_rate_limit = float_control(
        35,
        """Control the rising setpoint rate limit in units per :attr:`ramp_units`
        (float, 0 means no limit).""",
    )

    setpoint_rate_limit_down = float_control(
        1667,
        """Control the falling setpoint rate limit in units per :attr:`ramp_units`
        (float, 0 means no limit).""",
    )

    remote_setpoint = float_control(
        277,
        """Control the remote setpoint (float).

        Unlike :attr:`target_setpoint`, it is meant for frequently changing values. The
        remote setpoint must be enabled on the controller (``Loop.1.Setpoint.RSP_En``) and
        the loop put in remote auto mode. It must then be written at least every second,
        otherwise an alarm trips and the loop falls back to local auto mode.""",
    )

    ramp_done = Instrument.measurement(
        "I,1673",
        """Measure whether the setpoint ramp is done (bool).""",
        values=BOOLEANS,
        map_values=True,
    )

    ramp_units = Instrument.measurement(
        "I,531",
        """Measure the time unit of the setpoint rate limits (str 'secs', 'mins' or 'hours').

        It is read-only on the EPC3000, set it in the configuration of the controller.""",
        values={"secs": 0, "mins": 1, "hours": 2},
        map_values=True,
    )

    setpoint_high_limit = float_control(
        111,
        """Control the setpoint high limit (float).""",
    )

    setpoint_low_limit = float_control(
        112,
        """Control the setpoint low limit (float).""",
    )

    operating_mode = enum_control(
        273,
        """Control the operating mode (str 'auto' or 'manual').

        The controller must not be in standby to change it.""",
        values=OPERATING_MODES,
    )

    integral_hold = enum_control(
        264,
        """Control whether the integral action is held (bool).""",
        values=BOOLEANS,
    )

    standby_enabled = enum_control(
        1085,
        """Control whether the controller is forced into standby (bool).""",
        values=BOOLEANS,
    )

    execution_status = Instrument.measurement(
        "I,1088",
        """Measure the execution status (str 'working', 'standby' or 'startup').""",
        values={"working": 0, "standby": 1, "startup": 2},
        map_values=True,
    )

    temperature_units = enum_control(
        516,
        """Control the temperature units (str 'C', 'F' or 'K').""",
        values={"C": 0, "F": 1, "K": 2},
    )

    input_status = Instrument.measurement(
        "I,1932",
        """Measure the status of the process value input (str 'good', 'not configured',
        'out of range', 'under range', 'hardware invalid', 'scaling', 'out' or 'bad').""",
        values={
            "good": 0,
            "not configured": 1,
            "out of range": 2,
            "under range": 3,
            "hardware invalid": 4,
            "scaling": 5,
            "out": 6,
            "bad": 7,
        },
        map_values=True,
    )

    leak_current = Instrument.measurement(
        "F,1591",
        """Measure the leak current of the current transformer input in A (float).""",
    )
