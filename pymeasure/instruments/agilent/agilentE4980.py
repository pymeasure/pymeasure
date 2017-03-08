# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 13:04:42 2017

@author: DSpirito

LCR meter E4980AL
"""

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
    #TODO: check behaviour with lists
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
        # gets 4-ples of numbers
        zetas = [measured[_] for _ in range(0, len(aa), 4)]
        thetas = [measured[_] for _ in range(1, len(aa), 4)]
        return zetas, thetas
    
    #TODO: maybe refactor as property?
    def aperture(self,time=None, averages=1):
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
                print("Aperture is: "+self.ask(":APER?"))
