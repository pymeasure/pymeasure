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

    # List of modulation sources (Not yet included are DC FM)
    modulations = {"External": "S1",
                   "Int_400Hz": "S2",
                   "Int_1000Hz": "S3",
                   "OFF": "S4"}

    def AM(self, source,  depth=0):
        """
        This function sets the AM modulation feature, supported values for the source are:

       ==========  =======
       Value       Meaning
       ==========  =======
       OFF         no modulation active
       Int_400Hz   internal 400 Hz modulation source
       Int_1000Hz  internal 1000 Hz modulation source
       External    External source
       ==========  =======

        depth is the moduledation depth in percent

        *Note:*
            * AM & FM can be active at the same time
            * only one internal source can be active at the time

        """
        strict_range(depth, [0, 100])

        if source in self.modulations:
            self.write(f"AM {self.modulations[source]} {depth} PC")

    def FM(self, source,  deviation=0):
        """
        This function sets the FM modulation feature, supported values for the source are:

        ==========  =======
        Value       Meaning
        ==========  =======
        OFF         no modulation active
        Int_400Hz   internal 400 Hz modulation source
        Int_1000Hz  internal 1000 Hz modulation source
        External    External source
        ==========  =======

        deviation is the peak deviation value in kHz.

        *Note:*
            * AM & FM can be active at the same time
            * only one internal source can be active at the time

        """
        strict_range(deviation, [0, 400])
        if source in self.modulations:
            self.write(f"FM {self.modulations[source]} {deviation} KZ")

    frequency = Instrument.setting(
        "FR %9.0f HZ",
        """
        controls the output frequency of the instrument in Hz.
        For the 8567B the valid range is 100 kHz to 2060 MHz.

        """,
        validator=strict_range,
        values=[1.0E5, 2.060E9],
        )

    level = Instrument.setting(
        "AP%gDM",
        """
        sets the output level in dBm.

        """,
        validator=strict_range,
        values=[-143.5, 17.0],
        )

    level_offset = Instrument.setting(
        "AO%gDB",
        """
        sets the output offset in dB.

        """,
        validator=strict_range,
        values=[-100, 100.0],
        )

    output_enabled = Instrument.setting(
        "R%d",
        """
        controls if the output is enabled
        """,
        validator=strict_discrete_set,
        values={False: 2, True: 3},
        map_values=True
       )
