from pymeasure.generator import Generator
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear
from pint import Quantity as Q_
import time

generator = Generator()
adapter_string = 'ASRL3::INSTR'
inst = generator.instantiate(
    SmarActSCULinear,
    adapter_string,
    'SCUController',
    adapter_kwargs={'read_termination': '\n', 'write_termination': '\n'}
)

""" Test properties (Setter then Getter)"""
inst.amplitude = Q_(500, 'dV')
assert inst.amplitude == 500


inst = Q_(800, 'Hz')
assert inst.frequency == Q_(800, 'Hz')

inst.baudrate = 9600
assert inst.baudrate == 9600
# Identification
idn = inst.id
assert idn is not None

ch0 = inst.channel0
pos_type = inst.get_positioner_type()

ch0.move_steps_up(steps=100, freq=Q_(1000, 'Hz'), ampl=Q_(500, 'dV'))
time.sleep(0.5)

ch0.move_steps_down(steps=100, freq=Q_(1000, 'Hz'), ampl=Q_(500, 'dV'))
time.sleep(0.5)



is_present = inst.check_sensor_present()
assert is_present is True

# Calibrage et zérotage
inst.calibrate_sensor()
time.sleep(3.0)

inst.move_to_ref()
time.sleep(2.0)

inst.set_zero_pos()
time.sleep(0.5)

# Limites mécaniques et arrêt brutal
inst.move_to_end_up()
time.sleep(1.0)
inst.stop()
time.sleep(0.5)

inst.move_to_end_down()
time.sleep(1.0)
inst.stop()
time.sleep(0.5)

# ==========================================
# TESTS DES CANAUX (CLOSED LOOP)
# ==========================================
ch = inst.channel0

ch.move_abs(Q_(100, 'um'))
time.sleep(1.0)
pos_abs = ch.get_position()
# Le générateur enregistrera la valeur lue et la mettra dans le test

ch.move_rel(Q_(50, 'um'))
time.sleep(1.0)
pos_rel = ch.get_position()


"""Testing Channel commands"""
ch0 = inst.channel0
ch0.move_abs(Q_(100, 'um'))
assert ch0.get_position()==Q_(100, 'um')



# 4. Save the recording!
# This creates the file with all the expected_protocol tests.
generator.write_file("generated_test_smaract.py")
print("Done! Open 'generated_test_smaract.py' to see the magic.")