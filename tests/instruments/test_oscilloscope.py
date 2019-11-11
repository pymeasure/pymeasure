from pymeasure.instruments.instrument import Instrument
from pymeasure.instruments.oscilloscope import Oscilloscope
from pymeasure.instruments.rigol import *
from pymeasure.adapters import VISAAdapter

adapter = VISAAdapter("INPUT VISA ADDR HERE")
osc = Oscilloscope(adapter)
t = osc["T"]
c1 = osc[1]
c2 = osc[2]
acq = osc.getAcquisitor([t, c1, c2])



from matplotlib import pyplot as plt
for i in range(10):
    x, y1, y2 = acq()
    plt.plot(x, y1, label=str(i)+"_1")
    plt.plot(x, y2, label=str(i)+"_2")
    #plt.plot(y1, y2, label=str(i))
plt.grid()
plt.legend()
plt.show()