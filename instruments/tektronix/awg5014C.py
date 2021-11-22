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
from pymeasure.instruments.validators import strict_range, strict_discrete_set
from time import time
from pyvisa.errors import VisaIOError

class Channel(object):

        vpp_amplitude = Instrument.control(
            "voltage:amplitude?","voltage:amplitude %g",
            """ A floating point property that controls the output amplitude
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[50e-3, 4.5]
        )

        offset = Instrument.control(
            "voltage:offset?","voltage:offset %g",
            """ A floating point property that controls the amplitude
            offset. It is always in Volt. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        vpp_high = Instrument.control(
            "voltage:high?", "voltage:high %g",
            """ A floating point property that controls the output high level
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        vpp_low = Instrument.control(
            "voltage:low?", "voltage:low %g",
            """ A floating point property that controls the output low level
            in Vpp. This property can be set.""",
            validator=strict_range,
            values=[-2, 2]
        )

        load_waveform = Instrument.control(
            "waveform?", "waveform \"%s\"",
            """ Loads the waveform of a given name """
        )

        sampling_frequency = Instrument.control(
            "frequency:fixed?", "frequency:fixed %e",
            """ A floating point property that sets the sampling frequency.
            A given waveform will have frequency=sampling_frequency/number_of_points""",
            validator=strict_range,
            values=[10e6,10e9]
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

        def waveform(self, name, frequency=1e6, units='VPP',
                     amplitude=1, offset=0):
            """General setting method for loading and setting a full WF"""
            self.instrument.write("source%d:waveform %s" % (
                                  self.number, name))
            self.instrument.write("source%d:frequency:fixed %e" % (
                                  self.number, frequency))
            self.instrument.write("source%d:voltage:unit %s" % (
                                  self.number, units))
            self.instrument.write("source%d:voltage:amplitude %e%s" %(
                                  self.number, amplitude,units))
            self.instrument.write("source%d:voltage:offset %eV" %(
                                  self.number, offset))

class AWG5014C(Instrument):
    """Represents the Tektronix AWG 5000 series (written for 5014c, YMMV)
    arbitrary function generator and provides a high-level for
    interacting with the instrument. This is an AWG first an foremost so,
    while there are predefined waveforms (sine,triangle,etc) they are specified
    by a certain number of points so it is not as straight forward as specifying "SINE".
    You must know the name of the built in waveform to call it.

        afg=AFG5014C("GPIB::1")        # AFG on GPIB 1
        afg.reset()                    # Reset to default
    """

    trigger_wait_value = Instrument.control(
        "TRIGger:SEQUENCE:WVALue?", "TRIGger:SEQUENCE:WVALue %s",
        """ A string parameter to set the voltage while waiting for trigger:
        either the LAST value or FIRS value (not a typo)""",
        validator=strict_discrete_set,
        values={'LAST':'LAST', 'FIRS':'FIRS'},
        map_values=True
    )

    trigger_source = Instrument.control(
        "TRIGger:SEQUENCE:SOURce?", "TRIGger:SEQUENCE:SOURce %s",
        """ A string parameter to set the whether the trigger is INTernal or EXTernal""",
        validator=strict_discrete_set,
        values={'INT': 'INT', 'EXT': 'EXT'},
        map_values=True
    )

    trigger_slope = Instrument.control(
        "TRIGger:SEQUENCE:SLOPe?", "TRIGger:SEQUENCE:SLOPe %s",
        """ A string parameter to set the whether the trigger edge is POSitive or NEGative""",
        validator=strict_discrete_set,
        values={'POS': 'POS', 'NEG': 'NEG'},
        map_values=True
    )

    trigger_level = Instrument.control(
        "TRIGger:SEQUENCE:LEVel?", "TRIGger:SEQUENCE:LEVel %g",
        """ A float parameter that sets the trigger input level threshold. Unclear what the range is,
        0.2 V - 1.4 V is a valid range""",
    )

    trigger_impedance = Instrument.control(
        "TRIGger:SEQUENCE:IMPedance?", "TRIGger:SEQUENCE:IMPedance %d",
        """ An integer parameter to set the trigger input impedance to either 50 or 1000 Ohms""",
        validator=strict_discrete_set,
        values=[50,1000],
        map_values=True
    )

    sampling_frequency = Instrument.control(
        "source1:frequency:fixed?", "source1:frequency:fixed %e",
        """ A floating point property that controls the frequency.
        This property can be set.""",
        validator=strict_range,
        values=[10e6, 1.2e9]
    )

    run_mode = Instrument.control(
        "AWGControl:RMODe?", "AWGControl:RMODe %s",
        """ A string parameter controlling the AWG run mode. Can be:
        CONT: output continously outputs WF
        TRIG: Each trigger input fires off one cycle
        GAT: output is continuously output subject to stimulus being applied
        SEQ: output according to a loaded sequence file, if one isn't loaded, this is equal to triggered""",
        validator=strict_discrete_set,
        values=['CONT', 'TRIG', 'GAT', 'SEQ'],
    )


    def __init__(self, adapter, **kwargs):
        super(AWG5014C, self).__init__(
            adapter,
            "Tektronix AFG3152C arbitrary function generator",
            **kwargs
        )
        self.ch1 = Channel(self, 1)
        self.ch2 = Channel(self, 2)
        self.ch3 = Channel(self, 3)
        self.ch4 = Channel(self, 4)

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


    def start_awg(self):
        self.write('AWGC:RUN')

    def stop_awg(self):
        self.write('AWGC:STOP')

    def define_new_waveform(self, name, size, datatype='INT'):
        """
        Defines an empty waveform of name, of integer length size of datatype ('INT' or 'REAL'
        """
        self.write("wlist:waveform:new \"%s\",%i,%s" % (name,size,datatype))


    def delete_waveform(self, name):
        """
        Defines an empty waveform of name, of integer length size of datatype ('INT' or 'REAL'
        """
        self.write("wlist:waveform:delete \"%s\"" % name)

    def load_waveform(self,name, start_index, data, converter='f'):
        """
        Transfers a data to a waveform predifined in define_new_waveform. Max limit of data is 650,000,000 bytes,
        converter 'f' is for floating point, 'h' is for int16
        """

        cmd_string = 'wlist:waveform:data \"%s\", %d, %d,' % (name, start_index, len(data))
        self.adapter.connection.write_binary_values(cmd_string,data,datatype=converter,is_big_endian=True)