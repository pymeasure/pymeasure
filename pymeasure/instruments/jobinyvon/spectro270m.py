from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range

import time
import serial

if __name__ == '__main__':
    ser = serial.Serial('COM1', 9600, timeout=0.300, parity=serial.PARITY_NONE,
        bytesize=8, stopbits=1, xonxoff=0,
        rtscts=0, dsrdtr=1)


class JY270M(Instrument):
    """This is a class for the 270M JY spectrometer."""

    def __init__(self, adapter, name = "JY270M", **kwargs):(
        super().__init__(
            adapter,
            name,
            **kwargs)
    )

    motor_init = Instrument.setting(
        b'A',
        """This command is used to initialize the monochromator, only needs to be called once""",
    )

    """Backlash in number of motor steps"""
    backlash = 320

    """32 motor steps / nm"""
    steps_nm = 32


    def write(self, command):
        """This function allows for easier writing of the write command."""
        Instrument.write(self, command)

    def read_int(self):
        """This function allows to read input and transform it into integer format."""
        answer = self.adapter.readall()
        numeric_string = ''.join(char for char in answer.decode('utf-8') if char.isdigit())
        return int(numeric_string)

    def m_init(self):
        Instrument.write(self, b'A')

    def motor_busy_check(self):
        self.write(b'E')
        ans = self.adapter.readall()
        char = ans.decode('utf-8')
        if char == "oz":
            return True
        if char == "oq":
            return False



    def auto_baud(self):
        """This function allows for setting up the JY270M before measuring."""
        ser.write(b' ')
        rep = ser.readall()
        if len(rep) == 0:
            while len(rep) == 0:
                ser.write(b' ')
                time.sleep(0.5)
                rep = ser.readall()
        while chr(rep[0]) != 'F':
            if chr(rep[0]) == "*":
                ser.write(bytes([0xF7]))
                ser.write(b' ')
                rep = ser.readall()
            elif chr(rep[0]) == "B":
                ser.write(b'O2000\0')
                time.sleep(0.5)
                ser.write(b' ')
                rep = ser.readall()
            elif rep[0] == 27:
                ser.write(bytes([0xF8]))
                time.sleep(0.5)
                ser.write(b' ')
                rep = ser.readall()
                if chr(rep[0]) != "F":
                    ser.write(bytes([0xF8]))
                    ser.write(bytes([0xDE]))
                    time.sleep(0.5)
                    ser.write(b' ')
                    rep = ser.readall()
            else:
                ser.write(b' ')
                time.sleep(0.5)
                rep = ser.readall()


    def motor_control(self, lamda):
        self.write(b'H0\r')
        position = self.adapter.read_all()
        """Wavelength is transformed into motor steps."""
        motor_step = lamda*steps_nm
        while motor_step != position:
            if self.motor_busy_check():
                if motor_step > position:
                    s = ("%s%f\r'", "b'F0,", motor_step - position)
                    print(s)
                    ser.write(s)

                if motor_step < position:
                    s = ("%s%f\r'", "b'F0,", position - motor_step)
                    ser.write(s)
                    print(s)
            else:
                time.sleep(1)


spectro=JY270M(adapter=ser)

spectro.motor_control(20000)

"""control("H0\r", f"G0,{-1000}\r"""