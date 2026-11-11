#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from enum import IntFlag

from pymeasure.instruments import AdapterType, Channel, Instrument
from pymeasure.instruments.common_base import cast_or_str
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import (
    joined_validators,
    strict_discrete_set,
    strict_range,
    truncated_discrete_set,
)


class EventStatusByte(IntFlag):
    """Event Status Register (ESR) flags."""
    NONE = 0
    OPC = 1            # Bit 0: Operation Complete
    B1 = 2             # Bit 1: unused
    QYE = 4            # Bit 2: Query Error
    DDE = 8            # Bit 3: Device Specific Error
    EXE = 16           # Bit 4: Execution Error
    CME = 32           # Bit 5: Command Error
    B6 = 64            # Bit 6: unused
    PON = 128          # Bit 7: Power On


class StatusByte(IntFlag):
    """Status Byte (STB) flags."""
    NONE = 0
    B0 = 1             # Bit 0: unused
    B1 = 2             # Bit 1: unused
    ERR_QUEUE = 4      # Bit 2: Error(s) in Queue
    QDS = 8            # Bit 3: Questionable Data Summary
    MAV = 16           # Bit 4: Message Available
    SES = 32           # Bit 5: Standard Event Summary
    MSS = 64           # Bit 6: Master Summary Status
    OSR = 128          # Bit 7: Operation Status Register


class RigolGeneratorChannel(Channel):
    """Represents a voltage channel of a Rigol signal generator.

    .. code-block:: python

        c1 = fgen.channel_1
        c1.sine=(1e4, 4, 0, 0)

    """

    POLARITY = {
        "normal": "NORMAL",
        "inverted": "INVERTED"
    }

    # adjust for newer models: is NORM and INV there
    SYNC_POLARITY = {
        "positive": "POS",
        "negative": "NEG"
    }

    output_enabled = Channel.control(
        ":OUTP{ch}?",
        ":OUTP{ch} %s",
        """Control the status of the channel.
        True if the channel is on and False if not.""",
        validator=truncated_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    load = Channel.control(
        ":OUTP{ch}:LOAD?",
        ":OUTP{ch}:LOAD %s",
        """Control the output impedance of a given channel.
         Returns 9.9e+37 for infinite impedance.""",
        validator=joined_validators(strict_discrete_set, strict_range),
        values=[['INF'], [1, 10000]],
    )

    polarity = Channel.control(
        ":OUTP{ch}:POL?",
        ":OUTP{ch}:POL %s",
        """Control the output polarity of the specified channel.""",
        validator=truncated_discrete_set,
        values=POLARITY,
        map_values=True,
        cast=str,
    )

    sync_enabled = Channel.control(
        ":OUTP{ch}:SYNC?",
        ":OUTP{ch}:SYNC %s",
        """Control the synchronization flag.
          True if the channel triggers the synchronization connector and False if not """,
        validator=truncated_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    sync_polarity = Channel.control(
        ":OUTP{ch}:SYNC:POL?",
        ":OUTP{ch}:SYNC:POL %s",
        """Control the output polarity of sync signal of the specified channel.""",
        validator=truncated_discrete_set,
        values=SYNC_POLARITY,
        map_values=True,
        cast=str,
    )

    frequency = Channel.control(
        ":SOUR{ch}:FREQ?",
        ":SOUR{ch}:FREQ %f",
        """ Control the output frequency (Hz)"""
    )

    waveform = Channel.measurement(
        ":SOUR{ch}:APPL?",
        """
        Get a description of the waveform applied.
        List: [type_string, frequency, amplitude, offset, phase]
        """,
        cast=cast_or_str(float),
    )

    sine = Channel.setting(
        ":SOUR{ch}:APPL:SIN %f,%f,%f,%f",
        """
        Set the waveform generator to output a sine of specified parameters
        :param int freq: The frequency of the sine in Hz
        :param float ampl: The peak to peak amplitude of the sine in V
        :param float offset: The DC offset of the sine in V
        :param float phase: The phase offset of the sine in degrees
        """,
    )

    square = Channel.setting(
        ":SOUR{ch}:APPL:SQU %f,%f,%f,%f",
        """
        Set the waveform generator to output a square wave of specified parameters
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )

    square_duty_cycle = Channel.control(
        ":SOUR{ch}:FUNC:SQU:DCYC?",
        ":SOUR{ch}:FUNC:SQU:DCYC %f",
        """
        Control the duty cycle of square out of the waveform generator. (float)
        """,
    )

    square_period = Channel.control(
        ":SOUR{ch}:FUNC:SQU:PER?",
        ":SOUR{ch}:FUNC:SQU:PER %f",
        """
        Control the period of square waves (in seconds) out of the waveform generator.
        """,
    )

    # FIXME: model-dependent behavior: DG800 uses current ramp symmetry (default:50%, i.e. triangle)
    #       whereas e.g. DG6000 uses the max symmetry and overwrites the current symmetry setting
    #       with it (... and has a separate triangle command)
    ramp = Channel.setting(
        ":SOUR{ch}:APPL:RAMP %f,%f,%f,%f",
        """
        Set the waveform generator to output a ramp wave of specified parameters
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )

    pulse = Channel.setting(
        ":SOUR{ch}:APPL:PULS %f,%f,%f,%f",
        """
        Set the waveform generator to output a pulse wave of specified parameters
        Note that the duty cycle is specified using the pulse_duty_cycle method.
        :param int freq: The frequency of the wave in Hz
        :param float ampl: The peak to peak amplitude of the wave in V
        :param float offset: The DC offset of the wave in V
        :param float phase: The phase offset of the wave in degrees
        """,
    )

    pulse_duty_cycle = Channel.control(
        ":SOUR{ch}:FUNC:PULS:DCYC?",
        ":SOUR{ch}:FUNC:PULS:DCYC %f",
        """
        Control the duty cycle of pulses out of the waveform generator. (float)
        """,
    )

    pulse_width = Channel.control(
        ":SOUR{ch}:FUNC:PULS:WIDT?",
        ":SOUR{ch}:FUNC:PULS:WIDT %f",
        """
        Control the pulse width of pulses (in seconds) out of the waveform generator.
        """,
    )


class RigolGenerator(SCPIMixin, Instrument):
    """Provide the SCPI core shared by supported Rigol generator families.

    :param adapter: Adapter object or resource identifier used for communication.
    :param name: Name of the instrument.
    :param kwargs: Additional arguments passed to :class:`~pymeasure.adapters.VISAAdapter` when
        ``adapter`` is a string or integer; discarded when it is an Adapter object.

    """

    def __init__(self, adapter: AdapterType, name: str = "Rigol generator", **kwargs):
        super().__init__(adapter, name, **kwargs)

    event_status = Instrument.measurement(
        "*ESR?",
        """Get and clear the Standard Event Status Register (ESR, IntFlag).""",
        cast=lambda v: EventStatusByte(int(v))
    )

    def wait_for_opc(self, timeout: float = 10) -> None:
        """Block until the generator reports operation complete.

        :param timeout: Maximum time to wait in seconds.
        :raises TimeoutError: If the operation does not complete before ``timeout``.
        """
        deadline = time.monotonic() + timeout
        while True:
            if self.ask("*OPC?").strip() == "1":
                return
            if time.monotonic() > deadline:
                raise TimeoutError(f"wait_for_opc timed out after {timeout} s")
            time.sleep(0.1)
