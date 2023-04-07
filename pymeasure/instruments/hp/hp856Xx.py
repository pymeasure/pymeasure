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
from decimal import Decimal

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, \
    joined_validators, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Trace(str, Enum):
    A = "TRA"
    B = "TRB"


class MixerMode(str, Enum):
    Internal = "INT"
    External = "EXT"


class CouplingMode(str, Enum):
    AC = "AC"
    DC = "DC"


class DemodulationMode(str, Enum):
    Amplitude = "AM"
    Frequency = "FM"
    Off = "OFF"


class DetectionModes(str, Enum):
    NegativePeak = "NEG"
    Normal = "NRM"
    PositivePeak = "POS"
    Sample = "SMP"


class AmplitudeUnits(str, Enum):
    DBM = "DBM"
    DBMV = "DBMV"
    DBUV = "DBUV"
    V = "V"
    W = "W"
    AUTO = "AUTO"
    MANUAL = "MAN"


class ErrorCode:
    __error_code_list = {
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

    def __init__(self, code: int):
        self.code = int(code)
        (self.short, self.long) = self.__error_code_list[self.code]

    def __repr__(self):
        return "ErrorCode(\"" + self.short + " - " + self.long + "\")"

    def __eq__(self, other):
        return self.code == other.code

class HP856Xx(Instrument):
    """

    Some command descriptions are taken from the document: 'HP 8560A, 8561B Operating & Programming'
    """

    def __init__(self, adapter, name="Hewlett-Packard HP856Xx", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    id = Instrument.measurement(
        "ID?",
        """
        Get identification of the device with software and hardware revision (e.g. HP8560A,002,H03)
        """,
        maxsplit=0
    )

    attenuation = Instrument.control(
        "AT?", "AT %s",
        """
        Controls input attenuation in decade steps from 10 to 70db or set to AUTO and MAN(ual)
        as well as incremental control via UP/DN
        """,
        validator=joined_validators(strict_discrete_set, truncated_discrete_set),
        values=[["AUTO", "MAN", "UP", "DN"], [10, 20, 30, 40, 50, 60, 70]]
    )

    amplitude_unit = Instrument.control(
        "AUNITS?", "AUNITS %s",
        """
        Controls the amplitude unit with a selection of the following parameters:
        'DBM', 'DBMV', 'DBUV', 'V', 'W', 'AUTO', 'MAN'
        and affects the following properties:
        """,
        validator=strict_discrete_set,
        set_process=lambda v: v.value,
        values=[e for e in AmplitudeUnits]
    )

    def auto_couple(self):
        """
        Sets video bandwidth, resolution bandwidth, input attenuation,
        sweep time, and center frequency step-size to coupled mode. These functions can be recoupled
        individually or all at once. The spectrum analyzer chooses appropriate values for these
        functions. The video bandwidth and resolution bandwidth are set according to the coupled
        ratios stored under TODO and TODO.
        If no ratios are chosen, default ratios (1.0 and 0.011, respectively) are used instead.
        """
        self.write("AUTOCPL")

    def exchange_traces(self):
        """
        Exchanges the contents of trace A with those of trace B. If the traces are
        in clear-write or max-hold mode, the mode is changed to view. Otherwise, the traces remain
        in their initial mode.
        """
        self.write("AXB")

    def blank_trace(self, trace: Trace):
        """
        Blanks the chosen trace from the display. The current contents of the
        trace remain in the trace but are not updated.
        trace: Takes type 'Trace' selecting the trace
        """
        self.write("BLANK " + trace)

    def subtract_display_line_from_trace_b(self):
        """
        Subtracts the display line from trace B and places the result in dBm
        (when in log mode) in trace B, which is then set to view mode. In linear mode, the results
        are in volts.
        """
        self.write("BML")

    freq_center = Instrument.control(
        "CF?", "CF %s",
        """
        Sets the center frequency in hertz and sets the spectrum analyzer to center
        frequency / span mode. The span remains constant; the start and stop frequencies change as
        the center frequency changes.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[0, 1], ["UP", "DN"]],
        dynamic=True,
        set_process=lambda v: v if isinstance(v, str) else (
                '%.11E HZ' % Decimal(v)).replace('+', ''
                                                 )
    )

    def clear_write_trace(self, trace: Trace):
        """
        Sets the chosen trace to clear-write mode. This mode sets each element
        of the chosen trace to the bottom-screen value;
        then new data from the detector is put in the trace with each sweep.
        trace: Takes type 'Trace' selecting the trace
        """
        self.write("CLRW " + trace)

    def continuous_sweep(self):
        """
        Activates the continuous-sweep mode. This mode enables another
        sweep at the completion of the current sweep once the trigger conditions are met.
        """
        self.write("CONTS")

    coupling = Instrument.control(
        "COUPLE?", "COUPLE %s",
        """
        Specifies the mixer mode. Select either the internal mixer
        or supply an external mixer.
        """,
        validator=strict_discrete_set,
        set_process=lambda v: v.value,
        values=[e for e in CouplingMode]
    )

    demodulation_mode = Instrument.control(
        "DEMOD?", "DEMOD %s",
        """
        Activates either AM or FM demodulation, or turns the demodulation —
        off. Place a marker on a desired signal and then activate the 'demodulation_mode';
        demodulation takes place on this signal. If no marker is on, 'demodulation_mode'
        automatically places a marker at the center of the
        trace and demodulates the frequency at that marker position. Use the volume and squelch
        controls to adjust the speaker and listen.
        """,
        validator=strict_discrete_set,
        set_process=lambda v: v.value,
        values=[e for e in DemodulationMode]
    )

    demodulation_agc = Instrument.control(
        "DEMODAGC?", "DEMODAGC %s",
        """
        Turns the demodulation automatic gain control (AGC) on or off.
        The AGC keeps the volume of the speaker relatively constant during AM demodulation. AGC
        is available only during AM demodulation and when the frequency span is greater than 0 Hz.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "1", False: "0"},
        cast=str
    )

    demodulation_time = Instrument.control(
        "DEMODT?", "DEMODT %s",
        """
        Selects the amount of time that the sweep pauses at the marker to
        demodulate a signal. The default value is 1 second. When the frequency span equals 0 Hz,
        demodulation is continuous, except when between sweeps. For truly continuous demodulation,
        set the frequency span to 0 Hz and the trigger mode to single sweep (see TM).
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[100e-3, 60], ["UP", "DN"]],
        set_process=lambda v: v if isinstance(v, str) else ('%.11E' % Decimal(v)).replace('+', '')
    )

    detector_mode = Instrument.control(
        "DET?", "DET %s",
        """
        Specifies the IF detector used for acquiring measurement data. This is
        normally a coupled function, in which the spectrum analyzer selects the appropriate detector
        mode. Four modes are available: normal, positive, negative, and sample. The modes are
        described below. When a mode other than normal is chosen, a "D" appears on the left side of
        the display.
        """,
        validator=strict_discrete_set,
        set_process=lambda v: v.value,
        values=[e for e in DetectionModes]
    )

    # now implemented as a property but due to the ability of the underlying gpib command to
    # specify the unit, there would be an alternative implementation as a method to allow the user
    # to modify the setting unit without manipulating it via the 'amplitude_unit' property
    display_line = Instrument.control(
        "DL?", "DL %s",
        """
        Activates a horizontal display line for use as a visual aid or for
        computational purposes. The default value is 0 dBm. 'UP' or 'DN' changes the display line 
        by one vertical division.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[float("-inf"), float("inf")], ["ON", "OFF", "UP", "DN"]],
        set_process=lambda v: v if isinstance(v, str) else ('%.11E' % Decimal(v)).replace('+', '')
    )

    done = Instrument.measurement(
        "DONE?",
        """
        Returns True to the controller when all commands in a command string
        entered before DONE have been completed. Sending a 'triggger_sweep' command before DONE 
        ensures
        that the spectrum analyzer will complete a full sweep before continuing on in a program.
        
        Depending on the timeout a timeout error from the adapter will raise before the spectrum 
        analyzer can finish due to an extreme long sweep time
        """,
        map_values=True,
        values={True: "1"},
        cast=str
    )

    errors = Instrument.measurement(
        "ERR?",
        """
        Outputs a list of errors present. An error code of “0” means there are
        no errors present. For a list of error codes and descriptions, refer to Appendix C or the
        Installation and Verification Manual. Executing ERR clears all HP-IB errors. 
        For best results, enter error data immediately after querying for errors.
        """,
        cast=ErrorCode,
    )




class HP8560A(HP856Xx):
    # HP8560A is able to go up to 2.9 GHz
    freq_center_values = [[0, 2.9e9], ["UP", "DN"]]

    def __init__(self, adapter, name="Hewlett-Packard HP8560A", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )


class HP8561B(HP856Xx):
    # HP8561B is able to go up to 6.5 GHz
    freq_center_values = [[0, 6.5e9], ["UP", "DN"]]

    def __init__(self, adapter, name="Hewlett-Packard HP8561B", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

    mixer_mode = Instrument.control(
        "MXRMODE?", "MXRMODE %s",
        """
        Specifies the mixer mode. Select either the internal mixer
        or supply an external mixer.
        """,
        validator=strict_discrete_set,
        set_process=lambda v: v.value,
        values=[e for e in MixerMode]
    )

    conversion_loss = Instrument.control(
        "CNVLOSS?", "CNVLOSS %s",
        """
        Compensates for losses outside the instrument when in external
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
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[0, float("inf")], ["UP", "DN"]],
        set_process=lambda v: str(v) + " DB" if isinstance(v, float) else v
    )
