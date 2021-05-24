##############################################
Datron 1071 up to 7.5 digit DMM
##############################################

.. currentmodule:: pymeasure.instruments.datron.datron1071


**********************************************
General Information
**********************************************

    Represent the Datron 1071 high resulution DMM up to 7.5 digit, old but stable DMM
    Unit has no own SCPI commandos. 

    Implemented: more as BASIC, useful

    Commandos:
    avarage(True / False)   Avarage mode
    filter(True / False)    Filter mode
    set_b(val)              set B register
    set_c(val)              set C register
    set_high(val)           set high limit register
    set_low(val)            set low limit register
    front()                 set Front Terminal (read Manual!)
    rear()                  set Rear Terminal (read Manual!)
    inp_zero()              Input Zero, use low EMF short
    self_tst()              Self Test, no connection. todo Error handling
    ratio_off()             ratio modus off, normal mode
    ratio_1trig()           ratio modus on, one trigger to measure (read Manual!)
    ratio_1trig()           ratio modus on, two trigger to measure (read Manual!)
    mode_ohm()              set measurement mode ohm
    mode_acv()              set measurement mode AC Voltage
    mode_dcv()              set measurement mode DC Voltage
    mode_aci()              set measurement mode AC Current
    mode_dci()              set measurement mode DC Current
    mode_dcacv()            set measurement mode AC Voltage coppling DC
    mode_dcaci()            set measurement mode AC Current coppling DC
    cal_enable()            enable CALIBRATION MODE (read Manual!)
    cal_diable(self)        diable CALIBRATION MODE
    cal_zero()              DMM cal zero (read Manual!)
    cal_gain(opt: val)      Gain Cal of Range (read Manual!)
    cal_achf(opt: val)      Full Range HF @ AC, Cal of Range (read Manual!)
    cal_lin()               Lin cal, 1 Mohm Source spezial tool (read Manual!)
    cal_ib()                Ib cal Bias, 10 Mohm Source spezial tool (read Manual!)
    write_raw(val)          send raw data strint to DMM, 'R4F3' DCV, Range 1 V
    rangemode(mode)         range R0 - R7, auto
    minmax_cls()            clear min max store
    mode_max()              max modus
    mode_min()              min modus
    mode_maxmin()           max-min modus
    mode_maxmin_off()       max min modus off, normal mode
    triggermode(mode)       T0 - T7, int, ext, SW
    trigger()               SW trigger
    readval(loops=10,trg = False) Returns a List [0]Value, [1]Unit, 
        [2]Setting 

    get_register(register)  Get Register,B, C ,HLIMIT or LLIMIT
    
    
    
    
    
**********************************************
Examples
**********************************************


.. code-block:: python    
    
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
