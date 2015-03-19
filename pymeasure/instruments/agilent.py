#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Agilent classes -- RF Sweeper, Vector Network Analyzer
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.instruments import Instrument, discreteTruncate, RangeException
import numpy as np
import time, struct, re
from StringIO import StringIO

class Agilent8257D(Instrument):
    def __init__(self, resourceName, delay=0.02, **kwargs):
        super(Agilent8257D, self).__init__(resourceName,
            "Agilent 8257D RF Signal Generator", **kwargs
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
        return int(self.ask(":output?"))==1
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
        return True if int(self.ask(":output:mod?"))==1 else False 
    @modulation.setter
    def modulation(self, value):
        if value:
            self.write(":output:mod on;")
            self.write(":lfo:sour int; :lfo:ampl 2.0vp; :lfo:stat on;")
        else:
            self.write(":output:mod off;")
            self.write(":lfo:stat off;")

    def configure_modulation(self, freq=10.0e9, modType="amplitude", modDepth=100.0):
        if modType == "amplitude":
            #self.write(":AM1;")
            self.modulation = True
            self.write(":AM:SOUR INT; :AM:INT:FUNC:SHAP SINE; :AM:STAT ON;")
            self.write(":AM:INT:FREQ %g HZ; :AM %f" % (freq, modDepth))
        elif modType == "pulse":
            # Sets square pulse modulation at the desired freq
            self.modulation = True
            self.write(":PULM:SOUR:INT SQU; :PULM:SOUR INT; :PULM:STAT ON;")
            self.write(":PULM:INT:FREQ %g HZ;" % freq)
        else:
            print "This type of modulation does not exist."
        
    def setAmplitudeDepth(self, depth):
        """ Sets the depth of amplitude modulation which corresponds
        to the precentage of the signal modulated to
        """
        if depth > 0 and depth <= 100:
            self.write(":SOUR:AM %d" % depth)
        else:
            raise RangeException("Agilent E8257D amplitude modulation out of range")
            
    def setAmplitudeSource(self, source='INT'):
        """ Sets the source of the trigger for amplitude modulation """
        self.write(":SOUR:AM:SOUR %s" % source)
        
    def setAmplitudeModulation(self, enable=True):
        """ Enables (True) or disables (False) the amplitude modulation """
        self.write(":SOUR:AM:STAT %d" % enable)

    def setStepSweep(self):
        """ Sets up for a step sweep through frequency """
        self.write(":SOUR:FREQ:MODE SWE;:SOUR:SWE:GEN STEP;:SOUR:SWE:MODE AUTO;")
    
    def setRetrace(self, enable=True):
        self.write(":SOUR:LIST:RETR %d" % enable)
        
    def singleSweep(self):
        self.write(":SOUR:TSW")
        
    def startStepSweep(self):
        """ Initiates a step sweep """
        self.write(":SOUR:SWE:CONT:STAT ON")
        
    def stopStepSweep(self):
        """ Stops a step sweep """
        self.write(":SOUR:SWE:CONT:STAT OFF")

    def shutdown(self):
        self.modulation = False
        self.output = False


class Agilent8722ES(Instrument):
    """ Represents the Agilent8722ES Vector Network Analyzer
    and provides a high-level interface for taking scans of the
    scattering parameters.
    """

    SCAN_POINT_VALUES = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
    SCATTERING_PARAMETERS = ("S11", "S12", "S21", "S22")
    S11, S12, S21, S22 = SCATTERING_PARAMETERS

    def __init__(self, resourceName, **kwargs):
        super(Agilent8722ES, self).__init__(resourceName, "Agilent 8722ES Vector Network Analyzer", **kwargs)
        
        self.add_control("start_frequency", "STAR?", "STAR %.3e HZ")
        self.add_control("stop_frequency", "STOP?", "STOP %.3e HZ")
        self.add_control("sweep_time", "SWET?", "SWET%.2e")
    
    def setFixedFrequency(self, frequency):
        """ Sets the scan to be of only one frequency in Hz """
        self.setStartFrequency(frequency)
        self.setStopFrequency(frequency)
        self.setScanPoints(3)

    @property
    def parameter(self):
        for parameter in Agilent8722ES.SCATTERING_PARAMETERS:
            if int(self.values("%s?" % parameter))==1: return parameter
        return None
    @parameter.setter
    def parameter(self, value):
        if value in Agilent8722ES.SCATTERING_PARAMETERS:
            self.write("%s" % value)
        else:
            raise Exception("Invalid scattering parameter requested for Agilent 8722ES")
        
    @property
    def scan_points(self):
        """ Gets the number of scan points
        """
        search = re.search(r"\d\.\d+E[+-]\d{2}$", self.ask("POIN?"), re.MULTILINE)
        if search:
           return int(float(search.group()))
        else:
            raise Exception("Improper message returned for the number of points")
    @scan_points.setter
    def scan_points(self, points):
        """ Sets the number of scan points, truncating to an allowed
        value if not properly provided       
        """
        points = discreteTruncate(points, Agilent8722ES.SCAN_POINT_VALUES)
        if points:
            self.write("POIN%d" % points)
        else:
            raise RangeException("Maximum scan points (1601) for Agilent 8722ES"
                                 " exceeded") 
                                 
    def setIFBandwidth(self, bandwidth):
        """ Sets the resolution bandwidth (IF bandwidth) """
        allowedBandwidth = [10, 30, 100, 300, 1000, 3000, 3700, 6000]
        bandwidth = discreteTruncate(bandwidth, allowedBandwidth)
        if bandwidth:
            self.write("IFBW%d" % bandwidth)
        else:
            raise RangeException("Maximum IF bandwidth (6000) for Agilent "
                                 "8722ES exceeded")
    
    def setAveraging(self, averages):
        """ Turns on averaging of a specific number between 0 and 999        
        """
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("AVERO1")
            self.write("AVERFACT%d" % int(averages))
            
    def disableAveraging(self):
        """ Disables averaging """
        self.write("AVERO0")
        
    def isAveraging(self):
        """ Returns True if averaging is enabled """
        return self.ask("AVERO?") == '1\n'
            
    def restartAveraging(self, averages):
        if int(averages) > 999 or int(averages) < 0:
            raise RangeException("Averaging must be in the range 0 to 999")
        else:
            self.write("NUMG%d" % averages)
            
    def scan(self, averages=1, blocking=True, timeout=25, delay=0.1):
        """ Initiates a scan with the number of averages specified and
        blocks until the operation is complete if blocking is True
        """
        if averages == 1:
            self.disableAveraging()
            self.setSingleSweep()
        else:
            self.setAveraging(averages)
            self.write("*CLS;SRE 4;ESNB 1;")
            self.restartAveraging(averages)
            if blocking:
                self.adapter.wait_for_srq(timeout, delay)
    
    # TODO: Add method for determining if the scan is completed
    
    def scanSingle(self):
        """ Initiates a single scan """
        self.write("SING")
        
    def scanContinuous(self):
        """ Initiates a continuous scan """
        self.write("CONT")
    
    @property
    def frequencies(self):
        """ Returns a list of frequencies from the last scan
        """
        return np.linspace(self.start_frequency, self.stop_frequency, num=self.scan_points)
        
    @property
    def data(self):
        """ Returns the real and imaginary data from the last scan        
        """
        # TODO: Implement binary transfer instead of ASCII
        data = np.loadtxt(StringIO(self.ask("FORM4;OUTPDATA")), delimiter=',', dtype=np.float32)
        return data[:,0], data[:,1]
        
    def log_magnitude(self, real, imaginary): # dB
        return 20*np.log10(self.magnitude(real, imaginary))
    
    def magnitude(self, real, imaginary):
        return np.sqrt(real**2 + imaginary**2)
        
    def phase(self, real, imaginary): # degrees
        return np.arctan2(imaginary, real)*180/np.pi
        

