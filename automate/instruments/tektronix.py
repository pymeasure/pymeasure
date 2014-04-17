# Tektronix TDS 2012 (Digital Oscilliscope) Class
#
# Authors: Colin Jermain
# Copyright: 2013 Cornell University
#
from automate.instruments import RangeException, discreteTruncate
from automate.instruments.gpib import GPIBInstrument
from time import sleep
from array import array
import numpy as np
import re

class TDS2012(GPIBInstrument):

    def __init__(self, adapter, address):
        super(TDS2012, self).__init__(adapter, address)
