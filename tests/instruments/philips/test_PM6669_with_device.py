import pytest

from pymeasure.instruments.philips.PM6669 import PM6669, Functions

FUNCTION_STRINGS = [
    ("FREQ A", Functions.FREQUENCY_A),
    ("PER A", Functions.PER_A),
    ("FREQ B", Functions.FREQUENCY_B),
    ("TOTM A", Functions.TOT_A),
    ("WIDTH A", Functions.WIDTH_A),
]


@pytest.fixture(scope="module")
def philips_pm6669(connected_device_address):
    instr = PM6669(connected_device_address)
    instr.reset_to_defaults()
    return instr


@pytest.mark.parametrize("case, expected", FUNCTION_STRINGS)
def test_function_modes(philips_pm6669, case, expected):
    philips_pm6669.measuring_function = case
    assert philips_pm6669.measuring_function == expected


@pytest.mark.parametrize("case", [0, 0.1, 10, 25.5])
def test_timeout_times(philips_pm6669, case):
    philips_pm6669.measurement_timeout = case
    assert philips_pm6669.measurement_timeout == case


@pytest.mark.parametrize("case", [0.2, 1, 10])
def test_measurement_times(philips_pm6669, case):
    philips_pm6669.measurement_time = case
    assert philips_pm6669.measurement_time == case


@pytest.mark.parametrize("case", [True, False])
def test_freerun(philips_pm6669, case):
    philips_pm6669.freerun_enabled = case
    assert philips_pm6669.freerun_enabled == case
