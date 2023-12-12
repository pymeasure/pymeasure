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

"""
This example demonstrates how to control HP 34401A by SCPI on RS232 connection.
- Correct the RS232 Baud and Parity for your instrument

Run the program by changing to the directory containing this file and calling:
python hp34401a_rs232.py /dev/ttyUSB0
"""

import logging
import time
import serial
from pymeasure.adapters import SerialAdapter
from pymeasure.instruments.hp import HP34401A
import argparse

parser = argparse.ArgumentParser(description="HP 34401A read voltage")
parser.add_argument("serial", help="Serial port name")
args = parser.parse_args()

log = logging.getLogger('')
logging.getLogger().addHandler(logging.StreamHandler())
log.setLevel(logging.INFO)

adapter = SerialAdapter(port=args.serial,
                        baudrate=1200,  # Recommend value
                        parity=serial.PARITY_NONE,
                        stopbits=serial.STOPBITS_TWO,
                        bytesize=serial.EIGHTBITS,
                        xonxoff=True,
                        dsrdtr=True,
                        rtscts=False,
                        write_termination='\n',
                        read_termination='\n',
                        )
meter = HP34401A(adapter)
meter.reset()  # wait for reset
meter.clear()
meter.write('SYSTem:REMote')
time.sleep(1)
meter.status  # for flush input buffers
print('meter: {}, SCPI: {}, terminals: {}'.format(
    meter.id, meter.scpi_version, meter.terminals_used))

meter.function_ = 'DCV'
meter.range_ = 100
meter.resolution = 0.0001
meter.sample_count = 1
# meter.nplc = 0.02
# meter.autozero_enabled = False
# meter.trigger_count = 1
meter.trigger_delay = "MIN"

meter.displayed_text = 'TEST'
# meter.display_enabled = False
while True:
    voltage = meter.reading
    print("Measuring voltage: {} {}".format(voltage, "V"))

