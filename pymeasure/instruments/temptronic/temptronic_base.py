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

"""Implementation of an interface driver for ThermoStream® (TS) Systems devices.

# Reference Document for implementation:
ATS-515/615, ATS 525/625 & ATS 535/635 ThermoStream® Systems
Interface & Applications Manual
Revision E
September, 2019

# Safety hints
In case of script error, make sure thermostream will be shut down.
This can be established by e.g. means of try, finally statements.
Another way is by polling ``error_code`` integer status flags.
No automatic safety measures are part of this driver implementation.

"""
import logging
import time
from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_range,
                                              strict_range
                                              )

from enum import IntFlag

log = logging.getLogger(__name__)  # https://docs.python.org/3/howto/logging.html#library-config
log.addHandler(logging.NullHandler())


class TemperatureStatusCode(IntFlag):
    """Temperature status enums based on ``IntFlag``

    Used in conjunction with :attr:`~.temperature_condition_status_code`.

        ======  ======
        Value   Enum
        ======  ======
        32      CYCLING_STOPPED
        16      END_OF_ALL_CYCLES
        8       END_OF_ONE_CYCLE
        4       END_OF_TEST
        2       NOT_AT_TEMPERATURE
        1       AT_TEMPERATURE
        0       NO_STATUS
        ======  ======

    """

    CYCLING_STOPPED = 32  # bit 5 -- cycling stopped("stop on fail" signal was received)
    END_OF_ALL_CYCLES = 16  # bit 4 -- end of all cycles
    END_OF_ONE_CYCLE = 8   # bit 3 -- end of one cycle
    END_OF_TEST = 4   # bit 2 -- end of test (test time has elapsed)
    NOT_AT_TEMPERATURE = 2   # bit 1 -- not at temperature
    AT_TEMPERATURE = 1   # bit 0 -- at temperature (soak time has elapsed)
    NO_STATUS = 0   # bit 0 -- no temperature status indication


class ErrorCode(IntFlag):
    """Error code enums based on ``IntFlag``.

    Used in conjunction with :attr:`~.error_code`.

        ======  ======
        Value   Enum
        ======  ======
        16384   NO_DUT_SENSOR_SELECTED
        4096    BVRAM_FAULT
        2048    NVRAM_FAULT
        1024    NO_LINE_SENSE
        512     FLOW_SENSOR_HARDWARE_ERROR
        128     INTERNAL_ERROR
        32      AIR_SENSOR_OPEN
        16      LOW_INPUT_AIR_PRESSURE
        8       LOW_FLOW
        2       AIR_OPEN_LOOP
        1       OVERHEAT
        0       OK
        ======  ======

    """
    # bit 15 – reserved
    NO_DUT_SENSOR_SELECTED = 16384  # bit 14 – no DUT sensor selected
    # bit 13 – reserved
    BVRAM_FAULT = 4096   # bit 12 – BVRAM fault
    NVRAM_FAULT = 2048   # bit 11 – NVRAM fault
    NO_LINE_SENSE = 1024   # bit 10 – No Line Sense
    FLOW_SENSOR_HARDWARE_ERROR = 512    # bit 9  – flow sensor hardware error
    # bit 8  – reserved
    INTERNAL_ERROR = 128    # bit 7  – internal error
    # bit 6  – reserved
    AIR_SENSOR_OPEN = 32     # bit 5  – air sensor open
    LOW_INPUT_AIR_PRESSURE = 16     # bit 4  – low input air pressure
    LOW_FLOW = 8      # bit 3  – low flow
    # bit 2  – reserved
    AIR_OPEN_LOOP = 2      # bit 1  – air open loop
    OVERHEAT = 1      # bit 0  – overheat
    OK = 0  # ok state


class ATSBase(SCPIUnknownMixin, Instrument):
    """The base class for Temptronic ATSXXX instruments.
    """

    def __init__(self, adapter, name="ATSBase", **kwargs):
        super().__init__(adapter, name=name, **kwargs)

    def wait_for(self, query_delay=None):
        super().wait_for(0.05 if query_delay is None else query_delay)

    remote_mode = Instrument.setting(
        "%s",
        """``True`` disables TS GUI but displays a “Return to local" switch.""",
        validator=strict_discrete_set,
        values={True: "%RM", False: r"%GL"},
        map_values=True
    )

    maximum_test_time = Instrument.control(
        "TTIM?", "TTIM %g",
        """Control maximum allowed test time (s).

        :type: float

        This prevents TS from staying at a single temperature forever.
        Valid range: 0 to 9999
        """,
        validator=truncated_range,
        values=[0, 9999]
    )

    dut_mode = Instrument.control(
        "DUTM?", "DUTM %g",
        """ ``On`` enables DUT mode, ``OFF`` enables air mode

        :type: string

        """,
        validator=strict_discrete_set,
        values={'ON': 1, 'OFF': 0},
        map_values=True
    )

    dut_type = Instrument.control(
        "DSNS?", "DSNS %g",
        """Control DUT sensor type.

        :type: string

        Possible values are:

        ======  ======
        String  Meaning
        ======  ======
        ''      no DUT
        'T'     T-DUT
        'K'     K-DUT
        ======  ======

        Warning: If in DUT mode without DUT being connected, TS flags DUT error

        """,
        validator=strict_discrete_set,
        values={None: 0, 'T': 1, 'K': 2},
        map_values=True
    )

    dut_constant = Instrument.control(
        "DUTC?", "DUTC %g",
        """Control thermal constant (default 100) of DUT.

        :type: float

        Lower values indicate lower thermal mass, higher values indicate higher
        thermal mass respectively.
        """,
        validator=truncated_range,
        values=[20, 500]
    )

    head = Instrument.control(
        "HEAD?", "HEAD %s",
        """Control TS head position.

        :type: string

        ``down``: transfer head to lower position
        ``up``:   transfer head to elevated position
        """,
        validator=strict_discrete_set,
        values={'up': 0, 'down': 1},
        map_values=True
    )

    enable_air_flow = Instrument.setting(
        "FLOW %g",
        """Set TS air flow.

        ``True`` enables air flow, ``False`` disables it

        :type: bool

        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    temperature_limit_air_low = Instrument.control(
        "LLIM?", "LLIM %g",
        """Control lower air temperature limit.

        :type: float

        Valid range between -99 to 25 (°C). Setpoints below current value cause
        “out of range” error in TS.
        """,
        validator=truncated_range,
        values=[-99, 25],
        dynamic=True
    )

    temperature_limit_air_high = Instrument.control(
        "ULIM?", "ULIM %g",
        """upper air temperature limit.

        :type: float

        Valid range between 25 to 255 (°C). Setpoints above current value cause
        “out of range” error in TS.
        """,
        validator=truncated_range,
        values=[25, 225]
    )

    temperature_limit_air_dut = Instrument.control(
        "ADMD?", "ADMD %g",
        """Air to DUT temperature limit.

        :type: float

        Allowed difference between nozzle air and DUT temperature during
        settling. Valid range between 10 to 300 °C in 1 degree increments.
        """,
        validator=truncated_range,
        values=[10, 300]
    )

    temperature_setpoint = Instrument.control(
        "SETP?", "SETP %g",
        """Set or get selected setpoint's temperature.

        :type: float

        Valid range is -99.9 to 225.0 (°C) or as indicated by
        :attr:`~.temperature_limit_air_high`
        and :attr:`~.temperature_limit_air_low`.
        Use convenience function :meth:`~ATSBase.set_temperature`
        to prevent unexpected behavior.
        """,
        validator=truncated_range,
        values=[-99.9, 225]
    )

    temperature_setpoint_window = Instrument.control(
        "WNDW?", "WNDW %g",
        """Setpoint's temperature window.

        :type: float

        Valid range is between 0.1 to 9.9 (°C). Temperature status register
        flags ``at temperature`` in case soak time elapsed while temperature
        stays in between bounds given by this value around the current setpoint.
        """,
        validator=truncated_range,
        values=[0.1, 9.9]
    )

    temperature_soak_time = Instrument.control(
        "SOAK?", "SOAK %g",
        """
        Set the soak time for the currently selected setpoint.

        :type: float

        Valid range is between  0 to 9999 (s). Lower values shorten cycle times.
        Higher values increase cycle times, but may reduce settling errors.
        See :attr:`~.temperature_setpoint_window` for further information.
        """,
        validator=truncated_range,
        values=[0.0, 9999]
    )

    temperature = Instrument.measurement(
        "TEMP?",
        """Read current temperature with 0.1 °C resolution.

        :type: float

        Temperature readings origin depends on :attr:`dut_mode` setting.
        Reading higher than 400 (°C) indicates invalidity.
        """
    )

    temperature_condition_status_code = Instrument.measurement(
        "TECR?",
        """Temperature condition status register.

        :type: :class:`.TemperatureStatusCode`
        """,
        values=[0, 255],
        get_process=lambda v: TemperatureStatusCode(int(v)),
    )

    set_point_number = Instrument.control(
        "SETN?", "SETN %g",
        """Select a setpoint to be the current setpoint.

        :type: int

        Valid range is 0 to 17 when on the Cycle screen or
        or 0 to 2 in case of operator screen (0=hot, 1=ambient, 2=cold).
        """,
        validator=truncated_range,
        values=[0, 17]
    )

    local_lockout = Instrument.setting(
        "%s",
        """``True`` disables TS GUI, ``False`` enables it.
        """,
        validator=strict_discrete_set,
        values={True: r"%LL", False: r"%GL"},
        map_values=True
    )

    auxiliary_condition_code = Instrument.measurement(
        "AUXC?",
        """Read out auxiliary condition status register.

        :type: int

        Relevant flags are:

        ======  ======
        Bit     Meaning
        ======  ======
        10      None
         9      Ramp mode
         8      Mode: 0 programming, 1 manual
         7      None
         6      TS status: 0 start-up, 1 ready
         5      Flow: 0 off, 1 on
         4      Sense mode: 0 air, 1 DUT
         3      Compressor: 0 on, 1 off (heating possible)
         2      Head: 0 lower, upper
         1      None
         0      None
        ======  ======

        Refer to chapter 4 in the manual

        """,
    )

    copy_active_setup_file = Instrument.setting(
        "CFIL %g",
        """Copy active setup file (0) to setup n (1 - 12).

        :type: int
        """,
        validator=strict_range,
        values=[1, 12]
    )

    compressor_enable = Instrument.setting(
        "COOL %g",
        """ ``True`` enables compressors, ``False`` disables it.

        :type: Boolean

        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    total_cycle_count = Instrument.control(
        "CYCC?", "CYCC %g",
        """Set or read current cycle count (1 - 9999).

        :type: int

        Sending 0 will stop cycling

        """,
        validator=truncated_range,
        values=[0, 9999]
    )

    cycling_enable = Instrument.setting(
        "CYCL %g",
        """CYCL Start/stop cycling.

        :type: bool

        cycling_enable = True  (start cycling)
        cycling_enable = False (stop cycling)
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    current_cycle_count = Instrument.measurement(
        "CYCL?",
        """Read the number of cycles to do

        :type: int

        """,
    )

    error_code = Instrument.measurement(
        "EROR?",  # it is indeed EROR
        """Read the device-specific error register (16 bits).

        :type: :class:`ErrorCode`
        """,
        get_process=lambda v: ErrorCode(int(v)),
    )

    nozzle_air_flow_rate = Instrument.measurement(
        "FLWR?",
        """Read main nozzle air flow rate in scfm.
        """
    )

    main_air_flow_rate = Instrument.measurement(
        "FLRL?",
        """Read main nozzle air flow rate in liters/sec.
        """
    )

    learn_mode = Instrument.control(
        "LRNM?", "LRNM %g",
        """Control DUT automatic tuning (learning).

        :type: bool
            ``False``: off
            ``True``:  automatic tuning on

        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0}
    )

    ramp_rate = Instrument.control(
        "RAMP?", "RAMP %g",
        """Control ramp rate (K / min).

        :type: float

        allowed values:
        nn.n: 0 to 99.9 in 0.1 K per minute steps.
        nnnn: 100 to 9999 in 1 K per minute steps.
        """,
        validator=strict_discrete_set,
        values={i/10 for i in range(1000)} | {i for i in range(100, 10000)}
    )

    dynamic_temperature_setpoint = Instrument.measurement(
        "SETD?",
        """Read the dynamic temperature setpoint.

        :type: float
        """
    )

    load_setup_file = Instrument.setting(
        "SFIL %g",
        """loads setup file SFIL.

        Valid range is between 1 to 12.

        :type: int
        """,
        validator=strict_range,
        values=[1, 12]
    )

    temperature_event_status = Instrument.measurement(
        "TESR?",
        """ temperature event status register.

        :type: :class:`.TemperatureStatusCode`

        Hint: Reading will clear register content.

        """,
    )

    air_temperature = Instrument.measurement(
        "TMPA?",
        """Read air temperature in 0.1 °C increments.

        :type: float
        """
    )

    dut_temperature = Instrument.measurement(
        "TMPD?",
        """Read DUT temperature, in 0.1 °C increments.

        :type: float

        """
    )

    mode = Instrument.measurement(
        "WHAT?",
        """Returns a string indicating what the system is doing at the time the query is processed.

        :type: string

        """,
        values={'manual': 5,
                'program': 6,
                },
        map_values=True,
        dynamic=True
    )

    def reset(self):
        """Reset (force) the System to the Operator screen.

        :returns: self

        """
        self.write("RSTO")

        return self

    def enter_cycle(self):
        """Enter Cycle by sending ``RMPC 1``.

        :returns: self

        """
        self.write("RMPC 1")

        return self

    def enter_ramp(self):
        """Enter Ramp by sending ``RMPS 0``.

        :returns: self
        """
        self.write("RMPS 0")

        return self

    def clear(self):
        """Clear device-specific errors.

        See :attr:`~.error_code` for further information.
        """
        self.write("CLER")

        return self

    def next_setpoint(self):
        """Step to the next setpoint during temperature cycling.
        """
        self.write("NEXT")

    def configure(self,
                  temp_window=1,
                  dut_type='T',
                  soak_time=30,
                  dut_constant=100,
                  temp_limit_air_low=-60,
                  temp_limit_air_high=220,
                  temp_limit_air_dut=50,
                  maximum_test_time=1000
                  ):
        """Convenience method for most relevant configuration properties.

        :param dut_type:
            string: indicating which DUT type to use
        :param soak_time:
            float: elapsed time in soak_window before settling is indicated
        :param soak_window:
            float: Soak window size or temperature settlings bounds (K)
        :param dut_constant:
            float: time constant of DUT, higher values indicate higher thermal mass
        :param temp_limit_air_low:
            float: minimum flow temperature limit (°C)
        :param temp_limit_air_high:
            float: maximum flow temperature limit (°C)
        :param temp_limit_air_dut:
            float: allowed temperature difference (K) between DUT and Flow
        :param maximum_test_time:
            float: maximum test time (seconds) for a single temperature point (safety)

        :returns: self
        """

        self.temperature_setpoint_window = temp_window

        self.temperature_limit_air_low = temp_limit_air_low

        self.temperature_limit_air_high = temp_limit_air_high

        self.dut_type = dut_type

        self.maximum_test_time = maximum_test_time

        if dut_type is None:
            self.dut_mode = 'OFF'
        else:
            self.dut_constant = dut_constant
            self.dut_mode = 'ON'

        self.temperature_limit_air_dut = temp_limit_air_dut

        self.temperature_soak_time = soak_time

        # logging:

        wd = self.temperature_setpoint_window

        airflwlimlow = self.temperature_limit_air_low

        airflwlimhigh = self.temperature_limit_air_high

        dut = self.dut_type

        tst_time = self.maximum_test_time

        airdutlim = self.temperature_limit_air_dut

        sktime = self.temperature_soak_time

        message = (
            "Configuring TS finished, reading back:\n"
            f"DUT type: {dut}\n"
            f"Temperature Window: {wd} K\n"
            f"Maximum test time: {tst_time} s\n"
            f"Air flow temperature limit low: {airflwlimlow:.1f} K\n"
            f"Air flow temperature limit high: {airflwlimhigh:.1f} K\n"
            f"Air to DUT temperature limit: {airdutlim} degC\n"
            f"Soak time {sktime} s\n"
        )

        log.info(message)

        return self

    def set_temperature(self, set_temp):
        """sweep to a specified setpoint.

        :param set_temp:
            target temperature for DUT (float)

        :returns: self
        """
        if self.mode == 'manual':
            message = f"new set point temperature: {set_temp:.1f} Deg"
            log.info(message)

            if set_temp <= 20:
                self.set_point_number = 2  # cold
            elif set_temp < 30:
                self.set_point_number = 1  # ambient
            elif set_temp >= 30:
                self.set_point_number = 0  # hot
            else:
                raise ValueError(f"Temperature {set_temp} is impossible to set!")

        self.temperature_setpoint = set_temp  # fixed typo in attr name

        return self

    def wait_for_settling(self, time_limit=300):
        """block script execution until TS is settled.

        :param time_limit:
            set the maximum blocking time within TS has to settle (float).

        :returns: self

        Script execution is blocked until either TS has settled
        or time_limit has been exceeded (float).
        """

        time.sleep(1)
        t = 0
        t_start = time.time()
        while not self.at_temperature():  # assert at temperature
            time.sleep(1)
            t = time.time() - t_start

            tstatus = self.temperature_condition_status_code

            message = ("temp_set= %4.1f deg, "
                       "temp= %4.1f deg, "
                       "time= %.2f s, "
                       "status= %s"
                       )

            log.info(message,
                     self.temperature_setpoint,
                     self.temperature,
                     t,
                     tstatus)

            if t > time_limit:
                log.info('no settling achieved')
                break
        log.info('finished this temperature point')

        return self

    def shutdown(self, head=False):
        """Turn down TS (flow and remote operation).

        :param head: Lift head if ``True``

        :returns: self
        """

        self.enable_air_flow = 0
        self.remote_mode = False
        if head:
            self.head = 'up'
        super().shutdown()

        return self

    def start(self, enable_air_flow=True):
        """start TS in remote mode.

        :param enable_air_flow: flow starts if ``True``

        :returns: self
        """

        self.remote_mode = 1
        self.enable_air_flow = enable_air_flow  # enable TS

        return self

    def error_status(self):
        """Returns error status code (maybe used for logging).

        :returns: :class:`ErrorCode`
        """
        code = self.error_code
        if not code == 0:
            log.warning('%s', code)
        return code

    def cycling_stopped(self):
        """:returns: ``True`` if cycling has stopped.
        """
        return TemperatureStatusCode.CYCLING_STOPPED in self.temperature_condition_status_code

    def end_of_all_cycles(self):
        """:returns: ``True`` if cycling has stopped.
        """
        return TemperatureStatusCode.END_OF_ALL_CYCLES in self.temperature_condition_status_code

    def end_of_one_cycle(self):
        """:returns: ``True`` if TS is at end of one cycle.
        """
        return TemperatureStatusCode.END_OF_ONE_CYCLE in self.temperature_condition_status_code

    def end_of_test(self):
        """:returns: ``True`` if TS is at end of test.
        """
        return TemperatureStatusCode.END_OF_TEST in self.temperature_condition_status_code

    def not_at_temperature(self):
        """:returns: ``True`` if not at temperature.
        """
        return TemperatureStatusCode.NOT_AT_TEMPERATURE in self.temperature_condition_status_code

    def at_temperature(self):
        """:returns: ``True`` if at temperature.
        """
        return TemperatureStatusCode.AT_TEMPERATURE in self.temperature_condition_status_code
