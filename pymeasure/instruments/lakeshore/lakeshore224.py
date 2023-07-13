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
from pymeasure.instruments import Instrument
from pymeasure.instruments.lakeshore.lakeshore_base import LakeShoreTemperatureChannel

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class LakeShore224(Instrument):
    """ Represents the Lakeshore 224 Temperature monitor and provides a high-level interface
    for interacting with the instrument. Note that the 224 provides 12 temperature input channels
    (A, B, C1-5, D1-5). This driver makes use of the :ref:`LakeShoreChannels`

    .. code-block:: python

        monitor = LakeShore224('GPIB::1')

        print(monitor.input_A.kelvin)           # Print the temperature in kelvin on sensor A
        monitor.input_A.wait_for_temperature()  # Wait for the temperature on sensor A to stabilize.
    """

    i_ch = Instrument.ChannelCreator(LakeShoreTemperatureChannel,
                                     ['0', 'A', 'B',
                                      'C1', 'C2', 'C3', 'C4', 'C5',
                                      'D1', 'D2', 'D3', 'D4', 'D5'],
                                     prefix='input_')

    def __init__(self, adapter, name="Lakeshore Model 224 Temperature Controller", **kwargs):
        kwargs.setdefault('read_termination', "\r\n")
        super().__init__(
            adapter,
            name,
            **kwargs
        )
