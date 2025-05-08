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
from enum import IntEnum
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class HP8657B(Instrument):
    """ Represents the Hewlett Packard 8657B signal generator
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, adapter, name="Hewlett-Packard HP8657B", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    class Modulation(IntEnum):
        """
        IntEnum for the different modulation sources
        """
        EXTERNAL = 1
        INT_400HZ = 2
        INT_1000HZ = 3
        OFF = 4
        DC_FM = 5

    def check_errors(self):
        """
        Method to read the error status register
        as the 8657B does not support any readout of values, this will return 0 and log a warning

        """
        log.warning("HP8657B Does not support error status readout")

    def clear(self):
        """
        Reset the instrument to power-on default settings

        """
        self.adapter.connection.clear()

    id = "HP,8657B,N/A,N/A"  #: Manual ID entry

    am_depth = Instrument.setting(
        "AM %2.1f PC",
        """
        Set the modulation depth for AM,
        usable range 0-99.9%
        """,
        validator=strict_range,
        values=[0, 99.9],
        )

    am_source = Instrument.setting(
        "AM S%i",
        """
        Set the source for the AM function with :attr:`Modulation` enumeration.

        ==========  =======
        Value       Meaning
        ==========  =======
        OFF         no modulation active
        INT_400HZ   internal 400 Hz modulation source
        INT_1000HZ  internal 1000 Hz modulation source
        EXTERNAL    External source, AC coupling
        ==========  =======

        *Note:*
            * AM & FM can be active at the same time
            * only one internal source can be active at the time
            * use "OFF" to deactivate AM

        usage example:

        .. code-block:: python

            sig_gen = HP8657B("GPIB::7")
            ...
            sig_gen.am_source = sig_gen.Modulation.INT_400HZ    #  Enable int. 400 Hz source for AM
            sig_gen.am_depth = 50                               #  Set AM modulation depth to 50%
            ...
            sig_gen.am_source = sig_gen.Modulation.OFF          #  Turn AM off

        """,
        validator=strict_discrete_set,
        values=Modulation,
        )

    fm_deviation = Instrument.setting(
        "FM %3.1fKZ",
        """
        Set the peak deviation in kHz for the FM function,
        useable range 0.1 - 400 kHz

        *NOTE*:
            the maximum usable deviation is depending on the output frequency, refer to the
            instrument documentation for further detail.

        """,
        validator=strict_range,
        values=[0.1, 400],
        )

    fm_source = Instrument.setting(
        "FM S%i",
        """
        Set the source for the FM function with :attr:`Modulation` enumeration.

        ==========  =======
        Value       Meaning
        ==========  =======
        OFF         no modulation active
        INT_400HZ   internal 400 Hz modulation source
        INT_1000HZ  internal 1000 Hz modulation source
        EXTERNAL    External source, AC coupling
        DC_FM       External source, DC coupling (FM only)
        ==========  =======

        *Note:*
            * AM & FM can be active at the same time
            * only one internal source can be active at the time
            * use "OFF" to deactivate FM
            * refer to the documentation rearding details on use of DC FM mode

        usage example:

        .. code-block:: python

            sig_gen = HP8657B("GPIB::7")
            ...
            sig_gen.fm_source = sig_gen.Modulation.EXTERNAL     #  Enable external source for FM
            sig_gen.fm_deviation = 15                           #  Set FM peak deviation to 15 kHz
            ...
            sig_gen.fm_source = sig_gen.Modulation.OFF          #  Turn FM off

        """,
        validator=strict_discrete_set,
        values=Modulation,
        )

    frequency = Instrument.setting(
        "FR %10.0f HZ",
        """
        Set the output frequency of the instrument in Hz.

        For the 8567B the valid range is 100 kHz to 2060 MHz.
        """,
        validator=strict_range,
        values=[1.0E5, 2.060E9],
        )

    level = Instrument.setting(
        "AP %g DM",
        """
        Set the output level in dBm.

        For the 8657B the range is -143.5 to +17 dBm/

        """,
        validator=strict_range,
        values=[-143.5, 17.0],
        )

    level_offset = Instrument.setting(
        "AO %g DB",
        """
        Set the output offset in dB, usable range -199 to +199 dB.

        """,
        validator=strict_range,
        values=[-199.0, 199.0],
        )

    output_enabled = Instrument.setting(
        "R%d",
        """
        Control whether the output is enabled.
        """,
        validator=strict_discrete_set,
        values={False: 2, True: 3},
        map_values=True
       )

    def reset(self):
        self.adapter.connection.clear()

    def shutdown(self):
        self.adapter.connection.clear()
        self.output_enabled = False
        self.adapter.connection.close()
        super().shutdown()
