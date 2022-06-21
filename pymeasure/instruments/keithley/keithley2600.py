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
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2600(Instrument):
    """Represents the Keithley 2600 series (channel A and B) SourceMeter"""
    
    number_of_pins = 14
    
    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Keithley 2600 SourceMeter",
            **kwargs
        )
        self.ChA = Channel(self, 'a')
        self.ChB = Channel(self, 'b')
        
        self.dio_pins = []
        for i in range(1, Keithley2600.number_of_pins + 1):
            self.dio_pins[i] = DigitalIOPin(self, [i])

    @property
    def error(self):
        """ Returns a tuple of an error code and message from a
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
                
class DigitalIOPin:
    
    def __init__(self, instrument, pin_number):
        self.instrument = instrument
        self.pin_number = pin_number

    def ask(self, cmd):
        return self.instrument.ask(f'print(digio.trigger[{self.pin_number}].{cmd})')

    def write(self, cmd):
        self.instrument.write(f'digio.trigger.[{self.pin_number}].{cmd}')
        
    def check_errors(self):
        return self.instrument.check_errors()
        
    def assert_trigger(self):
        """This function asserts a trigger pulse on one of the digital I/O lines.
        """
        log.info("Asserting a trigger pulse on pin number %s." % self.pin_number)
        self.write('assert()')
        self.check_errors()
        
    def clear_trigger(self):
        """This function clears the trigger event on a digital I/O line.
        """
        log.info("Clearing trigger on pin number %s." % self.pin_number)
        self.write('clear()')
        self.check_errors()
        
    def get_event_id(self):
        """This function gets the mode in which the trigger event detector and
        the output trigger generator operate on the
        given trigger line. 
        """
        id = self.ask('EVENT_ID')
        self.check_errors()
        return int(id)
        
    trigger_mode = Instrument.control(
        'mode', 'mode=%d',
        """Property controlling the mode in which the trigger event detector and 
        the output trigger generator operate on the given trigger line.
        """,
        validator=strict_discrete_set,
        values={'TRIG_BYPASS': 0, 'TRIG_FALLING': 1, 'TRIG_RISING': 2, 'TRIG_EITHER': 3, 'TRIG_SYNCHRONOUSA': 4, 
                'TRIG_SYNCHRONOUS': 5, 'TRIG_SYNCHRONOUSM': 6, 'TRIG_RISINGA': 7, 'TRIG_RISINGM': 8},
        map_values=True
    )

class Channel:

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
        """Property controlling the channel output state (ON of OFF)
        """,
        validator=strict_discrete_set,
        values={'OFF': 0, 'ON': 1},
        map_values=True
    )

    source_mode = Instrument.control(
        'source.func', 'source.func=%d',
        """Property controlling the channel soource function (Voltage or Current)
        """,
        validator=strict_discrete_set,
        values={'voltage': 1, 'current': 0},
        map_values=True
    )

    measure_nplc = Instrument.control(
        'measure.nplc', 'measure.nplc=%f',
        """ Property controlling the nplc value """,
        validator=truncated_range,
        values=[0.001, 25],
        map_values=True
    )

    ###############
    # Current (A) #
    ###############
    current = Instrument.measurement(
        'measure.i()',
        """ Reads the current in Amps """
    )

    source_current = Instrument.control(
        'source.leveli', 'source.leveli=%f',
        """ Property controlling the applied source current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    compliance_current = Instrument.control(
        'source.limiti', 'source.limiti=%f',
        """ Property controlling the source compliance current """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    source_current_range = Instrument.control(
        'source.rangei', 'source.rangei=%f',
        """Property controlling the source current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    current_range = Instrument.control(
        'measure.rangei', 'measure.rangei=%f',
        """Property controlling the measurement current range """,
        validator=truncated_range,
        values=[-1.5, 1.5]
    )

    ###############
    # Voltage (V) #
    ###############
    voltage = Instrument.measurement(
        'measure.v()',
        """ Reads the voltage in Volts """
    )

    source_voltage = Instrument.control(
        'source.levelv', 'source.levelv=%f',
        """ Property controlling the applied source voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    compliance_voltage = Instrument.control(
        'source.limitv', 'source.limitv=%f',
        """ Property controlling the source compliance voltage """,
        validator=truncated_range,
        values=[-200, 200]
    )

    source_voltage_range = Instrument.control(
        'source.rangev', 'source.rangev=%f',
        """Property controlling the source current range """,
        validator=truncated_range,
        values=[-200, 200]
    )

    voltage_range = Instrument.control(
        'measure.rangev', 'measure.rangev=%f',
        """Property controlling the measurement voltage range """,
        validator=truncated_range,
        values=[-200, 200]
    )

    ####################
    # Resistance (Ohm) #
    ####################
    resistance = Instrument.measurement(
        'measure.r()',
        """ Reads the resistance in Ohms """
    )

    wires_mode = Instrument.control(
        'sense', 'sense=%d',
        """Property controlling the resistance measurement mode: 4 wires or 2 wires""",
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
        self.write('measure.v()')
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
