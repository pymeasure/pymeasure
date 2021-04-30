# -*- coding: utf-8 -*-
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

from pymeasure.instruments import Instrument
from enum import IntFlag



log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



class HP3478A(Instrument):
    """ Represents the Hewlett Packard 3748A 5 1/2 digit multimeter
    and provides a high-level interface for interacting
    with the instrument.

    As this unit predates SCPI some tricks are required to get this working
    """


    MODES={"DCV": "F1",
           "ACV": "F2",
           "R2W": "F3",
           "R4W": "F4",
           "DCI": "F5",
           "ACI": "F6",
           "Rext": "F7"
           }

    RANGES={"DCV": {3E-2: "R-2",3E-1: "R-1",3: "R0",30: "R1",300:"R2","auto": "RA"},
            "ACV": {3E-1: "R-1",3: "R0",30: "R1" ,300: "R2","auto": "RA"},
            "R2W": {30: "R1",300: "R2", 3E3: "R3",3E4: "R4",3E5: "R5", 3E6: "R6",
                    3E7: "R7","auto": "RA"},
            "R4W": {30: "R1",300: "R2", 3E3: "R3",3E4: "R4",3E5: "R5", 3E6: "R6",
                    3E7: "R7","auto": "RA"},
            "DCI": {3E-1: "R-1",3: "R0","auto": "RA"},
            "ACI": {3E-1: "R-1",3: "R0","auto": "RA"},
            "Rext": {3E6: "R7","auto": "RA"}
            }

    TRIGGERS={
        "auto": "T1",
        "internal": "T1",
        "external": "T2",
        "single": "T3",
        "hold": "T4",
        "fast": "T5"
        }
    

    measurement_string=''
    
    def __init__(self, resourceName, **kwargs):
        super(HP3478A, self).__init__(
            resourceName,
            "Hewlett-Packard HP3478A",
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            **kwargs
        )
    
    @property
    def error_status(self):
        """
        get the Error-status register value

        :return estatus: error status register value (confirm with manual for detail)
        :rtype estatus: int
        """
        estatus=self.ask('E')
        return estatus

    @property
    def status(self):
        """
        Reads the HP3478A status register (5-bytes)

        :return status: list of 5 status bytes (confirm with manual for detail).
        :rtype status: list
        """
        self.write("B")
        status_read=self.adapter.connection.read_bytes(5)
        status=[]
        for i in range(0,5):
            status.append(status_read[i])
        return status

    @property
    def status_readable(self):
        """
        Delivers a human-readble status based on the status() command

        :return hrs: human readable status
        :rtype hrs: str
        """
        status_read=self.status
        d_act=6-(status_read[0]&3)
        m_act=list(self.MODES.keys())[((status_read[0]>>5)&7)-1]
        if m_act=='DCV':
            m_str='V'
        if m_act=='ACV':
            m_str='V'
        if m_act=='DCI':
            m_str='A'
        if m_act=='ACI':
            m_str='A'
        if m_act=='R2W':
            m_str='Ohm'
        if m_act=='R4W':
            m_str='Ohm'
        if m_act=='Rext':
            m_str='Ohm'

        r_act=list(self.RANGES[m_act].keys())[(((status_read[0]>>2)&7)-1)]
        if r_act >=1E6:
            r_str=str(r_act/1E6)+' M'
        elif r_act >=1000:
            r_str=str(r_act/1000)+' k'
        elif r_act <= 1:
            r_str=str(r_act*1000)+' m'
        else:
            r_str=str(r_act)+ ' '

        hrs = '----- HP3478 ----- Status -----\n'
        hrs = hrs + 'The current range is '+r_str+m_str+' with '+str(d_act)+' 1/2 digits\r\n'

        hrs = hrs + 'General status: \r\n'
        hrs = hrs + '     Internal trigger: '+str(status_read[1]&1)+'\r\n'
        hrs = hrs + '     Autorange: '+str(status_read[1]>>1&1)+'\r\n'
        hrs = hrs + '     Auto Zero: '+str(status_read[1]>>2&1)+'\r\n'
        hrs = hrs + '     50 Hz opereration: '+str(status_read[1]>>3&1)+'\r\n'
        hrs = hrs + '     Front/Rear: '+str(status_read[1]>>4&1)+'\r\n'
        hrs = hrs + '     CalibrationRAM en: '+str(status_read[1]>>6&1)+'\r\n'
        hrs = hrs + '     External trigger: '+str(status_read[1]>>7&1)+'\r\n'
        hrs = hrs + 'Srq mask: '+str(status_read[2])+'\r\n'
        hrs = hrs + 'Error status: '+str(status_read[3])+'\r\n'
        hrs = hrs + 'DAC value: '+str(status_read[4])+'\r\n'
        return hrs

    @property
    def auto_zero(self):
        """
        Checks the autozero settings on the HP3478

        :return autozero: 0 --> Autozero off,1 --> Autozero on
        :rtype autozero: int
        """
        status_read=self.status()
        autozero=status_read[1]>>2&1
        return autozero

    @auto_zero.setter
    def auto_zero(self,on_off):
        """
        enable or disable the Autozero feature

        :param on_off: 0 --> disables autozero,1 --> enables autozero.
        :type on_off: int
        """
        if on_off == 1 or on_off == 0:
            self.write('Z{}'.format(on_off))
        else:
            raise Exception(ValueError("Value should be 0 or 1"))

    @property
    def active_connectors(self):
        """
        Status of the front/back conenction terminal switch

        :return front_back: 0 --> back terminals, 1 --> front terminals
        :rtype front_back: int
        """
        status_read=self.status()
        front_back=status_read[1]>>4&1
        return front_back

    @property
    def trigger(self):
        """
        Checks the trigger settings on the HP3478

        :return trigger_stat: string value describing the current status of the trigger
        :rtype trigger_stat: str
        """
        status_read=self.status()
        int_trig=status_read[1]&1
        ext_trig=status_read[1]>>7&1
        if int_trig==1 and ext_trig==0:
            trigger_stat='internal'
        if int_trig==0 and ext_trig==1:
            trigger_stat='external'
        if int_trig==0 and ext_trig==0:
            trigger_stat='hold'
        return trigger_stat

    @trigger.setter
    def trigger(self, trigger_mode):
        """
        sets the trigger mode

        :param trigger_mode: allowed values are: 'auto', 'internal', 'external', 'single', 'hold' or 'fast'
        :type trigger_mode: str
        """
        if trigger_mode in self.TRIGGERS.keys():
            self.write(self.TRIGGERS[trigger_mode])
        else:
            raise Exception(ValueError("Value not allowed"))

    def measure(self,mode='DCV',measurement_range='auto',auto_zero=1,digits=5, trigger='auto'):
        """
        returns a measurement result, depeding on the parameters


        :param mode: optional, measurement mode to be used, valid modes are: 'DCV','ACV','R2W' (2 wire Ohms mode),
            'R4W' (4 wire Ohms mode),'DCI','ACI', 'Rext' (extended Ohms mode, see manual for more detail), defaults to ['DCV']
        :type mode: str
        :param measurement_range: optional, manual selection for the measurement range or 'auto' for auto-ranging, defaults to [auto]
        :type measurement_range: int/str
        :param auto_zero: 0 --> Autozero off,1 --> Autozero on, defaults to [1]
        :type auto_zero: int
        :param digits: Number of digits selection, allowed values are 3,4,5, defaults to [5]
        :type digits: int
        :param trigger: Trigger mode selection, choices are: 'auto'='internal', 'external', 'single', 'hold', 'fast' (see manual for detail on this), defaults to ['auto']
        :type trigger: str
        :return measured_value: the value mesured based on the settings.
        :rtype measured_value: float
        """
        cached_ms=self.measurement_string
        if mode in self.MODES:
            self.measurement_string=self.MODES[mode]
        else:
            raise Exception(ValueError('Mode string not supported'))

        if measurement_range in self.RANGES[mode]:
            self.measurement_string=self.measurement_string+self.RANGES[mode][measurement_range]
        else:
            raise Exception(ValueError('Value not supported'))

        if auto_zero == 0 or auto_zero == 1:
            self.measurement_string=self.measurement_string+str('Z{}'.format(auto_zero))
        else:
            raise Exception(ValueError('Value not supported'))

        if digits == 3 or digits == 4 or digits == 5:
            self.measurement_string=self.measurement_string+str('N{}'.format(digits))
        else:
            raise Exception(ValueError('Value not supported'))

        if trigger in self.TRIGGERS:
            self.measurement_string=self.measurement_string+self.TRIGGERS[trigger]
        else:
            raise Exception(ValueError('Value not supported'))
      
        if cached_ms==self.measurement_string:
            measured_value=float(self.read())
        else:
            measured_value=float(self.ask(self.measurement_string))
        return measured_value

    def display_reset(self):
        """
        Resets the display of the HP3478A to the normal measurement dusplay.
        Especially helpful after using D2 or D3 command
        """
        self.write('D1')

    def reset(self):
        """
        Initatiates a reset of the HP3478A
        """
        self.adapter.connection.clear()

    def close(self):
        """
        close the current connection to the HP3478A
        """
        self.adapter.connection.close()

    def shutdown(self):
        """
        provides a way to gracefully close the conention to the HP3478A
        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
