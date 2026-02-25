import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.easttester import ET3510

#
# WARNING! This file was generated automatically apart from the imports below. DO NOT EDIT!
# See et3510 fixture in tests/instruments/easttester/test_et3510_with_device.py for generation code
#
from pymeasure.instruments.easttester.et35xx import (
    BiasSource, MeasurementRange, MeasurementSpeed, MeasurementType, TriggerSource
)


def test_init():
    with expected_protocol(
            ET3510,
            [],
            timeout=5000,
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'AMPL:ALC ON', None)],
     True),
    ([(b'AMPL:ALC OFF', None)],
     False),
))
def test_automatic_level_control_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.automatic_level_control = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'AMPL:ALC?', b'ON\n')],
     True),
    ([(b'AMPL:ALC?', b'OFF\n')],
     False),
))
def test_automatic_level_control_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.automatic_level_control == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SYST:BEEP:STAT OFF', None)],
     False),
    ([(b'SYST:BEEP:STAT ON', None)],
     True),
))
def test_beeper_enabled_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.beeper_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SYST:BEEP:STAT?', b'OFF\n')],
     False),
    ([(b'SYST:BEEP:STAT?', b'ON\n')],
     True),
))
def test_beeper_enabled_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.beeper_enabled == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'BIAS:STAT 2', None)],
     BiasSource.EXTERNAL),
    ([(b'BIAS:STAT 1', None)],
     BiasSource.INTERNAL),
))
def test_bias_source_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.bias_source = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'BIAS:STAT?', b'2\n')],
     BiasSource.EXTERNAL),
    ([(b'BIAS:STAT?', b'1\n')],
     BiasSource.INTERNAL),
))
def test_bias_source_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.bias_source == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'BIAS:VOLT:LEV -2.000000', None)],
     -2),
    ([(b'BIAS:VOLT:LEV 2.000000', None)],
     2),
    ([(b'BIAS:VOLT:LEV 1.500000', None)],
     1.5),
    ([(b'BIAS:VOLT:LEV -1.000000', None)],
     -1),
    ([(b'BIAS:VOLT:LEV 0.000000', None)],
     0),
))
def test_bias_voltage_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.bias_voltage = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'BIAS:VOLT:LEV?', b'-2.000000e+00\n')],
     -2.0),
    ([(b'BIAS:VOLT:LEV?', b'2.000000e+00\n')],
     2.0),
    ([(b'BIAS:VOLT:LEV?', b'1.500000e+00\n')],
     1.5),
    ([(b'BIAS:VOLT:LEV?', b'-1.000000e+00\n')],
     -1.0),
    ([(b'BIAS:VOLT:LEV?', b'0.000000e+00\n')],
     0.0),
))
def test_bias_voltage_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.bias_voltage == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FREQ 10.000000', None)],
     10),
    ([(b'FREQ 100.000000', None)],
     100),
    ([(b'FREQ 203.250000', None)],
     203.25),
    ([(b'FREQ 1000000.000000', None)],
     1000000),
    ([(b'FREQ 5000.000000', None)],
     5000),
))
def test_frequency_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.frequency = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FREQ?', b'1.000000e+01\n')],
     10.0),
    ([(b'FREQ?', b'1.000000e+02\n')],
     100.0),
    ([(b'FREQ?', b'2.032500e+02\n')],
     203.25),
    ([(b'FREQ?', b'1.000000e+06\n')],
     1000000.0),
    ([(b'FREQ?', b'5.000000e+03\n')],
     5000.0),
))
def test_frequency_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.frequency == value


def test_id_getter():
    with expected_protocol(
            ET3510,
            [(b'*IDN?', b'ZC,ET3510,08832428001,V2.00.2129.001\n')],
            timeout=5000,
    ) as inst:
        assert inst.id == 'ZC,ET3510,08832428001,V2.00.2129.001'


def test_impedance_getter():
    with expected_protocol(
            ET3510,
            [(b'FETC:IMP:FORM?', b'3.818719e-08,2.159702e+00\n')],
            timeout=5000,
    ) as inst:
        assert inst.impedance == [3.818719e-08, 2.159702]


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SYST:KLOC ON', None)],
     True),
    ([(b'SYST:KLOC OFF', None)],
     False),
))
def test_keypad_lock_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.keypad_lock = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'SYST:KLOC?', b'ON\n')],
     True),
    ([(b'SYST:KLOC?', b'OFF\n')],
     False),
))
def test_keypad_lock_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.keypad_lock == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:RANG:AUTO ON', None)],
     True),
    ([(b'FUNC:IMP:RANG:AUTO OFF', None)],
     False),
))
def test_measurement_auto_range_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.measurement_auto_range = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:RANG:AUTO?', b'ON\n')],
     True),
    ([(b'FUNC:IMP:RANG:AUTO?', b'OFF\n')],
     False),
))
def test_measurement_auto_range_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.measurement_auto_range == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:RANG 30', None)],
     MeasurementRange.RANGE_30),
    ([(b'FUNC:IMP:RANG 100', None)],
     MeasurementRange.RANGE_100),
    ([(b'FUNC:IMP:RANG 300', None)],
     MeasurementRange.RANGE_300),
    ([(b'FUNC:IMP:RANG 1000', None)],
     MeasurementRange.RANGE_1k),
    ([(b'FUNC:IMP:RANG 3000', None)],
     MeasurementRange.RANGE_3k),
    ([(b'FUNC:IMP:RANG 30000', None)],
     MeasurementRange.RANGE_30k),
    ([(b'FUNC:IMP:RANG 300000', None)],
     MeasurementRange.RANGE_300k),
    ([(b'FUNC:IMP:RANG 1000000', None)],
     MeasurementRange.RANGE_1M),
))
def test_measurement_range_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.measurement_range = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:RANG?', b'30\n')],
     MeasurementRange.RANGE_30),
    ([(b'FUNC:IMP:RANG?', b'100\n')],
     MeasurementRange.RANGE_100),
    ([(b'FUNC:IMP:RANG?', b'300\n')],
     MeasurementRange.RANGE_300),
    ([(b'FUNC:IMP:RANG?', b'1000\n')],
     MeasurementRange.RANGE_1k),
    ([(b'FUNC:IMP:RANG?', b'3000\n')],
     MeasurementRange.RANGE_3k),
    ([(b'FUNC:IMP:RANG?', b'30000\n')],
     MeasurementRange.RANGE_30k),
    ([(b'FUNC:IMP:RANG?', b'300000\n')],
     MeasurementRange.RANGE_300k),
    ([(b'FUNC:IMP:RANG?', b'1000000\n')],
     MeasurementRange.RANGE_1M),
))
def test_measurement_range_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.measurement_range == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'APER SLOW', None)],
     MeasurementSpeed.SLOW),
    ([(b'APER FAST', None)],
     MeasurementSpeed.FAST),
    ([(b'APER MEDium', None)],
     MeasurementSpeed.MEDIUM),
))
def test_measurement_speed_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.measurement_speed = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'APER?', b'SLOW,1.000000\n')],
     MeasurementSpeed.SLOW),
    ([(b'APER?', b'FAST,1.000000\n')],
     MeasurementSpeed.FAST),
    ([(b'APER?', b'MEDium,1.000000\n')],
     MeasurementSpeed.MEDIUM),
))
def test_measurement_speed_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.measurement_speed == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:TYPE CPD', None)],
     MeasurementType.CpD),
    ([(b'FUNC:IMP:TYPE CPQ', None)],
     MeasurementType.CpQ),
    ([(b'FUNC:IMP:TYPE CPG', None)],
     MeasurementType.CpG),
    ([(b'FUNC:IMP:TYPE CPRP', None)],
     MeasurementType.CpRp),
    ([(b'FUNC:IMP:TYPE CSD', None)],
     MeasurementType.CsD),
    ([(b'FUNC:IMP:TYPE CSQ', None)],
     MeasurementType.CsQ),
    ([(b'FUNC:IMP:TYPE CSRS', None)],
     MeasurementType.CsRs),
    ([(b'FUNC:IMP:TYPE LPD', None)],
     MeasurementType.LpD),
    ([(b'FUNC:IMP:TYPE LPQ', None)],
     MeasurementType.LpQ),
    ([(b'FUNC:IMP:TYPE LPG', None)],
     MeasurementType.LpG),
    ([(b'FUNC:IMP:TYPE LPRP', None)],
     MeasurementType.LpRp),
    ([(b'FUNC:IMP:TYPE LSD', None)],
     MeasurementType.LsD),
    ([(b'FUNC:IMP:TYPE LSQ', None)],
     MeasurementType.LsQ),
    ([(b'FUNC:IMP:TYPE LSRS', None)],
     MeasurementType.LsRs),
    ([(b'FUNC:IMP:TYPE RX', None)],
     MeasurementType.RX),
    ([(b'FUNC:IMP:TYPE ZTD', None)],
     MeasurementType.ZDeg),
    ([(b'FUNC:IMP:TYPE ZTR', None)],
     MeasurementType.ZRad),
    ([(b'FUNC:IMP:TYPE GB', None)],
     MeasurementType.GB),
    ([(b'FUNC:IMP:TYPE YTD', None)],
     MeasurementType.YDeg),
    ([(b'FUNC:IMP:TYPE YTR', None)],
     MeasurementType.YRad),
))
def test_measurement_type_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.measurement_type = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'FUNC:IMP:TYPE?', b'CPD\n')],
     MeasurementType.CpD),
    ([(b'FUNC:IMP:TYPE?', b'CPQ\n')],
     MeasurementType.CpQ),
    ([(b'FUNC:IMP:TYPE?', b'CPG\n')],
     MeasurementType.CpG),
    ([(b'FUNC:IMP:TYPE?', b'CPRP\n')],
     MeasurementType.CpRp),
    ([(b'FUNC:IMP:TYPE?', b'CSD\n')],
     MeasurementType.CsD),
    ([(b'FUNC:IMP:TYPE?', b'CSQ\n')],
     MeasurementType.CsQ),
    ([(b'FUNC:IMP:TYPE?', b'CSRS\n')],
     MeasurementType.CsRs),
    ([(b'FUNC:IMP:TYPE?', b'LPD\n')],
     MeasurementType.LpD),
    ([(b'FUNC:IMP:TYPE?', b'LPQ\n')],
     MeasurementType.LpQ),
    ([(b'FUNC:IMP:TYPE?', b'LPG\n')],
     MeasurementType.LpG),
    ([(b'FUNC:IMP:TYPE?', b'LPRP\n')],
     MeasurementType.LpRp),
    ([(b'FUNC:IMP:TYPE?', b'LSD\n')],
     MeasurementType.LsD),
    ([(b'FUNC:IMP:TYPE?', b'LSQ\n')],
     MeasurementType.LsQ),
    ([(b'FUNC:IMP:TYPE?', b'LSRS\n')],
     MeasurementType.LsRs),
    ([(b'FUNC:IMP:TYPE?', b'RX\n')],
     MeasurementType.RX),
    ([(b'FUNC:IMP:TYPE?', b'ZTD\n')],
     MeasurementType.ZDeg),
    ([(b'FUNC:IMP:TYPE?', b'ZTR\n')],
     MeasurementType.ZRad),
    ([(b'FUNC:IMP:TYPE?', b'GB\n')],
     MeasurementType.GB),
    ([(b'FUNC:IMP:TYPE?', b'YTD\n')],
     MeasurementType.YDeg),
    ([(b'FUNC:IMP:TYPE?', b'YTR\n')],
     MeasurementType.YRad),
))
def test_measurement_type_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.measurement_type == value


def test_monitor_current_ac_getter():
    with expected_protocol(
            ET3510,
            [(b'FETC:SMON:IAC?', b'5.007905e-09\n')],
            timeout=5000,
    ) as inst:
        assert inst.monitor_current_ac == 5.007905e-09


def test_monitor_voltage_ac_getter():
    with expected_protocol(
            ET3510,
            [(b'FETC:SMON:VAC?', b'5.482244e-02\n')],
            timeout=5000,
    ) as inst:
        assert inst.monitor_voltage_ac == 0.05482244


def test_monitor_voltage_dc_bias_getter():
    with expected_protocol(
            ET3510,
            [(b'FETC:SMON:EBV?', b'1.248779e+00\n')],
            timeout=5000,
    ) as inst:
        assert inst.monitor_voltage_dc_bias == 1.248779


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'TRIG:TDEL 1', None)],
     1),
    ([(b'TRIG:TDEL 5', None)],
     5),
    ([(b'TRIG:TDEL 10', None)],
     10),
    ([(b'TRIG:TDEL 0', None)],
     0),
))
def test_trigger_delay_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.trigger_delay = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'TRIG:TDEL?', b'1\n')],
     1.0),
    ([(b'TRIG:TDEL?', b'5\n')],
     5.0),
    ([(b'TRIG:TDEL?', b'10\n')],
     10.0),
    ([(b'TRIG:TDEL?', b'0\n')],
     0.0),
))
def test_trigger_delay_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.trigger_delay == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'TRIG:SOUR BUS', None)],
     TriggerSource.BUS),
    ([(b'TRIG:SOUR INTernal', None)],
     TriggerSource.INTERNAL),
    ([(b'TRIG:SOUR EXTernal', None)],
     TriggerSource.EXTERNAL),
    ([(b'TRIG:SOUR HOLD', None)],
     TriggerSource.MANUAL),
    ([(b'TRIG:SOUR BUS', None)],
     TriggerSource.BUS),
))
def test_trigger_source_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.trigger_source = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'TRIG:SOUR?', b'INTernal\n')],
     TriggerSource.INTERNAL),
    ([(b'TRIG:SOUR?', b'EXTernal\n')],
     TriggerSource.EXTERNAL),
    ([(b'TRIG:SOUR?', b'HOLD\n')],
     TriggerSource.MANUAL),
    ([(b'TRIG:SOUR?', b'BUS\n')],
     TriggerSource.BUS),
))
def test_trigger_source_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.trigger_source == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT 1.000000', None)],
     1),
    ([(b'VOLT 1.000000', None)],
     1),
    ([(b'VOLT 0.010000', None)],
     0.01),
    ([(b'VOLT 0.100000', None)],
     0.1),
    ([(b'VOLT 1.000000', None)],
     1),
    ([(b'VOLT 2.000000', None)],
     2),
))
def test_voltage_setter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        inst.voltage = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'VOLT?', b'1.000000e-02\n')],
     0.01),
    ([(b'VOLT?', b'1.000000e-01\n')],
     0.1),
    ([(b'VOLT?', b'1.000000e+00\n')],
     1.0),
    ([(b'VOLT?', b'2.000000e+00\n')],
     2.0),
))
def test_voltage_getter(comm_pairs, value):
    with expected_protocol(
            ET3510,
            comm_pairs,
            timeout=5000,
    ) as inst:
        assert inst.voltage == value


def test_beep():
    with expected_protocol(
            ET3510,
            [(b'SYST:BEEP:IMM', None)],
            timeout=5000,
    ) as inst:
        assert inst.beep() is None


def test_clear():
    with expected_protocol(
            ET3510,
            [(b'*CLS', None)],
            timeout=5000,
    ) as inst:
        assert inst.clear() is None


def test_trigger():
    with expected_protocol(
            ET3510,
            [(b'TRIG:IMM', None)],
            timeout=5000,
    ) as inst:
        assert inst.trigger() is None
