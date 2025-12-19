from typing import Union
from pint import Quantity as Q_

from pymeasure.instruments import Instrument
from pymeasure.instruments.smaract.utils import check_type

from pymeasure.instruments.validators import truncated_range


class SmarActSCU_USB(Instrument):
    """ Blblabla documentation

    """
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
        get_process = lambda s: Q_(s.split('CLF0F')[1], 'Hz'),
    )

    def move_abs(self, position: Union[Q_, int]):

        self.write(f":MPA0P{check_type(position, 'um')}")

    def move_pos_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f":MPR0P{check_type(position, 'um')}")

    def move_to_ref(self):
        """Moves to reference"""
        self.write(f":MTR0H0Z1")

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f":MES0DU")

    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f":MES0DD")

    def stop(self):
        """Stops any process."""
        self.write(f":S0")

    def get_position(self):
        """
        Retourne la position actuelle en micromètres.
        Commande: GP<channel>[cite: 971].
        """
        self.write(f":GP0")
        response = self.read()
        # Réponse format: :P<channel>P<position>
        response = response.split(":P0P")[1]
        return  float(response)
    def get_angle(self):
        """
        Retourne la position actuelle en micromètres.
        Commande: GP<channel>[cite: 971].
        """
        self.write(f":GA0")
        response = self.read()
        # Réponse format: :A<channel>A<position>R0
        response = response.split(":A0A")[1][:-2]
        return  float(response)
    def move_rel(self, angle: Q_):
        """Moves up a angle + current angle"""
        self.write(f":MAA0A{check_type(angle, ' m°')}")


if __name__ == "__main__":
    inst = SmarActSCU_USB('ASRL3::INSTR')
    inst.get_position()
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
