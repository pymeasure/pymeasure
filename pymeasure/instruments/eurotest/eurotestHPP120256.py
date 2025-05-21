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

from enum import IntFlag

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EurotestHPP120256(Instrument):
    """ Represents the Euro Test High Voltage DC Source model HPP-120-256
    and provides a high-level interface for interacting with the instrument using the
    Euro Test command set (Not SCPI command set).

    .. code-block:: python

        hpp120256 = EurotestHPP120256("GPIB0::20::INSTR")

        print(hpp120256.id)
        print(hpp120256.lam_status)
        print(hpp120256.status)

        hpp120256.ramp_to_zero(100.0)

        hpp120256.voltage_ramp = 50.0  # V/s
        hpp120256.current_limit = 2.0  # mA
        inst.kill_enabled = True  # Enable over-current protection
        time.sleep(1.0)  # Give time to enable kill
        inst.output_enabled = True
        time.sleep(1.0)  # Give time to output on

        abs_output_voltage_error = 0.02 # kV

        hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 40.0)

        # Here voltage HV output should be at 0.0 kV

        print("Setting the output voltage to 1.0kV...")
        hpp120256.voltage_setpoint = 1.0  # kV

        # Now HV output should be rising to reach the 1.0kV at 50.0 V/s

        hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 40.0)

        # Here voltage HV output should be at 1.0 kV

        hpp120256.shutdown()

        hpp120256.wait_for_output_voltage_reached(abs_output_voltage_error, 1.0, 60.0)

        # Here voltage HV output should be at 0.0 kV

        inst.output_enabled = False

        # Now the HV voltage source is in safe state
    """

    VOLTAGE_RANGE = [0.0, 12.0]  # kVolts
    CURRENT_RANGE = [0.0, 25.0]  # mAmps
    VOLTAGE_RAMP_RANGE = [10, 3000]  # V/s
    COMMAND_DELAY = 0.2  # s

    response_encoding = "iso-8859-2"
    regex = re.compile(r'([+-]?([\d]*\.)?[\d]+)')

    def __init__(self,
                 adapter,
                 name="Euro Test High Voltage DC Source model HPP-120-256",
                 query_delay=0.1,
                 write_delay=0.4,
                 timeout=5000,
                 **kwargs):

        super().__init__(
            adapter,
            name,
            write_termination="\n",
            read_termination="",
            send_end=True,
            includeSCPI=False,
            timeout=timeout,
            **kwargs
        )

        self.write_delay = write_delay
        self.query_delay = query_delay
        self.last_write_timestamp = 0.0

    # ####################################
    # # EuroTest-Command set. Non SCPI commands.
    # ####################################

    voltage_setpoint = Instrument.control(
        "STATUS,U", "U,%.3fkV",
        """Control the voltage set-point in kVolts (float strictly from 0 to 12).""",
        # getter device response: "U, RANGE=3.000kV, VALUE=2.458kV"
        validator=strict_range,
        values=VOLTAGE_RANGE,
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[2].strip()).groups()[0])
    )

    current_limit = Instrument.control(
        "STATUS,I", "I,%.3fmA",
        """Control the current limit in mAmps (float strictly from 0 to 25).""",
        # When this property acts as get, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA", then current_limit will return 1739.0,
        # hence the convenience of the get_process.
        validator=strict_range,
        values=CURRENT_RANGE,
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[2].strip()).groups()[0])
    )

    voltage_ramp = Instrument.control(
        "STATUS,RAMP", "RAMP,%dV/s",
        """Control the voltage ramp in Volts/second (int strictly from 10 to 3000).""",
        # When this property acts as get, the instrument will return a string like this:
        # "RAMP, RANGE=3000V/s, VALUE=1000V/s", then voltage_ramp will return 1000.0,
        # hence the convenience of the get_process.
        validator=strict_range,
        values=VOLTAGE_RAMP_RANGE,
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[2].strip()).groups()[0])
    )

    voltage = Instrument.measurement(
        "STATUS,MU",
        """Measure the actual output voltage in kVolts (float).""",
        # This property is a get so, the instrument will return a string like this:
        # "U, RANGE=3.000kV, VALUE=2.458kV", then voltage will return 2458.0,
        # hence the convenience of the get_process.
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[2].strip()).groups()[0])
    )

    voltage_range = Instrument.measurement(
        "STATUS,MU",
        """Measure the actual output voltage range in kVolts (float).""",
        # This property is a get so, the instrument will return a string like this:
        # "U, RANGE=3.000kV, VALUE=2.458kV", then voltage_range will return 3000.0,
        # hence the convenience of the get_process.
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[1]).groups()[0])
    )

    current = Instrument.measurement(
        "STATUS,MI",
        """Measure the actual output current in mAmps (float).""",
        # This property is a get so, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA", then current will return a 1739.0,
        # hence the convenience of the get_process."""
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[2].strip()).groups()[0])
    )

    current_range = Instrument.measurement(
        "STATUS,MI",
        """Measure the actual output current range in mAmps (float).""",
        # This property is a get so, the instrument will return a string like this:
        # "I, RANGE=5000mA, VALUE=1739mA, then current_range will return a 5000.0,
        # hence the convenience of the get_process.
        get_process=lambda r:
        float(EurotestHPP120256.regex.search(r[1].strip()).groups()[0])
    )

    kill_enabled = Instrument.control(
        "STATUS,DI", "KILL,%s",
        """Control the instrument kill enable (boolean).""",
        # When Kill is enabled yellow led is flashing and the output
        # will be shut OFF permanently without ramp if Iout > IOUTmax.
        validator=strict_discrete_set,
        values={True: 'ENable', False: 'DISable'},
        map_values=True,
        get_process=lambda r:
        EurotestHPP120256.EurotestHPP120256Status(
            int(r[1].strip()[:-1].encode(EurotestHPP120256.response_encoding).
                decode('utf-8', 'ignore'), 2)
        ) == EurotestHPP120256.EurotestHPP120256Status.KILL_ENABLE
    )

    output_enabled = Instrument.control(
        "STATUS,DI", "HV,%s",
        """Control the instrument output enable (boolean).""",
        # When output voltage is enabled green led is ON and the
        # voltage_setting will be present on the output.
        validator=strict_discrete_set,
        values={True: 'ON', False: 'OFF'},
        map_values=True,
        get_process=lambda r:
        EurotestHPP120256.EurotestHPP120256Status(
            int(r[1].strip()[:-1].encode(EurotestHPP120256.response_encoding).
                decode('utf-8', 'ignore'), 2)
        ) == EurotestHPP120256.EurotestHPP120256Status.OUTPUT_ON
    )

    id = Instrument.measurement(
        "ID",
        """Get the identification of the instrument (string) """,
        get_process=lambda r:
        r[1].strip().encode(EurotestHPP120256.response_encoding).decode('utf-8', 'ignore')
    )

    status = Instrument.measurement(
        "STATUS,DI",
        """Get the instrument status (EurotestHPP120256Status).""",
        # Every bit indicates the state of one subsystem of the HV Source.
        # response DI, b15 b14 b13 b12 b11 b10 b9 b8 b7 b6 b5 b4 b3 b2 b1 b0,
        #               0                   1
        # IpErr  b15    no input error      input error
        # Ramp   b14    no ramp             ramp
        # CutOut b13    -                   emergency off
        # TpErr  b12    no trip error       trip error
        # F3     b11                reserved
        # F2     b10                reserved
        # menu1  b9     submenu off         submenu on
        # menu0  b8     menu off            menu on
        # err    b7     no error            error
        # Creg   b6     no current control  current control
        # Vreg   b5     no voltage control  voltage control
        # pol    b4     negative            positive
        # inh    b3     no ext. inhibit     external inhibit
        # local  b2     remote              local
        # kilena b1     kill disable        kill enable
        # on     b0     off                 high voltage is ON
        get_process=lambda r:
        EurotestHPP120256.EurotestHPP120256Status(
            int(r[1].strip()[:-1].encode(EurotestHPP120256.response_encoding).
                decode('utf-8', 'ignore'), 2)
        )
    )

    lam_status = Instrument.measurement(
        "STATUS,LAM",
        """Get the instrument lam status (string).""",
        # LAM status is the status of the unit from the point
        # of view of the process. Fo example, as a response of asking STATUS,LAM, the HV
        # voltage could response one of the messages from the next list:
        # LAM,ERROR External Inhibit occurred during Kill enable
        # LAM,INHIBIT External Inhibit occurred
        # LAM,TRIP ERROR Software current trip occurred
        # LAM,INPUT ERROR Wrong command received
        # LAM,OK Status OK
        get_process=lambda r:
        r[1].strip().encode(EurotestHPP120256.response_encoding).decode('utf-8', 'ignore')
    )

    def emergency_off(self):
        """ The output of the HV source will be switched OFF permanently and the values
        of the voltage and current settings set to zero"""
        log.info("Sending emergency off command to the instrument.")

        self.write("EMCY OFF")

    def shutdown(self, voltage_rate=200.0):
        """
        Change the output voltage setting (V) to zero and
        the ramp speed - voltage_rate (V/s) of the output voltage.
        After calling shutdown, if the HV voltage output > 0
        it should drop to zero at a certain rate given by the voltage_rate parameter.
        :param voltage_rate: indicates the changing rate (V/s) of the voltage output
        """
        log.info(f"Executing the shutdown function with voltage_rate: {voltage_rate} V/s.")

        self.ramp_to_zero(voltage_rate)
        super().shutdown()

    def ramp_to_zero(self, voltage_rate=200.0):
        """
        Sets the voltage output setting to zero and the ramp setting
        to a value determined by the voltage_rate parameter.
        In summary, the method conducts (ramps) the voltage output to zero
        at a determinated voltage changing rate (ramp in V/s).
        :param voltage_rate: Is the changing rate (ramp in V/s) for the ramp setting
        """
        log.info(f"Executing the ramp_to_zero function with ramp: {voltage_rate} V/s.")

        self.voltage_ramp = voltage_rate
        self.voltage_setpoint = 0

    def wait_for_output_voltage_reached(self, voltage_setpoint, abs_output_voltage_error=0.03,
                                        check_period=1.0, timeout=60.0):
        """
        Wait until HV voltage output reaches the voltage setpoint.

        Checks the voltage output every check_period seconds and raises an exception
        if the voltage output doesn't reach the voltage setting until the timeout time.
        :param voltage_setpoint: the voltage in kVolts setted in the HV power supply which
        should be present at the output after some time (depends on the ramp setting).
        :param abs_output_voltage_error: absolute error in kVolts for being considered
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

        log.debug(f"\tWaiting for voltage output set. "
                  f"Reading output voltage every {check_period} seconds.\n"
                  f"\tTimeout: {timeout} seconds.")

        while True:
            actual_time = time.time()
            time.sleep(check_period)  # wait for voltage output reaches the voltage output setting
            voltage_output = self.voltage
            # check if voltage_output is set. If so then no more wait
            if math.isclose(voltage_output, voltage_setpoint,
                            rel_tol=0.0, abs_tol=abs_output_voltage_error):
                break

            log.debug("voltage_output_valid_range: "
                      "[" + str(voltage_setpoint - abs_output_voltage_error) +
                      ", " + str(voltage_setpoint + abs_output_voltage_error) + "]")
            log.debug("voltage_output: " + str(voltage_output))
            log.debug(f"Elapsed time: {round(actual_time - ref_time, ndigits=1)} seconds.")

            if actual_time > future_time:
                self.shutdown()  # in case the voltage were applied at the output
                raise TimeoutError("Timeout for wait_for_output_voltage_reached function")

        log.info("Waiting for voltage output set done.")

    # Wrapper functions for the Adapter object
    def write(self, command, **kwargs):
        """Overrides Instrument write method for including write_delay time after the parent call.

        :param command: command string to be sent to the instrument
        """
        actual_write_delay = time.time() - self.last_write_timestamp
        time.sleep(max(0, self.write_delay - actual_write_delay))
        super().write(command, **kwargs)
        self.last_write_timestamp = time.time()

    def ask(self, command):
        """ Overrides Instrument ask method for including query_delay time on parent call.
        :param command: Command string to be sent to the instrument.
        :returns: String returned by the device without read_termination.
        """
        return super().ask(command, self.query_delay)

    class EurotestHPP120256Status(IntFlag):
        """
        Auxiliary class create for translating the instrument 16bits_status_string into
        an Enum_IntFlag that will help to the user to understand such status.
        """
        # Status response from the instrument has to be interpreted as follows:
        #
        # response DI, b15 b14 b13 b12 b11 b10 b9 b8 b7 b6 b5 b4 b3 b2 b1 b0,
        # bit = 0,1
        # IpErr  b15    no input error      input error
        # Ramp   b14    no ramp             ramp
        # CutOut b13    -                   emergency off
        # TpErr  b12    no trip error       trip error
        # F3     b11                reserved
        # F2     b10                reserved
        # menu1  b9     submenu off         submenu on
        # menu0  b8     menu off            menu on
        # err    b7     no error            error
        # Creg   b6     no current control  current control
        # Vreg   b5     no voltage control  voltage control
        # pol    b4     negative            positive
        # inh    b3     no ext. inhibit     external inhibit
        # local  b2     remote              local
        # kilena b1     kill disable        kill enable
        # on     b0     off                 high voltage is ON
        #
        # For example, a status_string = "0100000000000111" will be translated to
        # EurotestHPP120256_status.RAMP|LOCAL|KILL_ENABLE|OUTPUT_ON

        INPUT_ERROR = 32768
        RAMP = 16384
        EMERGENCY_OFF = 8192
        TRIP_ERROR = 4096
        F3 = 2048
        F2 = 1024
        SUBMENU_ON = 512
        MENU_ON = 256
        ERROR = 128
        CURRENT_CONTROL = 64
        VOLTAGE_CONTROL = 32
        POLARIZATION_POSITIVE = 16
        EXTERNAL_INHIBIT = 8
        LOCAL = 4
        KILL_ENABLE = 2
        OUTPUT_ON = 1
