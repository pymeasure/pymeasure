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
from pymeasure.adapters import VISAAdapter


class RigolDG4000(Instrument):
    """Represents any Rigol DG4000 series function generator
    """
    current_settings = ({
        'frequency':1000,
        'amplitude':5,
        'offset':0,
        'phase':0,
        'delay':0
        })

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

    def display_sreen_saver_now(self):
        self.write(":DISPlay:SAVer:IMMediate")

    def source_apply(self,channel,**kwargs):
        std_parameters = ['frequency','amplitude','offset','phase']

        # Need to accomodate different limits vs function and instrument.
        allowed_parameter_values =({
            'frequency':[1e-6,60e6],
            'amplitude':[1e-3,10],
            'offset':[-5,5],
            'phase':[0,360],
            'delay':[0,360]
        })

        allowed_waveform_parameters = ({
            'CUSTom':std_parameters,
            'HARMonic':std_parameters,
            'NOISe':['amplitude','offset'],
            'PULSe':['frequency','amplitude','offset','delay'],
            'RAMP':std_parameters,
            'SINusoid':std_parameters,
            'SQUare':std_parameters,
            'USER':std_parameters
        })
        list_or_floats = joined_validators(strict_discrete_set, strict_range)
        allowed_waveforms = ['CUSTom', 'HARMonic', 'NOISe', 'PULSe', 'RAMP', 'SINusoid', 'SQUare', 'USER','CUST', 'HARM', 'NOIS', 'PULS', 'SIN', 'SQU']
        if 'waveform' in kwargs:
            waveform = strict_discrete_set(kwargs['waveform'],allowed_waveforms)
            command = f":SOURce{channel}:APPLy:{kwargs['waveform']} "
            for parameter in allowed_waveform_parameters[waveform]:
                if parameter in kwargs:
                    parameter_value = list_or_floats(kwargs[parameter],[["MIN","MAX"] ,allowed_parameter_values[parameter]])
                    command = command +f"{parameter_value},"
                else:
                    command = command + f"{self.current_settings[parameter]},"
        command = command[0:-1]
        self.write(command)

        for parameter in allowed_waveform_parameters[waveform]:
            self.current_settings[parameter] = kwargs[parameter]
