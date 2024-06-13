# Author: Amelie Deshazer
# Date: 2024/06/04
# Purpose: Communicates via a VISA adapter to the Rigol DSA815 by utilizing the start, center, and stop frequency. Can set up sweep time and take a spectrum


import logging 
import numpy as np 
import pyvisa
import matplotlib.pyplot as plt
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
     truncated_range,truncated_discrete_set,
     strict_discrete_set)

instrument_address = "USB0::0x1AB1::0x0960::DSA8A154202508::INSTR" 

#Class: DSA815
# Code is calling based on the setup IP address to convey information
# to and from the system
class DSA(Instrument):
    """Class for controlling RIGOL DSA815 spectrum analyzer"""
    #dsa815 = "GIPB::1::INSTR"

    #def __init__(self, resourceName):
       # super().__init__(resourceName)
    def __init__(self, adapter, name="RIGOL DSA815", **kwargs):
        super().__init__(adapter, name,includeSCPI=True,
            **kwargs)
        
    #Disables continuous sweep
    def continuous_off(self):
        self.write(":INITiate:CONTinuous OFF")
    
    #Sets up Sweep Time. 
    #Units in seconds
   # @property
    def sweep_time(self):
        return self.ask(":SENSe:SWEep:TIME?")
    #@sweep_time.setter
    def sweep_time(self, value):
        self.write(":SENSe:SWEep:TIME %f" % value)  
    def sweep_time_validator(self,value):
        return truncated_range(value, 2e-5, 7500)


    #Defines Start Frequency
    #float: convert a number into a decimal or maintain its decimal form
    #Units in Hz
    @property
    def start_frequency(self):
        return float(self.query(":SENSe:FREQuency:STARt?")) 
    
    @start_frequency.setter 
    def start_frequency(self, value):
        self.write(":SENSe:FREQuency:STARt %f" % value)

    def start_frequency_validator(self, value):
        return truncated_range(value, 0, 7.5e9) #units are in Hz
    
    #Defines Center Frequency
    #Units in Hz 
    @property
    def center_frequency(self):
        return float(self.query(":SENSe:FREQuency:CENTer?"))
    @center_frequency.setter
    def center_frequency(self,value):
        self.write(":SENSe:FREQuency:CENTer %f" % value)
    
    def center_frequency_validator(self,value):
        return truncated_range(value, 0, 7,5e9) 
    
    #Defines Stop Frequency 
    #Units in Hz
    @property
    def stop_frequency(self): 
        return float(self.query(":SENSe:FREQuency:STOP?"))
    
    @stop_frequency.setter
    def stop_frequency(self, value):
        self.write(":SENSe:FREQuency:STOP %f" % value)
  
    def stop_frequency_validator(self, value):
        return truncated_range(value, 0, 7.5e9) #units are in Hz

    #retrives the binary data and stores it by calling TRACE1
    def plot_trace_data(self):
        self.write(":TRACe:DATA? TRACE1")
        binary_data = self.read_raw()

        #plot the spectrum analyzer
        if binary_data.startwith(b'#'):
            header_length = int(binary_data[1:2]) #convert into array
            data_length = int(binary_data[2:2 + header_length])
            data_start = 2 + header_length
            data = binary_data[data_start:data_start +data_length]
        else: 
            raise ValueError("Unexpected Binary Format")
        
        #convert binary into array (float32 based on np)
        trace_data = np.frombuffer(data, dtype = np.float32)

        #creating an array of start and stop frequency
        start_freq = self.start_frequency
        stop_freq = self.stop_frequency
        frequency = np.linspace(start_freq,stop_freq,len(trace_data))

        #plot the data of Frequency vs Amplitude 
        plt.figure()
        plt.plot(frequency,trace_data)
        plt.title("Frequency (Hz) vs Amplitude (dBM)")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude (dBM)")
        plt.grid(True)
        plt.show

   
if __name__ == "__main__":
    dsa815 = DSA815(instrument_address) #calls the class to ensure IP address matches with GPIB

    print("Starting frequency: ",dsa815.start_frequency, "Hz")
    print("Center frequency ", dsa815.center_frequency, " Hz")
    print("Stop frequency ", dsa815.stop_frequency, " Hz")

    
    # Lines 70-83 asks user whether to change the listed frequencies. 
    # If statement automatically assumes yes based on prompt.
    # if not yes, it would spell out the current frequency that is unchanged.  
    update_start = input("Do you want to change the Start Frequency? (yes/no) :").strip().lower() == 'yes'
    if update_start: 
        new_start_frequency=float(input("Enter new Start Frequency (Hz): "))
        dsa815.start_frequency = new_start_frequency 
        print("Updated Start Frequency:", dsa815.start_frequency, " Hz")
    else:
        print("Start Frequency:", dsa815.start_frequency, " Hz")


    update_center = input("Do you want to change the Center Frequency? (yes/no) :").strip().lower() == 'yes' 
    if update_center: 
        new_center_frequency = float(input("Enter new Center Frequency (Hz): "))
        dsa815.center_frequency = new_center_frequency
        print("Updated Center Frequency:", dsa815.center_frequency, " Hz")
    else: 
        print("Center Frequency:", dsa815.center_frequency, " Hz")


    update_stop =input("Do you want to change the Stop Frequency? (yes/no)").strip().lower() == 'yes'
    if update_stop: 
        new_stop_frequency = float(input("Enter the new Stop Frequency (Hz): "))
        dsa815.stop_frequency = new_stop_frequency
        print("Updated Stop Frequency:", dsa815.stop_frequency," Hz")
    else: 
        print("Stop Frequency:",dsa815.stop_frequency, " Hz")

    #Gets a spectrum
    dsa815.plot_trace_data()

    #close the connection to the instrument
    dsa815.adapter.connection.close()

    #This is a test code for testing purposes.
    @property
    def total_frequency(self):
        """Creates array based on numpy"""
        start_freq = self.start_frequency, 
        stop_freq = self.stop_frequency,
        freq_points = self.frequency_points,
        return np.linspace(start_freq,stop_freq, freq_points,dtype = np.float64)
      
    def trace(self, number = 1):
        self.write(":FORMat:TRACe:DATA ASCii")
        data = np.loadtxt(
            StringIO(self.ask("TRACE:DATA? TRACE %d," % number)),
            delimiter = ',',
            dtype = np.float64
        )
        return data
    
    def get_graph(self, number=1):
        return pd.DataFrame({
            'Freqyency (Hz)': self.total_frequency,
            'Peak (dBm)': self.trace(number)
        })


       # self.write(":INITiate:IMMediate")
        #return self.ask(":TRACe:DATA? TRACE1,")  # Ensure the data format is set to ASCII
       # return self.ask()
    
        #return self.query(":TRACe:DATA TRACE1")
    
    continuous_off = Instrument.control(
        ":INITiate:CONTinuous?", ":INITiate:CONTinuous %d", 
        """Turns off continuous sweep""",
        values={True: 1, False: 0},
        map_values=False,
    )
   
        
       #self.query(":READ:ACPower?")
       # values = 
    #ac_power = Instrument.measurement(":READ:ACPower?",
                  #"""Fetch a measurement of power result""") 

    #Get a spectrum
    #get_spectrum = Instrument.control("INITiate:IMMediate")

    #restart_measur = Instrument.control("INITiate:RESTart")

    









