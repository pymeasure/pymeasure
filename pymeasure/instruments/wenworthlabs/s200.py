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
import time
from enum import IntEnum

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class S200(Instrument):
    """ Represents the Wenthworth Labs S200 Probe Table
    and provides a high-level for interacting with the instrument
    """

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

    chuck_lift = Instrument.control(
        "STA", "%r",
        "Control chuck lift of the probe station",
        validator=strict_discrete_set,
        values={True: 'CUP', False: 'CDW'},
        map_values=True,
        get_process=lambda r:
        r
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
        "PSX", "GTS X, %d",
        "Control the x-axis position in microns",
        validator=None,
        get_process=lambda r:
        int(r.replace("PSX_", ""))
    )

    y_position = Instrument.control(
        "PSY", "GTS Y, %d",
        "Control the y-axis position in microns",
        validator=None,
        get_process=lambda r:
        int(r.replace("PSY_",""))
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

    def check_set_errors(self):
        print("checking set errors")
        response = self.read()
        return response

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

        #SYSTEM CODES
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
