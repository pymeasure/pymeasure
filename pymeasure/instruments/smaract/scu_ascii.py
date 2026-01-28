from telnetlib import theNULL
from typing import Union
from pint import Quantity as Q_

from pymeasure.instruments import Instrument
from pymeasure.instruments.smaract.utils import check_type

from pymeasure.instruments.validators import truncated_range

# <channel> : zero-based channel index. Valid indices are 0,1 and 2
# <angel> : the current angle of the position in millidegree

class SmarActSCU_USB(Instrument):
    unit: str = ''

    def __init__(self, adapter, name='SCUController', **kwargs):
        super().__init__(adapter, name,
                         read_termination='\n',
                         write_termination='\n',
                         **kwargs)

        self._amplitude: Q_ = Q_(1000, 'dV')

    frequency_max = Instrument.control(
        ":GCLF0",
        ":SCLF0F%d",
        """ Control the maximum frequency in an absolute move """,
        set_process = lambda v: check_type(v, 'Hz'),
        get_process = lambda s: Q_(s[6:], 'Hz'),
    )

    def check_sensor_present(self):
        """Check if sensor is present."""

        self.write(f':GSP0')
        response = self.read()
        return response[3] == 'P'

    def set_zero_pos(self):
        """Set the current position as position zero."""
        if self.check_sensor_present is True:
            self.write(f"SZ0")
        else:
            raise NotImplementedError

    def check_amplitude(self, amplitude: Q_):
        if amplitude is None:
            amplitude = self._amplitude
        else:
            self._amplitude = amplitude
        # truncated amplitude zrt
        #Amplitude[150;1000]
        return amplitude

    def move_steps_up(self, steps: int, frequency=Q_(1000, 'Hz'), amplitude: Q_ = None):
        """Moves up, Freq[1;18500] in Hz and Amplitude[150;1000] in dV and Steps[1;30000] no unit"""

        amplitude = self.check_amplitude(amplitude)

        self.write(f"U0F{check_type(frequency,'Hz')}A{check_type(amplitude,'dV')} S{steps}")

    def move_steps_down(self, steps: int, frequency: Q_, amplitude: Q_):
        """Moves up, Freq[1;18500] in Hz and Amplitude[150;1000] in dV and Steps[1;30000] no unit"""
        self.write(f"D0F{check_type(frequency,'Hz')}A{check_type(amplitude,'dV')} S{steps}")

    def move_abs(self, position: Union[Q_, int]):
        raise NotImplementedError

    def move_rel(self, position: Q_):
        if position.magnitude >= 0:
            self.move_steps_up(position.magnitude)
        else:
            self.move_steps_down(position.magnitude)

    def move_to_ref(self):
        """Moves up/down to reference"""
        if self.unit == '':
            raise NotImplementedError
        else:
            self.write(f"MTR0")
    def move_to_ref(self):
        """Moves to reference"""
        self.write(f":MTR0H0Z1")

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f"MES0DU")
        self.write(f":MES0DU")

    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f"MES0DD")
        self.write(f":MES0DD")

    def stop(self):
        """Stops any process."""
        self.write(f":S0")

    def get_position(self, channel_index) -> Q_:
        """Retourne la position actuelle en micromètres."""
        if self.unit == '':
            raise NotImplementedError




class SmarActSCULinear(SmarActSCU_USB):
    unit = 'um'

    def move_abs(self, position: Q_):
        self.write(f":MPA0P{check_type(position, self.unit)}")

    def get_position(self, channel_index) -> Q_:
        """Retourne la position actuelle en micromètres.
        Commande: GP<channel>[cite: 971]."""
        self.write(f"GP{channel_index}")
        response = self.read
        # Réponse format: :P<channel>P<position>
        return Q_(float(response[3:]), self.unit)

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f"MPR{check_type(position, self.unit)}")


class SmarActSCUAngular(SmarActSCU_USB):
    unit = 'm°'

    def move_abs(self, position: Q_):
        self.write(f":MAA0P{check_type(position, self.unit)}")

    def get_angle(self, channel_index) -> Q_:
        """
        Retourne la position actuelle en millidegree.
        Commande: GP<channel>[cite: 971].
        """
        self.write(f"GA{channel_index}")
        response = self.read
        # Réponse format: :A<channel>A<angel>
        return Q_(float(response[3:]), self.unit)

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f"MAR{check_type(position, self.unit)}")


if __name__ == "__main__":
    inst = SmarActSCULinear('ASRL3::INSTR')
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
