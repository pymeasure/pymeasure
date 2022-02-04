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
from time import sleep

from pymeasure.adapters import VISAAdapter

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range, \
    modular_range_bidirectional, strict_discrete_set,strict_range

class ThorlabsTC200(Instrument):
    """Represents Thorlabs TC200 heater controller, serial settings are:
        Baud: 115200
        Data Bits: 8
        Parity: None
        Stop Bits: 1
        Flow Control: None
    Also the read_termination = '\r'
    and the write_termination = '\r'
    """

    MAX_TEMP = 205

    temperature_setpoint = Instrument.control("tset?", "tset=%.1f",
                                    """Set the temperature setpoint. from 20.0 to 200.0 to TMAX""")

    tmax = Instrument.control("tmax?", "tmax=%.1f",
                                              """Set the max temperature, [20.0, 205.0]""",
                              validator=strict_range,
                              values=[20.0, 205.0])

    pmax = Instrument.control("pmax?", "pmax=%.1f",
                              """Set the max power output, [0.1,18.0]""",
                              validator=strict_range,
                              values=[0.1, 18.0])


    temperature_actual = Instrument.measurement("tact?", "Actual temperature in C")

    @property
    def status(self):
        val = self.ask('stat?')
        if '\r' in val:
            val = val.split('\r')[-1]

        if 'stat' in val:
            val = val.replace('stat',"")

        if '?' in val:
            val = val.replace('?', "")

        return val

    @property
    def enabled(self):
        out = bin(int(self.status.split()[0]))
        if out[-1]=='1':
            return True
        else:
            return False

    @enabled.setter
    def enabled(self, bool):
        state = self.enabled
        if (state and not bool) or (not state and bool):
            self.toggle_enable()

    id = Instrument.measurement('*idn?', "Returns the instrument id")

    sensor = Instrument.control("sns?", "sns=%s",
                                """Select the sensor type:
                                ptc100, ptc1000, th10k""",
                                validator=strict_discrete_set,
                                values=['ptc100', 'ptc1000', 'th10k'])


    def __init__(self, adapter, **kwargs):
        super(ThorlabsTC200, self).__init__(
            adapter, "ThorlabsTC200 heater controller", includeSCPI=False, **kwargs)

        if isinstance(self.adapter, VISAAdapter):
            self.adapter.connection.baud_rate = 115200
            self.adapter.connection.read_termination = '\r'
            self.adapter.connection.write_termination = '\r'

    def write(self, command):
        self.adapter.connection.write(command)
        sleep(.2)
        self.adapter.connection.read() #this read takes care of the echo that the instrument reports

    def ask(self, command):
        self.write(command)
        out = self.read()
        out = out.replace(command, "")
        print(out)
        return out

    def values(self, command, **kwargs):
        out = self.ask(command)
        try:
            return [float(out)]
        except:
            return [out]

    def read(self):
        buff = self.adapter.connection.read_bytes(self.adapter.connection.bytes_in_buffer)
        decoded = buff.decode()
        for string in ['Celsius', 'C', '\r','>' ]:
            if string in decoded:
                decoded = decoded.replace(string,"")
        return decoded.strip()

    def toggle_enable(self):
        """
        If the unit is disabled this will enable it, if it is enabled this will disable it.
        :return:
        """
        self.adapter.write('ens')



