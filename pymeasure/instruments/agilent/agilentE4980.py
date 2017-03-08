#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set


class AgilentE4980(Instrument):
    """Represents LCR meter E4980A/AL"""

    ac_voltage = Instrument.control(":VOLT:LEV?", ":VOLT:LEV %g",
                                    "AC voltage level",
                                    validator=truncated_range,
                                    values=[0, 20])

    frequency = Instrument.control(":FREQ:CW?", ":FREQ:CW %g",
                                   "AC frequency",
                                   validator=truncated_range,
                                   values=[20, 3e5])

    # FETCH? returns [A,B,state]: impedance returns only A,B
    # TODO: check behaviour with lists
    #
    impedance = Instrument.measurement(":FETCH?", "Measured values A and B, according to mode",
                                       get_process=lambda x: x[:2])

    mode = Instrument.control("FUNCtion:IMPedance:TYPE?", "FUNCtion:IMPedance:TYPE %s",
                              "Select quantities to be measured",
                              validator=strict_discrete_set,
                              values=["CPD", "CPQ", "CPG", "CPRP",
                                      "CSD", "CSQ", "CSRS",
                                      "LPD", "LPQ", "LPG", "LPRP",
                                      "LPRD", "LSD", "LSQ",
                                      "LSRS", "LSRD", "RX",
                                      "ZTD", "ZTR", "GB", "YTD", "YTR"])

    def __init__(self, adapter, **kwargs):
        super(AgilentE4980, self).__init__(
            adapter, "Agilent E4980A/AL LCR meter", **kwargs
        )
        self.timeout = 30000
        # format: output ascii
        self.write("FORM ASC")

    def freq_sweep(self, freq_list, delay=0):
        """
        Run frequency list sweep
        freq_list: list of frequency to be swept
        delay: trigger delay between each frequency in the list"""
        # manual, page 299
        # self.write("*RST;*CLS")
        self.write("TRIG:SOUR BUS")
        self.write("DISP:PAGE LIST")
        # use mode STEP to use trigger delay
        self.write("LIST:MODE STEP")
        self.write("TRIG:DEL %f" % delay)
        lista_str = ",".join(['%e' % f for f in freq_list])
        self.write("LIST:FREQ %s" % lista_str)
        # trigger
        self.write("INIT:CONT ON")
        self.write(":TRIG:IMM")
        measured = self.values("FETCh:IMPedance:FORMatted?")
        # gets 4-ples of numbers (?)
        zetas = [measured[_] for _ in range(0, len(measured), 4)]
        thetas = [measured[_] for _ in range(1, len(measured), 4)]
        return zetas, thetas

    # TODO: maybe refactor as property?
    def aperture(self, time=None, averages=1):
        """
        set and get aperture
        time: string, SHORT, MED, LONG (case insensitive); if None, get values
        averages: numeric
        """
        if time is None:
            return self.ask(":APER?")
        else:
            if time.upper() in ["SHORT", "MED", "LONG"]:
                self.write(":APER {0}, {1}".format(time, averages))
            else:
                print("Time must be a string: SHORT, MED, LONG")
                print("Aperture is: " + self.ask(":APER?"))
