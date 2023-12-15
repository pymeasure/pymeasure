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
    """This function allows to read input and transform it into integer format."""
    numeric_string = ''.join(char for char in string if char.isdigit())
    return int(numeric_string)

class JY270M(Instrument):
    """This is a class for the 270M JY spectrometer."""

    """Backlash in number of motor steps"""
    backlash = 320
    _steps_nm = 32
    _lambda_max = 1171.68
    _max_steps = 37494

    def __init__(self, adapter, name = "JY270M", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

    def _write_read(self, command: bytes):
        self.write_bytes(command)
        read = b''
        for ind in range(10000):
            try:
                read += spectro.read_bytes(1)
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


    def check_get_errors(self, error):
        print(error)
        pass

    def motor_init(self):
        "This command is used to initialize the monochromator, only needs to be called once",
        self._write_read(b'A')
    #
    # grating_steps = Instrument.control('H0\r',
    #                                    'G0,%d\r',
    #                                    """Control the grating motor number of steps""",
    #                                    validator=strict_range,
    #                                    values=[0, 37494],
    #                                    get_process=read_int,
    #                                    )

    @property
    def grating_steps(self):
        return read_int(self._write_read(b'H0\r').decode())

    @grating_steps.setter
    def grating_steps(self, nsteps: int):
        """Absolut positioning"""
        ans = self._write_read(f'F0,{nsteps - self.grating_steps}\r'.encode())
        code = self._get_code(ans)
        assert code == 'o'

    @property
    def grating_wavelength(self):
        return self._lambda_max - (self._max_steps - self.grating_steps) / self._steps_nm

    @grating_wavelength.setter
    def grating_wavelength(self, wavelength: float):
        """Absolut positioning"""
        steps = int(self._max_steps - int((self._lambda_max - wavelength) * self._steps_nm))
        self.grating_steps = steps

    motor_busy_check= Instrument.measurement(
        "E\r".encode('utf-8'),
        """it asks the motor if it's busy. If we receive "oq" it's busy and "oz" if it's not """,
    )

    motor_position = Instrument.measurement(
        b'H0\r',
        """This property asks the instrument for its current position.""",
    )



    def read_int(self):
        """This function allows to read input and transform it into integer format."""
        answer = self.adapter.readall()
        numeric_string = ''.join(char for char in answer.decode('utf-8') if char.isdigit())
        return int(numeric_string)


    def motor_busy_check(self):
        Instrument.write(self, b'E\r')
        ans = self.adapter.readall()
        char = ans.decode('utf-8')
        if char == "oz":
            return True
        if char == "oq":
            return False


    def motor_move_relative(self, motor_steps: int):
        """we check if the motor is busy before sending the movement command."""
        code = self._get_code(self._write_read(f'F0,{motor_steps}\r'))
        assert code == 'o'

    def motor_control(self, lamda):
        """32 motor steps / nm"""
        steps_nm = 32
        Instrument.write(self, b'H0\r')
        position = self.read_int()
        """Wavelength is transformed into motor steps."""
        motor_final_step = lamda*steps_nm
        time.sleep(1)
        while abs(motor_final_step - position) > 1:
            self.motor_move_relative(motor_final_step-position)
            Instrument.write(self, b'H0\r')
            position = self.read_int()
        print("The final motor position is: " + str(position))
        print("The final wavelength is: " + str(position/32))


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

    # autobaud_status = spectro.auto_baud()
    # if autobaud_status:
    #     spectro.motor_init()

    spectro.grating_steps
    """spectro.write(b'H0\r')
    print(spectro.read_int())"""

    #spectro.motor_control(900.5)

    """spectro.write(b'A')"""

    """spectro.motor_move_relative(-10000)"""
    """c
    spectro=JY270M(adapter=ser)
        
    ontrol("H0\r", f"G0,{-1000}\r"""
