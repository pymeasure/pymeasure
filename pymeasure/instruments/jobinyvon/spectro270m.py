

if __name__ == '__main__':
    import serial

    ser = serial.Serial('COM1', 9600, timeout=0.300, parity=serial.PARITY_NONE,
                        bytesize=8, stopbits=1, xonxoff=0,
                        rtscts=0, dsrdtr=1)

    ser.write(b' ')
    print(ser.readall())
    ser.write(b'H0\r')
    print(ser.readall())
    ser.close()

 #control("H0\r", f"G0,{-1000}\r"