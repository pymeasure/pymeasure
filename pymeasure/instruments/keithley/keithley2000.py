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

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import Instrument


class Keithley2000(Instrument):

    measure = Instrument.control(
        "measure", ":read?",
        """ Returns a measurement reading for the configured variable. """,
        check_get_errors=True
    )
    voltage = measure # alias when measuring voltage
    resistance = measure # alias when measuring resistance

    def __init__(self, resourceName, **kwargs):
        super(Keithley2000, self).__init__(
            resourceName,
            "Keithley 2000 Multimeter",
            **kwargs
        )
        self.title = "Keithley (" + str(resourceName) + ")"
        # Set up data transfer format
        self.adapter.config(is_binary = False,
                            datatype = 'float32',
                            converter = 'f',
                            separator = ',')
                            
        # Reset the instrument.
        self.reset()
        
    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.adapter.values(":system:error?")
            if int(err[0]) != 0:
                errmsg = self.title + ": %s: %s" % (err[0],err[1])
                log.error(errmsg + '\n')
            else:
                break
            
    def get_config(self):
        """ Return the current configuration. """
        return self.ask(":CONFigure?").strip()[1:-1]

    def set_config(self, config, range = 0, nplc = 2, bandwidth = 1000):
        """ Set configuration.
        
        :param config: String describing the function, such as 'VAC', 'R4W', etc.
        :param Range: Maximum limit of reading, default = 0 (auto range).
        :param nplc: Number of power line cycles, default = 2.
        :param bandwidth: Bandwidth for AC measurement, default = 1000.
        """
        config = config.upper()
        func = self.config
        
        if config.find('V') > -1:
            func = 'VOLTage'
        if config.find('I') > -1:
            func = 'CURRrent'
        if config.find('AC') > -1:
            func = func + ':AC'
        if config.find('R') > -1:
            func = 'RESistance'
            if config.find('4') > -1:
                func = 'F' + func
        
        # Setting up
        self.write(":CONFigure:%s" % func)
        self.range = range
        self.nplc = nplc
        if config.find('AC') > -1:
            self.bandwidth = bandwidth

    # Establish a property
    config = property(get_config, set_config, "Current configuration of the instrument.")
    
    def get_range(self):
        """ Get the maximum limit of current configuration.

        :return: (Maximum limit, Auto Range status)        
        """
        return self.values(":%s:RANGe:UPPer?;AUTO?" % self.config,
                                         separator = ';')
     
    def set_range(self, maxvalue):
        """ Set range to accommodate maxvalue.
        
        auto range ON if maxvalue = 0
        """
        config = self.config
        if maxvalue != 0:
            self.write(":%s:RANGe %g" % (config, maxvalue))
        else:
            self.write(":%s:RANGe:AUTO ON" % config)

    # Establish a property
    range = property(get_range, set_range, "Maximum limit of reading.")
    
    def get_nplc(self):
        """ Return the current NPLC (number of power line cycles)."""
        return self.values(":%s:NPLCycles?" % self.config)
        
    def set_nplc(self, nplc):
        if nplc >= 0.01 and nplc <= 10:
            self.write(":%s:NPLCycles %g" %(self.config, nplc))
        else:
            errmsg = self.title + ": NPLC must be in 0.01 - 10. Do nothing."
            log.warning(errmsg + '\n')

    # Establish a property
    nplc = property(get_nplc, set_nplc, "Number of power line cycles.")
    
    def get_reference(self):
        """ Obtain the reference setting.
        
        :return: (Relative value, status ON/OFF)        
        """
        return self.values(":%s:REFerence?;REFerence:STATe?" % self.config,
                                 separator = ';')

    def set_reference(self, RefValue):
        """ Set reference value for output.
        No reference if RefValue is 0
        """
        config = self.config
        if RefValue == 0:
            # No reference
            self.write(":%s:REFerence:STATe OFF" % config)
        else:
            self.write(":%s:REFerence:STATe ON" % config)
            self.write(":%s:REFerence %g" %(config, RefValue))

    # Establish a property
    reference = property(get_reference, set_reference, "Relative value.")
    
    def get_average(self):
        """ Obtain the filter setting.
        
        :return: (number of counts, status ON/OFF, control MOVing/REPeat)
        """
        config = self.config
        return self.values(":%s:AVERage:COUNt?;STATe?" % config, 
                                separator = ';') \
            + self.values(":%s:AVERage:TCONtrol?" % config)
        
    def set_average(self, count, method = "REPeat"):
        """ Make multiple readings and output the average
        
        :param count: number of repeats, 1 - 100 \n
            if count = 1, average is OFF \n
        :param method: either "REPeat" (default) or "MOVing"
        """
        config = self.config
        if count <= 1:
            # No averaging
            self.write(":%s:AVERage:STATe OFF" %config)
        elif count > 100:
            errmsg = self.title + ": Number of counts must be <= 100. Do nothing."
            log.warning(errmsg + '\n')
        else:
            self.write(":%s:AVERage:STATe ON" %config)
            self.write(":%s:AVERage:TCONtrol %s" %(config, method))
            self.write(":%s:AVERage:COUNt %g" %(config, count))

    # Establish a property
    average = property(get_average, set_average, "Number of repeated readings.")
    
    def get_bandwidth(self):
        """ Obtain the bandwidth."""
        config = self.config
        # Check for AC mode
        if config.find('AC') > -1:
            return self.values(":%s:DETector:BANDwidth?" % self.config)
        else:
            errmsg = self.title + ": Cannot get bandwidth in DC mode."
            log.warning(errmsg + '\n')
        
        
    def set_bandwidth(self, bandwidth):
        """ Set bandwidth for AC measurement. """
        config = self.config
        # Check for AC mode
        if config.find('AC') > -1:
            self.write(":%s:DETector:BANDwidth %g" %(config, bandwidth))
        else:
            errmsg = self.title + ": Cannot set bandwidth in DC mode."
            log.warning(errmsg + '\n')

    # Establish a property
    bandwidth = property(get_bandwidth, set_bandwidth, "Bandwidth for AC measurement.")
            
    def reset(self):
        """ Reset instrument. """
        self.write("status:queue:clear;*RST;:STAT:PRES;:*CLS;")
        
    def beep(self, freq, dur):
        """ Make a beep sound
        
        :param freq: Frequency, Hz
        :param dur: Duration, seconds
        """
        self.write(":SYST:BEEP %g, %g" % (freq, dur))
    
    # The below methods are kept for compatibility with ealier versions    
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
