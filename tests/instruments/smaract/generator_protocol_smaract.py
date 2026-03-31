from pymeasure.generator import Generator
from pymeasure.instruments.smaract import scu_ascii
from pint import Quantity as Q_

# Create generator
gen = Generator()

# Instantiate instrument THROUGH generator
inst = gen.instantiate(
    scu_ascii.SmarActSCULinear,
    "ASRL3::INSTR",
    "smaract",
    adapter_kwargs={
        "baud_rate": 9600,
        "read_termination": "\n",
        "write_termination": "\n",
        "timeout": 3000,
    }
)
#used for simplicity reasons
ch = inst.channel0

# Instrument-level tests

inst.model
inst.serial_nb

inst.set_baudrate(9600)

ch.check_sensor_present
ch.calibrate_sensor

ch.set_zero_pos

# Channel-level tests

# Configuration
inst.frequency = Q_(500, "Hz")
inst.frequency

ch.frequency_max = Q_(500, "Hz")
ch.frequency_max

inst.amplitude = Q_(100, "um")
inst.amplitude

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

# Write test file

gen.write_file("V3_generated_scu_protocol_tests.py")