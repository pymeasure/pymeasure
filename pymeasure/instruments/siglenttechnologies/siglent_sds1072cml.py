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
from pymeasure.instruments.validators import strict_discrete_range,truncated_discrete_set,strict_range

class VoltageChannel(Channel):

    """ Implementation of a SIGLENT SDS1072CML Oscilloscope channel

    """
    vertical_division=Channel.control(
        "C{ch}:VDIV?","C{ch}:VDIV %s",
        "Sets or gets the vertical sensitivity of a channel.",
        validator=truncated_discrete_set,
        values={
                2e-3:"2.00E-03V",5e-3:"5.00E-03V",
                1e-2:"1.00E-02V",2e-2:"2.00E-02V",5e-2:"5.00E-02V",
                1e-1:"1.00E-01V",2e-1:"2.00E-01V",5e-1:"5.00E-01V",
                1e+0:"1.00E+00V",2e+0:"2.00E+00V",5e+0:"5.00E+00V",
                1e+1:"1.00E+01V"
                },
        get_process= lambda v : v.split(" ",1)[-1],
        map_values=True
    )
    coupling=Channel.control(
        "C{ch}:CPL?","C{ch}:CPL %s1M",
        "Sets and gets the channel coupling mode. (see UM p. 35)",
        validator=truncated_discrete_set,
        values={"AC":"A","DC":"D"},
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
        validator=truncated_discrete_set,
        values={5e-9:"5.00E-09S",
                1e-8:"1.00E-08S",2.5e-8:"2.50E-08S",5e-8:"5.00E-08S",
                1e-7:"1.00E-07S",2.5e-7:"2.50E-07S",5e-7:"5.00E-07S",
                1e-6:"1.00E-06S",2.5e-6:"2.50E-06S",5e-6:"5.00E-06S",
                1e-5:"1.00E-05S",2.5e-5:"2.50E-05S",5e-5:"5.00E-05S",
                1e-4:"1.00E-04S",2.5e-4:"2.50E-04S",5e-4:"5.00E-04S",
                1e-3:"1.00E-03S",2.5e-3:"2.50E-03S",5e-3:"5.00E-03S",
                1e-2:"1.00E-02S",2.5e-2:"2.50E-02S",5e-2:"5.00E-02S",
                1e-1:"1.00E-01S",2.5e-1:"2.50E-01S",5e-1:"5.00E-01S",
                1e0:"1.00E+00S",2.5e0:"2.50E+00S",5e0:"5.00E+00S",
                1e1:"1.00E+01S",2.5e1:"2.50E+01S",5e1:"5.00E+01S",
                },
                map_values=True,
                get_process=lambda v: v.split(" ",1)[-1]
    )
    status=Instrument.control(
        "SAST?",None,
        "Queries the sampling status of the scope (Stop, Ready, Trig'd, Armed)",
        get_process= lambda v : v.split(" ",1)[-1]
    )
    internalState=Instrument.control(
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
    stop=Instrument.control(
        "STOP",None,
        "Stops all acquisitions"
    )
    wait=Instrument.control(
        None,"WAIT %d",
        "Stops the scope from doing anything until it has completed the current acquisition (p.146)"
    )
    arm=Instrument.control(
        "ARM",None,
        "Changes the acquisition mode from 'STOPPED' to 'SINGLE'. Useful to ready scope for the next acquisition."
    )
    trigger_setup=Instrument.control(
        ":TRIG_SELECT?","TRSE %s,SR,%s,HT,%s,HV,%s",
        """ Read and set trigger setup as a dict containing the following keys:

        - "trigger_type": condition that will trigger the acquisition of waveforms [edge,
          slew,glit,intv,runt,drop]
        - "source": trigger source [c1,c2,c3,c4]
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
#    #Maybe make this a little more elegant? make a trigger channel?
#    @property
#    def trigger_source=Instrument.control(
#        "TRIG_SELECT?","TRSE %s,SR,%s",
#        "Sets the oscilloscope trigger to a specific type () the specified channel (str, {EX,EX/5,C1,C2})",
#        validator=truncated_discrete_set,
#        values=["EX","EX/5","C1","C2"],
#        get_process=lambda v : v[2].split(" ",1)[-1]
#    )
