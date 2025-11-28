
from pint import Quantity as Q_

from pymeasure.instruments import Instrument
from pymeasure.instruments.smaract.utils import check_type

class SmarActSCU_USB(Instrument):

    def __init__(self, adapter, name='SCUController', **kwargs):
        super().__init__(adapter, name,
                         read_termination='\n',
                         write_termination='\n',
                         **kwargs)

    frequency_max = Instrument.control(
        ":GCLF0",
        ":SCLF0F%d",
        """ Control the maximum frequency in an absolute move """,
        set_process = lambda v: check_type(v, 'Hz'),
        get_process = lambda s: Q_(s[6:], 'Hz'),
    )

    def move_abs(self, position: Q_):
        ...
        self.write()


if __name__ == "__main__":
    inst = SmarActSCU_USB('ASRL3::INSTR')
    pass

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
