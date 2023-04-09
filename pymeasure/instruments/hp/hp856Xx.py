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
    def __str__(self):
        return self.value


class Trace(StrEnum):
    A = "TRA"
    B = "TRB"


class MixerMode(StrEnum):
    Internal = "INT"
    External = "EXT"


class CouplingMode(StrEnum):
    AC = "AC"
    DC = "DC"


class DemodulationMode(StrEnum):
    Amplitude = "AM"
    Frequency = "FM"
    Off = "OFF"


class FrequencyReference(StrEnum):
    Internal = "INT"
    External = "EXT"


class DetectionModes(StrEnum):
    NegativePeak = "NEG"
    Normal = "NRM"
    PositivePeak = "POS"
    Sample = "SMP"


class AmplitudeUnits(StrEnum):
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

    attenuation = Instrument.control(
        "AT?", "AT %s",
        """
        Control input attenuation in decade steps from 10 to 70 db or set to AUTO and MAN(ual)
        """,
        validator=joined_validators(strict_discrete_set, truncated_discrete_set),
        values=[["AUTO", "MAN"], [10, 20, 30, 40, 50, 60, 70]]
    )

    amplitude_unit = Instrument.control(
        "AUNITS?", "AUNITS %s",
        """
        Control the amplitude unit with a selection of the following parameters: string
        'DBM', 'DBMV', 'DBUV', 'V', 'W', 'AUTO', 'MAN' or use the enum 'AmplitudeUnits'
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
        trace: Takes type 'Trace' selecting the trace or 'TRA', 'TRB'
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
        Set the center frequency in hertz and sets the spectrum analyzer to center
        frequency / span mode. The span remains constant; the start and stop frequencies change as
        the center frequency changes.
        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    def clear_write_trace(self, trace):
        """
        Set the chosen trace to clear-write mode. This mode sets each element
        of the chosen trace to the bottom-screen value;
        then new data from the detector is put in the trace with each sweep.
        trace: Takes type 'Trace' selecting the trace or 'TRA', 'TRB'
        """
        if not isinstance(trace, str):
            raise TypeError("Should be of type string but is '%s'" % type(trace))

        if trace not in [e for e in Trace]:
            raise ValueError("Only accepts values of [%s] but was '%s'" % ([e for e in Trace],
                                                                           trace))

        self.write("CLRW " + trace)

    def continuous_sweep(self):
        """
        Activate the continuous-sweep mode. This mode enables another
        sweep at the completion of the current sweep once the trigger conditions are met.
        """
        self.write("CONTS")

    coupling = Instrument.control(
        "COUPLE?", "COUPLE %s",
        """
        Set the input coupling to AC or DC coupling.
        Takes enum 'CouplingMode' or string 'AC', 'DC'. AC coupling protects
        the input of the analyzer from damaging dc signals, while limiting the lower frequency-range
        to 100 kHz (although the analyzer will tune down to 0 Hz with signal attenuation).
        """,
        validator=strict_discrete_set,
        values=[e for e in CouplingMode]
    )

    demodulation_mode = Instrument.control(
        "DEMOD?", "DEMOD %s",
        """
        Activates either AM or FM demodulation, or turns the demodulation —
        off. Takes enum 'DemodulationMode' or string 'OFF', 'AM', 'OFF'
        Place a marker on a desired signal and then activate the 'demodulation_mode';
        demodulation takes place on this signal. If no marker is on, 'demodulation_mode'
        automatically places a marker at the center of the
        trace and demodulates the frequency at that marker position. Use the volume and squelch
        controls to adjust the speaker and listen.
        """,
        validator=strict_discrete_set,
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
        "DEMODT?", "DEMODT %.11E",
        """
        Selects the amount of time that the sweep pauses at the marker to
        demodulate a signal. The default value is 1 second. When the frequency span equals 0 Hz,
        demodulation is continuous, except when between sweeps. For truly continuous demodulation,
        set the frequency span to 0 Hz and the trigger mode to single sweep (see TM).
        """,
        validator=strict_range,
        values=[100e-3, 60],
    )

    detector_mode = Instrument.control(
        "DET?", "DET %s",
        """
        Control the IF detector used for acquiring measurement data.
        Takes enum DetectionModes or string 'NEG', 'NRM', 'POS', 'SMP'. This is
        normally a coupled function, in which the spectrum analyzer selects the appropriate detector
        mode. Four modes are available: normal, positive, negative, and sample.
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
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[float("-inf"), float("inf")], ["ON", "OFF"]],
        set_process=lambda v: v if isinstance(v, str) else '%.11E' % v
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
        Outputs a list of errors present (of type ErrorCode). An error code of “0” means there are
        no errors present. For a list of error codes and descriptions, refer to Appendix C or the
        Installation and Verification Manual. Executing ERR clears all HP-IB errors.
        For best results, enter error data immediately after querying for errors.
        """,
        cast=ErrorCode,
    )

    elapsed_time = Instrument.measurement(
        "EL?",
        """
        Returns to the elapsed time (in hours) of analyzer operation.
        This value can be reset only by Hewlett-Packard.
        """,
        cast=int
    )

    start_frequency = Instrument.control(
        "FA?", "FA %.11E",
        """
        Set the start frequency and set the spectrum analyzer to start-frequency/
        stop-frequency mode. If the start frequency exceeds the stop frequency, the stop frequency
        increases to equal the start frequency plus 100 Hz. The center frequency and span change
        with changes in the start frequency.
        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    stop_frequency = Instrument.control(
        "FB?", "FB %.11E",
        """
        Set the stop frequency and sets the spectrum analyzer to start-frequency/
        stop-frequency mode. If the stop frequency is less than the start frequency, the start
        frequency decreases to equal the stop frequency minus 100 Hz. The center frequency and
        span change with changes in the stop frequency.
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
        """
    )

    lo_frequency = Instrument.measurement(
        "FDIAG LO,?",
        """
        Diagnostic Attribute
        Returns the first local oscillator frequency corresponding to the current start
        frequency.
        """
    )

    mroll_frequency = Instrument.measurement(
        "FDIAG MROLL,?",
        """
        Diagnostic Attribute
        Returns the main roller oscillator frequency corresponding to the current start
        frequency, except then the resolution bandwidth is less than or equal to 100 Hz.
        """
    )

    oroll_frequency = Instrument.measurement(
        "FDIAG OROLL,?",
        """
        Diagnostic Attribute
        Returns the offset roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.
        """
    )

    xroll_frequency = Instrument.measurement(
        "FDIAG XROLL,?",
        """
        Diagnostic Attribute
        Returns the transfer roller oscillator frequency corresponding to the current start
        frequency, except when the resolution bandwidth is less than or equal to 100 Hz.
        """
    )

    sampler_harmonic_number = Instrument.measurement(
        "FDIAG HARM,?",
        """
        Diagnostic Attribute
        Returns the sampler harmonic number corresponding to the current start
        frequency.
        """,
        get_process=lambda v: int(float(v))
    )

    # practically you could also write "OFF" to actively disable it or reset via "IP"
    frequency_display = Instrument.measurement(
        "FDSP?",
        """
        Returns if all annotations that describes the spectrum analyzer frequency
        setting are displayed or not. This includes the start and stop
        frequencies, the center frequency, the frequency span, marker readouts, the center
        frequency step-size, and signal identification to center frequency.  To retrieve the
        frequency data, query the spectrum analyzer.
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
        """,
        validator=strict_range,
        values=[0, 1],
        dynamic=True
    )

    frequency_reference = Instrument.control(
        "FREF?", "FREF %s",
        """
        The FREF command specifies the frequency reference source.
        Takes enum FrequencyReference or string 'INT', 'EXT'. Select either the internal
        frequency reference (INT) or supply your own external reference (EXT). An external reference
        must be 10 MHz (+100 Hz) at a minimum amplitude of 0 dBm. Connect the external
        reference to J9 (10 MHz REF IN/OUT) on the rear panel. When the external mode is
        selected, an "X" appears on the left edge of the display.
        """,
        validator=strict_discrete_set,
        values=[e for e in FrequencyReference]
    )

    def full_span(self):
        """
        Select the full frequency span as defined by the instrument. The full span
        is 2.9 GHz for the HP 8560A. For the HP 8561B, the full span is 6.5 GHz.
        """
        self.write("FS")

    graticule = Instrument.control(
        "GRAT?", "GRAT %s",
        """
        Turn the display graticule on or off.
        """,
        map_values=True,
        values={True: "1", False: "0"},
        validator=strict_discrete_set,
        cast=str
    )

    def hold(self):
        """
        Freezes the active function at its current value. If no function is active, no
        operation takes place.
        """
        self.write("HD")

    id = Instrument.measurement(
        "ID?",
        """
        Get identification of the device with software and hardware revision (e.g. HP8560A,002,H03)
        """,
        maxsplit=0,
        cast=str
    )

    def preset(self):
        """
        The IP command sets the spectrum analyzer to a known, predefined state.
        'preset' does not affect the contents of any data or trace registers or stored preselector
        data. 'preset' does not clear the input or output data buffers; to clear these, execute the
        statement CLEAR 718.
        """
        self.write("IP")


class HP8560A(HP856Xx):
    # HP8560A is able to go up to 2.9 GHz
    MAX_FREQUENCY = 6.5e9

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


class HP8561B(HP856Xx):
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
        The FULBAND command selects a commonly-used, external-mixer frequency band, as shown
        in the table. The harmonic lock function (HNLOCK) is also set; this locks the harmonic of
        the chosen band. External-mixing functions are not available with an HP 8560A Option 002.
        Takes frequency band letter as string.

        Frequency Band | Frequency Range (GHz) | Mixing Harmonic | Conversion Loss
        K   18.0—26.5       6- 30 dB
        A   26.5—40.0       8- 30 dB
        Q   33.0—50.0       10- 30 dB
        U   40.0—60.0       10- 30 dB
        V   50.0—75.0       14- 30 dB
        E   60.0—-90.0      16- 30 dB
        W   75.0—110.0      18- 30 dB
        F   90.0—140.0      24— 30 dB
        D   110.0—170.0     30- 30 dB
        G   140.0—220.0     36-— 30 dB
        Y   170.0—260.0     44-— 30 dB
        J   220.0—325.0     54- 30 dB
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
        The IDCF command sets the center frequency to the frequency obtained from the command
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
