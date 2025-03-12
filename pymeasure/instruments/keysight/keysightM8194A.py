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
from time import time, sleep
import numpy as np
from pyvisa.errors import VisaIOError


class Channel(object):

    def __init__(self, instrument, number, **kwargs):
        self.instrument = instrument
        self.number = number

        for key, item in kwargs.items():
            setattr(self, key, item)

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("output%d:%s" % (
                                      self.number, command), **kwargs)

    @property
    def output(self):
        return self.instrument.ask(":OUTP%d?" % self.number)

    @output.setter
    def output(self, state):
        if not isinstance(state, bool):
            raise TypeError("Can only set output with boolean values")
        if state:
            self.enable()
        else:
            self.disable()

    def enable(self):
        self.instrument.write(":OUTP%d ON" % self.number)

    def disable(self):
        self.instrument.write(":OUTP%d OFF" % self.number)

    @property
    def amplitude(self):
        return self.instrument.ask(":VOLT%d?" % self.number)

    @amplitude.setter
    def amplitude(self, amp):
        if amp < 0 or amp > 0.8:
            raise ValueError(f'Invalid amplitude: {amp}, must be 0<amp<0.8')
        self.instrument.write(f":VOLT{self.number} {amp}")

    @property
    def offset(self):
        return self.instrument.ask(f":VOLT{self.number}:OFFS?")

    @offset.setter
    def offset(self, offset):
        if offset < -0.75 or offset > 0.75:
            raise ValueError(f'Invalid offset {offset}, must be -.75 <offset<.75')
        self.instrument.write(f":VOLT{self.number}:OFFS {offset}")

class KeysightM8194A(Instrument):
    """Represents the keysight M8194A arbitrary waveform generator. NOTE:
    This AWG cannot do single traces. It just blasts.

    """

    def __init__(self, adapter, **kwargs):
        super(KeysightM8194A, self).__init__(
            adapter,
            "M8194 arbitrary waveform generator",
            **kwargs
        )
        self.num_channels = 2
        self.default_dir = 'C:\\Users\\Administrator\\Pictures'
        num_chan = int(self.num_channels)
        self.mapper = {}
        for i in range(num_chan):
            setattr(self, f'ch{i+1}', Channel(self, i+1,
                                             wait_for_trigger=self.wait_for_trigger,
                                              start_awg = self.start_awg,
                                              stop_awg = self.stop_awg))
            self.mapper[i + 1] = getattr(self,f'ch{i+1}')

        self.filedir = self.default_dir


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
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop():
                return

    def opc(self):
        return int(self.ask("*OPC?"))

    def start_awg(self):
        self.write(":INIT:IMM")

    def stop_awg(self):
        self.write(':ABOR')

    channel_mode = Instrument.control(
        ":INST:DACM?",
        ":INST:DACM %s",
        """
        Command to set how many channels are on and if they have markers.
        SING: just channel on is available
        DUAL: channel 1 and 2 are on
        MARK: Channel 1 with channels 3 and 4 as markers,
        DCMa: dual with channels 3 and 4 as markers""",
        validator=strict_discrete_set,
        values=['SING', 'DUAL', 'MARK', 'DCMa']
    )


    sampling_frequency = Instrument.control(
        ":SOUR:FREQ:RAST?", ":SOUR:FREQ:RAST %e",
        """ A floating point property that controls AWG sampling frequency.
        This property can be set.""",
        validator=strict_range,
        values=[100e9, 120e9]
    )

    def intialize_segment(self, channel, array):
        self.write(f':TRAC{channel}:DEF 1, {len(array)}, 0')

    @property
    def waveform_list(self):
        return self.ask(':MMEM:CAT?').replace('"','').split(',')

    filedir = Instrument.control(
        ":MMEM:CDIR?", ':MMEM:CDIR "%s"',
        """ A string property that sets where we are writing wf files.""",
    )
    @staticmethod
    def make_ieee4881(array):
        to_transfer = np.array(array)
        to_transferstr = ''
        for i, val in enumerate(to_transfer):
            if i == 0:
                to_transferstr = to_transferstr + str(val)
            else:
                to_transferstr = to_transferstr + '\n' + str(val)
        l = len(to_transferstr)
        to_transferstr = '#' + str(len(str(l))) + str(l) + to_transferstr

        return to_transferstr
    
    def transfer_array_to_file(self, array, filename):
        """
        Takes an array and saves it to the Documents folder of M8194A
        """
        array_max = np.max(array)
        array_min = np.min(array)
        if array_max > 1 or array_min < -1:
            raise ValueError("Array must be normalized between -1 and 1")
        array = (np.array(array) + 1)/2
        array *= 255
        array -= 128
        array = np.array(array).astype(np.int8)
        if filename + '.bin' in self.waveform_list:
            self.delete_waveform_file(filename)
            print('deleting')
        default_path = self.default_dir + '\\'+ filename +".bin"
        self.adapter.write_binary_values(f':MMEM:DATA "{default_path}", ',
                                            array,
                                            datatype='b',
                                            is_big_endian=False)


    def delete_waveform_file(self, name):
        """
        Deletes waveform in the default directory (you have no choice) with
        name (no suffix).
        """
        default_path = self.default_dir + '\\'+ name +".bin"
        self.write(f':MMEM:DEL "{default_path}"')


    def all_off(self):
        for key, item in self.mapper.items():
            item.disable()



    def transfer_and_load_direct(self, array, wfname:str, channel:int, efficient=False):
        """

        """
        if efficient:
            if wfname in self.waveform_list:
                self.load_waveform_from_file(wfname, channel)
        else:
            to_transferstr = self.make_ieee4881(array)
            self.write(f':TRAC{channel} 1, 0, {to_transferstr}')


    def load_waveform_from_file(self, filename,  channel):
        """
        Loads a waveform at pathtofile to the waveform list with name. Do not try and 
        use this unless you have dumped the file with self.transfer_array_to_file.
        """
        default_path = self.default_dir + '\\'+ filename +".bin"
        self.write(f':TRAC{channel}:IMP 1, "{default_path}", BIN8, IONLy, ON, ALEN')

