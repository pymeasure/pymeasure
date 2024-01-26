from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from enum import IntEnum, IntFlag

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MeasurementUnit(IntEnum):
    """Enumeration to represent the measurement unit the power meter will measure in"""

    WATTS = 0

    DBM = 1

    PERCENT = 2

    DB = 3


class SensorType(IntEnum):
    """Enumeration to represent the selected sensor type for the power meter"""

    #: Default (100% for all frequencies)
    DEFAULT = 0

    HP_8481A = 1

    #: HP 8482A, 8482B, 8482H
    HP_8482X = 2

    HP_8483A = 3

    HP_8481D = 4

    HP_8485A = 5

    HP_R8486A = 6

    HP_Q8486A = 7

    HP_R8486D = 8

    HP_8487A = 9


class OperatingMode(IntEnum):
    """Enumeration to represent the operating mode the power meter is currently in"""

    NORMAL = 0

    ZEROING = 6

    CALIBRATION = 8


class TriggerMode(IntEnum):
    """Enumeration to represent the trigger mode the power meter is currently in"""

    HOLD = 0

    FREE_RUNNING = 3


class GroupTriggerMode(IntEnum):
    """Enumeration to represent the group execute trigger mode the power meter is currently in"""

    IGNORE = 0

    TRIGGER_IMMEDIATE = 1

    TRIGGER_DELAY = 2


class EventStatusRegister(IntFlag):
    """Enumeration to represent the Event Status Register."""

    #: The bit is set when the power meter's LINE switch is set from STDBY to ON
    POWER_ON = 128

    #: This bit is set when an incorrect HP-IB code is sent to the power meter. For example,
    # the command “QX” is a command error.
    COMMAND_ERROR = 32

    #: This bit is set when incorrect data is sent to the power meter. For example, the command
    # “FR-3GZ” is an execution error.
    EXECUTION_ERROR = 16

    #: This bit is set true whenever a measurement error (error 1-49) occurs.
    DEVICE_DEPENDENT_ERROR = 8


Errors = {
    1: "Power meter cannot zero the sensor",
    5: "Power meter cannot calibrate sensor",
    11: "Input overload on sensor",
    15: "Sensor’s zero reference has drifted negative",
    17: "Input power on sensor is too high for current range",
    21: "Power reading over high limit",
    23: "Power reading under low limit",
    31: "No sensor connected to the input",
    33: "Both front and rear sensor inputs, have sensors connected (Option 002 or Option 003 only)",
    50: "Entered cal factor is out of range",
    51: "Entered offset is out of range",
    52: "Entered range number is out of range",
    54: "Entered recall register number is out of range",
    55: "Entered storage register number is out of range",
    56: "Entered reference cal factor is out of range",
    57: "RAM ID check failure",
    61: "Stack RAM failure",
    62: "ROM checksum failure",
    64: "RAM failure",
    65: "Analog I/O PIA Failure",
    66: "Keyboard and Display PIA Failure",
    67: "Analog-to-Digital converter Failure",
    68: "HP-IB failure",
    69: "Timer failure",
    70: "Keyboard/Display controller failure",
    71: "Keyboard data failure",
    72: "Data line to A3U26 is open.",
    73: "Keyboard/Display controller self-test failure",
    74: "Display not responding",
    75: "Digital failure",
}


class StatusMessage:
    MeasurementErrorCode = (0, 1)
    EntryErrorCode = (2, 2)
    OperatingMode = (4, 2)
    AutomaticRangeStatus = (6, 1)
    Range = (7, 1)
    # 8, 9 unused
    AutoFilterStatus = (10, 1)
    Filter = (11, 1)
    # 12, 13 unused
    LinearLogStatus = (14, 1)
    # A
    PowerRefStatus = (16, 1)
    RelativeModeStatus = (17, 1)
    TriggerMode = (18, 1)
    GroupTriggerMode = (19, 1)
    LimitsCheckingStatus = (20, 1)
    LimitsStatus = (21, 1)
    # 22 unused
    OffsetStatus = (23, 1)
    DutyCycleStatus = (24, 1)
    MeasurementUnits = (25, 1)


def _getstatus(status_type, modifier=lambda v: v):
    start_index, stop_offset = status_type
    return lambda v: modifier(int(v[start_index:start_index + stop_offset]))


class HP437B(Instrument):
    """Represents the HP437B Power Meters.

    .. note::
        Most command descriptions are taken from the document:
        'Operating Manual 437B Power Meter'
    """

    def __init__(self, adapter, name="Hewlett-Packard HP437B", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    def check_errors(self):
        errors = []
        while True:
            err = self.values("ERR?")
            # exclude upper limit and lower limit hit from real errors
            if int(err[0]) != 0 and int(err[0]) != 21 and int(err[0]) != 23:
                log.error(f"{self.name}: {err[0]}, {Errors[err[0]]}")
                errors.append(err)
            else:
                break
        return errors

    event_status = Instrument.measurement(
        "*ESR?",
        """
        Get the status byte and Master Summary Status bit.

        .. code-block:: python

            print(instr.request_service_conditions)
            StatusRegister.PowerOn|CommandError
        """,
        cast=int,
        get_process=lambda v: EventStatusRegister(v)
    )

    def activate_auto_range(self):
        """
        The power meter divides each sensor’s power range into 5 ranges of
        10 dB each. Range 1 is the most sensitive (lowest power levels), and
        Range 5 is the least sensitive (highest power levels). Range 5 can be
        less than 10 dB if the sensor’s power range is less than 50 dB. The
        range can be set either automatically or manually.
        'activate_auto_range' automatically selects the correct range for the current
        measurement.
        """
        self.write("RA")

    def calibrate(self, calibration_factor):
        """
        Calibrate a sensor to the power meter with a 'calibration_factor' in percent.
        """
        self.write("CL%.1fPCT" % calibration_factor)

    @property
    def calibration_factor(self):
        """
        Control the calibration factor of a specific power sensor at a specific input frequency.
        (A chart or table of CAL FACTOR % versus Frequency is printed on each sensor and an
        accompanying data sheet.) Calibration factor is entered in percent.
        Valid entries for 'calibration_factor' range from 1.0 to 150.0%.
        """
        self.write("KB")
        # returns CALFAC 097.9%
        display_content = self.display_output
        assert display_content[0:6] == "CALFAC"
        self.write("EX")
        return float(display_content[7:12])

    @calibration_factor.setter
    def calibration_factor(self, calibration_factor):
        values = [1.0, 150.0]
        strict_range(float(calibration_factor), values)

        self.write("KB%3.1fPCT" % float(calibration_factor))
        self.check_errors()

    display_enabled = Instrument.setting(
        "%s",
        """
        Set the display of the power meter active or inactive.
        """,
        map_values=True,
        values={True: "DE", False: "DD"}
    )

    display_all_segments_enabled = Instrument.setting(
        "%s",
        """
        Set all segments of the display of the power meter active or resume normal state.
        """,
        map_values=True,
        values={True: "DA", False: "DE"}
    )

    display_user_message = Instrument.setting(
        "DU %s",
        """
        Set a custom user message up to 12 alpha-numerical chars. If the string is empty or None
        the user message gets disabled.
        """,
        validator=lambda x, y: x if str(x).isalnum() and len(str(x)) <= 12 else str(x)[0:12],
        set_process=lambda v: str(v).upper().ljust(12)
    )

    display_output = Instrument.measurement(
        "OD",
        """
        Get the current displayed string of values of the power meter.

        .. code-block:: python

            print(instr.display_output)
            -0.23  dB REL

        """,
        cast=str
    )

    duty_cycle_enabled = Instrument.control(
        "SM", "DC%d",
        """
        Control whether the duty cycle is active or inactive. See :attr:`duty_cycle`
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.DutyCycleStatus),
        check_set_errors=True
    )

    @property
    def duty_cycle(self):
        """
        Control the duty cycle for calculation of a pulsed input signal. This function will cause
        the power meter to report the pulse power of a rectangular pulsed input signal. The
        allowable range of values for 'duty_cycle' is 0.00001 to 0.99999.

        Pulse power, as reported by the power meter, is a mathematical
        representation of the pulse power rather than an actual measurement.
        The power meter measures the average power of the pulsed input
        signal and then divides the measurement by the duty cycle value to
        obtain a pulse power reading.
        """
        self.write("DY")
        # returns DTYCY 01.000%
        display_content = self.display_output
        assert display_content[0:5] == "DTYCY"
        self.write("EX")
        return float(display_content[6:12]) / 100.0

    @duty_cycle.setter
    def duty_cycle(self, duty_cycle):
        values = [0.00001, 0.99999]
        strict_range(float(duty_cycle), values)

        self.write("DY%02.3fPCT" % (float(duty_cycle) * 100.0))
        self.check_errors()

    filter_automatic_enabled = Instrument.control(
        "SM", "%s",
        """
        Control the filter mode. By switching over from automatic to manual (true to false)
        the instrument implicitly keeps (holds) the filter value from the automatic selection.
        """,
        cast=bool,
        get_process=_getstatus(StatusMessage.AutoFilterStatus),
        set_process=lambda v: "FA" if v else "FH",
        check_set_errors=True
    )

    filter = Instrument.control(
        "SM", "FM%dEN",
        """
        Control the filter number for averaging. Setting a value implicitly enables the manual
        filter mode. Setting a value of 1 basically disables the averaging.
        """,
        values=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
        validator=strict_discrete_set,
        get_process=_getstatus(StatusMessage.Filter, (lambda x: 2 ** x)),
        check_set_errors=True
    )

    @property
    def frequency(self):
        """
        Control the frequency of the input signal. Entering a frequency causes the power meter to
        select a sensor-specific calibration factor. The allowed range of 'frequency'
        values is from 0.0001 to 999.9999 GHz with a 100 kHz resolution. The unit is Hz.
        """
        self.write("FR")
        # returns FR 000.0500GZ
        display_content = self.display_output
        assert display_content[0:2] == "FR"
        self.write("EX")

        return_value = float(display_content[3:11])
        if display_content[11:13] == "GZ":
            return_value *= 1e9
        else:
            return_value *= 1e6

        return return_value

    @frequency.setter
    def frequency(self, frequency):
        self.write("FR%08.4fGZ" % (float(frequency) / 1e9))
        self.check_errors()

    limits_enabled = Instrument.control(
        "SM", "LM%d",
        """
        Control the limits checking function to allow the power meter to monitor the
        power level at the sensor and to indicate when that power is outside
        preset limits.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.LimitsCheckingStatus),
        check_set_errors=True
    )

    @property
    def limit_high(self):
        """
        Control the upper limit for the builtin limit checking.
        """
        self.write("LH")
        # returns HI +299.999dB
        display_content = self.display_output
        assert display_content[0:2] == "HI"
        self.write("EX")
        return float(display_content[3:11])

    @limit_high.setter
    def limit_high(self, limit):
        """
        Control the upper limit for the builtin limit checking.
        """
        values = [-299.999, 299.999]
        strict_range(limit, values)

        self.write("LH%7.3fEN" % limit)
        self.check_errors()

    @property
    def limit_low(self):
        """
        Control the lower limit for the builtin limit checking.
        """
        self.write("LL")
        # returns HI +299.999dB
        display_content = self.display_output
        assert display_content[0:2] == "LO"
        self.write("EX")
        return float(display_content[3:11])

    @limit_low.setter
    def limit_low(self, limit):
        """
        Control the lower limit for the builtin limit checking.
        """
        values = [-299.999, 299.999]
        strict_range(limit, values)

        self.write("LL%7.3fEN" % limit)
        self.check_errors()

    limit_high_hit = Instrument.measurement(
        "SM",
        """
        Get if the upper limit check got triggered.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.LimitsStatus),
    )

    limit_low_hit = Instrument.measurement(
        "SM",
        """
        Get if the lower limit check got triggered.
        """,
        map_values=True,
        values={True: 2, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.LimitsStatus),
    )

    # just addressing the instrument to talk (without a query string) and read until EOI results
    # in only reading the RF power level
    power = Instrument.measurement(
        "",
        """
        Measure the power at the power sensor attached to the power meter in the corresponding unit.
        In case a measurement would be invalid the power meter responds with the value float('nan').
        """,
        get_process=lambda v: float("nan") if v == 9.0200e+40 else v

    )

    power_reference_enabled = Instrument.control(
        "SM", "OC%d",
        """
        Control the builtin reference power source 1mW @ 50 MHz.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.PowerRefStatus),
        check_set_errors=True
    )

    offset_enabled = Instrument.control(
        "SM", "OF%d",
        """
        Control the offset being applied.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.OffsetStatus),
        check_set_errors=True
    )

    @property
    def offset(self):
        """
        Control the offset applied to the measured value to compensate for
        signal gain or loss (for example, to compensate for the loss of a 10 dB
        directional coupler). Offsets are entered in dB.
        In case the :attr:`offset_enabled` is false this returns automatically 0.0
        """
        if self.offset_enabled:
            self.write("OS")
            # returns OFS +00.00 dB
            display_content = self.display_output
            assert display_content[0:3] == "OFS"
            self.write("EX")
            return float(display_content[4:10])
        else:
            return 0.0

    @offset.setter
    def offset(self, offset):
        values = [-99.99, 99.99]
        strict_range(offset, values)
        self.write("OS%5.2fEN" % offset)

    def reset(self):
        self.write("*RST")

    def clear_status_registers(self):
        self.write("*CLS")

    def preset(self):
        """
        Sets the power meter to a known state. Preset
        conditions are shown in the following table.

        .. list-table:: Preset values
            :widths: 25 25
            :header-rows: 1

            * - Parameter
              - Value/Condition
            * - Frequency
              - 50 MHz
            * - Resolution
              - 0.01 dB
            * - Duty Cylce
              - 1.000%, Off
            * - Relative
              - 0 dB, Off
            * - Power Reference
              - Off
            * - Range
              - Auto
            * - Unit
              - dBm
            * - Low Limit
              - -90.000 dBm
            * - High Limit
              - +90.000 dBm
            * - Limit Checking
              - Off
            * - Trigger Mode
              - Free Run
            * - Group Trigger Mode
              - Trigger with Delay
            * - Display Function
              - Display Enable
        """
        self.write("PR")

    relative_mode_enabled = Instrument.control(
        "SM", "RL%d",
        """
        Control the relative mode. In the relative mode the current measured power value will be
        used as reference and any further reported value from :attr:`power` will refer to this.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=_getstatus(StatusMessage.RelativeModeStatus),
        check_set_errors=True
    )

    measurement_unit = Instrument.measurement(
        "SM",
        """
        Get the measurement unit the power meter is currently reporting the power values in.

        Depends on: :attr:`relative_mode_enabled` and attr:`linear_display_enabled`

        .. code-block:: python

            instr.relative_mode_enabled = False
            instr.linear_display_enabled = True

            print(instr.measurement_unit)
            MeasurementUnit.Watts

        """,
        values=[e for e in MeasurementUnit],
        cast=int,
        get_process=_getstatus(StatusMessage.MeasurementUnits, lambda v: MeasurementUnit(v)),
    )

    linear_display_enabled = Instrument.control(
        "SM", "%s",
        """
        Control if the power meter displays or reports the power values in logarithmic or linear
        units. Set `linear_display_enabled` to 'True' to activate linear value readout.

        .. code-block:: python

            from pymeasure.instruments.hp.hp437b import LogLin

            instr.relative_mode_enabled = False
            instr.linear_display_enabled = True
        """,
        validator=strict_discrete_set,
        values={True: "LN", False: "LG"},
        cast=bool,
        map_values=True,
        get_process=_getstatus(StatusMessage.LinearLogStatus, lambda v: {0: "LN", 1: "LG"}[v])
    )

    @property
    def resolution(self):
        """
        Control the resolution of the power meter's measured value. Three levels of resolution
        can be
        set: 0.1 dB, 0.01 dB and 0.001 dB or if the selected unit is Watts 1%, 0.1% and 0.001%.
        """
        linear_display_enabled = self.linear_display_enabled
        mapping = {}
        if not linear_display_enabled:
            mapping = {1: 0.1, 2: 0.01, 3: 0.001}
        else:
            mapping = {1: 1, 2: 0.1, 3: 0.01}

        self.write("RE")
        self.check_errors()
        display_content = self.display_output
        self.check_errors()
        self.write("EX")
        assert display_content[0:3] == "RES"

        return mapping[int(display_content[3])]

    @resolution.setter
    def resolution(self, resolution):
        """
        Control the resolution of the power meter's measured value. Three levels of resolution can
        be set: 0.1 dB, 0.01 dB and 0.001 dB or if the selected unit is Watts 1%, 0.1% and 0.001%.
        """

        linear_display_enabled = self.linear_display_enabled
        allowed_values = {}
        if not linear_display_enabled:
            allowed_values = {0.1: 1, 0.01: 2, 0.001: 3}
        else:
            allowed_values = {1: 1, 0.1: 2, 0.01: 3}

        strict_discrete_set(resolution, allowed_values.keys())

        self.write(f"RE{allowed_values[resolution]}EN")
        self.check_errors()

    sensor_type = Instrument.setting(
        "SE%dEN",
        """
        Set the sensor type connected to the power meter to select the corresponding calibration
        factor.

        .. code-block:: python

            from pymeasure.instruments.hp.hp437b import SensorType

            instr.sensor_type = SensorType.HP_8481A

        """,
        validator=strict_discrete_set,
        values=[e for e in SensorType],
        check_set_errors=True
    )

    def sensor_data_clear(self, sensor_id):
        """
        Clear the Sensor Data table of 'sensor_id' previous to entering new values.
        """
        values = [0, 9]
        strict_range(sensor_id, values)

        self.write(f"CT{sensor_id}")

    def sensor_data_ref_cal_factor(self, sensor_id, ref_cal_factor):
        """
        Set the power sensor's reference calibration factor to the Sensor Data table.
        """
        values = [0, 9]
        strict_range(sensor_id, values)

        self.write(f"RF{sensor_id}{ref_cal_factor:4.1f}")
        self.check_errors()

    def sensor_data_write_cal_factor_table(self, sensor_id, frequency_table, cal_fac_table):
        """
        Write the 'calibration_table' for 'sensor_id' to the Sensor Data
        table. And write the reference calibration factor for the 'sensor_id'.
        Frequency is given in Hz. Calibration factor as percentage.

        The power meter’s memory contains space for 10 tables, numbered
        0—9. Tables 0-7 each contain space for 40 frequency /calibration
        factor pairs. Tables 8 and 9 each contain space for 80
        frequency/calibration factor pairs.

        This function clears the sensor table before writing.

        Example table:

        .. code-block:: python

            calibration_table = {
                10e6: 100.0,
                1e9: 96.5,
                2e9: 97.0
            }

            instr.sensor_data_cal_factor_table(0, calibration_table.keys(),
            calibration_table.values())
        """
        values = [0, 9]
        strict_range(sensor_id, values)

        if sensor_id in range(0, 7) and (len(cal_fac_table) > 40 or len(frequency_table)) > 40:
            raise ValueError(f"For sensor id {sensor_id} there aren't more than 40 frequency "
                             f"pairs allowed")
        if sensor_id in range(8, 9) and (len(cal_fac_table) > 80 or len(frequency_table)) > 80:
            raise ValueError(f"For sensor id {sensor_id} there aren't more than 80 frequency "
                             f"pairs allowed")
        if len(cal_fac_table) != len(frequency_table):
            raise ValueError(f"Frequency table and calibration factor table must have the same "
                             f"length {len(cal_fac_table)}!={len(frequency_table)}")

        self.sensor_data_clear(sensor_id)
        for frequency, cal_factor in zip(frequency_table, cal_fac_table):
            if frequency > 99.9e6:
                freq_suffix = "GZ"
                frequency /= 1e9
            elif frequency > 99.9e3:
                freq_suffix = "MZ"
                frequency /= 1e6
            else:
                freq_suffix = "KZ"
                frequency /= 1e3

            self.write(f"ET{sensor_id} {frequency:5.2f}{freq_suffix} {cal_factor}% EN")
            self.check_errors()
        self.write("EX")
        self.check_errors()

    def sensor_data_read_cal_factor_table(self, sensor_id):
        """
        Read the Sensor Data calibration table. See :meth:`sensor_data_write_cal_factor_table`
        Returns a tuple of frequencies as list and calibration factors as list.
        """
        allowed_values = [0, 9]
        strict_range(sensor_id, allowed_values)

        pairs = 80
        if sensor_id < 8:
            pairs = 40

        frequency_data = []
        cal_fac_data = []
        self.write(f"ET{sensor_id}")
        self.check_errors()
        for i in range(0, pairs):
            # outputs something like 38.00GZ 100.2%
            display_content = self.display_output

            frequency = float(display_content[0:5])
            if frequency == 0:
                break
            if display_content[5:7] == "GZ":
                frequency *= 1e9
            else:
                frequency *= 1e6

            calibration_factor = float(display_content[8:13])
            cal_fac_data.append(calibration_factor)
            frequency_data.append(frequency)

            self.write("EN")
            self.check_errors()

        self.write("EX")
        return frequency_data, cal_fac_data

    def sensor_data_write_id_label(self, sensor_id, label):
        """
        Set a particular power sensor’s ID label table to be modified. The sensor ID label must not
        exceed 7 characters. For example, to identify Sensor Data table #2
        with an ID number of 1234567:

        .. code-block:: python

            instr.sensor_data_id_label(2, "1234567")

        """

        values = [0, 9]
        strict_range(sensor_id, values)

        if len(label) > 7:
            raise ValueError("Sensor id label must not exceed length of 7")

        if not str(label).upper().isalnum():
            raise ValueError("Sensor id label only allows 0-9, A-Z")

        self.write(f"SN{sensor_id}{label}")

    automatic_range_enabled = Instrument.control(
        "SM", "%s",
        """
        Control the automatic range.
        The power meter divides each sensor’s power range into 5 ranges of 10 dB each. Range 1
        is the most sensitive (lowest power levels), and Range 5 is the least sensitive (highest
        power levels). The range can be set either automatically or manually.
        """,
        get_process=_getstatus(StatusMessage.AutomaticRangeStatus, lambda v: bool(v)),
        set_process=lambda v: "RM0EN" if v is True else "RH"
    )

    range = Instrument.control(
        "SM", "RM%dEN",
        """
        Control the range to be selected manually. Valid range numbers are 1 through 5.
        See :attr:`automatic_range_enabled` for further information.
        """,
        values=[1, 5],
        validator=strict_range,
        get_process=_getstatus(StatusMessage.Range)
    )

    def store(self, register):
        """
        The power meter can store instrument configurations for recall at a
        later time. The following information can be stored in the power
        meter’s internal registers:

        - reference calibration factor value
        - Measurement units (dBm or watts)
        - relative value and status (on or off)
        - power reference status (on or off)
        - calibration factor value
        - SENSOR ID (sensor data table selection)
        - offset value and status (on or off)
        - range (Auto or Set)
        - frequency value
        - resolution
        - duty cycle value and status (on or off)
        - Filter (number of readings averaged, auto or manual)
        - Limits value and status (on or off)

        Registers 1 through 10 are available for storing instrument
        configurations.
        """
        values = [1, 10]
        strict_range(register, values)
        self.write(f"ST{register}EN")

    operating_mode = Instrument.measurement(
        "SM",
        """
        Get the operating mode the power meter is currently in.
        """,
        get_process=_getstatus(StatusMessage.OperatingMode, lambda v: OperatingMode(v))
    )

    def zero(self):
        """
        Adjust the power meter’s internal circuitry for a zero power indication when no power is
        applied to the sensor.

        .. note::

            Ensure that no power is applied to the sensor while the power meter
            is zeroing. Any applied RF input power will cause an erroneous
            reading.

        """
        self.write("ZE")

    trigger_mode = Instrument.control(
        "SM", "TR%d",
        """
        Control the trigger mode.

        The power meter has two modes of triggered operation; standby mode and free run mode.
        Standby mode means the power meter is making measurements, but the display and HP-IB are
        not updated until a trigger command is received. Free run means that Meter takes
        measurements and updates the display and HP-IB continuously.
        """,
        values=[e for e in TriggerMode],
        validator=strict_discrete_set,
        get_process=_getstatus(StatusMessage.TriggerMode, lambda v: TriggerMode(v)),
        set_process=lambda v: int(v)
    )

    def trigger_immediate(self):
        """
        Trigger immediate.

        When the power meter receives the trigger immediate program code, it inputs one more data
        point into the digital filter, measures the reading from the filter, and then updates
        the display and HP-IB. (When the trigger immediate command is executed, the internal
        digital filter is not cleared.) The power meter then waits for the measurement results to
        be read by the controller. While waiting, the power meter can process most bus commands
        without losing the measurement results. If the power meter receives a trigger immediate
        command and then receives the GET (Group Execute Trigger) command, the trigger immediate
        command will be aborted and a new measurement cycle will be executed. Once the
        measurement results are read onto the bus, the power meter always reverts to standby/hold
        mode. Measurement results obtained via trigger immediate are normally valid only when the
        power meter is in a steady, settled state.
        """
        self.write("TR1")

    def trigger_delay(self):
        """
        Trigger with delay.

        Triggering with delay is identical to :meth:`trigger_immediate` except the power meter
        inserts a settling-time delay before taking the requested measurement.
        This settling time allows the internal digital filter to be updated with new values to
        produce valid, accurate measurement results. The trigger with delay command allows time
        for settling of the internal amplifiers and filters. It does not allow time for power
        sensor delay. In cases of large power changes, the delay may not be sufficient for
        complete settling. Accurate readings can be assured by taking two successive measurements
        for comparison. Once the measurement results are displayed and read onto the bus,
        the power meter reverts to standby mode.
        """
        self.write("TR2")

    group_trigger_mode = Instrument.control(
        "SM", "GT%d",
        """
        Control the group execute trigger mode.
        When in remote and addressed to listen, the power meter responds to a Trigger message (
        the Group Execute Trigger bus command [GET]) according to the programmed mode.
        """,
        values=[e for e in GroupTriggerMode],
        validator=strict_discrete_set,
        get_process=_getstatus(StatusMessage.GroupTriggerMode, lambda v: GroupTriggerMode(v)),
        set_process=lambda v: int(v)
    )
