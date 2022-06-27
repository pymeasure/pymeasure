#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments.keithley.keithley2750 import clean_closed_channels


def test_clean_closed_channels():
    # Example outputs from `self.ask(":ROUTe:CLOSe?")`
    example_outputs = ["(@)",  # if no channels are open. It is a string and not a list
                       "(@101)",  # if only 1 channel is open. It is a string and not a list
                       ["(@101", "105)"],  # if only 2 channels are open
                       ["(@101", 102.0, 103.0, 104.0, "105)"]]  # if more than 2 channels are open

    assert clean_closed_channels(example_outputs[0]) == []
    assert clean_closed_channels(example_outputs[1]) == [101]
    assert clean_closed_channels(example_outputs[2]) == [101, 105]
    assert clean_closed_channels(example_outputs[3]) == [101, 102, 103, 104, 105]
