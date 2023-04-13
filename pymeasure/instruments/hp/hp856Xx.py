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
from enum import Enum

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, \
    joined_validators, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class StrEnum(str, Enum):
    """
    Until StrEnum is broadly available / pymeasure relies on python => 3.10.x
    """

    def __str__(self):
        return self.value


class Trace(StrEnum):
    """
    Enumeration to represent either Trace A or Trace B
    """

    #: Trace A
    A = "TRA"

    #: Trace B
    B = "TRB"


class MixerMode(StrEnum):
    """
    Enumeration to represent the Mixer Mode of the HP8561B
    """

    #: Mixer Mode Internal
    Internal = "INT"

    #: Mixer Mode External
    External = "EXT"


class CouplingMode(StrEnum):
    """
    Enumeration to represent the Coupling Mode
    """

    #: AC
    AC = "AC"

    #: DC
    DC = "DC"


class DemodulationMode(StrEnum):
    """
    Enumeration to represent the Demodulation Mode
    """

    #: Amplitude Modulation
    Amplitude = "AM"

    #: Frequency Modulation
    Frequency = "FM"

    #: Demodulation Off
    Off = "OFF"


class FrequencyReference(StrEnum):
    """
    Enumeration to represent the frequency reference source
    """

    #: Internal Frequency Reference
    Internal = "INT"

    #: External Frequency Standard
    External = "EXT"


class DetectionModes(StrEnum):
    """
    Enumeration to represent the Detection Modes
    """

    #: Negative Peak Detection
    NegativePeak = "NEG"

    #: Normal Peak Detection
    Normal = "NRM"

    #: Positive Peak Detection
    PositivePeak = "POS"

    #: Sampl Mode Detection
    Sample = "SMP"


class AmplitudeUnits(StrEnum):
    """
    Enumeration to represent the amplitude units
    """

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
        """
        Initialize an ErrorCode

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
    """
    Represents the HP856XX series spectrum analyzers.
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
        values=[["AUTO", "MAN"], [10, 20, 30, 40, 50, 60, 70]]
    )

    amplitude_unit = Instrument.control(
        "AUNITS?", "AUNITS %s",
        """
        Control the amplitude unit with a selection of the following parameters: string
        'DBM', 'DBMV', 'DBUV', 'V', 'W', 'AUTO', 'MAN' or use the enum :class:`.AmplitudeUnits`

        Type: :code:`str`

        .. code-block:: python

            instr.amplitude_unit = 'DBMV'
            instr.amplitude_unit = AmplitudeUnits.DBMV

        """,
        validator=strict_discrete_set,
        values=[e for e in AmplitudeUnits]
    )

    def auto_couple(self):
        """
        Set the video bandwidth, resolution bandwidth, input attenuation,
        sweep time, and center frequency step-size to coupled mode. These functions can be recoupled
        individually or all at once. The spectrum analyzer chooses appropriate values for these
        functions. The video bandwidth and resolution bandwidth are set according to the coupled
        ratios stored under TODO and TODO.
        If no ratios are chosen, default ratios (1.0 and 0.011, respectively) are used instead.
        """
        self.write("AUTOCPL")

    def exchange_traces(self):
        """
        Exchange the contents of trace A with those of trace B. If the traces are
        in clear-write or max-hold mode, the mode is changed to view. Otherwise, the traces remain
        in their initial mode.
        """
        self.write("AXB")

    def blank_trace(self, trace):
        """
        Blank the chosen trace from the display. The current contents of the
        trace remain in the trace but are not updated.

        .. code-block:: python

            instr.blank_trace('TRA')
            instr.blank_trace(Trace.A)

        :param trace: A representation of the trace, either from :class:`.Trace` or
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
        """
        Subtract the display line from trace B and places the result in dBm
        (when in log mode) in trace B, which is then set to view mode. In linear mode, the results
        are in volts.
        """
        self.write("BML")

    center_frequency = Instrument.control(
        "CF?", "CF %.11E",
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
        """
        Set the chosen trace to clear-write mode. This mode sets each element
        of the chosen trace to the bottom-screen value;
        then new data from the detector is put in the trace with each sweep

        .. code-block:: python

            instr.clear_write_trace('TRA')
            instr.clear_write_trace(Trace.A)

        :param trace: A representation of the trace, either from :class:`.Trace` or
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

    def continuous_sweep(self):
        """
        Set the instrument to continuous-sweep mode. This mode enables another
        sweep at the completion of the current sweep once the trigger conditions are met.
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

        Takes a representation of the coupling mode, either from :class:`.CouplingMode` or
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

        Takes a representation of the demodulation mode, either from :class:`.DemodulationMode` or
        use 'OFF', 'AM', 'OFF'

        .. code-block:: python

            instr.demodulation_mode = 'AC'
            instr.demodulation_mode = DemodulationMode.AM

            if instr.demodulation_mode == DemodulationMode.FM:
                instr.demodulation_mode = Demodulation.OFF

        """,
        validator=strict_discrete_set,
        values=[e for e in DemodulationMode]
    )

    demodulation_agc = Instrument.control(
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

        Takes a representation of the detector mode, either from :class:`.DetectionModes` or
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
        "DL?", "DL %s",
        """
        Activate a horizontal display line for use as a visual aid or for
        computational purposes. The default value is 0 dBm.

        Type: :code:`float`, :code:`str`

        Takes a value with the unit of :attr:`amplitude_unit` or 'ON' / 'OFF'

        .. code-block:: python

            instr.display_line = 'ON'
            instr.display_line = -10

            if instr.detector_mode == 0:
                pass

        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[float("-inf"), float("inf")], ["ON", "OFF"]],
        set_process=lambda v: v if isinstance(v, str) else '%.11E' % v
    )

    done = Instrument.measurement(
        "DONE?",
        """
        Returns True to the controller when all commands in a command string
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

        """,
        map_values=True,
        values={True: "1"},
        cast=str
    )

    errors = Instrument.measurement(
        "ERR?",
        """
        Outputs a list of errors present (of type :class:`ErrorCode`). An empty list means there
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
        Returns the elapsed time (in hours) of analyzer operation.
        This value can be reset only by Hewlett-Packard.

        Type: :code:`int`

        .. code-block:: python

            print(elapsed_time)
            1998

        """,
        cast=int
    )

    start_frequency = Instrument.control(
        "FA?", "FA %.11E",
        """
        Constrol the start frequency and set the spectrum analyzer to start-frequency/
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
        "FB?", "FB %.11E",
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
        Diagnostic Attribute
        Returns the sampling oscillator frequency corresponding to the current start
        frequency.

        Type: :code:`float`
        """
    )

    lo_frequency = Instrument.measurement(
        "FDIAG LO,?",
        """
        Diagnostic Attribute
        Returns the first local oscillator frequency corresponding to the current start
        frequency.

        Type: :code:`float`
        """
    )

    mroll_frequency = Instrument.measurement(
        "FDIAG MROLL,?",
        """
        Diagnostic Attribute
        Returns the main roller oscillator frequency corresponding to the current start
        frequency, except then the resolution bandwidth is less than or equal to 100 Hz.

        Type: :code:`float`
        """
    )

    oroll_frequency = Instrument.measurement(
        "FDIAG OROLL,?",
        """
        Diagnostic Attribute
        Returns the offset roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.

        Type: :code:`float`
        """
    )

    xroll_frequency = Instrument.measurement(
        "FDIAG XROLL,?",
        """
        Diagnostic Attribute
        Returns the transfer roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.

        Type: :code:`float`
        """
    )

    sampler_harmonic_number = Instrument.measurement(
        "FDIAG HARM,?",
        """
        Diagnostic Attribute
        Returns the sampler harmonic number corresponding to the current start
        frequency.

        Type: :code:`int`
        """,
        get_process=lambda v: int(float(v))
    )

    # practically you could also write "OFF" to actively disable it or reset via "IP"
    frequency_display = Instrument.measurement(
        "FDSP?",
        """
        Returns 'False' if all annotations that describes the spectrum analyzer frequency
        setting are displayed. And vice versa 'True'. This includes the start and stop
        frequencies, the center frequency, the frequency span, marker readouts, the center
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

    def fft(self, source, destination, window):
        """
        The FFT command performs a discrete Fourier transform on the source trace array and stores
        the logarithms of the magnitudes of the results in the destination array. The maximum length
        of any of the traces is 601 points.
        Takes type 'Trace' or 'TRA', 'TRB'
        FFT is designed to be used in transforming zero-span amplitude-modulation information into
        the frequency domain. Performing an FFT on a frequency sweep will not provide time-domain
        results. The FFT results are displayed on the spectrum analyzer in a logarithmic
        amplitude scale. For the horizontal dimension, the frequency at the left side of the
        graph is 0 Hz, and at the right side is Finax- Fmax is equal to 300 divided by sweep time.
        As an example, if the sweep time of the analyzer is 60 ms, Fmax equals 5 kHz.
        The FFT algorithm assumes that the sampled signal is periodic with an integral number of
        periods within the time-record length (that is, the sweep time of the analyzer). Given this
        assumption, the transform computed is that of a time waveform of infinite duration, formed
        of concatenated time records. In actual measurements, the number of periods of the sampled
        signal within the time record may not be integral. In this case, there is a step
        discontinuity at the intersections of the concatenated time records in the assumed time
        waveform of infinite duration. This step discontinuity causes measurement errors,
        both amplitude uncertainty (where the signal level appears to vary with small changes in
        frequency) and frequency resolution (due to filter shape factor and sidelobes). Windows
        are weighting functions that are applied to the input data to force the ends of that
        data smoothly to zero, thus reducing the step discontinuity and reducing measurement
        errors.
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
        "FOFFSET?", "FOFFSET %.11E",
        """
        Add a specified offset to the displayed absolute-frequency values,
        including marker-frequency values. It does not affect the frequency range of the sweep, nor
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

    frequency_reference = Instrument.control(
        "FREF?", "FREF %s",
        """
        Control the frequency reference source.
        Select either the internal frequency reference (INT) or supply your own external
        reference (EXT). An external reference must be 10 MHz (+100 Hz) at a minimum amplitude of
        0 dBm. Connect the external reference to J9 (10 MHz REF IN/OUT) on the rear panel. When
        the external mode is selected, an "X" appears on the left edge of the display.

        Type: :code:`str`

        Takes element of :class:`.FrequencyReference` or use 'INT', 'EXT'

        .. code-block:: python

            instr.frequency_reference = 'INT'
            instr.frequency_reference = FrequencyReference.EXT

            if instr.frequency_reference == FrequencyReference.INT:
                instr.frequency_reference = FrequencyReference.EXT

        """,
        validator=strict_discrete_set,
        values=[e for e in FrequencyReference]
    )

    def full_span(self):
        """
        Set the spectrum analyzer to the full frequency span as defined by the instrument. The full
        span is 2.9 GHz for the HP 8560A. For the HP 8561B, the full span is 6.5 GHz.
        """
        self.write("FS")

    graticule = Instrument.control(
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
        """
        Freeze the active function at its current value. If no function is active, no
        operation takes place.
        """
        self.write("HD")

    id = Instrument.measurement(
        "ID?",
        """
        Returns identification of the device with software and hardware revision (e.g. HP8560A,002,
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
        """
        Set the spectrum analyzer to a known, predefined state.
        'preset' does not affect the contents of any data or trace registers or stored preselector
        data. 'preset' does not clear the input or output data buffers; to clear these, execute the
        statement CLEAR 718.
        """
        self.write("IP")

    logarithmic_scale = Instrument.control(
        "LG?", "LG %d",
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

    def linear_scale(self):
        """
        Set the spectrum analyzers display to linear amplitude scale. Measurements made on a linear
        scale can be read out in any units.
        """
        self.write("LN")

    def minimum_hold(self, trace):
        """
        Update the chosen trace with the minimum signal level detected at each
        trace-data point from subsequent sweeps. This function employs the negative peak detector
        (refer to the DET command).

        .. code-block:: python

            instr.minimum_hold('TRA')
            instr.minimum_hold(Trace.A)

        :param trace: A representation of the trace, either from :class:`.Trace` or
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
        Returns the amplitude of the active marker. If no marker is active, MKA
        places a marker at the center of the trace and returns that amplitude value.
        In the :meth:`amplitude_unit` unit.

        Type: :code:`float`

        .. code-block:: python

            level = instr.marker_amplitude
            unit = instr.amplitude_unit
            print("Level: %f %s" % (level, unit))

        """
    )

    def marker_to_center_frequency(self):
        """
        Set the center frequency to the frequency value of an active marker.
        """
        self.write("MKCF")

    marker_delta = Instrument.control(
        "MKD?", "MKD %.11E",
        """
        Place a second marker on the trace. The number specifies the distance
        in frequency or time (when in zero span) between the two markers.
        If queried - returns the frequency of the second marker.

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
        "MKF?", "MKF %.11E",
        """
        Place an active marker on the chosen frequency or can be queried to
        return the frequency of the active marker. Default units are in Hertz.

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

    def frequency_counter_mode(self, activate):
        """
        Activate a frequency counter that counts the frequency of the active
        marker or the difference in frequency between two markers. If no marker is active,
        'frequency_counter_mode' places a marker at the center of the trace and counts that marker
        frequency. The frequency counter provides a more accurate frequency reading; it pauses
        at the marker, counts the value, then continues the sweep. To adjust the frequency
        counter resolution, use the 'frequency_counter_resolution' command. To return the counter
        value, use the 'marker_frequency' command.

        :param activate: Whether to activate or to deactivate the frequency counter mode
        :type activate: bool

        .. code-block:: python

            instr.frequency_counter_mode(True)

        """

        if not isinstance(activate, bool):
            raise TypeError("Should be of type bool but is '%s'" % type(activate))

        parameter = "OFF"
        if activate:
            parameter = "ON"

        self.write("MKFC %s" % parameter)

    frequency_counter_resolution = Instrument.control(
        "MKFCR?", "MKFCR %d",
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

    def marker_minimum(self):
        """
        Place an active marker on the minimum signal detected on a trace.
        """
        self.write("MKMIN")

    # here would be the implementation of the command 'marker_normal' ('MKN') but
    # it has no advantage over the 'marker_frequency' command except if no marker is active it
    # places it automagically to the center of the trace (I think there's no sense in
    # implementing it here)

    marker_noise_mode = Instrument.control(
        "MKNOISE?", "MKNOISE %s",
        """
        Control the detector mode to sample and compute the average of 32 data points (16 points
        on one side of the marker, the marker itself, and 15 points on the other side of the
        marker). This average is corrected for effects of the log or linear amplifier, bandwidth
        shape factor, IF detector, and resolution bandwidth. If two markers are on (whether in
        'marker_delta' mode or 1/marker delta mode), 'marker_noise_mode' works on the active marker
        and not on the anchor marker. This allows you to measure signal-to-noise density directly.
        To query the value, use the 'marker_amplitude' command.

        Type: :code:`bool`

        .. code-block:: python

            # activate signal-to-noise density mode
            instr.marker_noise_mode = True

            # get noise density by `marker_amplitude`
            print("Signal-to-noise density: %d dbm / Hz" % instr.marker_amplitude)

        """,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )


class HP8560A(HP856Xx):
    """
    Represents the HP 8560A Spectrum Analyzer and
    provides a high-level interface for interacting with the instrument.

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


class HP8561B(HP856Xx):
    """
    Represents the HP 8561B Spectrum Analyzer and
    provides a high-level interface for interacting with the instrument.

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

    mixer_mode = Instrument.control(
        "MXRMODE?", "MXRMODE %s",
        """
        Specifie the mixer mode. Select either the internal mixer
        or supply an external mixer. Takes enum 'MixerMode' or string 'INT', 'EXT'
        """,
        validator=strict_discrete_set,
        values=[e for e in MixerMode]
    )

    conversion_loss = Instrument.control(
        "CNVLOSS?", "CNVLOSS %s",
        """
        Compensate for losses outside the instrument when in external
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

    def fullband(self, band):
        """
        Select a commonly-used, external-mixer frequency band, as shown
        in the table. The harmonic lock function :attr:`harmonic_number_lock` is also set; this
        locks the harmonic of the chosen band. External-mixing functions are not available with
        an HP 8560A Option 002. Takes frequency band letter as string.

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
        "HNLOCK?", "HNLOCK %s",
        """
        Lock a chosen harmonic so only that harmonic is used to sweep
        an external frequency band. To select a frequency band, use the 'fullband' command; it
        selects an appropriate harmonic for the desired band. To change the harmonic number, use
        'harmonic_number_lock'.
        Note that 'harmonic_number_lock' also works in internal-mixing modes.
        Once 'fullband' or 'harmonic_number_lock' are set, only center frequencies and spans that
        fall within the frequency band of the current harmonic may be entered. When the 'full_span'
        command is activated, the span is limited to the frequency band of the selected harmonic.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[int(1), int(54)], ["ON", "OFF"]],
        cast=int
    )

    def harmonic_number_unlock(self):
        """
        Unlock the harmonic number, allowing you to select frequencies and
        spans outside the range of the locked harmonic number. Also, when HNUNLK is executed,
        more than one harmonic can then be used to sweep across a desired span. For example, sweep
        a span from 18 GHz to 40 GHz. In this case, the analyzer will automatically sweep first
        using 6—, then using 8—.
        """
        self.write("HUNLK")

    def signal_identification_to_center_frequency(self):
        """
        Set the center frequency to the frequency obtained from the command
        SIGID. SIGID must be in AUTO mode and have found a valid result for this command to
        execute properly. Use SIGID on signals greater than 18 GHz {i.e., in external mixing mode).
        SIGID and IDCF may also be used on signals less than 6.5 GHz in an HP 8561B.
        """
        self.write("IDCF")

    signal_identification_frequency = Instrument.measurement(
        "IDFREQ?",
        """
        Returns the frequency of the last identified signal. After an instrument preset or an
        invalid signal identification, IDFREQ returns a “0”.
        """
    )

    mixer_bias = Instrument.control(
        "MBIAS?", "MBIAS %s",
        """
        Set the bias for an external mixer that requires diode bias for efficient
        mixer operation. The bias, which is provided on the center conductor of the IF input, is
        activated when MBIAS is executed. A "+" or "—" appears on the left edge of the spectrum
        analyzer display, indicating that positive or negative bias is on. When the bias is
        turned off, MBIAS is set to 0. Default units are in milliamps.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[float(-10E3), int(10E3)], ["ON", "OFF"]],
        cast=float
    )
