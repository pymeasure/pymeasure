# Author: Amelie Deshazer 
# Date: 6/6/2024
# Address: USB0::0x1AB1::0x0960::DSA8A154202508::INSTR 
# Purpose:Comunicate with the Rigol DSA815 Spectrum Analyzer and read out the start, center, and stop frequency. 
#         Also, set and read the sweep time and turn on or off the continuous sweep. For measurement to work, 
#         continuous sweep must be off.  

import numpy as np
import pandas as pd
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range

class DSA815(Instrument):
 
    start_frequency = Instrument.control(
        ":SENSe:FREQuency:STARt?", 
        ":SENSe:FREQuency:STARt %e",
    """Reads and sets start frequency""",
    validator = truncated_range, 
    values = [0,7.5e9] 
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

    frequency_points = Instrument.control(
          ":SENSe:SWEep:POINts?", ":SENSe:SWEep:POINts %d",
          """Sets the amount of sweep data points""",
          validator = truncated_range,
          values = [101,3001]
    )
 
    sweep_time = Instrument.control(
        ":SENSe:SWEEP:TIME?",
        ":SENSe:SWEEP:TIME %e",
        """Reads and sets the sweep time.""",
    validator = truncated_range, 
    values = [2e-5,7500]                 
    )

    #Turns on (1) or off(0) continuous sweep
    continuous_sweep = Instrument.control(
        ":INITiate:CONTinuous?",
        ":INITiate:CONTinuous %d",
        """Reads and sets continuous sweep on (1) or off (0)""",
    ) 

    def __init__(self, adapter, name="RIGOL DSA815 Spectrum Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        ) 
 
    def frequencies(self, freq_points = 601):
        """ Returns an array of frequency points based on the 
        start and stop frequency"""
        return np.linspace(
              self.start_frequency, 
              self.stop_frequency,
              freq_points, 
              dtype = np.float64
         )
    
    def trace(self):
        """Returns an array of `amplitude` data from the trace."""
        self.write("INITiate:IMMediate")
        self.write("TRACe:DATA TRACE1")
        data = self.ask(":TRACE? TRACE1")[12:]
        amplitude = [float(x) for x in data.split(",")]
        return amplitude
    
    def trace_df(self):
       """ Returns a pandas DataFrame containing the frequency
        and peak data for a particular trace, based on the
        trace number (1, 2, or 3).
        """
       trace1 = self.trace()
       return pd.DataFrame({
            'Frequency (GHz)': self.frequencies(len(trace1)) * 1e-9,
            'Amplitude (dBm)': trace1
            })