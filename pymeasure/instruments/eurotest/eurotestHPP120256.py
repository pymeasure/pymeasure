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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EurotestHPP120256(Instrument):
    """ Represents the Euro Test High Voltage DC Source model HPP-120-256
    and provides a high-level for interacting with the instrument.

    .. code-block:: python

        hpp120256 = EurotestHPP120256("GPIB::1")

        yoko.apply_current()                # Sets up to source current
        yoko.source_current_range = 10e-3   # Sets the current range to 10 mA
        yoko.compliance_voltage = 10        # Sets the compliance voltage to 10 V
        yoko.source_current = 0             # Sets the source current to 0 mA

        yoko.enable_source()                # Enables the current output
        yoko.ramp_to_current(5e-3)          # Ramps the current to 5 mA

        hpp120256.shutdown()                     # Ramps the current to 0 mA and disables output

    """

    VOLTAGE_RANGE = [0.0, 12.0]  # kVolts
    CURRENT_RANGE = [0.0, 25.0]  # mAmps
    VOLTAGE_RAMP_RANGE = [10, 3000]  # V/s

    # TODO: Crear post proces para extraer los parametros de lectura del string que devuelve la fuente \
    #  por ejemplo measure_current devuelve algo así IM, RANGE=5000mA, VALUE=1739mA y debemos devolver\
    #  una tupla (5000,1739)

    # ET-Command set. Non SCPI commands.
    voltage = Instrument.control(
        "STATUS,U", "U,%.3fkV",
        """ A floating point property that represents the output voltage
        setting (in kV) of the HV Source in kVolts. This property can be set. 
        When this property acts as get will return a string like this:
        U, RANGE=3000V, VALUE=2.458kV, then voltage will return a tuple 
        (3000.0, 2.458) hence the convenience of the get_process""",
        validator=strict_range,
        values=VOLTAGE_RANGE,
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )
    current = Instrument.control(
        "STATUS,I", "I,%.3fmA",
        """ A floating point property that represents the output current setting of the
        HV Source in mAmps. This property can be set. """,
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
        HV Source V/s. This property can be set. """,
        validator=strict_range,
        values=VOLTAGE_RAMP_RANGE,
        get_process=lambda v: (
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[1])[0]),
            float(re.findall(r'[+-]?\d+\.?\d+', v.split(",")[2])[0])
        )
    )

    measure_voltage = Instrument.measurement(
        "STATUS,MU",
        """ Measures the actual output voltage of the HV Source in kVolts. """,
    )

    measure_current = Instrument.measurement(
        "STATUS,MI",
        """ Measures the actual output current of the power supply in mAmps. """,
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
