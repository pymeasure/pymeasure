#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

        - "trigger_type": condition that will trigger the acquisition of waveforms [EDGE,
          slew,GLIT,intv,runt,drop]
        - "source": trigger source (str, {EX,EX/5,C1,C2}) 
        - "hold_type": hold type (refer to page 131 of programing guide)
        - "hold_value1": hold value1 (refer to page 131 of programing guide)

        This function fails if the oscilloscope is in alternating trigger mode

        """,
        set_process=lambda dictIn: (
         dictIn.get("trigger_type") if dictIn.get("trigger_type") is not None else "EDGE",
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         dictIn.get("hold_type") if dictIn.get("hold_type") is not None else "TI",
         dictIn.get("hold_value1") if dictIn.get("hold_value1") is not None else "100NS"
        ),
        get_process=lambda v:{
            "trigger_type":v[0].split(" ",1)[-1],
            "source":v[2] ,
            "hold_type":v[4],
            "hold_value1":v[6]
            }
    )
    trigger_level=Instrument.control(
        "TRLV?","%s:TRLV %s",
        """ Read and set trigger level as a dict containning the following keys:

        - "source": trigger source whose level will be changed (str, {EX,EX/5,C1,C2}) 
        - "trigger_level": Level at which the trigger will be set (float)
        """,
        set_process=lambda dictIn: (
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         "%.2eV"%dictIn.get("trigger_level") if dictIn.get("trigger_level") is not None else "0.00E+00V",
        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "trigger_level":float(v.split(" ",1)[-1][:-1]),
            }
    )
    trigger_coupling=Instrument.control(
        "TRCP?","%s:TRCP %s",
        """
            Reads or sets the trigger coupling on the provided channel. Expects and returns a dict containing the following keys:
            - "source": trigger source whose coupling will be changed (str, {EX,EX/5,C1,C2}) 
            - "trigger_coupling":  (str,{AC,DC}) Coupling to the trigger channel
        """,
        set_process=lambda dictIn: (
         dictIn.get("source") if dictIn.get("source") is not None else "C1",
         dictIn.get("trigger_coupling") if dictIn.get("trigger_coupling") is not None else "DC"

        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "trigger_coupling":v.split(" ",1)[-1]
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
         dictIn.get("trigger_slope") if dictIn.get("trigger_slope") is not None else "POS"

        ),
        get_process=lambda v:{
            "source":v.split(":",1)[0],
            "trigger_slope":v.split(" ",1)[-1]
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
#    #Maybe make this a little more elegant? make a trigger channel?
#    @property
#    def trigger_source=Instrument.control(
#        "TRIG_SELECT?","TRSE %s,SR,%s",
#        "Sets the oscilloscope trigger to a specific type () the specified channel (str, {EX,EX/5,C1,C2})",
#        validator=truncated_discrete_set,
#        values=["EX","EX/5","C1","C2"],
#        get_process=lambda v : v[2].split(" ",1)[-1]
#    )
