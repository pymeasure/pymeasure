from pymeasure.generator import Generator
from pymeasure.instruments.jobinyvon.spectro270m import JY270M
from pyvisa.constants import ControlFlow, Parity, StopBits
import time


generator = Generator()

inst = generator.instantiate(JY270M, 'COM1', 'jobinyvon.spectro270m', adapter_kwargs=dict(baud_rate=9600,
                                                                              timeout=300,
                                                                              parity=Parity.none,
                                                                              data_bits=8,
                                                                              stop_bits=StopBits.one,
                                                                              flow_control=ControlFlow.dtr_dsr,
                                                                              write_termination='',
                                                                              read_termination=''))


inst.auto_baud()
time.sleep(6)
ans = inst.write_read(b' ')
assert ans.decode() == 'F'
inst.motor_init()
time.sleep(30)
assert inst.gsteps == 37494
assert inst.entrysteps == 0
assert inst.exitsteps == 0

inst.move_grating_steps(0)
time.sleep(1)
inst.motor_stop()
time.sleep(1)
assert inst.gsteps > 0

inst.move_grating_steps(20000)
time.sleep(5)
assert inst.gsteps == 20000

inst.gsteps = -1000
time.sleep(3)
assert inst.gsteps == 19000

inst.move_grating_wavelength(650)
time.sleep(5)
assert abs(inst.get_grating_wavelength() - 650) <= 0.03125

inst.move_entry_slit_steps(50)
time.sleep(2)
assert inst.entrysteps == 50

"""
We check that the aperture of the entry slit in microns for an aperture of 50 steps is equal to 317.50063500127
"""
assert inst.get_entry_slit_microns() == 317.50063500127

inst.entrysteps = -50
time.sleep(2)
assert inst.entrysteps == 0

inst.move_entry_slit_microns(100)
assert abs(inst.get_entry_slit_microns() - 100.0) <= 6.3500128

inst.move_exit_slit_steps(50)
time.sleep(2)
assert inst.exitsteps == 50

"""
We check that the aperture of the entry slit in microns for an aperture of 50 steps is equal to 317.50063500127
"""
assert inst.get_exit_slit_microns() == 317.50063500127

inst.exitsteps = -50
time.sleep(2)
assert inst.exitsteps == 0

inst.move_exit_slit_microns(100)
assert abs(inst.get_exit_slit_microns() - 100.0) <= 6.3500128

assert inst.motor_busy_check() == False

generator.write_file(filename='test_jobinyvon_270M.py')