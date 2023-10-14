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
    Filter = (10, 2)
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

    def __getstatus(status_type: StatusMessage):
        start_index, stop_offset = status_type
        return lambda v: int(v[start_index:start_index + stop_offset])

    @property
    def options(self):
        raise NotImplementedError("This instrument is only partial SCPI conformant")

    def check_errors(self):
        errors = []
        while True:
            err = self.values("ERR?")
            if int(err[0]) != 0:
                log.error(f"{self.name}: {err[0]}, {Errors[0]}")
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

    calibration_factor = Instrument.control(
        "KB?", "KB%3.1fPCT",
        """
        Control the calibration factor of a specific power sensor at a specific input frequency. 
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
        get_process=__getstatus(StatusMessage.DutyCycleStatus)
    )

    duty_cycle = Instrument.setting(
        "DY%2.3fPCT",
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
    )

    status_message = Instrument.measurement(
        "SM",
        """
        """
    )

    filter_automatic_enabled = Instrument.control(

    )
