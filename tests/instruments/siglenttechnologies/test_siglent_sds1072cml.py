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

from time import sleep
import logging
from pymeasure.instruments import list_resources
import numpy as np
import pymeasure
from pymeasure.instruments.siglenttechnologies.siglent_sds1072cml import SDS1072CML
from pyvisa.errors import VisaIOError
import pyvisa
pyvisa.ResourceManager('@py')
#print(pymeasure.__version__)
#print(list_resources())
scope=SDS1072CML('USB0::62700::60986::SDS100P2151785::0::INSTR')
scope.timeDiv
scope.timeDiv=25e-3
print(scope.channel_1.vertical_division)
scope.channel_1.vertical_division=2e-4
scope.channel_1.coupling="AC"
print(scope.channel_1.coupling)
print(scope.is_ready)
scope.arm()

print(scope.trigger_setup)
triggerDict=scope.trigger_setup
triggerDict['trigger_type']=''
scope.trigger_setup=triggerDict
triggerLevel=scope.trigger_level
triggerLevel["trigger_level"]=0.1
scope.trigger_level=triggerLevel

triggerCoupling=scope.trigger_coupling
print(triggerCoupling)
triggerCoupling["trigger_coupling"]='DC'
scope.trigger_coupling=triggerCoupling
triggerSlope=scope.trigger_slope
print(triggerSlope)
triggerSlope["trigger_slope"]='NEG'
triggerSlope["source"]='C2'
scope.trigger_slope=triggerSlope
print(scope.trigger_mode)
scope.trigger_mode="AUTO"
#scope.trigger_setup=("GLIT","C1")
#scp.setCoupling(channel=1,mode='DC')
