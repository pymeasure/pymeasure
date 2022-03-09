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
import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

WL_RANGE = [1480, 1620]
LOCK_PW = 1234


class KeysightN7776C(Instrument):
    """
    This represents the Keysight N7776C Tunable Laser Source interface.

    .. code-block:: python

        laser = N7776C(address)
        laser.sweep_wl_start = 1550
        laser.sweep_wl_stop = 1560
        laser.sweep_speed = 1
        laser.sweep_mode = 'CONT'
        laser.output_enabled = 1
        while laser.sweep_state == 1:
            log.info('Sweep in progress.')
        laser.output_enabled = 0

    """
    def __init__(self, address, **kwargs):
        super(KeysightN7776C, self).__init__(
            address, "N7776C Tunable Laser Source", **kwargs)

    locked = Instrument.control(':LOCK?', ':LOCK %g,'+str(LOCK_PW),
                                """ Boolean property controlling the lock state (True/False) of
                                the laser source""",
                                validator=strict_discrete_set,
                                map_values=True,
                                values={True: 1, False: 0})

    output_enabled = Instrument.control('SOUR0:POW:STAT?', 'SOUR0:POW:STAT %g',
                                        """ Boolean Property that controls the state (on/off) of
                                        the laser source """,
                                        validator=strict_discrete_set,
                                        map_values=True,
                                        values={True: 1, False: 0})

    _output_power_mW = Instrument.control('SOUR0:POW?', 'SOUR0:POW %f mW',
                                          """ Floating point value indicating the laser output power
                                          in mW.""",
                                          get_process=lambda v: v*1e3)

    _output_power_dBm = Instrument.control('SOUR0:POW?', 'SOUR0:POW %f dBm',
                                           """ Floating point value indicating the laser output power
                                           in dBm.""")

    _output_power_unit = Instrument.control('SOUR0:POW:UNIT?', 'SOUR0:POW:UNIT %g',
                                            """ String parameter controlling the power unit used internally
                                            by the laser.""",
                                            map_values=True,
                                            values={'dBm': 0, 'mW': 1})

    @property
    def output_power_mW(self):
        self._output_power_unit = 'mW'
        return self._output_power_mW

    @output_power_mW.setter
    def output_power_mW(self, new_power):
        self._output_power_mW = new_power

    @property
    def output_power_dBm(self):
        self._output_power_unit = 'dBm'
        return self._output_power_dBm

    @output_power_dBm.setter
    def output_power_dBm(self, new_power):
        self._output_power_dBm = new_power

    trigger_out = Instrument.control('TRIG0:OUTP?', 'TRIG0:OUTP %s',
                                     """ Specifies if and at which point in a sweep cycle an output trigger
                                     is generated and arms the module. """,
                                     validator=strict_discrete_set,
                                     values=['DIS', 'STF', 'SWF', 'SWST'])

    trigger_in = Instrument.control('TRIG0:INP?', 'TRIG0:INP %s',
                                    """ Sets the incoming trigger response and arms the module. """,
                                    validator=strict_discrete_set,
                                    values=['IGN', 'NEXT', 'SWS'])

    wavelength = Instrument.control('sour0:wav?', 'sour0:wav %fnm',
                                    """ Absolute wavelength of the output light (in nanometers)""",
                                    validator=strict_range,
                                    values=WL_RANGE,
                                    get_process=lambda v: v*1e9)

    sweep_wl_start = Instrument.control('sour0:wav:swe:star?', 'sour0:wav:swe:star %fnm',
                                        """ Start Wavelength (in nanometers) for a sweep.""",
                                        validator=strict_range,
                                        values=WL_RANGE,
                                        get_process=lambda v: v*1e9)
    sweep_wl_stop = Instrument.control('sour0:wav:swe:stop?', 'sour0:wav:swe:stop %fnm',
                                       """ End Wavelength (in nanometers) for a sweep.""",
                                       validator=strict_range,
                                       values=WL_RANGE,
                                       get_process=lambda v: v*1e9)

    sweep_step = Instrument.control('sour0:wav:swe:step?', 'sour0:wav:swe:step %fnm',
                                    """ Step width of the sweep (in nanometers).""",
                                    validator=strict_range,
                                    values=[0.0001, WL_RANGE[1]-WL_RANGE[0]],
                                    get_process=lambda v: v*1e9)
    sweep_speed = Instrument.control('sour0:wav:swe:speed?', 'sour0:wav:swe:speed %fnm/s',
                                     """ Speed of the sweep (in nanometers per second).""",
                                     validator=strict_discrete_set,
                                     values=[0.5, 1, 50, 80, 200],
                                     get_process=lambda v: v*1e9)
    sweep_mode = Instrument.control('sour0:wav:swe:mode?', 'sour0:wav:swe:mode %s',
                                    """ Sweep mode of the swept laser source """,
                                    validator=strict_discrete_set,
                                    values=['STEP', 'MAN', 'CONT'])
    sweep_twoway = Instrument.control('sour0:wav:swe:rep?', 'sour0:wav:swe:rep %s',
                                      """Sets the repeat mode. Applies in stepped,continuous and
                                      manual sweep mode.""",
                                      validator=strict_discrete_set,
                                      map_values=True,
                                      values={False: 'ONEW', True: 'TWOW'})
    _sweep_params_consistent = Instrument.measurement(
        'sour0:wav:swe:chec?',
        """Returns whether the currently set sweep parameters (sweep mode, sweep start,
        stop, width, etc.) are consistent. If there is a
        sweep configuration problem, the laser source is not
        able to pass a wavelength sweep.""")

    sweep_points = Instrument.measurement('sour0:read:points? llog',
                                          """Returns the number of datapoints that the :READout:DATA?
                                          command will return.""")

    sweep_state = Instrument.control('sour0:wav:swe?', 'sour0:wav:swe %g',
                                     """ State of the wavelength sweep. Stops, starts, pauses
                                     or continues a wavelength sweep. Possible state values are
                                     0 (not running),
                                     1 (running) and
                                     2 (paused).
                                     Refer to the N7776C user manual for exact usage of the
                                     paused option. """,
                                     validator=strict_discrete_set,
                                     values=[0, 1, 2])

    wl_logging = Instrument.control('SOUR0:WAV:SWE:LLOG?', 'SOUR0:WAV:SWE:LLOG %g',
                                    """ State (on/off) of the lambda logging feature of the
                                    laser source.""",
                                    validator=strict_discrete_set,
                                    map_values=True,
                                    values={True: 1, False: 0})

    def valid_sweep_params(self):
        response = int(self._sweep_params_consistent[0])
        if response == 0:
            return True
        elif response == 368:
            log.warning('End Wavelength <= Start Wavelength.')
        elif response == 369:
            log.warning('Sweep time too small.')
        elif response == 370:
            log.warning('Sweep time too big.')
        elif response == 371:
            log.warning('Trigger Frequency too large.')
        elif response == 372:
            log.warning('Stepsize too small.')
        elif response == 373 or response == 378:
            log.warning('Number of triggers exceeds allowed limit.')
        elif response == 374:
            log.warning('The only allowed modulation source with lambda logging \
                        function is coherence control.')
        elif response == 375:
            log.warning('Lambda logging only works Step Finished output trigger configuration')
        elif response == 376:
            log.warning('Lambda logging can only be done in continuous sweep mode')
        elif response == 377:
            log.warning('The step size must be a multiple of the smallest possible step size')
        elif response == 379:
            log.warning('Continuous Sweep and Modulation on.')
        elif response == 380:
            log.warning('Start Wavelength is too small.')
        elif response == 381:
            log.warning('End Wavelength is too large.')
        else:
            log.warning('Unknown Error!')
        return False

    def next_step(self):
        """
        Performs the next sweep step in stepped sweep if it is paused or in manual mode.
        """
        self.write('sour0:wav:swe:step:next')

    def previous_step(self):
        """
        Performs one sweep step backwards in stepped sweep if its paused or in manual mode.
        """
        self.write('sour0:wav:swe:step:prev')

    def get_wl_data(self):
        """
        Function returning the wavelength data logged in the internal memory of the laser
        """
        return np.array(self.adapter.connection.query_binary_values('sour0:read:data? llog',
                        datatype=u'd'))

    def close(self):
        """
        Fully closes the connection to the instrument through the adapter connection.
        """
        self.adapter.connection.close()
