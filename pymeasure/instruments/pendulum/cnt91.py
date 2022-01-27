#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
    truncated_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# Programmer's guide 8-92, defined outside of the class, since it is used by
# `Instrument.control` without access to `self`.
MAX_MEASUREMENT_TIME = 1000


class CNT91(Instrument):
    """Represents a Pendulum CNT-91 frequency counter."""

    CHANNELS = {"A": 1, "B": 2, "C": 3, "E": 4, "INTREF": 6}
    MAX_BUFFER_SIZE = 32000  # User Manual 8-38

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('timeout', 120000)
        kwargs.setdefault('read_termination', '\n')
        super().__init__(
            resourceName,
            "Pendulum CNT-91",
            **kwargs,
        )

    @property
    def batch_size(self):
        """Maximum number of buffer entries that can be transmitted at once."""
        if not hasattr(self, "_batch_size"):
            self._batch_size = int(self.ask("FORM:SMAX?"))
        return self._batch_size

    def read_buffer(self, expected_length=0):
        """
        Read out the entire buffer.

        :param expected_length: The expected length of the buffer. If more
            data is read, values at the end are removed. Defaults to 0,
            which means that the entire buffer is returned independent of its
            length.
        :return: Frequency values from the buffer.
        """
        while not self.complete:
            # Wait until the buffer is filled.
            sleep(0.01)
        data = []
        # Loop until the buffer is completely read out.
        while True:
            # Get maximum number of buffer values.
            new = self.values(":FETC:ARR? MAX")
            data += new
            # Last values have been read from buffer.
            if len(new) < self.batch_size:
                # Remove the last values if the buffer is too long.
                if expected_length and len(data) > expected_length:
                    data = data[:expected_length]
                    log.info("Buffer was too long, truncated.")
                break
        return data

    external_start_arming_source = Instrument.control(
        "ARM:SOUR?",
        "ARM:SOUR %s",
        """
        Select arming input or switch off the start arming function.
        Options are 'A', 'B' and 'E' (rear). 'IMM' turns trigger off.
        """,
        validator=strict_discrete_set,
        values={"A": "EXT1", "B": "EXT2", "E": "EXT4", "IMM": "IMM"},
        map_values=True,
    )

    external_arming_start_slope = Instrument.control(
        "ARM:SLOP?",
        "ARM:SLOP %s",
        "Set slope for the start arming condition.",
        validator=strict_discrete_set,
        values=["POS", "NEG"],
    )

    continuous = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %s",
        "Controls whether to perform continuous measurements.",
        strict_discrete_set,
        values={True: 1.0, False: 0.0},
        map_values=True,
    )

    measurement_time = Instrument.control(
        ":ACQ:APER?",
        ":ACQ:APER %f",
        "Gate time for one measurement in s.",
        validator=strict_range,
        values=[2e-9, MAX_MEASUREMENT_TIME],  # Programmer's guide 8-92
    )

    format = Instrument.control(
        "FORM?",
        "FORM %s",
        "Reponse format (ASCII or REAL).",
        validator=strict_discrete_set,
        values=["ASCII", "REAL"],
    )

    interpolator_autocalibrated = Instrument.control(
        ":CAL:INT:AUTO?",
        "CAL:INT:AUTO %s",
        "Controls if interpolators should be calibrated automatically.",
        strict_discrete_set,
        values={True: 1.0, False: 0.0},
        map_values=True,
    )

    def configure_frequency_array_measurement(self, n_samples, channel):
        """
        Configure the counter for an array of measurements.

        :param n_samples: The number of samples
        :param channel: Measurment channel (A, B, C, E, INTREF)
        """
        n_samples = truncated_range(n_samples, [1, self.MAX_BUFFER_SIZE])
        channel = strict_discrete_set(channel, self.CHANNELS)
        channel = self.CHANNELS[channel]
        self.write(f":CONF:ARR:FREQ {n_samples},(@{channel})")

    def buffer_frequency_time_series(
        self, channel, n_samples, sample_rate, trigger_source=None
    ):
        """
        Record a time series to the buffer and read it out after completion.

        :param channel: Channel that should be used
        :param n_samples: The number of samples
        :param sample_rate: Sample rate in Hz
        :param trigger_source: Optionally specify a trigger source to start the
            measurement
        """
        if self.interpolator_autocalibrated:
            max_sample_rate = 125e3
        else:
            max_sample_rate = 250e3
        # Minimum sample rate is 1 sample in the maximum measurement time.
        sample_rate = strict_range(
            sample_rate, [1 / MAX_MEASUREMENT_TIME, max_sample_rate]
        )
        measurement_time = 1 / sample_rate

        self.clear()
        self.format = "ASCII"
        self.configure_frequency_array_measurement(n_samples, channel)
        self.continuous = False
        self.measurement_time = measurement_time

        if trigger_source:
            self.external_start_arming_source = trigger_source

        # start the measurement (or wait for trigger)
        self.write(":INIT")
