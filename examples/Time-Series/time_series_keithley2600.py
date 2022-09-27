# Example on how to use pymeasure with the keithley2636a
from pymeasure.instruments.keithley import Keithley2600
from time import sleep

smu = Keithley2600("ASRL/dev/ttyUSB0::INSTR")
# Connect keithley via RS-232 to USB connector to computer and follow https://pyvisa.readthedocs.io/projects/pyvisa-py/en/latest/ to detect the device
# import pyvisa
# rm = pyvisa.ResourceManager()
# rm.list_resources()

print(smu.id)


# %% When the with-block is exited, the shutdown method of the instrument will be called, turning the system into a safe state.

with Keithley2600("ASRL/dev/ttyUSB0::INSTR") as smu:
    smu.ChA.wires_mode = "2"
    smu.ChA.source_voltage = 1
    sleep(0.1)
    smu.ChA.apply_voltage()
    i = smu.ChA.current
    sleep(5) # wait here to give the instrument time to react
    v = smu.ChA.voltage
    sleep(5)

print(i, "A", v, "V")




