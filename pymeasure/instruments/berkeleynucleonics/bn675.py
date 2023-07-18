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

class Marker(object):

    level = Instrument.control(
        "LEVelb?", "LEVelb %g",
        """ A proper controlling the level of the marker output. Into 
        50 Ohms the minimum is 1 V and the max is 2.5 V.""",
    )

    mode = Instrument.control(
        "MODEb?", "MODEb %s",
        """ Sets the behavior of the marker according to mode:
        'FIXEDLow': marker fixed to low level
        'FIXEDHigh': marker fixed to high level
        'AUTOmatic': behavior varies according to run mode
        'REPLYdigital': behaves like digital 0, only works if digital channels > 0 """,
        validator=strict_discrete_set,
        values=['FIXEDLow', 'FIXEDHigh', 'AUTOmatic', 'REPLYdigital'],
    )

    skew = Instrument.control(
        "SKEWb?","SKEWb %g",
        """ A property to set the skew between the marker and analogue channels,
        resolution is 78 ps. Max skew depends on sampling rate""",
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        preprocess = f'MARKer:{command}'
        preprocess = preprocess.replace('b', str(self.number))
        return self.instrument.values(preprocess, **kwargs)

    def ask(self, command):
        preprocess = f'MARKer:{command}'
        preprocess = preprocess.replace('b', str(self.number))
        return self.instrument.query(preprocess)

    def write(self, command):
        preprocess = f'MARKer:{command}'
        preprocess = preprocess.replace('b', str(self.number))
        return self.instrument.write(preprocess)

    def read(self):
        self.instrument.read()

class Channel(object):

    inverted = Instrument.control(
        "POLarity?", "POLarity %s",
        """ A boolean property controlling the output polarity. True means the output is inverted.""",
        validator=strict_discrete_set,
        values={True: 'INVerted', False: 'NORMal'},
        map_values=True
    )

    output = Instrument.control(
        "STAT?", "STAT %d",
        """ A boolean property that turns on (True) or off (False) the output
        of the function generator. Can be set. """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
    )

    bloffset = Instrument.control(
        "BLOF?","BLOF %g",
        """ A floating point property that controls the amplitude
        offset. It is always in Volt. This property can be set.""",
        validator=strict_range,
        values=[-2, 2]
    )



    def __init__(self, instrument, number, **kwargs):
        self.instrument = instrument
        self.number = number
        self._elem = None
        self._elemprefix = None

        for key, item in kwargs.items():
            setattr(self, key, item)

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments.
        """
        return self.instrument.values("output%d:%s" % (
                                      self.number, command), **kwargs)
    def ask(self, command):
        self.instrument.query("output%d:%s" % (self.number, command))

    def write(self, command):
        self.instrument.write("output%d:%s" % (self.number, command))

    def read(self):
        self.instrument.read()

    def enable(self):
        self.instrument.write("output%d:state on" % self.number)

    def disable(self):
        self.instrument.write("output%d:state off" % self.number)

    def in_focus(self):
        self.instrument.write('DISPlay:FOCus CH%d' % self.number)

    @property
    def active_sequence_elem(self):
        return self._elem

    @active_sequence_elem.setter
    def active_sequence_elem(self,elem):
        self._elem = elem
        self._elemprefix = f"SEQ:ELEM{elem}:"

    @property
    def waveform(self):
        return self.instrument.ask(self._elemprefix+f"WAV{self.number}?")

    @waveform.setter
    def waveform(self, wfname):
        self.instrument.write(self._elemprefix + f"WAV{self.number} \"{wfname}\"")

    @property
    def waitevent(self):
        return self.instrument.ask(self._elemprefix + f"WAITE?")

    @waitevent.setter
    def waitevent(self, event):
        """
        Can choose:
        NONE: the sequence executes as soon as possible after each segment is done
        MANual: The wait event is triggered by remote *TRG or front pannel button
        TIMer: the wait event is generated by an internal timer
        EXTernal: wait event triggered by Trigger In port.
        """
        self.instrument.write(self._elemprefix + f"WAITE {event}")

    @property
    def pattern(self):
        return self.instrument.ask(self._elemprefix + f"PATTERN?")

    @pattern.setter
    def pattern(self, code):
        """
        Sets the pattern code this element in the sequence is listening for. Limited to [0,255]
        """
        self.instrument.write(self._elemprefix + f"PATTERN {code}")

    @property
    def patternjumptomode(self):
        return self.instrument.ask(self._elemprefix + f"PATTERNJUMPTOMode?")

    @patternjumptomode.setter
    def patternjumptomode(self, code):
        """
        Sets what happens when a pattern code is received. Options are:
        FIRST: jump to the begin of the sequence
        PREVIOUS: jump to the previous element of the sequence [last elem if at first]
        NEXT: Jump to the next element of the sequence [first element if last]
        ITEM: Jump to item define patternjumptoentry
        """
        self.instrument.write(self._elemprefix + f"PATTERNJUMPTOMode {code}")

    @property
    def patternjumptoentry(self):
        return self.instrument.ask(self._elemprefix + f"PATTERNJUMPTOEntry?")

    @patternjumptoentry.setter
    def patternjumptoentry(self, code):
        """
        Sets the elem in the sequence to jump to when the jump is intiated,
        if patternjumpmode is ITEM.
        """
        self.instrument.write(self._elemprefix + f"PATTERNJUMPTOEntry {code}")

    @property
    def amplitude(self):
        return self.instrument.ask(self._elemprefix + f"AMP{self.number}?")

    @amplitude.setter
    def amplitude(self, amp):
        self.instrument.write(self._elemprefix + f"AMP{self.number} {amp}")

    @property
    def offset(self):
        return self.instrument.ask(self._elemprefix + f"OFF{self.number}?")

    @offset.setter
    def offset(self, offset):
        self.instrument.write(self._elemprefix + f"OFF{self.number} {offset}")

    @property
    def elem_length(self):
        return self.instrument.ask(self._elemprefix + f"LENGth?")

    @elem_length.setter
    def elem_length(self, length):
        return self.instrument.write(self._elemprefix + f"LENGth {int(length)}")

    @property
    def elem_repetition(self):
        return self.instrument.ask(self._elemprefix + f"LOOP:COUNt?")

    @elem_repetition.setter
    def elem_repetition(self, length):
        if not isinstance(length, str):
            length = int(length)
        return self.instrument.write(self._elemprefix + f"LOOP:COUNt {length}")


class BN675_AWG(Instrument):
    """Represents the Berkeley nucleonics arbitrary waveform generator. WIP
    This AWG can switch between an AWG and an AFG. This driver is for the AWG. There
    is a SCPI command to switch between them but it is not implemented here.
    Each channel has its own sequencer, but to maintain synchronicity, the length of each
    channels' sequence must be the same. Because this is 2021, the AWG helpfully maintains
    a set of strategies to fix length mismatches from which you may choose. As such, the way
    AWG's are specified is "SEQ:ELEM[n]:WAV[m] wfname" where n is the n'th part in the sequence table and
    m is the channel to put the waveform with wfname.

    """

    burst_n_cycles = Instrument.control(
        "AWGC:BURST?", "AWGC:BURST %d",
        """ Integer parameter setting the number of cycles to burst in burst mode""",
    )

    num_channels = Instrument.measurement(
        "AWGC:CONF:CNUM?", """Returns the number of analog channels on the instrument"""
    )

    run_mode = Instrument.control(
        "AWGControl:RMODe?", "AWGControl:RMODe %s",
        """ A string parameter controlling the AWG run mode. Can be:
        CONT: output continously outputs WF
        BURST: burst n after trigger
        TCON: go into continous mode after trigger
        STEP: each trigger event causes the next wf in sequencer to fire
        ADVA: allows conditional hops around sequencer table""",
        validator=strict_discrete_set,
        values=['CONT', 'BURST', 'TCON', 'STEP', 'ADVA'],
    )

    run_state = Instrument.measurement(
        "AWGC:RSTAT?", """Queries the run state: 0 is stopped
        1 is waiting for trigger, 2 is running"""
    )

    jump_mode = Instrument.control(
        "AWGControl:JUMPM?", "AWGControl:JUMPM %s",
        """ A string parameter controlling the AWG jump mode when a jump code is received.
         Only relevant if run_mode is ADVA. Can be:
        AFTER: Jump after repetitions of current elements are done
        IMM: Jump as soon as possible
        """,
        validator=strict_discrete_set,
        values=['AFTER', 'IMM'],
    )

    send_strobe = Instrument.setting(
        "AWGControl:DJStrobe %d",
        """ An integer setting that initiates a corresponding jump. Valid numbers are between 0 and 255
         Only relevant if run_mode is ADVA:
        """,
        validator=strict_range,
        values=[0,255],
    )

    sampling_frequency = Instrument.control(
        "AWGC:SRAT?", "AWGC:SRAT %e",
        """ A floating point property that controls AWG sampling frequency.
        This property can be set.""",
        validator=strict_range,
        values=[10e6, 1.2e9]
    )

    trigger_source = Instrument.control(
        "TRIGger:SEQUENCE:SOURce?", "TRIGger:SEQUENCE:SOURce %s",
        """ A string parameter to set the whether the trigger is TIMer, EXTernal (BNC),
         or MANual (front panel or software) """,
        validator=strict_discrete_set,
        values=['TIM', 'EXT', 'MAN']
    )


    trigger_slope = Instrument.control(
        "TRIGger:SEQUENCE:SLOPe?", "TRIGger:SEQUENCE:SLOPe %s",
        """ A string parameter to set the whether the trigger edge is POSitive or NEGative, or BOTH""",
        validator=strict_discrete_set,
        values={'POS': 'POS', 'NEG': 'NEG', 'BOTH': 'BOTH'},
        map_values=True
    )

    trigger_level = Instrument.control(
        "TRIGger:SEQUENCE:LEVel?", "TRIGger:SEQUENCE:LEVel %g",
        """ A float parameter that sets the trigger input level threshold. Unclear what the range is,
        0.2 V - 1.4 V is a valid range""",
    )

    trigger_impedance = Instrument.control(
        "TRIGger:SEQUENCE:IMPedance?", "TRIGger:SEQUENCE:IMPedance %s",
        """ An integer parameter to set the trigger input impedance to either 50 or 1000 Ohms""",
        validator=strict_discrete_set,
        values={50: '50 Ohm',1000:'1 KOhm'},
        map_values=True
    )

    sequence_len = Instrument.control(
        "SEQ:LENG?", "SEQ:LENG %d",
        """ Integer atrribute to control the length of the sequence table for all channels""",
    )

    digital_n = Instrument.control(
        "DIG:NUM?", "DIG:NUM %d",
        """ Integer value number of digital channels enabled""",
    )

    digital_v_1 = Instrument.control(
        "DIG:LEV1?", "DIG:LEV1 %f",
        """Output level of Digital Pod A""",
    )

    digital_v_2 = Instrument.control(
        "DIG:LEV2?", "DIG:LEV2 %f",
        """Output level of Digital Pod B""",
    )

    digital_v_3 = Instrument.control(
        "DIG:LEV3?", "DIG:LEV3 %f",
        """Output level of Digital Pod C""",
    )

    digital_v_4 = Instrument.control(
        "DIG:LEV4?", "DIG:LEV4 %f",
        """Output level of Digital Pod D""",
    )

    digital_skew_1 = Instrument.control(
        "DIG:SKEW1?", "DIG:SKEW1 %f",
        """Clock skew of Digital Pod A""",
    )

    digital_skew_2 = Instrument.control(
        "DIG:SKEW2?", "DIG:SKEW2 %f",
        """Clock skew of Digital Pod B""",
    )

    digital_skew_3 = Instrument.control(
        "DIG:SKEW3?", "DIG:SKEW3 %f",
        """Clock skew of Digital Pod C""",
    )

    digital_skew_4 = Instrument.control(
        "DIG:SKEW4?", "DIG:SKEW1 %4",
        """Clock skew of Digital Pod D""",
    )

    @property
    def waveform_list(self):
        return self.ask('WLIST:LIST?').split(',')


    def __init__(self, adapter, **kwargs):
        super(BN675_AWG, self).__init__(
            adapter,
            "BN675 arbitrary waveform generator",
            **kwargs
        )
        self.default_dir = 'C:\\Users\\AWG3000\\Pictures\\Saved Pictures\\'
        num_chan = int(self.num_channels)
        self.mapper = {}
        for i in range(num_chan):
            setattr(self, f'ch{i+1}', Channel(self, i+1,
                                             trigger=self.trigger,
                                             wait_for_trigger=self.wait_for_trigger,
                                              start_awg = self.start_awg,
                                              stop_awg = self.stop_awg))
            self.mapper[i + 1] = getattr(self,f'ch{i+1}')

        for i in range(num_chan//2):
            setattr(self, f'marker{i+1}', Marker(self, i+1))

    def beep(self):
        self.write("system:beep")

    def all_off(self):
        for key, item in self.mapper.items():
            item.output = False

    def set_voltage_format(self, format):
        """
        Sets the way voltages are specified:
        'AMPL': specify voltages as amplitude + offset
        'HIGH': specify voltages as vlow and vhigh #TODO implement these on Channel
        """
        if format not in ['AMPL', 'HIGH']:
            raise ValueError(f'{format} not allowed. Specify AMPL or HIGH')
        self.write('DISP:UNIT:VOLT ' + format)


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
                    "Timeout expired while waiting for the Agilent 33220A" +
                    " to finish the triggering."
                )

            if should_stop():
                return



    def opc(self):
        return int(self.ask("*OPC?"))


    def start_awg(self, timeout=15000):
        """Starts the AWG to run. This may take some time, so we temporarily
         shift the timeout to be more conservative"""
        old_timeout = self.adapter.connection.timeout
        self.adapter.connection.timeout = timeout
        if self.run_state == 0:
            self.write('AWGC:RUN')
        self.adapter.connection.timeout = old_timeout


    def stop_awg(self):
        self.write('AWGC:STOP')

    def transfer_array(self, array, filename):
        """
        Takes an array and saves it to the Saved Pictures directory of the
        BN675
        """
        to_transfer = np.array(array)
        to_transferstr = ''
        for i, val in enumerate(to_transfer):
            if i == 0:
                to_transferstr = to_transferstr + str(val)
            else:
                to_transferstr = to_transferstr + '\n' + str(val)
        l = len(to_transferstr)
        to_transferstr = '#' + str(len(str(l))) + str(l) + to_transferstr
        default_path = self.default_dir + filename +".txt"
        self.write(f'MMEM:DOWN:FNAM "{default_path}"')
        #sleep(.01)
        self.write('MMEM:DOWN:DATA ' + to_transferstr)
        #sleep(.01)

    def delete_all_user(self, key=''):
        self.write('WLIST:WAV:DEL ALL')


    # todo add digital flag to the end of it
    def transfer_and_load(self, array, wfname, efficient=False,cautious=True, wftype='analog'):
        """
        Creates a file in the 'C:\\Users\\AWG3000\\Pictures\\Saved Pictures\\' directory
         with the filename wfname + '.txt' out of the input array (must be a single column).
         That file is then loaded to the waveform list with name wfname. If wfname.txt or wfname
         already exist in then they are overwritten.
        """
        if efficient:
            if wfname in self.waveform_list:
                return
        if cautious:
            wlist = self.waveform_list
            if wfname in wlist:
                self.delete_waveform(wfname)
                self.delete_waveform_file(wfname)
        self.transfer_array(array, wfname)
        self.load_waveform_from_file(wfname, self.default_dir+wfname, wftype)


    def load_waveform_from_file(self, name, pathtofile, wftype):
        #todo implement analog, digital specification

        """
        Loads a waveform at pathtofile to the waveform list with name. The default behavior assumes analog data
        """
        if wftype == 'digital':
            self.write("wlist:waveform:import \"%s\",\"%s\"" % (name,pathtofile+".txt"))
        else:
            self.write("wlist:waveform:import \"%s\",\"%s\"" % (name, pathtofile + ".txt,DIG"))

    def change_directory(self, directory):
        self.write('MMEM:CDIR \"%s\"' % directory)

    def delete_waveform(self, name):
        """
        Defines an empty waveform of name, of integer length size of datatype ('INT' or 'REAL'
        """
        self.write("wlist:waveform:delete \"%s\"" % name)

    def delete_waveform_file(self, filename):
        """
        Deletes the wf file in the default location with default append to name argument
        """
        default_path = self.default_dir + filename + '.txt'
        self.write(f'MMEM:DEL \"{default_path}\"')
