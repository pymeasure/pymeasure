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


class Thorlabs_101PM():
    def __init__(self, device_name):
        self.inst = rm.open_resource(device_name)
        return
    
    def get_ID(self):
        return self.inst.query('*IDN?')

    def set_units(self, unit):
        if unit.upper() != 'W' and unit.upper() != 'DBM':
            print("wrong units")
            return
        else: 
            self.inst.write("SENSE:POW:UNIT "+unit)

    def set_wavelength(self, wavelength):
        if 800 <= wavelength <= 1700:
            self.inst.write("SENSE:CORR:WAV " + str(wavelength))
        else:
            print("wavelength not in the range")
            return
        
    def get_power(self):
        return self.inst.query("MEAS:POW?")
    
    def get_wavelength(self):
        return self.inst.query("SENSE:CORR:WAV?")

    def set_averaging(self,count):
        if 0 <= count <= 40:
            self.inst.write("SENSE:AVERage " + str(count))
        else:
            print("averaging value not it range")
            return

    def set_autorange(self):
        self.inst.query("CURRent:RANGe:AUTO 1")

    def close_connection(self):
        self.inst.close()

    def set_upper_range_dBm(self, power):
        power_W = 10**(power/10)*.001
        self.inst.write("SENSe:POWer:RANGe "+str(power_W))

class Keithley_2230G():
    
    def __init__(self, address) -> None:
        # address = "USB0::0x05E6::0x2230::9208672::INSTR"
        # identification = 'Keithley Instruments, 2230G-30-1, 9208672, 1.16-1.05'

        # Initialize equipment
        self.inst = None
        self.rm = visa.ResourceManager()
        for n in range(3):
            try:
                self.inst = self.rm.open_resource(address)
                break
            except(visa.VisaIOError):
                time.sleep(0.5)
        if self.inst is None:
            raise Exception("Cannot connect to Keithley 2230G")
        self.inst.read_termination = '\n'
        self.inst.write_termination = '\n'
        self.inst.send_end = True
        
        # Verify the identification
    def get_ID(self):
        return self.inst.query("*IDN?")
        # msg = self.inst.query("*IDN?")
        # if msg != identification:
        #     raise Exception("Identification of Keithley 2230G is '%s', which should be '%s'." % (msg, identification))
    
    def reset(self):
        del self.inst
        self.__init__()
        self.inst.write('*RST')
    
    def configure(self, channel: int, voltage: float, compliance: float, enable: bool) -> None:
        assert channel in [1, 2, 3]
        self.inst.write(f'INST:SEL CH{channel}')
        self.inst.write(f"SOURCE:VOLT {voltage}V")
        self.inst.write(f"SOURCE:CURR {compliance}A")
        if enable:
            self.inst.write("SOURCE:OUTP:ENAB ON")
        else:
            self.inst.write("SOURCE:OUTP:ENAB OFF")
    
    def set_output(self, state: bool):
        if state:
            self.inst.write("SOURCE:OUTP ON")
        else:
            self.inst.write("SOURCE:OUTP OFF")

    def measure_voltage(self, channel: int) -> float:
        assert channel in [1, 2, 3]
        self.inst.write(f'INST:SEL CH{channel}')
        return float(self.inst.query(f"MEAS:VOLT? CH{channel}"))

    def measure_current(self, channel: int) -> float:
        assert channel in [1, 2, 3]
        self.inst.write(f'INST:SEL CH{channel}')
        return float(self.inst.query(f"MEAS:CURR? CH{channel}"))

    def enable_front_panel_keys(self):
        self.inst.write("SYST:LOC")
        del self.inst
        print("Please reconnect or reset next time")

    def close_connection(self):
        self.inst.close()


# opm = Thorlabs_101PM('USB0::0x1313::0x8076::M00935805::INSTR')


# opm.set_units('dBm')
# opm.set_averaging(7)
# opm.set_wavelength(1299)
# print(opm.get_power())
# print(opm.get_wavelength())

# opm.close_connection()

# import pyvisa as visa

# rm = visa.ResourceManager()
# print(rm.list_resources())


# inst = rm.open_resource('USB0::0x1313::0x8076::M00935805::INSTR')
# inst.timeout = 2000
# # inst.write_termination = "\n"
# # inst.read_termination = "\n"
# print(inst.query('*IDN?'))


# print(inst.write("SENSE:POW:UNIT DBM"))


# print(inst.query("MEAS:POW?"))
# print(inst.write("SENSE:CORR:WAV 1315"))

# print(inst.query("SENSE:CORR:WAV?"))
# # print(inst.read())





# inst.write('SENS:CORR:wavelength 1310')   #set the operating wavelength to 1310nm
# print(inst.query('SENS:CORR:wavelength?'))
# print(inst.read_bytes(1000, break_on_termchar='\r\n'))