"""
This example demonstrates how to make a graphical interface to preform
IV characteristic measurements. There are a two items that need to be 
changed for your system:

1) Correct the GPIB addresses in IVProcedure.startup for your instruments
2) Correct the directory to save files in MainWindow.queue

Run the program by changing to the directory containing this file and calling:

python iv_keithley.py

"""

import logging
log = logging.getLogger('')
log.addHandler(logging.NullHandler())

import sys
import numpy as np
import pandas as pd
from time import sleep

from pymeasure.instruments.agilent import Agilent34461A, Agilent34465A
from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.lecroy import WaveRunner606Zi

# Set the input parameters
max_voltage = 20
min_voltage = 0
voltage_step = 2
delay = .1

DATA_COLUMNS = ['Source Input Voltage (V)',
                'Input Voltage (V)',
                'Input Current (A)',
                'Input Power (W)',
                'Output DC Voltage (V)',
                'Resistance (Ohm)',
                'Switching freq. (Hz)',
                'Duty100']

data = pd.DataFrame(columns=DATA_COLUMNS)

log.info("Setting up instruments")
source = Chroma62024p6008('USB0::0x1698::0x0837::007000000446::0::INSTR')
print(source.id)
scope = WaveRunner606Zi('146.136.35.208')
print(scope.id)
vdclink = Agilent34465A('TCPIP0::146.136.35.247::inst0::INSTR')
print(vdclink.id)
vin_mot = Agilent34461A('TCPIP0::146.136.35.210::inst0::INSTR')
print(vin_mot.id)

source.output_disable()
source.output_current_limit = 3
source.output_voltage_level = 0
source.output_enable()
print(vdclink.voltage_dc)
print(vin_mot.voltage_dc)
sleep(2)

voltages = np.arange(min_voltage, max_voltage, voltage_step)
steps = len(voltages)

log.info("Starting to sweep through voltage")
for i, voltage in enumerate(voltages):
    log.debug("Measuring efficiency input voltage: %g V" % voltage)

    source.output_voltage_level = voltage
    # Or use source.ramp_to_current(current, delay=0.1)
    sleep(2)

    source_input_voltage = source.output_voltage
    source_input_current = source.output_current
    meas_input_voltage = vin_mot.voltage_dc
    output_voltage = vdclink.voltage_dc
    switching_freq = float(scope.get_measurement_Px(6))
    duty_boost = float(scope.get_measurement_Px(7))

    if abs(source_input_current) <= 1e-10:
        input_resistance = np.nan
    else:
        input_resistance = meas_input_voltage / source_input_current

    data.append({
        'Source Input Voltage (V)': source_input_voltage,
        'Input Voltage (V)': meas_input_voltage,
        'Input Current (A)': source_input_current,
        'Input Power (W)': meas_input_voltage * source_input_current,
        'Output DC Voltage (V)': output_voltage,
        'Resistance (Ohm)': input_resistance,
        'Switching freq. (Hz)': switching_freq,
        'Duty100': duty_boost}, ignore_index=True)

    data.to_csv('example.csv')
