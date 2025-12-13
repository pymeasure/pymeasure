#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from warnings import warn

import numpy as np
from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# The Keithley 2600* SMUs come in a few flavors with even last digits being 2 channels,
# and the next to last digit indicating the max voltage and resolution.
# We care about the limits not resolution.
# For a given number, the limits are the same, but enumerating each may save user time.
#    LV   HV  HV+fine current
# 1 2601 2611 2635
# 2 2602 2612 2636
# 2 2604 2614 2634 - No Ethernet for lower cost

class Keithley260X(SCPIMixin, Instrument):
    """Represents the Keithley 2600* series SourceMeter with at least one channel"""

    def __init__(self, adapter, name="Keithley 2600 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        # Channels are configured/initialized in the specific model.

    @property
    def next_error(self):
        """ Get a tuple of an error code and message from a
        single error. """
        err = self.ask('print(errorqueue.next())')
        err = err.split('\t')
        # Keithley Instruments Inc. sometimes on startup
        # if tab delimitated message is greater than one, grab first two as code, message
        # otherwise, assign code & message to returned error
        if len(err) > 1:
            err = (int(float(err[0])), err[1])
            code = err[0]
            message = err[1].replace('"', '')
        else:
            code = message = err[0]
        log.info(f"ERROR {str(code)},{str(message)} - len {str(len(err))}")
        return (code, message)

    @property
    def error(self):
        """Get the next error from the queue.

        .. deprecated:: 0.15
            Use `next_error` instead.
        """
        warn("Deprecated to use `error`, use `next_error` instead.", FutureWarning)
        return self.next_error


class Keithley2600(Keithley260X):
    """Backward compatible 2600 model - Not a real product"""
    def __init__(self, adapter, name="Keithley 2600 SourceMeter", **kwargs):
        warn("This is a generic 2 channel model. Using the actual model may " \
                " match limits and channels better.", FutureWarning)
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA = ChannelHV(self, 'a')
        self.ChB = ChannelHV(self, 'b')

class Keithley2601(Keithley260X):
    '''Represents the 2601 Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2601 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA = ChannelLV(self, 'a')

class Keithley2601A(Keithley2601):
    '''Represents the 2601A Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2601A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2601B(Keithley2601):
    '''Represents the 2601B Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2601B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2602(Keithley260X):
    '''Represents the 2602 Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2602 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA = ChannelLV(self, 'a')
        self.ChB = ChannelLV(self, 'b')

class Keithley2602A(Keithley2602):
    '''Represents the 2602A Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2602A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2602B(Keithley2602):
    '''Represents the 2602B Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2602B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2604B(Keithley2602):
    '''Represents the 2604B Dual Channel SMU'''
    # It doesn't look like 2604 non-Bs were made.
    def __init__(self, adapter, name="Keithley 2604B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2611(Keithley260X):
    '''Represents the 2611 Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2611 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA = ChannelHV(self, 'a')

class Keithley2611A(Keithley2601):
    '''Represents the 2611A Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2611A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2611B(Keithley2601):
    '''Represents the 2611B Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2611B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2612(Keithley260X):
    '''Represents the 2612 Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2612 SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
        self.ChA = ChannelHV(self, 'a')
        self.ChB = ChannelHV(self, 'b')

class Keithley2612A(Keithley2612):
    '''Represents the 2612A Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2612A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2612B(Keithley2612):
    '''Represents the 2612B Dual Channel SMU'''
    def __init__(self, adapter, name="Keithley 2612B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2634B(Keithley2612):
    '''Represents the 2634B Dual Channel SMU'''
    # It doesn't look like 2634 non-Bs were made.
    def __init__(self, adapter, name="Keithley 2634B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2635A(Keithley2611):
    '''Represents the 2635A Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2635A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2635B(Keithley2611):
    '''Represents the 2635B Single Channel SMU'''
    def __init__(self, adapter, name="Keithley 2635B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2636A(Keithley2612):
    '''Represents the 2636A Dual Channel SMU'''
    # It doesn't look like 2634 non-letters were made.
    def __init__(self, adapter, name="Keithley 2636A SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

class Keithley2636B(Keithley2612):
    '''Represents the 2636B Dual Channel SMU'''
    # It doesn't look like 2634 non-letters were made.
    def __init__(self, adapter, name="Keithley 2636B SourceMeter", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )


class CommonChannel:
    '''An SMU Channel. The Keithley SMUs here have either 1 or 2 channels.'''
    def __init__(self, instrument, channel):
        self.instrument = instrument
        self.channel = channel

    def ask(self, cmd):
        return float(self.instrument.ask(f'print(smu{self.channel}.{cmd})'))

    def write(self, cmd):
        self.instrument.write(f'smu{self.channel}.{cmd}')

    def values(self, cmd, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values(f'print(smu{self.channel}.{cmd})')

    def binary_values(self, cmd, header_bytes=0, dtype=np.float32):
        return self.instrument.binary_values('print(smu%s.%s)' %
                                             (self.channel, cmd,), header_bytes, dtype)

    def check_errors(self):
        return self.instrument.check_errors()

    source_output = Instrument.control(
        'source.output', 'source.output=%d',
        """Control the channel output state (ON of OFF)
        """,
        validator=strict_discrete_set,
        values={'OFF': 0, 'ON': 1},
        map_values=True
    )

    source_mode = Instrument.control(
        'source.func', 'source.func=%d',
        """Control the channel source function (Voltage or Current)
        """,
        validator=strict_discrete_set,
        values={'voltage': 1, 'current': 0},
        map_values=True
    )

    measure_nplc = Instrument.control(
        'measure.nplc', 'measure.nplc=%f',
        """ Control the nplc value """,
        validator=truncated_range,
        values=[0.001, 25],
        map_values=True
    )

    ####################
    # Resistance (Ohm) #
    ####################
    resistance = Instrument.measurement(
        'measure.r()',
        """ Get the resistance in Ohms """
    )

    wires_mode = Instrument.control(
        'sense', 'sense=%d',
        """Control the resistance measurement mode: 4 wires or 2 wires""",
        validator=strict_discrete_set,
        values={'4': 1, '2': 0},
        map_values=True
    )

    #######################
    # Measurement Methods #
    #######################

    def measure_voltage(self, nplc=1, voltage=21.0, auto_range=True):
        """ Configures the measurement of voltage.
        :param nplc: Number of power line cycles (NPLC) from 0.001 to 25
        :param voltage: Upper limit of voltage in Volts, from -200 V to 200 V
        :param auto_range: Enables auto_range if True, else uses the set voltage
        """
        log.info("%s is measuring voltage." % self.channel)
        self.write('measure.nplc=%f' % nplc)
        if auto_range:
            self.write('measure.autorangev=1')
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
        self.write('measure.i()')
        self.write('measure.nplc=%f' % nplc)
        if auto_range:
            self.write('measure.autorangei=1')
        else:
            self.current_range = current
        self.check_errors()

    def auto_range_source(self):
        """ Configures the source to use an automatic range.
        """
        if self.source_mode == 'current':
            self.write('source.autorangei=1')
        else:
            self.write('source.autorangev=1')

    def apply_current(self, current_range=None, compliance_voltage=0.1):
        """ Configures the instrument to apply a source current, and
        uses an auto range unless a current range is specified.
        The compliance voltage is also set.
        :param compliance_voltage: A float in the correct range for a
                                   :attr:`~.Keithley2600.compliance_voltage`
        :param current_range: A :attr:`~.Keithley2600.current_range` value or None
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
                                   :attr:`~.Keithley2600.compliance_current`
        :param voltage_range: A :attr:`~.Keithley2600.voltage_range` value or None
        """
        log.info("%s is sourcing voltage." % self.channel)
        self.source_mode = 'voltage'
        if voltage_range is None:
            self.auto_range_source()
        else:
            self.source_voltage_range = voltage_range
        self.compliance_current = compliance_current
        self.check_errors()

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
        self.source_output = 'OFF'

class ChannelHV(CommonChannel):
    '''Channel with limits for the 200V 261x or 263x models.'''
        ###############
    # Current (A) #
    ###############
    current = Instrument.measurement(
        'measure.i()',
        """ Get the current in Amps """
    )

    source_current = Instrument.control(
        'source.leveli', 'source.leveli=%f',
        """ Control the applied source current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    compliance_current = Instrument.control(
        'source.limiti', 'source.limiti=%f',
        """ Control the source compliance current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    source_current_range = Instrument.control(
        'source.rangei', 'source.rangei=%f',
        """Control the source current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    current_range = Instrument.control(
        'measure.rangei', 'measure.rangei=%f',
        """Control the measurement current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    ###############
    # Voltage (V) #
    ###############
    voltage = Instrument.measurement(
        'measure.v()',
        """ Get the voltage in Volts """
    )

    source_voltage = Instrument.control(
        'source.levelv', 'source.levelv=%f',
        """ Control the applied source voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    compliance_voltage = Instrument.control(
        'source.limitv', 'source.limitv=%f',
        """ Control the source compliance voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    source_voltage_range = Instrument.control(
        'source.rangev', 'source.rangev=%f',
        """Control the source current range """,
        validator=truncated_range,
        values=[-200, 200]
    )

    voltage_range = Instrument.control(
        'measure.rangev', 'measure.rangev=%f',
        """Control the measurement voltage range """,
        validator=truncated_range,
        values=[-200, 200]
    )

class Channel(ChannelHV):
    '''This is for backwards compatibility with the previous 2600 Channel definition.'''


class ChannelLV(CommonChannel):
    '''Channel with limits for the 40V 261x or 263x models.'''
    ###############
    # Current (A) #
    ###############
    current = Instrument.measurement(
        'measure.i()',
        """ Get the current in Amps """
    )

    source_current = Instrument.control(
        'source.leveli', 'source.leveli=%f',
        """ Control the applied source current """,
        validator=truncated_range,
        values=[-3, 3]
    )

    compliance_current = Instrument.control(
        'source.limiti', 'source.limiti=%f',
        """ Control the source compliance current """,
        validator=truncated_range,
        values=[-3, 3]
    )

    source_current_range = Instrument.control(
        'source.rangei', 'source.rangei=%f',
        """Control the source current range """,
        validator=truncated_range,
        values=[-3, 3]
    )

    current_range = Instrument.control(
        'measure.rangei', 'measure.rangei=%f',
        """Control the measurement current range """,
        validator=truncated_range,
        values=[-3, 3]
    )

    ###############
    # Voltage (V) #
    ###############
    voltage = Instrument.measurement(
        'measure.v()',
        """ Get the voltage in Volts """
    )

    source_voltage = Instrument.control(
        'source.levelv', 'source.levelv=%f',
        """ Control the applied source voltage """,
        validator=truncated_range,
        values=[-40, 40]
    )

    compliance_voltage = Instrument.control(
        'source.limitv', 'source.limitv=%f',
        """ Control the source compliance voltage """,
        validator=truncated_range,
        values=[-40, 40]
    )

    source_voltage_range = Instrument.control(
        'source.rangev', 'source.rangev=%f',
        """Control the source current range """,
        validator=truncated_range,
        values=[-40, 40]
    )

    voltage_range = Instrument.control(
        'measure.rangev', 'measure.rangev=%f',
        """Control the measurement voltage range """,
        validator=truncated_range,
        values=[-40, 40]
    )
