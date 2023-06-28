from __future__ import division
import pyvisa as visa
import numpy as np
import serial
import time

rm = visa.ResourceManager()


def get_inst_list():
    """
    Return a list of instruments.
    """
    return rm.list_resources()


class Keithley_24xx(object):
    def __init__(self, fullname):
        self.inst = rm.open_resource(resource_name=fullname)
        return

    def idn(self):
        """
        return IDN
        """
        return self.inst.query("*IDN?")

    def reset(self):
        """
        reset settings to initial values
        """
        self.inst.write("*RST")
        return

    def set_source_mode(self, mode):
        """
        set voltage source or current source
        :param mode: 'voltage' or 'current'
        """
        if mode.lower() in ["voltage", "vol", "v"]:
            self.inst.write(":SOUR:FUNC VOLT")
        elif mode.lower() in ["current", "curr", "i"]:
            self.inst.write(":SOUR:FUNC CURR")
        else:
            raise Exception("unkonwn mode:" + mode)
        return

    def set_sense_mode(self, mode):
        """
        set voltage source or current measurement
        :param mode: 'voltage' or 'current'
        """
        if mode.lower() in ["voltage", "vol", "v"]:
            self.inst.write(":SENS:FUNC VOLT")
        elif mode.lower() in ["current", "curr", "i"]:
            self.inst.write(":SENS:FUNC CURR")
        else:
            raise Exception("unkonwn mode:" + mode)
        return

    def set_autorange(self, on=True):
        """
        enable or disable autorange
        """
        if on == True:
            tmp = "ON"
        else:
            tmp = "OFF"
        self.inst.write(":SENS:CURR:RANG:AUTO {}".format(tmp))
        self.inst.write(":SENS:VOLT:RANG:AUTO {}".format(tmp))
        self.inst.write(":SOUR:CURR:RANG:AUTO {}".format(tmp))
        self.inst.write(":SOUR:VOLT:RANG:AUTO {}".format(tmp))
        return

    def set_voltage(self, v):
        """
        Set voltage, unit V, Sets the current channel.
        """
        self.inst.write(":SOUR:VOLT:LEV {}".format(v))
        return

    def set_current(self, i):
        """
        Set current, unit A, Sets the current channel.
        """
        self.inst.write(":SOUR:CURR:LEV {}".format(i))
        return

    def set_compliance(self, i=None, v=None):
        """
        set the limit of the output current or voltage
        :param i: set compliance current (A)
        :param v: set compliance voltage (V)
        """
        if i is not None:
            self.inst.write(":SENS:CURR:PROT {}".format(i))
        if v is not None:
            self.inst.write(":SENS:VOLT:PROT {}".format(v))
        return

    def ch_status(self, status=""):
        """
        Set/Get channel status
        if status is None, this function returns the status of the channel.
        if status is True/False, it enable/disable the channel
        """
        if status.lower() == "on":
            self.inst.write(":OUTP ON")
        elif status.lower() == "off":
            self.inst.write(":OUTP OFF")
        else:
            status = self.inst.query(":OUTP:STAT?")
        return status

    def measure(self):
        a = self.inst.query(":READ?")
        values = np.asarray(a.rstrip().split(","), dtype=float)
        volts = values[0]
        amps = values[1]
        return volts, amps


class Agilent_PowerMeter(object):
    def __init__(self, fullname):
        """
        Work with Agilent power meters
        """
        self.inst = rm.open_resource(fullname)
        self.name = fullname
        return

    def idn(self):
        """
        return IDN
        """
        return self.inst.query("*IDN?")

    def PowerMeter(self, ch=1):
        """
        get power meter measured value
        """
        p = self.inst.query("fetc1:chan{}:pow?".format(ch))
        return float(p.rstrip().split("<")[0])

    def read_wavelength(self, ch=1):
        """
        get power meter wavelength measured value in nm
        """
        p = self.inst.query(":SENS1:CHAN{}:POW:WAV?".format(ch))
        return 1e9 * float(p.rstrip().split("<")[0])

    def set_wavelength(self, ch, wav):
        """
        set wavelength (nm). wave is in nm.
        """
        self.inst.write(":SENS1:CHAN{}:POW:WAV {}".format(ch, wav * 1e-9))
        return

    def set_cal_offset(self, ch, dB):
        """
        set wavelength (nm). wave is in nm.
        """
        self.inst.write(":SENSE1:CHAN{}:CORR {}".format(ch, dB))
        return

    def read_cal_offset(self, ch):
        """
        set wavelength (nm). wave is in nm.
        """
        dB = self.inst.query(":SENSE1:CHAN{}:CORR?".format(ch))
        return float(dB.rstrip().split("<")[0])

    def set_averaging_time(self, atime):
        """
        set averaging time in seconds
        """
        self.inst.write(":SENSE1:CHAN1:POW:ATIM {}".format(atime))
        return

    def read_averaging_time(self):
        """
        read averaging time in seconds
        """
        atime = self.inst.query(":SENSE1:CHAN1:POW:ATIM?")
        return float(atime.rstrip().split("<")[0])

    def set_power_unit(self, ch, unit=0):
        """
        set power meter unit, unit=0 for dBm, unit=1 for W
        """
        self.inst.write(":SENSE1:CHAN{}:POW:UNIT {}".format(ch, unit))
        return

    def set_autorange(self, ch, auto=1):
        """
        set auto range, 1=ON, 0=OFF
        """
        self.inst.write(":SENSE1:CHAN{}:POW:RANGE:AUTO {}".format(ch, auto))
        return

    def start_minmax_mode(self):
        self.inst.write(":SENSE1:FUNC:STAT MINM,STAR")
        return

    def stop_minmax_mode(self):
        self.inst.write(":SENSE1:FUNC:STAT MINM,STOP")
        return

    def set_minmax_mode(self, mode, nsample=100):
        """
        set minmax mode
        mode = "CONT", "WIND", "REFR"
        nsample = number of samples when mode=window
        """
        self.inst.write(":SENSE1:FUNC:PAR:MINM {},{}".format(mode, nsample))
        return

    def get_minmax_state(self):
        result = self.inst.query("SENSE1:FUNC:STAT?")
        return result.rstrip().split(",")[1]

    def get_minmax_result(self, ch):
        result = self.inst.query("SENSE1:CHAN{}:FUNC:RES?".format(ch))
        minimum = float(result.split(",")[0].split(":")[1])
        maximum = float(result.split(",")[1].split(":")[1])
        return minimum, maximum, maximum - minimum


class Thorlabs_TEC(object):
    def __init__(self, address="COM5"):
        self.inst = serial.Serial(address, baudrate=115200, timeout=10)
        self.type = self.get_TEC_type()
        return

    def read(self):
        serialString = ""  # Used to hold data coming over UART
        while True:
            # Wait until there is data waiting in the serial buffer
            if self.inst.in_waiting > 0:
                # Read data out of the buffer until a carraige return / new line is found
                serialString = serialString + self.inst.read().decode("utf-8")
            else:
                break
        return serialString.rstrip()

    def query(self, command):
        for i in range(10):
            self.inst.write(command.encode())
            time.sleep(1)
            nbytes = self.inst.in_waiting
            if nbytes > 0:
                response = self.read()
                return response
        print("failed query")
        response = ""
        return response

    def get_TEC_type(self):
        TEC_type = self.query("m?/n")
        return TEC_type

    def get_set_temperature(self):
        mC = self.query("T?/n")
        degreesC = float(mC) / 1000
        return degreesC

    def get_actual_temperature(self):
        mC = self.query("Te?/n")
        degreesC = float(mC) / 1000
        return degreesC

    def set_temperature(self, degreesC):
        command = "T" + str(int(degreesC * 1000)) + "/n"
        print(command)
        n = self.inst.write(command.encode())
        return n
