#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set,\
    strict_range

from pymeasure.adapters import VISAAdapter


class Microtest8761(Instrument):
    """ Represents the microtest 8761 cable harness tester
    interface for interacting with the instrument.

    It can also be used for microtest 8740 8751 and 8700
    
    .. code-block:: python
        generator = Microtest8761("ASRLCOM8::INSTR")    #connect to instrument

        generator.testitem_conductance = 'ON'           #set test item: conductance
        generator.conductance_high = 10                 #set upper limit of conductance as 10 ohm
        generator.conductance_low = 1                   #set lower limit of conductance as 1 ohm

        data = generator.test()                         #begin test and return test data
    """

    testitem_conductance = Instrument.control(
        ":CONF:TESTITM:COND?", ":CONF:TESTITM:COND %f",
        """ A boolean property that set test item: conductance test.
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, 'on': 1, 'ON': 1, False: 0, 'off': 0, 'OFF': 0},
    )

    ##############################
    # Conductance Test #
    ##############################
    conductance_high = Instrument.control(
        ":CONF:COND:HILMT?", ":CONF:COND:HILMT %f",
        """ A floating property that controls the upper limit conductance 
        of the cable in ohm, from 0.001 ohm to 52 ohm (for microter 8761, 
        other version maybe different). Can be set. """,
        validator=strict_range,
        values=[0.001, 52],
    )

    conductance_low = Instrument.control(
        ":CONF:COND:HILMT?", ":CONF:COND:HILMT %f",
        """ A floating property that controls the upper limit conductance 
        of the cable in ohm, from 0.001 ohm to 52 ohm (for microter 8761,
        oter version maybe different). Can be set. """,
        validator=strict_range,
        values=[0.001, 52],
    )


    def test(self):
        """ Read Conductance data.
        """
        self.write(":KEY TEST")
        self.read()

    def info(self):
        """ Dsiplay system information.
        """
        self.write(":SYSTEM :INFO X1")

    def __init__(self, adapter, **kwargs):
        super(Microtest8761, self).__init__(
            adapter, "Microtest 8761 cable harness tester", **kwargs
        )