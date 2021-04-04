# -*- coding: utf-8 -*-
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set


class HP3478A(Instrument):
    """ Represents the Hewlett Packard 3748A 5 1/2 digit multimeter
    and provides a high-level interface for interacting
    with the instrument.
    
    As this unit predates SCIP some tricks are required to get this working
    """
    DIGITS=['n/a','5 digits','4 digits','3 digits']
    
    MODES=['n/a','DC Volts','AC volts','Ohms (2-wire)','Ohms (4-wire)',
           'DC current','AC current','Extended Ohms']
    
    RANGES=[['n/a'],
                ['n/a','30 mV DC','300 mV DC','3 V DC','30 V DC','300 V DC'],
                ['n/a','300 mV AC','3 V AC','30 V AC','300 V AC'],
                ['n/a', '30 Ohm', '300 Ohm', '3 kOhm', '30 kOhm', '300 kOhm', 
                 '3 MOhm','30 MOhm'],
                ['n/a', '30 Ohm', '300 Ohm', '3 kOhm', '30 kOhm', '300 kOhm', 
                 '3 MOhm','30 MOhm'],
                ['n/a','300 mA DC','3 A DC'],
                ['n/a','300 mA AC','3 A AC'],
                ['n/a','extended Ohms']]
    
    def __init__(self, resourceName, **kwargs):
        super(HP3478A, self).__init__(
            resourceName,
            "Hewlett-Packard HP3478A",
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            **kwargs
        )
