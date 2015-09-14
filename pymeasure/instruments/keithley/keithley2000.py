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

from pymeasure.instruments.instrument import Instrument

import logging


class Keithley2000(Instrument):

    def __init__(self, resourceName, name = "Keithley 2000 Multimeter", **kwargs):
        super(Keithley2000, self).__init__(
            resourceName,
            name,
            **kwargs
        )
        # Set up data transfer format
        self.adapter.config(is_binary = False,
                            datatype = 'float32',
                            converter = 'f',
                            separator = ',')
        self.add_measurement("measure", ":read?", 
                            checkErrorsOnGet = True, 
                            docs = "Measure and return a reading from the instrument.")
        # Clear any residual status bytes.
        self.clear()

        # The below properties are kept for compatibility with previous versions
        self.add_measurement("voltage", ":read?")
        self.add_measurement("resistance", ":read?")
        
    def check_errors(self):
        """ Read all errors from the instrument."""
        while True:
            err = self.adapter.ascii_values(":system:error?", 
                                    converter = 's', 
                                    separator = ',')
            if int(err[0]) != 0:
                logging.info("Keithley Encountered error: %s: %s\n" % (err[0],err[1]))
            else:
                break

    def set_config(self, config, Range = 0, nplc = 2, bandwidth = 1000):
        """ Set configuration.
        
        :param config: String describing the function, such as 'VAC', 'R4W', etc.
        :param Range: Maximum limit of reading, default = 0 (auto range).
        """
        config = config.upper()
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
        self.set_range(Range)
        self.set_nplc(nplc)
        if config.find('AC') > -1:
            self.set_bandwidth(bandwidth)

    def get_config(self):
        """ Return the current configuration. """
        return self.adapter.ask(":CONFigure?").strip()[1:-1]

    def set_range(self, maxvalue):
        """ Set range to accommodate maxvalue.
        
        auto range ON if maxvalue = 0
        """
        config = self.get_config()
        if maxvalue != 0:
            self.write(":%s:RANGe %g" % (config, maxvalue))
        else:
            self.write(":%s:RANGe:AUTO ON" % config)
    
    def get_range(self):
        """ Get the maximum limit of current configuration. """
        config = self.get_config()
        return self.values(":%s:RANGe:UPPer?" % config)

    def set_nplc(self, nplc):
        if nplc >= 0.01 and nplc <= 10:
            config = self.get_config()
            self.write(":%s:nplcycles %g" %(config, nplc))
        else:
            logging.error("Error: nplc must be in 0.01 - 10.")

    def set_reference(self, RefValue):
        """ Set reference value for output.
        No reference if RefValue is 0
        """
        config = self.get_config()
        if RefValue == 0:
            # No reference
            self.write(":%s:REFerence:STATe OFF" % config)
        else:
            self.write(":%s:REFerence:STATe ON" % config)
            self.write(":%s:REFerence %g" %(config, RefValue))

    def set_average(self, count, method = "REPeat"):
        """ Make multiple readings and output the average
        
        :param count: number of repeats, 1 - 100 \n
            if count = 1, average is OFF \n
        :param method: either "REPeat" (default) or "MOVing"
        """
        config = self.get_config()
        if count <= 1:
            # No averaging
            self.write(":%s:AVERage:STATe OFF" %config)
        elif count > 100:
            print "Error: number of repeats must be <= 100."
        else:
            self.write(":%s:AVERage:STATe ON" %config)
            self.write(":%s:AVERage:TCONtrol %s" %(config, method))
            self.write(":%s:AVERage:COUNt %g" %(config, count))

    def set_bandwidth(self, bandwidth):
        """ Set bandwidth for AC measurement. """
        config = self.get_config()
        # Check for AC mode
        if config.find('AC') > -1:
            self.write(":%s:DETector:BANDwidth %g" %(config, bandwidth))
            
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
