#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_discrete_set,
                                              strict_range)
from pymeasure.instruments import (Instrument,
                                   RangeException)

import pandas as pd
import re
import numpy as np

class AgilentB1500Instrument(Instrument):
    def query_learn(self, query_type):
        """ Issues *LRN? (learn) command to the instrument to read configuration.
        Returns dictionary of commands and set values.
        
        :param query_type: Query type according to the programming guide
        :type query_type: int
        :return: Dictionary of command and set values
        :rtype: dict
        """
        response = self.ask("*LRN? "+str(query_type))
        #response.split(';')
        response = re.findall(r'(?P<command>[A-Z]+)(?P<parameter>[0-9,]+)', response)
        response_dict = {}
        for element in response:
            response_dict[element[0]] = element[1].split(',')
        return response_dict

######################################
# Agilent B1500 Mainframe
######################################

class AgilentB1500(AgilentB1500Instrument):
    """ Represents the Agilent B1500 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking current-voltage (I-V) measurements.

    .. code-block:: python

        from pymeasure.instruments.agilent import AgilentB1500

        # explicitly define r/w terminations; set sufficiently large timeout or None.
        

        # reset the instrument
        

        # define configuration file for instrument and load config
        

        # save data variables, some or all of which are defined in the json config file.
        

        # take measurements
        

        # measured data is a pandas dataframe and can be exported to csv.
        
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent B1500 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self._smu_names = {}
        #setting of data output format -> determines how to read measurement data
        self._data_format = self._data_formatting("FMT"+self.query_data_format()[0])

#    def get_smu_names(self):
#        """ Dictionary of Channel Number and SMU Names. """
#        return self._smu_names

    def reset(self):
        """ Resets the instrument to default settings (``*RST``)
        """
        self.write("*RST")

    def query_modules(self):
        """ Queries module models from the instrument. 
        Returns dictionary of channel and module type.
        
        :return: Channel:Module Type
        :rtype: dict
        """
        modules = self.ask('UNT?')
        modules = modules.split(';')
        module_names = {
            'B1525A':'SPGU',
            'B1517A':'HRSMU',
            'B1511A':'MPSMU',
            'B1511B':'MPSMU',
            'B1510A':'HPSMU',
            'B1514A':'MCSMU',
            'B1520A':'MFCMU'
        }
        out = {}
        for i, module in enumerate(modules):
            module = module.split(',')
            if not module[0] == '0':
                try:
                    out[i] = module_names[module[0]]
                except:
                    raise NotImplementedError('Module {} is not implented yet!'.format(module[0]))
        return out

    def initialize_smu(self, channel, smu_type, name):
        """ Initializes SMU instance
        
        :param channel: SMU channel
        :type channel: int
        :param smu_type: SMU type, e.g. ``'HRSMU'``
        :type smu_type: str
        :param name: SMU name for pymeasure (data output etc.)
        :type name: str
        :return: SMU instance
        :rtype: SMU
        """
        channel = strict_discrete_set(channel,list(range(1,11))+list(range(101,1101,100))+list(range(102,1102,100)))
        if channel in range(1,11):
            channel = channel*100 + 1 #subchannel notation, first subchannel = channel for SMU/CMU
        self._smu_names[channel] = name
        return SMU(self.adapter, channel, smu_type, name)

    def initialize_all_smus(self):
        """ Initialize all SMUs by querying available modules and creating a SMU class instance for each.
        SMUs are accessible via attributes ``.smu1`` etc.
        """
        modules = self.query_modules()
        i=1
        for channel, smu_type in modules.items():
            if 'SMU' in smu_type:
                setattr(self, 'smu'+str(i), self.initialize_smu(channel, smu_type, 'SMU'+str(i)))
                i += 1

    def pause(self, pause_seconds):
        """ Pauses Command Excecution for given time in seconds (``PA``)
        
        :param pause_seconds: Seconds to pause
        :type pause_seconds: int
        """
        self.write("PA %d" % pause_seconds)

    def abort(self):
        """ Aborts the present operation but channels may still output current/voltage (``AB``)
        """
        self.write("AB")

    def start_meas(self):
        """ Starts Measurement (except High Speed Spot) (``XE``)
        """
        self.write("XE")
    
    def force_gnd(self):
        """ Force 0V on all channels immediately. Current Settings can be restored with RZ. (``DZ``)
        """
        self.write("DZ")

    def check_errors(self):
        """ Check for errors (``ERRX?``)
        """
        error = self.ask("ERRX?")
        error = re.match(r'(?P<errorcode>[+-]?\d+(?:\.\d+)?),"(?P<errortext>[\w\s.]+)', error).groups()
        if int(error[0]) == 0:
            return
        else:
            raise IOError("Agilent B1500 Error {0}: {1}".format(error[0],error[1]))

    def check_idle(self):
        """ Check if instrument is idle (``*OPC?``)
        """
        self.write("*OPC?")

    def clear_buffer(self):
        """ Clear output data buffer (``BC``) """
        self.write("BC")

    def clear_timer(self):
        """ Clear timer count (``TSR``) """
        self.write("TSR")

    def send_trigger(self):
        """ Send trigger to start measurement (``XE``) """
        self.write("XE")

    auto_calibration = Instrument.control(
        "?LRN 31","CM %d",
        """ Enable/Disable SMU auto-calibration every 30 minutes. (``CM``)""",
        values={True:1,False:0},
        validator=strict_discrete_set,
        map_values=True,
        get_process=(lambda response: re.search('(CM)(?P<parameter>[0-9,]+)', response).groups()[1])
    )


    ######################################
    # Data Formatting
    ######################################

    class _data_formatting_generic():
        """ Format data output head of measurement value into user readable values
        
        :param str output_format_str: Format string of measurement value
        :param dict smu_names: Dictionary of channel and SMU name
        """
        def __init__(self, output_format_str,smu_names={}):
            """ Stores parameters of the chosen output format
            for later usage in reading and processing instrument data.

            Data Names: e.g. "Voltage (V)" or "Current Measurement (A)"
            """
            sizes={"FMT1":16,"FMT11":17,"FMT21":19}
            try:
                self.size = sizes[output_format_str]
            except:
                raise NotImplementedError(
                "Data Format {0} is not implemented so far.".format(output_format_str)
                )
            self.format = output_format_str
            data_names_C = {
                "V":"Voltage (V)",
                "I":"Current (A)",
                "F":"Frequency (Hz)",
            }
            data_names_CG = {
                "Z":"Impedance (Ohm)",
                "Y":"Admittance (S)",
                "C":"Capacitance (F)",
                "L":"Inductance (H)",
                "R":"Phase (rad)",
                "P":"Phase (deg)",
                "D":"Dissipation factor",
                "Q":"Quality factor",
                "X":"Sampling index",
                "T":"Time (s)"
            }
            data_names_G = {
                "V":"Voltage Measurement (V)",
                "I":"Current Measurement (A)",
                "v":"Voltage Output (V)",
                "i":"Current Output (A)",
                "f":"Frequency (Hz)",
                "z":"invalid data"
            }
            if output_format_str in ['FMT1','FMT5','FMT11','FMT15']:
                self.data_names={**data_names_C,**data_names_CG}
            elif output_format_str in ['FMT21','FMT25']:
                self.data_names={**data_names_G,**data_names_CG}
            else:
                self.data_names={} #no header
            self.smu_names = smu_names

        def format_channel(self, channel_string):
            """ Returns channel number for given channel letter
            
            :param channel_string: Channel letter out of measurement data head
            :type channel_string: str
            :return: If possible SMU name, otherwise channel number or GNDU or MISC
            :rtype: int or str
            """
            channels = {"A":101,"B":201,"C":301,"D":401,"E":501,"F":601,"G":701,"H":801,"I":901,"J":1001,
                "a":102,"b":202,"c":302,"d":402,"e":502,"f":602,"g":702,"h":802,"i":902,"j":1002,
                "V":"GNDU","Z":"MISC"}
            channel = channels[channel_string]
            try:
                smu = self.smu_names[channel]
                return smu
            except:
                return channel
    
    class _data_formatting_FMT1(_data_formatting_generic):
        """ Data formatting for FMT1 format
        """
        def __init__(self, smu_names={}):
            super().__init__("FMT1", smu_names)

        def format_single(self, element):
            """ Format single measurement value
            
            :param element: Single measurement value read from the instrument
            :type element: str
            :return: Status, channel, data name, value
            :rtype: (str, str, str, float)
            """
            status = element[0] #one character
            channel = element[1]
            data_name = element[2]
            value = float(element[3:])
            channel = self.format_channel(channel)
            data_name = self.data_names[data_name]
            return (status,channel,data_name,value)
    
    class _data_formatting_FMT11(_data_formatting_FMT1):
        """ Data formatting for FMT11 format
        """
        def __init__(self, smu_names={}):
            super().__init__("FMT11", smu_names)
    
    class _data_formatting_FMT21(_data_formatting_generic):
        """ Data formatting for FMT21 format
        """
        def __init__(self, smu_names={}):
            super().__init__("FMT21", smu_names)

        def format_single(self, element):
            """ Format single measurement value
            
            :param element: Single measurement value read from the instrument
            :type element: str
            :return: Status (three digits), channel, data name, value
            :rtype: (str, str, str, float)
            """
            status = element[0:3] # three digits
            channel = element[3]
            data_name = element[4]
            value = float(element[5:])
            channel = self.format_channel(channel)
            data_name = self.data_names[data_name]
            return (status,channel,data_name,value)

    def _data_formatting(self, output_format_str,smu_names={}):
        """ Return data formatting class for given data format string
        
        :param output_format_str: Data output format, e.g. ``FMT21``
        :type output_format_str: str
        :param smu_names: Dictionary of channels and SMU names, defaults to {}
        :type smu_names: dict, optional
        :return: Corresponding formatting class
        :rtype: class
        """
        classes = {
            "FMT21":self._data_formatting_FMT21,
            "FMT1":self._data_formatting_FMT1,
            "FMT11":self._data_formatting_FMT11
            }
        try:
            format_class = classes[output_format_str]
        except:
            raise NotImplementedError(
            "Data Format {0} is not implemented so far.".format(output_format_str)
            )
        return format_class(smu_names)

    def data_format(self,output_format,mode=0):
        """ Specifies data output format. Check Documentation for parameters.
        Should be called once per session to set the data format for interpreting the read
        measurement values. (``FMT``)
        
        :param output_format: Output format string, e.g. ``FMT21``
        :type output_format: str
        :param mode: Data output mode, defaults to 0 (only measurement data is returned)
        :type mode: int, optional
        """
        output_format = strict_discrete_set(output_format,[1,2,3,4,5,11,12,13,14,15,21,22,25])
        mode = strict_range(mode,range(0,11))      
        self.write("FMT %d, %d" % (output_format, mode))
        self.check_errors()
        self._data_format = self._data_formatting("FMT%d" % output_format, self._smu_names)

    def query_data_format(self):
        return self.query_learn(31)['FMT']

    ######################################
    # Measurement Settings
    ######################################

    parallel_measurement = Instrument.setting(
        "PAD %d",
        """ Enable/Disable parallel measurements.
            Effective for SMUs using HSADC and measurement modes 1,2,10,18. (``PAD``)
        """,
        values={True:1,False:0},
        validator=strict_discrete_set,
        map_values=True,
        check_set_errors=True
    )

    def meas_mode(self, mode, *args):
        """ Set Measurement mode of channels. Measurements will be taken in the same order 
        as the SMU references are passed. (``MM``)
        
        :param mode: Measurement mode

            - Spot
            - Staircase Sweep
            - Sampling

        :type mode: str
        :param args: SMU references
        """
        mode_values = {"Spot":1,"Staircase Sweep":2,"Sampling":10}
        # values = {1,2,3,4,5,9,10,13,14,15,16,17,18,19,20,22,23,26,27,28}
        #mode = strict_discrete_set(mode,mode_values)
        try:
            mode = mode_values[mode]
        except:
            raise NotImplementedError("Measurement Mode {0} is not implemented yet.".format(mode))
        cmd = "MM %d" % mode
        for smu in args:
            cmd += ", %d" %smu.channel
        self.write(cmd)
        self.check_errors()

    # ADC Setup: AAD, AIT, AV, AZ

    def adc_setup(self,adc_type,mode,N=''):
        """ Set up operation mode and parameters of ADC for each ADC type. (``AIT``)
        Defaults:

            - HSADC: Auto N=1, Manual N=1, PLC N=1, Time N=0.000002(s)
            - HRADC: Auto N=6, Manual N=3, PLC N=1
        
        :param adc_type: ADC type (``'HSADC','HRADC','HSADC pulsed'``)
        :type adc_type: str
        :param mode: ADC mode (``'Auto','Manual','PLC','Time'``)
        :type mode: str
        :param N: additional parameter, check documentation, defaults to ''
        :type N: str, optional
        """
        adc_type_values={'HSADC':0,'HRADC':1,'HSADC pulsed':2}
        adc_type = strict_discrete_set(adc_type,adc_type_values)
        adc_type = adc_type_values[adc_type]
        mode_values={'Auto':0,'Manual':1,'PLC':2,'Time':3}
        mode = strict_discrete_set(mode,mode_values)
        mode = mode_values[mode]
        if (adc_type == 'HRADC') and (mode == 'Time'):
            raise ValueError("Time ADC mode is not available for HRADC")
        command = "AIT %d, %d" % (mode,adc_type)
        if not N == '':
            command += (", %f" % N)
        self.write(command)
        self.check_errors()

    def adc_averaging(self,number,mode='Auto'):
        """ Set number of averaging samples of the HSADC. (``AV``)
        
        Defaults: N=1, Auto
        
        :param number: Number of averages
        :type number: int
        :param mode: Mode (``'Auto','Manual'``), defaults to 'Auto'
        :type mode: str, optional
        """
        if number > 0:
            number = strict_range(number,range(1,1024))
            mode_values = {'Auto':0,'Manual':1}
            mode = strict_discrete_set(mode,mode_values)
            mode = mode_values[mode]
            self.write("AV %d, %d" % (number,mode))
        else:
            number = strict_range(number,range(-1,-101,-1))
            self.write("AV %d" % number)

    adc_auto_zero = Instrument.setting(
        "AZ %d",
        """ Enable/Disable ADC zero function. Halfs the integration time, if off. (``AZ``)""",
        values={True:1,False:0},
        validator=strict_discrete_set,
        map_values=True,
        check_set_errors=True
    )

    ######################################
    # Sweep Setup
    ######################################

    def sweep_timing(self,hold,delay,step_delay=0,step_trigger_delay=0,measurement_trigger_delay=0):
        """ Sets Hold Time, Delay Time and Step Delay Time for 
        staircase or multi channel sweep measurement. (``WT``)
        If not set, all parameters are 0.
        
        :param hold: Hold time
        :type hold: float
        :param delay: Delay time
        :type delay: float
        :param step_delay: Step delay time, defaults to 0
        :type step_delay: float, optional
        :param step_trigger_delay: Trigger delay time, defaults to 0
        :type step_trigger_delay: float, optional
        :param measurement_trigger_delay: Measurement trigger delay time, defaults to 0
        :type measurement_trigger_delay: float, optional
        """
        hold = strict_range(hold*100,range(0,65536))/100 # resolution 10ms
        delay = strict_range(delay*10000,range(0,655351))/10000 # resolution 0.1ms
        step_delay = strict_range(step_delay*10000,range(0,10001))/10000 # resolution 0.1ms
        step_trigger_delay = strict_range(step_trigger_delay*10000,range(0,10001))/10000 # resolution 0.1ms
        measurement_trigger_delay = strict_range(measurement_trigger_delay*10000,range(0,655351))/10000 # resolution 0.1ms
        self.write("WT %f, %f, %f, %f, %f" % (hold, delay, step_delay,step_trigger_delay,measurement_trigger_delay))
        self.check_errors()

    def sweep_auto_abort(self,abort,post='Start'):
        """ Enables/Disables the automatic abort function.
        Also sets the post measurement condition. (``WM``)
        
        :param abort: Enable/Disable automatic abort
        :type abort: bool
        :param post: Output after measurement (``'Start','Stop'``), defaults to 'Start'
        :type post: str, optional
        """
        abort_values = {True:2,False:1}
        abort = strict_discrete_set(abort.upper(),abort_values)
        abort = abort_values[abort.upper()]
        post_values = {"START":1,"STOP":2}
        post = strict_discrete_set(post.upper(),post_values)
        post = post_values[post.upper()]
        self.write("WM %d, %d" % (abort, post))
        self.check_errors()

    sampling_mode = Instrument.setting(
        "ML %d",
        """ Set linear or logarithmic sampling mode. (``ML``)""",
        values={"Linear":1,
        "Log 10 data/decade":2,"Log 25 data/decade":3,"Log 50 data/decade":4,
        "Log 100 data/decade":5,"Log 250 data/decade":6,"Log 5000 data/decade":7},
        validator=strict_discrete_set,
        map_values=True,
        check_set_errors=True
    )

    ######################################
    # Sampling Setup
    ######################################

    def sampling_timing(self,hold_bias,interval,number,hold_base=0):
        """ Sets Timing Parameters for the Sampling Measurement (``MT``)
        
        :param hold_bias: Bias hold time
        :type hold_bias: float
        :param interval: Sampling interval
        :type interval: float
        :param number: Number of Samples
        :type number: int
        :param hold_base: Base hold time, defaults to 0
        :type hold_base: float, optional
        """
        hold_bias = strict_range(hold_bias*100,range(0,65536))/100 # resolution 10ms
        interval = strict_range(interval*10000,range(0,655351))/10000 # resolution 0.1ms, restrictions apply (number of measurement channels)
        number = strict_range(number,range(0,100002)) # restrictions apply (number of measurement channels)
        hold_base = strict_range(hold_base*100,range(0,65536))/100 # resolution 0.01s
        self.write("MT %f, %f, %d, %f" % (hold_bias,interval,number,hold_base))
        self.check_errors()

    def sampling_auto_abort(self,abort,post='Bias'):
        """ Enables/Disables the automatic abort function.
        Also sets the post measurement condition. (``MSC``)
        
        :param abort: Enable/Disable automatic abort
        :type abort: bool
        :param post: Output after measurement (``'Base','Bias'``), defaults to 'Bias'
        :type post: str, optional
        """
        abort_values = {True:2,False:1}
        abort = strict_discrete_set(abort.upper(),abort_values)
        abort = abort_values[abort.upper()]
        post_values = {"BASE":1,"BIAS":2}
        post = strict_discrete_set(post.upper(),post_values)
        post = post_values[post.upper()]
        self.write("MSC %d, %d" % (abort, post))
        self.check_errors()

    ######################################
    # Read out of data
    ######################################

    def read_data(self,number_of_points):
        """ Reads all data from buffer and returns Pandas DataFrame. 
        Specify number of measurement points for correct splitting of the data list.
        
        :param number_of_points: Number of measurement points
        :type number_of_points: int
        :return: Measurement Data
        :rtype: pd.DataFrame
        """
        data = self.read()
        data = data.split(',')
        data = np.array(data)
        data = np.split(data,number_of_points)
        data = pd.DataFrame(data=data)
        data = data.applymap(self._data_format.format_single)
        heads = data.iloc[[0]].applymap(lambda x: ' '.join(x[1:3])) # channel & data_type
        heads = heads.to_numpy().tolist() #2D List
        heads = heads[0] #first row
        data = data.applymap(lambda x: x[3])
        data.columns = heads
        return data


    def read_channels(self,nchannels):
        """ Reads data for 1 measurement point from the buffer. Specify number of 
        measurement channels + sweep sources (depending on data output setting).
        
        :param nchannels: Number of channels which return data
        :type nchannels: int
        :return: Measurement data
        :rtype: tuple
        """
        data = self.adapter.read_bytes(self._data_format.size * nchannels)
        data = data.decode("ASCII")
        data = data.rstrip('\r,') # ',' if more data in buffer, '\r' if last data point
        data = data.split(',')
        data = map(self._data_format.format_single, data)
        data = tuple(data)
        return data

######################################        
# SMU Setup
######################################

class SMU(AgilentB1500Instrument):
    """ Provides specific methods for the SMUs of the Agilent B1500 mainframe
    
    :param resourceName: Resource name of the B1500 mainframe
    :param int channel: Channel number of the SMU
    :param str smu_type: Type of the SMU
    """

    def __init__(self, resourceName, channel, smu_type, name, **kwargs):
        super().__init__(
            resourceName,
            name, #"SMU of Agilent B1500 Semiconductor Parameter Analyzer"
            **kwargs
        )
        channel = strict_discrete_set(channel,list(range(1,11))+list(range(101,1101,100))+list(range(102,1102,100)))
        if channel in range(1,11):
            self.channel = channel*100 + 1 #subchannel notation, first subchannel = channel for SMU/CMU
        else:
            self.channel = channel
        smu_type = strict_discrete_set(smu_type,['HRSMU','MPSMU','HPSMU','MCSMU',
            'HCSMU','DHCSMU','HVSMU','UHCU','HVMCU','UHVU'])
        self.voltage_output_ranging = self.ranging(smu_type,source_type='Voltage',ranging_type='Output')
        self.voltage_meas_ranging = self.ranging(smu_type,source_type='Voltage',ranging_type='Measurement')
        self.current_output_ranging = self.ranging(smu_type,source_type='Current',ranging_type='Output')
        self.current_meas_ranging = self.ranging(smu_type,source_type='Current',ranging_type='Measurement')

        # Instrument settings need to be set up in __init__ 
        # since self.channel is required

        filter = Instrument.setting(
            ("FL %d" % self.channel) + ", %d",
            """ Enables/Disables SMU Filter. (``FL``)""",
            values={True:1,False:0},
            validator=strict_discrete_set,
            map_values=True,
            check_set_errors=True
        )

        series_resistor = Instrument.setting(
            ("SSR %d" % self.channel) + ", %d",
            """ Enables/Disables 1MOhm series resistor. (``SSR``)""",
            values={True:1,False:0},
            validator=strict_discrete_set,
            map_values=True,
            check_set_errors=True
        )

        meas_type = Instrument.setting(
            ("CMM %d" % self.channel) + ", %d",
            """ Set SMU measurement operation mode. (``CMM``)
            
            Possible values: ``"Compliance Side","Current","Voltage","Force Side","Compliance and Force Side"``
            """,
            values={"Compliance Side":0,"Current":1,"Voltage":2,"Force Side":3,"Compliance and Force Side":4},
            validator=strict_discrete_set,
            map_values=True,
            check_set_errors=True
        )
        
        adc_type = Instrument.setting(
            ("AAD %d" % self.channel)+", %d",
            """ Specify ADC type for each measurement channel individually. (``AAD``)

            Possible values: ``'HSADC','HRADC','HSADC pulsed'``
            """,
            validator=strict_discrete_set,
            values={'HSADC':0,'HRADC':1,'HSADC pulsed':2},
            map_values=True,
            check_set_errors=True)

        meas_range_current = Instrument.setting(
            ("RI %d" % self.channel) + ", %d",
            """ Sets the current measurement range. (``RI``)

            Possible settings depend on SMU type, e.g. ``'Auto Ranging'`` or ``'2 V'``
            """,
            validator=strict_discrete_set,
            values=self.current_meas_ranging.ranges,
            map_values=False,
            check_set_errors=True
            )

        meas_range_voltage = Instrument.setting(
            ("RV %d" % self.channel) + ", %d",
            """ Sets the current measurement range. (``RV``)

            Possible settings depend on SMU type, e.g. ``'Auto Ranging'`` or ``'1 nA'``
            """,
            validator=strict_discrete_set,
            values=self.voltage_meas_ranging.ranges,
            map_values=False,
            check_set_errors=True
            )
    
    @property
    def query_status(self):
        channel = str(self.channel)[0:-2] #only first digits of channel 101 -> 1 / 1001 -> 10
        channel = strict_range(int(channel),range(0,11))
        return self.query_learn(channel)

    def enable(self):
        """ Enable Source/Measurement Channel (``CN``)"""
        self.write("CN %d" % self.channel)
    
    def disable(self):
        """ Disable Source/Measurement Channel (``CL``)"""
        self.write("CL %d" % self.channel)

    def force_gnd(self):
        """ Force 0V immediately. Current Settings can be restored with ``RZ``. (``DZ``)"""
        self.write("DZ %d" % self.channel)

    class ranging():
        """ Possible Settings for SMU Current/Voltage Output/Measurement ranges.
        Transformation of available Voltage/Current Range Names to Index and back.
        Checks for compatibility with specified SMU type.
        
        :param str smu_type: SMU type
        :param str source_type: Source type, defaults to 'Voltage'
        :param str ranging_type: Ranging type, defaults to 'Output'
        """
        def __init__(self,smu_type,source_type='Voltage',ranging_type='Output'):
            if source_type.upper() == 'VOLTAGE':
                smu = {
                    'HRSMU': [0, 5, 20, 50, 200, 400, 1000],
                    'MPSMU': [0, 5, 20, 50, 200, 400, 1000],
                    'HPSMU': [0, 20, 200, 400, 1000, 2000],
                    'MCSMU': [0, 2, 20, 200, 400],
                    'HCSMU': [0, 2, 20, 200, 400],
                    'DHCSMU': [0, 2, 20, 200, 400],
                    'HVSMU': [0, 2000, 5000, 15000, 30000],
                    'UHCU': [0, 1000],
                    'HVMCU': [0, 15000, 30000],
                    'UHVU': [0, 103]
                    }
                if ranging_type.upper() == 'OUTPUT':
                    names = {
                        'Auto Ranging': 0,
                        '0.2 V limited auto ranging': 2,
                        '0.5 V limited auto ranging': 5,
                        '2 V limited auto ranging': 11,
                        '2 V limited auto ranging': 20,  # or 11
                        '5 V limited auto ranging': 50,
                        '20 V limited auto ranging': 12,
                        '20 V limited auto ranging': 200,  # or 12
                        '40 V limited auto ranging': 13,
                        '40 V limited auto ranging': 400,  # or 13
                        '100 V limited auto ranging': 14,
                        '100 V limited auto ranging': 1000,  # or 14
                        '200 V limited auto ranging': 15,
                        '200 V limited auto ranging': 2000,  # or 15
                        '500 V limited auto ranging': 5000,
                        '1500 V limited auto ranging': 15000,
                        '3000 V limited auto ranging': 30000,
                        '10 kV limited auto ranging': 103
                        }   
                elif ranging_type.upper() == 'MEASUREMENT':
                    names = {
                        'Auto Ranging': 0,
                        '0.2 V': 2,
                        '0.5 V': 5,
                        '2 V': 11,
                        '2 V': 20,  # or 11
                        '5 V': 50,
                        '20 V': 12,
                        '20 V': 200,  # or 12
                        '40 V': 13,
                        '40 V': 400,  # or 13
                        '100 V': 14,
                        '100 V': 1000,  # or 14
                        '200 V': 15,
                        '200 V': 2000,  # or 15
                        '500 V': 5000,
                        '1500 V': 15000,
                        '3000 V': 30000,
                        '10 kV': 103
                        }
                else:
                    raise ValueError(
                    'Specified Ranging Type is not valid (possible: Measurement or Output)'
                    )
            elif source_type.upper() == 'CURRENT':
                if ranging_type.upper() == 'OUTPUT':
                    names = {
                        'Auto Ranging': 0,
                        '1 pA limited auto ranging': 8,  # for ASU
                        '10 pA limited auto ranging': 9,
                        '100 pA limited auto ranging': 10,
                        '1 nA limited auto ranging': 11,
                        '10 nA limited auto ranging': 12,
                        '100 nA limited auto ranging': 13,
                        '1 uA limited auto ranging': 14,
                        '10 uA limited auto ranging': 15,
                        '100 uA limited auto ranging': 16,
                        '1 mA limited auto ranging': 17,
                        '10 mA limited auto ranging': 18,
                        '100 mA limited auto ranging': 19,
                        '1 A limited auto ranging': 20,
                        '2 A limited auto ranging': 21,
                        '20 A limited auto ranging': 22,
                        '40 A limited auto ranging': 23,
                        '500 A limited auto ranging': 26,
                        '2000 A limited auto ranging': 28
                        }
                    smu = {
                        # in combination with ASU also 8
                        'HRSMU': [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                        # in combination with ASU also 8,9,10
                        'MPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                        'HPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                        'MCSMU': [0, 15, 16, 17, 18, 19, 20],
                        'HCSMU': [0, 15, 16, 17, 18, 19, 20, 22],
                        'DHCSMU': [0, 15, 16, 17, 18, 19, 20, 21, 23],
                        'HVSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18],
                        'UHCU': [0, 26, 28],
                        'HVMCU': [],
                        'UHVU': []
                        }
                elif ranging_type.upper() == 'MEASUREMENT':
                    names = {
                        'Auto Ranging': 0,
                        '1 pA': 8,  # for ASU
                        '10 pA': 9,
                        '100 pA': 10,
                        '1 nA': 11,
                        '10 nA': 12,
                        '100 nA': 13,
                        '1 uA': 14,
                        '10 uA': 15,
                        '100 uA': 16,
                        '1 mA': 17,
                        '10 mA': 18,
                        '100 mA': 19,
                        '1 A': 20,
                        '2 A': 21,
                        '20 A': 22,
                        '40 A': 23,
                        '500 A': 26,
                        '2000 A': 28
                        }
                    smu = {
                        # in combination with ASU also 8
                        'HRSMU': [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                        # in combination with ASU also 8,9,10
                        'MPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19],
                        'HPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
                        'MCSMU': [0, 15, 16, 17, 18, 19, 20],
                        'HCSMU': [0, 15, 16, 17, 18, 19, 20, 22],
                        'DHCSMU': [0, 15, 16, 17, 18, 19, 20, 21, 23],
                        'HVSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18],
                        'UHCU': [0, 26, 28],
                        'HVMCU': [0, 19, 21],
                        'UHVU': [0, 15, 16, 17, 18, 19]
                        }
                else:
                    raise ValueError(
                    'Specified Ranging Type is not valid (possible: Measurement or Output)'
                    )
            else:
                raise ValueError(
                    'Specified Source Type is not valid (possible: Voltage or Current)'
                    )
            inverse = {v: k for k, v in names.items()}
            ranges = {}
            indizes = {}
            for i in smu[smu_type]:
                ranges[i] = inverse[i] # Index -> Name
                indizes[inverse[i]] = i # Name -> Index

            self.indizes = indizes
            self.ranges = ranges
            self.ranging_type = ranging_type.upper()

        def get_index(self, range_name, fixed=False):
            """ Gives Index of given Range Name. 
            Throws error if range is not supported by this SMU.
            
            Measurement: only give Range Name without "limited auto ranging"/"range fixed".
            
            :param range_name: Range name, e.g. '1 nA'
            :type range_name: str
            :param fixed: Fixed ranging, defaults to False
            :type fixed: bool, optional
            :return: Range index
            :rtype: int
            """
            try:
                index = self.indizes[range_name]
            except:
                raise ValueError(
                    'Specified Range Name is not valid or not supported by this SMU'
                )
            if self.ranging_type == 'MEASUREMENT':
                if fixed:
                    index = -1 * index
            return index

        def get_name(self, index):
            """ Give range name of given index
            
            :param index: Range index
            :type index: int
            :return: Range name
            :rtype: str
            """
            try:
                range = self.ranges[abs(index)]
            except:
                raise ValueError(
                    'Specified Range is not supported by this SMU'
                )
            if self.ranging_type == 'MEASUREMENT':
                ranging_type = ''  # auto ranging: 0
                if index < 0:
                    ranging_type = ' range fixed'
                elif index > 0:
                    ranging_type = ' limited auto ranging'
                range += ranging_type
            return range


    ######################################
    # Force Constant Output
    ######################################

    def force_current(self, irange, current, Vcomp='', comp_polarity='', vrange=''):
        """ Applies DC Current from SMU immediately. (``DI``)
        
        :param irange: Current output range index
        :type irange: int
        :param current: Current output in A
        :type current: float
        :param Vcomp: Voltage compliance, defaults to previous setting
        :type Vcomp: float, optional
        :param comp_polarity: Compliance polairty, defaults to auto
        :type comp_polarity: int, optional
        :param vrange: Voltage compliance ranging type, defaults to auto
        :type vrange: int, optional
        """
        output = "DI " + self.channel + (", %d, %f" % (irange, current))
        if not Vcomp == '':
            output += ", %f" % Vcomp
            if not comp_polarity == '':
                output += ", %d" % comp_polarity
                if not vrange == '':
                    output += ", %d" % vrange
        self.write(output)
        self.check_errors()

    def ramp_to_current(self, irange, target_current, Vcomp='', comp_polarity='', vrange='', stepsize=0.001, pause=20e-3):
        """ Ramps to a target current from the set current value with a given
        step size, each separated by a pause duration.

        :param target_current: A voltage in Amps
        :param irange: Current output range index
        :type irange: int
        :param current: Current output in A
        :type current: float
        :param Vcomp: Voltage compliance, defaults to previous setting
        :type Vcomp: float, optional
        :param comp_polarity: Compliance polairty, defaults to auto
        :type comp_polarity: int, optional
        :param vrange: Voltage compliance ranging type, defaults to auto
        :type vrange: int, optional
        :param stepsize: Size of the steps
        :param pause: A pause duration in seconds to wait between steps
        """
        status = self.query_status
        if 'CL' in status:
            #SMU is OFF
            start = 0
        elif 'DI' in status:
            start = status['DI'][2]
        else:
            log.info("SMU {} in different state. Changing to Current Source.".format(self.name))
            start = 0

        currents = np.arange(
            start,
            target_current,
            stepsize
        )
        for current in currents:
            self.force_current(irange, current, Vcomp, comp_polarity, vrange)
            time.sleep(pause)

    def force_voltage(self, vrange, voltage, Icomp='', comp_polarity='', irange=''):
        """ Applies DC Voltage from SMU immediately. (``DV``)
        
        :param vrange: Voltage output range index
        :type vrange: int
        :param voltage: Voltage output in V
        :type voltage: float
        :param Icomp: Current compliance, defaults to previous setting
        :type Icomp: float, optional
        :param comp_polarity: Compliance polarity, defaults to auto
        :type comp_polarity: str, optional
        :param irange: Current compliance ranging type, defaults to auto
        :type irange: int, optional
        """
        output = "DV " + self.channel + (", %d, %f" % (vrange, voltage))
        if not Icomp == '':
            output += ", %f" % Icomp
            if not comp_polarity == '':
                output += ", %d" % comp_polarity
                if not irange == '':
                    output += ", %d" % irange
        self.write(output)
        self.check_errors()

    def ramp_to_voltage(self, vrange, target_voltage, Icomp='', comp_polarity='', irange='', stepsize=0.1, pause=20e-3):
        """ Ramps to a target voltage from the set voltage value with a given
        step size, each separated by a pause duration.

        :param target_voltage: A voltage in Amps
        :param vrange: Voltage output range index
        :type vrange: int
        :param voltage: Voltage output in V
        :type voltage: float
        :param Icomp: Current compliance, defaults to previous setting
        :type Icomp: float, optional
        :param comp_polarity: Compliance polarity, defaults to auto
        :type comp_polarity: str, optional
        :param irange: Current compliance ranging type, defaults to auto
        :type irange: int, optional
        :param stepsize: Size of the steps
        :param pause: A pause duration in seconds to wait between steps
        """
        status = self.query_status
        if 'CL' in status:
            #SMU is OFF
            start = 0
        elif 'DV' in status:
            start = status['DV'][2]
        else:
            log.info("SMU {} in different state. Changing to Voltage Source.".format(self.name))
            start = 0

        voltages = np.arange(
            start,
            target_voltage,
            stepsize
        )
        for voltage in voltages:
            self.force_voltage(vrange, voltage, Icomp, comp_polarity, irange)
            time.sleep(pause)

    ######################################
    # Measurement Range: RI, RV, (RC, TI, TTI, TV, TTV, TIV, TTIV, TC, TTC)
    ######################################

    def meas_range_current_auto(self, mode, rate=50):
        """ Specifies the auto range operation. Check Documentation. (``RM``)
        
        :param mode: Range changing operation mode
        :type mode: int
        :param rate: Parameter used to calculate the *current* value, defaults to 50
        :type rate: int, optional
        """
        mode = strict_range(mode,range(1,4))
        if mode == 1:
            self.write("RM %d, %d" % (self.channel,mode))
        else:
            self.write("RM %d, %d, %d" % (self.channel,mode,rate))
        self.write

    ######################################
    # Staircase Sweep Measurement: (WT, WM -> Instrument), WV, WI
    ######################################

    def staircase_sweep_source(self,source_type,mode,source_range,start,stop,steps,comp,Pcomp=''):
        """ Specifies Staircase Sweep Source (Current or Voltage) and its parameters. (``WV`` or ``WI``)
        
        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param mode: Sweep mode (``"LinearSingle","LogSingle","LinearDouble","LogDouble"``)
        :type mode: str
        :param source_range: Source range index
        :type source_range: int
        :param start: Sweep start value
        :type start: float
        :param stop: Sweep stop value
        :type stop: float
        :param steps: Number of sweep steps
        :type steps: int
        :param comp: Compliance value
        :type comp: float
        :param Pcomp: Power compliance, defaults to not set
        :type Pcomp: float, optional
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "WV"
        elif source_type.upper() == "CURRENT":
            cmd = "WI"
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        mode_values={"LinearSingle":1,"LogSingle":2,"LinearDouble":3,"LogDouble":4}
        mode=strict_discrete_set(mode,mode_values)
        mode=mode_values[mode]
        if mode in [2,4]:
            if start >= 0 and stop >= 0:
                pass
            elif start <=0 and stop <= 0:
                pass
            else:
                raise ValueError("For Log Sweep Start and Stop Values must have the same polarity.")
        steps=strict_range(steps,range(1,10002))
        #check on comp value not yet implemented
        if Pcomp == '':
            self.write(cmd + ("%d, %d, %d, %f, %f, %f, %f" % (self.channel,mode,source_range,start,stop,steps,comp)))
        else:
            self.write(cmd + ("%d, %d, %d, %f, %f, %f, %f, %f" % (self.channel,mode,source_range,start,stop,steps,comp,Pcomp)))
        self.check_errors()

    # Synchronous Output: WSI, WSV, BSSI, BSSV, LSSI, LSSV

    def synchronous_sweep_source(self,source_type,source_range,start,stop,comp,Pcomp=''):
        """ Specifies Synchronous Staircase Sweep Source (Current or Voltage) and its parameters. (``WSV`` or ``WSI``)
        
        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param source_range: Source range index
        :type source_range: int
        :param start: Sweep start value
        :type start: float
        :param stop: Sweep stop value
        :type stop: float
        :param comp: Compliance value
        :type comp: float
        :param Pcomp: Power compliance, defaults to not set
        :type Pcomp: float, optional
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "WSV"
        elif source_type.upper() == "CURRENT":
            cmd = "WSI"
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        #check on comp value not yet implemented
        if Pcomp == '':
            self.write(cmd + ("%d, %d, %f, %f, %f" % (self.channel,source_range,start,stop,comp)))
        else:
            self.write(cmd + ("%d, %d, %f, %f, %f, %f" % (self.channel,source_range,start,stop,comp,Pcomp)))
        self.check_errors()

    ######################################
    # Sampling Measurements: (ML, MT -> Instrument), MV, MI, MSP, MCC, MSC
    ######################################
    
    def sampling_source(self,source_type,source_range,base,bias,comp):
        """ Sets DC Source (Current or Voltage) for sampling measurement.
        DV/DI commands on the same channel overwrite this setting. (``MV`` or ``MI``)
        
        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param source_range: Source range index
        :type source_range: int
        :param base: Base voltage/current
        :type base: float
        :param bias: Bias voltage/current
        :type bias: float
        :param comp: Compliance value
        :type comp: float
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "MV"
        elif source_type.upper() == "CURRENT":
            cmd = "MI"
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        #check on comp value not yet implemented
        self.write(cmd + ("%d, %d, %f, %f, %f" % (self.channel,source_range,base,bias,comp)))
        self.check_errors()