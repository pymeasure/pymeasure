from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import *
from enum import Enum, IntFlag

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class EventStatusRegister(IntFlag):
    """Enumeration to represent the Event Status Register."""

    #: The bit is set when the power meter's LINE switch is set from STDBY to ON
    PowerOn = 128

    #: This bit is set when an incorrect HP-IB code is sent to the power meter. For example,
    # the command “QX” is a command error.
    CommandError = 32

    #: This bit is set when incorrect data is sent to the power meter. For example, the command
    # “FR-3GZ” is an execution error.
    ExecutionError = 16

    #: This bit is set true whenever a measurement error (error 1-49) occurs.
    DeviceDependentError = 8


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
    Range = (6, 2)
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


class MeasurementUnit(Enum):
    Watts = 0

    dBm = 1

    Percent = 2

    dB = 3


class HP437B(Instrument):
    """Represents the HP856XX series spectrum analyzers.

    Don't use this class directly - use their derivative classes

    .. note::
        Most command descriptions are taken from the document:
        'HP 8560A, 8561B Operating & Programming'
    """

    def __init__(self, adapter, name="Hewlett-Packard HP437B", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=True,
            send_end=True,
            **kwargs,
        )

    def __getstatus(status_type: StatusMessage, modifier=lambda v: v):
        start_index, stop_offset = status_type
        return lambda v: modifier(int(v[start_index:start_index + stop_offset]))

    @property
    def options(self):
        raise NotImplementedError("This instrument is only partial SCPI conformant")

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
        get_process=lambda v: EventStatusRegister(int(v))
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

    calibration_factor = Instrument.setting(
        "KB%3.1fPCT",
        """
        Set the calibration factor of a specific power sensor at a specific input frequency. 
        (A chart or table of CAL FACTOR % versus Frequency is printed on each sensor and an 
        accompanying data sheet.) Calibration factor is entered in percent. 
        Valid entries for 'calibration_factor' range from 1.0 to 150.0%.
        """,
        validator=lambda v, vs: strict_discrete_range(v, vs, 0.1),
        values=[1.0, 150.0]
    )

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
        validator=lambda x, y: x if str(x).isalnum() and len(str(x)) <= 12 else str(x)[0:11],
        set_process=lambda v: str(v).upper().ljust(12)
    )

    duty_cycle_enabled = Instrument.control(
        "SM", "DC%d",
        """
        Set duty cycle active or inactive. See :attr:`duty_cycle`
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=__getstatus(StatusMessage.DutyCycleStatus),
        check_set_errors=True
    )

    duty_cycle = Instrument.setting(
        "DY%02.3fPCT",
        """
        Set the duty cycle for calculation of a pulsed input signal. This function will cause the
        power meter to report the pulse power of a rectangular pulsed input signal. The
        allowable range of values for 'duty_cycle' is 0.001 to 99.999%.

        Pulse power, as reported by the power meter, is a mathematical
        representation of the pulse power rather than an actual measurement.
        The power meter measures the average power of the pulsed input
        signal and then divides the measurement by the duty cycle value to
        obtain a pulse power reading.
        """,
        validator=lambda v, vs: strict_discrete_range(v, vs, 0.001),
        values=[0.001, 99.999],
        check_set_errors=True
    )

    # status_message = Instrument.measurement(
    #     "SM", "",
    #     """
    #     """
    # )

    filter_automatic_enabled = Instrument.control(
        "SM", "%s",
        """
        Control the filter mode. By switching over from automatic to manual (true to false)
        the instrument implicitly keeps (holds) the filter value from the automatic selection.
        """,
        cast=bool,
        get_process=__getstatus(StatusMessage.AutoFilterStatus),
        set_process=lambda v: "FA" if v else "FH",
        check_set_errors=True
    )

    filter = Instrument.control(
        "SM", "FM%dEN",
        """
        Control the filter number for averaging. Setting a value implicitly enables the manual 
        filter mode.
        """,
        values=[1, 2, 4, 8, 16, 32, 64, 128, 256, 512],
        validator=strict_discrete_set,
        get_process=__getstatus(StatusMessage.Filter, (lambda x: 2 ** x)),
        check_set_errors=True
    )

    frequency = Instrument.setting(
        "FR%08.4fGZ",
        """
        Setthe frequency of the input signal. Entering a frequency causes the power meter to select
        a sensor-specific calibration factor. The allowable range of 'frequency'
        values is from 0.0001 to 999.9999 GHz with a 100 kHz resolution.
        """,
        set_process=lambda v: v / 1e9,
        check_set_errors=True
    )

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
        get_process=__getstatus(StatusMessage.LimitsCheckingStatus),
        check_set_errors=True
    )

    limit_high = Instrument.setting(
        "LH%5.2fEN",
        """
        Set the upper limit for the builtin limit checking.
        """,
        check_set_errors=True
    )

    limit_low = Instrument.setting(
        "LL%5.2fEN",
        """
        Set the lower limit for the builtin limit checking.
        """,
        check_set_errors=True
    )

    limit_high_hit = Instrument.measurement(
        "SM",
        """
        Check if the upper limit check got triggered.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=__getstatus(StatusMessage.LimitsStatus),
    )

    limit_low_hit = Instrument.measurement(
        "SM",
        """
        Check if the lower limit check got triggered.
        """,
        map_values=True,
        values={True: 2, False: 0},
        cast=int,
        get_process=__getstatus(StatusMessage.LimitsStatus),
    )

    power = Instrument.measurement(
        "",
        """
        Measure the power at the power sensor attached to the power meter in the corresponding unit.
        """
    )

    power_reference_enabled = Instrument.control(
        "SM", "OC%d",
        """
        Control the builtin reference power source 1mW @ 50 MHz.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=__getstatus(StatusMessage.PowerRefStatus),
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
        get_process=__getstatus(StatusMessage.OffsetStatus),
        check_set_errors=True
    )

    offset = Instrument.setting(
        "OS%5.2fEN",
        """
        Set the offset applied to the measured value to compensate for
        signal gain or loss (for example, to compensate for the loss of a 10 dB
        directional coupler). Offsets are entered in dB.
        """,
        values=[-99.99, 99.99],
        validator=strict_range
    )

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
        used as reference and any further reported value from :attr:`power` will refere to this.
        """,
        map_values=True,
        values={True: 1, False: 0},
        cast=int,
        get_process=__getstatus(StatusMessage.RelativeModeStatus),
        check_set_errors=True
    )

    resolution = Instrument.control(
        "SM", "RES%d",
        """
        """,


    )
