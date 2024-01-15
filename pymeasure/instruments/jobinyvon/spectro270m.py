from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range, strict_range
from pyvisa.constants import ControlFlow, Parity, StopBits
import time
import pyvisa
from pyvisa import VisaIOError


def get_steps_returns(steps_str: str):
    steps_str = steps_str.lstrip('o')
    steps_str = steps_str.rstrip('\r')
    return int(steps_str)

def read_int(string: str):
    numeric_string = ''.join(char for char in string if char.isdigit())
    return int(numeric_string)

class JY270M(Instrument):
    """This is a class for the 270M JY spectrometer."""

    """Backlash in number of motor steps"""
    _backlash = 320
    _steps_nm = 32
    _slit_steps_micron = 0.15748
    _lambda_max = 1171.68
    _max_steps = 37494
    _max_steps_slit = 1102.36


    def __init__(self, adapter, name = "JY270M", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

    motor_init = Instrument.control(
        'A',
        '',
        """Spectrometer initialization""",
    )

    gsteps = Instrument.control(
        'H0\r',
        'F0,%d\r',
        """Control the relative step displacement of the grating motor""",
        get_process=get_steps_returns,
    )

    entrysteps = Instrument.control(
        'j0,0\r',
        'k0,0,%d\r',
        """Control the relative step displacement of the entry slit""",
        get_process=get_steps_returns,
    )

    exitsteps = Instrument.control(
        'j0,2\r',
        'k0,2,%d\r',
        """Control the relative step displacement of the exit slit""",
        get_process=get_steps_returns,
    )

    def read(self, **kwargs):
        read = b''
        for ind in range(10000):
            try:
                read += self.read_bytes(1)
            except VisaIOError:
                break
        return read.decode()

    def _write_read(self, command: bytes):
        self.write_bytes(command)
        read = b''
        for ind in range(10000):
            try:
                read += self.read_bytes(1)
            except VisaIOError:
                break
        return read

    def _get_code(self, ans: bytes):
        if len(ans) > 0:
            return ans.decode()[0]
        else:
            return ''

    def unstuck(self):
        ans = self._write_read(b'\xF8')
        ans = self._write_read(b'\xDE')

    def auto_baud(self):
        """Trying to establish intelligent mode

        Return True if done else False
        """
        while True:
            ans = self._write_read(b' ')
            if len(ans) != 0:
                break
                print(ans)

        code = self._get_code(ans)
        if code != 'F':
            if code == "*":
                ans = self._write_read(b'\xF7')
                code = self._get_code(ans)
                if code != '=':
                    return False
                ans = self._write_read(b' ')
                code = self._get_code(ans)

            if code == "B":
                ans = self._write_read(b'O2000\0')
                time.sleep(0.5)
                ans = self._write_read(b' ')
                code = self._get_code(ans)
                if code == 'F':
                    return True
                elif code == ' ':
                    ans = self._write_read(b'\xF8')
                    ans = self._write_read(b' ')
                    code = self._get_code(ans)
                    if code == 'F':

                        return True
                    else:
                        self.unstuck()
                        return False
                else:
                    self.unstuck()
                    return False
            else:
                self.unstuck()
                return False
        return True

    def move_grating_steps(self, nsteps: int):
        """Absolute positioning of the grating motor in number of steps"""
        ans = self._write_read(f'F0,{nsteps - self.gsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_grating_wavelength(self):
        """Reading the wavelength from the grating motor"""
        return self._lambda_max - ((self._max_steps - self.gsteps) / self._steps_nm)

    def move_grating_wavelength(self, wavelength: float):
        """Positioning of the grating motor in wavelength"""
        steps = int(self._max_steps - int((self._lambda_max - wavelength) * self._steps_nm))
        self.gsteps =steps

    def move_entry_slit_steps(self, nsteps: int):
        """Absolut positioning of the entry slit motor in number of steps"""
        ans = self._write_read(f'k0,0,{nsteps - self.entrysteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_entry_slit_microns(self):
        """Reading of the entry slit absolute position in millimeters"""
        return self.entrysteps/self._slit_steps_micron

    def move_entry_slit_microns(self, microns: float):
        """Absolute positioning of the entry slit in millimeters"""
        pos = microns * self._slit_steps_micron
        ans = self._write_read(f'k0,0,{pos - self.entrysteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def move_exit_slit_steps(self, nsteps: int):
        """Absolut positioning of the exit slit motor in number of steps"""
        ans = self._write_read(f'k0,2,{nsteps - self.exitsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_exit_slit_microns(self):
        """Reading of the exit slit absolute position in millimeters"""
        return self.exitsteps / self._slit_steps_micron

    def move_exit_slit_microns(self, microns: float):
        """Absolute positioning of the exit slit in millimeters"""
        pos = microns * self._slit_steps_micron
        ans = self._write_read(f'k0,2,{pos - self.exitsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def check_get_errors(self, error):
        print(error)
        pass

    def motor_stop(self):
        ans = self._write_read(b'L')
        code = self._get_code(ans)
        assert code == 'o'

    def motor_busy_check(self):
        ans = self._write_read(b'E\r').decode()
        if ans == "oz":
            return False
        if ans == "oq":
            return True

if __name__ == '__main__':
    spectro = JY270M('COM1',
                     baud_rate=9600,
                     timeout=300,
                     parity=Parity.none,
                     data_bits=8,
                     stop_bits=StopBits.one,
                     flow_control=ControlFlow.dtr_dsr,
                     write_termination='',
                     read_termination='')











