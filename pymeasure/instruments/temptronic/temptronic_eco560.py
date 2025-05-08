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

"""
Implementation of an interface class for ThermoStream® Systems devices.
Reference Document for implementation:
ECO-560/660 ThermoStream® Systems
Operators Manual
Revision B
September, 2018
"""

from pymeasure.instruments.temptronic.temptronic_base import ATSBase
from enum import IntFlag


class ECO560ErrorCode(IntFlag):
    """Error code enums based on ``IntFlag``.

    Used in conjunction with :attr:`~.error_code`.

        ======  ======
        Value   Enum
        ======  ======
        16384   NO_DUT_SENSOR_SELECTED
        8192    IMPROPER_SOFTWARE_VERSION
        1024    PURGE_HEAT_FAILURE
        512     FLOW_SENSOR_HARDWARE_ERROR
        256     DUT_OPEN_LOOP
        128     INTERNAL_ERROR
        64      OPEN_PURGE_TEMPERATURE_SENSOR
        32      AIR_SENSOR_OPEN
        16      LOW_INPUT_AIR_PRESSURE
        8       LOW_FLOW
        4       SETPOINT_OUT_OF_RANGE
        2       AIR_OPEN_LOOP
        1       OVERHEAT
        0       OK
        ======  ======

    """
    # bit 15 - reserved
    NO_DUT_SENSOR_SELECTED = 16384      # bit 14 – no DUT sensor selected
    IMPROPER_SOFTWARE_VERSION = 8192    # bit 13 – software revision error
    # bit 12 – reserved
    # bit 11 – reserved
    PURGE_HEAT_FAILURE = 1024           # bit 10 – purge heat failure
    FLOW_SENSOR_HARDWARE_ERROR = 512    # bit 9  – flow sensor hardware error
    DUT_OPEN_LOOP = 256                 # bit 8  – dut open loop
    INTERNAL_ERROR = 128                # bit 7  – internal error
    OPEN_PURGE_TEMPERATURE_SENSOR = 64  # bit 6  – open purge temperature sensor
    NO_PURGE_FLOW = 32                  # bit 5  – no purge flow
    LOW_INPUT_AIR_PRESSURE = 16         # bit 4  – low input air pressure
    LOW_FLOW = 8                        # bit 3  – low flow
    SETPOINT_OUT_OF_RANGE = 4           # bit 2  – setpoint out of range
    AIR_OPEN_LOOP = 2                   # bit 1  – air open loop
    OVERHEAT = 1                        # bit 0  – overheat
    OK = 0                              # ok state


class ECO560(ATSBase):
    """Represent the TemptronicECO560 instruments.
    """

    temperature_limit_air_low_values = [-150, 25]

    error_code_get_process = lambda v: ECO560ErrorCode(int(v))  # noqa: E731

    copy_active_setup_file = None
    # Not Implemented in ECO-560

    def __init__(self, adapter, name="Temptronic ECO-560 Thermostream", **kwargs):
        kwargs.setdefault('timeout', 3000)
        super().__init__(
            adapter,
            name,
            tcpip={'write_termination': '\n',
                   'read_termination': '\n'},
            **kwargs
        )
