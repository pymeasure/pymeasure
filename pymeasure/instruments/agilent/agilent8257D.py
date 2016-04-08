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

from pymeasure.instruments import Instrument, RangeException


class Agilent8257D(Instrument):
    """Interface for the Agilent 8257D signal generator
    """

    def __init__(self, resourceName, delay=0.02, **kwargs):
        super(Agilent8257D, self).__init__(
            resourceName,
            "Agilent 8257D RF Signal Generator",
            **kwargs
        )

        self.add_control("power",     ":pow?",  ":pow %g dbm;")
        self.add_control("frequency", ":freq?", ":freq %g Hz;")
        self.add_control("center_frequency", ":SOUR:FREQ:CENT?", ":SOUR:FREQ:CENT %e HZ")
        self.add_control("start_frequency", ":SOUR:FREQ:STAR?", ":SOUR:FREQ:STAR %e HZ")
        self.add_control("stop_frequency", ":SOUR:FREQ:STOP?", ":SOUR:FREQ:STOP %e HZ")
        self.add_control("start_power", ":SOUR:POW:STAR?", ":SOUR:POW:STAR %e DBM")
        self.add_control("stop_power", ":SOUR:POW:STOP?", ":SOUR:POW:STOP %e DBM")
        self.add_control("dwell_time", ":SOUR:SWE:DWEL1?", ":SOUR:SWE:DWEL1 %.3f")
        self.add_measurement("step_points", ":SOUR:SWE:POIN?")

    @property
    def output(self):
        return int(self.ask(":output?")) == 1

    @output.setter
    def output(self, value):
        if value:
            self.write(":output on;")
        else:
            self.write(":output off;")

    def enable(self):
        self.output = True

    def disable(self):
        self.output = False

    @property
    def modulation(self):
        return True if int(self.ask(":output:mod?")) == 1 else False

    @modulation.setter
    def modulation(self, value):
        if value:
            self.write(":output:mod on;")
            self.write(":lfo:sour int; :lfo:ampl 2.0vp; :lfo:stat on;")
        else:
            self.write(":output:mod off;")
            self.write(":lfo:stat off;")

    def configure_modulation(self, freq=10.0e9, modType="amplitude",
                             modDepth=100.0):
        if modType == "amplitude":
            # self.write(":AM1;")
            self.modulation = True
            self.write(":AM:SOUR INT; :AM:INT:FUNC:SHAP SINE; :AM:STAT ON;")
            self.write(":AM:INT:FREQ %g HZ; :AM %f" % (freq, modDepth))
        elif modType == "pulse":
            # Sets square pulse modulation at the desired freq
            self.modulation = True
            self.write(":PULM:SOUR:INT SQU; :PULM:SOUR INT; :PULM:STAT ON;")
            self.write(":PULM:INT:FREQ %g HZ;" % freq)
        else:
            raise Exception("This type of modulation does not exist.")

    def set_amplitude_depth(self, depth):
        """ Sets the depth of amplitude modulation which corresponds
        to the precentage of the signal modulated to
        """
        if depth > 0 and depth <= 100:
            self.write(":SOUR:AM %d" % depth)
        else:
            raise RangeException("Agilent E8257D amplitude modulation"
                                 " out of range")

    def set_amplitude_source(self, source='INT'):
        """ Sets the source of the trigger for amplitude modulation """
        self.write(":SOUR:AM:SOUR %s" % source)

    def set_amplitude_modulation(self, enable=True):
        """ Enables (True) or disables (False) the amplitude modulation """
        self.write(":SOUR:AM:STAT %d" % enable)

    def set_step_sweep(self):
        """ Sets up for a step sweep through frequency """
        self.write(":SOUR:FREQ:MODE SWE;"
                   ":SOUR:SWE:GEN STEP;"
                   ":SOUR:SWE:MODE AUTO;")

    def set_retrace(self, enable=True):
        self.write(":SOUR:LIST:RETR %d" % enable)

    def single_sweep(self):
        self.write(":SOUR:TSW")

    def start_step_sweep(self):
        """ Initiates a step sweep """
        self.write(":SOUR:SWE:CONT:STAT ON")

    def stop_step_sweep(self):
        """ Stops a step sweep """
        self.write(":SOUR:SWE:CONT:STAT OFF")

    def shutdown(self):
        self.modulation = False
        self.output = False
