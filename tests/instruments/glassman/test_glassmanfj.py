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

from pymeasure.instruments.glassman.glassman import Glassman

"""
Unit tests for Glassman class.

This test suite, needs the following setup to work properly:
    - A Glassman Series FJ power supply connected to the computer;
    - The device's address must be set in the RESOURCE constant;
"""

# Device configuration
##################################################
# Name
NAME = "Quadrupole p"

# Address
RESOURCE = "ASRL15::INSTR"

# Max output voltage (V)
MAXV = 2000

# Max output current (A)
MAXI = 0.060
##################################################

def test_get_version(GHV):
    return(GHV.query("V"))

def test_query(GHV):
    return(GHV.query("Q"))

#%% Open connection

QP=Glassman(RESOURCE, NAME)

#%%  Test sequence
print(test_get_version(QP))

print(test_query(QP))
   
#%% Close connection
   
QP.close()
del QP
    