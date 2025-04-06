#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


BOOL_MAPPINGS = {True: 1, False: 0}


class AgilentE4418BChannel(Channel):
    """Implementation of a base Agilent E4418B channel"""

    def abort(self):
        """Aborts channel"""
        self.write("ABOR{ch}")

    def init(self):
        """Set channel to make ameasurement"""
        self.write("INIT{ch}")

    power = Instrument.measurement(
        "MEAS{ch}?",
        "Measure power"
    )

    fetc = Instrument.measurement(
        "FETC{ch}?",
        "Get measured value"
        )

    averaging = Instrument.control(
        "SENS{ch}:AVER:COUN?", "SENS{ch}:AVER:COUN %i",
        "Control averaging (int)",
        validator=strict_range,
        values=[0, 1024],
        cast=int
    )

    averaging_enabled = Instrument.control(
        "SENS{ch}:AVER?", "SENS{ch}:AVER %i",
        "Control averaging enabled",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    averaging_auto_enabled = Instrument.control(
        "SENS{ch}:AVER:COUN:AUTO?", "SENS{ch}:AVER:COUN:AUTO %i",
        "Control auto averaging",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    display_resolution = Instrument.control(
        "DISP:WIND{ch}:RES?", "DISP:WIND{ch}:RES %i",
        "Control display resolution (int)",
        validator=strict_range,
        values=[1, 4],
        get_process=lambda getlist: int(getlist[1])
    )

    frequency = Instrument.control(
        "SENS{ch}:FREQ?", "SENS{ch}:FREQ %iHZ",
        "Control frequency in Hz (int)",
        validator=strict_range,
        values=[1000, 999900000000]
    )

    offset = Instrument.control(
        "SENS{ch}:CORR:GAIN{ch}?", "SENS{ch}:CORR:GAIN{ch} %f",
        "Control offset in (float)"
    )


class AgilentE4418B(SCPIMixin, Instrument):
    """
    Represents the Agilent E4418B Power Meter
    TODO: implement get_status

    .. code-block:: python

        instr =  vxi11.Instrument("192.168.88.116", "gpib0,13")
        pm = agilentE4418B.AgilentE4419B(instr);
        pm.reset()
        pm.clear()
        pm.remote_control_enabled = True
        pm.unit = "W"
        read_unit = pm.unit
        print(f'readB unit: {read_unit}')
        pm.powerref_enabled = True
        print(f'readB powerref: {pm.powerref_enabled}')

        pm.channels[2].abort()
        pm.channels[2].averaging = 1
        pm.channels[2].offset = 0
        print(f'readB offset: {pm.channels[2].offset}')
        print(f'readB averaging: {pm.channels[2].averaging}')
        pm.channels[2].averaging_enabled = False
        pm.channels[2].display_resolution = 2
        print(f'readB resolution: {pm.channels[2].resolution}')
        pm.channels[2].frequency = 50
        print(f'readB frequency: {pm.channels[2].frequency}')
        pm.channels[2].init()

        while True:
            print(f'powerB: {pm.channels[2].power}{read_unit}')
            time.sleep(0.1)
    """

    ch_1 = Instrument.ChannelCreator(AgilentE4418BChannel, 1)

    def __init__(self, adapter, name="Agilent E4418B Power Meter",
                 **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )

    powerref_enabled = Instrument.control(
        "OUTP:ROSC?", "OUTP:ROSC %d",
        "Control power reference. (bool)",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    unit = Instrument.control(
        "UNIT:POW?", "UNIT:POW %s",
        "Control measure unit (str)",
        validator=strict_discrete_set,
        values={"W", "DBM", "DB"}
    )

    disp_enable = Instrument.control(
        "DISP:ENAB?", "DISP:ENAB %d",
        "Control display enable. (bool)",
    )


class AgilentE4419B(AgilentE4418B):
    """Represents the Agilent E4419B Power Meter
    TODO: implement ratio mesurement
    """

    ch_2 = Instrument.ChannelCreator(AgilentE4418BChannel, 2)

    def __init__(self, adapter, name="Agilent E4419B Power Meter",
                 **kwargs):
        super().__init__(
            adapter, name, **kwargs
        )
