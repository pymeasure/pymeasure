import visa
rm = visa.ResourceManager()
print(rm.list_resources())

inst = rm.open_resource('USB0::0x1698::0x0837::007000000446::0::INSTR')
print(inst.query("*IDN?"))

inst = rm.open_resource('TCPIP0::146.136.35.247::inst0::INSTR')
print(inst.query("*IDN?"))

inst = rm.open_resource('TCPIP0::146.136.35.210::inst0::INSTR')
print(inst.query("*IDN?"))
