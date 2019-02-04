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
import datetime

import sys
import numpy as np
import pandas as pd
from time import sleep

from pymeasure.instruments.agilent import Agilent34461A, Agilent34465A
from pymeasure.instruments.chroma import Chroma62024p6008
from pymeasure.instruments.lecroy import WaveRunner606Zi

def timeStamped(fname, fmt='%Y%m%d%H%M%S{fname}'):
    return datetime.datetime.now().strftime(fmt).format(fname = fname)


def run():
    log_directory = 'D:\\HardCopy\\'

    # Set the input parameters
    max_voltage = 400
    min_voltage = 0
    voltage_step = 20
    delay = .1

    DATA_COLUMNS = ['DateTime',
                    'Source Input Voltage (V)',
                    'Input Voltage (V)',
                    'Input Current (A)',
                    'Input Power (W)',
                    'Output DC Voltage (V)',
                    'Resistance (Ohm)',
                    'Switching freq. (Hz)',
                    'Duty100',
                    'input_phase_current']

    data = pd.DataFrame(columns=DATA_COLUMNS)

    logging.basicConfig(filename='example.log',level=logging.DEBUG)
    logging.info("Setting up instruments")
    source = Chroma62024p6008('USB0::0x1698::0x0837::007000000446::0::INSTR', timeout=5000)
    print(source.id)
    scope = WaveRunner606Zi('146.136.35.208')
    print(scope.id)
    vdclink = Agilent34465A('TCPIP0::146.136.35.247::inst0::INSTR')
    print(vdclink.id)
    vin_mot = Agilent34461A('TCPIP0::146.136.35.210::inst0::INSTR')
    print(vin_mot.id)

    source.output_disable()
    source.output_current_limit = 5
    source.output_voltage_level = 0
    source.output_enable()
    print(vdclink.voltage_dc)
    print(vin_mot.voltage_dc)
    sleep(2)

    voltages = np.arange(min_voltage, max_voltage, voltage_step)
    steps = len(voltages)

    logging.info("Starting to sweep through voltage")
    for i, voltage in enumerate(voltages):
        print('set voltage to %d' % voltage)
        input("Press Enter to continue...")
        logging.info("Measuring efficiency input voltage: %g V" % voltage)
        try:
            source.output_voltage_level = voltage
            # Or use source.ramp_to_current(current, delay=0.1)
            sleep(5)
        except:
            source.output_disable()



        try:
            source_input_voltage = source.output_voltage
            source_input_current = source.output_current
            meas_input_voltage = vin_mot.voltage_dc
            output_voltage = vdclink.voltage_dc
            switching_freq = float(scope.get_measurement_Px(6))
            duty_boost = float(scope.get_measurement_Px(7))
            input_current_ph = float(scope.get_measurement_Px(3))
        except:
            meas_input_voltage = vin_mot.voltage_dc
            output_voltage = vdclink.voltage_dc
            switching_freq = float(scope.get_measurement_Px(6))
            duty_boost = float(scope.get_measurement_Px(7))
            input_current_ph = float(scope.get_measurement_Px(3))

        time_filename = timeStamped('_')
        filename_prtscr = log_directory + time_filename
        filename_csv = time_filename+'.csv'

        # filename_prtscr=(' foo.tif')
        scope.print_screen_autoname()
        sleep(2)

        if abs(source_input_current) <= 1e-10:
            input_resistance = np.nan
        else:
            input_resistance = meas_input_voltage / source_input_current

        data_dict = { 'DateTime': time_filename,
            'Source Input Voltage (V)': source_input_voltage,
            'Input Voltage (V)': meas_input_voltage,
            'Input Current (A)': source_input_current,
            'Input Power (W)': meas_input_voltage * source_input_current,
            'Output DC Voltage (V)': output_voltage,
            'Resistance (Ohm)': input_resistance,
            'Switching freq. (Hz)': switching_freq,
            'Duty100': duty_boost,
            'input_phase_current': input_current_ph}

        print(data_dict)

        df2 = pd.DataFrame([data_dict], columns=data_dict.keys())
        data = pd.concat([data, df2], axis=0, ignore_index=True)
        data.to_csv('example.csv')

    print('Finishing')
    scope.disconnect()
    source.output_disable()


if __name__ == "__main__":
    run()