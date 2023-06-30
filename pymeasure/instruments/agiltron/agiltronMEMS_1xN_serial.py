# -*- coding: utf-8 -*-
"""
Created on Wed May 17 14:13:51 2023

@author: Sasha
"""

## If USB is not recognized in device manager,
## download drivers from here: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=downloads


import serial

# from pymeasure.instruments import Instrument #, Channel
# from pymeasure.instruments.validators import strict_discrete_set, strict_range, \
    # strict_discrete_range
 
class AGILTRON_1_16():
    def __init__(self, port = 'com7'):
        # super().__init__(adapter, name, **kwargs)
        _baudrate = 115200
        _parity = serial.PARITY_NONE
        _stopbits = serial.STOPBITS_ONE

        self.ser = serial.Serial(port='com7',baudrate = _baudrate, parity=_parity, stopbits=_stopbits, timeout = 2, write_timeout = 2)
        
    def close_connection(self):
        self.ser.close()

    def read_partNumber(self):
        self.ser.write(b"*PN\r")
        self.ser.readline()
        print(self.ser.readline())

    def read_serialNumber(self):
        self.ser.write(b"*SN\r")
        self.ser.readline()
        print(self.ser.readline())

    def set_switch(self, output_channel=1):
        output_channel = str(output_channel)
        if len(output_channel) == 1:
            command = "*SW00{0}\r".format(output_channel)
            self.ser.write(bytes(command, encoding="utf8"))
        elif len(output_channel) == 2:
            command = "*SW0{0}\r".format(output_channel)
            self.ser.write(bytes(command, encoding="utf8"))
        self.ser.readline()
        print(self.ser.readline())
            
if __name__ =='__main__':
    switch = AGILTRON_1_16('COM7')

    switch.read_partNumber()
    switch.set_switch(15)
    switch.close_connection()





# _baudrate = 115200
# _parity=serial.PARITY_NONE
# _stopbits=serial.STOPBITS_ONE
# _bytesize=serial.EIGHTBITS


# switch_1_16 = serial.Serial(port='com6',baudrate = _baudrate, parity=_parity, stopbits=_stopbits, bytesize=_bytesize)

# switch_1_16.write(b'*PN\r')

# x = switch_1_16.readline()
# print(x)
# x = switch_1_16.readline()
# print(x)

# switch_1_16.write(b'*SN\r')

# x = switch_1_16.readline()
# print(x)
# x = switch_1_16.readline()
# print(x)

# switch_1_16.write(b'*SW002\r')

# x = switch_1_16.readline()
# print(x)
# x = switch_1_16.readline()
# print(x)


# switch_1_16.close()
