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
# FITNESS FOR A PARTICULAR PURPOSE AND NON INFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import logging
import math

import re
import time

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EurotestHPP120256(Instrument):

    """ Represents the Euro Test High Voltage DC Source model HPP-120-256
    and provides a high-level interface for interacting with the instrument using the
    Euro Test command set (Not SCPI command set).

    .. code-block:: python

    hpp120256 = EurotestHPP120256("GPIB0::20::INSTR",includeSCPI=False)

    response = hpp120256.id
    print(response)
    print(hpp120256.lam_status)
    print(hpp120256.status)

    hpp120256.ramp_to_zero(100.0)

    hpp120256.voltage_ramp = 50.0  # V/s
    time.sleep(command_delay)
    hpp120256.current_limit = 2.0  # mA
    time.sleep(command_delay)
    inst.enable_kill = "ON"  # Enable over-current protection
    time.sleep(command_delay)
    inst.enable_output = "ON"
    time.sleep(1.0)  # Give time to output on

    abs_output_voltage_error = 0.02 # kV

    hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 40.0)

    # Here voltage HV output should be at 0.0 kV

    print("Setting the output voltage to 1.0kV...")
    hpp120256.voltage = 1.0  # kV

    # Now HV output should be rising to reach the 1.0kV at 50.0 V/s

    hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 40.0)

    # Here voltage HV output should be at 1.0 kV

    hpp120256.shutdown(100.0)

    hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 60.0)

    # Here voltage HV output should be at 0.0 kV

    # Now the HV voltage source is in safe state

    """

    VOLTAGE_RANGE = [0.0, 12.0]  # kVolts
    CURRENT_RANGE = [0.0, 25.0]  # mAmps
    VOLTAGE_RAMP_RANGE = [10, 3000]  # V/s
    COMMAND_DELAY = 0.2  # s

    response_encoding = "iso-8859-2"
    f_numbers_regex_pattern = r'([+-]?([\d]*\.)?[\d]+)'
    regex = re.compile(f_numbers_regex_pattern)

    def __init__(self,
                 adapter,
                 includeSCPI=False,
                 query_delay=0.3,
                 timeout=5000,
                 **kwargs):

        super().__init__(
            adapter,
            "Euro Test High Voltage DC Source model HPP-120-256",
            write_termination="\n",
            read_termination="",
            send_end=True,
            includeSCPI=includeSCPI,
            **kwargs
        )

        self.query_delay = query_delay
        self.timeout = timeout

    # ####################################
    # # EuroTest-Command set. Non SCPI commands.
    # ####################################

    voltage = Instrument.control(
        "STATUS,U", "U,%.3fkV",
        """ A floating point property that represents the output voltage
        setting (in kV) of the HV Source. This property can be set.""",
        # getter device response: "U, RANGE=3.000kV, VALUE=2.458kV"
        validator=strict_range,
        values=VOLTAGE_RANGE,
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[2]).groups()[0])
    )

    current_limit = Instrument.control(
        "STATUS,I", "I,%.3fmA",
        """ A floating point property that represents the output current limit setting (in mA)
        of the HV Source. This property can be set.""",
        # When this property acts as get, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA", then current_limit will return 1739.0,
        # hence the convenience of the get_process.
        validator=strict_range,
        values=CURRENT_RANGE,
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[2]).groups()[0])
    )

    voltage_ramp = Instrument.control(
        "STATUS,RAMP", "RAMP,%dV/s",
        """ A integer property that represents the ramp speed (V/s) of the output voltage of the
        HV Source. This property can be set.""",
        # When this property acts as get, the instrument will return a string like this:
        # "RAMP, RANGE=3000V/s, VALUE=1000V/s", then voltage_ramp will return 1000.0,
        # hence the convenience of the get_process.
        validator=strict_range,
        values=VOLTAGE_RAMP_RANGE,
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[2]).groups()[0])
    )

    measure_voltage = Instrument.measurement(
        "STATUS,MU",
        """ Measures the actual output voltage of the HV Source (kV).""",
        # This property is a get so, the instrument will return a string like this:
        # "U, RANGE=3.000kV, VALUE=2.458kV", then measure_voltage will return 2458.0,
        # hence the convenience of the get_process.
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[2]).groups()[0])
    )

    voltage_range = Instrument.measurement(
        "STATUS,MU",
        """ Returns the actual output voltage range of the HV Source (kV).""",
        # This property is a get so, the instrument will return a string like this:
        # "U, RANGE=3.000kV, VALUE=2.458kV", then voltage_range will return 3000.0,
        # hence the convenience of the get_process.
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[1]).groups()[0])
    )

    measure_current = Instrument.measurement(
        "STATUS,MI",
        """ Measures the actual output current of the power supply (mA).""",
        # This property is a get so, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA", then measure_current_range will return a 1739.0,
        # hence the convenience of the get_process."""
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[2]).groups()[0])
    )

    current_range = Instrument.measurement(
        "STATUS,MI",
        """ Measures the actual output current range of the power supply (mA).""",
        # This property is a get so, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA, then current_range will return a 5000.0,
        # hence the convenience of the get_process.
        get_process=lambda v:
        float(EurotestHPP120256.regex.search(v[1]).groups()[0])
    )

    enable_kill = Instrument.setting(
        "KILL,%s",
        """ Enables or disables the kill function of the HV source.
         When Kill is enabled yellow led is flashing and the output
         will be shut OFF permanently without ramp if Iout > IOUTmax.""",
        validator=strict_discrete_set,
        values={'ON': 'ENable', 'OFF': 'DISable', 'ENable': 'ENable', 'DISable': 'DISable',
                'EN': 'ENable', 'DIS': 'DISable'},
        map_values=True
    )

    enable_output = Instrument.setting(
        "HV,%s",
        """Enables or disables the voltage output function of the HV source.
         When output voltage is enabled green led is ON and the
         voltage_setting will be present on the output""",
        validator=strict_discrete_set,
        values={'ON': 'ON', 'OFF': 'OFF', 'ENable': 'ON', 'DISable': 'OFF',
                'EN': 'ON', 'DIS': 'OFF'},
        map_values=True
    )

    id = Instrument.measurement(
        "ID",
        """ Returns the identification of the instrument """,
        get_process=lambda v:
        v[1].encode(EurotestHPP120256.response_encoding).decode('utf-8', 'ignore')
    )

    status = Instrument.measurement(
        "STATUS,DI",
        """ Returns the unit Status which is a 16bits response where
        every bit indicates the state of one subsystem of the HV Source.""",
        # TODO: Decode the status string bit to get a more info about yhe state of the instrument
        get_process=lambda v:
        v[1].encode(EurotestHPP120256.response_encoding).decode('utf-8', 'ignore')
    )

    lam_status = Instrument.measurement(
        "STATUS,LAM",
        """ Returns the LAM status which is the status of the unit from the point
        of view of the process. Fo example, as a response of asking STATUS,LAM, the HV
        voltage could response one of the messages from the next list:
        LAM,ERROR External Inhibit occurred during Kill enable
        LAM,INHIBIT External Inhibit occurred
        LAM,TRIP ERROR Software current trip occurred
        LAM,INPUT ERROR Wrong command received
        LAM,OK Status OK""",
        get_process=lambda v:
        v[1].encode(EurotestHPP120256.response_encoding).decode('utf-8', 'ignore')
    )

    def emergency_off(self):
        """ The output of the HV source will be switched OFF permanently and the values
        of the voltage a current settings set to zero"""
        log.info("Sending emergency off command to the instrument.")

        self.write("EMCY OFF")
        time.sleep(self.COMMAND_DELAY)

    def shutdown(self, ramp):
        """
        Change the output voltage setting (V) to zero and
        the ramp speed - changing rate (V/s) of the output voltage.
        After calling shutdown, if the HV voltage output > 0
        it should drop to zero at a certain rate given by the ramp parameter.
        :param ramp: indicates the changing rate (V/s) of the voltage output
        """
        log.info(f"Executing the shutdown function with ramp: {ramp} V/s.")

        self.ramp_to_zero(ramp)
        super().shutdown()

    def ramp_to_zero(self, ramp):
        """
        Sets the voltage output setting to zero and the ramp setting
        to a value determined by the ramp parameter.
        In summary, the method conducts (ramps) the voltage output to zero
        at a determinated voltage changing rate (ramp in V/s).
        :param ramp: Is the changing rate (ramp in V/s) for the ramp setting
        """
        log.info("Executing the ramp_to_zero function with ramp: {ramp} V/s.")

        self.voltage_ramp = ramp
        time.sleep(self.COMMAND_DELAY)
        self.voltage = 0
        time.sleep(self.COMMAND_DELAY)
        self.voltage = 0
        time.sleep(self.COMMAND_DELAY)

    def wait_for_output_voltage_reached(self, abs_output_voltage_error,
                                        check_period=1.0, timeout=60.0):
        """
        Wait until HV voltage output reaches the voltage setpoint.

        Checks the voltage output every check_period seconds and raises an exception
        if the voltage output doesn't reach the voltage setting until the timeout time.
        :param abs_output_voltage_error: absolute error of +-ten volts (0.01kV) for being considered
        an output voltage reached.
        :param check_period: voltage output will be measured every check_period (seconds) time.
        :param timeout: time (seconds) give to the voltage output to reach the voltage setting.
        :return: None
        :raises: Exception if the voltage output can't reach the voltage setting
        before the timeout completes (seconds).
        """
        log.info("Executing the wait_for_output_voltage_reached function.")

        ref_time = time.time()
        future_time = ref_time + timeout

        voltage_output_setting = self.voltage
        time.sleep(self.COMMAND_DELAY)
        voltage_output = self.measure_voltage
        voltage_output_set = math.isclose(voltage_output, voltage_output_setting, rel_tol=0.0,
                                          abs_tol=abs_output_voltage_error)

        while not voltage_output_set:
            actual_time = time.time()
            log.debug(f"\tWaiting for voltage output set. "
                      f"Reading output voltage every {check_period} seconds.\n"
                      f"\tTimeout: {timeout} seconds. Elapsed time: "
                      f"{round(actual_time - ref_time, ndigits=1)} seconds.")

            time.sleep(check_period)  # wait for voltage output reaches the voltage output setting
            voltage_output = self.measure_voltage
            voltage_output_set = math.isclose(voltage_output, voltage_output_setting, rel_tol=0.0,
                                              abs_tol=abs_output_voltage_error)
            log.debug("voltage_output_valid_range: "
                      "[" + str(voltage_output_setting - abs_output_voltage_error) +
                      ", " + str(voltage_output_setting + abs_output_voltage_error) + "]")
            log.debug("voltage_output: " + str(voltage_output))
            if actual_time > future_time:
                raise TimeoutError("Timeout for wait_for_output_voltage_reached function")

        return

    def ask(self, command):
        """ Overrides Instrument ask method for including query_delay time on parent call.
        :param command: Command string to be sent to the instrument.
        :returns: String returned by the device without read_termination.
        """
        return super().ask(command, self.query_delay)
