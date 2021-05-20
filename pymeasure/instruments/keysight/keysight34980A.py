#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from pymeasure.instruments import Instrument, discreteTruncate, RangeException 
import pyvisa as visa
from pyvisa import VisaIOError

class Keysight34980A(Instrument):
    """ Represents the Keysight34980A Multifunction Switch/Measure Unit
    and provides a high-level interface for taking scans with Keysight 34923A 
    Multifunction Switch/Measure Unit.
    """

    def __init__(self,device_address):
        print("Initializing Switch Matrix\n")
        global rm 
        rm = visa.ResourceManager()
        self.switch_data = rm.open_resource(device_address)

    #This command reads the instrument's (mainframe) identification string which contains 
    #four comma-separated fields. The first field is the manufacturer's name, the second 
    #field is the instrument model number, the third field is the serial number, and the 
    #fourth field is a firmware revision code which contains four codes separated by dashes. 
    def is_identification(self):
        return(str(self.switch_data.query('*IDN?')))

    #This command opens all channel relays and Analog Bus relays on the specified multiplexer 
    #or switch module. Alternately by specifying the "ALL" parameter, this command opens 
    #all channels on all installed modules. 
    def set_channel_open_all(self, module = 1):    
        self.switch_data.write(":ROUTe:OPEN:ALL " + str(module))

    #This command opens the specified channel on a multiplexer or switch module.         
    def set_channel_open(self, chan = ""):    
        self.switch_data.write(":ROUTe:OPEN (@" + str(chan) + ")")
        while(self.is_channel_open(chan) == 0):
            self.switch_data.write(":ROUTe:OPEN (@" + str(chan) + ")")

    #This command checks if the specified channel on a multiplexer or switch module is open. 
    def is_channel_open(self, chan = ""):    
        temp_values = self.switch_data.query_ascii_values(":ROUTe:OPEN? (@" + str(chan) + ")")
        return(str(temp_values[0]))

    #This command closes the connections to four Analog Buses on all installed modules. 
    def set_abus_close(self, abus = 1):
        chan = str("192") + str(abus)
        self.set_channel_close(chan)

    #This command opens the connections to four Analog Buses on installed modules. 
    def set_abus_open(self, abus = 1):
        self.switch_data.write(":ROUTe:OPEN:ABUS " + str(abus))
        while(self.is_abus_open(abus) == 1):
            self.switch_data.write(":ROUTe:OPEN:ABUS " + str(abus))

    #This command opens all connections to all four Analog Buses on all installed modules.
    def set_abus_open_all(self):
        self.switch_data.write(":ROUTe:OPEN:ABUS ALL")
        while((self.is_abus_open(1) == 1) and (self.is_abus_open(2) == 1) and (self.is_abus_open(3) == 1) and (self.is_abus_open(4) == 1)):
            self.switch_data.write(":ROUTe:OPEN:ABUS ALL")

    #This command closes all connections to all four Analog Buses on all installed modules.
    def set_abus_close_all(self):
        self.set_channel_close(1921)
        self.set_channel_close(1922)
        self.set_channel_close(1923)
        self.set_channel_close(1924)
        while((self.is_abus_close(1) == 1) and (self.is_abus_close(2) == 1) and (self.is_abus_close(3) == 1) and (self.is_abus_close(4) == 1)):
            self.set_channel_close(1921)
            self.set_channel_close(1922)
            self.set_channel_close(1923)
            self.set_channel_close(1924)

    #This command checks if Analog Buse is open. 
    def is_abus_open(self, abus = ""):    
        chan = str("192") + str(abus)
        return(str(self.is_channel_open(chan)))

    #This command checks if Analog Buse is close. 
    def is_abus_close(self, abus = ""):    
        chan = str("192") + str(abus)
        return(str(self.is_channel_close(chan)))

    #This command closes the specified channel on a multiplexer or switch module.         
    def set_channel_close(self, chan = ""):    
        self.switch_data.write(":ROUTe:CLOSe (@" + str(chan) + ")")
        while(self.is_channel_close(chan) == 0):
            self.switch_data.write(":ROUTe:CLOSe (@" + str(chan) + ")")
    
    #This command checks if the specified channel on a multiplexer or switch module is close. 
    def is_channel_close(self, chan = ""):    
        temp_values = self.switch_data.query_ascii_values(":ROUTe:CLOSe? (@" + str(chan) + ")") 
        return(str(temp_values[0]))

    #This command enables autoranging for ac current measurements on the specified channel.
    def set_ac_current_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO ON")
            while((self.is_ac_current_autorange()) == 0):
                self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO ON")
        else:
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_ac_current_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO ON (@" + str(chan) + ")")

    #This command disables autoranging for ac current measurements on the specified channel.
    def reset_ac_current_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO OFF")
            while((self.is_ac_current_autorange()) == 1):
                self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO OFF")
        else:
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_ac_current_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO OFF (@" + str(chan) + ")")

    #This command checks if autoranging for ac current measurements on the specified channel are enabled.       
    def is_ac_current_autorange(self, chan = ""):     
        if (chan == ""):
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO?") 
            temp_values = self.switch_data.read()
            return(str(temp_values[0]))
        else:    
            self.switch_data.write(":SENSe:CURRent:AC:RANGe:AUTO? (@" + str(chan) + ")") 
            temp_values = self.switch_data.read()
            return(str(temp_values[0]))

    #This command enables autoranging for dc current measurements on the specified channel.
    def set_dc_current_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO ON")
            while((self.is_dc_current_autorange()) == 0):
                self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO ON")
        else:    
            self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_dc_current_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO ON (@" + str(chan) + ")")

    #This command disables autoranging for dc current measurements on the specified channel.
    def reset_dc_current_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO OFF")
            while((self.is_dc_current_autorange()) == 1):
                self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO OFF")
        else:    
            self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_dc_current_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:CURRent:DC:RANGe:AUTO OFF (@" + str(chan) + ")")

    #This command checks if autoranging for dc current measurements on the specified channel are enabled.       
    def is_dc_current_autorange(self, chan = ""):    
        if (chan == ""):
            temp_values = self.switch_data.query_ascii_values(":SENSe:CURRent:DC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:    
            temp_values = self.switch_data.query_ascii_values(":SENSe:CURRent:DC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    #This command enables autoranging for ac voltage measurements on the specified channel.
    def set_ac_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO ON")
            while((self.is_ac_voltage_autorange()) == 0):
                self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO ON")
        else:
            self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_ac_voltage_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO ON (@" + str(chan) + ")")

    #This command disables autoranging for ac voltage measurements on the specified channel.
    def reset_ac_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF")
            while((self.is_ac_voltage_autorange()) == 1):
                self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF")
        else:
            self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_ac_voltage_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF (@" + str(chan) + ")")

    #This command checks if autoranging for ac voltage measurements on the specified channel are enabled.       
    def is_ac_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            temp_values = self.switch_data.query_ascii_values(":SENSe:VOLTage:AC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.switch_data.query_ascii_values(":SENSe:VOLTage:AC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    #This command enables autoranging for dc voltage measurements on the specified channel.
    def set_dc_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
            while((self.is_dc_voltage_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
        else:
            self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_dc_voltage_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO ON (@" + str(chan) + ")")

    #This command disables autoranging for dc voltage measurements on the specified channel.
    def reset_dc_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF")
            while((self.is_dc_voltage_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF")
        else:
            self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_dc_voltage_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF (@" + str(chan) + ")")

    #This command checks if autoranging for dc voltage measurements on the specified channel are enabled.       
    def is_dc_voltage_autorange(self, chan = ""):    
        if (chan == ""):
            temp_values = self.switch_data.query_ascii_values(":SENSe:VOLTage:DC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.switch_data.query_ascii_values(":SENSe:VOLTage:DC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    #This command enables autoranging for resistance measurements on the specified channel.
    def set_resistance_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:RESistance:RANGe:AUTO ON")
            while((self.is_resistance_autorange()) == 0):
                self.switch_data.write(":SENSe:RESistance:RANGe:AUTO ON")
        else:
            self.switch_data.write(":SENSe:RESistance:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_resistance_autorange(chan)) == 0):
                self.switch_data.write(":SENSe:RESistance:RANGe:AUTO ON (@" + str(chan) + ")")

    #This command disables autoranging for resistance measurements on the specified channel.
    def reset_resistance_autorange(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":SENSe:RESistance:RANGe:AUTO OFF")
            while((self.is_resistance_autorange()) == 1):
                self.switch_data.write(":SENSe:RESistance:RANGe:AUTO OFF")
        else:
            self.switch_data.write(":SENSe:RESistance:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_resistance_autorange(chan)) == 1):
                self.switch_data.write(":SENSe:RESistance:RANGe:AUTO OFF (@" + str(chan) + ")")

    #This command checks if autoranging for resistance measurements on the specified channel are enabled.       
    def is_resistance_autorange(self, chan = ""):    
        if (chan == ""):
            temp_values = self.switch_data.query_ascii_values(":SENSe:RESistance:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.switch_data.query_ascii_values(":SENSe:RESistance:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    #The following command configures the instrument for dc voltage measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_dc_voltage(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:VOLTage:DC?")
        dc_voltage = str(temp_values[0])
        return(dc_voltage)

    #The following command configures the instrument for ac voltage measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_ac_voltage(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:VOLTage:AC?")
        return(str(temp_values[0]))

    #The following command configures the instrument for dc current measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_dc_current(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:CURRent:DC?")
        return(str(temp_values[0]))

    #The following command configures the instrument for ac voltage measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_ac_current(self, chan, resolution = "DEFault", range_param = "AUTO"):
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:CURRent:AC?")
        return(str(temp_values[0]))

    #The following command configures the instrument for frequency measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_frequency(self, chan, resolution = "DEFault", range_param = "DEFault"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:FREQuency?")
        return(str(temp_values[0]))

    #The following command configures the instrument for period measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_period(self, chan, resolution = "DEFault", range_param = "DEFault"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:PERiod?")
        return(str(temp_values[0]))

    #The following command configures the instrument for resistance measurements, 
    #triggers the internal DMM to scan the specified channel.
    def measure_resistance(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:RESistance?")
        return(str(temp_values[0]))

    #The following command configures the instrument for temperature measurements on the specified channel.
    def measure_temperature(self, chan, probe = "TCouple", probe_type = "T", resolution = "DEFault", range_param = "AUTO"):   
        temp_values = self.switch_data.query_ascii_values(":MEASure:SCALar:TEMPerature?")
        return(str(temp_values[0]))

    #This command selects the temperature units (°C, °F, or Kelvins) on the specified channels. 
    #If you omit the optional <ch_list> parameter, this command applies to the internal DMM, 
    #independent of any channels or a scan list.
    def set_temperature_unit(self, chan = "", unit = 'K'):    
        if (chan == ""):
            self.switch_data.write(":UNIT:TEMPerature " + str(unit))
            while((self.is_temperature_unit()) != str(str(unit) + "\n")):
                self.switch_data.write(":UNIT:TEMPerature " + str(unit))    
        else:
            self.switch_data.write(":UNIT:TEMPerature " + str(unit) + ", (@" + str(chan) + ")")
            while((self.is_temperature_unit(chan)) != str(str(unit) + "\n")):
                self.switch_data.write(":UNIT:TEMPerature " + str(unit) + ", (@" + str(chan) + ")")

    #The command checks the temperature units (°C, °F, or Kelvins) on the specified channels. 
    #If you omit the optional <ch_list> parameter, this command applies to the internal DMM, 
    #independent of any channels or a scan list. 
    def is_temperature_unit(self, chan = ""):    
        if (chan == ""):
            self.switch_data.write(":UNIT:TEMPerature?") 
            temp_values = self.switch_data.read()
            return(str(temp_values))
        else:
            self.switch_data.write(":UNIT:TEMPerature? (@" + str(chan) + ")") 
            temp_values = self.switch_data.read()
            return(str(temp_values))

    #This command enables the inclusion of alarm information with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_alarm_enable(self):
        self.switch_data.write(":FORMat:READing:ALARm ON")
        while((self.switch_data.query_ascii_values(":FORMat:READing:ALARm?")) == 0):
            self.switch_data.write(":FORMat:READing:ALARm ON")

    #This command disables the inclusion of alarm information with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_alarm_disable(self):
        self.switch_data.write(":FORMat:READing:ALARm OFF")
        while((self.switch_data.query_ascii_values(":FORMat:READing:ALARm?")) == 1):
            self.switch_data.write(":FORMat:READing:ALARm OFF")

    #This command enables the inclusion of channel number information with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_channel_enable(self):
        self.switch_data.write(":FORMat:READing:CHANnel ON")
        while((self.switch_data.query_ascii_values(":FORMat:READing:CHANnel?")) == 0):
            self.switch_data.write(":FORMat:READing:CHANnel ON")

    #This command disables the inclusion of channel number information with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_channel_disable(self):
        self.switch_data.write(":FORMat:READing:CHANnel OFF")
        while((self.switch_data.query_ascii_values(":FORMat:READing:CHANnel?")) == 1):
            self.switch_data.write(":FORMat:READing:CHANnel OFF")

    #This command enables the inclusion of time stamp with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_time_enable(self):
        self.switch_data.write(":FORMat:READing:TIME ON")
        while((self.switch_data.query_ascii_values(":FORMat:READing:TIME?")) == 0):
            self.switch_data.write(":FORMat:READing:TIME ON")        

    #This command disables the inclusion of time stamp with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_time_disable(self):
        self.switch_data.write(":FORMat:READing:TIME OFF")
        while((self.switch_data.query_ascii_values(":FORMat:READing:TIME?")) == 1):
            self.switch_data.write(":FORMat:READing:TIME OFF") 

    #This command selects the time format for storing scanned data in memory. You can select 
    #ABSolute time (time of day with date) or RELative time (time in seconds since start of scan).         
    def format_reading_time_type(self, format = "ABS"):
        self.switch_data.write(":FORMat:READing:TIME:TYPE " + str(format))
        self.switch_data.write(":FORMat:READing:TIME:TYPE?")
        temp = self.switch_data.read()
        while(str(temp) != (str(format) + "\n")):
            self.switch_data.write(":FORMat:READing:TIME:TYPE?")
            temp = self.switch_data.read()
        self.format_reading_time_enable()

    #This command enables the inclusion of measurement units with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_unit_enable(self):
        self.switch_data.write(":FORMat:READing:UNIT ON")
        while((self.switch_data.query_ascii_values(":FORMat:READing:UNIT?")) == 0):
            self.switch_data.write(":FORMat:READing:UNIT ON")

    #This command disables the inclusion of measurement units with data retrieved 
    #by the READ? command, the FETCh? command, or other queries of scan results.
    def format_reading_unit_disable(self):
        self.switch_data.write(":FORMat:READing:UNIT OFF")
        while((self.switch_data.query_ascii_values(":FORMat:READing:UNIT?")) == 1):
            self.switch_data.write(":FORMat:READing:UNIT OFF")

    #The following command performs a calibration on the Internal DMM and returns a pass/fail indication.
    def is_calibrated(self, sec_code = "AG34980"):
        self.device_unsecure(sec_code)
        temp_values = self.switch_data.query_ascii_values(":CALibration?")
        temp = str(temp_values[0])
        self.device_secure(sec_code)
        return(temp)

    #This command allows you to enter a new security code to prevent accidental or 
    #unauthorized calibrations. The specified code is used to unsecure the mainframe 
    #and all installed modules.
    def calibrate_security_code_modify(self, old_sec_code = "AG34980", new_sec_code = "AG34980"):
        self.device_unsecure(old_sec_code)
        self.switch_data.write(":CALibration:SECure:CODE ," + str(new_sec_code))    
        self.device_secure(new_sec_code)

    #This command unsecures the instrument for calibration.         
    def device_unsecure(self, sec_code = "AG34980"):
        self.switch_data.write(":CALibration:SECure:STATe OFF," + str(sec_code))

    #This command secures the instrument for calibration. 
    def device_secure(self, sec_code = "AG34980"):
        self.switch_data.write(":CALibration:SECure:STATe ON," + str(sec_code))

    #This command checks the calibration security setting of the instrument.         
    def is_calibration_security_setting(self):
        temp_values = self.switch_data.query_ascii_values(":CALibration:SECure:STATe?")
        temp = str(temp_values[0])
        return(temp)

    #This command sets the power-line reference frequency used by the 
    #internal DMM's analog-to-digital converter.        
    def line_freq(self, freq_val = 60):
        self.switch_data.write(":CALibration:LFRequency " + str(freq_val))
        temp = self.switch_data.query_ascii_values(":CALibration:LFRequency?")
        while(temp[0] != freq_val):
                self.switch_data.write(":CALibration:LFRequency " + str(freq_val))
                temp = self.switch_data.query_ascii_values(":CALibration:LFRequency?")

    #This command checks the power-line reference frequency used by the 
    #internal DMM's analog-to-digital converter.        
    def measure_line_freq(self):
        temp_values = self.switch_data.query_ascii_values(":CALibration:LFRequency?")
        temp = str(temp_values[0])    
        return(temp)

    #This command enables the internal DMM. 
    def internal_dmm_enable(self):
        self.switch_data.write(":INSTrument:DMM:STATe ON")
        while(self.internal_dmm_state() == 0):
            self.switch_data.write(":INSTrument:DMM:STATe ON")

    #This command disables the internal DMM. 
    def internal_dmm_disable(self):
        self.switch_data.write(":INSTrument:DMM:STATe OFF")
        while(self.internal_dmm_state() == 1):
            self.switch_data.write(":INSTrument:DMM:STATe OFF")

    #This command checks the internal DMM setting.         
    def internal_dmm_state(self):
        temp_values = self.switch_data.query_ascii_values(":INSTrument:DMM:STATe?")
        temp = str(temp_values[0])     
        return(temp)

    #This command connects the internal DMM to the Analog Buses. 
    #When connected, the internal DMM is always connected to Analog Bus 1 (MEAS). 
    #For 4-wire measurements, the internal DMM is also connected to Analog Bus 2 (SENS).  
    def internal_dmm_connect(self):
        self.switch_data.write(":INSTrument:DMM:CONNect")
        while(self.internal_dmm_status() == 0):
            self.switch_data.write(":INSTrument:DMM:CONNect")

    #This command disconnects the internal DMM from the Analog Buses. 
    def internal_dmm_disconnect(self):
        self.switch_data.write(":INSTrument:DMM:DISConnect")
        while(self.internal_dmm_status() == 1):
            self.switch_data.write(":INSTrument:DMM:DISConnect")

    #This command checks the status of internal DMM connection. 
    #When connected, the internal DMM is always connected to Analog Bus 1 (MEAS). 
    #For 4-wire measurements, the internal DMM is also connected to Analog Bus 2 (SENS).  
    def internal_dmm_status(self):
        temp_values = self.switch_data.query_ascii_values(":INSTrument:DMM:CONNect?")
        return(temp_values[0])

    #This command assigns a user-defined label to the specified channels for use 
    #with the 34980A front panel and Web Interface.
    def channel_label(self, chan, label):
        self.switch_data.write(":ROUTe:CHANnel:LABel:DEFine \"" + str(label) + "\", (@" + str(chan) + ")")

    #This command clears all user-defined labels on all channels in the specified slot, 
    #or on all modules installed in the 34980A, and restores the factory-default labels 
    #to the front panel and Web Interface
    def clear_module_label(self, module = 1):
        self.switch_data.write(":ROUTe:CHANnel:LABel:CLEar:MODule " + str(module))

    #This command checks the factory-default labels for specified channels. 
    def is_channel_label(self, chan):
        self.switch_data.write(":ROUTe:CHANnel:LABel:DEFine? (@" + str(chan) + ")")
        temp = self.switch_data.read()
        return(temp)

    def __del__(self):
        self.switch_data.close()
        global rm
        print("\nSwitch Matrix Released")
        rm.close()    

