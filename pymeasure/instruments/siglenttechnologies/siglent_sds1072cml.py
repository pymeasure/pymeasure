#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_range,truncated_discrete_set,strict_range,truncated_range
import struct

class VoltageChannel(Channel):

    """ Implementation of a SIGLENT SDS1072CML Oscilloscope channel

    """
    vertical_division=Channel.control(
        "C{ch}:VDIV?","C{ch}:VDIV %s",
        "Sets or gets the vertical sensitivity of a channel.",
        validator=truncated_range,
        values=[2e-3,10],
        get_process= lambda v : float(v.split(" ",1)[-1][:-1]),
        set_process=lambda v: "%.2eV"%v
    )
    coupling=Channel.control(
        "C{ch}:CPL?","C{ch}:CPL %s1M",
        "Sets and gets the channel coupling mode. (see UM p. 35)",
        validator=truncated_discrete_set,
        values={"DC":"D","AC":"A"},
        map_values=True,
        get_process= lambda v : v.split(" ",1)[-1][0],
    )
    def getWaveform(self):
        """
        Returns the waveforms displayed in the channel.
        return:
            time: (1d array) the time in seconds since the trigger epoch for every voltage value in the waveforms
            voltages: (1d array) the waveform in V
        """
        command='C{ch}:WF? DAT2'
        descriptorDictionnary=self.getDesc()
        self.write(command) 
        response=self.read_bytes(count=32)
        rawWaveform=list(struct.unpack_from('%db'%descriptorDictionnary["numDataPoints"],response,offset=descriptorDictionnary["descriptorOffset"]))
        waveform=[point*descriptorDictionnary["verticalGain"]-descriptorDictionnary["verticalOffset"] for point in rawWaveform]
        timetags=[i*descriptorDictionnary["horizInterval"]+descriptorDictionnary["horizOffset"] for i in range(len(rawWaveform))]
        return timetags,waveform

    def getDesc(self):
        '''
        Gets the descriptor of data being sent when querying device for waveform
        :return:
            dict: A dictionnary with the keys:
                numDataPoints: the number of poitns in the waveform
                verticalGain: the voltage increment per code value (in V)
                verticalOffset: the voltage offset to add to the decoded voltage values
                horizInterval: the time interval between points in s
                horizOffset:the offset to add to the time steps
                descriptorOffset: Length of the C1:WF ALL,#9000000346 message
        '''
        command='C{ch}:WF? DESC'
        self.write(command)
        descriptor=self.read_bytes(count=1)
        descriptorOffset=21
        (numDataPoints,)=struct.unpack_from('l',descriptor,offset=descriptorOffset+60)
        (verticalGain,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+156)
        (verticalOffset,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+160)
        (horizInterval,)=struct.unpack_from('f',descriptor,offset=descriptorOffset+176)
        (horizOffset,)=struct.unpack_from('d',descriptor,offset=descriptorOffset+180)
        descriptorDictionnary={
            "numDataPoints":numDataPoints,
            "verticalGain":verticalGain,
            "verticalOffset":verticalOffset,
            "horizInterval":horizInterval,
            "horizOffset":horizOffset,
            "descriptorOffset":descriptorOffset
        }
        return descriptorDictionnary




class SDS1072CML(Instrument):
    """ Represents the SIGLENT SDS1072CML Oscilloscope
    and provides a high-level for interacting with the instrument
    """
    def __init__(self, adapter, name="Siglent SDS1072CML Oscilloscope", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
    channel_1=Instrument.ChannelCreator(VoltageChannel,"1")
    channel_2=Instrument.ChannelCreator(VoltageChannel,"2")

    timeDiv=Instrument.control(
        ":TDIV?",":TDIV %s",
        "Sets the time division to the closest possible value,rounding downwards.",
        validator=truncated_range,
        values=[5e-9,50],
        set_process=lambda v: "%.2eS"%v,
        get_process=lambda v: float(v.split(" ",1)[-1][:-1])
    )
    status=Instrument.control(
        "SAST?",None,
        "Queries the sampling status of the scope (Stop, Ready, Trig'd, Armed)",
        get_process= lambda v : v.split(" ",1)[-1]
    )
    internal_state=Instrument.control(
        "INR?",None,
        "Gets the scope's Internal state change register and clears it.",
        get_process= lambda v : v.split(" ",1)[-1]
    )
    is_ready=Instrument.control(
        "SAST?",None,
        "Checks if the scope is ready for the next acquisition",
        #validator=truncated_discrete_set,
        #values={True:"Stop",True:"Ready",True:"Armed",False:"Trig\'d"},
        #map_values=True,
        get_process= lambda v : True if (v.split(" ",1)[-1] in ["Stop","Ready","Armed"]) else False
    )
    def wait(self,time):
        """
        param time: time in seconds to wait for
        Stops the scope from doing anything until it has completed the current acquisition (p.146)
        """
        self.write("WAIT %d"%int(time))

    def arm(self):
        """
            Changes the acquisition mode from 'STOPPED' to 'SINGLE'. Useful to ready scope for the next acquisition
        """
        if self.is_ready:
            self.write('ARM')
            return True
        else:
            return False
        

    trigger_setup=Instrument.control(
        ":TRIG_SELECT?","TRSE %s,SR,%s,HT,%s,HV,%s",
        """ Read and set trigger setup as a dict containing the following keys:

        - "type": condition that will trigger the acquisition of waveforms [EDGE,
          slew,GLIT,intv,runt,drop]
        - "source": trigger source (str, {EX,EX/5,C1,C2}) 
        - "hold_type": hold type (refer to page 131 of programing guide)
        - "hold_value1": hold value1 (refer to page 131 of programing guide)

        This function fails if the oscilloscope is in alternating trigger mode

        """,
        set_process=lambda dictIn: (
         dictIn.get("type") if dictIn.get("type") is not None else "EDGE",
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         dictIn.get("hold_type") if dictIn.get("hold_type") is not None else "TI",
         dictIn.get("hold_value1") if dictIn.get("hold_value1") is not None else "100NS"
        ),
        get_process=lambda v:{
            "type":v[0].split(" ",1)[-1],
            "source":v[2] ,
            "hold_type":v[4],
            "hold_value1":v[6]
            }
    )
    trigger_level=Instrument.control(
        "TRLV?","%s:TRLV %s",
        """ Read and set trigger level as a dict containning the following keys:

        - "source": trigger source whose level will be changed (str, {EX,EX/5,C1,C2}) 
        - "level": Level at which the trigger will be set (float)
        """,
        set_process=lambda dictIn: (
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         "%.2eV"%dictIn.get("level") if dictIn.get("level") is not None else "0.00E+00V",
        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "level":float(v.split(" ",1)[-1][:-1]),
            }
    )
    trigger_coupling=Instrument.control(
        "TRCP?","%s:TRCP %s",
        """
            Reads or sets the trigger coupling on the provided channel. Expects and returns a dict containing the following keys:
            - "source": trigger source whose coupling will be changed (str, {EX,EX/5,C1,C2}) 
            - "coupling":  (str,{AC,DC}) Coupling to the trigger channel
        """,
        set_process=lambda dictIn: (
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         dictIn.get("coupling") if dictIn.get("coupling") is not None else "DC"

        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "coupling":v.split(" ",1)[-1]
            }
    )
    trigger_slope=Instrument.control(
        "TRSL?","%s:TRSL %s",
        """
            Reads or sets the trigger slope on the provided channel. Expects and returns a dict containing the following keys:
            - "source": trigger source whose slope will be changed (str, {EX,EX/5,C1,C2}) 
            - "trigger_slope": (str,{POS,NEG,WINDOW}) Triggers on rising, falling or Window.
        """,
        set_process=lambda dictIn: (
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         dictIn.get("slope") if dictIn.get("slope") is not None else "POS"

        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "slope":v.split(" ",1)[-1]
            }
    )
    trigger_mode=Instrument.control(
        "TRMD?","TRMD %s",
        """
            Sets the behavior of the trigger following a triggering event (str, {NORM, AUTO, SINGLE,STOP}) 
        """,
        values={"NORM","AUTO","SINGLE","STOP"},
        validator=truncated_discrete_set,
    )
    template=Instrument.control(
        "TMP?",None,
        """
            Returns a copy of the template that describes the various logical entities making up a complete waveform. In
            particular, the template describes in full detail the variables contained in the descriptor part of a waveform.
        """
    )
    def getTemplate(self):
        self.write("TMP?") 
        response=self.read_bytes(count=1)
        return response
    def getWaveAcq(self):
        '''
        Queries the amount of data to be sent from the scope to the controller.
        See page 144 of programming manual
        :return: nuttin
        '''
        return self.ask('WFSU?')
    def waveformSetup(self):
        '''
        Specifies the amount of data to be sent from the scope to the controller.
        See page 144 of programming manual
        :return: nuttin
        '''
        self.write('WFSU SP,0,FP,0')
        return self.getWaveAcq()
        

