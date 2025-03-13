from pymeasure.test import expected_protocol
from pymeasure.instruments.santec.tsl570 import TSL570


# Subclass TSL570 to override check_errors and avoid sending error queries.
class TSL570Test(TSL570):
    def check_errors(self):
        # Bypass error checking during tests.
        pass


# Patch the TSL570Test class methods to ignore only the 'check_instr_errors' keyword.
def _patched_write(self, command, **kwargs):
    kwargs.pop("check_instr_errors", None)
    return super(TSL570Test, self).write(command, **kwargs)


def _patched_ask(self, command, **kwargs):
    kwargs.pop("check_instr_errors", None)
    return super(TSL570Test, self).ask(command, **kwargs)


TSL570Test.write = _patched_write
TSL570Test.ask = _patched_ask

# With check_errors overridden, only the initialization command is expected.
init_sequence = [
    (b":SYSTem:COMMunicate:CODe 1", None),
]

# ========================= Optical Power Control Tests =========================


def test_output_enabled_setter():
    protocol = init_sequence + [(b":POWer:STATe 1", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.output_enabled = True


def test_output_enabled_getter():
    protocol = init_sequence + [(b":POWer:STATe?", b"1\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.output_enabled
        assert value is True


def test_power_unit_setter():
    protocol = init_sequence + [(b":POWer:UNIT 1", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.power_unit = "mW"


def test_power_unit_getter():
    protocol = init_sequence + [(b":POWer:UNIT?", b"0\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.power_unit
        assert value == "dBm"


def test_power_setpoint_setter():
    protocol = init_sequence + [(b":Power 5.000000e+00", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.power_setpoint = 5.0


def test_power_setpoint_getter():
    protocol = init_sequence + [(b":POWer?", b"5.000000e+00\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.power_setpoint
        assert abs(value - 5.0) < 1e-12


def test_power_reading():
    protocol = init_sequence + [(b":POWer:ACTual?", b"3.500000e+00\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.power_reading
        assert abs(value - 3.5) < 1e-12


# ========================= Wavelength Control Tests =========================


def test_wavelength_min():
    protocol = init_sequence + [(b":WAVelength:SWEep:RANGe:MINimum?", b"1.000000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength_min
        assert abs(value - 1e-06) < 1e-12


def test_wavelength_max():
    protocol = init_sequence + [(b":WAVelength:SWEep:RANGe:MAXimum?", b"2.000000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength_max
        assert abs(value - 2e-06) < 1e-12


def test_wavelength_setter():
    protocol = init_sequence + [(b":WAVelength 1.550000e-06", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.wavelength = 1.55e-06


def test_wavelength_getter():
    protocol = init_sequence + [(b":WAVelength?", b"1.550000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength
        assert abs(value - 1.55e-06) < 1e-12


def test_wavelength_start_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STARt 1.500000e-06", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.wavelength_start = 1.5e-06


def test_wavelength_start_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STARt?", b"1.500000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength_start
        assert abs(value - 1.5e-06) < 1e-12


def test_wavelength_stop_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STOP 1.600000e-06", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.wavelength_stop = 1.6e-06


def test_wavelength_stop_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STOP?", b"1.600000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength_stop
        assert abs(value - 1.6e-06) < 1e-12


def test_wavelength_step_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STEP 1.000000e-09", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.wavelength_step = 1e-09


def test_wavelength_step_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:STEP?", b"1.000000e-09\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength_step
        assert abs(value - 1e-09) < 1e-12


# ========================= Frequency Control Tests =========================


def test_frequency_min():
    protocol = init_sequence + [(b":FREQuency:SWEep:RANGe:MINimum?", b"1.000000e+14\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency_min
        assert abs(value - 1e14) < 1e-6


def test_frequency_max():
    protocol = init_sequence + [(b":FREQuency:SWEep:RANGe:MAXimum?", b"2.000000e+14\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency_max
        assert abs(value - 2e14) < 1e-6


def test_frequency_setter():
    protocol = init_sequence + [(b":FREQuency 2.000000e+14", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.frequency = 2e14


def test_frequency_getter():
    protocol = init_sequence + [(b":FREQuency?", b"2.000000e+14\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency
        assert abs(value - 2e14) < 1e-6


def test_frequency_start_setter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STARt 1.900000e+14", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.frequency_start = 1.9e14


def test_frequency_start_getter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STARt?", b"1.900000e+14\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency_start
        assert abs(value - 1.9e14) < 1e-6


def test_frequency_stop_setter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STOP 2.100000e+14", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.frequency_stop = 2.1e14


def test_frequency_stop_getter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STOP?", b"2.100000e+14\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency_stop
        assert abs(value - 2.1e14) < 1e-6


def test_frequency_step_setter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STEP 1.000000e+12", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.frequency_step = 1e12


def test_frequency_step_getter():
    protocol = init_sequence + [(b":FREQuency:SWEep:STEP?", b"1.000000e+12\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.frequency_step
        assert abs(value - 1e12) < 1e-6


# ========================= Sweep Settings Tests =========================


def test_start_sweep():
    protocol = init_sequence + [(b":WAVelength:SWEep 1", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        assert inst.start_sweep() is None


def test_start_repeat():
    protocol = init_sequence + [(b":WAVelength:SWEep:REPeat", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        assert inst.start_repeat() is None


def test_stop_sweep():
    protocol = init_sequence + [(b":WAVelength:SWEep 0", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        assert inst.stop_sweep() is None


def test_sweep_staus():
    protocol = init_sequence + [(b"WAVelength:SWEep?", b"0\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_staus
        assert value == "Stopped"


def test_sweep_mode_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:MODe 1", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_mode = "Continuous One-way"


def test_sweep_mode_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:MODe?", b"1\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_mode
        assert value == "Continuous One-way"


def test_sweep_pattern_setter():
    # Assume the initial sweep_mode is "Stepped Two-way" (mapped from 2).
    # Expect command to change sweep_mode to "Continuous Two-way" (mapped from 3).
    protocol = init_sequence + [
        (b":WAVelength:SWEep:MODe?", b"2\n"),
        (b":WAVelength:SWEep:MODe 3", None),
    ]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_pattern = "Continuous"


def test_sweep_pattern_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:MODe?", b"1\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        # Assuming the sweep_mode getter returns "Continuous One-way" (mapped from 1),
        # then sweep_pattern should be "Continuous".
        assert inst.sweep_pattern == "Continuous"


def test_sweep_routing_setter():
    # Assume the initial sweep_mode is "Stepped Two-way" (mapped from 2).
    # Expect command to change sweep_mode to "Stepped One-way" (mapped from 0).
    protocol = init_sequence + [
        (b":WAVelength:SWEep:MODe?", b"2\n"),
        (b":WAVelength:SWEep:MODe 0", None),
    ]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_routing = "One-way"


def test_sweep_routing_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:MODe?", b"1\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        # Assuming the sweep_mode getter returns "Continuous One-way" (mapped from 1),
        # then sweep_routing should be "Continuous".
        assert inst.sweep_routing == "One-way"


def test_sweep_speed_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:SPEed 10", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_speed = 10


def test_sweep_speed_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:SPEed?", b"10\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_speed
        assert value == 10


def test_sweep_dwell_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:DWELl 0.5", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_dwell = 0.5


def test_sweep_dwell_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:DWELl?", b"0.5\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_dwell
        assert abs(value - 0.5) < 1e-12


def test_sweep_delay_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:DELay 5", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_delay = 5


def test_sweep_delay_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:DELay?", b"1.0\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_delay
        assert abs(value - 1.0) < 1e-12


def test_sweep_cycles_setter():
    protocol = init_sequence + [(b":WAVelength:SWEep:CYCLes 5", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.sweep_cycles = 5


def test_sweep_cycles_getter():
    protocol = init_sequence + [(b":WAVelength:SWEep:CYCLes?", b"5\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_cycles
        assert value == 5


def test_sweep_count():
    protocol = init_sequence + [(b":WAVelength:SWEep:COUNt?", b"3\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.sweep_count
        assert value == 3
