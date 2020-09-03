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
import time
import numpy as np
from pymeasure.instruments import Instrument

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Keithley2600(Instrument):
    """Represents the Keithley 2600 series (channel A and B) SourceMeter"""
    def __init__(self, adapter, **kwargs):
        super(Keithley2600, self).__init__(
            adapter,
            "Keithley 2600 SourceMeter",
            **kwargs
        )
        self.ChA = Channel(self, 'a')
        self.ChB = Channel(self, 'b')


class Channel(object):

    @property
    def source_output(self):
        if self.instrument.ask('print(smu%s.source.output)' % self.channel)==1:
            return 'output is ON'
        elif self.instrument.ask('print(smu%s.source.output)' % self.channel)==0:
            return 'output is OFF'
    @source_output.setter
    def source_output(self, state):
        if state in ['on', 'off']:
            statedict={
                'off': 0,
                'on': 1
            }
            self.instrument.write('smu%s.source.output=%d' % (self.channel,statedict[state]))
        else:
            raise ValueError('State has to be either on or off!')

    @property
    def source_mode(self):
        return self.instrument.ask('print(smu%s.source.func)' % self.channel)
    @source_mode.setter
    def source_mode(self, mode):
        if mode in ['current', 'voltage']:
            modedict={
                "voltage": 1,
                "current": 0
            }
            self.instrument.write('smu%s.source.func=%d' % (self.channel, modedict[mode]))
        else:
            raise ValueError('Mode has to be either current or voltage!')

    @property
    def measure_nplc(self):
        return self.instrument.ask('print(smu%s.measure.nplc)' % self.channel)
    @measure_nplc.setter
    def measure_nplc(self, nplc):
        if nplc in range(0.001,25):
            self.instrument.write('smu%s.measure.nplc=%f' % (self.channel, nplc))
        else:
            raise ValueError('NPLC has to be in the interval [0.001,25]!')
    ###############
    # Current (A) #
    ###############
    @property
    def current(self):
        return float(self.instrument.ask('print(smu%s.measure.i())' % self.channel))

    @property
    def source_current(self):
        return float(self.instrument.ask('print(smu%s.source.leveli)' % self.channel))
    @source_current.setter
    def source_current(self, current):
        self.instrument.write('smu%s.source.leveli=%f' % (self.channel, current))

    @property
    def compliance_current(self):
        return float(self.instrument.ask('print(smu%s.source.limiti)' % self.channel))
    @compliance_current.setter
    def compliance_current(self, complvalue):
        self.instrument.write('smu%s.source.limiti=%f' % (self.channel, complvalue))

    @property
    def source_current_range(self):
        return float(self.instrument.ask('print(smu%s.source.rangei' % self.channel))
    @source_current_range.setter
    def source_current_range(self, rng):
        if rng in range(-1.5,1.5):
            self.instrument.write('smu%s.source.rangei=%f' % (self.channel, range))
        else:
            raise ValueError('Source current range has to be in the interval [-1.5,1.5]!')

    @property
    def current_range(self):
        return float(self.instrument.ask('print(smu%s.measure.rangei' % self.channel))
    @current_range.setter
    def current_range(self, rng):
        if rng in range(-1.5,1.5):
            self.instrument.write('smu%s.measure.rangei=%f' % (self.channel, rng))
        else:
            raise ValueError('Source current range has to be in the interval [-1.5,1.5]!')
    ###############
    # Voltage (V) #
    ###############

    @property
    def voltage(self):
        return float(self.instrument.ask('print(smu%s.measure.v())' % self.channel))
    @property
    def source_voltage(self):
        return float(self.instrument.ask('print(smu%s.source.levelv)' % self.channel))
    @source_voltage.setter
    def source_voltage(self, voltage):
        self.instrument.write('smu%s.source.levelv=%f' % (self.channel,voltage))

    @property
    def compliance_voltage(self):
        return float(self.instrument.ask('print(smu%s.source.limitv)' % self.channel))
    @compliance_voltage.setter
    def compliance_voltage(self, complvalue):
        if complvalue in range(-200,200):
            self.instrument.write('smu%s.source.limitv=%f' % (self.channel, complvalue))
        else:
            raise ValueError('Compliance voltage must be in the range [-200,200]!')

    @property
    def source_voltage_range(self):
        return float(self.instrument.ask('print(smu%s.source.rangev' % self.channel))
    @source_voltage_range.setter
    def source_voltage_range(self, rng):
        if rng in range(-200,200):
            self.instrument.write('smu%s.source.rangev=%f' % (self.channel, rng))
        else:
            raise ValueError('Source voltage range has to be in the interval [-200,200]!')

    @property
    def voltage_range(self):
        return float(self.instrument.ask('print(smu%s.measure.rangev' % self.channel))
    @voltage_range.setter
    def voltage_range(self, rng):
        if rng in range(-200,200):
            self.instrument.write('smu%s.measure.rangev=%f' % (self.channel, rng))
        else:
            raise ValueError('Source current range has to be in the interval [-200,200]!')
    ####################
    # Resistance (Ohm) #
    ####################

    @property
    def resistance(self):
        return float(self.instrument.ask('print(smu%s.measure.r())' % self.channel))

    @property
    def wires_mode(self):
        return self.instrument.ask('print(smu%s.sense)' % self.channel)
    @wires_mode.setter
    def wires_mode(self, mode):
        if mode in ['4', '2']:
            modedict = {
                "4": 1,
                "2": 0
            }
            self.instrument.write('smu%s.sense=%d' % (self.channel, modedict[mode]))
        else:
            raise ValueError('Wire mode has to be either 4 (wires) or 2 (wires)!')
    ###########
    # Methods #
    ###########

    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel

    def ask(self, cmd):
        return self.instrument.ask(cmd)

    def write(self, cmd):
        self.instrument.write(cmd)

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param voltage: Upper limit of voltage in Volts, from -200 V to 200 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info("%s is measuring voltage." % self.channel)
        self.write('smu%s.measure.v()' % self.channel)
        self.write('smu%s.measure.nplc=%f' % (self.channel, nplc))
        if auto_range:
            self.write('smu%s.measure.autorangev=1' % self.channel)
        else:
            self.voltage_range = voltage
        self.check_errors()

    def measure_current(self, nplc=1, current=1.05e-4, auto_range=True):
        """ Configures the measurement of current.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param current: Upper limit of current in Amps, from -1.5 A to 1.5 A
        :param auto_range: Enables auto_range if True, else uses the set current
        """
        log.info("%s is measuring current." % self.channel)
        self.write('smu%s.measure.i()' % self.channel)
        self.write('smu%s.measure.nplc=%f' % (self.channel, nplc))
        if auto_range:
            self.write('smu%s.measure.autorangei=1' % self.channel)
        else:
            self.current_range = current
        self.check_errors()

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        if self.source_mode == 'current':
            self.write('smu%s.source.autorangei=1' % self.channel)
        else:
            self.write('smu%s.source.autorangev=1' % self.channel)

    def apply_current(self, current_range=None, compliance_voltage=0.1):
        """ Configures the instrument to apply a source current, and
                uses an auto range unless a current range is specified.
                The compliance voltage is also set.
                :param compliance_voltage: A float in the correct range for a
                                           :attr:`~.Keithley2400.compliance_voltage`
                :param current_range: A :attr:`~.Keithley2400.current_range` value or None
                """
        log.info("%s is sourcing current." % self.channel)
        self.source_mode = 'current'
        if current_range is None:
            self.auto_range_source()
        else:
            self.source_current_range = current_range
        self.compliance_voltage = compliance_voltage
        self.check_errors()

    def apply_voltage(self, voltage_range=None,
                      compliance_current=0.1):
        """ Configures the instrument to apply a source voltage, and
        uses an auto range unless a voltage range is specified.
        The compliance current is also set.
        :param compliance_current: A float in the correct range for a
                                   :attr:`~.Keithley2400.compliance_current`
        :param voltage_range: A :attr:`~.Keithley2400.voltage_range` value or None
        """
        log.info("%s is sourcing voltage." % self.name)
        self.source_mode = 'voltage'
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current
        self.check_errors()

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
        single error. """
        err = self.values('errorqueue.next()')
        if len(err) < 2:
            err = self.read()  # Try reading again
        code = err[0]
        message = err[1].replace('"', '')
        return (code, message)

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("Keithley 2600 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for Keithley 2600 error retrieval.")

    def ramp_to_voltage(self, target_voltage, steps=30, pause=0.1):
        """ Ramps to a target voltage from the set voltage value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_voltage: A voltage in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps """
        voltages = np.linspace(self.source_voltage, target_voltage, steps)
        for voltage in voltages:
            self.source_voltage = voltage
            time.sleep(pause)

    def ramp_to_current(self, target_current, steps=30, pause=0.1):
        """ Ramps to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.
        :param target_current: A current in Amps
        :param steps: An integer number of steps
        :param pause: A pause duration in seconds to wait between steps """
        currents = np.linspace(self.source_current, target_current, steps)
        for current in currents:
            self.source_current = current
            time.sleep(pause)

    def shutdown(self):
        """ Ensures that the current or voltage is turned to zero
        and disables the output. """
        log.info("Shutting down channel %s." % self.channel)
        if self.source_mode == 'current':
            self.ramp_to_current(0.0)
        else:
            self.ramp_to_voltage(0.0)
        self.source_output='off'
