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

from pymeasure.instruments import Instrument


class S200(Instrument):
    """ Represents the Wenthworth Labs S200 Probe Table
    and provides a high-level for interacting with the instrument
    """

    def __init__(self,
                 adapter,
                 name="Wentworth Labs S200 Probe Table",
                 query_delay=0.1,
                 write_delay=0.1,
                 timeout=5000,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            write_termination="\n",
            read_termination="",
            send_end=True,
            includeSCPI=True,
            timeout=timeout,
            **kwargs
        )

    chuck_lift = Instrument.control(
        "STA", "%r",
        "Control chuck lift of the probe station",
        validator=[True, False],
        values={True: 'CUP', False: 'CDW'},
        map_values=True,
        get_process=lambda r:
        r
    )

    x_position = Instrument.control(
        "PSX", "GTS X, %d",
        "Control the x-axis position in microns",
        validator=None,
        get_process=lambda r:
        int(r.replace("PSX_",""))
    )

    y_position = Instrument.control(
        "PSY", "GTS Y, %d",
        "Control the y-axis position in microns",
        validator=None,
        get_process=lambda r:
        int(r.replace("PSY_",""))
    )

    status_byte = Instrument.measurement(
        "STA",
        "Measures the status byte of the instrument",
        get_process=lambda r:
        r
    )

    extended_status_info = Instrument.measurement(
        "STP",
        "Measures the extended status information of the instrument",
        get_process=lambda r:
        r
    )

