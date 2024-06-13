# Author: Amelie Deshazer 
# Date: 6/6/2024
# Address: USB0::0x1AB1::0x0960::DSA8A154202508::INSTR 
# Purpose: Properties and methods used to define start, stop, and center frequency to be controlled. Sweep time and continuous sweep can be controlled and set by their parameters. 
# Citations: 

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


import numpy as np
import pandas as pd
from io import StringIO
from time import sleep
from pymeasure.log import console_log
from pymeasure.experiment import Procedure, Results, Worker 
from pymeasure.experiment import IntegerParameter
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (truncated_discrete_set, truncated_range, strict_discrete_set)

dsa815 = "USB0::0x1AB1::0x0960::DSA8A154202508::INSTR"

#log = logging.getLogger(__name__)
#log.addHandler(logging.NullHandler())

class DSA815(Instrument):
   # """Class for controlling RIGOL DSA815 spectrum analyzer"""
    #def __init__(self, adapter, name="RIGOL DSA815", **kwargs):
     #   super().__init__(adapter, name,includeSCPI=True,
          #  **kwargs)
    def __init__(self, adapter, name="RIGOL DSA815 Spectrum Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
    start_frequency = Instrument.control(
        ":SENSe:FREQuency:STARt?", 
        ":SENSe:FREQuency:STARt %e",
    """Communicates with DSA815 Machine and reads out the Start Frequency""",
    validator = truncated_range, 
    values = [0,7.5e9] #units in Hz. Possible unit conversion? Use set_process 
    )

    center_frequency = Instrument.control(
        ":SENSe:FREQuency:CENTer?",
        ":SENSe:FREQuency:CENTer %e",
        """Reads and sets center frequency""",
    validator = truncated_range,
    values = [0, 7.5e9]                                       
    )

    stop_frequency = Instrument.control(
        ":SENSe:FREQuency:STOP?",
        ":SENSe:FREQuency:STOP %e",
        """Reads and sets the stop frequency""",
    validator = truncated_range,
    values = [0,1.5e9]
    )
    #Need to set this to 601
    frequency_points = Instrument.control(
          ":SENSe:SWEep:POINts?", ":SENSe:SWEep:POINts %d",
          """Sets the amount of sweep data points""",
          validator = truncated_range,
          values = [101,3001],
        #   cast = int,
        #   low = 101,
        #   high = 3001
    )

    sweep_time = Instrument.control(
        ":SENSe:SWEEP:TIME?",
        ":SENSe:SWEEP:TIME %e",
        """Reads and sets the sweep time. This function measures the start 
        and stop length to acquire frequencies""",
    validator = truncated_range, 
    values = [2e-5,7500] #converted into seconds                  
    )
    #Turns on (1) or off(0) continuous sweep
    continuous_sweep = Instrument.control(
        ":INITiate:CONTinuous?",
        ":INITiate:CONTinuous %d",
        """Reads and sets continuous sweep""",
    )
    
    def trace(self):
            try:
                print("please work") 
                self.write("INITiate:IMMediate")
                print("Hello world")
                self.write("TRACe:DATA TRACE1")
                print("OH IT WORKED!")
                data = self.ask(":TRACE? TRACE1")[12:]
                print("YES IT IS WORKING")
                return [float(x) for x in data.split(",")]
            except Exception as e:
                raise Exception("Error in trace function: " + str(e))
    
    
    
    #def frequencies(self):
    # def trace(self):
    #         self.write(":INITiate:IMMediate")
    #         self.write(":TRACe:DATA TRACE1")
    #         data =self.query(':TRACE? TRACE1')[12:] # Strip off 10 characters of header
    #         return data.split(",")
       
        # data = np.loadtxt(
        #     StringIO(self.ask(":TRACe:DATA? TRACE1")),
        #     delimiter=',',
        #     dtype=np.float64
        # )
        # print(data)
        # return data
    


    # measure_data = Instrument.control(
    #     "INITiate:IMMediate", ":READ",
    #     """Sets up the measurement"""
    # )
    # data_format = Instrument.control(
    #     ":FORMat:TRACe:DATA?",
    #     """Reads the data format"""
    # )
    # def trace(self):
    #     """ Returns a numpy array of the data for a particular trace
    #     based on the trace number (1, 2, or 3).
    #     """
    #     self.write("TRACe:DATA TRACE%d") #sets up the measurement
    # def frequencies(self):
    #     """ Returns a numpy array of frequencies in Hz that
    #     correspond to the current settings of the instrument.
    #     """
    #     return np.linspace(
    #         self.start_frequency(),
    #         self.stop_frequency(),
    #         self.frequency_points(),
    #         dtype=np.float64
    #     )

    #def trace_df(self, number=1):
       # """ Returns a pandas DataFrame containing the frequency
        #and peak data for a particular trace, based on the
        #trace number (1, 2, or 3).
        #"""
        #return pd.DataFrame({
            #'Frequency (GHz)': self.frequencies * 1e-9,
            #'Peak (dB)': self.trace(number)
      #  })
               



    
    




