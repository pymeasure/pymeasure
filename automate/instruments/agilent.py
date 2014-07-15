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

class Agilent8257D(Instrument):
    def __init__(self, resourceName, delay=0.02, **kwargs):
        super(Agilent8257D, self).__init__(resourceName, 
            "Agilent 8257D RF Signal Generator",
            delay=delay, **kwargs
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

    def __init__(self, resourceName, **kwargs):
        super(Agilent8722ES, self).__init__(resourceName, "Agilent 8722ES Vector Network Analyzer", **kwargs)
    
    def setFixedFrequency(self, frequency):
        """ Sets the scan to be of only one frequency in Hz """
        self.setStartFrequency(frequency)
        self.setStopFrequency(frequency)
        self.setScanPoints(3)
        
    def setScatteringParameter(self, element):
        """" Sets which scattering parameter to be measured based on the
        matrix element notation
        """
        if element == "11": self.write("S11")
        elif element == "12": self.write("S12")
        elif element == "21": self.write("S21")
        elif element == "22": self.write("S22")
        else:
            raise Exception("Invalid matrix element provided for Agilent 8722ES"
                            " scattering parameter")
        
    def setScanPoints(self, points):
        """ Sets the number of scan points, truncating to an allowed
        value if not properly provided       
        """
        points = discreteTruncate(points, Agilent8722ES.SCAN_POINT_VALUES)
        if points:
            self.write("POIN%d" % points)
        else:
            raise RangeException("Maximum scan points (1601) for Agilent 8722ES"
                                 " exceeded")
                                 
    def getScanPoints(self):
        """ Gets the number of scan points
        """
        search = re.search(r"\d\.\d+E[+-]\d{2}$", self.ask("POIN?"), re.MULTILINE)
        if search:
           return int(float(search.group()))
        else:
            raise Exception("Improper message returned for the number of points")
                                 
    def setSweepTime(self, time):
        """ Sets the time over which the scan takes place in seconds """
        self.write("SWET%.2e" % time)
                                 
    def setStartFrequency(self, frequency):
        """ Sets the start frequency for the scan in Hz """
        self.write("STAR%.3e" % frequency)
        
    def setStopFrequency(self, frequency):
        """ Sets the stop frequency for the scan in Hz """
        self.write("STOP%.3e" % frequency)        
                                 
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
            
    def scan(self, averages=1, blocking=True, timeout=0.1, abortEvent=None):
        """ Initiates a scan with the number of averages specified and
        blocks until the operation is complete if blocking is True
        """
        if averages == 1:
            self.disableAveraging()
            self.setSingleSweep()
        else:
            self.setAveraging(averages)
            self.restartAveraging(averages)
            if blocking:
                self.waitForScan(abortEvent)
    
    def scanSingle(self):
        """ Initiates a single scan """
        self.write("SING")
        
    def scanContinuous(self):
        """ Initiates a continuous scan """
        self.write("CONT")
        
    def waitForScan(self, timeout=0.1, abortEvent=None):
        """ Blocks until the scan returns a operation complete signal
        or an abort event is set        
        """
        while not abortEvent.isSet() and self.ask("OPC?") != '1\n':
            time.sleep(timeout)
    
    def getFrequencies(self):
        """ Returns a list of frequencies from the last scan
        """
        pass
        
    def getData(self):
        """ Returns the real and imaginary data from the last scan        
        """
        data = self.ask("FORM4;OUTPDATA")[2:-2].split("\n\n  ")
        real = np.zeros(len(data), np.float64)
        imag = np.zeros(len(data), np.float64)
        for i, point in enumerate(data):
            pair = point.split(",  ", 1)
            real[i] = float(pair[0])
            imag[i] = float(pair[1])
        return real, imag
        


# TODO: update this to use properties
class DSO_X2022A(Instrument):
    def __init__(self, resourceName, **kwargs):
        super(DSO_X2022A, self).__init__(resourceName, "Agilent DSO-X 2022A", chunk_size=10000000, term_chars = "", timeout=60)

        # Storing waveform info, one dictionary per channel
        self.channel1WaveformInfo = {}
        self.channel2WaveformInfo = {}

        # Caching waveform characteristics of both channels
        self.cached1 = False
        self.cached2 = False

        if 'logfunc' in kwargs:
            self.logfunc = kwargs['logfunc']
        # else:
        #     self.logfunc = print

    def getError(self):
        return self.ask(":system:error?")

    def getErrors(self, commandName=None):
        while True:
            err = self.getError()
            if "No error" in err:
                break
            elif err == "" or err == None:
                if commandName is not None:
                    raise Exception("%s: Unexpected response to error query" % commandName)
                else:
                    raise Exception("Unexpected response to error query")
            else:
                print "Error in command %s: %s" % (commandName, err)

    def shutdown(self):
        self.connection.close()

    # @checkErrors
    def autoscale(self):
        self.write(":autoscale")

    # @checkErrors
    def run(self):
        self.write(":RUN")

    # @checkErrors
    def stop(self):
        self.write(":STOP")

    # @checkErrors
    def single(self):
        self.write(":SINGLE")

    # =========================
    #        Horizontal 
    # =========================
    # @checkErrors
    def setTimebase(self, value):
        self.write(":timebase:scale %g" % (value/10.0))
        self.write(":timebase:mode main")

    # @checkErrors
    def setDelay(self, value):
        self.write(":timebase:delay %g" % value)

    # @checkErrors
    def setTimescale(self, value):
        self.write(":timebase:range %g" % value)

    # =========================
    #        Vertical 
    # =========================
    # @checkErrors
    def setRange(self, value, channel=1):
        self.write(":channel%d:range %g" % (channel, value))

    # @checkErrors
    def setOffset(self, value, channel=1):
        self.write(":channel%d:offset %g" % (channel, value))

    # @checkErrors
    def setCoupling(self, value, channel=1):
        if (value not in ["DC", "AC"]):
            raise Exception("Incorrect Initialization Parameter")
        else:
            self.write(":channel%d:offset %s" % (channel, value))

    # =========================
    #        Trigger 
    # =========================
    # @checkErrors
    def setEdgeTrigger(self, channel, level, sign=1):
        self.write(":trigger:mode edge")
        self.write(":trigger:edge:source channel%d" % channel)
        self.write(":trigger:edge:level %g" % level)
        if (sign>0):
            self.write(":trigger:edge:slope positive")
        else:
            self.write(":trigger:edge:slope negative")

    def setAutoSweep(self, auto):
        if auto:
            self.write(":trigger:sweep auto")
        else:
            self.write(":trigger:sweep normal")

    # @checkErrors
    def setExtTrigger(self):
        self.write(":trigger:mode edge")
        self.write(":trigger:edge:source external")
        self.write(":trigger:edge:slope positive")

    def trigger(self):
        self.write(":trigger:force")

    # =========================
    #       Acquisition 
    # =========================
    # @checkErrors
    def configureAcquisition(self, mode="normal", count=50):    
        if (mode not in ["normal", "average", "highres", "peak"]):
             raise Exception("Incorrect Initialization Parameter")
        else:
            self.write(":acquire:type %s" % mode)
        # This must apparently be 100, no matter what?
        self.write(":acquire:complete 100")
        if mode=="average":
            self.write(":acquire:count %d" % count)

        # Set waveform data formatting
        self.write(":waveform:format byte")
        self.write(":waveform:points:mode raw")

    def getAvailablePoints(self):
        return int(self.ask_for_values(":waveform:points?")[0])

    # @checkErrors
    def getWaveformInfo(self, channel=1, display=False):
        self.write(":waveform:source channel%d" % channel)

        wav_form_dict   = {0 : "BYTE", 1 : "WORD", 4 : "ASCii", }
        acq_type_dict   = {0 : "NORMal", 1 : "PEAK", 2 : "AVERage", 3 : "HRESolution", }
        preamble_string = self.ask(":waveform:preamble?")

        descriptions = ( "Waveform format: %s", "Acquire type: %s", "Waveform points desired: %s", 
                         "Waveform average count: %s", "Waveform X increment: %s", "Waveform X origin: %s", 
                         "Waveform X reference: %s", "Waveform Y increment: %s", "Waveform Y origin: %s", 
                         "Waveform Y reference: %s")

        keys = ( "wav_form", "acq_type", "wfmpts", "avgcnt", "x_increment", "x_origin",
                 "x_reference", "y_increment", "y_origin", "y_reference")

        values    = string.split(preamble_string, ",")
        values    = [float(value) for value in values]
        values[0] = wav_form_dict[int(values[0])]
        values[1] = acq_type_dict[int(values[1])]

        if channel == 1:
            self.channel1WaveformInfo = dict(zip(keys, values))
            self.cached1 = True
        elif channel == 2:
            self.channel2WaveformInfo = dict(zip(keys, values))
            self.cached2 = True
        else:
            raise Exception("Waveform Info: erroneous channel specification")

        if display:
            for key, value in dict(zip(descriptions, values)).iteritems():
                print key % value

    # @checkErrors
    def takeTrace(self, channel1=True, channel2=False):
        if channel1 and channel2:
            self.write(":digitize channel1, channel2")
        elif channel1:
            self.write(":digitize channel1")
        elif channel2:
            self.write(":digitize channel2")
        else:
            raise Exception("Scope:Digitize: No channels specified!")

    def takeTraceFast(self, channel1=True, channel2=False):
        if channel1 and channel2:
            self.write(":digitize channel1, channel2")
        elif channel1:
            self.write(":digitize channel1")
        elif channel2:
            self.write(":digitize channel2")
        else:
            raise Exception("Scope:Digitize: No channels specified!")

    # @checkErrors
    def downloadTrace(self, channel=1):
        self.write(":waveform:source channel%d" % channel)
        self.write(":waveform:data?")
        data = self.connection.read_raw()
        data = self.getBinaryBlock(data)
        data = np.array(struct.unpack("%dB" % len(data), data))
        
        # We need these to convert the binary value to something useful
        x_increment = self.ask_for_values(":waveform:xincrement?")[0]
        x_origin    = self.ask_for_values(":waveform:xorigin?")[0]
        y_increment = self.ask_for_values(":waveform:yincrement?")[0]
        y_origin    = self.ask_for_values(":waveform:yorigin?")[0]
        y_reference = self.ask_for_values(":waveform:yreference?")[0]

        yValues = y_origin + y_increment*(data - y_reference)
        xValues = x_origin + x_increment*np.arange(0, len(yValues))
        return np.array(xValues), np.array(yValues)

    def downloadTraceFast(self, channel=1):
        # Make sure we have the relevant info for reconstructing traces
        if channel==1:
            if not self.cached1:
                self.getWaveformInfo(channel=1)
        elif channel==2:
            if not self.cached2:
                self.getWaveformInfo(channel=2)

        self.write(":waveform:source channel%d" % channel)
        self.write(":waveform:data?")
        data = self.connection.read_raw()
        data = self.getBinaryBlock(data)
        data = np.array(struct.unpack("%dB" % len(data), data))

        if channel==1:
            info = self.channel1WaveformInfo
        else:
            info = self.channel2WaveformInfo

        yValues = info['y_origin'] + info['y_increment']*(data - info['y_reference'])
        xValues = info['x_origin'] + info['x_increment']*np.arange(0, len(yValues))      
        return np.array(xValues), np.array(yValues)

    def getBinaryBlock(self, sBlock):
        # First character should be "#".
        pound = sBlock[0:1]
        if pound != "#":
            print "PROBLEM: Invalid binary block format, pound char is '%s'." % pound
            raise Exception("Invalid binary block")
            return
        # Second character is number of following digits for length value.
        digits = sBlock[1:2]
        # Get the data out of the block and return it.
        return sBlock[int(digits) + 2:]

    # @checkErrors
    def getScreenshot(self):
        self.write(":hardcopy:inksaver off")
        data = self.ask(":display:data? png, color")
        return self.getBinaryBlock(data)

    def shutdown(self):
        self.connection.clear()
        pass
