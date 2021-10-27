"""
Antenna Pattern Measurement
Name: Python antenna directivity measurements
Synopsis: This test script implements an antenna measurement system
Description: This is a test script to evaluate the basic
capability of PyVISA. Antenna directivity is measured as
a function of azimuth at several frequencies.
Requires: DAMS platform controller, Anritsu VNA 
PyVISA, NI VISA drivers and other SciPy modules
Author: 
Date: May 2, 2016 coding started
Revision History
"""
import os
#import sys
import numpy as np
import pandas as pd
import visa, time
import matplotlib.pyplot as plt
#%matplotlib inline

rm = visa.ResourceManager() #use default resource manager
print(rm.list_resources())

# open DAMS and the VNA
dams = rm.open_resource('ASRL3::INSTR') 
dams.open()
vna = rm.open_resource('TCPIP::172.18.140.12::INSTR') 
vna.open()

#configure the DAMS
dams.baud_rate = 57600
dams.write('GG*')
dams.write('GGN+0cz')
dams.write('X0F')   # Turn on Full Stepping
dams.write('X0P1')  # Set holding current on
dams.write('X0B60') # Set Begin Speed (steps per second)
dams.write('X0E100')    #Set End Speed (steps per second)
dams.write('X0S2')  #Set Acceleration Slope (standard is 2)

#configure the VNA
#Sets the resolution of the sweep
#LOW for 137 data points
#MED for 275 data points
#HIGH for 551 data points
vna.write(':SWE:RES LOW') # set number of data ponts
vna.write('SOUR:POW HIGH')   # HIGH: 0 dBm, LOW: -35 dBm
vna.write(':CONFigure:MEASure:S21:LMAG')    # set to measure s21

#take measurements at the following frequencies, units are GHz
freq_list = [1.56, 1.57, 1.575, 1.58, 1.59]

# set span a bit wider than lowest and highest frequencies
f_start = np.min(freq_list) - 0.005  # set for 5MHz lower
f_stop = np.max(freq_list) + 0.005  # set for 5MHz higher
vna.write(':FREQ:STAR '+'{:.3f}'.format(f_start)+' GHz')
vna.write(':FREQ:STOP '+'{:.3f}'.format(f_stop)+' GHz')

# clear all markers
vna.write(':CALC:MARK:AOFF')  #turns off all markers
#vna.write(':CALC:MARK:TABL:STAT OFF') #turn off marker table <<-- not working

#set markers
for i in range(len(freq_list)):
    #print(freq_list[i])
    vna.write(':CALC:MARK'+str(i+1)+':STAT ON')
    vna.write(':CALC:MARK'+str(i+1)+':X '+str(freq_list[i])+' GHz')

# set up measurement interval
steps_per_rev = 2880.0
meas_inc = 2.0    #take measurement every X degrees
step_size = steps_per_rev/360.0 * meas_inc
num_steps = 360.0/meas_inc

#make a list of np.arrays
raw_data = [[]]*len(freq_list)
for i in range(len(freq_list)):
    raw_data[i] = np.zeros(num_steps)

az = np.zeros(num_steps)    # azmuth angle

dams_str = 'X0RN+'+str(int(step_size))+'\r'# build DAMS control string
  
# run DAMS 360 deg in Az and store data in array
for i in range(int(num_steps)):
    dams.write(dams_str)
    time.sleep(2)       # wait 2 sec before taking data
    az[i] = i*meas_inc
    # read markers
    for j in range(len(freq_list)):
        raw_data[j][i] = float(vna.ask(':CALC:MARK'+str(j+1)+':Y?'))
        
# normalize raw data
r_max = np.max(raw_data)
norm_data = [[]]*len(freq_list)
for i in range(len(freq_list)):
    norm_data[i] = raw_data[i]-r_max

# To add one subplot
# The 111 specifies 1 row, 1 column on subplot #1
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)
ax.grid(True)
minGrid = -30  #set plot grid
maxGrid = 0
gridSpacing = 5
ax.set_yticks(np.arange(minGrid,maxGrid,gridSpacing))
ax.set_theta_zero_location("N")
ax.set_theta_direction(-1)
ax.autoscale(enable=False)

# add data to the plot
plot_x = az[:] * np.pi/180.0
for i in range(len(freq_list)):
    ax.plot(plot_x, norm_data[i], linewidth=2, label=str(freq_list[i])+'GHz')    
    
# Setting the graph title & legend
ax.set_title("Normalized Test Data")      
ax.legend(bbox_to_anchor =(-.5,1),loc=2)
plt.show()

# save numpy arrays into a panda data frame
values = [[]]*(len(freq_list)+1)
values[0] = az
for i in range(len(freq_list)):
    values[i+1] = norm_data[i]

df = pd.DataFrame(values)
# add lables to data
df = df.rename(index={0:'Az'})
for i in range(len(freq_list)):
    df = df.rename(index={i+1:str(freq_list[i])+'GHz'})    
    
# save data frame to file in the project directory
os.chdir(r'C:\Users\...\Documents\Python for Instrument Control')
writer = pd.ExcelWriter('Antenna_data.xlsx')
df.to_excel(writer,'Sheet1')
writer.save()

#End 
print('Done')

A plastic fixture to mount antennas was made and is shown in the Figure below.  The antenna mounted to the fixture is a C-Band antenna.


Last updated: 6/26/2016


Posted 7th May 2016 by Unknown
 
0 Add a comment

