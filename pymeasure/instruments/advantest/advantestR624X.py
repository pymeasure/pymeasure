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

import logging
from enum import IntEnum, IntFlag
from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, \
    strict_range

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SampleHold(IntEnum):
    MODE_0 = 0
    MODE_100uS = 6
    MODE_200uS = 7
    MODE_500uS = 8
    MODE_1mS = 9
    MODE_2mS = 10
    MODE_5mS = 11
    MODE_10mS = 12
    MODE_1PLC = 13  # Number of power line cycles
    MODE_2PLC = 14
    MODE_5PLC = 15
    MODE_10PLC = 16
    MODE_20PLC = 17


class SampleMode(IntEnum):
    ASYNC = 1  # Asynchronous operation
    PULSED_SYNC = 2  # Synchronous operation of DC measurement and pulse measurement
    PULSED_POSITIVE = 3  # Positive tracking operation for DC measurement and pulse measurement
    PULSED_REVERSE = 4  # DC measurement, pulse measurement reverse polarity tracking operation
    SWEEP_SYNC = 5  # Synchronous operation of sweep measurement
    SWEEP_DELAYED = 6  # Delayed sweep operation
    SWEEP_DOUBLE = 7  # Double synchronous sweep operation
    BINARY_SEARCH = 8  # Binary search
    LINEAR_SEARCH = 9  # Linear search


class VoltageRange(IntEnum):
    # When the integration time is sample hold mode (SH) and between 100 μs to 500 μs, the
    # resolution is as follows.
    #
    # Integration time Decomposition energy (digit)
    # SH, 100μs        10 digits
    # 200μs            5 digits
    # 500μs            2 digits

    # The range that maximizes the number of digits in the measurement data is automatically
    # selected.
    # It cannot be specified for pulse measurement and pulse sweep.

    AUTO = 0  # ±1μV resolution

    # Limited auto range
    # It operates in the same way as the auto range except that the specified range is minimized.
    # It cannot be specified for pulse measurement and pulse sweep.
    AUTO_600mV = 23  # ±1μV resolution
    AUTO_6V = 24  # ±10μV resolution
    AUTO_60V = 25  # ±100μV resolution
    AUTO_200V = 26  # ±1mV resolution

    # Best fixed range
    # - Voltage generation When measuring voltage (VSVM), the range is the same as the generation
    #   range.
    # - In the case of current generation voltage measurement (ISVM), it is in the same range as the
    #   compliance range.
    FIXED_BEST = 20  # ±1μV - 1mV resolution

    # Measure in the specified range.
    FIXED_600mV = 3  # ±1μV resolution
    FIXED_6V = 4  # ±10μV resolution
    FIXED_60V = 5  # ±100μV resolution
    FIXED_200V = 6  # ±1mV resolution


class CurrentRange(IntEnum):
    # When the integration time is sample hold mode (SH) and between 100 μs to 500 μs, the
    # resolution is as follows.
    #
    # Integration time Decomposition energy (digit)
    # SH, 100μs        10 digits
    # 200μs            5 digits
    # 500μs            2 digits

    # The range that maximizes the number of digits in the measurement data is automatically
    # selected.
    # It cannot be specified for pulse measurement and pulse sweep.
    AUTO = 0  # ±10fA resolution

    # It operates in the same way as the auto range, except that the specified range is the minimum
    # range. It cannot be specified for pulse measurement and pulse sweep.
    AUTO_6nA = 23  # ±10fA resolution
    AUTO_60nA = 24  # ±100fA resolution
    AUTO_600nA = 25  # ±1pA resolution
    AUTO_6μA = 26  # ±10pA resolution
    AUTO_60μA = 27  # ±100pA resolution
    AUTO_600μA = 28  # ±1nA resolution
    AUTO_6mA = 29  # ±10nA resolution
    AUTO_60mA = 30  # ±100nA resolution
    AUTO_600mA = 31  # ±1μA resolution
    AUTO_2A_6A = 32  # ±10μA resolution
    AUTO_20A = 33  # ±100μA resolution

    # Current generation when measuring current (ISIM), the range is the same as the generation
    # range. When measuring voltage generation current (VSIM), it is in the same
    # range as the compliance range.
    FIXED_BEST = 20  # ±10fA - ±100μA resolution

    # A fixed range cannot be specified for internal measurements.
    # It can be specified only for external measurement. MEASURE INPUT-ANALOG COMMON
    # Also measures the voltage between the terminals as the specified current range data.
    FIXED_6nA = 3  # ±10fA resolution
    FIXED_60nA = 4  # ±100fA resolution
    FIXED_600nA = 5  # ±1pA resolution
    FIXED_6μA = 6  # ±10pA resolution
    FIXED_60μA = 7  # ±100pA resolution
    FIXED_600μA = 8  # ±1nA resolution
    FIXED_6mA = 9  # ±10nA resolution
    FIXED_60mA = 10  # ±100nA resolution
    FIXED_600mA = 11  # ±1μA resolution
    FIXED_2A_6A = 12  # ±10μA resolution
    FIXED_20A = 13  # ±100μA resolution


class SweepMode(IntEnum):
    LINEAR_ONE_WAY_SWEEP = 1
    LOG_ONE_WAY_SWEEP = 2
    LINEAR_ROUND_TRIP_SWEEP = 3
    LOG_ROUND_TRIP_SWEEP = 4


class OutputType(IntEnum):
    REAL_TIME_OUTPUT = 1  # there is output every time it is measured
    BUFFERING_OUTPUT_ALL = 2  # output all at once after sweeping
    BUFFERING_OUTPUT_SPECIFIED = 3  # After sweeping, only output the specified data


class TriggerInputType(IntEnum):
    ALL = 1
    SOFTWARE_ONLY = 2
    CHANNELS_ONLY = 3


class MeasurementType(IntEnum):
    MEASURE_DATA = 1
    MEASURE_DATA_AND_OCCURENCE = 2


class SequenceInterruptionType(IntEnum):
    """ 1.  Release pause state is a valid command only in the
            sequence program pause state. otherwise it is ignored.

        2.  Pause state enters the pause state when the currently
            executing program ends.

        3.  Abort sequence program stops the sequence program when
            the currently executing program ends. If the currently running program
            is a sweep operation, interrupt the sweep operation and stop the sequence
            program. The output value will be the bias value.

    """
    RELEASE_PAUSE = 1
    PAUSE = 2
    INTERRUPT_SEQUENCE = 3


class DOR(IntFlag):
    """ bit assigment for the Device Operation Register (DOR):

        =========  ==========================
        Bit (dec)  Description
        =========  ==========================
         13        Indicates that the fast tokens program is running.
         12        Error in search measurement
         11        End of sequence program/high-speed sequence program execution
         10        Sequence program Pause state
         9         Fan stop detection
         8         Self-test error occurred (logic part)
         7         Trigger wait state in trigger link master operation
         6         Calibration mode status
         5         Trigger link ON state
         4         Trigger link bus error
         3         Sequence program/high-speed sequence 1 program/add/de) waiting
         2         Wait for sequence program wait time
         1         Sequence program running
         0         Synchronous operation state
        =========  ==========================

    """
    FAST_TOKENS_PROGRAM_IS_RUNNING = 1 << 13
    ERROR_IN_SEARCH_MEASUREMENT = 1 << 12
    END_OF_SEQUENCE_PROGRAM = 1 << 11
    SEQUENCE_PROGRAM_PAUSE_STATE = 1 << 10
    FAN_STOP_DETECTION = 1 << 9
    SELF_TEST_ERROR_LOGIC = 1 << 8
    TRIGGER_WAIT_STATE = 1 << 7
    CALIBRATION_MODE_STATUS = 1 << 6
    TRIGGER_LINK_ON_STATE = 1 << 5
    TRIGGER_LINK_BUS_ERROR = 1 << 4
    SEQUENCE_PROGRAM_WAITING = 1 << 3
    WAIT_FOR_SEQUENCE_PROGRAM_WAIT_TIME = 1 << 2
    SEQUENCE_PROGRAM_RUNNING = 1 << 1
    SYNCHRONOUS_OPERATION_STATE = 1 << 0


class COR(IntFlag):
    """ bit assigment for the Channel Operations Register (COR):

        =========  =============================================
        Bit (dec)  Description
        =========  =============================================
         14        The result of the comparison operation is HI
         13        The result of the comparison operation is GO
         12        The result of the comparison operation is LO
         11        Overheat detection
         10        Overload detection
         9         Oscillation detection
         8         Compliance detection
         7         Synchronous operation master channel
         6         Measurement data output specification
         5         There is measurement data
         4         Self-test error occurrence (analog part)
         3         Measurement data buffer full
         2         Waiting for trigger
         1         End of sweep
         0         Operated state
        =========  =============================================

    """
    COMPARISON_RESULT_HI = 1 << 14
    COMPARISON_RESULT_GO = 1 << 13
    COMPARISON_RESULT_LO = 1 << 12
    OVERHEAT_DETECTION = 1 << 11
    OVERLOAD_DETECTION = 1 << 10
    OSCILLATION_DETECTION = 1 << 9
    COMPLIANCE_DETECTION = 1 << 8
    SYNCHRONOUS_OPERATION_MASTER_CHANNEL = 1 << 7
    MEASUREMENT_DATA_OUTPUT_SPECIFICATION = 1 << 6
    HAS_MEASUREMENT_DATA = 1 << 5
    SELF_TEST_ERROR_ANALOG_SECTION = 1 << 4
    MEASUREMENT_DATA_BUFFER_FULL = 1 << 3
    WAITING_FOR_TRIGGER = 1 << 2
    END_OF_SWEEP = 1 << 1
    OPERATED_STATE = 1 << 0


class SRER(IntFlag):
    """ bit assigment for the Service Request Enable Register (SRER):

        =========  ===========================================================
        Bit (dec)  Description
        =========  ===========================================================
         0          none
         1          ERR Set when any of QYE, DDE, EXE, or CME in
                    the Standard Event Status Register (SESR) is set.
         2          DOP Set when a bit in the device operation register
                    for which the enable register is set to enabled is set.
                    Cleared by reading the device operation register.
         3          none
         4          MAV Set when output data is set in the output queue.
                    Cleared when output data is read.
         5          ESB Set when a bit in the Standard Event Status Register
                    (SESR) is set and the enable register is set to Enabled.
                    Cleared by reading SESR.
         6          RQS (MSS) Set when bit O to bit 5 and bit 7 of the
                    Status Byte register are set. (this bit is read-only)
         7          COP Set when a bit in the Channel Operations Register
                    is set with the Enable Register set to Enable.
                    Cleared by reading the Channel Operations Register.
        =========  ===========================================================

    """
    ERR = 1 << 1
    DOP = 1 << 2
    MAV = 1 << 4
    ESB = 1 << 5
    RQS = 1 << 6
    COP = 1 << 7


class SESR(IntFlag):
    """ bit assigment for the Standard Event Status Register (SESR):

        =========  ==========================
        Bit (dec)  Description
        =========  ==========================
         0         OPC (Operation Complete) not used
         1         RQC unused
         2         QYE (Query Error) Set when the output queue
                   overflows when reading without output data.
         3         DDE (Device Dependent Error) Set when an
                   error occurs in the self-test.
         4         EXE (Execution Error) Set when the input
                   data is outside the range set internally,
                   or when the command cannot be executed.
         5         CME (Command Error) Set when an undefined header
                   or data format is wrong, or when there is a
                   syntax error in the command.
         6         URQ unused
         7         PON Set when power is switched from OFF to ON.
        =========  ==========================

    """
    OPC = 1 << 0
    RQC = 1 << 1
    QYE = 1 << 2
    DDE = 1 << 3
    EXE = 1 << 4
    CME = 1 << 5
    URQ = 1 << 6
    PON = 1 << 7


class TriggerOutputSignalTiming(IntFlag):
    """ bit assigment for the timing of the trigger output signal
       output from TRIGGER OUT on the rear panel:

        =========  =============================
        Bit (dec)  Description
        =========  =============================
         5         At the end of the sweep
         4         At the end of the pulse width
         3         At the end of the pulse cycle
         2         At the end of measurement
         1         At the start of measurement
         0         At the start of occurrence
        =========  =============================

    """
    END_OF_SWEEP = 1 << 5
    END_OF_THE_PULSE_WIDTH = 1 << 4
    END_OF_THE_PULSE_CYCLE = 1 << 3
    END_OF_MEASUREMENT = 1 << 2
    START_OF_MEASUREMENT = 1 << 1
    START_OF_OCCURRENCE = 1 << 0


"""
TODO, implement the following commands:

(54) LDS? This is a query command for reading the currently set parameters via GPIB.

(93) MAR ~; NENT The MAR ~; NENT command sets the search measurement sense channel source, target
measurement,
and compliance values, and the search channel start/stop and compliance values.
It also sets the output state after stopping for both the sense channel and search channel.
(94) MAR~；CMD~；NEN During search measurement, you can set ON/OFF of the measurement data comparison
calculation and the upper and lower limit data to be compared.

Syntax:
MAR 0, search mode, generated value after stop; command; NEN

1 Binary search measurement: sense channel
2 Binary search measurement: search channel (negative feedback search)
3 Binary search measurement: search channel (positive feedback search)
4 Linear search measurement: sense channel
5 Linear search measurement: search channel

Occurrence value after stopping
1 Generates a bias value.
2 Leave the finished generation value as is.
3 Generate stop values.

- The commands that can be used for search measurement are shown below.

                Binary search                 Linear search
sense channel:  FXI, FXV, PXI, PXV, CMD       FXI, FXV, PXI, PXV, CMD
search channel: WI, WV                        WI, WV, PWI, PWV, CMD

- If you set a command other than the above with the MAR ~; NENT command, an error will occur.
- The linear search CMD (comparison operation) command is set to either the sense channel or the
search channel.
  Therefore, if the CMD command is set for both channels, the comparison operation is performed with
the one that was set later.

Number of steps: 2. When the source range is 600mV, search is performed in steps of 20µV.
MAR 0, 1, 2;FXV 1, 20, 6, 17, 2, 0;NENT
MAR 0, 2, 2;WV 2, 1, 1, 20, -3, 0, 17, 6.2E-2, -3; NENT

(95) PGST~;END # Program number that specifies the command to be executed by the high-speed sequence
program. This command stores in memory.

Commands that can be used unconditionally
DV, DI, PV, PI
WT, MST, RV, RI
CMD, CN, CL, OPM, FL
LTL, DIOS, DIOE, EXT
PCEL, MAR ~ NENT

Commands that can be used with MAR ~ ; NEN commands
FXV, FXI. PXV, PXI, WV, WI, PWV, PWI

(96) EXT # This command is used to set a conditional jump in the program of a high-speed sequence
program.
(97) PGON To execute a high-speed sequence program, store the program in program numbers 1 to 20
with the PGST ; END command in advance.
Note that program numbers that do not store programs are skipped without being executed.
(98) PGOF This command cancels the start/enable state of the high-speed sequence program set by the
PGON command.
(99) PCEL This command clears the program stored in memory by the PGST command.
"""


def map_values(value, values):
    return values[strict_discrete_set(value, values)]


class AdvantestR624X(SCPIUnknownMixin, Instrument):
    """ Represents the Advantest R624X series (channel A and B) SourceMeter and provides a
    high-level interface for interacting with the instrument.

    This is the base class for both AdvantestR6245 and AdvantestR6246 devices. It's not
    necessary to instantiate this class directly instead create an instance of the
    AdvantestR6245 or AdvantestR6246 class as shown in the following example:

    .. code-block:: python

        smu = AdvantestR6246("GPIB::1")
        smu.reset()                                                     # Set default parameters
        smu.ch_A.current_source(source_range = CurrentRange.FIXED_60mA,
                                source_value = 0,                       # Source current at 0 A
                                voltage_compliance = 10)                # Voltage compliance at 10 V
        smu.ch_A.enable_source()                                        # Enables the source output
        smu.ch_A.measure_voltage()
        smu.ch_A.current_change_source = 5e-3                           # Change to 5mA
        print(smu.read_measurement())                                   # Read and print the voltage
        smu.ch_A.standby()                                              # Put channel A in standby

    """

    def __init__(self, adapter, name="R624X Source meter Base Class", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.sequence = []
        self.store_to_sequence = False
        self.sequence_line_count = 0

    def write(self, command, **kwargs):
        if self.store_to_sequence:
            self.append_sequence_command(command)
        else:
            super().write(command, **kwargs)

    def check_errors(self):
        errors = {
            100: "A fan stop was detected.",
            101: "Since the overload detection of the {0} channel was activated, it was set to"
                 "standby.",
            102: "Since the overheat detection of the {0} channel worked, I made it a standby.",
            200: "Received an undefined command.",
            201: "There is an error in the data format.",
            210: "Received data outside the set range.",
            211: "A command was received that cannot be executed in the current settings.",
            221: "Data output buffer overflowed.",
        }

        error = self.ask('err?')
        unit = int(error[0:2])
        err = int(error[2:5])
        channel = f'{"B" if unit > 1 else "A"}'

        if err in errors:
            message = errors[err].format(channel)
        elif err > 0 and err < 100:
            if unit == 0:
                message = "As a result of the self-test, an abnormality was found in the logic" \
                          "part."
            else:
                message = f"Result of self-test {channel}-channel was found to be abnormal."
        elif err > 99 and err < 200:
            message = "Internal error, calibration error"
        else:
            message = "Setting error"

        if err == 0:
            return
        else:
            raise OSError(
                f"{self.name} Error {error[0:5]}: {message}")

    def enable_source(self):
        """ Put channel A & B into the operating state (``CN``).

        .. note::
            When the 'interlock control' of the 'SCT' command is '2' and the
            clock signal is 'HI', it will not enter the operating state.
        """
        self.write('cn 0')

    def standby(self):
        """ Put channel A & B in standby mode (``CL``).
        """
        self.write('cl 0')

    def clear_status_register(self):
        """ Clears the Standard Event Status Register (SESR) and
        related queues (excluding output queues) (``*CLS``).
        """
        self.write('*cls')

    srq_enabled = Instrument.setting(
        "s%d",
        """ Set a boolean that controls whether the GPIB SRQ feature is
        enabled, takes values of True or False (``S0/S1``).

        :type: bool

        The SRQ feature of the GPIB bus provides hardware handshaking between
        the GPIB controller card in the PC and the instrument. This allows
        synchronization between moving data to the PC with the state of the
        instrument without the need to use time delay functions.
        """,
        validator=strict_discrete_set,
        values={False: 1, True: 0},
        map_values=True
    )

    def trigger(self):
        """ Outputs the trigger signal or the start of sweep and
        search measurement to both A and B channels and the trigger link (``XE``).

        .. note::

            * When both A channel and B channel are waiting for a trigger,
              both channels are triggered.
            * When either channel A or B is waiting for a trigger,
              only the channel that is waiting for a trigger is triggered.
            * When both A channel and B channel are waiting for sweep start,
              this will apply sweep start to both channels.
            * When either channel A or B is in the sweep start waiting state,
              only the channel in the sweep start waiting state is started.
            * When either channel A or B is waiting for a trigger and the
              other is waiting for a sweep start, trigger and sweep start
              are applied, respectively.
            * When the trigger link is ON and this is the master unit,
              set the \\*TRG signal on the trigger link bus to TRUE.
            * When the trigger link is ON and the master unit,
              the trigger link is activated.

        """
        self.write('xe 0')

    def stop(self):
        """ Stops the sweep when the sweep is started by
        the XE command or the trigger input signal (``SP``). """
        self.write('sp 0')

    def set_digital_output(self, values):
        """ Outputs a 16-bit signal from the DIGITAL OUT output terminal
        on the rear panel. You can set up to 9 output data (``DIOS``).
        If there are multiple values specified, the data is output at
        intervals of about 2ms and fixed as the final data.

        :param values: Digital out bit values
        :type values: int or list

        .. note::
            The output of digital data to the DIGITAL OUT pin is only the bits
            specified by the DIOE command. Bits that are not specified will
            result in alarm output or unused, and no digital data will be output.
        """
        if isinstance(values, list):
            values = [str(i) for i in values]
            values = ",".join(values)
        self.write(f'dios 0,{values}')

    sweep_delay_time = Instrument.setting(
        "gdly 0,%.4e",
        """ Set the sweep delay time (Ta) or generation / delay time (Ta)
        of the master channel and slave channel during delayed sweep operation
        or synchronous operation between pulse measurements (``GDLY``).

        :type: float

        .. note::
            If the sweep delay time does not meet (Ta<Tw and Ta<Td+Tit),
            an execution error will occur and it will not be set:

            Tw: Pulse width
            Td: Major delay time
            Tit: Integration time
        """,
    )

    def append_sequence_command(self, command):
        valid_commands = [
            'jm', 'gdly', 'fl', 'dv', 'di', 'fxv', 'fxi', 'wv', 'wi', 'mdwv', 'mdwi', 'pv', 'pi',
            'pxv', 'pxi', 'pwv', 'pwi', 'mpwv', 'mpwi', 'rv', 'ri', 'mst', 'wt', 'cm', 'cmd', 'nug',
            'ofm', 'fmt', 'mbc', 'fmt', 'wm', 'cn', 'cl', 'opm', 'osl', 'ltl', 'tjm', 'xe', '*trg',
            'tot', 'sct', 'osig', 'dios', 'dioe', 'ian', 'tlnk', 'wait', 'sav', 'rcl', '*sre',
            '*ese', '*cls', 'coe', 'doe']

        if not self.store_to_sequence:
            raise ValueError("init_sequence() should be called first")

        for s in valid_commands:
            if s == command.lower()[:len(s)]:
                self.sequence.append(command)

    def init_sequence(self):
        """ This function starts the redirection of :meth:`~.write`
        to :meth:`~.store_sequence_command` to automatically create a sequence program.
        """
        self.sequence = []
        self.store_to_sequence = True
        self.sequence_line_count = 0

    def start_sequence(self, repeat=1):
        """ This function starts the sequence program which is
        initiated by :meth:`~.init_sequence` and ended by :meth:`~.end_sequence`.
        """
        self.start_sequence_program(1, self.sequence_line_count, repeat)

    def end_sequence(self):
        """ This function ends the sequence program which is
        initiated by :meth:`~.init_sequence`.
        """
        command = ''
        self.store_to_sequence = False
        for s in self.sequence:

            # Sequence memory has a maximum of 128x100 characters
            if len(command) + len(s) + 1 < 128:
                command += s + ';'
            else:
                self.sequence_line_count += 1
                if self.sequence_line_count > 100:
                    raise OSError(
                        f"{self.name} Error out of sequence memory")

                self.store_sequence_command(self.sequence_line_count, command)
                command = s + ';'

        self.sequence_line_count += 1
        self.store_sequence_command(self.sequence_line_count, command)

        self.sequence = []

    def sequence_wait(self, wait_mode, wait_value):
        """ Waits for program execution and is used only for sequence programs (``WAIT``).

        :param int wait_mode: Whether wait time (1) or trigger input count (2) is specified
        :param float wait_value: Wait time or trigger input count as specified by wait_mode

        This command has the following functions:

          * Make the execution of the next program wait for the specified time.
          * Makes the next program execution wait until the specified number of triggers is input.

        Regardless of the wait mode, if the wait data is 0, the wait operation is not performed.
        When the wait mode is "2", the following commands and signals can be used as trigger inputs:

          * XE (XE 0, XE 1, XE 2)
          * \\*TRG
          * GET command (group execute trigger)
          * Trigger input signal on rear panel

        """
        wait_mode = strict_discrete_set(wait_mode, [1, 2])
        self.write(f'wait {wait_mode},{wait_value}')

    def start_sequence_program(self, start, stop, repeat):
        """ Starts from the program number until the stop of the sequence program (``RU``).
        Executes sequentially up to the program number, and repeats for the number of times of
        specified.

        :param int start: Number of the program to start from ranging 1 to 100
        :param int stop: Number of the program to stop at ranging from 1 to 100
        :param int repeat: Number of times repeated from 1 to 100
        """
        start = truncated_range(start, [1, 100])
        stop = truncated_range(stop, [1, 100])
        repeat = truncated_range(repeat, [1, 100])

        self.write(f'ru 0,{start},{stop},{repeat}')

    def store_sequence_command(self, line, command):
        """ Stores the program to be executed in the sequence program (``ST``).
        If the program already exists, it is replaced with the new sequence.

        :param int line: Line number specified of memory location
        :param str command: Command(s) specified to be stored delimited by a semicolon (;)
        """
        line = truncated_range(line, [1, 100])
        if command[-1:] != ';':
            command += ';'
        self.write(f'st {line};{command}end')

    def interrupt_sequence_command(self, action):
        """ Interrupts the sequence program executed
        by the :py:meth:`~start_sequence_program` command (``SQSP``).

        :param action: Specifies sequence interruption setup
        :type action: :class:`SequenceInterruptionType`
        """
        action = strict_discrete_set(action, [1, 2, 3])
        self.write(f'sqsp {action}')

    sequence_program_number = Instrument.measurement(
        "lnub?",
        """ Measure the amount of program sequences stored in the sequence memory (``LNUB?``).
        """,
        cast=int,
    )

    def sequence_program_listing(self, line):
        """ This is a query command to know the command list stored in the
        program number of the sequence program memory (``LST?``).

        :param int action: Specifying the memory location for reading the commands
        :return: Commands stored in sequence memory
        :rtype: str
        """
        line = truncated_range(line, [1, 100])
        return self.ask('lst? {line}')

    def trigger_output_signal(self, trigger_output, alarm_output, scanner_output):
        """ Directly output the trigger output signal, alarm output signal,
        scanner (start/stop) output signal from GPIB (``OSIG``).

        :param int trigger_output: Number specifying type of trigger output
        :param int alarm_output: Number specifying type of alaram output
        :param int scanner_output: Number specifying the type of scanner output

        Trigger output:

        1. Do not output to trigger output.
        2. Output a negative pulse to the trigger output.

        Alarm output:

        1. Finish output GO, LO.HI both set to HI level. (reset)
        2. Finish output Set GO to LO level.
        3. Set home output LO to LO level.
        4. Terminate output HI to LO level.

        Scanner - (start/stop) output:

        1. Set the scanner scoot output to HI level. Output a negative pulse to the stop output.
        2. Make the scanner start output low.
        3. Output a HI level for the scanner start output and a negative pulse for the stop output.

        """
        trigger_output = strict_discrete_set(trigger_output, [1, 2])
        alarm_output = strict_discrete_set(alarm_output, [1, 2, 3, 4])
        scanner_output = strict_discrete_set(scanner_output, [1, 2, 3])

        self.write(f'osig 0,{trigger_output},{alarm_output},{scanner_output}')

    def set_output_format(self, delimiter_format, block_delimiter, terminator):
        """ Sets the format and terminator of the output data output by GPIB (``FMT``).

        :param int delimiter_format: Type of delimiter format
        :param int block_delimiter: Type of block delimiter
        :param int terminator: Type of termination character

        The output of <EOI> (End or Identify) is output at the following timing:
        1,2: Simultaneously with LF
        4: Simultaneously with the last output data

        If the output data format is specified as binary format,
        the terminator is fixed to <EOI> only and the terminator selection is ignored.

        delimiter_format:

            1. ASCII format with header
            2. No header, ASCII format
            3. Binary format

        block_delimiter:

            1. Make it the same as the terminator.
            2. Use semicolon ;
            3. Use comma ,

        terminator:

            1. CR, LF<EOI>
            2. LF<EOI>
            3. LF
            4. <EOI>

        === =================================================================================
        1st character header:
        -------------------------------------------------------------------------------------
        A)  Normal measurement data
        B)  Measurement data during overrange
        C)  Compliance (limiter) is working.
        D)  Oscillation detection is working.
        E)  [Indicates the generated data]
        F)  Measurement data when an error occurs in the search measurement
        Z)  Measurement data is not stored in the buffer memory.
        === =================================================================================

        === =================================================================================
        2nd character header:
        -------------------------------------------------------------------------------------
        A)  A-channel data during asynchronous operation (A-channel generation data)
        B)  B-channel data during asynchronous operation (B channel generation data)
        I)  A-channel data for synchronous, sweeping, delayed sweep, and double synchronous
            sweep operations.
        J)  B-channel data for synchronous, sweeping, delayed sweep, and double synchronous
            sweep operations.
        === =================================================================================

        === =================================================================================
        3rd character header:
        -------------------------------------------------------------------------------------
        A)  Current generation, voltage measurement (ISVM) [Current generation]
        B)  Voltage generation, current measurement (VSIM) [Voltage generation]
        C)  Current generation, current measurement (ISIM)
        D)  Voltage generation, voltage measurement (VSVM)
        E)  Current generation, external voltage measurement (IS, EXT, VM)
        F)  Voltage generation, external current measurement (VS, EXT, IM)
        G)  Current generation, external current measurement (IS, EXT. IM)
        H)  Voltage generation, external voltage measurement (VS, EXT, VM)
        Z)  The measurement data is not stored in the buffer memory.
        === =================================================================================

        === =================================================================================
        4th character header:
        -------------------------------------------------------------------------------------
        A)  No operation (fixed to A)
        B)  Null operation result
        C)  The result of the comparison operation is GO.
        D)  The result of the comparison operation is LO.
        E)  The result of the comparison operation is HI.
        F)  The result of null operation + comparison operation is GO.
        G)  The result of null operation + comparison operation is LO.
        H)  The result of null operation + comparison operation is HI.
        Z)  Measurement data is not stored in the buffer memory.
        === =================================================================================

        """
        delimiter_format = strict_discrete_set(delimiter_format, [1, 2, 3])
        block_delimiter = strict_discrete_set(block_delimiter, [1, 2, 3])
        terminator = strict_discrete_set(terminator, [1, 2, 3, 4])

        self.write(f'fmt 0,{delimiter_format},{block_delimiter},{terminator}')

    service_request_enable_register = Instrument.control(
        '*sre?', '*sre %i',
        """ Control the contents of the service request enable register (SRER)
        in the form of a :class:`SRER` ``IntFlag`` (``*SRE``).

        .. note::
            Bits other than the RQS bit are not cleared by serial polling.
            When :meth:`~.power_on_clear` is set, status byte enable register,
            SESER, device operation enable register, channel operation,
            the enable register is cleared and no SRQ is issued.

        """,
        validator=truncated_range,
        values=[0, 255],
        get_process=lambda v: SRER(int(v)),
    )

    event_status_enable = Instrument.control(
        '*ese?', '*ese %i',
        """ Control the standard event status enable. (``*ESE``) """,
        validator=truncated_range,
        values=[0, 255],
    )

    power_on_clear = Instrument.control(
        '*psc?', '*psc %i',
        """ Control the power on clear flag, takes
        values True or False. (``*PSC``) """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    device_operation_enable_register = Instrument.control(
        'doe?', 'doe %i',
        """ Control the device operation output enable register (DOER) (``DOE?``).
        """,
        validator=truncated_range,
        values=[0, 65535],
    )

    digital_out_enable_data = Instrument.control(
        'dioe?', 'dioe 0,%i',
        """ Control the contents of digital out enable data set (``DIOE``).
        """,
        validator=truncated_range,
        values=[0, 65535],
    )

    status_byte_register = Instrument.measurement(
        "*stb?",
        """ Measure the contents of the status byte register and MSS bits without
        using a serial poll (``*STB?``).

        The Status Byte Register has a hierarchical structure. ERR, DOP, ESB,
        and COP bits, except RQS and MAV, have lower-level status registers.
        Each register is paired with an enable register that can be selected
        to output to the Status Byte register or not. The status byte register
        also has an enable register, which allows you to select whether or
        not to issue a service request SRQ.

        .. note::

            \\*STB? command can read bit 6 as MSS (logical OR of other bits).
        """,
        cast=int,
    )

    event_status_register = Instrument.measurement(
        "*esr?",
        """ Measure the contents of the standard event status register (SESR) in
        the form of a :class:`SESR` ``IntFlag`` (``*ESR?``).

        .. note::
            SESR is cleared after being read.

        """,
        values=[0, 255],
        get_process=lambda v: SESR(int(v)),
    )

    device_operation_register = Instrument.measurement(
        "doc?",
        """ Measure the contents of the device operations register (DOR)
        in the form of a :class:`DOR` ``IntFlag`` (``DOC?``).

        """,
        values=range(0, 65535),
        get_process=lambda v: DOR(int(v)),
    )

    error_register = Instrument.measurement(
        "err?",
        """ Measure the contents of the error register (``ERR?``).
        """,
        cast=int,
    )

    self_test = Instrument.measurement(
        "*tst?",
        """ A query command that runs a self-test and reads the result (``*TST?``).
        """,
        cast=int,
    )

    trigger_link_function_enabled = Instrument.setting(
        "tlnk 0,%d",
        """ Set a boolean that controls whether the trigger link function is
        enabled, takes values of True or False. (``TLNK``)

        :type: bool
        """,
        validator=strict_discrete_set,
        values={False: 1, True: 2},
        map_values=True
    )

    display_enabled = Instrument.setting(
        "disp 0,%d",
        """ Set a boolean that controls whether the display is
        on or off, takes values of True or False. (``DISP``)

        :type: bool
        """,
        validator=strict_discrete_set,
        values={False: 2, True: 1},
        map_values=True
    )

    line_frequency = Instrument.setting(
        "lf 0,%d",
        """ Set the used power supply frequency (``LF``) to 50 or 60hz.
        With this command, the integration time per PLC for the measurement
        will be one cycle of the power supply frequency you are using.

        :type: int
        """,
        validator=strict_discrete_set,
        values={50: 1, 60: 2},
        map_values=True
    )

    store_config = Instrument.setting(
        "sav %d",
        """ Set the memory area for the config to be stored at (``SAV``).
        There are five memory areas from 0 to 4 for storing.

        :type: int
        """,
        validator=strict_range,
        values=range(0, 4),
    )

    load_config = Instrument.setting(
        "rcl %d",
        """ Set the memory area for the config to be loaded from (``RCL``).
        There are five areas (0~4) where parameters can be loaded by the RCL command.

        :type: int
        """,
        validator=strict_range,
        values=range(0, 4),
    )

    def set_lo_common_connection_relay(self, enable, lo_relay=None):
        """ Turn the connection relay on/off between the A channel
        LO (internal analog common) and the LO (internal analog common)
        of the B channel (``LTL``).

        :param bool enable: A boolean property that controls whether or not the
            connection relay is enabled. Valid values are True and False.
        :param lo_relay: A boolean property that controls whether or not the internal
            analog common relay is enabled. Valid values are True,
            False and None (don't change lo relay setting).
        :type lo_relay: bool, optional

        """
        enable = map_values(enable, {True: 2, False: 1})
        lo_relay = map_values(lo_relay, {True: 2, False: 1, None: 3})

        self.write(f'ltl 0,{enable},{lo_relay}')

    def parse_measurement(self, measurement):
        if ' ' in measurement:
            measurement = measurement.split(' ')
            return (float(measurement[1]), measurement[0])
        else:
            return (float(measurement), None)

    def read_measurement(self):
        """ Reads the triggered value, for example triggered by the external input.
        """
        return self.parse_measurement(self.read())[0]


class SMUChannel(Channel):
    """ Instantiated by main instrument class for every SMUChannel
    """

    def __init__(self, parent, id, voltage_range, current_range):
        super().__init__(parent, id)
        self.voltage_range = voltage_range[id]
        self.current_range = current_range[id]

    def insert_id(self, command):
        return command.format_map({self.placeholder: ord(self.id) - 64})

    def clear_measurement_buffer(self):
        """ Clears the measurement data buffer (``MBC``). """
        self.write('mbc {ch}')

    def set_output_type(self, output_type, measurement_type):
        """ Sets the output method and type of the GPIB output (``OFM``).

        :param output_type: A property that controls the type of output
        :type output_type: int or :class:`OutputType`
        :param measurement_type: A property that controls the measurement type
        :type measurement_type: int or :class:`MeasurementType`

        .. note::

            For the format of the output data, refer to :meth:`AdvantestR624X.set_output_format`.
            For DC and pulse measurements, the output method is fixed to '1' (real-time output).
            When the output method '3' (buffering output) is specified, the measured data is not
            stored in memory.

        """
        output_type = OutputType(output_type)
        measurement_type = MeasurementType(measurement_type)
        self.write(f'ofm {{ch}},{output_type.value},{measurement_type.value}')

    analog_input = Channel.setting(
        "fl {ch},%d",
        """ Set the analog input terminal (ANALOG INPUT) on the rear panel ON or OFF (``FL``).

        :type: int

            1. Turn off the analog input.
            2. Analog input ON, gain x1.
            3. Analog input ON, gain x2.5.

        """,
        validator=strict_range,
        values=range(1, 3),
    )

    trigger_output_timing = Channel.setting(
        "tot {ch},%d",
        """ Set the timing of the trigger output signal
        output from TRIGGER OUT on the rear panel (``TOT``).
        the status in the form of a :class:`TriggerOutputSignalTiming` ``IntFlag``.

        :type: :class:`.TriggerOutputSignalTiming`

        """,
        validator=strict_range,
        values=range(0, 63),
        # get_process=lambda v: TriggerOutputSignalTiming(int(v)),
    )

    def set_scanner_control(self, output, interlock):
        """  Sets the SCANNER CONTROL (START, STOP)
        output signal and INTERLOCK input signal on the rear panel (``SCT``).

        :param int output: A property that controls the scanner output
        :param int interlock: A property that controls the scanner interlock type

        output:

            1. Scanner, Turn off the control signal output.
            2. Output to the scanner control signal at the start / stop of the sweep.
            3. Operate / Standby Scanner, Output to the control signal.

        interlock:

            1. Turn off the interlock signal input.
            2. Set as a stamper when the interlock signal input is HI.
            3. When the interlock signal input is HI, it is on standby, and when it is LO, it is
               operated.

        """
        output = strict_discrete_set(output, [1, 2, 3])
        interlock = strict_discrete_set(interlock, [1, 2, 3])
        self.write(f'sct {{ch}},{output},{interlock}')

    trigger_input = Channel.setting(
        "tjm {ch},%d",
        """ Set the type of trigger input (``TJM``).

        :type: :class:`.TriggerInputType`

        +------------------------+---+---+---+
        | Trigger input types    | 1 | 2 | 3 |
        +========================+===+===+===+
        | \\*TRG                  | O | O | X |
        +------------------------+---+---+---+
        | XE 0                   | O | O | X |
        +------------------------+---+---+---+
        | XE Channel             | O | O | O |
        +------------------------+---+---+---+
        | GET                    | O | O | X |
        +------------------------+---+---+---+
        | Trigger input signal   | O | X | X |
        +------------------------+---+---+---+

        O can be used, X cannot be used

        .. note::

            The sweep operation cannot be started by the trigger input signal.
            Be sure to start it with the 'XE' command. Once started, it is
            possible to advance the sweep with a trigger input signal.

        """,
        validator=strict_range,
        values=range(1, 3),
        # get_process=lambda v: TriggerInputType(int(v)),
    )

    fast_mode_enabled = Channel.setting(
        "fl {ch},%d",
        """ Set the channel response mode to fast or slow,
        takes values of True or False (``FL``).

        :type: bool

        """,
        validator=strict_discrete_set,
        values={False: 2, True: 1},
        map_values=True
    )

    sample_hold_mode = Channel.setting(
        "mst {ch},%d",
        """ Set the integration time of the measurement (``MST``).

        :type: :class:`.SampleHold`

        .. note::

            - Valid only for pulse measurement and pulse sweep measurement.
            - In sample hold mode, the AD transformation is just before the fall
              of the pulse width.
            - The sample hold mode cannot be set during DC measurement and DC sweep
              measurement. When set to sample-and-hold mode, the integration time is 100 µs.
              However, in 2-channel synchronous operation, if one channel is in pulse
              generation and the other is in sample-and-hold mode, the DC measurement
              side also operates in sample-and-hold mode.
            - When performing pulse measurement and pulse sweep measurement, it
              is necessary to satisfy the restrictions on the pulse width (Tw),
              pulse period (Tp), and measure delay time (Td) of the WT command.
              If the constraint is not satisfied, the integration time is unchanged.
              To lengthen the integration time, first change the pulse width (Tw)
              and pulse period (Tp). When shortening the pulse width and pulse
              cycle, shorten the integration time first.

        """,
        validator=strict_discrete_set,
        values=[0, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17],
        # get_process=lambda v: SampleHold(int(v)),
    )

    def set_sample_mode(self, mode, auto_sampling=True):
        """ Sets synchronous, asynchronous, tracking operation
        and search measurement between channels (``JM``).

        :param mode: Sample Mode
        :type mode: :class:`.SampleMode`
        :param auto_sampling: Whether or not auto sampling is enabled, defaults to True
        :type auto_sampling: bool, optional

        """
        mode = SampleMode(mode)
        auto_sampling = map_values(auto_sampling, {True: 1, False: 2})

        self.write(f'jm {mode.value},{auto_sampling},{{ch}}')

    def set_timing_parameters(self, hold_time, measurement_delay, pulsed_width, pulsed_period):
        """ Set the hold time, measuring time, pulse width and the pulse period (``WT``).

        :param float hold_time: total amount of time for the complete pulse, until next pulse comes
        :param float measurement_delay: time between measurements
        :param float pulsed_width: Time specifying the pulse width
        :param float pulsed_period: Time specifying the pulse period

        .. note::

            Pulse measurement has the following restrictions depending on the pulse period (Tp)
            setting. (For pulse sweep measurements, there are no restrictions.)

                - Tp < 2ms : Not measured.
                - 2ms <= Tp < 10ms : Measure once every 5 ~ 20ms.
                - 10ms <= Tp: Measured at each pulse generation.

        """
        self.write(f"wt {{ch}},{hold_time:.4e},{measurement_delay:.4e},{pulsed_width:.4e},"
                   "{pulsed_period:.4e}")

    def select_for_output(self):
        """ This is a query command to select a channel and to
        output the measurement data (``FCH?``). When the output channel is selected
        by the FCH command, the measured data of the same channel is
        returned until the output channel is changed by the next FCH command.

        .. note::

            Reading measurements with the RMM command does not affect channel
            specification with the FCH command. In the default state,
            the measurement data of channel A is output.

        """
        self.write("fch_0{ch}?")

    def trigger(self):
        """ Measurement trigger command for sweep, start search measurement or sweep step action
        (``XE``).
        """
        self.write('xe {ch}')

    ###############
    # Voltage (V) #
    ###############

    def measure_voltage(self, enable=True, internal_measurement=True,
                        voltage_range=VoltageRange.AUTO):
        """ Sets the voltage measurement ON/OFF, measurement input, and
        voltage measurement range as parameters (``RV``).

        :param enable: boolean property that enables or disables voltage measurement.
            Valid values are True (Measure the voltage flowing at the OUTPUT terminal)
            and False (Measure the voltage from the rear panel -ANALOG COMMON).
        :type enable: bool, optional
        :param internal_measurement: A boolean property that enables or disables the internal
            measurement.
        :type internal_measurement: bool, optional
        :param voltage_range: Specifying voltage range
        :type voltage_range: :class:`.VoltageRange`, optional

        """
        voltage_range = VoltageRange(voltage_range)
        enable = map_values(enable, {True: 1, False: 2})
        internal_measurement = map_values(internal_measurement, {True: 1, False: 2})

        self.write(f'rv {{ch}},{enable},{internal_measurement},{voltage_range.value}')

    def voltage_source(self, source_range, source_value, current_compliance):
        """ Sets the source range, source value and the current compliance
        for the DC (constant voltage) measurement (``DV``).

        :param source_range: Specifying source range
        :type source_range: :class:`.VoltageRange`
        :param float source_value: A number specifying the source voltage value
        :param float current_compliance: A number specifying the current compliance

        .. note::

            Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
            The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        source_range = VoltageRange(source_range)
        source_value = truncated_range(source_value, self.voltage_range)

        self.write(f'dv {{ch}},{source_range.value},{source_value:.4e},{current_compliance:.4e}')

    def voltage_pulsed_source(self, source_range, pulse_value, base_value, current_compliance):
        """ Sets the source range, pulse value, base value and the current compliance
        of the pulse (voltage) measurement (``PV``).

        .. note::

            Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
            The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        source_range = VoltageRange(source_range)
        pulse_value = truncated_range(pulse_value, self.voltage_range)
        base_value = truncated_range(base_value, self.voltage_range)

        self.write(f'pv {{ch}},{source_range.value},{pulse_value:.4e},{base_value:.4e},'
                   '{current_compliance:.4e}')

    change_source_voltage = Channel.setting(
        "spot {ch},%.4e",
        """ Set new target voltage (``SPOT``).

        :type: float

        .. note::

            Only the DC action source value and pulse action pulse value
            are changed using the currently set DC action and pulse action parameters.
            Measure after the change and set the channel to output the measured data
            to the specified ch. In other words, it's the same as running the following
            commands:

              1. DV/DI/PV/PI
              2. XE xx
              3. FCH xx

        """,
    )

    def voltage_fixed_level_sweep(
            self, voltage_range, voltage_level, measurement_count, current_compliance, bias=0):
        """ Sets the fixed level sweep (voltage) generation range, level value,
        current compliance and the bias value (``FXV``).

        .. note::

            Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
            The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        voltage_range = VoltageRange(voltage_range)
        voltage_level = truncated_range(voltage_level, self.voltage_range)

        self.write(f'fxv {{ch}},{voltage_range.value},{voltage_level:.4e},'
                   '{measurement_count},{current_compliance:.4e},{bias:.4e}')

    def voltage_fixed_pulsed_sweep(
            self, voltage_range, pulse, base, measurement_count, current_compliance, bias=0):
        """ Sets the fixed pulse (voltage) sweep generation range,
        pulse value, base value, number of measurements, current compliance and the bias value
        (``PXV``).

        .. note::

            Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
            The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        voltage_range = VoltageRange(voltage_range)
        pulse = truncated_range(pulse, self.voltage_range)
        base = truncated_range(base, self.voltage_range)

        self.write(f'pxv {{ch}},{voltage_range.value},{pulse:.4e},{base:.4e},'
                   '{measurement_count},{current_compliance:.4e},{bias:.4e}')

    def voltage_sweep(
            self, sweep_mode, repeat, voltage_range, start_value, stop_value, steps,
            current_compliance, bias=0):
        """ Sets the sweep mode, number of repeats, source range,
        start value, stop value, number of steps, current compliance,
        and the bias value for staircase (linear/log) voltage sweep (``WV``).

        .. note::

            - Sweep mode, number of repeats, and number of steps are subject to the following
              restrictions.

                - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                    - When the OFM command sets the output data output method to 1 or 2 m x number
                      of refreshes x N <= 2048
                    - m x N <= 2048 when the OFM command sets the output data output method to 3.

            - Regardless of the specified current compliance polarity, both polarities (+ and -) are
              set.
            - The current compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        steps = truncated_range(steps, [2, 2048])
        voltage_range = VoltageRange(voltage_range)

        self.write(f'wv {{ch}},{sweep_mode.value},{repeat},{voltage_range.value},'
                   '{start_value:.4e},{stop_value:.4e},{steps}, '
                   '{current_compliance:.4e},{bias:.4e}')

    def voltage_pulsed_sweep(
            self, sweep_mode, repeat, voltage_range, base, start_value, stop_value, steps,
            current_compliance, bias=0):
        """ Sets the sweep mode, repeat count, generation range,
        base value, start value, stop value, number of steps, current compliance
        and the bias value for a pulse wave (linear/log) voltage sweep (``PWV``).

        .. note::

            - The sweep mode, number of refreshes, and number of steps are subject to the following
              restrictions:

                - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                    - When the OFM command sets the output data output method to 1 or 2 m x number
                      of refreshes x N <= 2048
                    - m x N <= 2048 when the OFM command sets the output data output method to 3.

            - For the current compliance polarity, regardless of the specified current compliance
              polarity, the compliance of both polarities (+ and -) is set.
            - The current compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        steps = truncated_range(steps, [2, 2048])
        voltage_range = VoltageRange(voltage_range)

        self.write(f'pwv {{ch}},{sweep_mode.value},{repeat},{voltage_range.value},{base:.4e},'
                   '{start_value:.4e},{stop_value:.4e},{steps},{current_compliance:.4e},'
                   '{bias:.4e}')

    def voltage_random_sweep(
            self, sweep_mode, repeat, start_address, stop_address, current_compliance, bias=0):
        """ Sets the sweep mode, repeat count, start address, stop address,
        current compliance and the bias value of constant voltage random sweep (``MDWV``).

        .. note::

          - Sweep mode, number of repeats, start address and stop address are subject to the
            following restrictions:

              - Start address < Stop address
              - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                  - When the OFM command sets the output data output method to 1 or 2 m x number of
                    refreshes x N <= 2048
                  - m x N <= 2048 when the OFM command sets the output data output method to 3.

          - Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
          - The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        start_address = truncated_range(start_address, [1, 2048])
        stop_address = truncated_range(stop_address, [1, 2048])

        self.write(f'mdwv {{ch}},{sweep_mode.value},{repeat},{start_address},{stop_address},'
                   '{current_compliance:.4e},{bias:.4e}')

    def voltage_random_pulsed_sweep(
            self, sweep_mode, repeat, start_address, stop_address, current_compliance, bias=0):
        """ Sets the sweep mode, repeat count, base value, start address,
        stop address, current compliance and the bias value of the constant voltage random pulse
        sweep (``MPWV``).

        .. note::

          - Sweep mode, number of repeats, start address and stop address are subject to the
            following restrictions:

              - Start address < Stop address
              - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                  - When the OFM command sets the output data output method to 1 or 2 m x number of
                    refreshes x N <= 2048
                  - m x N <= 2048 when the OFM command sets the output data output method to 3.

          - Regardless of the specified current compliance polarity, both polarities (+ and -) are
            set.
          - The current compliance range is automatically set to the minimum range that includes the
            set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        start_address = truncated_range(start_address, [1, 2048])
        stop_address = truncated_range(stop_address, [1, 2048])

        self.write(f'mpwv {{ch}},{sweep_mode.value},{repeat},{start_address},{stop_address},'
                   '{current_compliance:.4e},{bias:.4e}')

    def voltage_set_random_memory(self, address, voltage_range, output, current_compliance):
        """ The command stores the specified value to the randomly generated data memory (``RMS``).

        Stored generated values are swept within the specified memory
        address range by the MDWV, MDWI, MPWV, MPWI commands.

        """

        voltage_range = VoltageRange(voltage_range)
        address = truncated_range(address, [1, 2048])

        self.write(f'rms {address};dv{{ch}},{voltage_range.value},{output:.4e},'
                   '{current_compliance:.4e};rend')

    ###############
    # Current (A) #
    ###############

    def current_source(self, source_range, source_value, voltage_compliance):
        """ Sets the source range, source value, voltage compliance
        of the DC (constant current) measurement (``DI``).

        :param source_range: Specifying source range
        :type source_range: :class:`.CurrentRange`
        :param float source_value: A number specifying the source current value
        :param float voltage_compliance: A number specifying the voltage compliance

        .. note::

            Regardless of the specified voltage compliance polarity, both polarities (+ and -) are
            set.
            The voltage compliance range is automatically set to the minimum range that includes the
            set value.

        """
        source_range = CurrentRange(source_range)
        source_value = truncated_range(source_value, self.current_range)

        self.write(f'di {{ch}},{source_range.value},{source_value:.4e},{voltage_compliance:.4e}')

    def current_pulsed_source(self, source_range, pulse_value, base_value, voltage_compliance):
        """ Sets the source range, pulse value, base value and the voltage compliance
        of the pulse (current) measurement (``PI``).

        .. note::

            Regardless of the specified voltage compliance polarity, both polarities (+ and -) are
            set.
            The voltage compliance range is automatically set to the minimum range that includes the
            set value.

        """
        source_range = CurrentRange(source_range)
        pulse_value = truncated_range(pulse_value, self.current_range)
        base_value = truncated_range(base_value, self.current_range)

        self.write(f'pi {{ch}},{source_range.value},{pulse_value:.4e},{base_value:.4e},'
                   '{voltage_compliance:.4e}')

    change_source_current = Channel.setting(
        "spot {ch},%.4e",
        """ Set new target current (``SPOT``).

        :type: float

        .. note::

            Only the DC action source value and pulse action pulse value
            are changed using the currently set DC action and pulse action parameters.
            Measure after the change and set the channel to output the measured data
            to the specified ch. In other words, it's the same as running the following
            commands:

              1. DV/DI/PV/PI
              2. XE xx
              3. FCH xx

        """
    )

    def current_fixed_level_sweep(
            self, current_range, current_level, measurement_count, voltage_compliance, bias=0):
        """ Sets the fixed level sweep (current) generation range, level value,
        voltage compliance and the bias value (``FXI``).

        .. note::

            Regardless of the specified voltage compliance polarity, both polarities (+ and -) are
            set.
            The voltage compliance range is automatically set to the minimum range that includes the
            set value.

        """
        current_range = CurrentRange(current_range)

        self.write(f'fxi {{ch}},{current_range.value},{current_level:.4e},{measurement_count},'
                   '{voltage_compliance:.4e},{bias:.4e}')

    def current_fixed_pulsed_sweep(
            self, current_range, pulse, base, measurement_count, voltage_compliance, bias=0):
        """ Sets the fixed pulse (current) sweep generation range,
        pulse value, base value, number of measurements, voltage compliance and the bias value
        (``PXI``).

        .. note::

            Regardless of the specified voltage compliance polarity, both polarities of + and - are
            set.
            The voltage compliance range is automatically set to the minimum range that includes the
            set value.

        """
        current_range = CurrentRange(current_range)

        self.write(f'pxi {{ch}},{current_range.value},{pulse:.4e},{base:.4e},{measurement_count},'
                   '{voltage_compliance:.4e},{bias:.4e}')

    def current_sweep(
            self, sweep_mode, repeat, current_range, start_value, stop_value, steps,
            voltage_compliance, bias=0):
        """ Sets the sweep mode, number of repeats, source range,
        start value, stop value, number of steps, voltage compliance
        and bias value for the staircase (linear/log) current sweep (``WI``).

        .. note::

            - The sweep mode, number of refreshes, and number of steps are subject to the following
              restrictions:

                - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                    - When the OFM command sets the output data output method to 1 or 2, m x number
                      of repeats x N <= 2048.
                    - m x N <= 2048 when the OFM command sets the output data output method to 3.

            - Regardless of the specified voltage compliance polarity, both polarities (+ and -) are
              set.
            - The voltage compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        steps = truncated_range(steps, [2, 2048])
        current_range = CurrentRange(current_range)

        self.write(f'wi {{ch}},{sweep_mode.value},{repeat},{current_range.value},'
                   '{start_value:.4e},{stop_value:.4e},{steps},{voltage_compliance:.4e},'
                   '{bias:.4e}')

    def current_pulsed_sweep(
            self, sweep_mode, repeat, current_range, base, start_value, stop_value, steps,
            voltage_compliance, bias=0):
        """ Sets the sweep mode, repeat count, generation range,
        base value, start value, stop value, number of steps, voltage compliance
        and the bias value for a pulse wave (linear/log) current sweep (``PWI``).

        .. note::

            - The sweep mode, number of refreshes, and number of steps are subject to the following
              restrictions:

                - Let N = number of steps, m = l (one-way sweep), m = 2 (round-trip sweep).

                    - When the OFM command sets the output data output method to 1 or 2, m x number
                      of repeats x N <= 2048.
                    - m x N <= 2048 when the OFM command sets the output data output method to 3.

            - Regardless of the specified voltage compliance polarity, both polarities (+ and -) are
              set.
            - The voltage compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        steps = truncated_range(steps, [2, 2048])
        current_range = CurrentRange(current_range)

        self.write(
            f'pwi {{ch}},{sweep_mode.value},{repeat},{current_range.value},{base:.4e},'
            '{start_value:.4e},{stop_value:.4e},{steps},{voltage_compliance:.4e},{bias:.4e}')

    def measure_current(self, enable=True, internal_measurement=True,
                        current_range=CurrentRange.AUTO):
        """ Set the current measurement ON/OFF, measurement input, and current measurement range as
        parameters (``RI``).

        :param enable: boolean property that enables or disables current measurement.
            Valid values are True (Measure the current flowing at the OUTPUT terminal) and False
            (Measure the current from the rear panel -ANALOG COMMON).
        :type enable: bool, optional
        :param internal_measurement: A boolean property that enables or disables the internal
            measurement.
        :type internal_measurement: bool, optional
        :param current_range: Specifying voltage range
        :type current_range: :class:`.CurrentRange`, optional

        """
        current_range = CurrentRange(current_range)
        enable = map_values(enable, {True: 1, False: 2})
        internal_measurement = map_values(internal_measurement, {True: 1, False: 2})

        self.write(f'ri {{ch}},{enable},{internal_measurement},{current_range.value}')

    def current_random_sweep(
            self, sweep_mode, repeat, start_address, stop_address, current_compliance, bias=0):
        """ Sets the sweep mode, repeat count, start address,
        stop address, voltage compliance and the bias value of constant current random sweep
        (``MDWI``).

        .. note::

            - Sweep mode, number of repeats, start address and stop address are subject to the
              following restrictions:

                - Start address < Stop address
                - Let N = (stop number 1 - start number + 1), m = 1 (one-way sweep), m = 2
                  (round-trip sweep).

                    - When the output data output method is set to 1 or 2 with the OFM command m x
                      number of repeats x N <= 2048
                    - When the output data output method is set to 3 with the OFM command m x N <=
                      2048

            - For the voltage compliance polarity, regardless of the specified voltage compliance
              polarity, both polarities of + and – are set.
            - The voltage compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        start_address = truncated_range(start_address, [1, 2048])
        stop_address = truncated_range(stop_address, [1, 2048])

        self.write(
            f'mdwi {{ch}},{sweep_mode.value},{repeat},{start_address},{stop_address},'
            '{current_compliance:.4e},{bias:.4e}')

    def current_random_pulsed_sweep(
            self, sweep_mode, repeat, start_address, stop_address, current_compliance, bias=0):
        """ Sets the sweep mode, repeat count, base value, start address,
        stop address, voltage compliance and the bias value of constant current random pulse sweep
        (``MPWI``).

        .. note::
            - Sweep mode, number of repeats, start address and stop address are subject to the
              following restrictions:

                - Start address < Stop address
                - Let N = (stop number 1 - start number + 1), m = 1 (one-way sweep), m = 2
                  (round-trip sweep).

                    - When the output data output method is set to 1 or 2 with the OFM command m x
                      number of repeats x N <= 2048
                    - When the output data output method is set to 3 with the OFM command m x N <=
                      2048

            - For the voltage compliance polarity, regardless of the specified voltage compliance
              polarity, both polarities of + and – are set.
            - The voltage compliance range is automatically set to the minimum range that includes
              the set value.

        """
        sweep_mode = SweepMode(sweep_mode)
        repeat = truncated_range(repeat, [0, 1024])
        start_address = truncated_range(start_address, [1, 2048])
        stop_address = truncated_range(stop_address, [1, 2048])

        self.write(
            f'mpwi {{ch}},{sweep_mode.value},{repeat},{start_address},{stop_address},'
            '{current_compliance:.4e},{bias:.4e}')

    def current_set_random_memory(self, address, current_range, output, voltage_compliance):
        """ Store the current parameters to randomly generated data memory (``RMS``).

        Stored generated values are swept within the specified memory
        address range by the MDWV, MDWI, MPWV, MPWI commands.

        """
        current_range = CurrentRange(current_range)
        address = truncated_range(address, [1, 2048])

        self.write(
            f'rms {address};di{{ch}},{current_range.value},{output:.4e},'
            '{voltage_compliance:.4e};rend')

    def read_random_memory(self, address):
        """ Return memory specified by address location (``RMS?``).

        :param int address: Adress to specify memory location.
        :returns: Set values returned by the device from the specified address location.
        :rtype: str

        """
        address = truncated_range(address, [1, 2048])
        return self.ask(f'rms_1{{ch}}? {address}')

    def enable_source(self):
        """ Put the specified channel into an operating state (``CN``).
        """
        self.write('cn {ch}')

    def standby(self):
        """ Put the specified channel into standby state (``CL``).
        """
        self.write('cl {ch}')

    def stop(self):
        """ Stops the sweep when the sweep is started by the
        XE command or the trigger input signal (``SP``).
        """
        self.write('sp {ch}')

    def output_all_measurements(self):
        """ Output all measurements in the measurement
        data buffer of the specified channel (``RMM?``).

        .. note::

            For the output format, refer to :meth:`AdvantestR624X.set_output_format`.
            When a memory address where no measurement data is stored is read, 999.999E+99 will be
            returned.

        """
        self.write('rmm_0{ch}?')

    def read_measurement_from_addr(self, addr):
        """ Output only one measurement at the specified
        memory address from the measurement data buffer of the specified channel.

        :param int addr: Specifies the address to read from.
        :return: float Measurement data

        .. note::

            For the output format, refer to :meth:`AdvantestR624X.set_output_format`.
            When a memory address where no measurement data is stored is read, 999.999E+99 will be
            returned.

        """
        measurement = self.ask(f'rmm_1{{ch}}? {addr}')
        return self.parent.parse_measurement(measurement)

    measurement_count = Channel.measurement(
        "nub_0{ch}?",
        """ Measaure the number of measurements contained in the measurement
        data buffer (``NUB?``). """,
        cast=int
    )

    null_operation_enabled = Channel.setting(
        "nug {ch},%d",
        """ Set a boolean that controls whether the null operation
        is enabled, takes values of True or False (``NUG``).

        :type: bool

        .. Acquisition timing of null data::

            - Null data captures the next measurement data for which null computation is
              enabled as null data during DC measurement or pulse measurement.
            - A sweep operation does not capture null data.
            - If null calculation is enabled during sweep operation, null data obtained
              by DC operation or pulse operation will be used for calculation.
            - Indicates the timing of null data acquisition during DC operation.

        .. note::

            - Null data is not rewritten even if the null operation is disabled.
            - Null data is rewritten only when null operation is changed from OFF to ON or
              initialized in case of DC operation or pulse operation.

        """,
        validator=strict_discrete_set,
        values={False: 1, True: 2},
        map_values=True
    )

    def set_wire_mode(self, four_wire, lo_guard=True):
        """ Used to switch remote sense and to set the LO-GUARD relay ON/OFF.
        It operates regardless of operating state or standby state (``OSL``).

        :param bool four_wire: A boolean property that enables or disables four wire measurements.
            Valid values are True (enables 4-wire sensing) and False (enables two-terminal sensing).
        :param bool lo_guard: A boolean property that enables or disables the LO-GUARD relay.

        """
        four_wire = map_values(four_wire, {True: 1, False: 2})
        lo_guard = map_values(lo_guard, {True: 1, False: 2})

        self.write(f'osl {{ch}},{four_wire},{lo_guard}')

    auto_zero_enabled = Channel.setting(
        "cm {ch},%d",
        """ Set the auto zero option to ON or OFF. Valid values are
        True (enabled) and False (disabled) (``CM``).

        :type: bool

        This command sets auto zero (automatically calibrate the
        zero point of the measured value operation.

        1. Periodically perform auto zero.
        2. Auto zero once, no periodic auto zeros thereafter.

        When the auto zero mode is set to True, the following operations are performed.

        - For DC operation and pulse operation:

            - At the end of one sweep, if he has exceeded the last autozero by more than 10 seconds,
              he will do one autozero.
            - If sweep start is specified during auto zero, the sweep will start after auto zero
              ends.

        - Sweep operation

            - Auto zero is performed once every 10 seconds.
            - If measurement or pulse output is specified during auto zero, it will be executed
              after auto zero ends.

        """,
        validator=strict_discrete_set,
        values={False: 2, True: 1},
        map_values=True
    )

    def set_comparison_limits(self, comparison, voltage_value, upper_limit, lower_limit):
        """ Sets the channel ON/OFF based on the measurement comparison
        and the data of the upper and lower limits to be compared (``CMD``).

        :param bool comparison: A boolean property that controls whether or not
            the comparison function is enabled. Valid values are True or False.
        :param bool voltage_value: A boolean property that controls whether or not
            voltage or current values are passed. Valid values are True or False.
        :param float upper_limit: Number specifying the upper comparison limit
        :param float lower_limit: Number specifying the lower comparison limit

        """
        comparison = map_values(comparison, {True: 2, False: 1})
        voltage_value = map_values(voltage_value, {True: 1, False: 2})

        self.write(f'cmd {{ch}},{comparison},{voltage_value},{upper_limit:.4e},{lower_limit:.4e}')

    relay_mode = Channel.setting(
        "opm {ch},%d",
        """ Set the HI/LO relays for standby mode.
        This command does not operate the Operate Relay (``OPM``).

        :type: int

        1. When executing an operation only the HI side turns ON, in standby both HI and LO are
           turned OFF.
        2. When executing an operation only the LO side turns ON, in standby both HI and LO are
           turned OFF.
        3. When executing an operation both HI and LO turn ON, in standby both HI and LO are turned
           OFF.
        4. When executing an operation only the HI side turns ON, in standby only the HI side is
           turned OFF.

        """,
        validator=strict_range,
        values=range(1, 4),
    )

    operation_register = Channel.measurement(
        "coc_0{ch}?",
        """ Measure the contents of the Channel Operations Register (COR)
        in the form of a :class:`COR` ``IntFlag`` (``COC?``).

        """,
        values=range(0, 65535),
        get_process=lambda v: COR(int(v)),
    )

    output_enable_register = Channel.control(
        "coe_0{ch}?",
        "coe_0{ch} %d",
        """ Control the settings of the channel operation output enable
        register (COER) in the form of a :class:`COR` IntFlag ?(``COE?``).

        """,
        validator=strict_range,
        values=range(0, 65535),
        get_process=lambda v: COR(int(v)),
    )

    def calibration_init(self):
        """ Initialize the calibration data (``CINI``). """
        self.write('cini {ch}')

    def calibration_store_factor(self):
        """ Store the calibration factor
        in the non-volatile memory (EEPROM) (``CSRT``). """
        self.write('csrt {ch}')

    calibration_measured_value = Channel.setting(
        "std {ch},%.4e",
        """ Set the measured value measured by an external standard
        for the generated value of this instrument and start calibration (``STD``).

        :type: float

        """,
    )

    calibration_generation_factor = Channel.setting(
        "ccs {ch},%.4e",
        """ Set the increment or decrement for the generation
        calibration factor of the current generation range (``CCS``). It is used when
        the generated value deviates from the true value.

        :type: float

        """,
    )

    calibration_factor = Channel.setting(
        "ccm {ch},%.4e",
        """ Set the increment of the measurement calibration
        factor of the current measurement range (``CCM``).

        :type: float
        """,
    )


class AdvantestR6245(AdvantestR624X):
    """ Main instrument class for Advantest R6245 DC Voltage/Current Source/Monitor
    """
    voltage_range = {'A': [-220.0, 220.0], 'B': [-220.0, 220.0]}
    current_range = {'A': [-2.0, 2.0], 'B': [-2.0, 2.0]}

    ch_A = Instrument.ChannelCreator(SMUChannel, 'A',
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    ch_B = Instrument.ChannelCreator(SMUChannel, 'B',
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    def __init__(self, adapter, name="Advantest R6245 SourceMeter", **kwargs):
        kwargs
        super().__init__(
            adapter,
            name,
            **kwargs
        )


class AdvantestR6246(AdvantestR624X):
    """ Main instrument class for Advantest R6246 DC Voltage/Current Source/Monitor
    """
    voltage_range = {'A': [-62.0, 62.0], 'B': [-220.0, 220.0]}
    current_range = {'A': [-20.0, 20.0], 'B': [-2.0, 2.0]}

    ch_A = Instrument.ChannelCreator(SMUChannel, 'A',
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    ch_B = Instrument.ChannelCreator(SMUChannel, 'B',
                                     voltage_range=voltage_range,
                                     current_range=current_range)

    def __init__(self, adapter, name="Advantest R6246 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
