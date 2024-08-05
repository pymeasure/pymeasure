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

from struct import unpack
from enum import Enum

from pymeasure.instruments import Instrument

# class ResponseChar(enum):
#     """
#     Enumeration for the various response codes sent by the instrument
#     """
#     S = "A" # Set expects Acknowledge
#     Q = "R" # Query expects Response
#     V = "B" # Version expects SW version
#     C = "A" # Configure expects Acknowledge

class Glassman(Instrument):
    """
    Represents the Glassman High Voltage power supplies.
    
    This class was written for the FJ Series, but should also work with the
    FR, EJ, ET, and EY Series.
    
    Prerequisites for remote control:
        - Interlock on J3 must be satisfied
        - HV ON function must be enabled via the front panel `HV ON` button or
            Remote `HV ON` pins on J3
    
    
    Supports the following, as defined in `Instruction Manual EJ/ET/EY/FJ/FR
        Series` (102002-177 Rev M2):
            
        Command: Set (S), Query (Q), Version (V), Configure (C)
    
        Response: Acknowledge (A), Response (R), SW Version (B), Error (E)
    
    
    :param adapter: adapter address, "ASRL20::INSTR"
    :param name: Unique device name
    :param voltage_max: Maximum output voltage magnitude in volts
    :param polarity: Voltage polarity, +1 or -1
    :param current_max: Maximum output current magnitude in Ampheres
    """
        
    # Initializer
    def __init__(self, adapter, name="GHV", voltage_max=0, current_max=0, polarity=+1, **kwargs):
        super().__init__(
            adapter,
            name,
            asrl = {'baud_rate': 9600},
            read_termination = '\r',
            write_termination = '\r',
            includeSCPI = False,
            **kwargs
        )
        self.address = adapter
        self.voltage_max = voltage_max
        self.voltage_setpoint = 0
        self.polarity = polarity
        self.current_max = current_max
        self.current_setpoint = 0
        self._output = False
        self._device_timeout = True
        self.value_max = int(0xFFF) # Full scale 12 bit hexadecimal value

    # Class attributes/variables
    class Mode(Enum):
        """
        Enum for the possible modes of operations of the instrument
        """

        #: Constant voltage mode
        voltage = "0"
        #: Constant current mode
        current = "1"
    
    
    # Properties
    @property
    def voltage(self):
        """
        Query the device and return the output voltage
        
        GHV.voltage
        
        """
        print('Setpoint: ', self.voltage_setpoint, ' V')
        print('Output: ', self.status()["Voltage"], ' V')
        return
    
    @voltage.setter
    def voltage(self, value):
        """
        Set the voltage output on the device in +/- volts
        
        GHV.voltage = 0.000
        
        """
        self.voltage_setpoint = value
        if self._output and self.status()["Output"] and self.voltage_setpoint > self.voltage_max * 0.02:
            # If output is off, first setpoint must be < 2% max output
            self.set_status(voltage=self.voltage_max * 0.02)
        self.set_status(voltage=self.voltage_setpoint)        
        return
        
    @property
    def current(self):
        """
        Query the device and return the output current
        
        GHV.current
        
        """
        print('Setpoint: ', self.current_setpoint, ' A')
        print('Output: ', self.status()["Current"], ' A')
        return
    
    @current.setter
    def current(self, value):
        """
        Set the current output on the device in Ampheres
        
        GHV.current = 0.000
        
        """
        self.current_setpoint = value
        if self._output and self.status()["Output"]:
            self.set_status(current=self.current_setpoint)
        return
        
    @property
    def reset(self):
        """
        Reset the device and class properties
        
        GHV.reset
        
        """
        self.voltage_setpoint = 0
        self.current_setpoint = 0
        self._output = False
        self._device_timeout = True
        self.set_status(reset=True)
        print(self.name, ' reset')
        return
    
    @property
    def enable(self):
        """
        Enable the output
        
        GHV.enable
        
        """
        self.set_status(output=True)
        return
    
    @property
    def disable(self):
        """
        Disable the output
        
        GHV.disable
        
        """
        self.set_status(output=False)
        return
    
    # @property
    # def output(self):
    #     """
    #     Gets/sets the output status.

    #     This is a toggle setting. True will turn on the instrument output
    #     while False will turn it off.

    #     :type: `bool`
    #     """
    #     return self.status()["output"]

    # @output.setter
    # def output(self, newval):
    #     if not isinstance(newval, bool):
    #         raise TypeError("Output status mode must be a boolean.")
    #     self.set_status(output=newval)
    
    @property
    def device_timeout(self):
        """
        Gets the timeout instrument side.
        
        GHV.device_timeout

        This is a toggle setting. ON will set the timeout to 1.5
        seconds while OFF will disable it.

        """
        return self._device_timeout

    @device_timeout.setter
    def device_timeout(self, newval):
        """
        Sets the timeout instrument side.
        
        GHV.device_timeout = True | False

        This is a toggle setting. ON will set the timeout to 1.5
        seconds while OFF will disable it.

        :type: `bool`
        """
        if not isinstance(newval, bool):
            raise TypeError("Device timeout mode must be a boolean.")
        
        cmd = format(int(not newval), "01d")
                
        self.query("C" + cmd)  # Device acknowledges
        self._device_timeout = newval
        
    # version = Instrument.measurement(
    #     "V",
    #     """The software revision level of the power supply's data interface. (str)"""
    #     )
    # 
    # output_enabled = Instrument.control(
    #     '',
    #     '',
    #     """Get/Set the power output status. (bool)"""
    #     )
    # 
    # current = Instrument.measurement(
    #     '',
    #     """Measure the output current value"""•
    #     )
    # 
    # voltage = Instrument.measurement(
    #     '',
    #     """Measure the output voltage value"""
    #     )
    # 
    # voltage_setpoint = Instrument.setting(
    #     '',
    #     """Set the output voltage """
    #     )
    
    
    # Methods
    def query(self, command):
        """
        Sends a command to the device and returns the response message
        
            - Prepends SOH and appends computed checksum
            - Validates received message checksum
        
        :param command: Byte string to be written
        :rtype: `string`
        """
        checksum = self._chksum_mod256(command)
        cmd = "\x01" + command + checksum
        super().write(cmd)
        
        # no need to wait fo response
        out = super().read()
        
        if out[0] == 'A':
            return out
        else:
            if self._chksum_mod256(out[1:-2]) != out[-2:]:
                raise ConnectionError(f"Invalid checksum: '{out[-2:]}' != '{checksum}'")
            else:
                return out[1:-2]
    
    def set_status(self, voltage=None, current=None, output=None, reset=False):
        """
        Sets the status on the device
        
        GHV.set_status(0.0, 0.0, False | True, False | True)
        
        """
        if reset:
            cmd = format(4, "013d")
        else:
            # The maximum value is encoded as the maximum of three hex characters (4095)
            cmd = ""

            # If the voltage is not specified, keep it as is
            self.voltage_setpoint = (
                voltage if voltage is not None else self.voltage_setpoint
            )
            ratio = float((self.voltage_setpoint / self.voltage_max) * self.polarity)
            voltage_int = int(round(self.value_max * ratio))
            self._voltage_setpoint = self.voltage_max * float(voltage_int) / self.value_max
            assert 0.0 <= self._voltage_setpoint <= self.voltage_max
            cmd += format(voltage_int, "03X")

            # If the current is not specified, keep it as is
            self.current_setpoint = (
                current if current is not None else self.current_setpoint
            )
            ratio = float(self.current_setpoint / self.current_max)
            current_int = int(round(self.value_max * ratio))
            self._current_setpoint = self.current_max * float(current_int) / self.value_max
            assert 0.0 <= self._current_setpoint <= self.current_max
            cmd += format(current_int, "03X")

            # If the output status is not specified, keep it as is
            self._output = output if output is not None else self._output
            control = f"00{int(self._output)}{int(not self._output)}"
            cmd += format(int(control, 2), "07X")
        
        qry = "S" + cmd
        out = self.query(qry)
        
        if out != 'A':
            raise RuntimeError("Invalid response received: " + qry + " " + out)
        else:
            return
    
    def status(self):
        """
        Prints class properties and queries power supply for a response packet
        that contains the output voltage, output current, and status bits
        
        GHV.status()
        
        :rtype: `dict`
        """
        
        out = self.query("Q")
        
        (voltage_output, current_output, monitors) = unpack("@3s3s3x1c2x", bytes(out, "utf-8"))
        
        try:
            voltage_output = self._parse_voltage(voltage_output)
            current_output = self._parse_current(current_output)
            mode, fault, output = self._parse_monitors(monitors)
        except:
            raise RuntimeError("Cannot parse response packet")
            
        return {
            "Voltage Setpoint": self.voltage_setpoint,
            "Voltage": voltage_output,
            "Current Setpoint": self.current_setpoint,
            "Current": current_output,
            "Mode": mode,
            "Fault": fault,
            "Output": output,
        }
    
    def _parse_voltage(self, word):
        """
        Parses the 3 byte voltage in the response packet

        :param word: Byte string response (R) packet

        :rtype: 
        """
        
        value = int(word.decode("utf-8"), 16)
        value_max = int(0x3FF)
        return self.polarity * self.voltage_max * float(value) / value_max 
    
 
    def _parse_current(self, word):
        """
        Parses the 3 byte current in the response packet

        :param word: Byte string response (R) packet

        :rtype:
        """
        value = int(word.decode("utf-8"), 16)
        value_max = int(0x3FF)
        return self.current_max * float(value) / value_max

    def _parse_monitors(self, word):
        """
        Parses the control mode, fault, and output bits in the response packet

        :param word: Byte string response (R) packet

        :rtype:
        """
        bits = format(int(word, 16), "04b")
        mode = self.Mode(bits[-1])
        fault = bits[-2] == "1"
        output = bits[-3] == "1"
        return mode, fault, output
    
    # def write(self, command):
    #     """
    #     Overrides the adapter's `write` method, prepending the SOH character
    #     and appending the computed message checksum
        
    #     :param command: Byte string to be written
    #     """
    #     checksum = self.chksum_mod256(command)
    #     super().write("\x01" + command + checksum)
    
    # def read(self):
    #     """
    #     Overrides the adapter's `read` method, validating the checksum, and
    #     intrepreting error codes
        
    #     :returns msg: ASCII message
    #     """
    #     out = super().read()
        
    #     checksum = self.chksum_mod256(out[1:-2])
        
    #     if checksum != out[-2:]:
    #         raise ConnectionError(f"Invalid checksum: '{out[-2:]}' != '{checksum}'")
    #     else:
    #         return out[0:-2]
    
    @staticmethod
    def _chksum_mod256(byte_string):
        """
        Calculates the modulo 256 checksum of a byte string.
        
        :param byte_string: Byte string used to compute the checksum
        
        :returns: string corresponding to the hexidecimal value of the checksum, without the `0x` prefix
        """
        characters = list(byte_string)
        total = 0
        for c in characters:
            total += ord(c)
            
        return format(total % 256, "02X")
    
    def close(self):
        """
        Fully closes the connection to the instrument through the adapter connection.
        """
        self.adapter.close()