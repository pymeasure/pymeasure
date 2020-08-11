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

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number
    
    def ask(self,command):
        return self.instrument.ask("OUTPut{number}:{cmd}".format(number = self.number, cmd=command))
        
    def write(self, command):
        self.instrument.write(":OUTPut{number}:{cmd}".format(number = self.number,cmd=command))

    def read(self, command):
        return self.instrument.read("OUTPut{number}:{cmd}".format(number = self.number, cmd=command))

    def values(self, command, **kwargs):
        return self.instrument.values(":OUTPut{number}:{cmd}".format(number = self.number, cmd=command),**kwargs)
class Channel(object):
    def __init__(self, instrument,number):
        self.instrument = instrument
        self.number = number
        self.output = Output(instrument, number)


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
        self.current_channel = 1
        self.ch1 = Channel(self,1)
        self.ch2 = Channel(self,2)

    def display_sreen_saver_now(self):
        self.write(":DISPlay:SAVer:IMMediate")

    def source_apply(self,channel,**kwargs):
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
        if 'waveform' in kwargs:
            waveform = strict_discrete_set(kwargs['waveform'],allowed_waveforms)
            # Convert the user supplied waveform (1 of 2 ways to specify it) into 1 common type for internal use
            waveform_internal = allowed_waveforms[waveform]
            command = 'SOURce{channel}:APPLy:{shape} '.format(channel=channel, shape=waveform_internal)
            for parameter in allowed_waveform_parameters[waveform_internal]:
                if parameter in kwargs:
                    allowed_parameter_values = allowed_waveform_parameters[waveform_internal][parameter]
                    parameter_value = list_or_floats(kwargs[parameter], allowed_parameter_values)
                    command = command +'{parameter_value},'.format(parameter_value=parameter_value)
                    self.channel_settings[channel][parameter] = parameter_value
                else:
                    command = command + '{current_setting},'.format(current_setting=self.channel_settings[channel][parameter])
        
        self.current_channel = channel
        command = command[0:-1]
        self.write(command)