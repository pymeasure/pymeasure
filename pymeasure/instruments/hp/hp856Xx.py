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


class HP8560A(HP856Xx):
    # HP8560A is able to go up to 2.9 GHz
    freq_center_values = [[0, 2.9e9], ["UP", "DN"]]

    def __init__(self, name="Hewlett-Packard HP8560A", **kwargs):
        super().__init__(
            name,
            **kwargs,
        )


class HP8561B(HP856Xx):
    # HP8561B is able to go up to 6.5 GHz
    freq_center_values = [[0, 6.5e9], ["UP", "DN"]]

    def __init__(self, name="Hewlett-Packard HP8561B", **kwargs):
        super().__init__(
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
