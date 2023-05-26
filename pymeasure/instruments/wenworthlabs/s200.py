#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from enum import IntEnum

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_discrete_range, \
    strict_range, multivalue_strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class S200(Instrument):
    """ Represents the Wenthworth Labs S200 Probe Table
    and provides a high-level for interacting with the instrument
    """

    # Movement boundaries of the Pegassus S200 chuck
    S200_MAX_X = 210000  # in microns
    S200_MAX_Y = 210000  # in microns
    S200_MIN_X = 1100  # in microns
    S200_MIN_Y = 1100  # in microns

    Z_OVERTRAVEL_VALID_RANGE = [0, 100]  # in microns
    Z_FINELIFT_VALID_RANGE = [0, 10000]  # in microns
    Z_GROSSLIFT_VALID_RANGE = [0, 100000]  # in microns
    X_Y_INDEX_VALID_RANGE = [0, 10000]  # in tens of microns
    X_POS_VALID_RANGE = [S200_MIN_X, S200_MAX_X]  # in tens of microns
    Y_POS_VALID_RANGE = [S200_MIN_Y, S200_MAX_Y]  # in tens of microns

    def __init__(self,
                 adapter,
                 name="Wentworth Labs S200 Probe Table",
                 query_delay=0.1,
                 write_delay=0.1,
                 timeout=5000,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            write_termination="\n",
            read_termination="\n",
            send_end=True,
            includeSCPI=True,
            timeout=timeout,
            **kwargs
        )
        self.command_execution_info = S200.ExecutionInfoCode(0)

    chuck_lift = Instrument.setting(
        "%s",
        "Control the chuck to the fine down (CDW) or fine up (CUP) position.",
        # The GDW/GUP command is used to move the chuck to the Gross Up or Gross
        # Down positions.

        validator=strict_discrete_set,
        values={True: 'CUP', False: 'CDW'},
        map_values=True,
        check_set_errors=True
    )

    chuck_gross_lift = Instrument.setting(
        "%s",
        "Control the chuck to the gross down (CDW) or fine up (CUP) position.",
        # The CDW/CUP command is used to move the chuck to the Fine Down or
        # Fine Up positions. The GUP command may be used to move the chuck to a
        # safe gross lift height ready for probing the first die. Subsequent Z movements
        # to move the probes onto and off of the die under test should use the CUP and
        # CDW command. If edge sensors are being used this will dynamically adjust
        # the gross lift value to track the wafer surface. Therefore it is advisable not to
        # use the GUP command during the probing process until the start of the next
        # wafer. Doing so may cause unexpected results.
        # AWP compatible: Yes
        validator=strict_discrete_set,
        values={True: 'GUP', False: 'GDW'},
        map_values=True,
        check_set_errors=True
    )

    chuck_override = Instrument.setting(
        "%s",
        "Control the chuck override of the main chuck of the probe station.",
        validator=strict_discrete_set,
        values={True: 'CO1', False: 'CO0'},
        map_values=True,
        check_set_errors=True
    )

    lamp_on = Instrument.setting(
        "%s",
        "Control lamp on/off of the probe station",
        validator=strict_discrete_set,
        values={True: 'LI1', False: 'LI0'},
        map_values=True,
        check_set_errors=True
    )

    x_position = Instrument.control(
        "PSS X", "GTS X,%d",
        "Control the x-axis position in microns",
        validator=strict_range,
        values=X_POS_VALID_RANGE,
        get_process=lambda r:
        int(r.replace("PSS ", "")),
        check_set_errors=True
    )

    y_position = Instrument.control(
        "PSS Y", "GTS Y,%d",
        "Control the y-axis position in microns",
        validator=strict_range,
        values=Y_POS_VALID_RANGE,
        get_process=lambda r:
        int(r.replace("PSS ", "")),
        check_set_errors=True
    )

    xy_position = Instrument.control(
        "PSS XY", "GTXY %d,%d",
        "Control the xy-axis position in microns",
        validator=multivalue_strict_range,
        values=X_POS_VALID_RANGE,
        separator=" ",
        get_process=lambda r:
        [int(numeric_string) for numeric_string in r[1].split(",", maxsplit=1)],
        check_set_errors=True
    )

    z_position = Instrument.measurement(
        "PSGM",
        "Measures the z-axis position in microns",
        get_process=lambda r:
        int(r.replace("PSGM ", ""))
    )

    x_index = Instrument.control(
        "RXM", "WXM %d",
        "Control the x index of the chuck in units of 10 microns ",
        # AWP compatible: Yes
        validator=strict_range,
        values=X_Y_INDEX_VALID_RANGE,
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("RXM ", ""))
    )

    y_index = Instrument.control(
        "RYM", "WYM %d",
        "Control the y index of the chuck in units of 10 microns ",
        # AWP compatible: Yes
        validator=strict_range,
        values=X_Y_INDEX_VALID_RANGE,
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("RYM ", ""))
    )

    theta_position = Instrument.control(
        "PSTH", "GTTH %d",
        "Control the rotation of the chuck to the Theta-axis position in millidegrees "
        "specified in the parameter",
        # AWP compatible: No
        validator=strict_range,
        values=[0, 359999],
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("PSTH ", ""))
    )

    z_overtravel = Instrument.control(
        "RZIM", "WZIM %d",
        "Control the z-axis overtravel (in um) of the chuck of the probe station",
        # AWP compatible: No
        validator=strict_range,
        values=Z_OVERTRAVEL_VALID_RANGE,
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("RZIM ", ""))
    )

    z_grosslift = Instrument.control(
        "RKGM", "WKGM %d",
        "Control the z-axis gross lift (in um) of the chuck of the probe station",
        # AWP compatible: No
        validator=strict_range,
        values=Z_GROSSLIFT_VALID_RANGE,
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("RKGM ", ""))
    )

    z_finelift = Instrument.control(
        "RKFM", "WKFM %d",
        "Control the z-axis fine lift (in um) of the chuck of the probe station",
        # AWP compatible: No
        validator=strict_range,
        values=Z_FINELIFT_VALID_RANGE,
        check_set_errors=True,
        get_process=lambda r:
        int(r.replace("RKFM ", ""))
    )

    indexing_mode = Instrument.setting(
        "%s",
        "Control the indexing mode."
        "If True, Enters indexing mode and moves to the first die to be probed, or moves to the "
        "next die to be probed if already in indexing mode. Indexing mode is exiting "
        "using the NXF command (above).",
        # AWP compatible: Yes
        validator=strict_discrete_set,
        values={True: 'NXT', False: 'NXF'},
        map_values=True,
        check_set_errors=True
    )

    next_die_down = Instrument.setting(
        "NXD",
        "Moves to the die below the current die",
        # AWP compatible: Yes
        check_set_errors=True
    )

    next_die_up = Instrument.setting(
        "NXU",
        "Moves to the die above the current die",
        check_set_errors=True
    )

    next_die_right = Instrument.setting(
        "NXR",
        "Moves to the die right of the current die",
        check_set_errors=True
    )

    next_die_left = Instrument.setting(
        "NXL",
        "Moves to the die left of the current die",
        check_set_errors=True
    )

    status_byte = Instrument.measurement(
        "STA",
        "Measures the status byte of the instrument",
        get_process=lambda r:
        r
    )

    extended_status_info = Instrument.measurement(
        "STP",
        "Measures the extended status information of the instrument",
        get_process=lambda r:
        r
    )

    exit_remote = Instrument.setting(
        "ESC",
        "Sets the proble table in local mode. Exits remote mode."
        # This command does not send a reply. However, when remote mode is re-entered,
        # the Pegasus unit sends an INF_000 message
    )

    serial_number = Instrument.measurement(
        "GSN",
        "Measures the serial number of the probe table",
        # AWP compatible: No
        get_process=lambda r:
        str(r)
    )

    software_version_number = Instrument.measurement(
        "VSN",
        "Measures the software version number of the probe table",
        # AWP compatible: Yes
        get_process=lambda r:
        str(r)
    )

    hardware_build = Instrument.measurement(
        "GHB",
        "Measures the hardware build version number of the probe table",
        # AWP compatible: No
        get_process=lambda r:
        r
    )

    model_id = Instrument.measurement(
        "GID",
        "Measures the model id of the probe table",
        # AWP compatible: Yes
        # Returns model information about the Pegasus unit. The information consists of the
        # Pegasus model name, followed by a semi - colon, followed by a list of options
        # separated by commas.
        # Options can include:
        # LM – Compatible with LabMaster.
        # Pins – Optional chuck load pins fitted.
        # Platform – Optional motorised platform fitted.
        # PR – Optional PR camera fitted.
        # PMM – Optional motorised PMM fitted.
        # CAP – Optional motorised CAPs fitted
        # Z2 – Front flying arm
        # Z3 – Right flying arm
        # Reader – Optional OCR
        # Robot – Robot loader
        # Cleaner – Prober cleaner support
        get_process=lambda r:
        r
    )

    def move_to_load_position(self):
        """
        Moves the manual load position following a LDS command.
        AWP compatible: Yes
        :return: None
        """
        self.write("LDB")
        self.check_set_errors()

    def move_to_manual_load_position(self):
        """
        Moves to the manual load position and moves the chuck to the Z reference height (LDM/LDL).
        AWP compatible: Yes (LDL only)
        :return: None
        """
        self.write("LDM")
        self.check_set_errors()

    def move_to_probing_zone_centre_position(self):
        """
        Moves to the centre of the probing zone and moves the chuck to the gross lift height.
        AWP compatible: Yes
        :return: None
        """
        self.write("LDC")
        self.check_set_errors()

    def move_to_change_probecard_position(self):
        """
        Moves to the position for changing the Probe Card.
        AWP compatible: Yes
        :return: None
        """
        self.write("LDS")
        self.check_set_errors()

    def check_set_errors(self):
        response_code = self.read().replace("INF ", "")
        self.command_execution_info = S200.ExecutionInfoCode(int(response_code))
        log.warning(f"Command execution response '{self.command_execution_info.name}' after "
                    f"setting a value.")
        return [self.command_execution_info.name]

    class ExecutionInfoCode(IntEnum):
        """
        Auxiliary class create for translating the instrument three digits code into
        an Enum_IntEnum that will help to the user to understand information giving by the
        instrument after the execution of certain commands.
        """
        # Info code from the instrument has to be interpreted as follows:
        #
        # response --> 'INF_XXX'

        #  GENERAL
        NO_ERROR = 0
        ATTEMPT_TO_MOVE_IN_X_OR_Y_OUTSIDE_THE_CURRENT_AREA = 3
        UNRECOGNISED_PROBER_COMMAND = 8
        X_INCREMENT_OR_Y_INCREMENT_IS_ZERO = 9

        # SEQUENCE FAULTS
        ATTEMPT_TO_MOVE_X_Y_OR_THETA_WITH_THE_CHUCK_RAISED = 10
        SYSTEM_OR_AXIS_IS_UNREFERENCED = 11
        UNDER_OR_OVER_RANGE_PROBER_VARIABLE = 12
        PROBER_VARIABLE_IS_TOO_SMALL2 = 13
        PROBER_VARIABLE_IS_TOO_LARGE = 14
        PROBER_VARIABLE_IS_AN_INVALID_MULTIPLE2 = 15
        PROBING_HEIGHT_IS_ABOVE_Z_LIMIT = 16

        # EDGE SENSOR FAULTS
        EDGE_SENSOR_OPEN_WHEN_AT_GROSS_DOWN_POSITION_GUP_FUNCTION = 30
        EDGE_SENSOR_OPEN_AFTER_MOVING_TO_FINE_DOWN_POSITION_CDW_FUNCTION = 31
        EDGE_SENSOR_OPEN_WHEN_AT_FINE_DOWN_POSITION_CUP_AND_NXT_FUNCTIONS = 32
        EDGE_SENSOR_NOT_OPENING_WITHIN_SEARCH_WINDOW_CUP_FUNCTION = 33
        EDGE_SENSOR_OPEN_DURING_AS_THE_CHUCK_IS_BEING_LIFTED_GUP_FUNCTION = 39

        # HARDWARE FAULTS
        EDGE_SENSOR_OPEN_WHEN_CHUCK_AT_FINE_DOWN_POSITION = 20
        MOTOR_FAILED_TO_REFERENCE = 21
        CHUCK_NOT_GROSS_LIFTED_WHEN_NXT_COMMAND_SENT = 22
        TESTER_HAS_TIMED_OUT_DURING_TTL_TEST_USING_THE_TST_FUNCTION = 24
        CLAMP_HOLDING_THE_WAFER_FAILED_TO_OPEN_TO_LOAD_UNLOAD_A_WAFER = 28
        CLAMP_HOLDING_THE_WAFER_FAILED_TO_CLOSE_PRIOR_TO_MOVING_THE_CHUCK = 29

        # LEARN MODE PROGRAM DOWNLOAD FAULTS
        LMP_COMMAND_USED_BEFORE_AN_LMC_COMMAND_OR_AFTER_AN_LME_COMMAND = 70
        LEARN_MODE_PROGRAM_MEMORY_IS_FULL = 71

        # INFORMATION CODES
        EDGE_SENSOR_STATE_CHANGED_TO_OPEN = 50
        EDGE_SENSOR_STATE_CHANGED_TO_CLOSED = 51

        # SYSTEM CODES
        INTERNAL_SYSTEM_FAULT_PLEASE_CONTACT_YOUR_WENTWORTH_SERVICE_AGENT = 300
        COMMAND_HAS_ATTEMPTED_TO_ACCESS_UN_INITIALISED_HARDWARE = 301
        ERROR_IN_INTERFACE_PROTOCOL_WITH_STEPPER_MOTOR_CONTROL_FIRMWARE = 302
        SYSTEM_HARDWARE_DOES_NOT_SUPPORT_THE_REQUESTED_FUNCTION = 303
        INCORRECT_PERIPHERAL_FOR_THE_REQUESTED_COMMAND_FUNCTION = 304
        ERROR_ACCESSING_CONTROLLER_FILE_SYSTEM = 305
        USER_HAS_ABORTED_THE_COMMAND_FUNCTION = 306

        # PROBING_EXCEPTION_CODES
        DURING_TESTING_THE_FAILURE_COUNT_HAS_EXCEEDED_THE_FAIL_LIMIT_DEVICE_PARAMETER = 400
        CARTRIDGE_IS_GETTING_LOW_AND_SHOULD_BE_CHANGED = 401
        CARTRIDGE_IS_EMPTY_AND_MUST_BE_CHANGED_FOR_CORRECT_OPERATION = 402
        THE_FINISH_TEST_SIGNAL_HNATI_THAT_THE_PREVIOUS_DEVICE_HAS_COMPLETED_TESTING_WITHIN_THE_EXPECTED_TIME = 403
        SHNA_THAT_THE_CURRENT_DEVICE_HAS_COMPLETED_TESTING_WITHIN_THE_EXPECTED_TIME = 404
        IHNA_TO_INDICATE_THAT_THE_CURRENT_DEVICE_HAS_COMPLETED_TESTING_WITHIN_THE_EXPECTED_TIME = 405
        IHNA_TO_INDICATE_THAT_THE_CURRENT_DEVICE_HAS_STARTED_TESTING_WITHIN_THE_EXPECTED_TIME = 406
        THE_TESTER_COMMAND_IS_INVALID_TSTLR_COMMAND = 407
        NO_COMMAND_RECEIVED_FROM_THE_TESTER_WITHIN_THE_EXPECTED_TIME = 410
        INVALID_COMMAND_RECEIVED_FROM_THE_TESTER = 411
        ABORT_PROBING_COMMAND_RECEIVED_FROM_THE_TESTER = 412

        # STEPPER_MOTOR_ERROR_CODES
        THE_STEPPER_MOTOR_HAS_NOT_BEEN_CORRECTLY_INITIALISED = 500
        THE_STEPPER_MOTOR_FAILED_TO_REFERENCE_CORRECTLY = 501
        THE_STEPPER_MOTOR_DETECTED_AN_UNEXPECTED_FAULT = 502
        NO_ACKNOWLEDGEMENT_RECEIVED_BACK_FROM_A_STEPPER_COMMAND = 503
        ATTEMPT_TO_UPDATE_THE_STEPPER_MOTOR_WHILE_IT_IS_STILL_MOVING = 504
        THE_STEPPER_MOTOR_DETECTED_THAT_THE_EDGE_SENSOR_OPENED_UNEXPECTEDLY_DURING_MOVEMENT = 505
        NO_ACKNOWLEDGEMENT_WAS_RECEIVED_BACK_FROM_A_STEPPER_COMMAND_WITHIN_THE_EXPECTED_TIME = 506
        THE_STEPPER_COMMAND_RECEIVED_WAS_NOT_RECOGNISED = 507
        THE_STEPPER_COMMAND_RECEIVED_CONTAINED_INVALID_DATA = 508

        # SAFETY AND LIMIT CODES
        AN_ATTEMPT_TO_MOVE_THE_MOTOR_AT_A_SPEED_GREATER_THAN_ITS_VELOCITY_LIMIT = 600
        AN_ATTEMPT_TO_MOVE_A_COMPONENT_WHEN_A_DOOR_OR_CONTACT_HAS_BEEN_OPENED = 601
        A_DOOR_OR_CONTACT_HAS_BEEN_OPENED_WHILE_A_COMPONENT_IS_MOVING = 602
        A_VACUUM_SENSOR_HAS_DETECTED_THAT_THE_VACUUM_FAILED_TO_TURN_ON = 603
        A_VACUUM_SENSOR_HAS_DETECTED_THAT_THE_VACUUM_FAILED_TO_TURN_OFF = 604

        # STAGE I/O INTERFACE CODES
        NO_COMMUNICATION_BETWEEN_THE_CONTROLLER_AND_THE_STAGE_I_O_INTERFACE = 630
        NO_ACKNOWLEDGEMENT_RECEIVED_FROM_THE_STAGE_I_O_INTERFACE_WITHIN_THE_EXPECTED_TIME = 631
        MULTIPLE_ERRORED_PACKETS_RECEIVED_FROM_THE_STAGE_I_O_INTERFACE = 632

        # NETWORK(INTERNET_PROTOCOL) CODES
        UNEXPECTED_IP_COMMUNICATION_ERROR = 650
        NO_COMMUNICATION_RECEIVED_OVER_IP_WITHIN_THE_EXPECTED_TIME = 651
        CONNECTION_ERROR_TO_REMOTE_SYSTEM_OVER_IP = 652
        IP_SOCKET_ERROR = 653
        UNABLE_TO_RESOLVE_HOST_NAME_AS_IP_ADDRESS = 654
        DOMAIN_NAME_NOT_SUPPLIED_AS_REQUIRED_BY_DNS = 655

        # PERIPHERAL CODES
        PROBE_CLEANER_MATERIAL_NEEDS_CHANGING = 700
        PROBE_CLEANING_PAUSED_BY_USER = 701
        PROBE_CLEANING_ABORTED_BY_USER = 702
        ATTEMPT_TO_SET_PROBE_CLEANING_HEIGHT_ABOVE_Z_LIMIT = 703
        ATTEMPT_TO_SET_CAMERA_HEIGHT_ABOVE_GROSS_HEIGHT = 710
        UNABLE_TO_ACCESS_OCR_READER = 720
        NO_CHARACTER_READ_FROM_THE_OCR_READER_WITHIN_THE_EXPECTED_TIME = 721
        ATTEMPT_TO_READ_THE_ID_OF_THE_OCR_READER_FAILED = 722
        PREFIX_CHARACTERS_ARE_MISSING_FROM_THE_ID_READ_FROM_THE_OCR_READER = 724
        POSTFIX_CHARACTERS_ARE_MISSING_FROM_THE_ID_READ_FROM_THE_OCR_READER = 725
        FAILED_TO_LOAD_FROM_THE_MANUAL_LOAD_AREA = 730

        # FAILURE ANALYSIS AND PMM CODES
        PROBE_BELOW_PRETOUCH_HEIGHT = 800
        DEVICE_IS_NOT_ALIGNED = 801
        INCORRECT_ARGUMENT_COUNT = 804
        ANGLE_NOT_SUITABLE_FOR_ALIGNMENT = 805
        UNEXPECTED_ERROR_DETECTED = 806
        INCORRECT_DEVICE_ALIGNMENT = 807
        INVALID_HEIGHT = 808

        # CUSTOMISATION ERROR CODES
        INKER_LIFT_ERROR = 900
        PREVIOUS_DEVICE_FINISH_TEST_SIGNAL_HAS_NOT_ASSERTED = 901
        CURRENT_DEVICE_FINISH_TEST_SIGNAL_HAS_NOT_ASSERTED = 902
