"""
.. codeauthor:: Kevin Kennedy <protonyx@users.noreply.github.com>

Connecting to the Instrument
----------------------------

The Regatron sources can be outfitted with Ethernet-to-USB adapters for use
with the TopCon software. In order to connect to the source with an adapter
installed, you must install the drivers so that the device appears as a
local COM port to the operating system.
"""
from pymeasure.instruments import Instrument
from pymeasure.adapters.serial import SerialAdapter

import numpy as np

import struct
import serial

import time

timeout_rise_voltage = 0.1
timeout_rise_power = 0.1

class Regatron():
    """
    Driver for Regatron TopCon compatible Power Supplies
    """
    
    def __init__(self, port_str):            
        self.port = serial.Serial(port=port_str,baudrate=38400, bytesize=8, parity='N', stopbits=1, timeout=1.0)

    def open(self):
        # Configure the COM Port
        if not self.port.is_open:
            self.port.open()
        self._serial = self.getSerialNumber()
        self._fw = self.getFirmwareVersion()
    
    def close(self):
        self.port.close()
    
    def getProperties(self):
        return {
            'deviceVendor':     'Regatron',
            'deviceModel':      'TopCon Device',
            'deviceSerial':     self._serial,
            'deviceFirmware':   self._fw
        }
    
    def _sendFrame(self, frame):
        """
        Send a frame
        
        Calculates the checksum and attaches a header to the outgoing
        data frame.
        
        Checksum is calculated by adding all data bytes, then mod by 0x100
        First byte is a sync byte, it is always 0xA5
        
        :returns: None
        """
        fmt = 'BBB'
        
        total = 0
        for bt in bytearray(frame):
            total += bt
        checksum = total % 0x100
        
        header = struct.pack(fmt, 0xA5, len(frame), checksum)
        
        full = header + frame
        
        self.port.write(full)
        self.port.flush()
        
    def _recvFrame(self):
        """
        Receive a frame
        
        Reads the header first to find out how many bytes to receive
        in the payload section
        
        :returns: byte string, payload section of frame
        """
        header = self.port.read(3)
        
        sync, len, checksum = struct.unpack('BBB', header)
        # TODO Verify checksum?
        
        payload = self.port.read(len)
        
        return payload
        
    def _cmdReadMemoryWord(self, address):
        """
        Read a memory word
        
        Talk ID: 0x10
        Address is Little-endian (Least Significant Byte first)
        
        :returns: int16
        """
        frame = struct.pack('BBBB', 0x10, address&0xFF, (address>>8)&0xFF, (address>>16)&0xFF)
        
        self._sendFrame(frame)
        
        ret = self._recvFrame()
        
        try:
            talkid, status, datal, datah = struct.unpack('BBBB', ret)
            
            # Process returned data
            data = (datah<<8) | (datal)
            if data > 32768:
                data = data-65536;
            return data
        
        except:
            return 0
    
    def _cmdWriteMemoryWord(self, address, data):
        """
        Write a memory word
        
        Talk ID: 0x11
        Address is Little-endian (Least Significant Byte first)
        Data is Little-endian
        
        :returns: bool, True is successful, False otherwise
        """
        frame = struct.pack('BBBBBB', 0x11, address&0xFF, (address>>8)&0xFF, (address>>16)&0xFF, data&0xFF, (data>>8)&0xFF)
        
        self._sendFrame(frame)
        
        ret = self._recvFrame()
        
        try:
            talkid, status = struct.unpack('BB', ret)
            
            # TODO: Check status?
            
            return True
        
        except:
            return False
        
    def powerOn(self):
        """
        Switch on the power supply unit
        """
        self._cmdWriteMemoryWord(0x005089, 1)
        
    def powerOff(self):
        """
        Switch off the power supply unit
        """
        self._cmdWriteMemoryWord(0x005089, 0)
        
    def getErrors(self):
        pass
    
    def clearErrors(self):
        """
        Clear all errors and warnings. In a multi-unit system the errors and 
        warnings of all slave units will be cleared as well.
        """
        self._cmdWriteMemoryWord(0x00508B, 1)

    def selectUnit(self, index):
        """
        Select a unit within the system for queries that require a unit to be
        selected.
        
        Possible values:
        * 0: Master
        * 1-63: Slave
        * 64: System
        
        The slave number (1 ... 63) required for the ModuleSelectIndex depends on 
        the multi-unit operating mode and can be calculated with the values of 
        the multi-unit ID selectors on the front panel according to the 
        following formula:
        
        +==============================+===================+
        | Multi-unit operating mode    | ModuleSelectIndex |
        +==============================+===================+
        | Parallel or series operation | (8 * AH) + AL     |
        +------------------------------+-------------------+
        | Multi-load operation         | (16 * AH) + AL    |
        +------------------------------+-------------------+
        
        :param index: ModuleSelectIndex
        :type index: int
        """
        self._cmdWriteMemoryWord(0x0050D0, index)
        
    def getState(self):
        """
        Returns the state of the selected unit. Select a unit using `selectUnit`.
        
        Possible values with Voltage OFF:
        
          * 'POWERUP'
          * 'READY'
          * 'ERROR'
          * 'STOP'
          
        Possible values with Voltage ON:
        
          * 'RUN'
          * 'WARN'
          
        :returns: str
        """
        states = {
            2: "POWERUP",
            4: "READY",
            12: "ERROR",
            14: "STOP",
            8: "RUN",
            10: "WARN"}
        
        ret = self._cmdReadMemoryWord(0x00508C)
        
        return states.get(ret, "UNKNOWN")
    
    def getMode(self):
        """
        Returns the mode of the selected unit. Select a unit using `selectUnit`.
        
        Possible values:
        
          * 'cv': Constant Voltage
          * 'cc': Constant Current
          * 'cp': Constant Power
          * 'ulim': Usense limit active
          * 'plim': Psense limit active
          * 'cder': Current derating active
          
        :returns: str
        """
        modes = {
            0: 'cv',
            1: 'cc',
            2: 'cp',
            3: 'ulim',
            4: 'plim',
            5: 'cder'}
        
        ret = self._cmdReadMemoryWord(0x0050B8)
        
        return modes.get(ret, 'UNKNOWN')
    
    def getSerialNumber(self):
        """
        Get the firmware serial number.
        
        :returns: str
        """
        sn_h = self._cmdReadMemoryWord(0x005128)
        sn_l = self._cmdReadMemoryWord(0x005129)
        
        sn = (sn_h << 16) | sn_l
        
        ssn = str(sn)
        toadd = ord('A') - ord('0')
        a = chr(ord(ssn[4]) + toadd)
        b = chr(ord(ssn[5]) + toadd)
        
        return "{0:04d}-{1}{2}-{3:04d}".format(int(ssn[0:3]), a, b, int(ssn[6:]))
    
    def getFirmwareVersion(self):
        """
        Get the firmware version
        
        :returns: str
        """
        high = self._cmdReadMemoryWord(0x007E01)
        mid = self._cmdReadMemoryWord(0x007E02)
        low = self._cmdReadMemoryWord(0x007E03)
        
        return "{0:d}.{1:d}.{2:d}".format(high, mid, low)
    
    def getSystemVoltageRange(self):
        """
        Get the minimum and maximum system voltage levels
        
        Units: V
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x005112)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
            
        max_lvl = self._cmdReadMemoryWord(0x00510B)
        
        return min_lvl, max_lvl
    
    def getSystemCurrentRange(self):
        """
        Get the minimum and maximum system current levels
        
        Units: A
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x005113)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
        
        max_lvl = self._cmdReadMemoryWord(0x00510C)
        
        return min_lvl, max_lvl
    
    def getSystemPowerRange(self):
        """
        Get the minimum and maximum system power levels
        
        Units: kW
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x005114)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
        
        max_lvl = self._cmdReadMemoryWord(0x00510D)
        
        return min_lvl, max_lvl
        
    def getModuleVoltageRange(self):
        """
        Get the minimum and maximum voltage levels for the currently selected
        module.
        
        Units: V
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x00510F)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
            
        max_lvl = self._cmdReadMemoryWord(0x005100)
        
        return min_lvl, max_lvl
    
    def getModuleCurrentRange(self):
        """
        Get the minimum and maximum current levels for the currently selected
        module.
        
        Units: A
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x005110)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
            
        max_lvl = self._cmdReadMemoryWord(0x005101)
        
        return min_lvl, max_lvl
    
    def getModulePowerRange(self):
        """
        Get the minimum and maximum power levels for the currently selected
        module.
        
        Units: kW
        
        :returns: tuple (minimum, maximum)
        """
        min_lvl = self._cmdReadMemoryWord(0x005111)
#        if min_lvl > 32768:
#            min_lvl = 65536-min_lvl;
            
        max_lvl = self._cmdReadMemoryWord(0x005102)
        
        return min_lvl, max_lvl
    
    def riseVoltage(self, act_voltage, fin_voltage, max_voltage_step):
        """
        Rise output voltage with max_voltage_step
        """
        voltage_steps=np.linspace(act_voltage, fin_voltage, max_voltage_step)
        for ii, voltage in enumerate(voltage_steps):
            self.setVoltage(voltage=voltage)
            time.sleep(timeout_rise_voltage)
        
        return 

    def setVoltage(self, voltage):
        """
        Set the voltage limit.
        
        Note::
        
           The master unit must be selected using `selectUnit(0)`
           
        :param voltage: Voltage setpoint 
        :type voltage: float
        """
        range = self.getSystemVoltageRange()
        min_lvl, max_lvl = map(float, range)
        
        set_voltage = int(voltage*(4000.0)/max_lvl)
        
        self._cmdWriteMemoryWord(0x005080, set_voltage)
        
    def setCurrent(self, neg, pos):
        """
        Set the forward and reverse current flow limits.
        
        Note::
        
           The master unit must be selected using `selectUnit(0)`
           
        :param neg:     Reverse Current setpoint
        :type neg:      float
        :param pos:     Forward Current setpoint
        :type pos:      float
        """
        range = self.getSystemCurrentRange()
        min_lvl, max_lvl = map(float, range)
        
        set_current_neg = int((neg) * (-4000.0) / min_lvl)
        set_current_pos = int((pos) * (4000.0) / max_lvl)
        
        self._cmdWriteMemoryWord(0x30251D, set_current_neg)
        self._cmdWriteMemoryWord(0x005081, set_current_pos)
        
    def setPower(self, neg, pos):
        """
        Set the forward and reverse power flow limits.
        
        Note::
        
           The master unit must be selected using `selectUnit(0)`
           
        :param neg:     Reverse Power setpoint
        :type neg:      float
        :param pos:     Forward Power setpoint
        :type pos:      float
        """
        range = self.getSystemPowerRange()
        min_lvl, max_lvl = map(float, range)
        
        set_power_neg = int((neg/1000) * (-4000.0) / min_lvl)
        set_power_pos = int((pos/1000) * (4000.0) / max_lvl)
        
        self._cmdWriteMemoryWord(0x30251E, set_power_neg)
        self._cmdWriteMemoryWord(0x005082, set_power_pos)
       
    def getTerminalVoltage(self):
        """
        Get the actual system output voltage
        
        Note::
        
           The module select should be set to system using:  `selectUnit(64)`
        
        :returns: float
        """
        voltage = self._cmdReadMemoryWord(0x005084)
        
        range = self.getSystemVoltageRange()
        min_lvl, max_lvl = map(float, range)
        
        return float((voltage) * (max_lvl) / (4000.0))
        
    def getTerminalCurrent(self):
        """
        Get the actual system output current
        
        Note::
        
           The module select should be set to system using:  `selectUnit(64)`
        
        :returns: float
        """
        current = self._cmdReadMemoryWord(0x005085)
        
        range = self.getSystemCurrentRange()
        min_lvl, max_lvl = map(float, range)
        
        return float((current) * (max_lvl) / (4000.0))
        #=======================================================================
        # # Register Address: 0x005085
        # data = self._cmdReadMemoryWord(0x005085)
        # 
        # # Value Range: 0 - 4000 (4000 = 125 A)
        # # The gain from the datasheet seems to be wrong
        # # This gain was generated by calibration
        # gain = 0.0399877 # 125.0/4000.0
        # current = data * gain
        # return current
        #=======================================================================
        
    def getTerminalPower(self):
        """
        Get the actual system output power
        
        Note::
        
           The module select should be set to system using:  `selectUnit(64)`
        
        :returns: float
        """
        power = self._cmdReadMemoryWord(0x005086)
        
        range = self.getSystemPowerRange()
        min_lvl, max_lvl = map(float, range)
        
        return float((power) * (max_lvl) / (4000.0))
    
    def getVoltagePreset(self):
        """
        """
        range = self.getSystemVoltageRange()
        min_lvl, max_lvl = map(float, range)
        
        voltage_pu = self._cmdReadMemoryWord(0x005080)
        
        voltage = voltage_pu/(4000.0) * max_lvl
        
        return voltage
        
        
    def getCurrentPreset(self):
        """
        """
        range = self.getSystemCurrentRange()
        min_lvl, max_lvl = map(float, range)
        
        current_pu = self._cmdReadMemoryWord(0x005081)
        
        current_preset = current_pu/(4000.0)*max_lvl
        
        return current_preset
        
    def getPowerPreset(self):
        """
        """
        range = self.getSystemPowerRange()
        min_lvl, max_lvl = map(float, range)
        
        power_pu = self._cmdReadMemoryWord(0x005082)
        
        power_preset = power_pu/(4000.0)*max_lvl
        
        return power_preset
    
    def getVoltageLimitQ4(self):
        """

        """
        range = self.getSystemVoltageRange()
        min_lvl, max_lvl = map(float, range)
        
        voltage_pu = self._cmdReadMemoryWord(0x30251F)
        
        voltage = voltage_pu/(4000.0) * max_lvl
        
        return voltage
        
        
    def getCurrentLimitQ4(self):
        """

        """
        range = self.getSystemCurrentRange()
        min_lvl, max_lvl = map(float, range)
        
        current_pu = self._cmdReadMemoryWord(0x30251D)
        
        current_preset = current_pu/(4000.0)*max_lvl
        
        return current_preset
        
    def getPowerLimitQ4(self):
        """

        """
        range = self.getSystemPowerRange()
        min_lvl, max_lvl = map(float, range)
        
        power_pu = self._cmdReadMemoryWord(0x30251E)
        
        power_preset = power_pu/(4000.0)*max_lvl
        
        return power_preset

    def print_preset_value(self):
        print('VQ1[V] = %f' % self.getVoltagePreset())
        print('IQ1[A] = %f' % self.getCurrentPreset())
        print('PQ1[kW] = %f' % self.getPowerPreset())
        print('VQ4[V] = %f' % self.getVoltageLimitQ4())
        print('IQ4[A]  = %f' % self.getCurrentLimitQ4())
        print('PQ4[kW]  = %f' % self.getPowerLimitQ4())