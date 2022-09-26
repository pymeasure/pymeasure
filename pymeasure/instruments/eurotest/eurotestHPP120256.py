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
import logging
import re
import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EurotestHPP120256(Instrument):
    """ Represents the Euro Test High Voltage DC Source model HPP-120-256
    and provides a high-level for interacting with the instrument.

    .. code-block:: python

        hpp120256 = EurotestHPP120256("GPIB::1")

        hpp120256.current_limit = 2.0       # Sets up to limit the output current to 2mA
        hpp120256.voltage = 2.0             # Sets the HV voltage output to 2kV
        hpp120256.voltage_ramp = 100.0      # Sets the HV voltage output ramp to 100.0 V/s
        hpp120256.enable_kill()             # Enables the kill function
        hpp120256.enable_output()           # Enables the HV output

        for x in range(20):
            time.sleep(0.5)
            voltage_range, measured_voltage = hpp120256.measure_voltage
            current_range, measured_current = hpp120256.measure_current
            print("Voltage range: %.3f, Measured voltage: %.3f", (voltage_range, measured_voltage))
            print("Measure range: %.3f, Measured current: %.3f", (current_range, measured_current))

        hpp120256.shutdown()                # Ramps the voltage to 0 and disables output

    """


    VOLTAGE_RANGE = [0.0, 12.0]  # kVolts
    CURRENT_RANGE = [0.0, 25.0]  # mAmps
    VOLTAGE_RAMP_RANGE = [10, 3000]  # V/s

    # ET-Command set. Non SCPI commands.
    voltage = Instrument.control(
        "STATUS,U", "U,%.3fkV",
        """ A floating point property that represents the output voltage
        setting (in kV) of the HV Source in kVolts. This property can be set. 
        When this property acts as get will return a string like this:
        U, RANGE=3000V, VALUE=2.458kV, then voltage will return a tuple 
        (3000.0, 2.458) hence the convenience of the get_process.""",
        validator=strict_range,
        values=VOLTAGE_RANGE,
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )
    current_limit = Instrument.control(
        "STATUS,I", "I,%.3fmA",
        """ A floating point property that represents the output current limit setting of the
        HV Source in mAmps. This property can be set. When this property acts as get 
        will return a string like this: I, RANGE=5000mA, VALUE=1739mA, then current_limit will 
        return a tuple (5000.0, 1739.0) hence the convenience of the get_process.""",
        validator=strict_range,
        values=CURRENT_RANGE,
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )

    voltage_ramp = Instrument.control(
        "STATUS,RAMP", "RAMP,%dV/s",
        """ A integer property that represents the ramp speed of the output voltage of the
        HV Source V/s. This property can be set.  When this property acts as get 
        will return a string like this: RAMP, RANGE=3000V/s, VALUE=1000V/s, then voltage_ramp will 
        return a tuple (3000.0, 1000.0) hence the convenience of the get_process.""",
        validator=strict_range,
        values=VOLTAGE_RAMP_RANGE,
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )

    measure_voltage = Instrument.measurement(
        "STATUS,MU",
        """ Measures the actual output voltage of the HV Source in kVolts. 
        This property is a get so will return a string like this: 
        U, RANGE=3.000kV, VALUE=2.458kV, then measure_voltage will 
        return a tuple (3000.0, 2458.0) hence the convenience of the get_process.""",
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )

    measure_current = Instrument.measurement(
        "STATUS,MI",
        """ Measures the actual output current of the power supply in mAmps. 
        This property is a get so will return a string like this: 
        I, RANGE=5000mA, VALUE=1739mA, then measure_current will 
        return a tuple (5000.0, 1739.0) hence the convenience of the get_process.""",
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )

    @property
    def id(self):
        """ Returns the identification of the instrument """
        return self.ask("ID")

    def status(self):
        """ Returns the unit status which is a 16bits response where
        every bit indicates teh state of one subsystem of the HV Source."""
        return self.ask("STATUS,DI")

    def lam_status(self):
        """ Returns the LAM status which is the status of the untit from the point
        of view of the process. Fo example, as a response of asking STATUS,LAM, the HV
        voltage could response one of the messages from the next list:
            LAM,ERROR External Inhibit occurred during Kill enable
            LAM,INHIBIT External Inhibit occurred
            LAM,TRIP ERROR Software current trip occurred
            LAM,INPUT ERROR Wrong command received
            LAM,OK Status OK"""
        return self.ask("STATUS,LAM")

    def wait_for_voltage_output_set(self):
        voltage_output_setting = self.voltage[1]
        error = 10  # error of +-ten volts to enter into the voltage stable window
        voltage_output = self.measure_voltage[1]
        voltage_output_set = (voltage_output > (voltage_output_setting - error)) and \
                             (voltage_output < (voltage_output_setting + error))

        while not voltage_output_set:
            time.sleep(1) #wait for voltage output reaches the voltage output setting
            voltage_output = self.measure_voltage[1]
            voltage_output_set = (voltage_output > (voltage_output_setting - error)) and \
                                 (voltage_output < (voltage_output_setting + error))

        #if you are here is because

    def enable_output(self):
        """ Enables the output of the HV source. """
        self.write("HV,ON")

    def disable_output(self):
        """ Disables the output of the HV source. """
        self.write("HV,OFF")

    def enable_kill(self):
        """ Enables the kill function of the HV source.
         When Kill is enabled yellow led is flashing and the output
         will be shut OFF permanently without ramp if Iout > IOUTmax."""
        self.write("KILL,ENable")

    def disable_kill(self):
        """ Disables the kill function of the HV source.
         When Kill is disabled yellow led is not flashing and the output
         will NOT be shut OFF permanently if Iout > IOUTmax."""
        self.write("KILL,DISable")

    def shutdown(self):
        """
        Ramps the voltage to 0 and disables output
        """
        self.voltage = 0
        self.wait_for_voltage_output_set()
        self.disable_output()
        self.disable_kill()
        super().shutdown()

    def emergency_off(self):
        """ The output of the HV source will be switched OFF permanently and the values
        of the voltage a current settings set to zero"""
        self.write("EMCY OFF")

    # SCPI Commands
    # voltage = Instrument.control(
    #     ":READ:VOLTage?", ":VOLTage %g",
    #     """ A floating point property that represents the output voltage
    #     setting (in kV) of the HV Source in kVolts. This property can be set. """,
    #     validator=strict_range,
    #     values=VOLTAGE_RANGE
    # )
    #
    # current = Instrument.control(
    #     ":READ:CURRent?", ":CURRent %g",
    #     """ A floating point property that represents the output current setting of
    #     HV Source in mAmps. This property can be set. """,
    #     validator=strict_range,
    #     values=CURRENT_RANGE
    # )
    #
    # measure_voltage = Instrument.measurement(
    #     "MEASure:VOLTage?",
    #     """ Measures the actual output voltage of the HV Source in kVolts. """,
    # )
    #
    # measure_current = Instrument.measurement(
    #     "MEASure:CURRent?",
    #     """ Measures the actual output current of the power supply in mAmps. """,
    # )

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter, "Euro Test High Voltage DC Source model HPP-120-256", **kwargs
        )
