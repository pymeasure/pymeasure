from typing import Union
from pint import Quantity as Q_

from pymeasure.instruments import Instrument
from pymeasure.instruments.smaract.utils import check_type

from pymeasure.instruments.validators import truncated_range


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



    def move_abs(self, position: Union[Q_, int]):

        self.write(f":MPA0P{check_type(position, 'um')}")

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f"MPR{check_type(position, 'um')}")

    def move_to_ref(self, position: Q_):
        """Moves up/down to reference"""
        self.write(f"MTR0")

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f"M0DU")

    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f"M0DD")

    def stop(self):
        """Stops any process."""
        self.write(f"S")

    def get_position(self, channel_index):
        """
        Retourne la position actuelle en micromètres.
        Commande: GP<channel>[cite: 971].
        """
        self.write(f"GP{channel_index}")
        response = self.read
        # Réponse format: :P<channel>P<position>
        return  float(response[3:])
        return None








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
