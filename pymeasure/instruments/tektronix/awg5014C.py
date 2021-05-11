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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from time import time
from pyvisa.errors import VisaIOError

class Channel(object):

        vpp_amplitude = Instrument.control(
            "voltage:amplitude?","voltage:amplitude %eVPP",
            """ A floating point property that controls the output amplitude
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[50e-3, 2]
        )

        offset = Instrument.control(
            "voltage:offset?","voltage:offset %e",
            """ A floating point property that controls the amplitude
            offset. It is always in Volt. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        vpp_high = Instrument.control(
            "voltage:high?", "voltage:high %eVPP",
            """ A floating point property that controls the output high level
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        vpp_low = Instrument.control(
            "voltage:low?", "voltage:low %eVPP",
            """ A floating point property that controls the output low level
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        load_waveform = Instrument.control(
            "waveform?", "waveform %s",
            """ Loads the waveform of a given name """
        )

        def __init__(self, instrument, number):
            self.instrument = instrument
            self.number = number

        def values(self, command, **kwargs):
            """ Reads a set of values from the instrument through the adapter,
            passing on any key-word arguments.
            """
            return self.instrument.values("source%d:%s" % (
                                          self.number, command), **kwargs)
        def ask(self, command):
            self.instrument.query("source%d:%s" % (self.number, command))

        def write(self, command):
            self.instrument.write("source%d:%s" % (self.number, command))

        def read(self):
            self.instrument.read()

        def enable(self):
            self.instrument.write("output%d:state on" % self.number)

        def disable(self):
            self.instrument.write("output%d:state off" % self.number)

        def waveform(self, shape='SIN', frequency=1e6, units='VPP',
                     amplitude=1, offset=0):
            """General setting method for a complete wavefunction"""
            self.instrument.write("source%d:function:shape %s" % (
                                  self.number, shape))
            self.instrument.write("source%d:frequency:fixed %e" % (
                                  self.number, frequency))
            self.instrument.write("source%d:voltage:unit %s" % (
                                  self.number, units))
            self.instrument.write("source%d:voltage:amplitude %e%s" %(
                                  self.number, amplitude,units))
            self.instrument.write("source%d:voltage:offset %eV" %(
                                  self.number, offset))

class AFG3152C(Instrument):
    """Represents the Tektronix AWG 5000 series (written for 5014c, YMMV)
    arbitrary function generator and provides a high-level for
    interacting with the instrument. This is an AWG first an foremost so,
    while there are predefined waveforms (sine,triangle,etc) they are specified
    by a certain number of points so it is not as straight forward as specifying "SINE".
    You must know the name of the built in waveform to call it.

        afg=AFG3152C("GPIB::1")        # AFG on GPIB 1
        afg.reset()                    # Reset to default
    """

    def __init__(self, adapter, **kwargs):
        super(AFG3152C, self).__init__(
            adapter,
            "Tektronix AFG3152C arbitrary function generator",
            **kwargs
        )
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)

    def beep(self):
        self.write("system:beep")

    def trigger(self):
        """ Send a trigger signal to the function generator. """
        self.write("*TRG")

    def wait_for_trigger(self, timeout=3600, should_stop=lambda: False):
        """ Wait until the triggering has finished or timeout is reached.

        :param timeout: The maximum time the waiting is allowed to take. If
                        timeout is exceeded, a TimeoutError is raised. If
                        timeout is set to zero, no timeout will be used.
        :param should_stop: Optional function (returning a bool) to allow the
                            waiting to be stopped before its end.

        """
        self.write("*OPC?")

        t0 = time()
        while True:
            try:
                ready = bool(self.read())
            except VisaIOError:
                ready = False

            if ready:
                return

            if timeout != 0 and time() - t0 > timeout:
                raise TimeoutError(
                    "Timeout expired while waiting for the WAS8104A" +
                    " to finish the triggering."
                )

            if should_stop:
                return

    def opc(self):
        return int(self.query("*OPC?"))

    sampling_frequency = Instrument.control(
        "source1:frequency:fixed?", "source1:frequency:fixed %e",
        """ A floating point property that controls the frequency.
        This property can be set.""",
        validator=strict_range,
        values=[10e6, 1.2e9]
    )

    def define_new_waveform(self, name, size, datatype='INT'):
        """
        Defines an empty waveform of name, of integer length size of datatype ('INT' or 'REAL'
        """
        self.write("wlist:waveform:new \"%s\",%i,%s" % (name,size,datatype))
