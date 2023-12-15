
import pyvisa
from pyvisa import ResourceManager
from pyvisa.constants import ControlFlow, Parity, StopBits

rm = ResourceManager()

try:
    spectro = rm.open_resource('COM1',
                     baud_rate=9600,
                     timeout=1000,
                     parity=Parity.none,
                     data_bits=8,
                     stop_bits=StopBits.one,
                     flow_control=ControlFlow.dtr_dsr,
                     write_termination='',
                     read_termination='')

    spectro.write_raw(b' ')
    spectro.read_bytes(1)

except:
    pass
finally:
    spectro.close()
