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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from time import sleep
from enum import IntFlag


class Thermotron3800(Instrument):
    """ Represents the Thermotron 3800 Oven.
    For now, this driver only supports using Control Channel 1.
    There is a 1000ms built in wait time after all write commands.
    """

    def __init__(self, adapter, name="Thermotron 3800", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )

    def write(self, command):
        super().write(command)
        # Insert wait time after sending command.
        # This wait time should be >1000ms for consistent results.
        sleep(1)

    id = Instrument.measurement(
        "IDEN?", """ Reads the instrument identification

        :return: String
        """
    )

    temperature = Instrument.measurement(
        "PVAR1?", """ Reads the current temperature of the oven
        via built in thermocouple. Default unit is Celsius, unless
        changed by the user.

        :return: float
        """
    )

    mode = Instrument.measurement(
        "MODE?", """ Gets the operating mode of the oven.

        :return: Tuple(String, int)
        """,
        get_process=lambda mode: Thermotron3800.__translate_mode(mode)
    )

    setpoint = Instrument.control(
        "SETP1?", "SETP1,%g",
        """ A floating point property that controls the setpoint
        of the oven in Celsius. This property can be set.
        "setpoint" will not update until the "run()" command is called.
        After setpoint is set to a new value, the "run()" command
        must be called to tell the oven to run to the new temperature.

        :return: None
        """,
        validator=strict_range,
        values=[-55, 150]
    )

    def run(self):
        '''
        Starts temperature forcing. The oven will ramp to the setpoint.

        :return: None
        '''
        self.write("RUNM")

    def stop(self):
        '''
        Stops temperature forcing on the oven.

        :return: None
        '''
        self.write("STOP")

    def initalize_oven(self, wait=True):
        '''
        The manufacturer recommends a 3 second wait time after after initializing the oven.
        The optional "wait" variable should remain true, unless the 3 second wait time is
        taken care of on the user end. The wait time is split up in the following way:
        1 second (built into the write function) +
        2 seconds (optional wait time from this function (initialize_oven)).

        :return: None
        '''
        self.write("INIT")
        if wait:
            sleep(2)

    class Thermotron3800Mode(IntFlag):
        """
        +--------+--------------------------------------+
        | Bit    | Mode                                 |
        +========+======================================+
        | 0      | Program mode                         |
        +--------+--------------------------------------+
        | 1      | Edit mode (controller in stop mode)  |
        +--------+--------------------------------------+
        | 2      | View program mode                    |
        +--------+--------------------------------------+
        | 3      | Edit mode (controller in hold mode)  |
        +--------+--------------------------------------+
        | 4      | Manual mode                          |
        +--------+--------------------------------------+
        | 5      | Delayed start mode                   |
        +--------+--------------------------------------+
        | 6      | Unused                               |
        +--------+--------------------------------------+
        | 7      | Calibration mode                     |
        +--------+--------------------------------------+
        """
        PROGRAM_MODE = 1
        EDIT_MODE_STOP = 2
        VIEW_PROGRAM_MODE = 4
        EDIT_MODE_HOLD = 8
        MANUAL_MODE = 16
        DELAYED_START_MODE = 32
        UNUSED = 64
        CALIBRATION_MODE = 128

    @staticmethod
    def __translate_mode(mode_coded_integer):

        mode = Thermotron3800.Thermotron3800Mode(int(mode_coded_integer))

        return mode
