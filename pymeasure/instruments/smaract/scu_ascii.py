import numpy as ny

#import serial reste a installer
#import serial.tools.list_ports
import time

from pymeasure.instruments import Instrument

class SmarActSCU_USB(Instrument):

    def __init__(self, adapter, name='SCUController', **kwargs):
        super().__init__(adapter, name,
                         read_termination='\n',
                         write_termination='\n',
                         **kwargs)


if __name__ == "__main__":
    inst = SmarActSCU_USB('ASRL3::INSTR')
    pass
    inst.close()
    # import pyvisa
    # rm = pyvisa.ResourceManager()
    # ressources = rm.list_resources()
    # print(ressources)
    #
    # inst = rm.open_resource(ressources[0])
    # inst.write_termination = '\n'
    # inst.read_termination = '\n'
    # pass
    #
    # inst.close()
