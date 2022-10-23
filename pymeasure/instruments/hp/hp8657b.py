#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HP8657B(Instrument):
    """ Represents the Hewlett Packard 8657B signal generator
    and provides a high-level interface for interacting
    with the instrument.

    *Note:* this instrument is a listen only instrument, so no readings can be get from the
    instrument

    """

    def __init__(self, adapter, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            "Hewlett-Packard HP8657B",
            **kwargs,
        )
    # TODO: Fixit
    # def check_errors(self):
    #     """
    #     Method to read the error status register

    #     :return error_status: one byte with the error status register content
    #     :rtype error_status: int
    #     """
    #     # Read the error status reigster only one time for this method, as
    #     # the manual states that reading the error status register also clears it.
    #     current_errors = int(self.ask("ERR?"))
    #     if current_errors != 0:
    #         log.error("HP6632 Error detected: %s", self.ERRORS(current_errors))
    #     return self.ERRORS(current_errors)

    def clear(self):
        """
        Resets the instrument to power-on default settings

        """
        self.adapter.connection.clear()

    # TODO: FIXIT
    # id = Instrument.measurement(
    #     "ID?",
    #     """
    #     Reads the ID of the instrument and returns this value for now

    #     """,
    # )

    amplitude = Instrument.setting(
        "AP%gDM",
        """
        A floating point property that sets the output amplitude in dBm.

        *Note:* At the moment only amplitudes in dBm are accepted

        """,
        validator=strict_range,
        values=[-143.5, 17.0],
    )

    amplitude_offset = Instrument.setting(
        "AO%gDB",
        """
        A floating point property that sets the output amplitude in dBm.

        """,
        validator=strict_range,
        values=[-100, 100.0],
    )

    frequency = Instrument.setting(
        "FR%gHZ",
        """
        A bool property which controls if the OCP (OverCurrent Protection) is enabled
        """,
        validator=strict_range,
        values=[100E5, 2.060E9],
    )

    output_enabled = Instrument.setting(
        "R%d",
        """
        A bool property which controls if the outputis enabled
        """,
        validator=strict_discrete_set,
        values={False: 2, True: 3},
        map_values=True
    )
