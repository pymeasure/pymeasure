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
from time import sleep
from warnings import warn

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Defined outside of the class, since it is used by `Instrument.control` without access to `self`.
MIN_GATE_TIME = 2e-8  # Programmer's guide 8-92
MAX_GATE_TIME = 1000  # Programmer's guide 8-92
MIN_BUFFER_SIZE = 4  # Programmer's guide 8-39
MAX_BUFFER_SIZE = 10000  # Programmer's guide 8-39


class CNT91(SCPIUnknownMixin, Instrument):
    """Represents a Pendulum CNT-91 frequency counter."""

    CHANNELS = {"A": 1, "B": 2, "C": 3, "E": 4, "INTREF": 6}

    def __init__(self, adapter, name="Pendulum CNT-91", **kwargs):
        # allow long-term measurements, add 30 s for data transfer
        kwargs.setdefault("timeout", 24 * 60 * 60 * 1000 + 30)
        kwargs.setdefault("read_termination", "\n")

        super().__init__(
            adapter,
            name,
            asrl={"baud_rate": 256000},
            **kwargs,
        )

    @property
    def batch_size(self):
        """Get maximum number of buffer entries that can be transmitted at once."""
        if not hasattr(self, "_batch_size"):
            self._batch_size = int(self.ask("FORM:SMAX?"))
        return self._batch_size

    external_start_arming_source = Instrument.control(
        "ARM:SOUR?",
        "ARM:SOUR %s",
        """Control external arming source ('A', 'B', 'E' (rear) or 'IMM' for immediately arming).""",  # noqa: E501
        validator=strict_discrete_set,
        values={"A": "EXT1", "B": "EXT2", "E": "EXT4", "IMM": "IMM"},
        map_values=True,
    )

    external_arming_start_slope = Instrument.control(
        "ARM:SLOP?",
        "ARM:SLOP %s",
        """Control slope for the start arming condition (str 'POS' or 'NEG').""",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
    )

    continuous = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %s",
        """Control whether to perform continuous measurements.""",
        strict_discrete_set,
        values={True: 1.0, False: 0.0},
        map_values=True,
    )

    @property
    def measurement_time(self):
        """
        Control gate time of one measurement in s (float strictly from 2e-8 to 1000).

        .. deprecated:: 0.14
           Use `gate_time` instead.
        """
        warn("`measurement_time` is deprecated, use `gate_time` instead.", FutureWarning)
        return self.gate_time

    @measurement_time.setter
    def measurement_time(self, value):
        warn("`measurement_time` is deprecated, use `gate_time` instead.", FutureWarning)
        self.gate_time = value

    gate_time = Instrument.control(
        ":ACQ:APER?",
        ":ACQ:APER %s",
        """Control gate time of one measurement in s (float strictly from 2e-8 to 1000).""",
        validator=strict_range,
        values=[MIN_GATE_TIME, MAX_GATE_TIME],  # Programmer's guide 8-92
    )

    format = Instrument.control(
        "FORM?",
        "FORM %s",
        "Control response format ('ASCII' or 'REAL').",
        validator=strict_discrete_set,
        values={"ASCII": "ASC", "REAL": "REAL"},
        map_values=True,
    )

    interpolator_autocalibrated = Instrument.control(
        ":CAL:INT:AUTO?",
        "CAL:INT:AUTO %s",
        """Control if interpolators should be calibrated automatically (bool).""",
        strict_discrete_set,
        values={True: 1.0, False: 0.0},
        map_values=True,
    )

    def read_buffer(self, n=MAX_BUFFER_SIZE):
        """
        Read out `n` samples from the buffer.

        :param n: Number of samples that should be read from the buffer. The maximum number of
            10000 samples is read out by default.
        :return: Frequency values from the buffer.
        """
        n = truncated_range(n, [MIN_BUFFER_SIZE, MAX_BUFFER_SIZE])  # Programmer's guide 8-39
        while not self.complete:
            # Wait until the buffer is filled.
            sleep(0.01)
        return self.values(f":FETC:ARR? {'MAX' if n == MAX_BUFFER_SIZE else n}")

    def configure_frequency_array_measurement(self, n_samples, channel, back_to_back=True):
        """
        Configure the counter for an array of measurements.

        :param n_samples: The number of samples
        :param channel: Measurement channel (A, B, C, E, INTREF)
        :param back_to_back: If True, the buffer measurement is performed back-to-back.
        """
        n_samples = truncated_range(n_samples, [MIN_BUFFER_SIZE, MAX_BUFFER_SIZE])
        channel = strict_discrete_set(channel, self.CHANNELS)
        channel = self.CHANNELS[channel]
        self.write(f":CONF:ARR:FREQ{':BTB' if back_to_back else ''} {n_samples},(@{channel})")

    def buffer_frequency_time_series(
        self,
        channel,
        n_samples,
        sample_rate=None,  # deprecated, only kept for backwards compatibility
        gate_time=None,
        trigger_source=None,
        back_to_back=True,
    ):
        """
        Record a time series to the buffer and read it out after completion.

        :param channel: Channel that should be used
        :param n_samples: The number of samples
        :param gate_time: Gate time in s
        :param trigger_source: Optionally specify a trigger source to start the measurement
        :param back_to_back: If True, the buffer measurement is performed back-to-back.
        :param sample_rate: Sample rate in Hz

           .. deprecated:: 0.14
              Use parameter `gate_time` instead.
        """
        if (gate_time is None) and (sample_rate is None):
            raise ValueError("`gate_time` must be specified.")
        if sample_rate is not None:
            warn("`sample_rate` is deprecated, use `gate_time` instead.", FutureWarning)
            if gate_time is not None:
                raise ValueError("Only one of `gate_time` and `sample_rate` can be specified.")
            gate_time = 1 / sample_rate
        self.clear()
        self.format = "ASCII"
        self.configure_frequency_array_measurement(n_samples, channel, back_to_back=back_to_back)
        self.continuous = False
        self.gate_time = gate_time

        if trigger_source:
            self.external_start_arming_source = trigger_source

        # start the measurement (or wait for trigger)
        self.write(":INIT")
