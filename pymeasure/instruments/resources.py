#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

import visa


def list_resources():
    """
    Prints the available resources, and returns a list of VISA resource names
    
    .. code-block:: python

        resources = list_resources()
        #prints (e.g.)
            #0 : GPIB0::22::INSTR : Agilent Technologies,34410A,******
            #1 : GPIB0::26::INSTR : Keithley Instruments Inc., Model 2612, *****
        dmm = Agilent34410(resources[0])
    
    """
    rm = visa.ResourceManager()
    instrs = rm.list_resources()
    for n, instr in enumerate(instrs):
        # trying to catch errors in comunication
        try:
            res = rm.open_resource(instr)
            # try to avoid errors from *idn?
            try:
                # noinspection PyUnresolvedReferences
                idn = res.ask('*idn?')[:-1]
            except visa.Error:
                idn = "Not known"
            finally:
                res.close()
                print(n, ":", instr, ":", idn)
        except visa.VisaIOError as e:
            print(n, ":", instr, ":", "Visa IO Error: check connections")
            print(e)
    rm.close()
    return instrs
