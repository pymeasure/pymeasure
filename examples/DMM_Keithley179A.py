from pymeasure.instruments.keithley import Keithley179A
from pymeasure.adapters import PrologixAdapter

adapter = PrologixAdapter('/dev/ttyUSB0')
KeithleyDMM = Keithley179A(adapter.gpib(24))

print (KeithleyDMM.id)

print (KeithleyDMM.readval)


