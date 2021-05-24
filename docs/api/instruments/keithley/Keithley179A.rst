##############################################
Datron 1071 up to 7.5 digit DMM
##############################################

.. currentmodule:: pymeasure.instruments.datron.datron1071


**********************************************
General Information
**********************************************

  
    Represent the Keithley 179A DMM
    Read value Keithley 179A
    no units, the Keithley 179A can not cange any mode or range,
    only manuel set on DMM
        
    Read value Keithley 179A no units
    Unit has no own SCPI commandos. 
 

    Commandos:
    readval     read val from DMM 
    id          fake IDN
    
    
    
    
**********************************************
Examples
**********************************************


.. code-block:: python    
    
from pymeasure.instruments.keithley import Keithley179A
from pymeasure.adapters import PrologixAdapter

adapter = PrologixAdapter('/dev/ttyUSB0')
KeithleyDMM = Keithley179A(adapter.gpib(24))

print (KeithleyDMM.id)

print (KeithleyDMM.readval)
