#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

WL_RANGE = [1480,1620]

class N7776C(Instrument):
    """
    This represents the Keysight N7776C Tunable Laser Source interface
    .. code-block:: python
        laser = N7776C( address )
    
    """
    def __init__(self, address, **kwargs):
        super(N7776C, self).__init__(
            address, "N7776C Tunable Laser Source",**kwargs)

    def reset(self):
        self.write('*RST')

    def set_power(self,value,unit='mW'):
        if not unit in ['dBm','mW']:
            raise ValueError('Unknown Power Unit.')

        self._output_power_unit = unit.lower()
        self.output_power = value

    def get_power(self,unit_output=False):
        power_reading = self._output_power
        power_unit = self._output_power_unit
        if unit_output:
            return (power_reading,power_unit)
        else:
            return power_reading



    output = Instrument.control('SOUR0:POW:STAT?','SOUR0:POW:STAT %g',
                                    """ Boolean Property that controls the state (on/off) of the laser source """,
                                    validator=strict_discrete_set,
                                    values=[True,False],
                                    set_process=lambda v: int(v),
                                    get_process=lambda v: bool(v))




    _output_power = Instrument.control('SOUR0:POW?','SOUR0:POW %f',
                                    """ Floating point value indicating the laser output power in the unit set by the user (see _output_power_unit).""")
    _output_power_unit = Instrument.control('SOUR0:POW?','SOUR0:POW %f',
                                    """ String parameter controlling the power unit used internally by the laser.""",
                                    map_values=True,
                                    values={'dBm':0,'mW':1})

    trigger_out = Instrument.control('TRIG0:OUTP?','TRIG0:OUTP %s',
                                    """ Specifies if and at which point in a sweep cycle an output trigger is generated and arms the module. """,
                                    validator=strict_discrete_set,
                                    values=['DIS','STF','SWF','SWST'])
    trigger_in = Instrument.control('TRIG0:INP?','TRIG0:INP %s',
                                    """ Sets the incoming trigger response and arms the module. """,
                                    validator=strict_discrete_set,
                                    values=['IGN','NEXT','SWS'])

    sweep_wl_start = Instrument.control('sour0:wav:swe:star?','sour0:wav:swe:star %fnm',
                                    """ Start Wavelength (in nanometers) for a sweep.""",
                                    validator=strict_range,
                                    values=WL_RANGE)
    sweep_wl_stop = Instrument.control('sour0:wav:swe:stop?','sour0:wav:swe:stop %fnm',
                                    """ End Wavelength (in nanometers) for a sweep.""",
                                    validator=strict_range,
                                    values=WL_RANGE)

    sweep_step = Instrument.control('sour0:wav:swe:step?','sour0:wav:swe:step %fnm',
                                    """ Step width of th[e sweep (in nanometers).""",
                                    validator=strict_range,
                                    values=[0.0001,WL_RANGE[1]-WL_RANGE[0]])
    sweep_speed = Instrument.control('sour0:wav:swe:speed?','sour0:wav:swe:speed %fnm/s',
                                    """ Speed of the sweep (in nanometers per second).""",
                                    validator=strict_discrete_set,
                                    values=[0.5,1,50,80,200]) #TODO: Get Real values
    sweep_mode = Instrument.control('sour0:wav:swe:mode?','sour0:wav:swe:mode %s',
                                    """ Sweep mode of the swept laser source """,
                                    validator=strict_discrete_set,
                                    values=['STEP','MAN','CONT'])
    _sweep_check = Instrument.measurement('sour0:wav:swe:chec?',
                                    """Returns whether the currently set sweep parameters (sweep mode, sweep start, stop, width, etc.) are consistent. If there is a
                                    sweep configuration problem, the laser source is not able to pass a wavelength sweep.""")
    sweep_points = Instrument.measurement('sour0:read:points? llog',
                                    """Returns the number of datapoints that the :READout:DATA? command will return.""")
    sweep = Instrument.control('sour0:wav:swe?','sour0:wav:swe %g',""" State of the wavelength sweep. Stops, starts, pauses or continues a wavelength sweep.""")

    wl_logging = Instrument.control('SOUR0:WAV:SWE:LLOG?','SOUR0:WAV:SWE:LLOG %g',""" State (on/off) of the lambda logging feature of the laser source.""")


    def get_wl_data(self):
        return np.array(self.adapter.connection.query_binary_values('sour0:read:data? llog',datatype=u'd'))    

    def close(self):
        self.adapter.connection.close()