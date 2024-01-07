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
from pymeasure.adapters import Adapter
from enum import StrEnum
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class SHRC203Errors(Enum):
    """
    IntFlag type to decode error register queries. Error codes are as follows:
    0 ~ 1FFFFFF(Hexadecimal number)
    1bit: Normal (S1 to S10 and emergency stop has not occurred)
    2bit: Command error
    3bit: Scale error (S1)
    4bit: Disconnection error (S2)
    5bit: Overflow error (S4)
    6bit: Emergency stop
    7bit: Hunting error (S3)
    8bit: Limit error (S5)
    9bit: Counter overflow (S6)
    10bit: Auto config error
    11bit: 24V IO overload warning (W1)
    12bit: 24V terminal block overload warning (W2)
    13bit: System error (S7)
    14bit: Motor driver overheat warning (W3)
    15bit: Motor driver overheat error (S10)
    16bit: Out of in-position range   (after positioning is completed) (READY)
    17bit: Out of in-position range (During positioning operation) (BUSY)
    18bit: Logical origin return is in progress
    19bit: Mechanical origin return is in progress
    20bit: CW limit detection
    21bit: CCW limit detection
    22bit: CW software limit stop
    23bit: CCW software limit stop
    24bit: NEAR sensor detection
    25bit: ORG sensor detection
    """

    NO_ERR = "1"
    CMD_ERR = "3"
    SCALE_ERR = "7"
    DISCONN_ERR = "F"
    OVERFLOW_ERR = "1F"
    EMERGENCY_STOP = "3F"
    HUNTING_ERR = "7F"
    LIMIT_ERR = "FF"
    COUNTER_OVERFLOW = "1FF"
    AUTO_CONFIG_ERR = "3FF"
    IO_OVERLOAD_WARNING = "7FF"
    TERMINAL_OVERLOAD_WARNING = "FFF"
    SYSTEM_ERR = "1FFF"
    DRIVER_OVERHEAT_WARNING = "3FFF"
    DRIVER_OVERHEAT_ERR = "7FFF"
    OUT_OF_RANGE_READY = "FFFF"
    OUT_OF_RANGE_BUSY = "1FFFF"
    LOGICAL_ORIGIN_RETURN = "3FFFF"
    MECHANICAL_ORIGIN_RETURN = "7FFFF"
    CW_LIMIT_DETECTION = "FFFFF"
    CCW_LIMIT_DETECTION = "1FFFFF"
    CW_SOFTWARE_LIMIT_STOP = "3FFFFF"
    CCW_SOFTWARE_LIMIT_STOP = "7FFFFF"
    NEAR_SENSOR_DETECTION = "FFFFFF"
    ORG_SENSOR_DETECTION = "1FFFFFF"


class SHRC203(Instrument):
    """
    Represents the OptoSigma SHRC203 three-axis controller and provides a
    high-level interface for interacting with the instrument.
    
    :param adapter: The VISA resource name of the controller
    :param name: The name of the controller
    :param kwargs: Any valid key-word argument for VISAAdapter
    """

    # TODO: correct values, {axis}
    speed = Instument.control("?D:{axis}", "D:{axis} {value}", "docs", validator=truncated_range, values=[0, 10000], units="mm/s")

    # TODO: correct values
    division = Instrument.control("","","docs", validator=strict_discrete_set, values=[1, 2, 5, 10, 20, 50, 100, 200, 500, 1000])


    def __init__(self,
                 adapter,
                 name="OptoSigma SHRC-203 Stage Controller",
                 **kwargs
                 ):

        super().__init__(
            adapter,
            name,
            **kwargs
        )


    def home(self):
        """
        Perform mechanical origin return.
        """
        self.write("H")

    def move(self, axis, position):
        """
        Move the stage to the specified position.
        """
        self.write

    def wait_for(self, query_delay=0):
        """

        """

    def speed(self, ):
        """

        """