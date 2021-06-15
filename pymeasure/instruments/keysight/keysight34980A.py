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
    """ Represents the Keysight 34980A Multifunction Switch/Measure Unit
    and provides a high-level interface for taking scans with Keysight 34923A
    Multifunction Switch/Measure Unit.
    """

    def __init__(self, resourceName, **kwargs):
        super(Keysight34980A, self).__init__(resourceName, "Keysight 34980A Multifunction Switch/Measure Unit", **kwargs)
    
    def set_channel_open_all(self, module = 1):    
        """
        This command opens all channel relays and Analog Bus relays on the specified multiplexer 
        or switch module. Alternately by specifying the "ALL" parameter, this command opens 
        all channels on all installed modules. 
        """
        self.write(":ROUTe:OPEN:ALL " + str(module))

    def set_channel_open(self, chan = ""):    
        """
        This command opens the specified channel on a multiplexer or switch module.         
        """
        self.write(":ROUTe:OPEN (@" + str(chan) + ")")
        while(self.is_channel_open(chan) == 0):
            self.write(":ROUTe:OPEN (@" + str(chan) + ")")

    
    def is_channel_open(self, chan = ""):    
        """
        This command checks if the specified channel on a multiplexer or switch module is open. 
        """
        temp_values = self.values(":ROUTe:OPEN? (@" + str(chan) + ")")
        return(str(temp_values[0]))

    def set_abus_close(self, abus = 1):
        """
        This command closes the connections to four Analog Buses on all installed modules. 
        """
        chan = str("192") + str(abus)
        self.set_channel_close(chan)

    def set_abus_open(self, abus = 1):
        """
        This command opens the connections to four Analog Buses on installed modules. 
        """
        self.write(":ROUTe:OPEN:ABUS " + str(abus))
        while(self.is_abus_open(abus) == 1):
            self.write(":ROUTe:OPEN:ABUS " + str(abus))

    def set_abus_open_all(self):
        """
        This command opens all connections to all four Analog Buses on all installed modules.
        """
        self.write(":ROUTe:OPEN:ABUS ALL")
        while((self.is_abus_open(1) == 1) and (self.is_abus_open(2) == 1) and (self.is_abus_open(3) == 1) and (self.is_abus_open(4) == 1)):
            self.write(":ROUTe:OPEN:ABUS ALL")

    def set_abus_close_all(self):
        """
        This command closes all connections to all four Analog Buses on all installed modules.
        """

        self.set_channel_close(1921)
        self.set_channel_close(1922)
        self.set_channel_close(1923)
        self.set_channel_close(1924)
        while((self.is_abus_close(1) == 1) and (self.is_abus_close(2) == 1) and (self.is_abus_close(3) == 1) and (self.is_abus_close(4) == 1)):
            self.set_channel_close(1921)
            self.set_channel_close(1922)
            self.set_channel_close(1923)
            self.set_channel_close(1924)

    def is_abus_open(self, abus = ""):    
        """
        This command checks if Analog Buse is open. 
        """
        chan = str("192") + str(abus)
        return(str(self.is_channel_open(chan)))

    def is_abus_close(self, abus = ""):    
        """
        This command checks if Analog Buse is close. 
        """
        chan = str("192") + str(abus)
        return(str(self.is_channel_close(chan)))

    def set_channel_close(self, chan = ""):    
        """
        This command closes the specified channel on a multiplexer or switch module.         
        """
        self.write(":ROUTe:CLOSe (@" + str(chan) + ")")
        while(self.is_channel_close(chan) == 0):
            self.write(":ROUTe:CLOSe (@" + str(chan) + ")")
    
    def is_channel_close(self, chan = ""):    
        """
        This command checks if the specified channel on a multiplexer or switch module is close. 
        """
        temp_values = self.values(":ROUTe:CLOSe? (@" + str(chan) + ")") 
        return(str(temp_values[0]))

    def set_ac_current_autorange(self, chan = ""):    
        """
        This command enables autoranging for ac current measurements on the specified channel.
        """

        if (chan == ""):
            self.write(":SENSe:CURRent:AC:RANGe:AUTO ON")
            while((self.is_ac_current_autorange()) == 0):
                self.write(":SENSe:CURRent:AC:RANGe:AUTO ON")
        else:
            self.write(":SENSe:CURRent:AC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_ac_current_autorange(chan)) == 0):
                self.write(":SENSe:CURRent:AC:RANGe:AUTO ON (@" + str(chan) + ")")

    def reset_ac_current_autorange(self, chan = ""):    
        """
        This command disables autoranging for ac current measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:CURRent:AC:RANGe:AUTO OFF")
            while((self.is_ac_current_autorange()) == 1):
                self.write(":SENSe:CURRent:AC:RANGe:AUTO OFF")
        else:
            self.write(":SENSe:CURRent:AC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_ac_current_autorange(chan)) == 1):
                self.write(":SENSe:CURRent:AC:RANGe:AUTO OFF (@" + str(chan) + ")")

    def is_ac_current_autorange(self, chan = ""):     
        """
        This command checks if autoranging for ac current measurements on the specified channel are enabled.       
        """
        if (chan == ""):
            self.write(":SENSe:CURRent:AC:RANGe:AUTO?") 
            temp_values = self.read()
            return(str(temp_values[0]))
        else:    
            self.write(":SENSe:CURRent:AC:RANGe:AUTO? (@" + str(chan) + ")") 
            temp_values = self.read()
            return(str(temp_values[0]))

    def set_dc_current_autorange(self, chan = ""):    
        """
        This command enables autoranging for dc current measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:CURRent:DC:RANGe:AUTO ON")
            while((self.is_dc_current_autorange()) == 0):
                self.write(":SENSe:CURRent:DC:RANGe:AUTO ON")
        else:    
            self.write(":SENSe:CURRent:DC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_dc_current_autorange(chan)) == 0):
                self.write(":SENSe:CURRent:DC:RANGe:AUTO ON (@" + str(chan) + ")")

    def reset_dc_current_autorange(self, chan = ""):    
        """
        This command disables autoranging for dc current measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:CURRent:DC:RANGe:AUTO OFF")
            while((self.is_dc_current_autorange()) == 1):
                self.write(":SENSe:CURRent:DC:RANGe:AUTO OFF")
        else:    
            self.write(":SENSe:CURRent:DC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_dc_current_autorange(chan)) == 1):
                self.write(":SENSe:CURRent:DC:RANGe:AUTO OFF (@" + str(chan) + ")")

    def is_dc_current_autorange(self, chan = ""):    
        """
        This command checks if autoranging for dc current measurements on the specified channel are enabled.       
        """
        if (chan == ""):
            temp_values = self.values(":SENSe:CURRent:DC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:    
            temp_values = self.values(":SENSe:CURRent:DC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    def set_ac_voltage_autorange(self, chan = ""):    
        """
        This command enables autoranging for ac voltage measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:VOLTage:AC:RANGe:AUTO ON")
            while((self.is_ac_voltage_autorange()) == 0):
                self.write(":SENSe:VOLTage:AC:RANGe:AUTO ON")
        else:
            self.write(":SENSe:VOLTage:AC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_ac_voltage_autorange(chan)) == 0):
                self.write(":SENSe:VOLTage:AC:RANGe:AUTO ON (@" + str(chan) + ")")

    def reset_ac_voltage_autorange(self, chan = ""):    
        """
        This command disables autoranging for ac voltage measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF")
            while((self.is_ac_voltage_autorange()) == 1):
                self.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF")
        else:
            self.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_ac_voltage_autorange(chan)) == 1):
                self.write(":SENSe:VOLTage:AC:RANGe:AUTO OFF (@" + str(chan) + ")")

    def is_ac_voltage_autorange(self, chan = ""):    
        """
        This command checks if autoranging for ac voltage measurements on the specified channel are enabled.       
        """
        if (chan == ""):
            temp_values = self.values(":SENSe:VOLTage:AC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.values(":SENSe:VOLTage:AC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    def set_dc_voltage_autorange(self, chan = ""):    
        """
        This command enables autoranging for dc voltage measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
            while((self.is_dc_voltage_autorange(chan)) == 0):
                self.write(":SENSe:VOLTage:DC:RANGe:AUTO ON")
        else:
            self.write(":SENSe:VOLTage:DC:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_dc_voltage_autorange(chan)) == 0):
                self.write(":SENSe:VOLTage:DC:RANGe:AUTO ON (@" + str(chan) + ")")

    def reset_dc_voltage_autorange(self, chan = ""):    
        """
        This command disables autoranging for dc voltage measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF")
            while((self.is_dc_voltage_autorange(chan)) == 1):
                self.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF")
        else:
            self.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_dc_voltage_autorange(chan)) == 1):
                self.write(":SENSe:VOLTage:DC:RANGe:AUTO OFF (@" + str(chan) + ")")

    def is_dc_voltage_autorange(self, chan = ""):    
        """
        This command checks if autoranging for dc voltage measurements on the specified channel are enabled.       
        """
        if (chan == ""):
            temp_values = self.values(":SENSe:VOLTage:DC:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.values(":SENSe:VOLTage:DC:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    def set_resistance_autorange(self, chan = ""):    
        """
        This command enables autoranging for resistance measurements on the specified channel.
        """
        if (chan == ""):
            self.write(":SENSe:RESistance:RANGe:AUTO ON")
            while((self.is_resistance_autorange()) == 0):
                self.write(":SENSe:RESistance:RANGe:AUTO ON")
        else:
            self.write(":SENSe:RESistance:RANGe:AUTO ON (@" + str(chan) + ")")
            while((self.is_resistance_autorange(chan)) == 0):
                self.write(":SENSe:RESistance:RANGe:AUTO ON (@" + str(chan) + ")")

    def reset_resistance_autorange(self, chan = ""):    
        """
        This command disables autoranging for resistance measurements on the specified channel.
        """    
        if (chan == ""):
            self.write(":SENSe:RESistance:RANGe:AUTO OFF")
            while((self.is_resistance_autorange()) == 1):
                self.write(":SENSe:RESistance:RANGe:AUTO OFF")
        else:
            self.write(":SENSe:RESistance:RANGe:AUTO OFF (@" + str(chan) + ")")
            while((self.is_resistance_autorange(chan)) == 1):
                self.write(":SENSe:RESistance:RANGe:AUTO OFF (@" + str(chan) + ")")

    def is_resistance_autorange(self, chan = ""):    
        """
        This command checks if autoranging for resistance measurements on the specified channel are enabled.       
        """
        if (chan == ""):
            temp_values = self.values(":SENSe:RESistance:RANGe:AUTO?") 
            return(str(temp_values[0]))
        else:
            temp_values = self.values(":SENSe:RESistance:RANGe:AUTO? (@" + str(chan) + ")") 
            return(str(temp_values[0]))

    def measure_dc_voltage(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        """
        The following command configures the instrument for dc voltage measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:VOLTage:DC?")
        dc_voltage = str(temp_values[0])
        return(dc_voltage)

    def measure_ac_voltage(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        """
        The following command configures the instrument for ac voltage measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:VOLTage:AC?")
        return(str(temp_values[0]))

    def measure_dc_current(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        """
        The following command configures the instrument for dc current measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:CURRent:DC?")
        return(str(temp_values[0]))

    def measure_ac_current(self, chan, resolution = "DEFault", range_param = "AUTO"):
        """
        The following command configures the instrument for ac voltage measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:CURRent:AC?")
        return(str(temp_values[0]))

    def measure_frequency(self, chan, resolution = "DEFault", range_param = "DEFault"):    
        """
        The following command configures the instrument for frequency measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:FREQuency?")
        return(str(temp_values[0]))

    def measure_period(self, chan, resolution = "DEFault", range_param = "DEFault"):    
        """
        The following command configures the instrument for period measurements, 
        triggers the internal DMM to scan the specified channel.    
        """
        temp_values = self.values(":MEASure:SCALar:PERiod?")
        return(str(temp_values[0]))

    def measure_resistance(self, chan, resolution = "DEFault", range_param = "AUTO"):    
        """
        The following command configures the instrument for resistance measurements, 
        triggers the internal DMM to scan the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:RESistance?")
        return(str(temp_values[0]))

    def measure_temperature(self, chan, probe = "TCouple", probe_type = "T", resolution = "DEFault", range_param = "AUTO"):   
        """
        The following command configures the instrument for temperature measurements on the specified channel.
        """
        temp_values = self.values(":MEASure:SCALar:TEMPerature?")
        return(str(temp_values[0]))

    def set_temperature_unit(self, chan = "", unit = 'K'):    
        """
        This command selects the temperature units (°C, °F, or Kelvins) on the specified channels. 
        If you omit the optional <ch_list> parameter, this command applies to the internal DMM, 
        independent of any channels or a scan list.
        """
        if (chan == ""):
            self.write(":UNIT:TEMPerature " + str(unit))
            while((self.is_temperature_unit()) != str(str(unit) + "\n")):
                self.write(":UNIT:TEMPerature " + str(unit))    
        else:
            self.write(":UNIT:TEMPerature " + str(unit) + ", (@" + str(chan) + ")")
            while((self.is_temperature_unit(chan)) != str(str(unit) + "\n")):
                self.write(":UNIT:TEMPerature " + str(unit) + ", (@" + str(chan) + ")")

    def is_temperature_unit(self, chan = ""):    
        """
        The command checks the temperature units (°C, °F, or Kelvins) on the specified channels. 
        If you omit the optional <ch_list> parameter, this command applies to the internal DMM, 
        independent of any channels or a scan list. 
        """
        if (chan == ""):
            self.write(":UNIT:TEMPerature?") 
            temp_values = self.read()
            return(str(temp_values))
        else:
            self.write(":UNIT:TEMPerature? (@" + str(chan) + ")") 
            temp_values = self.read()
            return(str(temp_values))

    def format_reading_alarm_enable(self):
        """
        This command enables the inclusion of alarm information with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:ALARm ON")
        while((self.values(":FORMat:READing:ALARm?")) == 0):
            self.write(":FORMat:READing:ALARm ON")

    def format_reading_alarm_disable(self):
        """
        This command disables the inclusion of alarm information with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:ALARm OFF")
        while((self.values(":FORMat:READing:ALARm?")) == 1):
            self.write(":FORMat:READing:ALARm OFF")

    def format_reading_channel_enable(self):
        """
        This command enables the inclusion of channel number information with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:CHANnel ON")
        while((self.values(":FORMat:READing:CHANnel?")) == 0):
            self.write(":FORMat:READing:CHANnel ON")

    def format_reading_channel_disable(self):
        """
        This command disables the inclusion of channel number information with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:CHANnel OFF")
        while((self.values(":FORMat:READing:CHANnel?")) == 1):
            self.write(":FORMat:READing:CHANnel OFF")

    def format_reading_time_enable(self):
        """
        This command enables the inclusion of time stamp with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:TIME ON")
        while((self.values(":FORMat:READing:TIME?")) == 0):
            self.write(":FORMat:READing:TIME ON")        

    def format_reading_time_disable(self):
        """
        This command disables the inclusion of time stamp with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:TIME OFF")
        while((self.values(":FORMat:READing:TIME?")) == 1):
            self.write(":FORMat:READing:TIME OFF") 

    def format_reading_time_type(self, format = "ABS"):
        """
        This command selects the time format for storing scanned data in memory. You can select 
        Absolute time (time of day with date) or RELative time (time in seconds since start of scan).         
        """
        self.write(":FORMat:READing:TIME:TYPE " + str(format))
        self.write(":FORMat:READing:TIME:TYPE?")
        temp = self.read()
        while(str(temp) != (str(format) + "\n")):
            self.write(":FORMat:READing:TIME:TYPE?")
            temp = self.read()
        self.format_reading_time_enable()

    def format_reading_unit_enable(self):
        """
        This command enables the inclusion of measurement units with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:UNIT ON")
        while((self.values(":FORMat:READing:UNIT?")) == 0):
            self.write(":FORMat:READing:UNIT ON")

    def format_reading_unit_disable(self):
        """
        This command disables the inclusion of measurement units with data retrieved 
        by the READ? command, the FETCh? command, or other queries of scan results.
        """
        self.write(":FORMat:READing:UNIT OFF")
        while((self.values(":FORMat:READing:UNIT?")) == 1):
            self.write(":FORMat:READing:UNIT OFF")

    def is_calibrated(self, sec_code = "AG34980"):
        """
        The following command performs a calibration on the Internal DMM and returns a pass/fail indication.
        """
        self.device_unsecure(sec_code)
        temp_values = self.values(":CALibration?")
        temp = str(temp_values[0])
        self.device_secure(sec_code)
        return(temp)

    def calibrate_security_code_modify(self, old_sec_code = "AG34980", new_sec_code = "AG34980"):
        """
        This command allows you to enter a new security code to prevent accidental or 
        unauthorized calibrations. The specified code is used to unsecure the mainframe 
        and all installed modules.
        """
        self.device_unsecure(old_sec_code)
        self.write(":CALibration:SECure:CODE ," + str(new_sec_code))    
        self.device_secure(new_sec_code)

    def device_unsecure(self, sec_code = "AG34980"):
        """
        This command unsecures the instrument for calibration.         
        """
        self.write(":CALibration:SECure:STATe OFF," + str(sec_code))

    def device_secure(self, sec_code = "AG34980"):
        """
        This command secures the instrument for calibration. 
        """
        self.write(":CALibration:SECure:STATe ON," + str(sec_code))

    def is_calibration_security_setting(self):
        """
        This command checks the calibration security setting of the instrument.         
        """
        temp_values = self.values(":CALibration:SECure:STATe?")
        temp = str(temp_values[0])
        return(temp)

    def line_freq(self, freq_val = 60):
        """
        This command sets the power-line reference frequency used by the 
        internal DMM's analog-to-digital converter.        
        """
        self.write(":CALibration:LFRequency " + str(freq_val))
        temp = self.values(":CALibration:LFRequency?")
        while(temp[0] != freq_val):
                self.write(":CALibration:LFRequency " + str(freq_val))
                temp = self.values(":CALibration:LFRequency?")

    def measure_line_freq(self):
        """
        This command checks the power-line reference frequency used by the 
        internal DMM's analog-to-digital converter.        
        """
        temp_values = self.values(":CALibration:LFRequency?")
        temp = str(temp_values[0])    
        return(temp)

    def internal_dmm_enable(self):
        """
        This command enables the internal DMM. 
        """
        self.write(":INSTrument:DMM:STATe ON")
        while(self.internal_dmm_state() == 0):
            self.write(":INSTrument:DMM:STATe ON")

    def internal_dmm_disable(self):
        """
        This command disables the internal DMM. 
        """
        self.write(":INSTrument:DMM:STATe OFF")
        while(self.internal_dmm_state() == 1):
            self.write(":INSTrument:DMM:STATe OFF")

    def internal_dmm_state(self):
        """
        This command checks the internal DMM setting.         
        """
        temp_values = self.values(":INSTrument:DMM:STATe?")
        temp = str(temp_values[0])     
        return(temp)

    def internal_dmm_connect(self):
        """
        This command connects the internal DMM to the Analog Buses. 
        When connected, the internal DMM is always connected to Analog Bus 1 (MEAS). 
        For 4-wire measurements, the internal DMM is also connected to Analog Bus 2 (SENS).  
        """
        self.write(":INSTrument:DMM:CONNect")
        while(self.internal_dmm_status() == 0):
            self.write(":INSTrument:DMM:CONNect")

    def internal_dmm_disconnect(self):
        """
        This command disconnects the internal DMM from the Analog Buses. 
        """
        self.write(":INSTrument:DMM:DISConnect")
        while(self.internal_dmm_status() == 1):
            self.write(":INSTrument:DMM:DISConnect")

    def internal_dmm_status(self):
        """
        This command checks the status of internal DMM connection. 
        When connected, the internal DMM is always connected to Analog Bus 1 (MEAS). 
        For 4-wire measurements, the internal DMM is also connected to Analog Bus 2 (SENS).  
        """
        temp_values = self.values(":INSTrument:DMM:CONNect?")
        return(temp_values[0])

    def channel_label(self, chan, label):
        """
        This command assigns a user-defined label to the specified channels for use 
        with the 34980A front panel and Web Interface.
        """
        self.write(":ROUTe:CHANnel:LABel:DEFine \"" + str(label) + "\", (@" + str(chan) + ")")

    def clear_module_label(self, module = 1):
        """
        This command clears all user-defined labels on all channels in the specified slot, 
        or on all modules installed in the 34980A, and restores the factory-default labels 
        to the front panel and Web Interface
        """
        self.write(":ROUTe:CHANnel:LABel:CLEar:MODule " + str(module))

    def is_channel_label(self, chan):
        """
        This command checks the factory-default labels for specified channels. 
        """
        self.write(":ROUTe:CHANnel:LABel:DEFine? (@" + str(chan) + ")")
        temp = self.read()
        return(temp)
