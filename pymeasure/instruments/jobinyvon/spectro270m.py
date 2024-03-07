#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range, strict_range
from pyvisa.constants import ControlFlow, Parity, StopBits
import time
import pyvisa
from pyvisa import VisaIOError


def get_steps_returns(steps_str: str):
    """
    When asked for the number of steps, the spectrometer returns a string in
    format "o(number of steps)\r", with this function we get rid of the "o" and 
    the "\r" and we convert the resulting string to an integer.
    """
    steps_str = steps_str.lstrip('o')
    steps_str = steps_str.rstrip('\r')
    return int(steps_str)

def read_int(string: str):
    """
    When we expect a numeric answer from the spectrometer, it sometimes sends 
    some more characters in between, and with this function we get rid of those
    extra characters. 
    """
    numeric_string = ''.join(char for char in string if char.isdigit())
    return int(numeric_string)

class JY270M(Instrument):
    """This class represents the Jobin-Yvon 270M Driver."""

    """Backlash in number of motor steps."""
    _backlash = 320
    
    """Number of motor steps per nm, nm per motor step, slit steps per micron, and microns per slit step."""
    _steps_nm = 32
    _nm_step = 1/_steps_nm
    _slit_steps_micron = 0.15748
    _slit_microns_step = 1.0/_slit_steps_micron
    
    """Maximum value for the wavelength in nm, maximum number of steps for
    the grating motor and for the entry and exit slits."""
    _lambda_max = 1171.68
    _max_steps = 37494
    _max_steps_slit = 1102.36


    def __init__(self, adapter, name = "JY270M", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

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
        """
        This function reads the answer of the spectrometer one byte at a time.
        """
        read = b''
        for ind in range(10000):
            try:
                read += self.read_bytes(1)
            except VisaIOError:
                break
        return read.decode()

    def write_read(self, command: bytes):
        """
        This function writes a command to the spectrometer and reads the answer of the spectrometer one byte at a time.
        """
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
        ans = self.write_read(b'\xF8')
        ans = self.write_read(b'\xDE')

    def auto_baud(self):
        """Trying to establish intelligent mode

        Return True if done else False
        """
        while True:
            ans = self.write_read(b' ')
            if len(ans) != 0:
                break
                print(ans)

        code = self._get_code(ans)
        if code != 'F':
            if code == "*":
                ans = self.write_read(b'\xF7')
                code = self._get_code(ans)
                if code != '=':
                    return False
                ans = self.write_read(b' ')
                code = self._get_code(ans)

            if code == "B":
                ans = self.write_read(b'O2000\0')
                time.sleep(0.5)
                ans = self.write_read(b' ')
                code = self._get_code(ans)
                if code == 'F':
                    return True
                elif code == ' ':
                    ans = self.write_read(b'\xF8')
                    ans = self.write_read(b' ')
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

    def motor_init(self) -> bool:
        """
        Spectrometer initialization
        """
        self.write_read(b'A')
        time.sleep(30)

    def move_grating_steps(self, nsteps: int):
        """Absolute positioning of the grating motor in number of steps."""
        ans = self.write_read(f'F0,{nsteps - self.gsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_grating_wavelength(self):
        """Reading the wavelength from the grating motor."""
        return self._lambda_max - ((self._max_steps - self.gsteps) / self._steps_nm)

    def move_grating_wavelength(self, wavelength: float):
        """Absolute positioning of the grating motor in wavelength"""
        steps = int(self._max_steps - int((self._lambda_max - wavelength) * self._steps_nm))
        self.move_grating_steps(steps)

    def move_entry_slit_steps(self, nsteps: int):
        """Absolute positioning of the entry slit motor in number of steps"""
        ans = self.write_read(f'k0,0,{nsteps - self.entrysteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_entry_slit_microns(self):
        """Reading of the entry slit absolute position in micrometers"""
        return self.entrysteps/self._slit_steps_micron

    def move_entry_slit_microns(self, microns: float):
        """Absolute positioning of the entry slit in micrometers"""
        pos = microns * self._slit_steps_micron
        ans = self.write_read(f'k0,0,{pos - self.entrysteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def move_exit_slit_steps(self, nsteps: int):
        """Absolut positioning of the exit slit motor in number of steps"""
        ans = self.write_read(f'k0,2,{nsteps - self.exitsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def get_exit_slit_microns(self):
        """Reading of the exit slit absolute position in millimeters"""
        return self.exitsteps / self._slit_steps_micron

    def move_exit_slit_microns(self, microns: float):
        """Absolute positioning of the exit slit in millimeters"""
        pos = microns * self._slit_steps_micron
        ans = self.write_read(f'k0,2,{pos - self.exitsteps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    def check_get_errors(self, error):
        print(error)
        pass

    def motor_stop(self):
        ans = self.write_read(b'L')
        code = self._get_code(ans)
        assert code == 'o'

    def motor_busy_check(self):
        ans = self.write_read(b'E\r').decode()
        if ans == "oz":
            return False # We return False if the motor is not busy.
        if ans == "oq":
            return True # We return True if the motor is busy.

    def motor_available(self):
        """
        This function verifies if the grating motor or the slits motors are free.
        """
        while self.motor_busy_check():
            pass
        time.sleep(1)
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
                     read_termination='',
                     includeSCPI=False)
