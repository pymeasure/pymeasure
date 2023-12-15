import serial


if __name__ == '__main__':
    try:
        ser = serial.Serial('COM1', 9600, timeout=0.300, parity=serial.PARITY_NONE,
        bytesize=8, stopbits=1, xonxoff=0,
        rtscts=0, dsrdtr=1)
        pass
    except:
        pass
    finally:
        ser.close()