import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.keithley import KeithleyDMM6500


def test_init():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None)],
    ):
        pass  # Verify the expected communication.


def test_aperture_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:APER 0.0015', None)],
    ) as inst:
        inst.aperture = 0.0015


def test_aperture_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:APER?', b'0.0015\n')],
    ) as inst:
        assert inst.aperture == 0.0015


def test_autorange_enabled_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:RANG:AUTO 1', None)],
    ) as inst:
        inst.autorange_enabled = True


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:RANG:AUTO?', b'0\n')],
     False),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:RANG:AUTO?', b'1\n')],
     True),
))
def test_autorange_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.autorange_enabled == value


def test_autozero_enabled_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:AZER 0', None)],
    ) as inst:
        inst.autozero_enabled = False


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:AZER?', b'1\n')],
     True),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:AZER?', b'0\n')],
     False),
))
def test_autozero_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.autozero_enabled == value


def test_command_set_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'*LANG?', b'SCPI\n')],
    ) as inst:
        assert inst.command_set == 'SCPI'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':READ?', b'-4.999995E-01\n')],
     -0.4999995),
    ([(b'*LANG SCPI', None),
      (b':READ?', b'3.414127E-04\n')],
     0.0003414127),
))
def test_current_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.current == value


def test_current_ac_bandwidth_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:AC:DET:BAND?', b'30\n')],
    ) as inst:
        assert inst.current_ac_bandwidth == 30.0


def test_current_ac_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:CURR:AC:DIG?', b'6\n')],
    ) as inst:
        assert inst.current_ac_digits == 6


def test_current_ac_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:AC:RANG?', b'0.01\n')],
    ) as inst:
        assert inst.current_ac_range == 0.01


def test_current_ac_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:AC:REL?', b'0\n')],
    ) as inst:
        assert inst.current_ac_relative == 0.0


def test_current_ac_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:AC:REL:STAT?', b'0\n')],
    ) as inst:
        assert inst.current_ac_relative_enabled is False


def test_current_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:CURR:DIG?', b'3\n')],
    ) as inst:
        assert inst.current_digits == 3


def test_current_nplc_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:NPLC?', b'2\n')],
    ) as inst:
        assert inst.current_nplc == 2.0


def test_current_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:RANG?', b'0.01\n')],
    ) as inst:
        assert inst.current_range == 0.01


def test_current_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:REL?', b'0.5\n')],
    ) as inst:
        assert inst.current_relative == 0.5


def test_current_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:CURR:REL:STAT?', b'1\n')],
    ) as inst:
        assert inst.current_relative_enabled is True


def test_detector_bandwidth_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:AC\n'),
             (b'CURR:AC:DET:BAND 30', None)],
    ) as inst:
        inst.detector_bandwidth = 30


def test_detector_bandwidth_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:AC\n'),
             (b'CURR:AC:DET:BAND?', b'30\n')],
    ) as inst:
        assert inst.detector_bandwidth == 30.0


def test_digits_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b':DISP:CURR:DC:DIG 3', None)],
    ) as inst:
        inst.digits = 3


def test_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b':DISP:CURR:DC:DIG?', b'3\n')],
    ) as inst:
        assert inst.digits == 3


def test_frequency_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':READ?', b'0.000000E+00\n')],
    ) as inst:
        assert inst.frequency == 0.0


def test_frequency_aperature_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FREQ:APER?', b'0.2\n')],
    ) as inst:
        assert inst.frequency_aperature == 0.2


def test_frequency_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:FREQ:DIG?', b'6\n')],
    ) as inst:
        assert inst.frequency_digits == 6


def test_frequency_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FREQ:REL?', b'0\n')],
    ) as inst:
        assert inst.frequency_relative == 0.0


def test_frequency_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FREQ:REL:STAT?', b'0\n')],
    ) as inst:
        assert inst.frequency_relative_enabled is False


def test_frequency_threshold_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FREQ:THR:RANG?', b'10\n')],
    ) as inst:
        assert inst.frequency_threshold == 10.0


def test_frequency_threshold_auto_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FREQ:THR:RANG:AUTO?', b'1\n')],
    ) as inst:
        assert inst.frequency_threshold_auto_enabled is True


def test_id_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'*IDN?', b'KEITHLEY INSTRUMENTS,MODEL DMM6500,04592448,1.7.12b\n')],
    ) as inst:
        assert inst.id == 'KEITHLEY INSTRUMENTS,MODEL DMM6500,04592448,1.7.12b'


def test_line_frequency_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SYST:LFR?', b'60\n')],
    ) as inst:
        assert inst.line_frequency == 60.0


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "CURR:DC"', None)],
     'current'),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "CURR:AC"', None)],
     'current ac'),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "VOLT:DC"', None)],
     'voltage'),
))
def test_mode_setter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        inst.mode = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n')],
     'current'),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:AC\n')],
     'current ac'),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'VOLT:AC\n')],
     'voltage ac'),
))
def test_mode_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.mode == value


def test_nplc_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:NPLC 2', None)],
    ) as inst:
        inst.nplc = 2


def test_nplc_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:NPLC?', b'2\n')],
    ) as inst:
        assert inst.nplc == 2.0


def test_period_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':READ?', b'0.000000E+00\n')],
    ) as inst:
        assert inst.period == 0.0


def test_period_aperature_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:PER:APER?', b'0.2\n')],
    ) as inst:
        assert inst.period_aperature == 0.2


def test_period_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:PER:DIG?', b'6\n')],
    ) as inst:
        assert inst.period_digits == 6


def test_period_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:PER:REL?', b'0\n')],
    ) as inst:
        assert inst.period_relative == 0.0


def test_period_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:PER:REL:STAT?', b'0\n')],
    ) as inst:
        assert inst.period_relative_enabled is False


def test_period_threshold_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:PER:THR:RANG?', b'0.1\n')],
    ) as inst:
        assert inst.period_threshold == 0.1


def test_period_threshold_auto_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:PER:THR:RANG:AUTO?', b'1\n')],
    ) as inst:
        assert inst.period_threshold_auto_enabled is True


def test_range_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:RANG:AUTO 0;UPP 1.0', None)],
    ) as inst:
        inst.range = 1.0


def test_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:RANG?', b'1\n')],
    ) as inst:
        assert inst.range == 1.0


def test_relative_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:REL 0.5', None)],
    ) as inst:
        inst.relative = 0.5


def test_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:REL?', b'0.5\n')],
    ) as inst:
        assert inst.relative == 0.5


def test_relative_enabled_setter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC?', b'CURR:DC\n'),
             (b'CURR:DC:REL:STAT 1', None)],
    ) as inst:
        inst.relative_enabled = True


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:REL:STAT?', b'0\n')],
     False),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC?', b'CURR:DC\n'),
      (b'CURR:DC:REL:STAT?', b'1\n')],
     True),
))
def test_relative_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.relative_enabled == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':READ?', b'9.900000E+37\n')],
     9.9e+37),
    ([(b'*LANG SCPI', None),
      (b':READ?', b'9.900000E+37\n')],
     9.9e+37),
))
def test_resistance_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.resistance == value


def test_resistance_4W_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:FRES:DIG?', b'6\n')],
    ) as inst:
        assert inst.resistance_4W_digits == 6


def test_resistance_4W_nplc_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FRES:NPLC?', b'1\n')],
    ) as inst:
        assert inst.resistance_4W_nplc == 1.0


def test_resistance_4W_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FRES:RANG?', b'1E+07\n')],
    ) as inst:
        assert inst.resistance_4W_range == 10000000.0


def test_resistance_4W_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FRES:REL?', b'0\n')],
    ) as inst:
        assert inst.resistance_4W_relative == 0.0


def test_resistance_4W_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FRES:REL:STAT?', b'0\n')],
    ) as inst:
        assert inst.resistance_4W_relative_enabled is False


def test_resistance_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:RES:DIG?', b'6\n')],
    ) as inst:
        assert inst.resistance_digits == 6


def test_resistance_nplc_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:RES:NPLC?', b'1\n')],
    ) as inst:
        assert inst.resistance_nplc == 1.0


def test_resistance_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:RES:RANG?', b'1E+07\n')],
    ) as inst:
        assert inst.resistance_range == 10000000.0


def test_resistance_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:RES:REL?', b'0\n')],
    ) as inst:
        assert inst.resistance_relative == 0.0


def test_resistance_relative_enabled_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:RES:REL:STAT?', b'0\n')],
    ) as inst:
        assert inst.resistance_relative_enabled is False


def test_system_time_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SYST:TIME? 1', b'Thu Sep 21 09:06:41 2023\n')],
    ) as inst:
        assert inst.system_time == 'Thu Sep 21 09:06:41 2023'


def test_terminals_used_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'ROUT:TERM?', b'REAR\n')],
    ) as inst:
        assert inst.terminals_used == 'REAR'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':READ?', b'1.200272E-03\n')],
     0.001200272),
    ([(b'*LANG SCPI', None),
      (b':READ?', b'5.943143E-04\n')],
     0.0005943143),
))
def test_voltage_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.voltage == value


def test_voltage_ac_bandwidth_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:AC:DET:BAND?', b'3\n')],
    ) as inst:
        assert inst.voltage_ac_bandwidth == 3.0


def test_voltage_ac_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:VOLT:AC:DIG?', b'6\n')],
    ) as inst:
        assert inst.voltage_ac_digits == 6


def test_voltage_ac_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:AC:RANG?', b'1\n')],
    ) as inst:
        assert inst.voltage_ac_range == 1.0


def test_voltage_ac_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:AC:REL?', b'0\n')],
    ) as inst:
        assert inst.voltage_ac_relative == 0.0


def test_voltage_digits_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:VOLT:DIG?', b'6\n')],
    ) as inst:
        assert inst.voltage_digits == 6


def test_voltage_nplc_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:NPLC?', b'1\n')],
    ) as inst:
        assert inst.voltage_nplc == 1.0


def test_voltage_range_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:RANG?', b'1\n')],
    ) as inst:
        assert inst.voltage_range == 1.0


def test_voltage_relative_getter():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:VOLT:REL?', b'0\n')],
    ) as inst:
        assert inst.voltage_relative == 0.0


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:VOLT:REL:STAT?', b'0\n')],
     False),
    ([(b'*LANG SCPI', None),
      (b':SENS:VOLT:REL:STAT?', b'0\n')],
     False),
))
def test_voltage_relative_enabled_getter(comm_pairs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.voltage_relative_enabled == value


def test_check_errors():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'SYST:ERR?', b'0,"No error;0;0 0"\n')],
    ) as inst:
        assert inst.check_errors() == []


def test_clear():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'*CLS', None)],
    ) as inst:
        assert inst.clear() is None


def test_displayed_text():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':DISP:CLE', None),
             (b':DISP:SCR SWIPE_USER', None),
             (b':DISP:USER1:TEXT "Hello"', None),
             (b':DISP:USER2:TEXT "DMM6500"', None)],
    ) as inst:
        assert inst.displayed_text(*('Hello', 'DMM6500'), ) is None


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "CURR:DC"', None),
      (b':SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG 0.01', None)],
     (), {}, None),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "CURR:AC"', None),
      (b':SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG 0.01', None)],
     (), {'ac': True}, None),
))
def test_measure_current(comm_pairs, args, kwargs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.measure_current(*args, **kwargs) == value


def test_measure_frequency():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC "FREQ:VOLT"', None)],
    ) as inst:
        assert inst.measure_frequency() is None


def test_measure_period():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b':SENS:FUNC "PER:VOLT"', None)],
    ) as inst:
        assert inst.measure_period() is None


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "RES"', None),
      (b':SENS:RES:RANG:AUTO 0;:SENS:RES:RANG 1e+07', None)],
     (), {}, None),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "FRES"', None),
      (b':SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG 1e+07', None)],
     (), {'wires': 4}, None),
))
def test_measure_resistance(comm_pairs, args, kwargs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.measure_resistance(*args, **kwargs) == value


@pytest.mark.parametrize("comm_pairs, args, kwargs, value", (
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "VOLT:DC"', None),
      (b':SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG 1', None)],
     (), {}, None),
    ([(b'*LANG SCPI', None),
      (b':SENS:FUNC "VOLT:AC"', None),
      (b':SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:AC:RANG 1', None)],
     (), {'ac': True}, None),
))
def test_measure_voltage(comm_pairs, args, kwargs, value):
    with expected_protocol(
            KeithleyDMM6500,
            comm_pairs,
    ) as inst:
        assert inst.measure_voltage(*args, **kwargs) == value


def test_reset():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'*RST', None)],
    ) as inst:
        assert inst.reset() is None


def test_trigger_single_autozero():
    with expected_protocol(
            KeithleyDMM6500,
            [(b'*LANG SCPI', None),
             (b'AZER:ONCE', None)],
    ) as inst:
        assert inst.trigger_single_autozero() is None
