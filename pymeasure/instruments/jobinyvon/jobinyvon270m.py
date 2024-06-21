#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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
from pyvisa.constants import ControlFlow, Parity, StopBits
import time
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
    """
    This class represents the Jobin-Yvon 270M Driver.
    """

    """Number of motor steps per nm, nm per motor step, slit steps per 
    micron, and microns per slit step."""
    _steps_nm = 32
    _nm_step = 1 / _steps_nm
    _slit_steps_micron = 0.560
    _slit_microns_step = 1.0 / _slit_steps_micron

    """Maximum value for the wavelength in nm, maximum number of steps 
    for the grating motor and for the entry and exit slits."""
    lambda_0 = 1171.68
    _max_steps = 37494
    _max_steps_slit = 1102.36 # do not know what this is for?

    @property
    def default_timeout(self):
        """
        Usual timeout needed for normal use.
        """
        return 300

    @property
    def steps_in_one_nanometer(self):
        return self._steps_nm

    @property
    def nanometers_in_one_step(self):
        return self._nm_step

    @property
    def micrometers_in_one_step(self):
        return self._slit_microns_step

    @property
    def max_grating_steps(self):
        return self._max_steps

    def __init__(self, adapter, name="JY270M", **kwargs):

        kwargs.update(dict(baud_rate=9600,
                           timeout=self.default_timeout,
                           parity=Parity.none,
                           data_bits=8,
                           stop_bits=StopBits.one,
                           flow_control=ControlFlow.dtr_dsr,
                           write_termination='',
                           read_termination='',
                           includeSCPI=False))

        super().__init__(
            adapter,
            name,
            **kwargs)

    gsteps = Instrument.control(
        'H0\r',
        'F0,%d\r',
        "Control the relative step displacement of the grating motor.",
        get_process=get_steps_returns)

    entry_steps = Instrument.control(
        'j0,0\r',
        'k0,0,%d\r',
        "Control the relative step displacement of the entry slit.",
        get_process=get_steps_returns)

    exit_steps = Instrument.control(
        'j0,2\r',
        'k0,2,%d\r',
        "Control the relative step displacement of the exit slit.",
        get_process=get_steps_returns)

    def read(self, **kwargs):
        """
        This function reads the answer of the spectrometer one byte at a time.
        """
        read = b''
        for ind in range(100):
            try:
                r = self.read_bytes(1)
                read += r
                if r == b'\r':
                    "Not all readings end with \r so we rely on timeouts to end the loop."
                    break
            except VisaIOError:
                break
        return read.decode()

    def write_read(self, command: bytes, nread: int = 100, timeout=None, **kwargs):
        """
        This function writes a command to the spectrometer and reads the
        answer of the spectrometer one byte at a time.
        """
        timeout = self.default_timeout if timeout is None else timeout
        self.adapter.connection.timeout = timeout
        for ind in range(nread):
            try:
                r = self.read_bytes(1)
                read += r
                if r == b'\r':
                    "Not all readings end with \r so we rely on timeouts to end the loop."
                    break
            except VisaIOError:
                break
        self.adapter.connection.timeout = self.default_timeout
        return read

    @staticmethod
    def _get_code(ans: bytes):
        if len(ans) > 0:
            return ans.decode()[0]
        else:
            return ''

    def unstuck(self):
        """
        Unstuck the instrument, if it got stuck.
        """
        self.write_read(b'\xF8')
        self.write_read(b'\xDE')

    def auto_baud(self):
        """
        Set the instrument to intelligent mode to start communication.
        
        This function tries to set the spectrometer into
        intelligent mode (mode that allows communication with the
        instrument). The logic of this function is based on the
        spectrometer's datasheet.
        
        :return: boolean whether setting the instrument into
            intelligent mode was successful.
        """
        
        while True:
            ans = self.write_read(b' ')
            if len(ans) != 0:
                break

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
                self.write_read(b'O2000\0')
                time.sleep(0.5)
                ans = self.write_read(b' ')
                code = self._get_code(ans)
                if code == 'F':
                    return True
                elif code == ' ':
                    self.write_read(b'\xF8')
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
        Spectrometer initialization function.
        """
        ans = self.write_read(b'A', nread=1, timeout=100000)
        code = self._get_code(ans)
        if code != 'o':
            raise IOError(f'Wrong return code from driver, received {code}')
        return True

    def move_grating_steps(self, nsteps: int):
        """
        ABSOLUTE positioning of the grating motor in number of steps.
        """
        ans = self.write_read(f'F0,{nsteps - self.gsteps}\r'.encode(), nread=1, timeout=20000)
        code = self._get_code(ans)
        if code != 'o':
            raise IOError(f'Wrong return code from driver, received {code}')

    @property
    def grating_wavelength(self):
        """
        Reading the wavelength from the grating motor of the spectrometer.
        """
        return self.lambda_0 - ((self._max_steps - self.gsteps) / self._steps_nm)

    @grating_wavelength.setter
    def grating_wavelength(self, wavelength: float):
        """
        ABSOLUTE positioning of the grating motor in wavelength.
        """
        steps = int(self._max_steps - int((self.lambda_0 - wavelength) * self._steps_nm))
        self.move_grating_steps(steps)

    def move_entry_slit_steps(self, nsteps: int):
        """
        ABSOLUTE positioning of the entry slit motor in number of steps.
        """
        ans = self.write_read(f'k0,0,{nsteps - self.entry_steps}\r'.encode(), nread=1, timeout=10000)
        time.sleep(0.5)
        code = self._get_code(ans)
        if code != 'o':
            raise IOError(f'Wrong return code from driver, received {code}')

    @property
    def entry_slit_microns(self):
        """
        Reading of the ABSOLUTE position of the entrance slit in micrometres.
        """
        return self.entry_steps / self._slit_steps_micron

    def move_entry_slit_microns(self, microns: float):
        """
        ABSOLUTE positioning of the entry slit in micrometers.
        """
        pos_steps = microns * self._slit_steps_micron
        pos_steps = int(pos_steps)
        self.move_entry_slit_steps(pos_steps)

    def move_exit_slit_steps(self, nsteps: int):
        """
        ABSOLUTE positioning of the exit slit motor in number of steps.
        """
        ans = self.write_read(f'k0,2,{nsteps - self.exit_steps}\r'.encode(), nread=1, timeout=10000)
        time.sleep(0.5)
        code = self._get_code(ans)
        if code != 'o':
            raise IOError(f'Wrong return code from driver, received {code}')

    @property
    def exit_slit_microns(self):
        """
        Reading of the ABSOLUTE position of the exit slit in micrometres.
        """
        return self.exit_steps / self._slit_steps_micron

    def move_exit_slit_microns(self, microns: float):
        """
        ABSOLUTE positioning of the exit slit in micrometres.
        """
        pos_steps = microns * self._slit_steps_micron
        pos_steps = int(pos_steps)
        self.move_exit_slit_steps(pos_steps)

    def check_get_errors(self, error):
        print(error)
        pass

    def motor_stop(self):
        """
        Stopping of all the motors when this function is called.
        """
        ans = self.write_read(b'L')
        code = self._get_code(ans)
        if code != 'o':
            raise IOError(f'Wrong return code from driver, received {code}')

    motor_busy = Instrument.measurement("E\r", values={True: "oq", False: "oz"}, map_values=True)

    def motor_available(self):
        """
        This function verifies that the grating motor or the slit motors are free.
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
