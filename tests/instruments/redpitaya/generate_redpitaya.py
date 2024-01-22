import datetime
import time

from pymeasure.generator import Generator
from pymeasure.instruments.redpitaya import RedPitayaScpi

ip_address = '169.254.134.87'
port = 5000

generator = Generator()
inst: RedPitayaScpi = generator.instantiate(RedPitayaScpi, f"TCPIP::{ip_address}::{port}::SOCKET", 'redpitaya',
                             adapter_kwargs=dict(read_termination='\r\n',
                                                 write_termination='\r\n',
                                                 ))


inst.time = datetime.time(13, 7, 20)
assert inst.time.hour == 13
assert inst.time.minute == 7

inst.date = datetime.date(2023, 12, 22)
assert inst.date == datetime.date(2023, 12, 22)

inst.board_name

inst.digital_reset()

for ind in range(8):
    inst.led[ind].enabled = True
    assert inst.led[ind].enabled

    inst.led[ind].enabled = False
    assert not inst.led[ind].enabled

for ind in range(7):
    inst.dioN[ind].direction_in = True
    assert inst.dioN[ind].direction_in
    inst.dioN[ind].direction_in = False
    assert not inst.dioN[ind].direction_in

    inst.dioN[ind].enabled = True
    assert inst.dioN[ind].enabled

    inst.dioN[ind].enabled = False
    assert not inst.dioN[ind].enabled

for ind in range(7):
    inst.dioN[ind].direction_in = True
    assert inst.dioN[ind].direction_in
    inst.dioN[ind].direction_in = False
    assert not inst.dioN[ind].direction_in

    inst.dioP[ind].enabled = True
    assert inst.dioP[ind].enabled

    inst.dioP[ind].enabled = False
    assert not inst.dioP[ind].enabled

inst.analog_reset()

for ind in range(4):
    inst.analog_in_slow[ind].voltage
    inst.analog_out_slow[ind].voltage = 0.5

for ind in range(17):
    inst.decimation = 2**ind
    assert inst.decimation == 2**ind

assert inst.average_skipped_samples is False
inst.average_skipped_samples = True
assert inst.average_skipped_samples

assert inst.acq_units == 'VOLTS'
inst.acq_units = 'RAW'
assert inst.acq_units == 'RAW'

assert inst.acq_size == 16384

assert inst.acq_format == 'ASCII'
inst.acq_format = 'BIN'
assert inst.acq_format == 'BIN'


generator.write_file('test_redpitaya.py')