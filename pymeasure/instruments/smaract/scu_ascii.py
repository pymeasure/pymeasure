
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
        self._freq: Q_ = Q_(260, 'Hz')
        self.steps =250


    frequency_max = Instrument.control(
        ":GCLF0",
        ":SCLF0F%d",
        """Control the maximum frequency in an absolute move""",
        set_process = lambda v: check_type(v, 'Hz'),
        get_process = lambda s: Q_(s[6:], 'Hz'),
    )

    #WORKING
    def check_sensor_present(self):
        """Check if the sensor is present."""
        self.write(f':GSP0')
        response = self.read()
        return response == ':SP0P'

    def calibrate_sensor(self):
        """Calibrate the sensor. Has to done before the use of move to reference. Make sure not close to mechanical limit"""
        self.write(f':CS0')
        #M.WEBER : possible de regarder les 'status code' pour verifier si la caliberation s'est bien effectué

    def set_zero_pos(self):
        """Set the current position as position zero."""
        if self.check_sensor_present:
            self.write(f":SZ0")
        else:
            raise NotImplementedError

    def check_amplitude(self, amplitude: Q_):
        """Check if amplitude is present and if it is inside the given boundary."""
        if amplitude is None:
            amplitude = self._amplitude
        else:
            self._amplitude = amplitude
        if amplitude > 1000 or amplitude < 150:
            raise ValueError
        return amplitude

    def check_freq(self, freq: Q_):
        """Check if frequency is present and if it is inside the given boundary."""
        if freq is None:
            freq = self._freq
        else:
            self._freq = freq
        if freq > 18500 or freq < 1:
            raise ValueError
        return freq

    def check_steps(self, steps):
        """Check if steps are parametrized and if it is inside the given boundary."""
        if steps is None:
            steps = self._steps
        else:
            self._steps = steps
        if steps > 30000 or steps < 1:
            raise ValueError
        return steps

    def set_steps_parameters(self, steps: int, freq: Q_ = int, amplitude: Q_ = int):
        """Set steps parameters.Freq[1;18500] in Hz and Amplitude[150;1000] in dV and Steps[1;30000] no unit"""
        amplitude = self.check_amplitude(amplitude)
        freq = self.check_freq(freq)
        steps = self.check_steps(steps)

    def move_steps_up(self, steps: int, freq: Q_ = int, amplitude: Q_ = int):
        """Moves up, Freq[1;18500] in Hz and Amplitude[150;1000] in dV and Steps[1;30000] no unit"""

        amplitude = self.check_amplitude(amplitude)
        freq=self.check_freq(freq)

        self.write(f":U0F{check_type(freq,'Hz')}A{check_type(amplitude,'dV')}S{steps}")

    def move_steps_down(self, steps: int, freq: Q_ = int, amplitude: Q_ = int):
        """Moves up, Freq[1;18500] in Hz and Amplitude[150;1000] in dV and Steps[1;30000] no unit"""
        amplitude = self.check_amplitude(amplitude)
        freq = self.check_freq(freq)

        self.write(f":D0F{check_type(freq, 'Hz')}A{check_type(amplitude, 'dV')}S{steps}")

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
            self.write(f"MTR0H1000Z1")

    def move_to_end_up(self):
        """Moves up until end of line"""
        self.write(f":MES0DU")


    def move_to_end_down(self):
        """Moves down until end of line"""
        self.write(f":MES0DD")

    def stop(self):
        """Stops any process."""
        self.write(f":S0")

    def get_position(self) :
        """Returns the current position in micrometres."""
        if check_sensor_present():
        if self.unit == '':
            raise NotImplementedError

class SmarActSCULinear(SmarActSCU_USB):
    unit = 'um'

    def move_abs(self, position: Q_):
        self.write(f":MPA0P{check_type(position, self.unit)}")

    def get_position(self):
        """Returns the current position in micrometres."""
        self.write(f":GP0")
        pos = self.read()
        self.position = (Q_(float(pos[4:]), self.unit))
        return self.position

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f"MPR{check_type(position, self.unit)}")


class SmarActSCUAngular(SmarActSCU_USB):
    unit = 'm°'

    def move_abs(self, position: Q_):
        self.write(f":MAA0P{check_type(position, self.unit)}")

    def get_angle(self):
        """ Returns the current angle in degrees"""
        self.write(f":GA0")
        ang = self.read()
        self.angle = (Q_(float(ang[4:]), self.unit))
        return self.angle

    def move_rel(self, position: Q_):
        """Moves up a distance + current position"""
        self.write(f"MAR{check_type(position, self.unit)}")


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
