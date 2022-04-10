#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from time import sleep

class Thermotron3800(Instrument):
    """ Represents the Thermotron 3800 Oven.
    For now, this driver only supports using Control Channel 1.
    There is a 1000ms built in wait time after all write commands.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Thermotron 3800",
            includeSCPI=False,
            **kwargs
        )

    def write(self, command):
        super().write(command)
        # Insert wait time after sending command. This wait time should be >1000ms for consistent results.
        sleep(1)

    id = Instrument.measurement(
        "IDEN?", """ Reads the instrument identification 
        
        :return: String
        """
    )

    temperature = Instrument.measurement(
        "PVAR1?", """ Reads the current temperature of the oven 
        via built in thermocouple
        
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
        Setpoint may not return the correct value until the "run" command is sent. 
        
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

    def initalize_oven(self):
        '''
        Please wait 3 seconds after calling initialize_oven before running
        any other oven commands (per manufacturer's instructions).

        :return: None
        '''
        self.write("INIT")

    @staticmethod
    def __translate_mode(mode_coded_integer):
        '''
        Bit 0 = Program mode
        Bit 1 = Edit mode (controller in stop mode)
        Bit 2 = View program mode
        Bit 3 = Edit mode (controller in hold mode)
        Bit 4 = Manual mode
        Bit 5 = Delayed start mode
        Bit 6 = Unused
        Bit 7 = Calibration mode
        '''
        map = {
            1: "Program mode",
            2: "Edit mode (controller in stop mode)",
            4: "View program mode",
            8: "Edit mode (controller in hold mode)",
            16: "Manual mode",
            32: "Delayed start mode",
            64: "Unused (Error)",
            128: "Calibration mode"
        }

        mode_coded_integer_int = int(mode_coded_integer)

        if mode_coded_integer in map:
            return tuple( (map[mode_coded_integer_int], mode_coded_integer_int) )
        else:
            return tuple( ("Unknown mode.", mode_coded_integer_int) )
