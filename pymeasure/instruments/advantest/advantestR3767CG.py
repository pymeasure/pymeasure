#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set, strict_range


class AdvantestR3767CG(Instrument):
    """ Represents the Advantest R3767CG VNA. Implements controls to change the analysis
    	range and to retreve the data for the trace. 
    """

    id = Instrument.measurement(
    	"*IDN?", """ Reads the instrument identification """
    )

    center_frequency = Instrument.control(
    	":FREQ:CENT?", ":FREQ:CENT %d",
        """Center Frequency in Hz""",
        validator=strict_range,
        values=[300000, 8000000000]
    )

    span_frequency = Instrument.control(
    	":FREQ:SPAN?", ":FREQ:SPAN %d",
        """Span Frequency in Hz""",
        validator=strict_range,
        values=[1, 8000000000]
    )

    start_frequency = Instrument.control(
        ":FREQ:STAR?", ":FREQ:STAR %d", 
        """ Starting frequency in Hz """,
        validator=strict_range,
        values=[1, 8000000000]
    )

    stop_frequency  = Instrument.control(
        ":FREQ:STOP?",":FREQ:STOP %d", 
        """ Stoping frequency in Hz """,
        validator=strict_range,
        values=[1, 8000000000]
    )

    trace_1 = Instrument.measurement(
        "TRAC:DATA? FDAT1", """ Reads the Data array from trace 1 after formatting """
    )

    def __init__(self, resourceName, **kwargs):
        super(AdvantestR3767CG, self).__init__(
            resourceName,
            "Advantest R3767CG",
            **kwargs
        )

        # Tell unit to operate in IEEE488.2-1987 command mode.
        self.write("OLDC OFF") 
