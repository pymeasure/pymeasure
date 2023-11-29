import time
import serial


if __name__ == '__main__':

    ser = serial.Serial('COM1', 9600, timeout=0.300, parity=serial.PARITY_NONE,
                        bytesize=8, stopbits=1, xonxoff=0,
                        rtscts=0, dsrdtr=1)


    """This function puts the 270M into intelligent mode."""
    def auto_baud():
        ser.write(b' ')
        rep = ser.readall()
        if len(rep) == 0:
            while len(rep) == 0:
                ser.write(b' ')
                time.sleep(0.5)
                rep = ser.readall()
                #print(rep)

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
                #print(chr(rep[0]))
            elif rep[0] == 27:
                ser.write(bytes([0xF8]))
                time.sleep(0.5)
                ser.write(b' ')
                rep = ser.readall()

                """Passage à l'étape 7"""
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
                #print(rep[0])
        ser.write(b'A')

    def motor_control(lamda):
        """backlash in number of motor steps"""
        backlash = 320
        """32 motor steps / nm"""
        ser.write(b'H0\r')
        rep = ser.readall()
        position = int(rep.decode('utf-8')[1:])
        """conversion de la longueur d'onde en pas moteur"""
        motor_step = lamda*32

        ser.write(b'E')
        response = ser.readall()
        if response == "oz":
            if motor_step > position:
                s = ("%s%f\r'", "b'F0,", motor_step-position)
                print(s)
                ser.write(s)

            if motor_step < position:
                s = ("%s%f\r'", "b'F0,", position-motor_step)
                ser.write(s)
                print(s)
        else:
            time.sleep(2)


    #auto_baud()
motor_control(800)


"""control("H0\r", f"G0,{-1000}\r"""