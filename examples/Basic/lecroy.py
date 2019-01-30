# Import necessary packages
from pymeasure.instruments.lecroy import WaveRunner606Zi
import numpy as np
import pandas as pd
from time import sleep

# Set the input parameters
data_points = 50
averages = 50
max_current = 0.01
min_current = -max_current

# Connect and configure the instrument
scope = WaveRunner606Zi("TCPIP0::146.136.35.208::inst0::INSTR")
print(scope.id)
vgs=scope.measurement.top('C1')
sleep(0.1) # wait here to give the instrument time to react
vds=scope.measurement.top('C2')
sleep(0.1) # wait here to give the instrument time to react
vds_pk=scope.measurement.max('C2')
sleep(0.1) # wait here to give the instrument time to react
iph=scope.measurement.rms('C3')
sleep(0.1) # wait here to give the instrument time to react
iph_pk2pk=scope.measurement.peak2peak('C3')
sleep(0.1) # wait here to give the instrument time to react


