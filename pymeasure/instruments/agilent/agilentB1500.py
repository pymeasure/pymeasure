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
import time
from enum import IntEnum
from collections import Counter, namedtuple

class QueryLearn():
    @staticmethod
    def query_learn(ask, query_type):
            """ Issues ``*LRN?`` (learn) command to the instrument to read configuration.
            Returns dictionary of commands and set values.
            
            :param query_type: Query type according to the programming guide
            :type query_type: int
            :return: Dictionary of command and set values
            :rtype: dict
            """
            response = ask("*LRN? "+str(query_type))
            #response.split(';')
            response = re.findall(r'(?P<command>[A-Z]+)(?P<parameter>[0-9,\+\-\.E]+)', response)
            # check if commands are unique -> suitable as keys for dict
            counts = Counter([item[0] for item in response])
            # responses that start with a channel number
            # the channel number should always be included in the key
            include_chnum = [
                'RI','RV', # Ranging
                'WV','WI','WSV','WSI', # Staircase Sweep
                'PV','PI','PWV','PWI', # Pulsed Source
                'MV','MI','MSP' # Sampling
                'SSR','RM','AAD' # Series Resistor, Auto Ranging, ADC
                ] #probably not complete yet...
            response_dict = {}
            for element in response:
                parameters = element[1].split(',')
                name = element[0]
                if (counts[name] > 1) or (name in include_chnum):
                    # append channel (first parameter) to command as dict key
                    name += parameters[0]
                    parameters = parameters[1:]
                if len(parameters) == 1:
                    parameters = parameters[0]
                response_dict[name] = parameters
            return response_dict
        
    @classmethod
    def query_learn_header(cls, ask, query_type, smu_references, single_command=False):
        """Issues ``*LRN?`` (learn) command to the instrument to read configuration.
        Processes information to human readable values for debugging purposes or file headers.
        
        :param ask: ask method of the instrument
        :type ask: Instrument.ask
        :param query_type: Number according to Programming Guide
        :type query_type: int or str
        :param smu_references: SMU references by channel
        :type smu_references: dict
        :param single_command: if only a single command should be returned, defaults to False
        :type single_command: str
        :return: Read configuration
        :rtype: dict
        """
        response = cls.query_learn(ask, query_type)
        if not single_command == False:
            response = response[single_command]
        ret = {}
        for key, value in response.items():
            command = re.findall(r'(?P<command>[A-Z]+)', key)[0] #command without channel
            new_dict = getattr(cls, command)(key, value, smu_references=smu_references)
            ret = {**ret, **new_dict}
        return ret

    @staticmethod
    def to_dict(parameters, names, *args):
        """ Takes parameters returned by ``query_learn`` and ordered list 
        of corresponding parameter names (optional function) and returns
        dict of parameters including names.
        
        :param parameters: Parameters for one command returned by ``query_learn``
        :type parameters: dict
        :param names: list of names or (name, function) tuples, ordered
        :type names: list
        :return: Parameter name and (processed) parameter
        :rtype: dict
        """
        ret = {}
        if isinstance(parameters, str):
            #otherwise string is enumerated
            parameters_iter = [(0, parameters)]
        else:
            parameters_iter = enumerate(parameters)
        for i, parameter in parameters_iter:
            if isinstance(names[i], tuple):
                ret[names[i][0]] = names[i][1](parameter,*args)
            else:
                ret[names[i]] = parameter
        return ret

    @classmethod
    def to_dict_channel(cls, key, parameters, names, key_string='{}', smu_references={}):
        """ Extension of ``to_dict`` to extract channel from command and look
        up corresponding SMU reference
        
        :param key: Command key of parameter dict, e.g. ``DI2``
        :type key: str
        :param key_string: String to construct key for return value, may contain ``{}`` to insert channel
        :type names: str
        :param smu_references: Dict of Channels and SMU references
        :type smu_references: dict
        :return: Dict of dict with ``key_string`` as key
        """
        smu = cls._get_smu(key, smu_references)
        ret = cls.to_dict(parameters, names, smu)
        return {key_string.format(smu.name):ret}
    
    @staticmethod
    def _get_smu(key, smu_references):
        command = re.findall(r'(?P<command>[A-Z]+)', key)[0] #command without channel
        channel = key[len(command):]
        return smu_references[int(channel)]

    #Instrument Settings: 31
    @classmethod
    def TM(cls, key, parameters, smu_references={}):
        names = ['Trigger Mode'] #enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def AV(cls, key, parameters, smu_references={}):
        names = ['ADC Averaging Number', ('ADC Averaging Mode', lambda parameter:str(AutoManual(int(parameter))))]
        return cls.to_dict(parameters, names)
    
    @classmethod
    def CM(cls, key, parameters, smu_references={}):
        names = ['Auto Calibration Mode'] #enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def FMT(cls, key, parameters, smu_references={}):
        names = ['Output Data Format','Output Data Mode'] #enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def MM(cls, key, parameters, smu_references={}):
        names = [('Measurement Mode', lambda parameter: str(MeasMode(int(parameter))))]
        ret = cls.to_dict(parameters[0], names)
        smu_names = []
        for channel in parameters[1:]:
            smu_names.append(smu_references[int(channel)].name)
        ret['Measurement Channels'] = ', '.join(smu_names)
        return ret

    #Measurement Ranging: 32
    @classmethod
    def RI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + ' Current Measurement Range', lambda parameter: smu.current_ranging.meas(int(parameter)).name)]
        return cls.to_dict(parameters, names)

    @classmethod
    def RV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + ' Voltage Measurement Range', lambda parameter: smu.voltage_ranging.meas(int(parameter)).name)]
        return cls.to_dict(parameters, names)
    
    #Sweep: 33
    @classmethod
    def WM(cls, key, parameters, smu_references={}):
        names = [('Auto Abort Status', lambda parameter: {2:True,1:False}[int(parameter)]), 
        ('Output after Measurement', lambda parameter: str(StaircaseSweepPostOutput(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def WT(cls, key, parameters, smu_references={}):
        names = ['Hold Time (s)', 'Delay Time (s)', 'Step Delay Time (s)', 'Step Source Trigger Delay Time (s)', 'Step Measurement Trigger Delay Time (s)']
        return cls.to_dict(parameters, names)

    @classmethod
    def WV(cls, key, parameters, smu_references={}):
        names = [
            ("Sweep Mode", lambda parameter, smu: str(SweepMode(int(parameter)))),
            ("Voltage Range", lambda parameter, smu: smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)", "Stop Voltage (V)", "Number of Steps",
            "Current Compliance (A)", "Power Compliance (W)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Voltage Sweep Source (WV)", smu_references=smu_references)

    @classmethod
    def WI(cls, key, parameters, smu_references={}):
        names = [
            ("Sweep Mode", lambda parameter, smu: str(SweepMode(int(parameter)))),
            ("Current Range", lambda parameter, smu: smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)", "Stop Current (A)", "Number of Steps",
            "Voltage Compliance (V)", "Power Compliance (W)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Current Sweep Source (WI)", smu_references=smu_references)

    @classmethod
    def WSV(cls, key, parameters, smu_references={}):
        names = [
            ("Voltage Range", lambda parameter, smu: smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)", "Stop Voltage (V)",
            "Current Compliance (A)", "Power Compliance (W)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Synchronous Voltage Sweep Source (WSV)", smu_references=smu_references)

    @classmethod
    def WSI(cls, key, parameters, smu_references={}):
        names = [("Current Range", lambda parameter, smu: smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)", "Stop Current (A)",
            "Voltage Compliance (V)", "Power Compliance (W)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Synchronous Current Sweep Source (WSI)", smu_references=smu_references)
    
    #SMU Measurement Operation Mode: 46
    @classmethod
    def CMM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + ' Measurement Operation Mode', lambda parameter: str(MeasOpMode(int(parameter))))]
        return cls.to_dict(parameters, names)

    #Sampling: 47
    @classmethod
    def MSC(cls, key, parameters, smu_references={}):
        names = [('Auto Abort Status', lambda parameter: {2:True,1:False}[int(parameter)]), 
        ('Output after Measurement', lambda parameter: str(SamplingPostOutput(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def MT(cls, key, parameters, smu_references={}):
        names = ['Hold Bias Time (s)', 'Sampling Interval (s)', 'Number of Samples', 'Hold Base Time (s)']
        return cls.to_dict(parameters, names)

    @classmethod
    def ML(cls, key, parameters, smu_references={}):
        names = [('Sampling Mode', lambda parameter: str(SamplingMode(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def MV(cls, key, parameters, smu_references={}):
        names = [("Voltage Range", lambda parameter, smu: smu.voltage_ranging.output(int(parameter)).name),
            "Base Voltage (V)", "Bias Voltage (V)", "Current Compliance (A)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Voltage Source (MV)", smu_references=smu_references)

    @classmethod
    def MI(cls, key, parameters, smu_references={}):
        names = [("Current Range", lambda parameter, smu: smu.current_ranging.output(int(parameter)).name),
            "Base Current (A)", "Bias Current (A)", "Voltage Compliance (V)"]
        return cls.to_dict_channel(
            key, parameters, names, key_string="{}: Current Source (MI)", smu_references=smu_references)

    #SMU Series Resistor: 53
    @classmethod
    def SSR(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + ' Series Resistor', lambda parameter: bool(int(parameter)))]
        return cls.to_dict(parameters, names)

    #Auto Ranging Mode: 54
    @classmethod
    def RM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [smu.name + ' Ranging Mode', smu.name + ' Ranging Mode Parameter']
        return cls.to_dict(parameters, names)

    #ADC: 55, 56
    @classmethod
    def AAD(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + ' ADC', lambda parameter: str(ADCType(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def AIT(cls, key, parameters, smu_references={}):
        adc_type = key[3:]
        adc_name = str(ADCType(int(adc_type)))
        names = [(adc_name + ' Mode', lambda parameter:str(ADCMode(int(parameter)))),
            adc_name + ' Parameter']
        return cls.to_dict(parameters, names)

    @classmethod
    def AZ(cls, key, parameters, smu_references={}):
        names = [('ADC Auto Zero', lambda parameter: str(bool(int(parameter))))]
        return cls.to_dict(parameters, names)



######################################
# Agilent B1500 Mainframe
######################################

class AgilentB1500(Instrument):
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
        self._smu_references = {}
        #setting of data output format -> determines how to read measurement data
        self._data_format = self._data_formatting("FMT"+self.query_data_format()[0])

    def query_learn(self, query_type):
        return QueryLearn.query_learn(self.ask, query_type)

    def query_learn_header(self, query_type, **kwargs):
        return QueryLearn.query_learn_header(self.ask, query_type, self._smu_references, **kwargs)

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
                    out[i+1] = module_names[module[0]] # i+1: channels start at 1 not at 0
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
        if channel in list(range(101,1101,100))+list(range(102,1102,100)):
            channel = int(str(channel)[0:-2]) #subchannels not relevant for SMU/CMU
        channel = strict_discrete_set(channel,range(1,11))
        self._smu_names[channel] = name
        smu_reference = SMU(self.adapter, channel, smu_type, name)
        self._smu_references[channel] = smu_reference
        return smu_reference

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

    @property
    def auto_calibration(self):
        """ Enable/Disable SMU auto-calibration every 30 minutes. (``CM``)"""
        response = self.query_learn(31)['CM']
        response = bool(int(response))
        return response

    @auto_calibration.setter
    def auto_calibration(self, setting):
        setting = int(setting)
        self.write('CM %d' % setting)
        self.check_errors()

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
            channel = channel[0:-2] # subchannels not relevant for SMU/CMU
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

    @property
    def parallel_measurement(self):
        """ Enable/Disable parallel measurements.
            Effective for SMUs using HSADC and measurement modes 1,2,10,18. (``PAD``)
        """
        response = self.query_learn(110)['PAD']
        response = bool(int(response))
        return response
    
    @parallel_measurement.setter
    def parallel_measurement(self, setting):
        setting = int(setting)
        self.write('PAD %d' % setting)
        self.check_errors()

    def query_meas_settings(self):
        """Read settings for ``TM``, ``AV``, ``CM``, ``FMT`` and ``MM`` commands from the isntrument.
        """
        return self.query_learn_header(31)
    
    def query_meas_mode(self):
        return self.query_learn_header(31, single_command='MM')

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
        mode = MeasMode.get(mode)
        cmd = "MM %d" % mode.value
        for smu in args:
            if isinstance(smu, SMU):
                cmd += ", %d" % smu.channel
        self.write(cmd)
        self.check_errors()

    # ADC Setup: AAD, AIT, AV, AZ

    def query_adc_setup(self):
        """Read ADC settings from the intrument.
        """
        return {**self.query_learn_header(55), **self.query_learn_header(56)}


    def adc_setup(self,adc_type,mode,N=''):
        """ Set up operation mode and parameters of ADC for each ADC type. (``AIT``)
        Defaults:

            - HSADC: Auto N=1, Manual N=1, PLC N=1, Time N=0.000002(s)
            - HRADC: Auto N=6, Manual N=3, PLC N=1
        
        :param adc_type: ADC type (``'HSADC','HRADC','HSADC_PULSED'``)
        :type adc_type: str
        :param mode: ADC mode (``'Auto','Manual','PLC','Time'``)
        :type mode: str
        :param N: additional parameter, check documentation, defaults to ''
        :type N: str, optional
        """
        
        adc_type = ADCType.get(adc_type)
        mode = ADCMode.get(mode)
        if (adc_type == ADCType['HRADC']) and (mode == ADCMode['Time']):
            raise ValueError("Time ADC mode is not available for HRADC")
        command = "AIT %d, %d" % (mode.value, adc_type.value)
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
            mode = AutoManual.get(mode).value
            self.write("AV %d, %d" % (number,mode))
        else:
            number = strict_range(number,range(-1,-101,-1))
            self.write("AV %d" % number)
        self.check_errors()

    @property
    def adc_auto_zero(self):
        """ Enable/Disable ADC zero function. Halfs the integration time, if off. (``AZ``)"""
        response = self.query_learn(56)['AZ']
        response = bool(int(response))
        return response

    @adc_auto_zero.setter
    def adc_auto_zero(self, setting):
        setting = int(setting)
        self.write('AZ %d' % setting)
        self.check_errors()

    ######################################
    # Sweep Setup
    ######################################

    def query_staircase_sweep_settings(self):
        """Reads Staircase Sweep Measurement settings from the instrument.
        Returns dict, values may not be used to set up measurement, but for 
        information/documentation purposes. (Human Readable)
        """
        return self.query_learn_header(33)
        

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
        abort = strict_discrete_set(abort,abort_values)
        abort = abort_values[abort]
        post = StaircaseSweepPostOutput.get(post)
        self.write("WM %d, %d" % (abort, post.value))
        self.check_errors()

    ######################################
    # Sampling Setup
    ######################################

    def query_sampling_settings(self):
        """Reads Sampling Measurement settings from the instrument.
        Returns dict, values may not be used to set up measurement, but for 
        information/documentation purposes. (Human Readable)
        """
        return self.query_learn_header(47)

    @property
    def sampling_mode(self):
        """ Set linear or logarithmic sampling mode. (``ML``)"""
        response = self.query_learn(47)
        response = response['ML']
        return SamplingMode(response)

    @sampling_mode.setter
    def sampling_mode(self, mode):
        mode = SamplingMode.get(mode).value
        self.write("ML %d" % mode)
        self.check_errors()

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
        post = SamplingPostOutput.get(post).value
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

class SMU(object):
    """ Provides specific methods for the SMUs of the Agilent B1500 mainframe
    
    :param resourceName: Resource name of the B1500 mainframe
    :param int channel: Channel number of the SMU
    :param str smu_type: Type of the SMU
    """

    def __init__(self, adapter, channel, smu_type, name, **kwargs):
        self.adapter = adapter
        channel = strict_discrete_set(channel,range(1,11))
        self.channel = channel
        smu_type = strict_discrete_set(smu_type,['HRSMU','MPSMU','HPSMU','MCSMU',
            'HCSMU','DHCSMU','HVSMU','UHCU','HVMCU','UHVU'])
        self.voltage_ranging = SMUVoltageRanging(smu_type)
        self.current_ranging = SMUCurrentRanging(smu_type)
        self.name = name

    ##########################################
    # Wrappers of B1500 communication methods
    ##########################################
    def write(self, string):
        """Wraps ``write`` method of B1500.
        """
        self.adapter.write(string)

    def ask(self, string):
        """Wraps ``ask`` method of B1500.
        """
        return self.adapter.ask(string)

    def query_learn(self, query_type, command):
        """Wraps ``query_learn`` method of B1500.
        """
        response = QueryLearn.query_learn(self.ask, query_type)
        # query_learn returns settings of all smus
        # pick setting for this smu only
        response = response[command + self.channel]
        return response

    def check_errors(self):
        """Wraps ``check_errors`` method of B1500.
        """
        return self.adapter.check_errors()
    ##########################################

    def query_status(self):
        return QueryLearn.query_learn(self.ask, str(self.channel))

    def enable(self):
        """ Enable Source/Measurement Channel (``CN``)"""
        self.write("CN %d" % self.channel)
    
    def disable(self):
        """ Disable Source/Measurement Channel (``CL``)"""
        self.write("CL %d" % self.channel)

    def force_gnd(self):
        """ Force 0V immediately. Current Settings can be restored with ``RZ``. (``DZ``)"""
        self.write("DZ %d" % self.channel)

    @property
    def filter(self):
        """ Enables/Disables SMU Filter. (``FL``)"""
        response = self.adapter.query_learn(30)
        if 'FL' in response.keys():
            #only present if filter of all channels are off
            return False
        else:
            if str(self.channel) in response['FL0']:
                return False
            elif str(self.channel) in response['FL1']:
                return True
            else:
                raise NotImplementedError('Filter Value cannot be read!')

    @filter.setter
    def filter(self, setting):
        setting = strict_discrete_set(int(setting),(0,1))
        self.write("FL %d, %d" % (self.channel, setting))
        self.check_errors()

    @property
    def series_resistor(self):
        """ Enables/Disables 1MOhm series resistor. (``SSR``)"""
        response = self.query_learn(53, 'SSR')
        response = bool(int(response))
        return response

    @series_resistor.setter
    def series_resistor(self, setting):
        setting = strict_discrete_set(int(setting),(0,1))
        self.write("SSR %d, %d" % (self.channel, setting))
        self.check_errors()

    @property
    def meas_op_mode(self):
        """ Set SMU measurement operation mode. (``CMM``)
            
        Possible values: ``"Compliance Side","Current","Voltage","Force Side","Compliance and Force Side"``
        """
        response = self.query_learn(46, 'CMM')
        response = int(response)
        return MeasOpMode(response)

    @meas_op_mode.setter
    def meas_op_mode(self, op_mode):
        if isinstance(op_mode, int):
            op_mode = ADCType(op_mode)
        else:
            op_mode = ADCType[op_mode]
        self.write("CMM %d, %d" % (self.channel, op_mode.value))
        self.check_errors()


    @property
    def adc_type(self):
        """ADC type of individual measurement channel. (``AAD``)

        Possible values: ``'HSADC','HRADC','HSADC_PULSED'``
        """
        response = self.query_learn(55, 'AAD')
        response = int(response)
        return ADCType(response)

    @adc_type.setter
    def adc_type(self, adc_type):
        if isinstance(adc_type, int):
            adc_type = ADCType(adc_type)
        else:
            adc_type = ADCType[adc_type]
        self.write("AAD %d, %d" % (self.channel, adc_type.value))
        self.check_errors()


    @property
    def meas_range_current(self):
        """ Current measurement range index. (``RI``)

        Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging.
        """
        response = self.query_learn(32, 'RI')
        response = self.current_ranging.meas(response)
        return response

    @meas_range_current.setter
    def meas_range_current(self, meas_range):
        meas_range_index = self.current_ranging.meas(meas_range).index
        self.write("RI %d, %d" % (self.channel, meas_range_index))
        self.check_errors()
    
    @property
    def meas_range_voltage(self):
        """ Voltage measurement range index. (``RV``)

            Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging.
        """
        response = self.query_learn(32, 'RV')
        response = self.voltage_ranging.meas(response)
        return response

    @meas_range_voltage.setter
    def meas_range_voltage(self, meas_range):
        meas_range_index = self.voltage_ranging.meas(meas_range).index
        self.write("RV %d, %d" % (self.channel, meas_range_index))
        self.check_errors()

    


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
        irange = self.current_ranging.output(irange).index
        output = "DI " + self.channel + (", %d, %f" % (irange, current))
        if not Vcomp == '':
            output += ", %f" % Vcomp
            if not comp_polarity == '':
                output += ", %d" % comp_polarity
                if not vrange == '':
                    output += ", %d" % vrange
                    vrange = self.voltage_ranging.output(vrange).index
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
        irange = self.current_ranging.output(irange).index
        status = self.query_status()
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
        vrange = self.voltage_ranging.output(vrange).index
        output = "DV " + self.channel + (", %d, %f" % (vrange, voltage))
        if not Icomp == '':
            output += ", %f" % Icomp
            if not comp_polarity == '':
                output += ", %d" % comp_polarity
                if not irange == '':
                    output += ", %d" % irange
                    irange = self.current_ranging.output(irange).index
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
        vrange = self.voltage_ranging.output(vrange).index
        status = self.query_status()
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
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "WI"
            source_range = self.current_ranging.output(source_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        mode = SweepMode.get(mode).value
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
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "WSI"
            source_range = self.current_ranging.output(source_range).index
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
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "MI"
            source_range = self.current_ranging.output(source_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        #check on comp value not yet implemented
        self.write(cmd + ("%d, %d, %f, %f, %f" % (self.channel,source_range,base,bias,comp)))
        self.check_errors()

class Ranging():
    """ Possible Settings for SMU Current/Voltage Output/Measurement ranges.
    Transformation of available Voltage/Current Range Names to Index and back.
    Checks for compatibility with specified SMU type.
    
    :param str smu_type: SMU type
    :param str source_type: Source type, defaults to 'Voltage'
    :param str ranging_type: Ranging type, defaults to 'Output'
    """
    
    Range = namedtuple('Range','name index')

    def __init__(self, supported_ranges, all_ranges, measurement=False):
        inverse = {}
        for k, v in all_ranges.items():
            if isinstance(v, tuple):
                for v2 in v:
                    inverse[v2] = k
            else:
                inverse[v] = k
        #inverse = {v: k for k, v in all_ranges.items()}
        ranges = {}
        indizes = {}
        for i in supported_ranges:
            ranges[i] = inverse[i] # Index -> Name, Name not unique
            indizes[inverse[i]] = i # Name -> Index, only one Index per Name

        self.indizes = indizes
        self.ranges = ranges
        self.ranging_type_measurement = measurement
    
    def __call__(self, input, fixed=False):
        """Gives named tuple (name/index) of given Range. 
        Throws error if range is not supported by this SMU.
        
        :param input: Range name or index
        :type input: str or int
        :param fixed: Fixed measurement range, defaults to False (limited auto ranging)
        :type fixed: bool, optional
        :return: named tuple (name/index) of range
        :rtype: namedtuple
        """
        if isinstance(input, int):
            index = input
            name = self._get_name(index)
        else:
            name = input
            index = self._get_index(name, fixed=fixed)
        return self.Range(name=name, index=index)

    def _get_index(self, range_name, fixed=False):
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
                'Specified Range Name {} is not valid or not supported by this SMU'.format(range_name)
            )
        if self.ranging_type_measurement:
            if fixed:
                index = -1 * index
        return index

    def _get_name(self, index):
        """ Give range name of given index
        
        :param index: Range index
        :type index: int
        :return: Range name
        :rtype: str
        """
        try:
            range_name = self.ranges[abs(index)]
        except:
            raise ValueError(
                'Specified Range {} is not supported by this SMU'.format(abs(index))
            )
        if self.ranging_type_measurement:
            ranging_type = ''  # auto ranging: 0
            if index < 0:
                ranging_type = ' range fixed'
            elif index > 0:
                ranging_type = ' limited auto ranging'
            range_name += ranging_type
        return range_name

class SMUVoltageRanging():
    def __init__(self, smu_type):
        supported_ranges = {
                'HRSMU': [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
                'MPSMU': [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
                'HPSMU': [0, 11, 20, 12, 200, 13, 400, 14, 1000, 15, 2000],
                'MCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
                'HCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
                'DHCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
                'HVSMU': [0, 15, 2000, 5000, 15000, 30000],
                'UHCU': [0, 14, 1000],
                'HVMCU': [0, 15000, 30000],
                'UHVU': [0, 103]
                }
        supported_ranges = supported_ranges[smu_type]
        output_ranges = {
            'Auto Ranging': 0,
            '0.2 V limited auto ranging': 2,
            '0.5 V limited auto ranging': 5,
            '2 V limited auto ranging': (11, 20),
            #'2 V limited auto ranging': 20,  # or 11
            '5 V limited auto ranging': 50,
            '20 V limited auto ranging': (12, 200),
            #'20 V limited auto ranging': 200,  # or 12
            '40 V limited auto ranging': (13, 400),
            #'40 V limited auto ranging': 400,  # or 13
            '100 V limited auto ranging': (14, 1000),
            #'100 V limited auto ranging': 1000,  # or 14
            '200 V limited auto ranging': (15, 2000),
            #'200 V limited auto ranging': 2000,  # or 15
            '500 V limited auto ranging': 5000,
            '1500 V limited auto ranging': 15000,
            '3000 V limited auto ranging': 30000,
            '10 kV limited auto ranging': 103
            }   
        meas_ranges = {
            'Auto Ranging': 0,
            '0.2 V': 2,
            '0.5 V': 5,
            '2 V': (11, 20),
            #'2 V': 20,  # or 11
            '5 V': 50,
            '20 V': (12, 200),
            #'20 V': 200,  # or 12
            '40 V': (13, 400),
            #'40 V': 400,  # or 13
            '100 V': (14, 1000),
            #'100 V': 1000,  # or 14
            '200 V': (15, 2000),
            #'200 V': 2000,  # or 15
            '500 V': 5000,
            '1500 V': 15000,
            '3000 V': 30000,
            '10 kV': 103
            }
        self.output = Ranging(supported_ranges, output_ranges)
        self.meas = Ranging(supported_ranges, meas_ranges, measurement=True)

class SMUCurrentRanging():
    def __init__(self, smu_type):
        supported_output_ranges = {
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
        supported_output_ranges = supported_output_ranges[smu_type]
        output_ranges = {
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
        supported_meas_ranges = {
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
        supported_meas_ranges = supported_meas_ranges[smu_type]
        meas_ranges = {
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
        self.output = Ranging(supported_output_ranges, output_ranges)
        self.meas = Ranging(supported_meas_ranges, meas_ranges, measurement=True)

class CustomIntEnum(IntEnum):
    """Provides additional methods to IntEnum:
    - Conversion to string automatically replaces '_' with ' ' in names and converts to title case
    - get classmethod to get enum reference with name or integer
    """
    def __str__(self):
        return self.name.replace("_", " ").title()

    @classmethod
    def get(cls, input_value):
        """Give Enum member by specifying name or value.
        
        :param input_value: Enum name or value
        :type input_value: str or int
        :return: Enum member
        """
        if isinstance(input_value, int):
            return cls(input_value)
        else:
            return cls[input_value.upper()]

class ADCType(CustomIntEnum):
    HSADC = 0
    HRADC = 1
    HSADC_PULSED =2

    def __str__(self):
        return self.name.replace("_", " ") #.title()

class ADCMode(CustomIntEnum):
    AUTO = 0
    MANUAL = 1
    PLC = 2
    TIME = 3

class AutoManual(CustomIntEnum):
    AUTO = 0
    MANUAL = 1

class MeasMode(CustomIntEnum):
    SPOT = 1
    STAIRCASE_SWEEP = 2
    SAMPLING = 10

class MeasOpMode(CustomIntEnum):
    COMPLIANCE_SIDE = 0
    CURRENT = 1
    VOLTAGE = 2
    FORCE_SIDE = 3
    COMPLIANCE_AND_FORCE_SIDE = 4

class SweepMode(CustomIntEnum):
    LINEAR_SINGLE = 1
    LOG_SINGLE = 2
    LINEAR_DOUBLE = 3
    LOG_DOUBLE = 4

class SamplingMode(CustomIntEnum):
    LINEAR = 1
    LOG_10 = 2
    LOG_25 = 3
    LOG_50 = 4
    LOG_100 = 5
    LOG_250 = 6
    LOG_5000 = 7

    def __str__(self):
        names = {1:"Linear",
        2:"Log 10 data/decade",3:"Log 25 data/decade",4:"Log 50 data/decade",
        5:"Log 100 data/decade",6:"Log 250 data/decade",7:"Log 5000 data/decade"}
        return names[self.value]

class SamplingPostOutput(CustomIntEnum):
    BASE = 1
    BIAS = 2

class StaircaseSweepPostOutput(CustomIntEnum):
    START = 1
    STOP = 2