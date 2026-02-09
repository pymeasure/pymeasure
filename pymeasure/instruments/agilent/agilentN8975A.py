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

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set


class AgilentN8975AFrequency(Channel):
    """A class representing the frequency subsystem of the Noise Figure Analyzer."""

    start = Channel.control(
        "FREQ:STAR?",
        "FREQ:STAR %f",
        """Control the start frequency in Hz for the sweep frequency :attr:`mode`
        (float, strictly from ``10e6`` to ``26.4999e9``).""",
        validator=strict_range,
        values=[10e6, 26.4999e9],
        )

    stop = Channel.control(
        "FREQ:STOP?",
        "FREQ:STOP %f",
        """Control the stop frequency in Hz for the sweep frequency :attr:`mode`
        (float, strictly from ``10.1e6`` to ``26.5e9``).""",
        validator=strict_range,
        values=[10.1e6, 26.5e9],
        )

    mode = Channel.control(
        "FREQ:MODE?",
        "FREQ:MODE %s",
        """Control the method by which measurement frequencies are generated
        (str, strictly ``sweep``, ``fixed`` or ``list``).

        - ``sweep``: frequency values are generated from the :attr:`start`, :attr:`stop`
          and :attr:`number_of_points` parameters
        - ``fixed``: the :attr:`fixed_value` frequency is used
        - ``list``: frequencies are taken from :attr:`list_data`

        """,
        map_values=True,
        values={"sweep": "SWE",
                "fixed": "FIX",
                "list": "LIST",
                },
        )

    fixed_value = Channel.control(
        "FREQ:FIX?",
        "FREQ:FIX %f",
        """Control the frequency in Hz in the fixed frequency :attr:`mode`
        (float, strictly from ``10e6`` to ``26.5e9``).""",
        validator=strict_range,
        values=[10e6, 26.5e9],
        )

    list_data = Channel.control(
        "FREQ:LIST:DATA?",
        "FREQ:LIST:DATA %s",
        """Control the frequencies in Hz for the list frequency :attr:`mode` (list of float).""",
        set_process=lambda v: ','.join(map(str, v)),
        preprocess_reply=lambda v: v.strip("\x00"),
        )

    number_of_entries = Channel.measurement(
        "FREQ:LIST:COUN?",
        """Get the number of entries in the list frequency :attr:`mode` (int).""",
        cast=int,
        )

    number_of_points = Instrument.control(
        "SWE:POIN?",
        "SWE:POIN %d",
        """Control the number of points for the sweep frequency :attr:`mode`
        (int, strictly from ``2`` to ``401``).""",
        validator=strict_range,
        values=[2, 401],
        cast=int,
        )


class AgilentN8975A(SCPIMixin, Instrument):
    """
    A class representing the Agilent N8975A Noise Figure Analyzer.

    .. code-block:: python

        nfa = AgilentN8975A("GPIB0::16::INSTR")
        nfa.adapter.connection.timeout = 30000  # set a new timeout to 30 sec
        nfa.abort()  # abort all running measurements
        nfa.single()  # perform a single sweep measurement
        nfa.complete
        noise_figure = nfa.noise_figure_db  # get the noise figure data
        gain = nfa.gain_db  # get the gain data

    """

    frequency = Instrument.ChannelCreator(AgilentN8975AFrequency)

    def __init__(self, adapter,
                 name="Agilent N8975A",
                 timeout=5000,
                 **kwargs):
        super().__init__(adapter, name,
                         timeout=timeout,
                         **kwargs
                         )

    def abort(self):
        """Stop any current measurement."""
        self.write("ABOR")

    def calibrate(self):
        """Initiate a user calibration."""
        self.write("CORR:COLL STAN")

    def initiate(self):
        """Trigger a measurement."""
        self.write("INIT:IMM")

    def single(self):
        """Perform a single sweep."""
        self.continuous_mode_enabled = False
        self.abort()
        self.initiate()
        self.complete

    average = Instrument.control(
        "AVER:COUN?",
        "AVER:COUN %d",
        """Control the number of averaging samples (int, strictly from ``1`` to ``999``)""",
        validator=strict_range,
        values=[1, 999],
        get_process=lambda v: int(float(v)),  # NFA returns e.g. '+1.00000000E+000'.
                                              # This cannot be casted to int ditectly.
        )

    average_enabled = Instrument.control(
        "AVER?",
        "AVER %d",
        """Control whether averaging is enabled or not (bool).""",
        validator=strict_range,
        values={False: 0, True: 1}
        )

    bandwidth = Instrument.control(
        "BAND?",
        "BAND %f",
        """Control the measurement bandwidth in Hz (float, strictly ``100e3``, ``200e3``,
        ``400e3``, ``1e6``, ``2e6`` or ``4e6``).""",
        validator=strict_discrete_set,
        values=[100e3, 200e3, 400e3, 1e6, 2e6, 4e6]
        )

    continuous_mode_enabled = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %d",
        """Control whether the continuous sweep mode is enabled or not (bool).""",
        map_values=True,
        values={False: 0, True: 1}
        )

    @property
    def gain(self):
        """Get the corrected gain data in dB (list of float)."""
        _type = "ARRAY"
        if self.frequency.mode == "fixed":
            _type = "SCALAR"
        return self.values(f"FETCH:{_type}:DATA:CORR:GAIN? DB",
                           preprocess_reply=lambda v: v.strip("\x00")
                           )

    @property
    def noise_figure(self):
        """Get the corrected noise figure data in dB (list of float)."""
        _type = "ARRAY"
        if self.frequency.mode == "fixed":
            _type = "SCALAR"
        return self.values(f"FETCH:{_type}:DATA:CORR:NFIG? DB",
                           preprocess_reply=lambda v: v.strip("\x00")
                           )
