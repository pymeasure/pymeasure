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
from pymeasure.instruments.validators import strict_discrete_set


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())



class HP3478A(Instrument):
    """ Represents the Hewlett Packard 3748A 5 1/2 digit multimeter
    and provides a high-level interface for interacting
    with the instrument.

    As this unit predates SCPI some tricks are required to get this working
    """

    DIGITS={3: "N3",
            4: "N4",
            5: "N5"
            }

    AZ={"off": "Z0",
        "on": "Z1"
        }

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
            "R2W": {30: "R1",300: "R2", 3E3: "R3",3E4: "R4",3E5: "R5", 3E6: "R6", 3E7: "R7","auto": "RA"},
            "R4W": {30: "R1",300: "R2", 3E3: "R3",3E4: "R4",3E5: "R5", 3E6: "R6", 3E7: "R7","auto": "RA"},
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

    def __init__(self, resourceName, **kwargs):
        super(HP3478A, self).__init__(
            resourceName,
            "Hewlett-Packard HP3478A",
            includeSCPI=False,
            send_end=True,
            read_termination="\r\n",
            **kwargs
        )


    def error_status(self):
        """
        get the Error-status register value

        Returns
        -------
        estatus : TYPE
            DESCRIPTION.

        """
        estatus=self.ask('E')
        return estatus

    def status(self):
        """
        Reads the HP3478A status register (5-bytes)

        Returns
        -------
        status : TYPE
            DESCRIPTION.

        """
        status_read=self.adapter.connection.query_binary_values("B","b",data_points=5)
        status=[]
        for i in range(0,len(status_read)):
            # print(bin(status_read[i]))
            status.append(status_read[i])
        return status

    # def status_readable(self):
    #     """
    #     Delivers a human-readble status based on the status() command

    #     Returns
    #     -------
    #     None.

    #     """
    #     status_read=self.status()
    #     d_select=status_read[0]&3
    #     r_select=(status_read[0]>>2)&7
    #     m_select=(status_read[0]>>5)&7
    #     print(RANGES[m_select][r_select])
    #     print(DIGITS[d_select])
    #     print(MODES[m_select])
    #     #TODO: add decodung on status byte, e.g. AZ on/off, Front/rear selection
    #     print('General status: ',status_read[1])
    #     print('srq mask: ',status_read[2])
    #     print('Error status: ',status_read[3])
    #     print('DAC value: ',status_read[4])

    @property
    def auto_zero(self):
        """
        Checks the autozero settings on the HP3478

        Returns
        -------
        autozero : int
            0 == Autozero off
            1 == Autozero on

        """
        status_read=self.status()
        autozero=status_read[1]>>2&1
        return autozero

    @auto_zero.setter
    def auto_zero(self,on_off):
        """
        Offers the possibility to enable or disable the Autozero feature

        Parameters
        ----------
        on_off : int
            expects either 0 or 1
            0 --> disabled autozero
            1 --> enables autozero.

        Returns
        -------
        None.

        """
        if on_off==0:
            self.write('Z0')
        else:
            if on_off==1:
                self.write('Z1')

    def active_connectors(self):
        """
        checks the status of the front/back switch, selecting either the front
        or back mearsurement terminals

        Returns
        -------
        front_back : int
            0 == back terminals
            1 == front terminals


        """
        status_read=self.status()
        front_back=status_read[1]>>4&1
        return front_back


    def measure(self,mode='DCV',measurement_range='auto',auto_zero="on",digits=5, trigger='auto'):
        """
        returens a measurement result, depeding on the parameters
        see also the other measure_ functions for the HP3478A.



        Parameters
        ----------
        mode : TYPE, optional
            DESCRIPTION. The default is 'DCV'.
        measurement_range : TYPE, optional
            DESCRIPTION. The default is 'auto'.
        auto_zero : TYPE, optional
            DESCRIPTION. The default is 1.
        digits : TYPE, optional
            DESCRIPTION. The default is 5.
        trigger : TYPE, optional
            DESCRIPTION. The default is 'auto'.

        Returns
        -------
        measured_value : TYPE
            DESCRIPTION.

        """
        measurement_string=''
        if mode in self.MODES:
            measurement_string=self.MODES[mode]
        else:
            raise Exception('Mode string not supported')

        if measurement_range in self.RANGES[mode]:
            measurement_string=measurement_string+self.RANGES[mode][measurement_range]

        if auto_zero in self.AZ:
            measurement_string=measurement_string+self.AZ[auto_zero]

        if digits in self.DIGITS:
            measurement_string=measurement_string+self.DIGITS[digits]

        if trigger in self.TRIGGERS:
            measurement_string=measurement_string+self.TRIGGERS[trigger]

        # print(measurement_string)
        measured_value=float(self.ask(measurement_string))
        return measured_value


    def display_reset(self):


        """
        Resets the display of the HP3478A to the normal measurement dusplay.
        Especially helpful after using D2 or D3 command

        Returns
        -------
        None.

        """
        self.write('D1')

    def reset(self):
        self.adapter.connection.clear()

    def close(self):
        self.adapter.connection.close()

    def shutdown(self):
        self.adapter.connection.clear()
        self.adapter.connection.close()

