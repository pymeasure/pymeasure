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
    """Represents the Agilent 8257D Signal Generator and 
    provides a high-level interface for interacting with 
    the instrument.
    """

    power = Instrument.control(
        ":POW?;", ":POW %g dBm;",
        """ A floating point property that represents the output power
        in dBm. This property can be set.
        """
    )
    frequency = Instrument.control(
        ":FREQ?;", ":FREQ %e Hz;",
        """ A floating point property that represents the output frequency
        in Hz. This property can be set.
        """
    )
    start_frequency = Instrument.control(
        ":SOUR:FREQ:STAR?", ":SOUR:FREQ:STAR %e Hz",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """
    )
    center_frequency = Instrument.control(
        ":SOUR:FREQ:CENT?", ":SOUR:FREQ:CENT %e Hz;",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """
    )
    stop_frequency = Instrument.control(
        ":SOUR:FREQ:STOP?", ":SOUR:FREQ:STOP %e Hz",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """
    )
    start_power = Instrument.control(
        ":SOUR:POW:STAR?", ":SOUR:POW:STAR %e dBm",
        """ A floating point property that represents the start power
        in dBm. This property can be set.
        """
    )
    start_power = Instrument.control(
        ":SOUR:POW:STOP?", ":SOUR:POW:STOP %e dBm",
        """ A floating point property that represents the stop power
        in dBm. This property can be set.
        """
    )
    dwell_time = Instrument.control(
        ":SOUR:SWE:DWEL1?", ":SOUR:SWE:DWEL1 %.3f",
        """ A floating point property that represents the settling time
        in seconds at the current frequency or power setting. 
        This property can be set.
        """
    )
    step_points = Instrument.control(
        ":SOUR:SWE:POIN?", ":SOUR:SWE:POIN %d",
        """ An integer number of points in a step sweep. This property
        can be set.
        """
    )

    def __init__(self, resourceName, delay=0.02, **kwargs):
        super(Agilent8257D, self).__init__(
            resourceName,
            "Agilent 8257D RF Signal Generator",
            **kwargs
        )

    def get_output(self):
        """ Return if the output is ON"""
        return int(self.ask(":output?")) == 1

    def set_output(self, value):
        """ Set output ON/OFF"""
        if value:
            self.write(":output on;")
        else:
            self.write(":output off;")
            
    output = property(get_output, set_output)
    
    def enable(self):
        """ Set output = ON"""
        self.output = True

    def disable(self):
        """ Set output = OFF"""
        self.output = False

    def get_modulation(self):
        """ Return if modulation is ON"""
        return True if int(self.ask(":output:mod?")) == 1 else False

    def set_modulation(self, value):
        """ Set modulation ON/OFF"""
        if value:
            self.write(":output:mod on;")
            self.write(":lfo:sour int; :lfo:ampl 2.0vp; :lfo:stat on;")
        else:
            self.write(":output:mod off;")
            self.write(":lfo:stat off;")

    modulation = property(get_modulation, set_modulation)
    
    def configure_modulation(self, freq=10.0e9, modType="amplitude",
                             modDepth=100.0):
        """ Configure modulation and turn modulation ON
        
        :param freq: Modulation frequency, Hz
        :param modType: 'amplitude' or 'pulse'
        :param modDepth: AM modulation magnitude in percentage
        """
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
