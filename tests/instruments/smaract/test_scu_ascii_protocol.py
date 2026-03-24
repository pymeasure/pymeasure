from pymeasure.generator import Generator
from pymeasure.instruments.smaract.scu_ascii import SmarActSCULinear
from pint import Quantity as Q_

# Create generator
gen = Generator()

# Instantiate instrument THROUGH generator
inst = gen.instantiate(
    SmarActSCULinear,
    "ASRL3::INSTR",   # your device address
    "smaract",
    adapter_kwargs={"baud_rate": 9600}
)

# -----------------------
# Instrument-level tests
# -----------------------
inst.model
inst.serial_nb

# -----------------------
# Channel-level tests
# -----------------------
ch = inst.channel0

# Configuration
ch.frequency_max = Q_(500, "Hz")
ch.frequency_max

ch.safe_direction = "up"
ch.safe_direction

ch.safe_direction = "down"
ch.safe_direction

# Position / status
ch.get_position()
ch.get_positioner_type()

# Motion commands
ch.move_abs(Q_(100, "um"))
ch.move_rel(Q_(50, "um"))

ch.move_steps_up(100)
ch.move_steps_down(100)

ch.move_to_ref()
ch.move_to_end_up()
ch.move_to_end_down()

ch.stop()

# Calibration / sensor
ch.check_sensor_present()
ch.calibrate_sensor()

# -----------------------
# Write test file
# -----------------------
gen.write_file("generated_scu_protocol_tests.py")