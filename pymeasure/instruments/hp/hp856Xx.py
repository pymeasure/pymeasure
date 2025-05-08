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
from math import log10
from enum import Enum, IntFlag
from datetime import datetime

import numpy as np

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, \
    joined_validators, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


try:
    from enum import StrEnum
except ImportError:
    class StrEnum(str, Enum):
        """Until StrEnum is broadly available / pymeasure relies on python <=
        3.10.x."""

        def __str__(self):
            return self.value


class WindowType(StrEnum):
    """Enumeration to represent the different window mode for FFT functions"""

    #: Flattop provides optimum amplitude accuracy
    Flattop = "FLATTOP"

    #: Hanning provides an amplitude accuracy/frequency resolution compromise
    Hanning = "HANNING"

    #: Uniform provides equal weighting of the time record for measuring transients.
    Uniform = "UNIFORM"


class StatusRegister(IntFlag):
    """Enumeration to represent the Status Register."""

    #: Request Service
    RQS = 64

    #: Set when error present
    ERROR_PRESENT = 32

    #: Any command is completed
    COMMAND_COMPLETE = 16

    #: Unused but sometimes set
    NA = 8

    #: Set when any sweep is completed
    END_OF_SWEEP = 4

    #: Set when display message appears
    MESSAGE = 2

    #: Trigger is activated
    TRIGGER = 1

    #: No Interrupts can interrupt the program sequence
    NONE = 0


class Trace(StrEnum):
    """Enumeration to represent either Trace A or Trace B."""

    #: Trace A
    A = "TRA"

    #: Trace B
    B = "TRB"


class SweepCoupleMode(StrEnum):
    """Enumeration."""

    #: Stimulus Response
    SpectrumAnalyzer = "SA"

    #: Spectrum Analyeze
    StimulusResponse = "SR"


class SweepOut(StrEnum):
    """Enumeration."""

    #: 0 - 10V Ramp
    Ramp = "RAMP"

    #: DC Ramp 0.5V / GHz
    Fav = "FAV"


class MixerMode(StrEnum):
    """Enumeration to represent the Mixer Mode of the HP8561B."""

    #: Mixer Mode Internal
    Internal = "INT"

    #: Mixer Mode External
    External = "EXT"


class SourceLevelingControlMode(StrEnum):
    """Enumeration to represent the Source Leveling Control Mode of the
    HP8560A."""

    #: Source Leveling Control Mode Internal
    Internal = "INT"

    #: Source Leveling Control Mode External
    External = "EXT"


class PeakSearchMode(StrEnum):
    """Enumeration to represent the Marker Peak Search Mode."""

    #: Place marker to the highest value on the trace
    High = "HI"

    #: Place marker to the next highest value on the trace
    NextHigh = "NH"

    #: Place marker to the next peak to the right
    NextRight = "NR"

    #: Place marker to the next peak to the left
    NextLeft = "NL"


class CouplingMode(StrEnum):
    """Enumeration to represent the Coupling Mode."""

    #: AC
    AC = "AC"

    #: DC
    DC = "DC"


class DemodulationMode(StrEnum):
    """Enumeration to represent the Demodulation Mode."""

    #: Amplitude Modulation
    Amplitude = "AM"

    #: Frequency Modulation
    Frequency = "FM"

    #: Demodulation Off
    Off = "OFF"


class TriggerMode(StrEnum):
    """Enumeration to represent the different trigger modes"""

    #: External Mode
    External = "EXT"

    #: Free Running
    Free = "FREE"

    #: Line Mode
    Line = "LINE"

    #: Video Mode
    Video = "VID"


class TraceDataFormat(StrEnum):
    """Enumeration to represent the different trace data formats."""

    #: A-Block format
    A_BLOCK = "A"

    #: Binary format
    BINARY = "B"

    #: I-Block format
    I_BLOCK = "I"

    #: ASCII format
    ASCII = "M"

    #: Real numbers format like are in Hz, volts, watts, dBm, dBmV, dBuV, dBV, or seconds.
    REAL = "P"


class FrequencyReference(StrEnum):
    """Enumeration to represent the frequency reference source."""

    #: Internal Frequency Reference
    Internal = "INT"

    #: External Frequency Standard
    External = "EXT"


class DetectionModes(StrEnum):
    """Enumeration to represent the Detection Modes."""

    #: Negative Peak Detection
    NegativePeak = "NEG"

    #: Normal Peak Detection
    Normal = "NRM"

    #: Positive Peak Detection
    PositivePeak = "POS"

    #: Sampl Mode Detection
    Sample = "SMP"


class AmplitudeUnits(StrEnum):
    """Enumeration to represent the amplitude units."""

    #: DB over millit Watt
    DBM = "DBM"

    #: DB over milli Volt
    DBMV = "DBMV"

    #: DB over micro Volt
    DBUV = "DBUV"

    #: Volts
    V = "V"

    #: Watt
    W = "W"

    #: Automatic Unit (Usually derives to 'DBM')
    AUTO = "AUTO"

    #: Manual Mode
    MANUAL = "MAN"


class ErrorCode:
    """
    Class to decode error codes from the spectrum analyzer.
    """
    __error_code_list = {
        0: ("NO ERR", "No Error at all"),
        100: ("PWRON", "Power-on state is invalid; default state is loaded"),
        101: ("NO STATE", "State to be RECALLed not valid or not SAVEd"),
        106: ("ABORTED!", "Current operation is aborted; HP-IB parser reset"),
        107: ("HELLO ??", "No HP-IB listener is present"),
        108: ("TIME OUT", "Analyzer timed out when acting as controller"),
        109: ("CtrlFail", "Analyzer unable to take control of the bus"),
        110: ("NOT CTRL", "Analyzer is not system controller"),
        111: ("# ARGMTS", "Command does not have enough arguments"),
        112: ("??CMD??", "Unrecognized command"),
        113: ("FREQ NQ!", "Command cannot have frequency units"),
        114: ("TIME NOG!", "Command cannot have time units"),
        115: ("AMPL NO!", "Command cannot have amplitude units"),
        116: ("PUNITS??", "Unrecognizable units"),
        117: ("NOP NUM", "Command cannot have numeric units"),
        118: ("NOP EP", "Enable parameter cannot be used"),
        119: ("NOP UPDN", "UP/DN are not valid arguments for command"),
        120: ("NOP ONOF", "ON/OFF are not valid arguments for command"),
        121: ("NOP ARG", "AUTO/MAN are not valid arguments for command"),
        122: ("NOP TRC", "Trace registers are not valid for command"),
        123: ("NOP ABLK", "A-block format not valid here"),
        124: ("NOP IBLK", "I-block format not valid here"),
        125: ("NOP STRNG", "Strings are not valid for this command"),
        126: ("NO ?", "This command cannot be queried"),
        127: ("BAD DTMD", "Not a valid peak detector mode"),
        128: ("PK WHAT?", "Not a valid peak search parameter"),
        129: ("PRE TERM", "Premature A-block termination"),
        130: ("BAD TDF", "Arguments are only for TDF command"),
        131: ("?? AM/FM", "AM/FM are not valid arguments for this command"),
        132: ("!FAV/RMP", "FAV/RAMP are not valid arguments for this command"),
        133: ("!INT/EXT", "INT/EXT are not valid arguments for this command"),
        134: ("??? ZERO", "ZERO is not a valid argument for this command"),
        135: ("??? CURR", "CURR is not a valid argument for this command"),
        136: ("??? FULL", "FULL is not a valid argument for this command"),
        137: ("??? LAST", "LAST is not a valid argument for this command"),
        138: ("!GRT/DSP", "GRT/DSP are not valid arguments for this command"),
        139: ("PLOTONLY", "Argument can only be used with PLOT command"),
        140: ("?? PWRON", "PWRON is not a valid argument for this command"),
        141: ("BAD ARG", "Argument can only be used with FDIAG command"),
        142: ("BAD ARG", "Query expected for FDIAG command"),
        143: ("NO PRESL", "No preselector hardware to use command with (HP 8562B)"),
        200: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        201: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        250: ("OUTOF RG", "ADC input is outside of ADC range"),
        251: ("NO IRQ", "Microprocessor not receiving interrupt from ADC"),
        300: ("YTO UNLK", "YTO (1ST LO) phase-locked loop (PLL) is unlocked"),
        301: ("YTO UNLK", "YTO PLL is unlocked"),
        302: ("OFF UNLK", "Offset Roller Oscillator PLL is unlocked"),
        303: ("XFR UNLK", "Transfer Roller Oscillator PLL is unlocked"),
        304: ("ROL UNLK", "Main Roller Oscillator PLL is unlocked"),
        305: ("FREQ ACC", "Frequency accuracy error"),
        306: ("FREQ ACC", "Frequency accuracy error"),
        307: ("FREQ ACC", "Frequency accuracy error"),
        308: ("FREQ ACC", "Frequency accuracy error"),
        309: ("FREQ ACC", "Frequency accuracy error"),
        310: ("FREQ ACC", "Frequency accuracy error"),
        311: ("FREQ ACC", "Frequency accuracy error"),
        312: ("FREQ ACC", "Frequency accuracy error"),
        313: ("FREQ ACC", "Frequency accuracy error"),
        314: ("FREQ ACC", "Frequency accuracy error"),
        315: ("FREQ ACC", "Frequency accuracy error"),
        316: ("FREQ ACC", "Frequency accuracy error"),
        317: ("FREQ ACC", "Frequency accuracy error"),
        318: ("FREQ ACC", "Frequency accuracy error"),
        319: ("FREQ ACC", "Frequency accuracy error"),
        320: ("FREQ ACC", "Frequency accuracy error"),
        321: ("FREQ ACC", "Frequency accuracy error"),
        322: ("FREQ ACC", "Frequency accuracy error"),
        323: ("FREQ ACC", "Frequency accuracy error"),
        324: ("FREQ ACC", "Frequency accuracy error"),
        325: ("FREQ ACC", "Frequency accuracy error"),
        326: ("FREQ ACC", "Frequency accuracy error"),
        327: ("OFF UNLK", "Offset Roller Oscillator PLL is unlocked"),
        328: ("FREQ ACC", "Frequency accuracy error"),
        329: ("FREQ ACC", "Frequency accuracy error"),
        331: ("FREQ ACC", "Frequency accuracy error"),
        333: ("600 UNLK", "600 MHz Reference Oscillator PLL is unlocked"),
        334: ("LO AMPL", "YTO (ist LO) unleveled"),
        400: ("AMPL 100", "Unable to adjust amplitude of 100 Hz resolution bandwidth"),
        401: ("AMPL 300", "Unable to adjust amplitude of 300 Hz resolution bandwidth"),
        402: ("AMPL 1K", "Unable to adjust amplitude of 1 kHz resolution bandwidth"),
        403: ("AMPL 3K", "Unable to adjust amplitude of 3 kHz resolution bandwidth"),
        404: ("AMPL 10K", "Unable to adjust amplitude of 10 kHz resolution bandwidth"),
        405: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        406: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        407: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        408: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        409: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        410: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        411: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        412: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        413: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        414: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        415: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        416: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        417: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        418: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        419: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        420: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        421: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        422: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        423: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        424: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        425: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        426: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        427: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        428: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        429: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        430: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        431: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        432: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        433: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        434: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        435: ("RBW 301", "Unable to adjust 300 Hz resolution bandwidth"),
        436: ("RBW 302", "Unable to adjust 300 Hz resolution bandwidth"),
        437: ("RBW 303", "Unable to adjust 300 Hz resolution bandwidth"),
        438: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        439: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        440: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        441: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        442: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        443: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        444: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        445: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        446: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        447: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        448: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        449: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        450: ("IF SYSTM", "IF hardware failure Check other error messages"),
        451: ("IF SYSTM", "IF hardware failure Check other error messages"),
        452: ("IF SYSTM", "IF hardware failure Check other error messages"),
        454: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        455: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        456: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        457: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        458: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        459: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        460: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        461: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        462: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        463: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        464: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        465: ("FREQ ACC", "Unable to adjust step gain amplifiers"),
        466: ("LIN AMPL", "Unable to adjust linear amplitude scale"),
        467: ("LOG AMPL", "Unable to adjust log amplitude scale"),
        468: ("LOG AMPL", "Unable to adjust log amplitude scale"),
        469: ("LOG AMPL", "Unable to adjust log amplitude scale"),
        470: ("LOG AMPL", "Unable to adjust log amplitude scale"),
        471: ("RBW 30K", "Unable to adjust 30 kHz resolution bandwidth"),
        472: ("RBW 100K", "Unable to adjust 100 kHz resolution bandwidth"),
        473: ("RBW 300K", "Unable to adjust 300 kHz resolution bandwidth"),
        474: ("RBW 1M", "Unable to adjust 1 MHz resolution bandwidth"),
        475: ("RBW 30K", "Unable to adjust 30 kHz resolution bandwidth"),
        476: ("RBW 100K", "Unable to adjust 30 kHz resolution bandwidth"),
        477: ("RBW 300K", "Unable to adjust 300 kHz resolution bandwidth"),
        478: ("RBW 1M", "Unable to adjust 1 MHz resolution bandwidth"),
        483: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        484: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        485: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        486: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        487: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        488: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        489: ("RBW 101", "Unable to adjust 100 Hz resolution bandwidth"),
        490: ("RBW 102", "Unable to adjust 100 Hz resolution bandwidth"),
        491: ("RBW 103", "Unable to adjust 100 Hz resolution bandwidth"),
        492: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        493: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        494: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        495: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        496: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        497: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        498: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        499: ("CAL UNLK", "A16 IF Adjustment Cal Oscillator is unlocked"),
        500: ("AMPL 30K", "Unable to adjust amplitude of 30 kHz resolution bandwidth"),
        501: ("AMPL 1M", "Unable to adjust amplitude of 100 kHz resolution bandwidth"),
        502: ("AMPL 3M", "Unable to adjust amplitude of 300 kHz resolution bandwidth"),
        503: ("AMPL 1M", "Unable to adjust amplitude of 1 MHz resolution bandwidth"),
        504: ("AMPL 30K", "Unable to adjust amplitude of 30 kHz resolution bandwidth"),
        505: ("AMPL 1M", "Unabie to adjust amplitude of 100 kHz resolution bandwidth"),
        506: ("AMPL 3M", "Unable to adjust amplitude of 300 kHz resolution bandwidth"),
        507: ("AMPL 1M", "Unable to adjust amplitude of 1 MHz resolution bandwidth"),
        508: ("AMPL 30K", "Unable to adjust amplitude of 30 kHz resolution bandwidth"),
        509: ("AMPL 1M", "Unable to adjust amplitude of 100 kHz resolution bandwidth"),
        510: ("AMPL 3M", "Unable to adjust amplitude of 300 kHz resolution bandwidth"),
        511: ("AMPL 1M", "Unable to adjust amplitude of 1 MHz resolution bandwidth"),
        512: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        513: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        514: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        515: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        516: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        517: ("RBW 100", "Unable to adjust 100 Hz resolution bandwidth"),
        518: ("RBW 300", "Unable to adjust 300 Hz resolution bandwidth"),
        519: ("RBW 1K", "Unable to adjust 1 kHz resolution bandwidth"),
        520: ("RBW 3K", "Unable to adjust 3 kHz resolution bandwidth"),
        521: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth"),
        522: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth SYM POLE 1"),
        523: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth SYM POLE 2"),
        524: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth SYM POLE 3"),
        525: ("RBW 10K", "Unable to adjust 10 kHz resolution bandwidth SYM POLE 4"),
        526: ("RBW <300", "Unable to adjust <300 Hz resolution bandwidths"),
        527: ("RBW <301", "Step gain correction failed for <300 Hz resolution bandwidth"),
        528: ("RBW <302", "Unable to adjust <300 Hz resolution bandwidths"),
        529: ("RBW <303", "Unable to adjust <300 Hz resolution bandwidths"),
        530: ("RBW <304", "Unable to adjust <300 Hz resolution bandwidths"),
        531: (
            "RBW <305", "Unable to adjust gain versus frequency for resoultion bandwidths <300 Hz"),
        532: ("RBW <306", "Absolute gain data for resolution bandwidths <300 Hz not acceptable"),
        533: ("RBW <307", "Unable to adjust <300 Hz resolution bandwidths"),
        534: ("RBW <308", "Unable to adjust frequency accuracy for resolution bandwidths <100 Hz"),
        535: ("RBW <309", "Unable to adjust <300 Hz resolution bandwidths"),
        536: ("RBW <310", "Unable to adjust <300 Hz resolution bandwidths"),
        537: ("RBW <311", "Unable to adjust <300 Hz resolution bandwidths"),
        538: ("RBW <312", "Unable to adjust <300 Hz resolution bandwidths"),
        539: ("RBW <313", "Unable to adjust <300 Hz resolution bandwidths"),
        540: ("RBW <314", "Unable to adjust <300 Hz resolution bandwidths"),
        551: ("AMPL", "Unable to adjust step gain amplifiers"),
        552: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        553: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        554: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        555: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        556: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        557: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        558: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        559: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        560: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        561: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        562: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        563: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        564: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        565: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        566: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        567: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        568: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        569: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        570: ("LOG AMPL", "Unable to adjust amplitude of log scale"),
        571: ("AMPL", "Unable to adjust step gain amplifiers"),
        572: ("AMPL 1M", "Unable to adjust amplitude of 1 MHz resolution bandwidth"),
        573: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        574: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        575: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        576: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        577: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        581: ("AMPL", "Unable to adjust 100 kHz and <10 kHz resolution bandwidths"),
        582: ("AMPL", "Unable to adjust 100 kHz and <10 kHz resolution bandwidths"),
        583: ("RBW 30K", "Unable to adjust 30 kHz resolution bandwidth"),
        584: ("RBW 100K", "Unable to adjust 100 kHz resolution bandwidth"),
        585: ("RBW 300K", "Unable to adjust 300 kHz resolution bandwidth"),
        586: ("RBW 1M", "Unable to adjust 1 MHz resolution bandwidth"),
        587: ("RBW 30K", "Unable to adjust 30 kHz resolution bandwidth"),
        588: ("RBW 300K", "Unable to adjust 100 kHz resolution bandwidth"),
        589: ("RBW 300K", "Unable to adjust 300 kHz resolution bandwidth"),
        590: ("RBW 1M", "Unable to adjust 1 MHz resolution bandwidth"),
        591: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        592: ("LOG AMPL", "Unable to adjust amplitude in log scale"),
        600: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        601: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        650: ("OUTOF RG", "ADC input is outside of the ADC range"),
        651: ("NO IRQ", "Microprocessor is not receiving interrupt from ADC"),
        700: ("EEROM", "Checksum error of EEROM A2U501"),
        701: ("AMPL CAL", "Checksum error of frequency response correction data"),
        702: ("ELAP TIM", "Checksum error of elapsed time data"),
        703: ("AMPL CAL", "Checksum error of frequency response correction data"),
        704: ("PRESELCT", "Checksum error of customer preselector peak data"),
        705: ("ROM U306", "Checksum error of program ROM A2U306"),
        706: ("ROM U307", "Checksum error of program ROM A2U307"),
        707: ("ROM U308", "Checksum error of program ROM A2U308"),
        708: ("ROM U309", "Checksum error of program ROM A2U309"),
        709: ("ROM U310", "Checksum error of program ROM A2U310"),
        710: ("ROM U311", "Checksum error of program ROM A2U311"),
        711: ("RAM U303", "Checksum error of system RAM A2U303"),
        712: ("RAM U302", "Checksum error of system RAM A2U302"),
        713: ("RAM U301", "Checksum error of system RAM A2U301"),
        714: ("RAM U300", "Checksum error of system RAM A2U300"),
        715: ("RAM U305", "Checksum error of system RAM A2U305"),
        716: ("RAM U304", "Checksum error of system RAM A2U304"),
        717: ("BAD uP!!", "Microprocessor not fully operational"),
        718: ("BATTERY?", "Nonvolatile RAM not working; check battery"),
        750: ("SYSTEM", "Hardware/ firmware interaction; check other errors"),
        751: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        752: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        753: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        754: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        755: ("SYSTEM", "Hardware/firmware interaction; check other errors"),
        900: ("TG UNLVL", "Tracking generator output is unleveled"),
        901: ("TGFrqLmt",
              "Tracking generator output unleveled because START FREQ is set "
              "below tracking generator frequency limit (300 kHz)"),
        902: ("BAD NORM",
              "The state of the stored trace does not match the current state of the analyzer"),
        903: ("&> DLMT", "Unnormalized trace A is off-screen with trace math or normalization on"),
        904: (
            "&> DLMT",
            "Calibration trace (trace B) is off-screen with trace math or normalization on")
    }

    # integer representation of error code
    code = 0

    def __init__(self, code):
        """Initialize an ErrorCode.

        :param code: Representing an error as id or short description
        :type code: str, int
        """
        if not (isinstance(code, int) or isinstance(code, str)):
            print(type(code))
            raise TypeError("Initialziation type for code must be integer or string")

        try:
            self.code = int(code)
            if self.code not in self.__error_code_list.keys():
                raise ValueError()

        except (ValueError, TypeError):
            raise ValueError("This error code doesn't exist")

        (self.short, self.long) = self.__error_code_list[self.code]

    def __repr__(self):
        return "ErrorCode(\"" + self.short + " - " + self.long + "\")"

    def __eq__(self, other):
        return self.code == other.code


class HP856Xx(Instrument):
    """Represents the HP856XX series spectrum analyzers.

    Don't use this class directly - use their derivative classes

    .. note::
        Most command descriptions are taken from the document:
        'HP 8560A, 8561B Operating & Programming'
    """

    def __init__(self, adapter, name="Hewlett-Packard HP856Xx", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    def adjust_all(self):
        """Activate the local oscillator (LO) and intermediate frequency (IF)
        alignment routines. These are the same routines that occur when is switched on.
        Commands following 'adjust_all' are not executed until after the analyzer has finished the
        alignment routines.
        """
        self.write("ADJALL")

    def set_crt_adjustment_pattern(self):
        """Activate a CRT adjustment pattern, shown in Figure 5-3. Use the
        X POSN, Y POSN, and TRACE ALIGN adjustments (available from the rear panel) to
        align the display. Use X POSN and Y POSN to move the display horizontally and vertically,
        respectively. Use TRACE ALIGN to straighten a tilted display. To remove the pattern from
        the screen, execute the :meth:`preset` command."""
        self.write("ADJCRT")

    adjust_if = Instrument.control(
        "ADJIF?", "ADJIF %s",
        """
        Control the automatic IF adjustment. This function is normally
        on. Because the IF is continuously adjusting, executing the IF alignment routine is seldom
        necessary. When the IF adjustment is not active, an "A" appears on the left side of the
        display.

        - `"FULL"` IF adjustment is done for all IF settings.
        - `"CURR"` IF adjustment is done only for the IF settings currently displayed.
        - `False` turns the continuous IF adjustment off.
        - `True` reactivates the continuous IF adjustment.

        Type: :code:`bool, str`
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0", "FULL": "FULL", "CURR": "CURR"},
        cast=str
    )

    trace_a_minus_b_enabled = Instrument.control(
        "AMB?", "AMB %s",
        """
        Control subtraction of the contents of trace B from trace A.
        It places the result, in dBm (when in log mode), in trace A. When in linear mode,
        the result is in volts. If trace A is in clear-write or max-hold mode, this function is
        continuous. When AMB is active, an "M" appears on the left side of the display.
        :attr:`trace_a_minus_b_plus_dl`  overrides AMB.

        Type: :code:`bool`

        .. warning::

            The displayed amplitude of each trace element falls in one of 600 data points.
            There are 10 points of overrange, which corresponds to one-sixth of a division
            Kg of overrange. When adding or subtracting trace data, any results exceeding
            this limit are clipped at the limit.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    trace_a_minus_b_plus_dl_enabled = Instrument.control(
        "AMBPL?", "AMBPL %s",
        """
        Control subtraction of trace B from trace A and addition to the display line,
        and stores the result in dBm (when in log mode) in trace A. When in linear
        mode, the result is in volts. If trace A is in clear-write or max-hold mode, this function
        is continuous. When this function is active, an "M" appears on the left side of the display.

        Type: :code:`bool`

        .. warning::

            The displayed amplitude of each trace element falls in one of 600 data points.
            There are 10 points of overrange, which corresponds to one-sixth of a division
            Kg of overrange. When adding or subtracting trace data, any results exceeding
            this limit are clipped at the limit.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    annotation_enabled = Instrument.control(
        "ANNOT?", "ANNOT %s",
        """
        Set the display annotation off or on.

        Type: :code:`bool`
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    attenuation = Instrument.control(
        "AT?", "AT %s",
        """
        Control the input attenuation in decade steps from 10 to 70 db (type 'int') or set to
        'AUTO' and 'MAN'(ual)

        Type: :code:`str`, :code:`int`

        .. code-block:: python

            instr.attenuation = 'AUTO'
            instr.attenuation = 60

        """,
        validator=joined_validators(strict_discrete_set, truncated_discrete_set),
        values=[["AUTO", "MAN"], np.arange(10, 80, 10)],
        cast=int,
    )

    amplitude_unit = Instrument.control(
        "AUNITS?", "AUNITS %s",
        """
        Control the amplitude unit with a selection of the following parameters: string
        'DBM', 'DBMV', 'DBUV', 'V', 'W', 'AUTO', 'MAN' or use the enum :class:`AmplitudeUnits`

        Type: :code:`str`

        .. code-block:: python

            instr.amplitude_unit = 'dBmV'
            instr.amplitude_unit = AmplitudeUnits.dBmV

        """,
        validator=strict_discrete_set,
        values=[str(e).upper() for e in AmplitudeUnits],
        set_process=lambda v: str(v).upper()
    )

    def write(self, command, **kwargs):
        if "{amplitude_unit}" in command:
            command = command.format(amplitude_unit=self.amplitude_unit)
        super().write(command, **kwargs)

    def set_auto_couple(self):
        """Set the video bandwidth, resolution bandwidth, input attenuation,
        sweep time, and center frequency step-size to coupled mode.

        These functions can be recoupled individually or all at once.
        The spectrum analyzer chooses appropriate values for these
        functions. The video bandwidth and resolution bandwidth are set
        according to the coupled ratios stored under :attr:`resolution_bandwidth_to_span_ratio`
        and :attr:`video_bandwidth_to_resolution_bandwidth`. If
        no ratios are chosen, default ratios (1.0 and 0.011,
        respectively) are used instead.
        """
        self.write("AUTOCPL")

    def exchange_traces(self):
        """Exchange the contents of trace A with those of trace B.

        If the traces are in clear-write or max-hold mode, the mode is
        changed to view. Otherwise, the traces remain in their initial
        mode.
        """
        self.write("AXB")

    def blank_trace(self, trace):
        """Blank the chosen trace from the display. The current contents of the
        trace remain in the trace but are not updated.

        .. code-block:: python

            instr.blank_trace('TRA')
            instr.blank_trace(Trace.A)

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B

        :type trace: str
        :raises TypeError: Type isn't 'string'
        :raises ValueError: Value is 'TRA' nor 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))
        self.write("BLANK " + trace)

    def subtract_display_line_from_trace_b(self):
        """Subtract the display line from trace B and places the result in dBm
        (when in log mode) in trace B, which is then set to view mode.

        In linear mode, the results are in volts.
        """
        self.write("BML")

    center_frequency = Instrument.control(
        "CF?", "CF %.11E Hz",
        """
        Control the center frequency in hertz and sets the spectrum analyzer to center
        frequency / span mode.

        The span remains constant; the start and stop frequencies change as
        the center frequency changes.

        Type: :code:`float`

        .. code-block:: python

            instr.center_frequency = 300.5e6
            if instr.center_frequency == 200e3:
                print("Correct frequency")

        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    def clear_write_trace(self, trace):
        """Set the chosen trace to clear-write mode. This mode sets each
        element of the chosen trace to the bottom-screen value; then new data
        from the detector is put in the trace with each sweep.

        .. code-block:: python

            instr.clear_write_trace('TRA')
            instr.clear_write_trace(Trace.A)

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B

        :type trace: str
        :raises TypeError: Type isn't 'string'
        :raises ValueError: Value is 'TRA' nor 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))

        self.write("CLRW " + trace)

    def set_continuous_sweep(self):
        """Set the instrument to continuous-sweep mode.

        This mode enables another sweep at the completion of the current
        sweep once the trigger conditions are met.
        """
        self.write("CONTS")

    coupling = Instrument.control(
        "COUPLE?", "COUPLE %s",
        """
        Control the input coupling of the spectrum analyzer.
        AC coupling protects the input of the analyzer from damaging dc signals, while limiting
        the lower frequency-range to 100 kHz (although the analyzer will tune down to 0 Hz with
        signal attenuation).

        Type: :code:`str`

        Takes a representation of the coupling mode, either from :class:`CouplingMode` or
        use 'AC' / 'DC'

        .. code-block:: python

            instr.coupling = 'AC'
            instr.coupling = CouplingMode.DC

            if instr.coupling == CouplingMode.DC:
                pass

        """,
        validator=strict_discrete_set,
        values=[e for e in CouplingMode]
    )

    demodulation_mode = Instrument.control(
        "DEMOD?", "DEMOD %s",
        """
        Control the demodulation mode of the spectrum analyzer. Either AM or FM demodulation,
        or turns the demodulation — off.
        Place a marker on a desired signal and then set :attr:`demodulation_mode`;
        demodulation takes place on this signal. If no marker is on, :attr:`demodulation_mode`
        automatically places a marker at the center of the trace and demodulates the frequency at
        that marker position. Use the volume and squelch controls to adjust the speaker and listen.

        Type: :code:`str`

        Takes a representation of the demodulation mode, either from :class:`DemodulationMode` or
        use 'OFF', 'AM', 'FM'

        .. code-block:: python

            instr.demodulation_mode = 'AC'
            instr.demodulation_mode = DemodulationMode.AM

            if instr.demodulation_mode == DemodulationMode.FM:
                instr.demodulation_mode = Demodulation.OFF

        """,
        validator=strict_discrete_set,
        values=[e for e in DemodulationMode]
    )

    demodulation_agc_enabled = Instrument.control(
        "DEMODAGC?", "DEMODAGC %s",
        """
        Control the demodulation automatic gain control (AGC).
        The AGC keeps the volume of the speaker relatively constant during AM demodulation. AGC
        is available only during AM demodulation and when the frequency span is greater than 0 Hz.

        Type: :code:`bool`

        .. code-block:: python

            instr.demodulation_agc = True

            if instr.demodulation_agc:
                instr.demodulation_agc = False

        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    demodulation_time = Instrument.control(
        "DEMODT?", "DEMODT %.11E",
        """
        Control the amount of time that the sweep pauses at the marker to
        demodulate a signal. The default value is 1 second. When the frequency span equals 0 Hz,
        demodulation is continuous, except when between sweeps. For truly continuous demodulation,
        set the frequency span to 0 Hz and the trigger mode to single sweep (see TM).
        Minimum 100 ms to maximum 60 s

        Type: :code:`float`

        .. code-block:: python

            # set the demodulation time to 1.2 seconds
            instr.demodulation_time = 1.2

            if instr.demodulation_time == 10:
                pass

        """,
        validator=strict_range,
        values=[100e-3, 60],
    )

    detector_mode = Instrument.control(
        "DET?", "DET %s",
        """
        Control the IF detector used for acquiring measurement data.
        This is normally a coupled function, in which the spectrum analyzer selects the
        appropriate detector mode. Four modes are available: normal, positive, negative, and sample.

        Type: :code:`str`

        Takes a representation of the detector mode, either from :class:`DetectionModes` or
        use 'NEG', 'NRM', 'POS', 'SMP'

        .. code-block:: python

            instr.detector_mode = DetectionModes.SMP
            instr.detector_mode = 'NEG'

            if instr.detector_mode == DetectionModes.SMP:
                pass

        """,
        validator=strict_discrete_set,
        values=[e for e in DetectionModes]
    )

    # now implemented as a property but due to the ability of the underlying gpib command to
    # specify the unit, there would be an alternative implementation as a method to allow the user
    # to modify the setting unit without manipulating it via the 'amplitude_unit' property
    display_line = Instrument.control(
        "DL?", "DL %g.11E {amplitude_unit}",
        """
        Control the horizontal display line for use as a visual aid or for
        computational purposes. The default value is 0 dBm.

        Type: :code:`float`

        Takes a value with the unit of :attr:`amplitude_unit`

        .. code-block:: python

            instr.display_line = -10

            if instr.display_line == 0:
                pass

        """
    )

    display_line_enabled = Instrument.setting(
        "DL %s",
        """
        Set the horizontal display line for use as a visual aid either on or off.

        .. code-block:: python

            instr.display_line_enabled = False

        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"}
    )

    done = Instrument.measurement(
        "DONE?",
        """
        Get back (e.g. return) when all commands in a command string
        entered before 'done' has been completed. Sending a :meth:`trigger_sweep` command
        before 'done' ensures that the spectrum analyzer will complete a full sweep before
        continuing on in a program.
        Depending on the timeout a timeout error from the adapter will raise before the spectrum
        analyzer can finish due to an extreme long sweep time

        .. code-block:: python

            instr.trigger_sweep()

            # wait for a full sweep and than 'do_something'
            if instr.done:
                do_something()

        """
    )

    def check_done(self):
        """
        Return when all commands in a command string
        entered before :meth:'check_done' has been completed. Sending a :meth:`trigger_sweep`
        command before 'check_done' ensures that the spectrum analyzer will complete a full sweep
        before continuing on in a program. Depending on the timeout a timeout error from the
        adapter will raise before the spectrum analyzer can finish due to an extreme long sweep
        time.

        .. code-block:: python

            instr.trigger_sweep()

            # wait for a full sweep and than 'do_something'
            instr.check_done()
            do_something()

        """
        # no error checking because there is no possibility to return anything else than '1'
        self.ask("DONE?")

    errors = Instrument.measurement(
        "ERR?",
        """
        Get a list of errors present (of type :class:`ErrorCode`). An empty list means there
        are no errors. Reading 'errors' clears all HP-IB errors. For best results, enter error
        data immediately after querying for errors.

        Type: :class:`ErrorCode`

        .. code-block:: python

            errors = instr.errors
            if len(errors) > 0:
                print(errors[0].code)

            for error in errors:
                print(error)

            if ErrorCode(112) in errors:
                print("yeah")

        Example result of this python snippet:

        .. code-block:: python

            112
            ErrorCode("??CMD?? - Unrecognized command")
            ErrorCode("NOP NUM - Command cannot have numeric units")
            yeah

        """,
        cast=ErrorCode,
        get_process=lambda v: v if isinstance(v, list) else []
    )

    elapsed_time = Instrument.measurement(
        "EL?",
        """
        Get the elapsed time (in hours) of analyzer operation.
        This value can be reset only by Hewlett-Packard.

        Type: :code:`int`

        .. code-block:: python

            print(elapsed_time)
            1998

        """,
        cast=int
    )

    start_frequency = Instrument.control(
        "FA?", "FA %.11E Hz",
        """
        Control the start frequency and set the spectrum analyzer to start-frequency/
        stop-frequency mode. If the start frequency exceeds the stop frequency, the stop frequency
        increases to equal the start frequency plus 100 Hz. The center frequency and span change
        with changes in the start frequency.

        Type: :code:`float`

        .. code-block:: python

            instr.start_frequency = 300.5e6
            if instr.start_frequency == 200e3:
                print("Correct frequency")

        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    stop_frequency = Instrument.control(
        "FB?", "FB %.11E Hz",
        """
        Control the stop frequency and set the spectrum analyzer to start-frequency/
        stop-frequency mode. If the stop frequency is less than the start frequency, the start
        frequency decreases to equal the stop frequency minus 100 Hz. The center frequency and
        span change with changes in the stop frequency.

        Type: :code:`float`

        .. code-block:: python

            instr.stop_frequency = 300.5e6
            if instr.stop_frequency == 200e3:
                print("Correct frequency")

        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    sampling_frequency = Instrument.measurement(
        "FDIAG SMP,?",
        """
        Get the sampling oscillator frequency corresponding to the current start
        frequency.
        Diagnostic Attribute

        Type: :code:`float`
        """
    )

    lo_frequency = Instrument.measurement(
        "FDIAG LO,?",
        """
        Get the first local oscillator frequency corresponding to the current start
        frequency.
        Diagnostic Attribute

        Type: :code:`float`
        """
    )

    mroll_frequency = Instrument.measurement(
        "FDIAG MROLL,?",
        """
        Get the main roller oscillator frequency corresponding to the current start
        frequency, except then the resolution bandwidth is less than or equal to 100 Hz.

        Diagnostic Attribute

        Type: :code:`float`
        """
    )

    oroll_frequency = Instrument.measurement(
        "FDIAG OROLL,?",
        """
        Get the offset roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.

        Diagnostic Attribute

        Type: :code:`float`
        """
    )

    xroll_frequency = Instrument.measurement(
        "FDIAG XROLL,?",
        """
        Get the transfer roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.

        Diagnostic Attribute

        Type: :code:`float`
        """
    )

    sampler_harmonic_number = Instrument.measurement(
        "FDIAG HARM,?",
        """
        Get the sampler harmonic number corresponding to the current start
        frequency.

        Diagnostic Attribute

        Type: :code:`int`
        """,
        get_process=lambda v: int(float(v))
    )

    # practically you could also write "OFF" to actively disable it or reset via "IP"
    frequency_display_enabled = Instrument.measurement(
        "FDSP?",
        """
        Get the state of all annotations that describes the spectrum analyzer frequency.
        returns 'False' if no annotations are shown and vice versa 'True'. This includes the start
        and stop frequencies, the center frequency, the frequency span, marker readouts, the center
        frequency step-size, and signal identification to center frequency.  To retrieve the
        frequency data, query the spectrum analyzer.

        Type: :code:`bool`

        .. code-block:: python

            if instr.frequency_display:
                print("Frequencies get displayed")

        """,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    def do_fft(self, source, destination, window):
        """Calculate and show a discrete Fourier transform.

        The FFT command performs a discrete Fourier transform on the source
        trace array and stores the logarithms of the magnitudes of the results
        in the destination array. The maximum length of any of the traces is
        601 points. FFT is designed to be used in transforming zero-span
        amplitude-modulation information into the frequency domain. Performing
        an FFT on a frequency sweep will not provide time-domain results. The
        FFT results are displayed on the spectrum analyzer in a logarithmic
        amplitude scale. For the horizontal dimension, the frequency at the
        left side of the graph is 0 Hz, and at the right side is Finax- Fmax is
        equal to 300 divided by sweep time. As an example, if the sweep time of
        the analyzer is 60 ms, Fmax equals 5 kHz. The FFT algorithm assumes
        that the sampled signal is periodic with an integral number of periods
        within the time-record length (that is, the sweep time of the
        analyzer). Given this assumption, the transform computed is that of a
        time waveform of infinite duration, formed of concatenated time
        records. In actual measurements, the number of periods of the sampled
        signal within the time record may not be integral. In this case, there
        is a step discontinuity at the intersections of the concatenated time
        records in the assumed time waveform of infinite duration. This step
        discontinuity causes measurement errors, both amplitude uncertainty
        (where the signal level appears to vary with small changes in
        frequency) and frequency resolution (due to filter shape factor and
        sidelobes). Windows are weighting functions that are applied to the
        input data to force the ends of that data smoothly to zero, thus
        reducing the step discontinuity and reducing measuremen errors.

        :param source: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :param destination: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :param window: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B

        :type source: str
        :type destination: str
        :type window: str
        """
        if not isinstance(source, str):
            raise TypeError("Should be of type string but is '%s'" % type(source))

        if not isinstance(destination, str):
            raise TypeError("Should be of type string but is '%s'" % type(destination))

        if not isinstance(window, str):
            raise TypeError("Should be of type string but is '%s'" % type(window))

        if source not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           source))
        if destination not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           destination))
        if window not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           window))
        self.write("FFT %s,%s,%s" % (source, destination, window))

    frequency_offset = Instrument.control(
        "FOFFSET?", "FOFFSET %.11E Hz",
        """
        Control an offset added to the displayed absolute-frequency values,
        including marker-frequency values.

        It does not affect the frequency range of the sweep, nor
        does it affect relative frequency readouts. When this function is active, an "F" appears on
        the left side of the display.
        Changes all the following frequency measurements.

        Type: :code:`float`

        .. code-block:: python

            instr.frequency_offset = 2e6
            if instr.frequency_offset == 2e6:
                print("Correct frequency")

        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    frequency_reference_source = Instrument.control(
        "FREF?", "FREF %s",
        """
        Control the frequency reference source.
        Select either the internal frequency reference (INT) or supply your own external
        reference (EXT). An external reference must be 10 MHz (+100 Hz) at a minimum amplitude of
        0 dBm. Connect the external reference to J9 (10 MHz REF IN/OUT) on the rear panel. When
        the external mode is selected, an "X" appears on the left edge of the display.

        Type: :code:`str`

        Takes element of :class:`FrequencyReference` or use 'INT', 'EXT'

        .. code-block:: python

            instr.frequency_reference_source = 'INT'
            instr.frequency_reference_source = FrequencyReference.EXT

            if instr.frequency_reference_source == FrequencyReference.INT:
                instr.frequency_reference_source = FrequencyReference.EXT

        """,
        validator=strict_discrete_set,
        values=[e for e in FrequencyReference]
    )

    def set_full_span(self):
        """Set the spectrum analyzer to the full frequency span as defined by
        the instrument.

        The full span is 2.9 GHz for the HP 8560A. For the HP 8561B, the
        full span is 6.5 GHz.
        """
        self.write("FS")

    graticule_enabled = Instrument.control(
        "GRAT?", "GRAT %s",
        """
        Control the display graticule. Switch it either on or off.

        Type: :class:`bool`

        .. code-block:: python

            instr.graticule = True

            if instr.graticule:
                pass

        """,
        map_values=True,
        values={True: "1", False: "0"},
        validator=strict_discrete_set,
        cast=str
    )

    def hold(self):
        """Freeze the active function at its current value.

        If no function is active, no operation takes place.
        """
        self.write("HD")

    id = Instrument.measurement(
        "ID?",
        """
        Get the identification of the device with software and hardware revision (e.g. HP8560A,002,
        H03)

        Type: :class:`str`

        .. code-block:: python

            print(instr.id)
            HP8560A,002,H02

        """,
        maxsplit=0,
        cast=str
    )

    def preset(self):
        """Set the spectrum analyzer to a known, predefined state.

        'preset' does not affect the contents of any data or trace
        registers or stored preselector data. 'preset' does not clear
        the input or output data buffers;
        """
        self.write("IP")

    logarithmic_scale = Instrument.control(
        "LG?", "LG %d DB",
        """
        Control the logarithmic amplitude scale. When in linear
        mode, querying 'logarithmic_scale' returns a “0”.
        Allowed values are 0, 1, 2, 5, 10

        Type: :class:`int`

        .. code-block:: python

            if instr.logarithmic_scale:
                pass

            # set the scale to 10 db per division
            instr.logarithmic_scale = 10

        """,
        cast=int,
        validator=strict_discrete_set,
        values=[0, 1, 2, 5, 10]
    )

    def set_linear_scale(self):
        """Set the spectrum analyzers display to linear amplitude scale.

        Measurements made on a linear scale can be read out in any
        units.
        """
        self.write("LN")

    def set_minimum_hold(self, trace):
        """Update the chosen trace with the minimum signal level detected at
        each trace-data point from subsequent sweeps. This function employs the
        negative peak detector (refer to the :attr:`detector_mode` command).

        .. code-block:: python

            instr.minimum_hold('TRA')
            instr.minimum_hold(Trace.A)

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B

        :type trace: str
        :raises TypeError: Type isn't 'string'
        :raises ValueError: Value is 'TRA' nor 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))

        self.write("MINH %s" % trace)

    marker_amplitude = Instrument.measurement(
        "MKA?",
        """
        Get the amplitude of the active marker. If no marker is active, MKA
        places a marker at the center of the trace and returns that amplitude value.
        In the :meth:`amplitude_unit` unit.

        Type: :code:`float`

        .. code-block:: python

            level = instr.marker_amplitude
            unit = instr.amplitude_unit
            print("Level: %f %s" % (level, unit))

        """
    )

    def set_marker_to_center_frequency(self):
        """Set the center frequency to the frequency value of an active
        marker."""
        self.write("MKCF")

    marker_delta = Instrument.control(
        "MKD?", "MKD %.11E Hz",
        """
        Control a second marker on the trace. The parameter value specifies the distance
        in frequency or time (when in zero span) between the two markers.
        If queried - returns the frequency or time of the second marker.

        Type: :code:`float`

        .. code-block:: python

            # place second marker 1 MHz apart from the first marker
            instr.marker_delta = 1e6

            # print frequency of second marker in case it got moved automatically
            print(instr.marker_delta)

        """
    )

    # the documentation mentions this command, but it doesn't work on my unit and a
    # reference unit so I leave it here for reference but commented out
    #
    # marker_reciprocal = Instrument.control(
    #    "MKDR?", "MKDR %.11E",
    #    """
    #    Return the reciprocal of the frequency or time (when in zero span)
    #    difference between two markers.
    #    """
    # )

    marker_frequency = Instrument.control(
        "MKF?", "MKF %.11E Hz",
        """
        Control the frequency of the active marker.
        Default units are in Hertz.

        Type: :code:`float`

        .. code-block:: python

            # place marker no. 1 at 100 MHz
            instr.marker_frequency = 100e6

            # print frequency of the marker in case it got moved automatically
            print(instr.marker_frequency)

        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    frequency_counter_mode_enabled = Instrument.setting(
        "MKFC %s",
        """
        Set the device into a frequency counter mode that counts the frequency of the active
        marker or the difference in frequency between two markers. If no marker
        is active, 'frequency_counter_mode_enabled' places a marker at the center of
        the trace and counts that marker frequency. The frequency counter
        provides a more accurate frequency reading; it pauses at the marker,
        counts the value, then continues the sweep. To adjust the frequency
        counter resolution, use the 'frequency_counter_resolution' command. To
        return the counter value, use the 'marker_frequency' command.

        .. code-block:: python

            instr.frequency_counter_mode_enabled = True
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    frequency_counter_resolution = Instrument.control(
        "MKFCR?", "MKFCR %d Hz",
        """
        Control the resolution of the frequency counter. Refer to the 'frequency_counter_mode'
        command. The default value is 10 kHz.

        Type :code:`int`

         .. code-block:: python

            # activate frequency counter mode
            instr.frequency_counter_mode = True

            # adjust resolution to 1 Hz
            instr.frequency_counter_resolution = 1

            if instr.frequency_counter_resolution:
                pass

        """,
        validator=strict_range,
        values=[1, 1e1, 1e2, 1e3, 1e4, 1e5, 1e6],
        maxsplit=0,
        preprocess_reply=lambda v: str(int(float(v))),
        cast=int
    )

    def set_marker_minimum(self):
        """Place an active marker on the minimum signal detected on a trace."""
        self.write("MKMIN")

    # here would be the implementation of the command 'marker_normal' ('MKN') but
    # it has no advantage over the 'marker_frequency' command except if no marker is active it
    # places it automagically to the center of the trace (I think there's no sense in
    # implementing it here)

    marker_noise_mode_enabled = Instrument.control(
        "MKNOISE?", "MKNOISE %s",
        """
        Control the detector mode to sample and compute the average of 32 data points (16 points
        on one side of the marker, the marker itself, and 15 points on the other side of the
        marker). This average is corrected for effects of the log or linear amplifier, bandwidth
        shape factor, IF detector, and resolution bandwidth. If two markers are on (whether in
        'marker_delta' mode or 1/marker delta mode), 'marker_noise_mode_enabled' works on the active
        marker and not on the anchor marker. This allows you to measure signal-to-noise density
        directly. To query the value, use the 'marker_amplitude' command.

        Type: :code:`bool`

        .. code-block:: python

            # activate signal-to-noise density mode
            instr.marker_noise_mode_enabled = True

            # get noise density by `marker_amplitude`
            print("Signal-to-noise density: %d dbm / Hz" % instr.marker_amplitude)

        """,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    def deactivate_marker(self, all_markers=False):
        """Turn off the active marker or, if specified, turn off all markers.

        :param all_markers: If True the call deactivates all markers, if false only the currently
            active marker (optional)
        :type all_markers: bool

        .. code-block:: python

            # place first marker at 300 MHz
            instr.marker_frequency = 300e6

            # place second marker 2 MHz apart from first
            instr.marker_delta = 2e6

            # deactivate active marker (delta marker)
            instr.deactivate_marker()

            # deactivate all markers
            instr.deactivate_marker(all_markers=True)
        """
        if all_markers:
            self.write("MKOFF ALL")
        else:
            self.write("MKOFF")

    def search_peak(self, mode):
        """Place a marker on the highest point on a trace, the next-highest
        point, the next-left peak, or the next-right peak. The default is 'HI'
        (highest point). The trace peaks must meet the criteria of the marker
        threshold and peak excursion functions in order for a peak to be found.
        See also the :attr:`peak_threshold` and :attr:`peak_excursion`
        commands.

        :param mode: Takes 'HI', 'NH', 'NR', 'NL' or the enumeration :class:`PeakSearchMode`
        :type mode: str

        .. code-block:: python

            instr.search_peak('NL')
            instr.search_peak(PeakSearchMode.NextHigh)
        """
        if not isinstance(mode, str):
            raise TypeError("Should be of type string but is '%s'" % type(mode))

        if mode not in [e for e in PeakSearchMode]:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             ([e for e in PeakSearchMode], mode))

        self.write("MKPK %s" % mode)

    marker_threshold = Instrument.control(
        "MKPT?", "MKPT %g {amplitude_unit}",
        """
        Control the minimum amplitude level from which a peak on the trace can
        be detected. The default value is -130 dBm. See also the :attr:`peak_excursion` command.
        Any portion of a peak that falls below the peak threshold is used to satisfy the peak
        excursion criteria. For example, a peak that is equal to 3 dB above the threshold when
        the peak excursion is equal to 6 dB will be found if the peak extends an additional 3 dB
        or more below the threshold level. Maximum 30 db to minimum -200 db.

        Type: :code:`signed int`

        .. code-block:: python

            instr.marker_threshold = -70
            if instr.marker_threshold > -80:
                pass

        """,
        validator=strict_range,
        values=[-200, 30]
    )

    peak_excursion = Instrument.control(
        "MKPX?", "MKPX %g DB",
        """
        Control what constitutes a peak on a trace. The chosen value specifies
        the amount that a trace must increase monotonically, then decrease monotonically, in order
        to be a peak. For example, if the peak excursion is 10 dB, the amplitude of the sides of a
        candidate peak must descend at least 10 dB in order to be considered a peak (see Figure 5-4)
        The default value is 6 dB. In linear mode, enter the marker peak excursion as a unit-less
        number.
        Any portion of a peak that falls below the peak threshold is also used to satisfy the peak
        excursion criteria. For example, a peak that is equal to 3 dB above the threshold when the
        peak excursion is equal to 6 dB will be found if the peak extends an additional 3 dB or more
        below the threshold level.

        Type: :code:`float`

        .. code-block:: python

            instr.peak_excursion = 2
            if instr.peak_excursion == 2:
                pass

        """,
        validator=strict_range,
        values=[0.1, 99]
    )

    def set_marker_to_reference_level(self):
        """Set the reference level to the amplitude of an active marker.

        If no marker is active, 'marker_to_reference_level' places a
        marker at the center of the trace and uses that marker amplitude
        to set the reference level.
        """
        self.write("MKRL")

    def set_marker_delta_to_span(self):
        """Set the frequency span equal to the frequency difference between two
        markers on a trace.

        The start frequency is set equal to the frequency of the left-
        most marker and the stop frequency is set equal to the frequency
        of the right-most marker.
        """
        self.write("MKSP")

    def set_marker_to_center_frequency_step_size(self):
        """Set the center frequency step-size equal to the frequency value of
        the active marker."""
        self.write("MKSS")

    marker_time = Instrument.control(
        "MKT?", "MKT %gS",
        """
        Control the marker's time value. Default units are seconds.

        Type: :code:`float`

        .. code-block:: python

            # set marker at sweep time corresponding second two
            instr.marker_time = 2

            if instr.marker_time == 2:
                pass

        """
    )

    marker_signal_tracking_enabled = Instrument.control(
        "MKTRACK?", "MKTRACK %s",
        """
        Control whether the center frequency follows the active marker.

        This is done after every sweep, thus maintaining the marker value at the
        center frequency. This allows you to “zoom in” quickly from a wide span to a narrow one,
        without losing the signal from the screen. Or, use 'marker_signal_tracking_enabled' to keep
        a slowly drifting signal centered on the display. When this function is active,
        a "K" appears on the left edge of the display.

        Type: :code:`bool`
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: "1", False: "0"},
        cast=str
    )

    mixer_level = Instrument.control(
        "ML?", "ML %d DB",
        """
        Control the maximum signal level that is at the input mixer. The
        attenuator automatically adjusts to ensure that this level is not exceeded for signals less
        than the reference level. From -80 to -10 DB.

        Type: :code:`int`
        """,
        validator=strict_range,
        cast=int,
        values=[-80, -10]
    )

    def set_maximum_hold(self, trace):
        """Set the chosen trace with the maximum signal level detected at each
        trace-data point from subsequent sweeps. This function employs the
        positive peak detector (refer to the :attr:`detector_mode` command).
        The detector mode can be changed, if desired, after max hold is
        initialized.

        .. code-block:: python

            instr.maximum_hold('TRA')
            instr.maximum_hold(Trace.A)

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B

        :type trace: str
        :raises TypeError: Type isn't 'string'
        :raises ValueError: Value is 'TRA' nor 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))

        self.write("MXMH %s" % trace)

    normalize_trace_data_enabled = Instrument.control(
        "NORMLIZE?", "NORMLIZE %s",
        """
        Control the normalization routine for
        stimulus-response measurements. This function subtracts trace B from trace A, offsets the
        result by the value of the normalized reference position
        (:attr:`normalized_reference_level`), and displays the result in trace A.
        'normalize_trace_data_enabled' is intended for use with the :meth:`store_open` and
        :meth:`store_short` or :meth:`store_thru` commands. These functions are used to store a
        reference trace into trace B.
        Refer to the respective command descriptions for more information.
        Accurate normalization occurs only if the reference trace and the measured trace are
        on-screen. If any of these traces are off-screen, an error message will be displayed.
        If the error message ERR 903 A > DLMT is displayed, the range level (RL) can be adjusted
        to move the measured response within the displayed measurement range of the analyzer. If
        ERR 904 B > DLMT is displayed, the calibration is invalid and a thru or open/short
        calibration must be performed.
        If active (ON), the 'normalize_trace_data' command is automatically turned off with an
        instrument preset (IP) or at power on.

        Type: :code:`bool`
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: "1", False: "0"},
        cast=str
    )

    normalized_reference_level = Instrument.control(
        "NRL?", "NRL %d {amplitude_unit}",
        """
        Control the normalized reference level. It is intended to be used with the
        :attr:`normalize_trace_data` command. When using 'normalized_reference_level', the input
        attenuator and IF step gains are not affected. This function is a trace-offset function
        enabling the user to offset the displayed trace without introducing hardware-switching
        errors into the stimulus-response measurement. The unit of measure for
        'normalized_reference_level' is dB. In absolute power mode (dBm), reference level (
        :attr:`reference_level`) affects the gain and RF attenuation settings of the instrument,
        which affects the measurement or dynamic range. In normalized mode
        (relative power or dB-measurement mode), NRL offsets the trace data on-screen and does
        not affect the instrument gain or attenuation settings. This allows the displayed
        normalized trace to be moved without decreasing the measurement accuracy due to changes
        in gain or RF attenuation. If the measurement range must be changed to bring trace data
        on-screen, then the range level should be adjusted. Adjusting the range-level normalized
        mode has the same effect on the instrument settings as does reference level in absolute
        power mode (normalize off).

        Type: :code:`int`

        .. code-block:: python

            # reference level in case of normalization to -30 DB
            instr.normalized_reference_level = -30

            if instr.normalized_reference_level == -30:
                pass
        """,
        validator=strict_range,
        values=[-200, 30],
        cast=int
    )

    normalized_reference_position = Instrument.control(
        "NRPOS?", "NRPOS %f DB",
        """
        Control the normalized reference-position that corresponds to the
        position on the graticule where the difference between the measured and calibrated traces
        resides. The dB value of the normalized reference-position is equal to the normalized
        reference level. The normalized reference-position may be adjusted between 0.0 and 10.0,
        corresponding to the bottom and top graticule lines, respectively.

        Type: :code:`float`

        .. code-block:: python

            instr.normalized_reference_position = 5.5

            if instr.normalized_reference_position == 5.5:
                pass
        """,
        validator=strict_range,
        values=[0.0, 10.0]
    )

    display_parameters = Instrument.measurement(
        "OP?",
        """
        Get the location of the lower left (P1) and upper right (P2) vertices as a tuple of
        the display window.

        Type: :code:`tuple`

        .. code-block:: python

            repr(instr.display_parameters)
            (72, 16, 712, 766)

        """,
        maxsplit=4,
        cast=int,
        get_process=tuple
    )

    def plot(self, p1x, p1y, p2x, p2y):
        """Copies the specified display contents onto any HP-GL plotter. Set
        the plotter address to 5, select the Pi and P2 positions, and then
        execute the plot command. P1 and P2 correspond to the lower-left and
        upper-right plotter positions, respectively. If P1 and P2 are not
        specified, default values (either preloaded from power-up or sent in
        via a previous plot command) are used. Once PLOT is executed, no
        subsequent commands are executed until PLOT is done.

        :param p1x: plotter-dependent value that specify the lower-left plotter position x-axis
        :type p1x: int
        :param p1y: plotter-dependent value that specify the lower-left plotter position y-axis
        :type p1y: int
        :param p2x: plotter-dependent values that specify the upper-right plotter position x-axis
        :type p2x: int
        :param p2y: plotter-dependent values that specify the upper-right plotter position y-axis
        :type p2y: int
        """
        if not (isinstance(p1x, int) or isinstance(p1y, int) or isinstance(p2x, int) or
                isinstance(p2y, int)):
            raise TypeError("Should be of type int")

        self.write("PLOT %d,%d,%d,%d" % (p1x, p1y, p2x, p2y))

    protect_state_enabled = Instrument.control(
        "PSTATE?", "PSTATE %s",
        """
        Control the storing of any new data in the state or trace registers.
        If set to 'True', the registers are “locked”; the data in them cannot be erased or
        overwritten, although the data can be recalled. To “unlock” the registers, and store new
        data, set 'protect_state_enabled' to off by selecting 'False' as the parameter.

        Type: :code:`bool`
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: "1", False: "0"},
        cast=str
    )

    def get_power_bandwidth(self, trace, percent):
        """Measure the combined power of all signal responses contained in a
        trace array. The command then computes the bandwidth equal to a
        percentage of the total power. For example, if 100% is specified, the
        power bandwidth equals the current frequency span. If 50% is specified,
        trace elements are eliminated from either end of the array, until the
        combined power of the remaining trace elements equals half of the total
        power computed. The frequency span of these remaining trace elements is
        the power bandwidth output to the controller.

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :param percent: Percentage of total power 0 ... 100 %
        :type trace: str
        :type percent: float

        .. code-block:: python

            # reset spectrum analyzer
            instr.preset()

            # set to single sweep mode
            instr.sweep_single()

            instr.center_frequency = 300e6
            instr.span = 1e6

            instr.maximum_hold()

            instr.trigger_sweep()

            if instr.done:
                pbw = instr.power_bandwidth(Trace.A, 99.0)
                print("The power bandwidth at 99 percent is %f kHz" % (pbw / 1e3))
        """
        ran = np.arange(0, 100, 0.1)

        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if not isinstance(percent, float):
            raise TypeError("Should be of type float but is '%s'" % type(percent))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             ([e for e in Trace], trace))

        if percent not in ran:
            raise ValueError("Only accepts values in the range of %s but was '%s'" %
                             (ran, percent))

        return float(self.ask("PWRBW %s,%.1f?" % (trace, percent)))

    resolution_bandwidth = Instrument.control(
        "RB?", "RB %s",
        """
        Control the resolution bandwidth. This is normally a coupled function that
        is selected according to the ratio selected by the RBR command. If no ratio is selected, a
        default ratio (0.011) is used. The bandwidth, which ranges from 10 Hz to 2 MHz, may also be
        selected manually.

        Type: :code:`str, dec`
        """,
        validator=joined_validators(strict_discrete_set, truncated_discrete_set),
        values=[["AUTO", "MAN"], np.arange(10, 2e6)],
        set_process=lambda v: v if isinstance(v, str) else f"{int(v)} Hz",
        get_process=lambda v: v if isinstance(v, str) else int(v)
    )

    resolution_bandwidth_to_span_ratio = Instrument.control(
        "RBR?", "RBR %.3f",
        """
        Control the coupling ratio between the resolution bandwidth and the
        frequency span. When the frequency span is changed, the resolution bandwidth is changed
        to satisfy the selected ratio. The ratio ranges from 0.002 to 0.10. The “UP” and “DN”
        parameters adjust the ratio in a 1, 2, 5 sequence. The default ratio is 0.011.
        """,
        validator=strict_range,
        values=np.arange(0.002, 0.10, 0.001)
    )

    def recall_open_short_average(self):
        """Set the internally stored open/short average reference trace into
        trace B. The instrument state is also set to the stored open/short
        reference state.

        .. code-block:: python

            instr.preset()
            instr.sweep_single()
            instr.start_frequency = 300e3
            instr.stop_frequency = 1e9

            instr.source_power_enabled = True
            instr.sweep_couple = SweepCoupleMode.StimulusResponse
            instr.source_peak_tracking()

            input("CONNECT OPEN. PRESS CONTINUE WHEN READY TO STORE.")
            instr.trigger_sweep()
            instr.done()
            instr.store_open()

            input("CONNECT SHORT. PRESS CONTINUE WHEN READY TO STORE AND AVERAGE.")
            instr.trigger_sweep()
            instr.done()
            instr.store_short()

            input("RECONNECT DUT. PRESS CONTINUE WHEN READY.")
            instr.trigger_sweep()
            instr.done()

            instr.normalize = True

            instr.trigger_sweep()
            instr.done()

            instr.normalized_reference_position = 8
            instr.trigger_sweep()

            instr.preset()
            # demonstrate recall of open/short average trace
            instr.recall_open_short_average()
            instr.trigger_sweep()
        """
        self.write("RCLOSCAL")

    def recall_state(self, inp):
        """Set to the display a previously saved instrument state. See
        :meth:`save_state`.

        :param inp: State to be recalled: either storage slot 0 ... 9 or 'LAST' or 'PWRON'
        :param inp: str, int

        .. code-block:: python

            instr.save_state(7)
            instr.preset()
            instr.recall_state(7)
        """
        values = ["LAST", "PWRON"] + [str(f) for f in range(0, 9)]
        if not (isinstance(inp, str) or isinstance(inp, int)):
            raise TypeError("Should be of type 'str' or 'int' but is '%s'" % type(inp))

        if str(inp) not in values:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             (values, str(inp)))

        self.write("RCLS %s" % str(inp))

    def recall_trace(self, trace, number):
        """Recalls previously saved trace data to the display. See
        :meth:`save_trace`. Either as Trace A or Trace B.

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :param number: Storage location from 0 ... 7 where to store the trace
        :type trace: str
        :type number: int

        .. code-block:: python

            instr.preset()
            instr.center_frequency = 300e6
            instr.span = 20e6

            instr.save_trace(Trace.A, 7)
            instr.preset()

            # reload - at 7 stored trace - to Trace B
            instr.recall_trace(Trace.B, 7)
        """
        ran = range(0, 7)
        if not isinstance(trace, str):
            raise TypeError("Should be of type str but is '%s'" % type(trace))

        if not isinstance(number, int):
            raise TypeError("Should be of type int but is '%s'" % type(number))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             ([e for e in Trace], trace))

        if number not in ran:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             (ran, number))

        self.write("RCLT %s,%s" % (trace, number))

    def recall_thru(self):
        """Recalls the internally stored thru-reference trace into trace B.

        The instrument state is also set to the stored thru-reference
        state.
        """
        self.write("RCLTHRU")

    firmware_revision = Instrument.measurement(
        "REV?",
        """
        Get the revision date code of the spectrum analyzer firmware.

        Type: :code:`datetime.date`
        """,
        get_process=lambda v: datetime.strptime(v, '%y%m%d').date(),
        cast=str
    )

    reference_level = Instrument.control(
        "RL?", "RL %g {amplitude_unit}",
        """
        Control the reference level, or range level when in normalized mode. (Range level
        functions the same as reference level.) The reference level is the top horizontal line on
        the graticule. For best measurement accuracy, place the peak of a signal of interest on the
        reference-level line. The spectrum analyzer input attenuator is coupled to the reference
        level and automatically adjusts to avoid compression of the input signal. Refer also to
        :attr:`amplitude_unit`. Minimum reference level is -120.0 dBm or 2.2 uV

        Type: :code:`float`
        """
    )

    reference_level_calibration = Instrument.control(
        "RLCAL?", "RLCAL %g",
        """
        Control the calibration of the reference level remotely and retuns the
        current calibration. To calibrate the reference level, connect the 300 MHz calibration
        signal to the RF input. Set the center frequency to 300 MHz, the frequency span to 20
        MHz, and the reference level to -10 dBm. Use the RLCAL command to move the input signal
        to the reference level. When the signal peak falls directly on the reference-level line,
        the reference level is calibrated. Storing this value in the analyzer in EEROM can be
        done only from the front panel. The RLCAL command, when queried, returns the current value.

        Type: :code:`float`

        .. code-block:: python

            # connect cal signal to rf input
            instr.preset()
            instr.amplitude_unit = AmplitudeUnits.DBM
            instr.center_frequency = 300e6
            instr.span = 100e3
            instr.reference_level = 0
            instr.trigger_sweep()

            instr.peak_search(PeakSearchMode.High)
            level = instr.marker_amplitude
            rlcal = instr.reference_level_calibration - int((level + 10) / 0.17)
            instr.reference_level_calibration = rlcal
        """,
        cast=int,
        validator=strict_range,
        values=[-33, 33]
    )

    reference_offset = Instrument.control(
        "ROFFSET?", "ROFFSET %d DB",
        """
        Control an offset applied to all amplitude readouts (for example, the
        reference level and marker amplitude). The offset is in dB, regardless of the selected scale
        and units. The offset can be useful to account for gains of losses in accessories connected
        to the input of the analyzer. When this function is active, an "R" appears on the left
        edge of the display.

        Type: :code:`int`
        """,
        cast=int,
        values=[-100, 100],
        validator=strict_range
    )

    request_service_conditions = Instrument.control(
        "RQS?", "RQS %d",
        """
        Control a bit mask that specifies which service requests can interrupt
        a program sequence.

        .. code-block:: python

            instr.request_service_conditions = StatusRegister.ERROR_PRESENT | StatusRegister.TRIGGER

            print(instr.request_service_conditions)
            StatusRegister.ERROR_PRESENT|TRIGGER
        """,
        get_process=lambda v: StatusRegister(int(v))
    )

    def save_state(self, inp):
        """Saves the currently displayed instrument state in the specified
        state register.

        :param inp: State to be recalled: either storage slot 0 ... 9 or 'LAST' or 'PWRON'
        :param inp: str, int

        .. code-block:: python

            instr.preset()
            instr.center_frequency = 300e6
            instr.span = 20e6
            instr.save_state("PWRON")
        """
        values = ["PWRON"] + [str(f) for f in range(0, 9)]
        if not (isinstance(inp, str) or isinstance(inp, int)):
            raise TypeError("Should be of type 'str' or 'int' but is '%s'" % type(inp))

        if str(inp) not in values:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             (values, str(inp)))

        self.write("SAVES %s" % str(inp))

    def save_trace(self, trace, number):
        """Saves the selected trace in the specified trace register.

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :param number: Storage location from 0 ... 7 where to store the trace
        :type trace: str
        :type number: int

        .. code-block:: python

            instr.preset()
            instr.center_frequency = 300e6
            instr.span = 20e6

            instr.save_trace(Trace.A, 7)
            instr.preset()

            # reload - at 7 stored trace - to Trace B
            instr.recall_trace(Trace.B, 7)
        """
        ran = range(0, 7)
        if not isinstance(trace, str):
            raise TypeError("Should be of type str but is '%s'" % type(trace))

        if not isinstance(number, int):
            raise TypeError("Should be of type int but is '%s'" % type(number))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             ([e for e in Trace], trace))

        if number not in ran:
            raise ValueError("Only accepts values of [%s] but was '%s'" %
                             (ran, number))

        self.write("SAVET %s,%s" % (trace, number))

    serial_number = Instrument.measurement(
        "SER?",
        """
        Get the spectrum analyzer serial number.
        """,
        cast=str
    )

    def sweep_single(self):
        """Sets the spectrum analyzer into single-sweep mode.

        This mode allows only one sweep when trigger conditions are met.
        When this function is active, an 'S' appears on the left edge of
        the display.
        """
        self.write("SNGLS")

    span = Instrument.control(
        "SP?", "SP %s",
        """
        Control the frequency span. The center frequency does not change with
        changes in the frequency span; start and stop frequencies do change. Setting the frequency
        span to 0 Hz effectively allows an amplitude-versus-time mode in which to view signals. This
        is especially useful for viewing modulation. Querying SP will leave the analyzer in center
        frequency /span mode.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[["FULL", "ZERO"], [float("-inf"), float("inf")]],
        set_process=lambda v: v if isinstance(v, str) else "%.11E Hz" % v,
        get_process=lambda v: v if isinstance(v, str) else v
    )

    squelch = Instrument.control(
        "SQUELCH?", "SQUELCH %s",
        """
        Control the squelch level for demodulation. When this function is
        on, a dashed line indicating the squelch level appears on the display.
        A marker must be active and above the squelch line for demodulation to occur. Refer to
        the :attr:`demodulation_mode` command. The default value is -120 dBm.

        Type: :code:`str,int`

        .. code-block:: python

            instr.preset()
            instr.start_frequency = 88e6
            instr.stop_frequency = 108e6

            instr.peak_search(PeakSearchMode.High)
            instr.demodulation_time = 10

            instr.squelch = -60
            instr.demodulation_mode = DemodulationMode.FM
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[["ON", "OFF"], range(-220, 30)],
        set_process=lambda v: v if isinstance(v, str) else f"{v} {{amplitude_unit}}"
    )

    squelch_enabled = Instrument.setting(
        "SQUELCH %s",
        """
        Set squelch for demodulation active or inactive. For further information see :attr:`squelch`
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    def request_service(self, input):
        """Triggers a service request. This command allows you to force a
        service request and test a program designed to handle service requests.
        However, the service request can be triggered only if it is first
        masked using the :attr:`request_service_conditions` command.

        :param input: Bits to emulate a service request
        :type input: :class:`StatusRegister`
        """
        if input not in range(0, 255):
            raise ValueError("Bit mask needs to be between 0 ... 255")

        self.write("SRQ %d" % input)

    # `center_frequency_step_size` would be a command but is pretty unnecesary

    sweep_time = Instrument.control(
        "ST?", "ST %s",
        """
        Control the sweep time. This is normally a coupled function which is
        automatically set to the optimum value allowed by the current instrument settings.
        Alternatively, you may specify the sweep time. Note that when the specified sweep time is
        too fast for the current instrument settings, the instrument is no longer calibrated and the
        message 'MEAS UNCAL' appears on the display. The sweep time cannot be adjusted when the
        resolution bandwidth is set to 10 Hz, 30 Hz, or 100 Hz.

        Type: :code:`str, float`

        Real from 50E—3 to 100 when the span is greater than 0 Hz; 50E—6 to 60 when
        the span equals 0 Hz. When the resolution bandwidth is <100 Hz, the sweep time
        cannot be adjusted.
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[["AUTO", "MAN"], np.arange(50E-6, 100)],
        set_process=lambda v: v if isinstance(v, str) else ("%.3f S" % v)
    )

    status = Instrument.measurement(
        "STB?",
        """
        Get the decimal equivalent of the bits set in the
        status byte (see the RQS and SRQ commands). STB is equivalent to a serial poll command.
        The RQS and associated bits are cleared in the same way that a serial poll command would
        clear them.
        """,
        get_process=lambda v: StatusRegister(int(v))
    )

    def store_open(self):
        """Save the current instrument state and trace A into nonvolatile
        memory.

        This command must be used in conjunction with the
        :meth:`store_short` command and must precede the
        :meth:`store_short` command. The data obtained during the store
        open procedure is averaged with the data obtained during the
        :meth:`store_short` procedure to provide an open/short
        calibration. The instrument state (that is, instrument settings)
        must not change between the :meth:`store_open` and
        :meth:`store_short` operations in order for the open/short
        calibration to be valid. Refer to the :meth:`store_short`
        command description for more information.
        """
        self.write("STOREOPEN")

    def store_short(self):
        """Take currently displayed trace A data and averages this data with
        previously stored open data, and stores it in trace B.

        This command is used in conjunction with the :meth:`store_open`
        command and must be preceded by it for proper operation. Refer
        to the :meth:`store_open` command description for more
        information. The state of the open/short average trace is stored
        in state register #8.
        """
        self.write("STORESHORT")

    def store_thru(self):
        """Store a thru-calibration trace into trace B and into the nonvolatile
        memory of the spectrum analyzer.

        The state of the thru information is stored in state register
        #9.
        """
        self.write("STORETHRU")

    sweep_couple = Instrument.control(
        "SWPCPL?", "SWPCPL %s",
        """
        Control the sweep couple mode which is either a stimulus-response or spectrum-analyzer
        auto-coupled sweep time. In stimulus-response mode, auto-coupled sweep times are usually
        much faster for swept-response measurements. Stimulus-response auto-coupled sweep times
        are typicallly valid in stimulus-response measurements when the system’s frequency span is
        less than 20 times the bandwidth of the device under test.

        Type: :code:`str` or :class:`SweepCoupleMode`
        """,
        validator=strict_discrete_set,
        values=[e for e in SweepCoupleMode]
    )

    sweep_output = Instrument.control(
        "SWPOUT?", "SWPOUT %s",
        """
        Control the sweep-related signal that is available from J8 on the rear
        panel. FAV provides a dc ramp of 0.5V/GHz. RAMP provides a 0—10 V ramp corresponding
        to the sweep ramp that tunes the first local oscillator (LO). For the HP 8561B, in multiband
        sweeps one ramp is provided for each frequency band.

        Type: :code:`str` or :class:`SweepOut`
        """,
        validator=strict_discrete_set,
        values=[e for e in SweepOut]
    )

    trace_data_format = Instrument.control(
        "TDF?", "TDF %s",
        """
        Control the format used to input and output trace data (see the
        TRA/TRB command, You must specify the desired format when
        transferring data from the spectrum analyzer to a computer; this is optional when
        transferring data to the analyzer.

        Type: :code:`str` or :class:`TraceDataFormat`

        .. warning::
            Only needed for manual read out of trace data. Don't use this if you don't know what
            You are doing.
        """,
        validator=strict_discrete_set,
        values=[e for e in TraceDataFormat]
    )

    threshold = Instrument.control(
        "TH?", "TH %.2E {amplitude_unit}",
        """
        Control the minimum amplitude level and clips data at this value. Default
        value is -90 dBm. See also - :attr:`marker_threshold` does not clip data below its threshold

        Type: :code:`str, float` range -200 to 30

        .. note::
            When a trace is in max-hold mode, if the threshold is raised above any of the
            trace data, the data below the threshold will be permanently lost.
        """,
        validator=strict_discrete_set,
        values=np.arange(-200, 30),
    )

    threshold_enabled = Instrument.setting(
        "TH %s",
        """
        Set the threshold active or inactive. See :attr:`threshold`
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    def set_title(self, string):
        """Sets character data in the title area of the display, which is in
        the upper-right corner.

        A title can be up to two rows of sixteen characters each, Carriage
        return and line feed characters are not allowed.
        """
        if not isinstance(string, str):
            raise TypeError("Parameter should be of type 'str'")

        if len(string) > 32:
            raise ValueError("Title should have maximum 32 chars but has '%d'" % len(string))

        self.write("TITLE@%s@" % string)

    trigger_mode = Instrument.control(
        "TM?", "TM %s",
        """
        Control the trigger mode. Selected trigger conditions must be met in order for
        a sweep to occur. For the available modes refer to :class:`TriggerMode`.
        When any trigger mode other than free run is selected,
        a "T" appears on the left edge of the display.
        """,
        validator=strict_discrete_set,
        values=[e for e in TriggerMode]
    )

    def _get_trace_data(self, trace):
        self.write("TDF M")

        amp_units = str(self.ask("AUNITS?"))
        ref_lvl = float(self.ask("RL?"))
        log_scale = float(self.ask("LG?"))

        cmd_str = ""
        if trace is Trace.A:
            cmd_str += "TRA?"
        elif trace is Trace.B:
            cmd_str += "TRB?"

        values = self.values(cmd_str, cast=int)

        if amp_units is AmplitudeUnits.W:
            # calculate dbm from watts
            ref_lvl = (10 * log10(ref_lvl)) + 30
        elif amp_units is AmplitudeUnits.DBUV:
            # calculate dbm from dbuv in 50 Ohm system
            ref_lvl = ref_lvl - 107
        elif amp_units is AmplitudeUnits.V:
            # calculate dbm from volts in 50 Ohm system
            ref_lvl = 20 * log10((ref_lvl / 0.05) ** 0.5)
        elif amp_units is AmplitudeUnits.DBMV:
            # calculate dbm from dbmv
            ref_lvl = ref_lvl - 46.9897

        result_values = []
        for value in values:
            if log_scale != 0:
                result_value = round(ref_lvl + (log_scale * ((value - 600) / 60)), 2)
                result_values.append(result_value)
            else:
                raise NotImplementedError("Linear scaling isn't supported by get_trace_data_ ")

        return result_values

    def get_trace_data_a(self):
        """
        Get the data of trace A as a list.

        The function returns the 601 data points as a list in the amplitude format.
        Right now it doesn't support the linear scaling due to the manual just being wrong.
        """
        return self._get_trace_data(Trace.A)

    def get_trace_data_b(self):
        """
        Get the data of trace B as a list.

        The function returns the 601 data points as a list in the amplitude format.
        Right now it doesn't support the linear scaling due to the manual just being wrong.
        """
        return self._get_trace_data(Trace.B)

    set_trace_data_a = Instrument.setting(
        "TDF P;TRA %s",
        """
        Set the trace data of trace A.

        .. warning::

            The string based method this attribute is using takes its time. Something around 5000ms
            timeout at the adapter seems to work well.
        """,
        set_process=lambda v: (','.join([str(i) for i in v])),
    )

    set_trace_data_b = Instrument.setting(
        "TDF P;TRB %s",
        """
        Set the trace data of trace B also allows to write the data.

        .. warning::

            The string based method this attribute is using takes its time. Something around 5000ms
            timeout at the adapter seems to work well.
        """,
        set_process=lambda v: (','.join([str(i) for i in v]))
    )

    def trigger_sweep(self):
        """Command the spectrum analyzer to take one full sweep across the trace display.
        Commands following TS are not executed until after the analyzer has finished the trace
        sweep. This ensures that the instrument is set to a known condition before subsequent
        commands are executed.
        """
        self.write("TS")

    def create_fft_trace_window(self, trace, window_mode):
        """Creates a window trace array for the fast Fourier transform (FFT) function.

        The trace-window function creates a trace array according to three built-in
        algorithms: UNIFORM, HANNING, and FLATTOP. When used with the FFT command,
        the three algorithms give resultant passband shapes that represent a compromise among
        amplitude uncertainty, sensitivity, and frequency resolution. Refer to the FFT command
        description for more information.

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :type trace: str
        :param window_mode: A representation of the window mode, either from :class:`WindowType` or
            use 'HANNING', 'FLATTOP' or 'UNIFORM'
        :type window_mode: str
        """

        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))

        if not isinstance(window_mode, str):
            raise TypeError("Should be of type string but is '%s'" % type(window_mode))

        if window_mode not in [e for e in WindowType]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in
                                                                            WindowType],
                                                                           window_mode))

        self.write("TWNDOW %s,%s" % (trace, window_mode))

    video_average = Instrument.control(
        "VAVG?", "VAVG %d",
        """
        Control the video averaging function. Video averaging smooths the
        displayed trace without using a narrow bandwidth. 'video_average' sets the IF detector to
        sample mode (see the DET command) and smooths the trace by averaging successive traces
        with each other. If desired, you can change the detector mode during video averaging.
        Video averaging is available only for trace A, and trace A must be in clear-write mode for
        'video_average' to operate. After 'video_average' is executed, the number of sweeps that
        have been averaged appears at the top of the analyzer screen. Using video averaging
        allows you to view changes to the entire trace much faster than using narrow video
        filters. Narrow video filters require long sweep times, which may not be desired. Video
        averaging, though requiring more sweeps, uses faster sweep times; in some cases, it can
        produce a smooth trace as fast as a video filter.

        Type: :code:`str, int`
        """,
        validator=strict_range,
        values=np.arange(1, 999),
        cast=int
    )

    video_average_enabled = Instrument.setting(
        "VAVG %s",
        """
        Set the video averaging either active or inactive. See :attr:`video_average`
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    video_bandwidth = Instrument.control(
        "VB?", "VB %s",
        """
        Control the video bandwidth. This is normally a coupled function that
        is selected according to the ratio selected by the VBR command. (If no ratio is selected,
        a default ratio, 1.0, is used instead.) Video bandwidth filters (or smooths) post-detected
        video information. The bandwidth, which ranges from 1 Hz to 3 MHz, may also be selected
        manually. If the specified video bandwidth is less than 300 Hz and the resolution bandwidth
        is greater than or equal to 300 Hz, the IF detector is set to sample mode. Reducing the
        video bandwidth or increasing the number of video averages will usually smooth the trace
        by about as much for the same total measurement time. Reducing the video bandwidth to
        one-third or less of the resolution bandwidth is desirable when the number of video
        averages is above 25. For the case where the number of video averages is very large, and
        the video bandwidth is equal to the resolution bandwidth, internal mathematical limitations
        allow about 0.4 dB overresponse to noise on the logarithmic scale. The overresponse is
        negligible (less than 0.1 dB) for narrower video bandwidths.

        Type: :code:`int`
        """,
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[["AUTO", "MAN"], np.arange(1, 3e6)],
        cast=int,
        set_process=lambda v: v if isinstance(v, str) else f"{v} Hz"
    )

    video_bandwidth_to_resolution_bandwidth = Instrument.control(
        "VBR?", "VBR %.3f",
        """
        Control the coupling ratio between the video bandwidth and the
        resolution bandwidth. Thus, when the resolution bandwidth is changed, the video bandwidth
        changes to satisfy the ratio. The ratio ranges from 0.003 to 3 in a 1, 3, 10 sequence. The
        default ratio is 1. When a new ratio is selected, the video bandwidth changes to satisfy the
        new ratio—the resolution bandwidth does not change value.
        """,
        validator=strict_range,
        values=np.arange(0.002, 0.10, 0.001)
    )

    def view_trace(self, trace):
        """Display the current contents of the selected trace, but does not update
        the contents. View mode may be executed before a sweep is complete when :meth:`sweep_single`
        and :meth:`trigger_sweep` are not used.

        :param trace: A representation of the trace, either from :class:`Trace` or
            use 'TRA' for Trace A or 'TRB' for Trace B
        :type trace: str
        :raises TypeError: Type isn't 'string'
        :raises ValueError: Value is 'TRA' nor 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))
        self.write("VIEW " + trace)

    video_trigger_level = Instrument.control(
        "VTL?", "VTL %.3f {amplitude_unit}",
        """
        Control the video trigger level when the trigger mode is set to VIDEO (refer
        to the :attr:`trigger_mode` command). A dashed line appears on the display to indicate the
        level. The default value is 0 dBm. Range -220 to 30.

        Type: :code:`float`
        """,
        validator=strict_range,
        values=[-220, 30]
    )


class HP8560A(HP856Xx):
    """Represents the HP 8560A Spectrum Analyzer and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        from pymeasure.instruments.hp import HP8560A
        from pymeasure.instruments.hp.hp856Xx import AmplitudeUnits

        sa = HP8560A("GPIB::1")

        sa.amplitude_unit = AmplitudeUnits.DBUV
        sa.start_frequency = 299.5e6
        sa.stop_frequency = 300.5e6

        print(sa.marker_amplitude)
    """

    # HP8560A is able to go up to 2.9 GHz
    MAX_FREQUENCY = 2.9e9

    def __init__(self, adapter, name="Hewlett-Packard HP8560A", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

        self.center_frequency_values = [0, self.MAX_FREQUENCY]
        self.start_frequency_values = [0, self.MAX_FREQUENCY]
        self.stop_frequency_values = [0, self.MAX_FREQUENCY]
        self.frequency_offset_values = [0, self.MAX_FREQUENCY]
        self.marker_frequency_values = [0, self.MAX_FREQUENCY]
        self.span_values = [["FULL", "ZERO"], [0, self.MAX_FREQUENCY]]

    source_leveling_control = Instrument.control(
        "SRCALC?", "SRCALC %s",
        """
        Control if internal or external leveling is used with the
        built-in tracking generator.
        Takes either 'INT', 'EXT' or members of enumeration :class:`SourceLevelingControlMode`

        Type: :code:`str`

        .. code-block:: python

            instr.preset()
            instr.sweep_single()
            instr.center_frequency = 300e6
            instr.span = 1e6

            instr.source_power = -5

            instr.trigger_sweep()
            instr.source_leveling_control = SourceLevelingControlMode.External

            if ErrorCode(900) in instr.errors:
                print("UNLEVELED CONDITION. CHECK LEVELING LOOP.")

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=strict_discrete_set,
        values=[e for e in SourceLevelingControlMode]
    )

    tracking_adjust_coarse = Instrument.control(
        "SRCCRSTK?", "SRCCRSTK %d",
        """
        Control the coarse adjustment to the frequency of the built-in
        tracking-generator oscillator. Once enabled, this adjustment is made in
        digital-to-analogconverter (DAC) values from 0 to 255. For fine adjustment, refer to the
        :attr:`tracking_adjust_fine` command description.

        Type: :code:`int`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=strict_range,
        values=[0, 255],
        cast=int
    )

    tracking_adjust_fine = Instrument.control(
        "SRCFINTK?", "SRCFINTK %d",
        """
        Control the fine adjustment of the frequency of the built-in
        tracking-generator oscillator. Once enabled, this adjustment is made in
        digital-to-analogconverter (DAC) values from 0 to 255. For coarse adjustment, refer to
        the :attr:`tracking_adjust_coarse` command description.

        Type: :code:`int`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=strict_range,
        values=[0, 255],
        cast=int
    )

    source_power_offset = Instrument.control(
        "SRCPOFS?", "SRCPOFS %g {amplitude_unit}",
        """
        Control the offset of the displayed power of the built-in tracking generator so that
        it is equal to the measured power at the input of the spectrum analyzer. This function may
        be used to take into account system losses (for example, cable loss) or gains (for example,
        preamplifier gain) reflecting the actual power delivered to the device under test.

        Type: :code:`int`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=strict_range,
        values=[-100, 100],
        cast=int
    )

    source_power_step = Instrument.control(
        "SRCPSTP?", "SRCPSTP %.2f DB",
        """
        Control the step size of the source power level, source power offset, and
        power-sweep range functions. Range: 0.1 ... 12.75 DB with 0.05 steps.

        Type: :code:`float`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=strict_range,
        values=np.arange(0.1, 12.75, 0.05)
    )

    source_power_sweep = Instrument.control(
        "SRCPSWP?", "SRCPSWP %.2f DB",
        """
        Control the power-sweep function, where the
        output power of the tracking generator is swept over the power-sweep range chosen. The
        starting source power level is set using the :attr:`source_power` command. The output power
        of the tracking generator is swept according to the sweep rate of the spectrum analyzer.

        Type: :code:`str, float`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=truncated_discrete_set,
        values=np.arange(0.1, 12.75, 0.05),
    )

    source_power_sweep_enabled = Instrument.setting(
        "SRCPSWP %s",
        """
        Set the power sweep active or inactive. See :attr:`source_power_sweep`.
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    source_power = Instrument.control(
        "SRCPWR?", "SRCPWR %s",
        """
        Control the built-in tracking generator's output power.

        Type: :code:`str, float`

        .. note::
            Only available with an HP 8560A Option 002.
        """,
        validator=joined_validators(strict_discrete_set, truncated_discrete_set),
        values=[["OFF", "ON"], np.arange(-10, 2.8, 0.05)],
        set_process=lambda v: v if isinstance(v, str) else ("%.2f {amplitude_unit}" % v)
    )

    source_power_enabled = Instrument.setting(
        "SRCPWR %s",
        """
        Set the built-in tracking generator on or off. See :attr:`source_power`
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    def activate_source_peak_tracking(self):
        """Activate a routine which automatically adjusts both the coarse and
        fine-tracking adjustments to obtain the peak response of the tracking
        generator on the spectrum-analyzer display. Tracking peak is not
        necessary for resolution bandwidths greater than or equal to 300 kHz. A
        thru connection should be made prior to peaking in order to ensure
        accuracy.

        .. note::
            Only available with an HP 8560A Option 002.
        """
        self.write("SRCTKPK")


class HP8561B(HP856Xx):
    """Represents the HP 8561B Spectrum Analyzer and provides a high-level
    interface for interacting with the instrument.

    .. code-block:: python

        from pymeasure.instruments.hp import 8561B
        from pymeasure.instruments.hp.hp856Xx import AmplitudeUnits

        sa = HP8560A("GPIB::1")

        sa.amplitude_unit = AmplitudeUnits.DBUV
        sa.start_frequency = 6.4e9
        sa.stop_frequency = 6.5e9

        print(sa.marker_amplitude)
    """

    # HP8561B is able to go up to 6.5 GHz
    MAX_FREQUENCY = 6.5e9

    def __init__(self, adapter, name="Hewlett-Packard HP8561B", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

        self.center_frequency_values = [0, self.MAX_FREQUENCY]
        self.start_frequency_values = [0, self.MAX_FREQUENCY]
        self.stop_frequency_values = [0, self.MAX_FREQUENCY]
        self.frequency_offset_values = [0, self.MAX_FREQUENCY]
        self.marker_frequency_values = [0, self.MAX_FREQUENCY]
        self.span_values = [["FULL", "ZERO"], [0, self.MAX_FREQUENCY]]

    conversion_loss = Instrument.control(
        "CNVLOSS?", "CNVLOSS %s DB",
        """
        Control the compensation for losses outside the instrument when in external
        mixer mode (such as losses within connector cables, external mixers, etc.).
        'conversion_loss' specifies the mean conversion loss for the current harmonic band.
        In a full frequency band (such as band K), the mean conversion loss is defined as the
        minimum loss plus the maximum loss for that band divided by two.
        Adjusting for conversion loss allows the system to remain
        calibrated (that is, the displayed amplitude values have the conversion loss incorporated
        into them). The default value for any band is 30 dB. The spectrum analyzer must be in
        external-mixer mode in order for this command to work. When in internal-mixer mode,
        querying 'conversion_loss' returns a zero.
        """,
        validator=strict_range,
        values=[0, float("inf")]
    )

    def set_fullband(self, band):
        """Select a commonly-used, external-mixer frequency band, as shown in
        the table. The harmonic lock function :attr:`harmonic_number_lock` is
        also set; this locks the harmonic of the chosen band. External-mixing
        functions are not available with an HP 8560A Option 002. Takes
        frequency band letter as string.

        .. list-table:: Title
            :widths: 25 25 25 25
            :header-rows: 1

            * - Frequency Band
              - Frequency Range (GHz)
              - Mixing Harmonic
              - Conversion Loss
            * - K
              - 18.0 — 26.5
              - 6
              - 30 dB
            * - A
              - 26.5 — 40.0
              - 8
              - 30 dB
            * - Q
              - 33.0—50.0
              - 10
              - 30 dB
            * - U
              - 40.0—60.0
              - 10
              - 30 dB
            * - V
              - 50.0—75.0
              - 14
              - 30 dB
            * - E
              - 60.0—-90.0
              - 16
              - 30 dB
            * - W
              - 75.0—110.0
              - 18
              - 30 dB
            * - F
              - 90.0—140.0
              - 24
              - 30 dB
            * - D
              - 110.0—170.0
              - 30
              - 30 dB
            * - G
              - 140.0—220.0
              - 36
              - 30 dB
            * - Y
              - 170.0—260.0
              - 44
              - 30 dB
            * - J
              - 220.0—325.0
              - 54
              - 30 dB
        """
        frequency_mapping = {
            "K": [18e9, 26.5e9],
            "A": [26.5e9, 40e9],
            "Q": [33e9, 50e9],
            "U": [40e9, 60e9],
            "V": [50e9, 75e9],
            "E": [60e9, 90e9],
            "W": [75e9, 110e9],
            "F": [90e9, 140e9],
            "D": [110e9, 170e9],
            "G": [140e9, 220e9],
            "Y": [170e9, 260e9],
            "J": [220e9, 325e9],
        }

        if not isinstance(band, str):
            raise TypeError("Frequency band should be of type string but is '%s'" % type(band))

        if band not in frequency_mapping.keys():
            raise ValueError("Should be one of the available bands but is '%s'" % band)

        self.center_frequency_values = frequency_mapping[band]
        self.start_frequency_values = frequency_mapping[band]
        self.stop_frequency_values = frequency_mapping[band]

        self.write("FULLBAND %s" % band)

    harmonic_number_lock = Instrument.control(
        "HNLOCK?", "HNLOCK %d",
        """
        Control the lock to a chosen harmonic so only that harmonic is used to sweep
        an external frequency band. To select a frequency band, use the 'fullband' command; it
        selects an appropriate harmonic for the desired band. To change the harmonic number, use
        'harmonic_number_lock'.
        Note that 'harmonic_number_lock' also works in internal-mixing modes.
        Once 'fullband' or 'harmonic_number_lock' are set, only center frequencies and spans that
        fall within the frequency band of the current harmonic may be entered. When the
        'set_full_span' command is activated, the span is limited to the frequency band of the
        selected harmonic.
        """,
        validator=strict_range,
        values=[1, 54],
        cast=int
    )

    harmonic_number_lock_enabled = Instrument.setting(
        "HNLOCK %s",
        """
        Set the harmonic number locking active or inactive. See :attr:`harmonic_number_lock`.
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    def unlock_harmonic_number(self):
        """Unlock the harmonic number, allowing you to select frequencies and
        spans outside the range of the locked harmonic number.

        Also, when HNUNLK is executed, more than one harmonic can then
        be used to sweep across a desired span. For example, sweep a
        span from 18 GHz to 40 GHz. In this case, the analyzer will
        automatically sweep first using 6—, then using 8—.
        """
        self.write("HUNLK")

    def set_signal_identification_to_center_frequency(self):
        """Set the center frequency to the frequency obtained from the command
        SIGID.

        SIGID must be in AUTO mode and have found a valid result for
        this command to execute properly. Use SIGID on signals greater
        than 18 GHz {i.e., in external mixing mode). SIGID and IDCF may
        also be used on signals less than 6.5 GHz in an HP 8561B.
        """
        self.write("IDCF")

    signal_identification_frequency = Instrument.measurement(
        "IDFREQ?",
        """
        Measure the frequency of the last identified signal. After an instrument preset or an
        invalid signal identification, IDFREQ returns a “0”.
        """
    )

    mixer_bias = Instrument.control(
        "MBIAS?", "MBIAS %.3f MA",
        """
        Set the bias for an external mixer that requires diode bias for efficient
        mixer operation. The bias, which is provided on the center conductor of the IF input, is
        activated when MBIAS is executed. A "+" or "—" appears on the left edge of the spectrum
        analyzer display, indicating that positive or negative bias is on. When the bias is
        turned off, MBIAS is set to 0. Default units are in milliamps.
        """,
        validator=strict_range,
        values=[float(-10E3), int(10E3)],
        cast=float
    )

    mixer_bias_enabled = Instrument.setting(
        "MBIAS %s",
        """
        Control the bias for an external mixer. See :attr:`mixer_bias`.
        """,
        map_values=True,
        values={True: "ON", False: "OFF"},
        validator=strict_discrete_set
    )

    mixer_mode = Instrument.control(
        "MXRMODE?", "MXRMODE %s",
        """
        Control the mixer mode. Select either the internal mixer
        or supply an external mixer. Takes enum 'MixerMode' or string 'INT', 'EXT'
        """,
        validator=strict_discrete_set,
        values=[e for e in MixerMode]
    )

    def peak_preselector(self):
        """Peaks the preselector in the HP 8561B Spectrum Analyzer.

        Make sure the entire frequency span is in high band, set the
        desired trace to clear-write mode, place a marker on a desired
        signal, then execute PP. The peaking routine zooms to zero span,
        peaks the preselector tracking, then returns to the original
        position. To read the new preselector peaking number, use the
        PSDAC command. Commands following PP are not executed until
        after the analyzer has finished peaking the preselector.
        """
        self.write("PP")

    preselector_dac_number = Instrument.control(
        "PSDAC?", "PSDAC %d",
        """
        Control the preselector peak DAC number. For use with an
        HP 8561B Spectrum Analyzer.

        Type: :code:`int`
        """,
        cast=int,
        validator=strict_range,
        values=[0, 255]
    )

    signal_identification = Instrument.control(
        "SIGID?", "SIGID %s",
        """
        Control the signal identification for identifying signals for the external
        mixing frequency bands.
        Two signal identification methods are available. AUTO employs the image response method
        for locating correct mixer responses. Place a marker on the desired signal, then activate
        signal_identification = 'AUTO'. The frequency of a correct response appears in the active
        function block. Use this mode before executing the
        :meth:`signal_identification_to_center_frequency` command. The second method of signal
        identification, 'MAN', shifts responses both horizontally and vertically. A correct
        response is shifted horizontally by less than 80 kHz. To ensure accuracy in MAN mode,
        limit the frequency span to less than 20 MHz.
        Where True = manual mode is active and False = auto mode is active or
        'signal_identification' is off.
        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: "1", False: "0", "AUTO": "AUTO", "MAN": "MAN"},
        cast=str
    )
