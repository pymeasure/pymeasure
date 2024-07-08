# Author: Amelie Deshazer
# Data: 2024-06-10
# Purpose: Perform a spectrum measurement with the DSA815 spectrum analyzer. 
# The measurement is performed in a seperate class and are saved in a .csv file. 
# A GUI is used as an interactive interface for plots and data analysis. 

import logging 
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from time import sleep
from pymeasure.instruments.rigol import DSA815
from pymeasure.log import console_log
from pymeasure.display import Plotter
from pymeasure.experiment import Procedure, Results, Worker
from pymeasure.experiment import IntegerParameter, FloatParameter



#adapter ="USB0::0x1AB1::0x0960::DSA8A154202508::INSTR"
adapter = DSA815("USB0::0x1AB1::0x0960::DSA8A154202508::INSTR")

#Set the parameters for the spectrum analyzer




class DSA815Spectrum(Procedure):
    def __init__(self, adapter, name="RIGOL DSA815 Spectrum Analyzer", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
    start_freq = adapter.write("SENSe:FREQuency:STARt 6e6")
    center_freq = adapter.write("SENSe:FREQuency:CENTer 5e6")
    stop_freq = adapter.write("`SENSe:FREQuency:STOP 10e6")
    sweep_time = adapter.write("SENSe:SWEep:TIME 1")
    data_points = adapter.write("SENSe:SWEep:POINts 3001")
    adapter.write("INITiate:CONTinuous OFF")

    adapter.write("INITiate:IMMediate")
    adapter.write("TRACe:DATA TRACE1")

    #start_freq = FloatParameter('Start Frequency', units = 'Hz', default =0)
    #center_freq = FloatParameter('Center Frequency', units = 'Hz', default = 5e6)
    #stop_freq = FloatParameter('Stop Frequency', units = 'Hz', default = 10e6)
    #sweep_time = FloatParameter('Sweep Time', units = 's', default = 0.01)
    #data_points = IntegerParameter('Data Points', default = 3001)

    DATA_COLUMNS = ['Frequency (Hz)', 'Amplitude (dBm)']
    
    def startup(self):
        log.info("Starting spectrum measurement")
        self.spectrum = DSA815("USB0::0x1AB1::0x0960::DSA8A154202508::INSTR")
    def execute(self):
        data = self.spectrum.acquire()
        for i in range(self.data_points):
            data = {'Frequency (Hz)': data[0][i], 'Amplitude (dBm)': data[1][i]} #check notes
            self.emit('results', data)
            log.debug("Emitting results: %s" % data)
            sleep(0.01)
            if self.should_stop():
                log.warning("Received stop request")
                break

if __name__ == "__main__":
    console_log(log)

    log.info("Creating the DSA815 instrument")
    procedure = DSA815Spectrum()
    procedure.data_points = 3001
    procedure.start_freq = 0 
    procedure.center_freq = 5e6
    procedure.stop_freq = 10e6

    data_filename = "test_spectrum.csv"
    log.info("Getting spectrum results with a data file: %s" % data_filename)
    results = Results(procedure, data_filename)
    plotter = Plotter(results)

    log.info("Constructing the measurement")
    worker = Worker(results)
    worker.start()
    log.info("Measurement started") 

    log.info("Waiting for the measurement to finish")
    worker.join(timeout = 3600)
    log.info("Measurement complete")