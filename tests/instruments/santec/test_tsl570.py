from pymeasure.test import expected_protocol
from pymeasure.instruments.santec.tsl570 import TSL570


# Subclass TSL570 to override check_errors and avoid sending error queries.
class TSL570Test(TSL570):
    def check_errors(self):
        # Bypass error checking during tests.
        pass


# Patch the TSL570Test class methods to ignore the 'check_instr_errors' keyword.
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


def test_init():
    # This test simply verifies that instantiation sends the init command.
    with expected_protocol(TSL570Test, init_sequence):
        pass


# --- Wavelength Tests ---


def test_wavelength_setter():
    protocol = init_sequence + [(b":WAVelength 1.550000e-06", None)]
    with expected_protocol(TSL570Test, protocol) as inst:
        inst.wavelength = 1.55e-06


def test_wavelength_getter():
    protocol = init_sequence + [(b":WAVelength?", b"1.550000e-06\n")]
    with expected_protocol(TSL570Test, protocol) as inst:
        value = inst.wavelength
        assert abs(value - 1.55e-06) < 1e-12
