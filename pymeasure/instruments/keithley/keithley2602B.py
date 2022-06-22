# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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
from pymeasure.instruments import Instrument
from pymeasure.instruments.keithley.keithley2600 import Keithley2600
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class Keithley2602B(Keithley2600):
    """Represents the Keithley 2602B SourceMeter. This class adds digital I/O 
    functionality to the Keithley2600 series driver. Note that this driver can
    be used to control any of the other 2600 series models that support digital
    I/O (2601B, 2611B, 2612B, 2635B, 2636B).
    """
    
    number_of_pins = 14
    
    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            includeSCPI=False,
            **kwargs
        )
        
        self.dio_pins = []
        for i in range(1, Keithley2602B.number_of_pins + 1):
            self.dio_pins[i] = DigitalIOPin(self, i)
            
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
    
    def get_overrun_status(self):
        """This function gets the event detector overrun status. If this is
        true, an event was ignored because the event detector was already in the
        detected state when the event occurred. This is an indication of the
        state of the event detector built into the line itself. It does not
        indicate if an overrun occurred in any other part of the trigger model
        or in any other detector that is monitoring the event."""
        status = self.ask('EVENT_ID')
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
    