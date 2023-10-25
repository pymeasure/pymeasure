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

import pyvisa
from serial.tools import list_ports


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
    rm = pyvisa.ResourceManager()
    instrs = rm.list_resources()
    for n, instr in enumerate(instrs):
        # trying to catch errors in comunication
        try:
            res = rm.open_resource(instr)
            # try to avoid errors from *idn?
            try:
                # noinspection PyUnresolvedReferences
                idn = res.query('*idn?')[:-1]
            except pyvisa.Error:
                idn = "Not known"
            finally:
                res.close()
                print(n, ":", instr, ":", idn)
        except pyvisa.VisaIOError as e:
            print(n, ":", instr, ":", "Visa IO Error: check connections")
            print(e)
    rm.close()
    return instrs


def find_serial_port(vendor_id=None, product_id=None, serial_number=None):
    """Find the VISA port name of the first serial device with the given USB information.

    Use `None` as a value if you do not want to check for that parameter.

    .. code-block:: python

        resource_name = find_serial_port(vendor_id=1256, serial_number="SN12345")
        dmm = Agilent34410(resource_name)

    :param int vid: Vendor ID.
    :param int pid: Product ID.
    :param str sn: Serial number.
    :return str: Port as a VISA string for a serial device (e.g. "ASRL5" or "ASRL/dev/ttyACM5").
    """
    for port in sorted(list_ports.comports()):
        if ((vendor_id is None or port.vid == vendor_id)
                and (product_id is None or port.pid == product_id)
                and (serial_number is None or port.serial_number == str(serial_number))):
            # remove "COM" from windows serial port names.
            port_name = port.device.replace("COM", "")
            return "ASRL" + port_name
    raise AttributeError("No device found for the given data.")
