# %% Example on how to use pymeasure with the keithley2636a
# Code blocks are seperated by # %%
# We use a 1 MOhm resistor connected with clamps to channel A (plus and minus wires) as test object

import numpy as np
import pandas as pd
from pymeasure.instruments.keithley import Keithley2600
from pymeasure.instruments import list_resources
from time import sleep, time


# Example on how to connect to your device
# For Debian GNU/Linux your user needs to be member of the *dialout* group (sudo adduser <USER> dialout) to have the right of accessing USB devices
# Connect keithley via RS-232 to USB connector to computer and check if it is connected:
list_resources() # -> this will list your connections e.g. ('ASRL/dev/ttyUSB1::INSTR',)

# %% For interactive use connect to the instrument
smu = Keithley2600("ASRL/dev/ttyUSB1::INSTR")
print(smu.id)

# %% Define measureement parameter
voltage = 10 # bias in V
duration = 5 # s
nplc = 10 # Number power line cycles from 0.001 to 25 (f = 50 Hz or 60 Hz -> nplc = 1 / f )
line_frequency = 50  # can we read this from the instrument?
t_step = nplc / line_frequency  

n_datapoints = int(duration / t_step + 1) # one point more since we want to measure at cero too
i_range = 1e-3 # range of the current
i_compliance=0.1 # max current / compliance

# %% When the with-block is exited, the shutdown method of the instrument will be called, turning the system into a safe state.
with Keithley2600("ASRL/dev/ttyUSB1::INSTR") as smu:

    # First define input parameters
    smu.reset()
    smu.ChA.wires_mode = "2"
    smu.ChA.source_voltage = voltage
    sleep(0.1) # wait here to give the instrument time to react

    smu.ChA.measure_current(nplc=nplc, current=i_range, auto_range=False) # with auto_range=True it takes very long and sleep(X) might to be increased
    sleep(0.1)

    # Apply bias
    smu.ChA.apply_voltage(compliance_current=i_compliance)  # Somehow I would expect this to turn source on but it does not
    sleep(0.1)
    smu.ChA.source_output = "ON" # needed to turn source on

    # Measure current
    currents = np.zeros(n_datapoints)
    times = np.zeros(n_datapoints)

    for i in range(n_datapoints):
        times[i] = time()
        currents[i] = smu.ChA.current
    sleep(0.1)
    smu.ChA.source_output = "OFF" # needed to turn source off even inside with statement

    # Beep once the measurement is done -> this is not implemented so we send lua strings to the smu -> for a list of commands see https://www.tek.com/keithley-source-measure-units/smu-2600b-series-sourcemeter-manual-8
    smu.write("beeper.enable = beeper.ON")
    smu.write("beeper.beep(.5,292.00)")


# %% Save the data columns in a pandas DataFrame and inspect 
data = pd.DataFrame({
    'Time (s)': times - times[0],
    'Current (A)': currents
})

# For 1 MOhm and 10V bias we expect ~ 0.01 mA -> in my case it measured 0.009 mA but this should be tolerable. If your measurement is totally off check all the connections
print(data.tail())
print("Compare the difference of duration = {}s and the end time of {}s in our DataFrame".format(duration, data["Time (s)"][-1:].values))
print("The timing is not accurate since there is a delaye from the for-loop. If you do only care about the number of datapoints this is not a problem")

# %% Advanced example with buffer
# At the time of writing the low level function to use the buffer of the device is not available via attributes
# So we use the write() and read() methods to access them like the beeper above
with Keithley2600("ASRL/dev/ttyUSB1::INSTR") as smu:

    # First define input parameters
    smu.reset()
    smu.ChA.wires_mode = "2"

    # Prepare buffer
    smu.write("smua.nvbuffer1.clear()")  # smua corresponds to smu.ChA
    #smu.write("smua.measure.interval = t/5")   # Time between measurements in (s); ! If to small, smallest possible steps will be chosen 
    smu.write("smua.nvbuffer1.appendmode = 1")
    smu.write("smua.nvbuffer1.collecttimestamps	= 1") # True
    smu.write("smua.measure.count = {}".format(n_datapoints))


    smu.ChA.source_voltage = voltage
    sleep(0.1) # wait here to give the instrument time to react
    smu.ChA.measure_current(nplc=nplc, current=i_range, auto_range=False) # with auto_range=True it takes very long and sleep(X) might to be increased
    sleep(0.1)

    # Apply bias
    smu.ChA.apply_voltage(compliance_current=i_compliance)  # Somehow I would expect this to turn source on but it does not
    sleep(0.1)
    smu.ChA.source_output = "ON" # needed to turn source on

    # Measure current
    smu.write("smua.measure.i(smua.nvbuffer1)")
    #smu.write("waitcomplete()") # somehow not needed
    sleep(duration + 1) # Wait the time the measurement takes

    currents = np.fromstring(smu.ask("printbuffer(1, {}, smua.nvbuffer1)".format(n_datapoints)), sep=",")
    timestamps = np.fromstring(smu.ask("printbuffer(1, {}, smua.nvbuffer1.timestamps)".format(n_datapoints)), sep=",")

    smu.ChA.source_output = "OFF" # needed to turn source off even inside with statement

    # Beep once the measurement is done -> this is not implemented so we send lua strings to the smu -> for a list of commands see https://www.tek.com/keithley-source-measure-units/smu-2600b-series-sourcemeter-manual-8
    smu.write("beeper.enable = beeper.ON")
    smu.write("beeper.beep(.5,292.00)")

# %% Save the data columns in a pandas DataFrame and inspect 
data = pd.DataFrame({
    'Time (s)': timestamps,
    'Current (A)': currents
})

# For 1 MOhm and 10V bias we expect ~ 0.01 mA -> in my case it measured 0.009 mA but this should be tolerable. If your measurement is totally off check all the connections
print(data.tail())
print("Compare the difference of duration = {}s and the end time of {}s in our DataFrame".format(duration, data["Time (s)"][-1:].values))
print("The timing is way more accurate")

# Save data to file
#data.to_csv('example.csv')

