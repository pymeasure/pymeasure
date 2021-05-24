from pymeasure.instruments.datron import datron1071
from pymeasure.adapters import PrologixAdapter
import time

# Adapter Prologix USB GPIB Adapter
adapter = PrologixAdapter('/dev/ttyUSB0')
#Datron on GPIB Adresse 30
dmm = datron1071(adapter.gpib(30))

#Read 'Fake' IDN
print (dmm.id)

time.sleep(1)
#set DC Voltage
dmm.mode_dcv()
#set to sw Trigger
dmm.triggermode('SW')
#Range R6 = 1000 V
dmm.rangemode('R6')
#Trigger DMM 
dmm.trigger()
time.sleep(5)
#Read DMM
print (dmm.readval(trg=True))

#set DMM internel trigger moder
dmm.triggermode('int')
#set range R1 = 100 mV
dmm.rangemode('R1')

n=0
while n !=10:
    #read dmm val only
    print (dmm.readval(trg=False)[0])
    n = n+1

