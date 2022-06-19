#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from enum import IntFlag
from time import sleep
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class HardwareErrorException(Exception):
    pass


class SpollStatus(IntFlag):
    """ IntFlag type that represents the status of the device
    """

    MEASUREMENT_READY = 1
    READY_FOR_TRIGGERING = 2
    MEASURING_START_ENABLE = 4
    MEASURING_STOP_ENABLE = 8
    GATE_OPEN = 16
    ERROR = 32
    UNUSED = 64
    UNUSED2 = 128


class MSRFlag(IntFlag):
    """ IntFlag type to build the mask that triggers an service request (SRQ). Set this via the MSR command
    """
    MEASUREMENT_READY = 1
    READY_FOR_TRIGGERING = 2
    MEASURING_START_ENABLE = 4
    MEASURING_STOP_ENABLE = 8
    PROGRAMMING_ERROR = 16
    HARDWARE_FAULT = 32
    TIME_OUT = 64
    UNUSED = 128

class PM6669(Instrument):
    """ Represents the Philips PM 6669 instrument.
    """


    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Philips PM 6669",
            **kwargs
        )
        self.write("EOI ON")

    def wait_for_measurement(self, poll_interval=1):
        s = self.spoll()
        while not (s & SpollStatus.MEASUREMENT_READY):
            sleep(poll_interval)
            s = self.spoll()
            if (s & SpollStatus.HARDWARE_FAULT):
                raise HardwareErrorException()

    def spoll(self):
        self.adapter.connection.write("++spoll\n".encode())
        return SpollStatus(int(self.adapter.connection.readlines()[0].decode()))

    def trigger(self):
        self.write("X")


PM6669.id = Instrument.measurement(
    "ID?", """ Reads the instrument identification """
)

PM6669.frequency = Instrument.measurement(
    "FREQ", "Reads the freqeuncy in Hertz",
    get_process=lambda x: float(x.split("\n")[0][5:])
)

PM6669.channel = Instrument.control(
    "FNC?", "FREQ %s", """ Sets the channel, valid values are A or B """,
    validator=strict_discrete_set,
    values=['A', 'B'],
    get_process=lambda x: x[7]
)

PM6669.measurement_time = Instrument.control(
    "MEAC?", "MTIME %g", """ Reads Measurement time""",
    validator=strict_range,
    values=[0, 10],
    get_process=lambda x:  float(x[0][5:]) if x[0].startswith("MTIME") is True else 0
)

PM6669.freerun = Instrument.control(
    "MEAC?", "FRUN %s", """ Reads the freerun settings""",
    validator=strict_discrete_set,
    values={"OFF": "OFF", "ON": "ON", True: "ON", False: "OFF"},
    get_process=lambda x:  x[1].split("\n")[0][6:] if x[0].startswith("MTIME") == True else 0
)

PM6669.timeout = Instrument.measurement(
    "MEAC?", """ Reads Measurement timeout, this timeout only has meaning when freerun is off.""",
    get_process=lambda x:  float(x[1].split("\n")[2][5:]) if x[0].startswith("MTIME") == True else 0
)

PM6669.meac = Instrument.measurement(
    "MEAC?", """ Reads the measurement settings from the device """
)

PM6669.defaults = Instrument.measurement(
    "DCL", """ Reset to instrument defaults """
)