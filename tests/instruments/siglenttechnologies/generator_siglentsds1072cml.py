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
from pymeasure.generator import Generator
import pyvisa
from matplotlib import pyplot as plt
pyvisa.ResourceManager('@py')
#print(pymeasure.__version__)
#print(list_resources())
generator=Generator()
scope=generator.instantiate(SDS1072CML,'USB0::62700::60986::SDS100P2151785::0::INSTR')
#scope=SDS1072CML('USB0::62700::60986::SDS100P2151785::0::INSTR')
scope.timeDiv=1e-3
assert scope.timeDiv==1e-3
scope.channel_1.vertical_division=2
assert scope.channel_1.vertical_division==2
scope.channel_1.coupling="AC"
assert scope.channel_1.coupling=="AC"

scope.trigger.setTriggerConfig(source="EX",coupling="DC",level=0.5,slope='POS')


timetag1,waveform1=scope.channel_1.getWaveform()
timetag2,waveform2=scope.channel_2.getWaveform()
generator.write_file("~/Downloads/test_siglent_sds1072cml.py")