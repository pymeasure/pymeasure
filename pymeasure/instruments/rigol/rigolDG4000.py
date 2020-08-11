#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range,
    joined_validators
)


class Output(object):
    list_or_floats = joined_validators(strict_discrete_set, strict_range)

    impedance = Instrument.control(
        'IMPedance?','IMPedance %s',
        """Set output impedance between 1 to 10k Ohms""",
        validator=strict_range,
        values=[1,10000]
    )

    #This seems to be the same as impedance
    load = Instrument.control(
        'LOAD?','LOAD %s',
        """Set output load between 1 to 10k Ohms""",
        validator=strict_range,
        values=[1,10000]
    )

    noise_scale = Instrument.control(
        "NOISe:SCALe?","NOISe:SCALe %s",
        """Set/Query the scale of the noise superimposed on the output""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[0,50]]
    )

    noise_state = Instrument.control(
        "NOISe:STATe?","NOISe:STATe %s",
        """ Enable/Disable the noise super imposed on the output channel""",
        validator=strict_discrete_set,
        values=["ON","OFF"]
    )

    polarity = Instrument.control(
        "POLarity?","POLarity %s",
        """Set/Query the signal polarity on the output""",
        validator=strict_discrete_set,
        values = ["NORMal","NORM","INVerted","INV"]
    )

    state = Instrument.control(
        "STATe?","STATe %s",
        """ Enable/Disable the output channel""",
        validator=strict_discrete_set,
        values=["ON","OFF"]
    )

    sync_polarity = Instrument.control(
        "SYNC:POLarity?","SYNC:POLarity %s",
        """Set/Query the signal polarity of the outputs SYNC connector""",
        validator=strict_discrete_set,
        values=["POSitive", "POS","NEGative","NEG"]
    )

    sync_state = Instrument.control(
        "SYNC:STATe?","SYNC:STATe %s",
        """Set/Query the state of the outputs SYNC signal""",
        validator=strict_discrete_set,
        values = ["ON","OFF"]
    )

    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel
    
    def ask(self,command):
        return self.instrument.ask(":OUTPut{channel}:{cmd}".format(channel = self.channel, cmd=command))
        
    def write(self, command):
        self.instrument.write(":OUTPut{channel}:{cmd}".format(channel = self.channel,cmd=command))

    def read(self, command):
        return self.instrument.read(":OUTPut{channel}:{cmd}".format(channel = self.channel, cmd=command))

    def values(self, command, **kwargs):
        return self.instrument.values(":OUTPut{channel}:{cmd}".format(channel = self.channel, cmd=command),**kwargs)
class Channel(object):
    list_or_floats = joined_validators(strict_discrete_set, strict_range)


#region SOURce:BURSt MODES

    burst_gate_polarity = Instrument.control(
        "BURSt:GATE:POLarity?","BURSt:GATE:POLarity %s",
        """Set the channel to output a busrt when gated by the signal on the instruments Mod/FSK/Trig rear connector""",
        validator=strict_discrete_set,
        values=["NORMal","NORM","INVerted","INV"]
    )

    burst_internal_period = Instrument.control(
        "BURSt:INTernal:PERiod?","BURSt:INTernal:PERiod %s",
        """Set the occurance rate of an N cycle burst of what ever the current waveform is""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[0,50]]
    ) #TODO: Set proper range limit > 1us + waveform period * N

    burst_mode = Instrument.control(
        "BURSt:MODE?","BURSt:MODE %s",
        """Set the burst type to N Cycle, gated or infinite""",
        validator=strict_discrete_set,
        values=["TRIGgered","TRIG","GATed","GAT","INFinity","INF"]
    )

    burst_cycles = Instrument.control(
        "BURSt:NCYCles?","BURSt:NCYCles %s",
        """Set/Query the number of cycles in the burst""",
        validator = list_or_floats,
        values = [["MIN","MAX","MINimum","MAXimum"],[1,5e5]]
    ) #TODO: Get range as a function of trigger source (int vs ext)

    burst_phase = Instrument.control(
        "BURSt:PHASe?","BURSt:PHASe %s",
        """Set/Query the phase angle for when to start the burst""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[0,360]]
    )

    burst_state = Instrument.control(
        "BURSt:STATe?","BURSt:STATe %s",
        """Enable/Disable/Query Burst functionality""",
        validator=strict_discrete_set,
        values = ["ON","OFF"]
    )

    burst_delay = Instrument.control(
        "BURSt:DELay?","BURSt:DELay %s",
        """Set/Query the delay between tigger and start of burst""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[0,85]]
    )#TODO: Upper limit is also constrained by waveform period when on internal trigger

    def burst_trigger_immediate(self):
        self.write("BURSt:TRIGger:IMMediate")

    burst_trigger_slope = Instrument.control(
        "BURSt:TIGger:SLOPe?","BURSt:TIGger:SLOPe %s",
        """Set/Query which edge of the external trigger signal should be used""",
        validator=strict_discrete_set,
        values=["POSitive","POS","NEGative","NEG"]
    )

    burst_trigger_source = Instrument.control(
        "BURSt:TRIGger:SOURce?","BURSt:TRIGger:SOURce %s",
        """Set/Query the trigger source""",
        validator=strict_discrete_set,
        values=["INTernal","INT","EXTernal","EXT","MANual","MAN"]
    )

    burst_trigger_out = Instrument.control(
        "BURSt:TRIGger:TRIGOut?","BURSt:TRIGger:TRIGOut %s",
        """Set/Query the edge type of the trigger output signal""",
        validator=strict_discrete_set,
        values=["OFF","POSitive","POS","NEGative","NEG"]
    )
#endregion

#region SOURce:FREQuency MODES
    frequency_sweep_center = Instrument.control(
        "FREQuency:CENTer?","FREQuency:CENTer %s",
        """Set/Query the center frequency of the sweep""",
        validator=strict_range,
        values=[1e-6,60e6]
    ) #TODO: Limits for other instruments in DG4000 family

    frequency_sweep_span = Instrument.control(
        "FREQuency:SPAN?","FREQuency:SPAN %s",
        """Set/Query the sweep span""",
        validator= list_or_floats,
        values = [["MIN","MAX","MINimum","MAXimum"],[1e-6,60e6]
    ) #TODO: Instrument dependent limit

    frequency_sweep_start_freq = Instrument.control(
        "FREQuency:STARt?","FREQuency:STARt %s",
        """Set/Query the start frequency""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[1e-6,60e6]
    ) #TODO: Instrument & waveform dependent limit

    frequency_sweep_stop_freq = Instrument.control(
        "FREQuency:STOP?","FREQuency:STOP %s",
        """Set/Query the stop frequency""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[1e-6,60e6]
    ) #TODO: Instrument & waveform dependent limit

    frequency = Instrument.control(
        "FREQuency:FIXed?","FREQuency:FIXed %s",
        """Set/Query the frequency of the base waveform""",
        validator = list_or_floats,
        values = [["MIN","MAX","MINimum","MAXimum"],[1e-6,60e6]]
    ) #TODO: Waveform dependent limits


#endregion


    def __init__(self, instrument,channel):
        self.instrument = instrument
        self.channel = channel
        self.output = Output(instrument, channel)
        self.channel_settings = ({
                            'waveform':'SINusoid'
                            'frequency':1000,
                            'amplitude':5,
                            'offset':0,
                            'phase':0,
                            'delay':0
                            })

    def ask(self,command):
        return self.instrument.ask(":SOURce{channel}:{cmd}".format(channel = self.channel, cmd=command))
        
    def write(self, command):
        self.instrument.write(":SOURce{channel}:{cmd}".format(channel = self.channel,cmd=command))

    def read(self, command):
        return self.instrument.read(":SOURce{channel}:{cmd}".format(channel = self.channel, cmd=command))

    def values(self, command, **kwargs):
        return self.instrument.values(":SOURce{channel}:{cmd}".format(channel = self.channel, cmd=command),**kwargs)

    def source_apply(self,**kwargs):
        allowed_waveform_parameters = ({
            'CUSTom':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,15e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                }),
            'HARMonic':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,30e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                }),
            'NOISe':(
                {
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]]
                }),
            'PULSe':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,15e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'delay':[["MIN","Minimum","MAX","MAXimum"],[1e-6,4e6]]
                }),
            'RAMP':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,1e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                }),
            'SINusoid':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,60e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                }),
            'SQUare':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,25e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                }),
            'USER':(
                {
                'frequency':[["MIN","Minimum","MAX","MAXimum"],[1e-6,15e6]],
                'amplitude':[["MIN","Minimum","MAX","MAXimum"],[1e-3,10]],
                'offset':[["MIN","Minimum","MAX","MAXimum"],[-5,5]],
                'phase':[["MIN","Minimum","MAX","MAXimum"],[0,360]]
                })
        })

        list_or_floats = joined_validators(strict_discrete_set, strict_range)
        allowed_waveforms =   ({'CUSTom':'CUSTom',
                                'CUST':'CUSTom', 
                                'HARMonic':'HARMonic', 
                                'HARM':'HARMonic', 
                                'NOISe':'NOISe', 
                                'NOIS':'NOISe', 
                                'PULSe':'PULSe', 
                                'PULS':'PULSe', 
                                'RAMP':'RAMP', 
                                'SINusoid':'SINusoid',
                                'SIN':'SINusoid',  
                                'SQUare':'SQUare', 
                                'SQU':'SQUare',
                                'USER':'USER'
                                })
        if len(kwargs) == 0:
            return self.ask('APPLy?')

        if 'waveform' in kwargs:
            waveform = strict_discrete_set(kwargs['waveform'],allowed_waveforms)
            # Convert the user supplied waveform (1 of 2 ways to specify it) into 1 common type for internal use
            waveform_internal = allowed_waveforms[waveform]
            command = 'APPLy:{shape} '.format(shape=waveform_internal)
            for parameter in allowed_waveform_parameters[waveform_internal]:
                if parameter in kwargs:
                    allowed_parameter_values = allowed_waveform_parameters[waveform_internal][parameter]
                    parameter_value = list_or_floats(kwargs[parameter], allowed_parameter_values)
                    command = command +'{parameter_value},'.format(parameter_value=parameter_value)
                    self.channel_settings[parameter] = parameter_value
                else:
                    command = command + '{current_setting},'.format(current_setting=self.channel_settings[parameter])
        
        command = command[0:-1]
        self.write(command)


class RigolDG4000(Instrument):
    """Represents any Rigol DG4000 series function generator"""

    NVM_LOCATIONS = ['USER'+str(x) for x in range(1,11)]
    list_or_floats = joined_validators(strict_discrete_set,strict_range)

    id = Instrument.measurement(
        "*IDN?", """ Query the ID character string of the instrument. """
    )

    reset = Instrument.measurement(
        "*RST", """ Restore the instrument to its default state """
    )

    trigger = Instrument.measurement(
        "*TRG", """ Trigger the instrument to generate an output """
    )

    save_settings = Instrument.control(
        "", "*SAV %s",
        """Save the current instrument state to the specified storage location in NVM""",
        validator=strict_discrete_set,
        values=NVM_LOCATIONS
    )

    restore_settings = Instrument.control(
        "", "*RCL %s",
        """Restore instrument settings based on data in specified NVM storage location""",
        validator=strict_discrete_set,
        values=NVM_LOCATIONS
    )

    display_brightness = Instrument.control(
        ":DISPlay:BRIGhtness?",":DISPlay:BRIGhtness %s",
        """Set the brightness of the instruments display screen""",
        validator=list_or_floats,
        values=[["MIN","MAX","MINimum","MAXimum"],[1,100]]
    )

    display_screen_saver = Instrument.control(
        "DISPlay:SAVer:STATe?","DISPlay:SAVer:STATe %s",
        """Enable/Disable the instruments display screen saver""",
        validator=strict_discrete_set,
        values=["ON","OFF"]
    )

    def __init__(self, resourceName,**kwargs):
        super(RigolDG4000, self).__init__(
            resourceName,
            "Rigol DG4000",
            **kwargs
        )
        self.channel_settings = ({
                        1:({
                            'frequency':1000,
                            'amplitude':5,
                            'offset':0,
                            'phase':0,
                            'delay':0
                            }),
                        2:({
                            'frequency':1000,
                            'amplitude':5,
                            'offset':0,
                            'phase':0,
                            'delay':0
                            })
                        })
        self.ch1 = Channel(self,1)
        self.ch2 = Channel(self,2)

    def display_sreen_saver_now(self):
        self.write(":DISPlay:SAVer:IMMediate")

    