"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""
import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument


class Keithley2000(Instrument):

    def __init__(self, resourceName, **kwargs):
        super(Keithley2000, self).__init__(
            resourceName,
            "Keithley 2000 Multimeter",
            **kwargs
        )
        self.add_measurement("voltage", ":read?")
        self.add_measurement("resistance", ":read?")

    def check_errors(self):
        errors = map(int, self.values(":system:error?"))
        for err in errors:
            if err != 0:
                log.info("Keithley Encountered error: %d\n" % err)

    def config_measure_resistance(self, wires=2, nplc=2):
        if (wires == 2):
            self.write(":configure:resistance")
            self.write(":resistance:nplcycles %g" % nplc)
        elif (wires == 4):
            self.write(":configure:fresistance")
            self.write(":fresistance:nplcycles %g" % nplc)
        else:
            raise Exception("Incorrect measurement type specified")

    def config_measure_voltage(self, voltage_range=0.5, nplc=2):
            self.write(":configure:voltage")
            self.write(":voltage:nplcycles %g" % nplc)
            self.write(":voltage:range %g" % voltage_range)
