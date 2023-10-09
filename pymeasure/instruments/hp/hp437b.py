from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, \
    joined_validators, strict_range
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

    @property
    def options(self):
        raise NotImplementedError("This instrument is only partial SCPI conformant")

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
        """
    )

    display_enabled = Instrument.setting(
        "%s",
        """
        Set the display of the power meter active or inactive.
        """,
        map_values=True,
        validator={True: "DE", False: "DD"}
    )

    display_all_segments_enabled = Instrument.setting(
        "%s",
        """
        Set all segments of the display of the power meter active or resume normal state.
        """,
        map_values=True,
        validator={True: "DA", False: "DE"}
    )

    display_user_message = Instrument.setting(
        "DU %s",
        """
        """,
        validator=lambda x, y: str(x).isalnum() and len(str(x)) <= 12,
        set_process=lambda v: str(v).upper()
    )

    duty_cycle_enabled = Instrument.
