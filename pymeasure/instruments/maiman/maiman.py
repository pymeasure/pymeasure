import serial, serial.tools.list_ports
import time

class maiman_laser_driver:
    VID = 4292
    PID = 60000
    def __init__(self, requested_SN, requested_com):

        _baudrate = 115200
        _parity = serial.PARITY_NONE
        _stopbits = serial.STOPBITS_ONE

        if requested_com == None:
            device_list = serial.tools.list_ports.comports()
            correct_ports = []
            for device in device_list:
                if device.vid == maiman_laser_driver.VID and device.pid == maiman_laser_driver.PID:
                    correct_ports.append(device.device)

            for port in correct_ports:
                self.ser = serial.Serial(port, baudrate=_baudrate, parity=_parity, stopbits=_stopbits)
                serial_number = self.read_serial_number()
                if serial_number == requested_SN:
                    print(port)
                    break
                else:
                    self.close_connection()
                

        elif requested_SN == None:
            self.ser = serial.Serial(requested_com, baudrate=_baudrate, parity=_parity, stopbits=_stopbits)

    def close_connection(self):
        self.ser.close()

    def set_current(self, current):
        if current >= self.get_max_current_limit():
            print('ERROR: desired current larger than HW limit')
            return
        current = current * 10
        current = hex(current).upper()
        current = current[2:]
        if len(current) == 1:
            current = '000' + current
        elif len(current) == 2:
            current = '00' + current 
        elif len(current) == 3:
            current = '0' + current
        #print(current)
        self.ser.write(("P0300 "+str(current)+"\r").encode())
        time.sleep(0.4)

    def get_max_current_limit(self):
        self.ser.write("J0308\r".encode())
        read_value = self.read()
        read_value = read_value.split()
        current = read_value[1]
        print(str(round(int(str(current),16) * .1,2))+'mA')
        return round(int(str(current),16) * .1,2)

    def get_current_value(self):
        self.ser.write("J0300\r".encode())
        read_value = self.read()
        read_value = read_value.split()
        current = read_value[1]
        print(str(int(str(current),16) * .1)+'mA')
        return int(str(current),16) * .1

    def set_TEC_temp(self, temp):
        temp = temp * 100
        temp = hex(temp).upper()
        temp = temp[2:]
        if len(temp) == 1:
            temp = '000' + temp
        elif len(temp) == 2:
            temp = '00' + temp 
        elif len(temp) == 3:
            temp = '0' + temp
        #print(temp)
        self.ser.write(("P0A10 "+str(temp)+"\r").encode())
        time.sleep(0.3)

    def get_TEC_temp(self):
        self.ser.write("J0A10\r".encode())
        time.sleep(0.3)
        read_value = self.read()
        read_value = read_value.split()
        current = read_value[1]
        print(str(int(str(current),16) * .01)+'C')
        return int(str(current),16) * .01
    
    def read(self):
        # result = ''
        line = ''
        while True:
            c = self.ser.read().decode('utf-8')
            if c == '\r':#chr(13):
                break
            line += c
        return line.strip()
    
    def get_driver_state(self):
        self.ser.write("J0700\r".encode())
        time.sleep(0.2)
        read_value = self.read()
        read_value = read_value.split()
        print(bin(int(read_value[1], 16)))

    def set_driver_off(self):
        self.ser.write("P0700 0010\r".encode())
        time.sleep(0.3)

    def set_driver_on(self):
        self.ser.write("P0700 0008\r".encode())
        time.sleep(0.3)

    def set_TEC_on(self):
        self.ser.write("P0A1A 0008\r".encode())
        time.sleep(0.3)

    def set_TEC_off(self):
        self.ser.write("P0A1A 0010\r".encode())
        time.sleep(0.3)

    def get_serial_number(self):
        self.ser.write("J0701\r".encode())
        read_value = self.read()
        read_value = read_value.split()
        serial_number = read_value[1]
        return serial_number

###########
# Example #
###########


# driver1 = maiman_laser_driver("1214",None) # connect to driver 
# driver = maiman_laser_driver('1214',None) # connect to driver, second argument can be a com port

# driver.get_max_current_limit() # return & prints current limit set by HW

# driver.set_TEC_on() 
# driver.set_TEC_temp(28) # in C
# driver.get_TEC_temp()

# driver.set_driver_on()
# time.sleep(0.2)
# driver.set_driver_on() 
# time.sleep(0.2)
# driver.set_current(750) # in mA; function checks if current exceed max set by HW, if yes, ERROR message --> to avoid HW restart
# time.sleep(0.2)
# driver.get_current_value()

# print(driver.get_serial_number())

# driver.close_connection()
