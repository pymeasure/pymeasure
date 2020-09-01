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

from pymeasure.instruments import Instrument, discreteTruncate
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, truncated_range

import numpy as np
import time
import re


class ApexAP1000(Instrument):
    """Represents Apex's AP1000 Multi-test platform"""
    SLOTS = range(1,9)
    DEV_KINDS = {'PM':'POW','TF':'FLT','TL':'TLS'}
    PM_CHANNELS = [1,2]
    PM_UNIT = ['W','mW','dBm']
    STATUS = {'Off':0,'On':1}


    def __init__(self, resourceName, **kwargs):
        super(ApexAP1000, self).__init__(
            resourceName,
            "Apex AP1000",
            **kwargs
        )
        self.__slot = None

    def headStr(self,kind):
        return ApexAP1000.DEV_KINDS[kind]+"[%02d]:"%self.slot

    @property
    def slot(self):
        """ Get current slot number
        """
        if self.__slot in ApexAP1000.SLOTS:
            return self.__slot
        else:
            raise ValueError('Bad slot number !')

    @slot.setter
    def slot(self,num):
        """ Set current slot number
        You have to set the good slot before asking the functions related
        to any module
        """
        if num in ApexAP1000.SLOTS:
            self.__slot=num
        else:
            raise ValueError('Bad slot number !')

    # Powermeter module related functions
    @property
    def PM_averages(self):
        """ PowerMeter module.
        Get wanted number of averages for current slot.
        """
        return int(self.ask(self.headStr('PM')+'AVG?'))

    @PM_averages.setter
    def PM_averages(self,num):
        """ PowerMeter module.
        Sets wanted number of averages for current slot.
        """
        self.write(self.headStr('PM')+'AVG %d'%num)

    def PM_getPower(self,channel,unit='W'):
        """ PowerMeter module.
        Get actual power on given channel with given unit.
        - channel can be {}.
        - unit can be {}.
        """
        if unit not in ApexAP1000.PM_UNIT:
            raise ValueError('Unknow physical unit during power measurement')
        if channel not in ApexAP1000.PM_CHANNELS:
            raise ValueError('Unknow channel during power measurement')
        str = {'W':'MW','mW':'MW','dBm':'DBM'}
        value = float(self.ask(self.headStr('PM')+'%s[%d]?'%(str[unit],channel)))
        if unit is 'W':
            value = value * 1e-3
        return value

    def PM_setWavelength(self,channel,wavelength):
        """ PowerMeter module.
        Sets wavelength for given channel for calibration
        - channel can be {}.
        """
        if channel not in ApexAP1000.PM_CHANNELS:
            raise ValueError('Unknow channel during power measurement')
        sentStr = self.headStr('PM')+'SETWAVELENGTH[%d] %g'%(channel,wavelength)
        return self.write(sentStr)

    # tunablefilter module related functions
    @property
    def TF_wavelength(self):
        """ Tunable Filter module.
        Gets tunable filter wavelength.
        """
        return int(self.ask(self.headStr('TF')+'TWL?'))

    @TF_wavelength.setter
    def TF_wavelength(self,wavelength):
        """ Tunable Filter  module.
        Sets tunable filter wavelength.
        """
        self.write(self.headStr('TF')+'TWL %g',wavelength)

    def TF_stopSweep(self):
        """ Tunable Filter  module.
        Stops current wavelength sweep
        """
        self.write(self.headStr('TF')+'TSTO')

    def TF_startSweep(self):
        """ Tunable Filter  module.
        Starts  wavelength sweeping
        """
        self.write(self.headStr('TF')+'TSTGL')

    # tunable laser module related functions
    @property
    def TL_wavelength(self):
        """ Tunable Laser module.
        Gets tunable laser wavelength.
        """
        return int(self.ask(self.headStr('TL')+'TWL?'))

    @TL_wavelength.setter
    def TL_wavelength(self,wavelength):
        """ Tunable Filter  module.
        Sets tunable laser wavelength.
        """
        self.write(self.headStr('TL')+'TWL %d',wavelength)

    @property
    def TL_power(self):
        """ Tunable Laser module.
        Gets tunable laser power.
        """
        return int(self.ask(self.headStr('TL')+'TPDB?'))

    @TL_power.setter
    def TL_power(self,power):
        """ Tunable Filter  module.
        Sets tunable laser power.
        """
        self.write(self.headStr('TL')+'TPDB %d',power)

    def TL_status(self,status):
        """ Tunable Laser module.
        Sets tunable laser On or Off :
        - status is 'On' or 'Off'
        """
        self.write(self.headStr('TL')+'L%d',ApexAP1000.STATUS['status'])
