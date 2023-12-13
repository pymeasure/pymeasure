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

    """Backlash in number of motor steps"""
    backlash = 320


    motor_init = Instrument.setting(
        b'A',
        """This command is used to initialize the monochromator, only needs to be called once""",
    )

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

    def m_init(self):
        Instrument.write(self, b'A')

    def motor_busy_check(self):
        Instrument.write(self, b'E\r')
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
                print(1)
        while chr(rep[0]) != 'F':
            if chr(rep[0]) == "*":
                ser.write(bytes([0xF7]))
                print(2)
                ser.write(b' ')
                rep = ser.readall()
            elif chr(rep[0]) == "B":
                ser.write(b'O2000\0')
                print(3)
                time.sleep(0.5)
                ser.write(b' ')
                rep = ser.readall()
            elif rep[0] == 27:
                ser.write(bytes([0xF8]))
                print(4)
                time.sleep(0.5)
                ser.write(b' ')
                rep = ser.readall()
                if chr(rep[0]) != "F":
                    ser.write(bytes([0xF8]))
                    ser.write(bytes([0xDE]))
                    print(5)
                    time.sleep(0.5)
                    ser.write(b' ')
                    rep = ser.readall()
            else:
                ser.write(b' ')
                time.sleep(0.5)
                rep = ser.readall()

    def motor_move_relative(self, motor_step):
        """we check if the motor is busy before sending the movement command."""
        while not self.motor_busy_check():
            pass
        command = "F0," + str(motor_step) + "\r"
        Instrument.write(self, command.encode('utf-8'))
        while not self.motor_busy_check():
            pass

    def readall(self):
        ser.readall()

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

spectro=JY270M(adapter=ser)

"""spectro.write(b'H0\r')
print(spectro.read_int())"""

spectro.motor_control(900.5)

"""spectro.write(b'A')"""

"""spectro.motor_move_relative(-10000)"""
"""control("H0\r", f"G0,{-1000}\r"""
