#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import itertools
from unittest.mock import patch

import pytest

from pymeasure.instruments.keysight.keysightb2910bl import (
    B2910BLReading,
    B2910BLSweepPoint,
    KeysightB2910BL,
    SweepShutdownError,
)
from pymeasure.test import expected_protocol

NO_ERROR = '0,"No error"'


def add_write(protocol, command):
    protocol.extend([(command, None), ("SYST:ERR?", NO_ERROR)])


def add_checked_query(protocol, command, response):
    protocol.extend([(command, response), ("SYST:ERR?", NO_ERROR)])


def add_interlock_query(protocol, response):
    add_checked_query(protocol, ":SYSTem:INTerlock:TRIPped?", response)


def add_config(protocol, mode, source_value, compliance, nplc=0.1, voltage_range=None,
               current_range=None):
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":ABORt:ALL (@1)")
    add_write(protocol, ":SOURce1:FUNCtion:SHAPe DC")
    add_write(protocol, ":SOURce1:VOLTage:MODE FIXed")
    add_write(protocol, ":SOURce1:CURRent:MODE FIXed")
    if mode == "VOLT":
        add_write(protocol, f":SENSe1:CURRent:DC:PROTection:LEVel {compliance:g}")
        add_write(
            protocol,
            f":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude {source_value:g}",
        )
        add_write(
            protocol,
            f":SOURce1:VOLTage:LEVel:TRIGgered:AMPLitude {source_value:g}",
        )
        add_checked_query(
            protocol,
            ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?",
            f"{source_value:g}",
        )
    else:
        add_write(protocol, f":SENSe1:VOLTage:DC:PROTection:LEVel {compliance:g}")
        add_write(
            protocol,
            f":SOURce1:CURRent:LEVel:IMMediate:AMPLitude {source_value:g}",
        )
        add_write(
            protocol,
            f":SOURce1:CURRent:LEVel:TRIGgered:AMPLitude {source_value:g}",
        )
        add_checked_query(
            protocol,
            ":SENSe1:VOLTage:DC:PROTection:LEVel?",
            f"{compliance:g}",
        )
    add_write(protocol, f":SOURce1:FUNCtion:MODE {mode}")
    add_checked_query(protocol, ":SOURce1:FUNCtion:MODE?", mode)
    active_value_command = (
        ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?"
        if mode == "VOLT"
        else ":SENSe1:VOLTage:DC:PROTection:LEVel?"
    )
    active_value = source_value if mode == "VOLT" else compliance
    add_checked_query(protocol, active_value_command, f"{active_value:g}")
    add_write(protocol, ":SOURce1:VOLTage:RANGe:AUTO 1")
    add_write(protocol, ":SOURce1:CURRent:RANGe:AUTO 1")
    add_write(protocol, ':SENSe1:FUNCtion:ON "VOLT","CURR"')
    add_write(protocol, f":SENSe1:VOLTage:DC:RANGe:AUTO {int(voltage_range is None)}")
    if voltage_range is not None:
        add_write(protocol, f":SENSe1:VOLTage:DC:RANGe {voltage_range:g}")
    add_write(protocol, f":SENSe1:CURRent:DC:RANGe:AUTO {int(current_range is None)}")
    if current_range is not None:
        add_write(protocol, f":SENSe1:CURRent:DC:RANGe {current_range:g}")
    protocol.append((":SYSTem:LFRequency?", "50"))
    protocol.append(("SYST:ERR?", NO_ERROR))
    add_write(protocol, ":SENSe1:VOLTage:DC:APERture:AUTO 0")
    add_write(protocol, ":SENSe1:VOLTage:DC:NPLCycles:AUTO 0")
    add_write(protocol, f":SENSe1:VOLTage:DC:NPLCycles {nplc:g}")
    add_write(protocol, ":OUTPut1:ON:AUTO 0")
    add_write(protocol, ":OUTPut1:OFF:AUTO 0")
    for action in ("ACQuire", "TRANsient"):
        add_write(protocol, f":ARM1:{action}:COUNt 1")
        add_write(protocol, f":ARM1:{action}:SOURce AINT")
        add_write(protocol, f":TRIGger1:{action}:COUNt 1")
        add_write(protocol, f":TRIGger1:{action}:SOURce AINT")


def add_prepare_read_point(protocol, mode, source_setting=0.0):
    add_write(protocol, ":OUTPut1:ON:AUTO 0")
    add_write(protocol, ":OUTPut1:OFF:AUTO 0")
    add_write(protocol, ":ABORt:ALL (@1)")
    add_write(protocol, ":SOURce1:FUNCtion:SHAPe DC")
    add_write(protocol, ":SOURce1:VOLTage:MODE FIXed")
    add_write(protocol, ":SOURce1:CURRent:MODE FIXed")
    add_write(protocol, ':SENSe1:FUNCtion:ON "VOLT","CURR"')
    for action in ("ACQuire", "TRANsient"):
        add_write(protocol, f":ARM1:{action}:COUNt 1")
        add_write(protocol, f":ARM1:{action}:SOURce AINT")
        add_write(protocol, f":TRIGger1:{action}:COUNt 1")
        add_write(protocol, f":TRIGger1:{action}:SOURce AINT")
    add_write(protocol, ":FORMat:DATA ASCii")
    add_write(protocol, ":FORMat:ELEMents:SENSe VOLT,CURR,SOUR")
    add_checked_query(protocol, ":SOURce1:FUNCtion:MODE?", mode)
    source_function = "VOLTage" if mode == "VOLT" else "CURRent"
    add_checked_query(
        protocol,
        f":SOURce1:{source_function}:LEVel:IMMediate:AMPLitude?",
        f"{source_setting:g}",
    )
    add_write(
        protocol,
        f":SOURce1:{source_function}:LEVel:TRIGgered:AMPLitude {source_setting:g}",
    )


def add_read_point(
    protocol,
    mode,
    values="1.0,0.01,1.0",
    compliance="0",
    check_read=True,
    source_setting=0.0,
):
    add_prepare_read_point(protocol, mode, source_setting)
    protocol.append((":READ? (@1)", values))
    if check_read:
        protocol.append(("SYST:ERR?", NO_ERROR))
        trip_command = (
            ":SENSe1:CURRent:DC:PROTection:TRIPped?"
            if mode == "VOLT"
            else ":SENSe1:VOLTage:DC:PROTection:TRIPped?"
        )
        add_checked_query(protocol, trip_command, compliance)


def add_sweep_start(protocol, mode, first_point, compliance):
    add_config(protocol, mode, first_point, compliance)
    add_checked_query(protocol, ":SOURce1:FUNCtion:MODE?", mode)
    add_checked_query(
        protocol,
        ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?"
        if mode == "VOLT"
        else ":SENSe1:VOLTage:DC:PROTection:LEVel?",
        f"{first_point if mode == 'VOLT' else compliance:g}",
    )
    add_write(protocol, ":OUTPut1 1")


def add_sweep(protocol, mode, points, compliance, samples):
    add_sweep_start(protocol, mode, points[0], compliance)
    for index, (point, sample) in enumerate(zip(points, samples)):
        add_checked_query(protocol, ":OUTPut1?", "1")
        if index:
            source_function = "VOLTage" if mode == "VOLT" else "CURRent"
            add_write(
                protocol,
                f":SOURce1:{source_function}:LEVel:IMMediate:AMPLitude {point:g}",
            )
        add_read_point(protocol, mode, sample[0], sample[1], source_setting=point)
        add_checked_query(protocol, ":OUTPut1?", "1")
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")


def test_constructor_has_only_explicit_channel_one_and_no_traffic():
    with expected_protocol(KeysightB2910BL, []) as instrument:
        assert instrument.ch1.id == 1
        assert instrument.ch1.parent is instrument


@pytest.mark.parametrize(
    "attribute,value,error_type",
    [
        ("source_voltage", True, TypeError),
        ("source_current", float("nan"), ValueError),
        ("current_limit", float("inf"), ValueError),
        ("source_voltage_range", 6.0, ValueError),
    ],
)
def test_invalid_raw_properties_do_not_write(attribute, value, error_type):
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(error_type):
        setattr(instrument.ch1, attribute, value)


def test_boolean_control_rejects_integer_values_without_writing():
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(TypeError):
        instrument.ch1.output_enabled = 1


def test_source_mode_boolean_ranges_measurement_and_compliance_properties():
    protocol = [
        (":SOURce1:FUNCtion:MODE?", "VOLT"),
        ("SYST:ERR?", NO_ERROR),
        (":SENSe1:VOLTage:DC:PROTection:LEVel?", "2"),
        ("SYST:ERR?", NO_ERROR),
        (":SOURce1:FUNCtion:MODE CURR", None),
        ("SYST:ERR?", NO_ERROR),
        (":OUTPut1?", "0"),
        ("SYST:ERR?", NO_ERROR),
        (":SOURce1:FUNCtion:MODE?", "CURR"),
        ("SYST:ERR?", NO_ERROR),
        (":SENSe1:VOLTage:DC:PROTection:LEVel?", "2"),
        ("SYST:ERR?", NO_ERROR),
        (":OUTPut1 1", None),
        ("SYST:ERR?", NO_ERROR),
        (":SENSe1:CURRent:DC:RANGe?", "1.0"),
        ("SYST:ERR?", NO_ERROR),
        (":SENSe1:VOLTage:DC:PROTection:TRIPped?", "1"),
        ("SYST:ERR?", NO_ERROR),
        (":SENSe1:VOLTage:DC:NPLCycles?", "0.25"),
        ("SYST:ERR?", NO_ERROR),
    ]
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        assert instrument.ch1.source_mode == "VOLT"
        instrument.ch1.source_mode = "curr"
        assert instrument.ch1.output_enabled is False
        instrument.ch1.output_enabled = True
        assert instrument.ch1.current_range == 1.0
        assert instrument.ch1.voltage_compliance_tripped is True
        assert instrument.ch1.nplc == 0.25


@pytest.mark.parametrize(
    "attribute,value,command,frequency",
    [
        ("source_voltage", 1.25, ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude 1.25", None),
        ("source_current", -0.05, ":SOURce1:CURRent:LEVel:IMMediate:AMPLitude -0.05", None),
        ("voltage_limit", 5.0, ":SENSe1:VOLTage:DC:PROTection:LEVel 5", None),
        ("current_limit", 0.001, ":SENSe1:CURRent:DC:PROTection:LEVel 0.001", None),
        ("output_enabled", False, ":OUTPut1 0", None),
        ("source_voltage_range", 2.0, ":SOURce1:VOLTage:RANGe 2", None),
        ("source_current_range", 0.001, ":SOURce1:CURRent:RANGe 0.001", None),
        ("source_voltage_autorange", False, ":SOURce1:VOLTage:RANGe:AUTO 0", None),
        ("source_current_autorange", True, ":SOURce1:CURRent:RANGe:AUTO 1", None),
        ("voltage_range", 20.0, ":SENSe1:VOLTage:DC:RANGe 20", None),
        ("current_range", 1e-6, ":SENSe1:CURRent:DC:RANGe 1e-06", None),
        ("voltage_autorange", False, ":SENSe1:VOLTage:DC:RANGe:AUTO 0", None),
        ("current_autorange", True, ":SENSe1:CURRent:DC:RANGe:AUTO 1", None),
        ("nplc", 0.1, ":SENSe1:VOLTage:DC:NPLCycles 0.1", "60"),
        ("nplc_autorange_enabled", False, ":SENSe1:VOLTage:DC:NPLCycles:AUTO 0", None),
        ("aperture_autorange_enabled", False, ":SENSe1:VOLTage:DC:APERture:AUTO 0", None),
        ("remote_sense_enabled", True, ":SENSe1:REMote 1", None),
        ("auto_output_on_enabled", False, ":OUTPut1:ON:AUTO 0", None),
        ("auto_output_off_enabled", False, ":OUTPut1:OFF:AUTO 0", None),
        ("output_off_mode", "hiz", ":OUTPut1:OFF:MODE HIZ", None),
    ],
)
def test_channel_property_controls_use_native_scpi(attribute, value, command, frequency):
    protocol = []
    if frequency is not None:
        protocol.append((":SYSTem:LFRequency?", frequency))
        if attribute == "nplc":
            protocol.append(("SYST:ERR?", NO_ERROR))
            add_write(protocol, ":SENSe1:VOLTage:DC:APERture:AUTO 0")
            add_write(protocol, ":SENSe1:VOLTage:DC:NPLCycles:AUTO 0")
    add_write(protocol, command)
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        setattr(instrument.ch1, attribute, value)


def test_nplc_setter_validates_native_frequency_before_disabling_automatic_modes():
    protocol = [
        (":SYSTem:LFRequency?", "60"),
        ("SYST:ERR?", NO_ERROR),
    ]
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        ValueError, match="outside the native range"
    ):
        instrument.ch1.nplc = 0.0004


@pytest.mark.parametrize(
    "attribute,command",
    [
        ("voltage_compliance_tripped", ":SENSe1:VOLTage:DC:PROTection:TRIPped?"),
        ("current_compliance_tripped", ":SENSe1:CURRent:DC:PROTection:TRIPped?"),
    ],
)
def test_compliance_trip_properties_strictly_parse_nr1(attribute, command):
    protocol = [(command, "0"), ("SYST:ERR?", NO_ERROR)]
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        assert getattr(instrument.ch1, attribute) is False


@pytest.mark.parametrize(
    "attribute,command",
    [
        ("output_enabled", ":OUTPut1?"),
        ("source_voltage_autorange", ":SOURce1:VOLTage:RANGe:AUTO?"),
        ("current_compliance_tripped", ":SENSe1:CURRent:DC:PROTection:TRIPped?"),
    ],
)
def test_boolean_properties_reject_multiple_response_fields(attribute, command):
    protocol = [(command, "0,1"), ("SYST:ERR?", NO_ERROR)]
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        ValueError, match="one NR1 boolean"
    ):
        getattr(instrument.ch1, attribute)


@pytest.mark.parametrize(
    "attribute,command,response,expected",
    [
        ("voltage", ":MEASure:VOLTage:DC? (@1)", "-2.5E-01", -0.25),
        ("current", ":MEASure:CURRent:DC? (@1)", "+4.2E-06", 4.2e-6),
    ],
)
def test_native_voltage_and_current_measurement_properties(
    attribute, command, response, expected
):
    protocol = [(command, response), ("SYST:ERR?", NO_ERROR)]
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        assert getattr(instrument.ch1, attribute) == expected


def test_configure_voltage_uses_native_commands_and_leaves_output_off():
    protocol = []
    add_config(protocol, "VOLT", 20.0, 1.0, 0.1, None, 1.0)
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        instrument.ch1.configure_voltage(20, 1, current_range=1.0)


def test_configure_current_uses_voltage_compliance_and_fixed_source():
    protocol = []
    add_config(protocol, "CURR", -0.02, 10.0, 0.1, 2.0, None)
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        instrument.ch1.configure_current(-0.02, 10.0, voltage_range=2.0)


@pytest.mark.parametrize(
    "args,error_type",
    [
        ((50.0, 0.2), ValueError),
        ((float("nan"), 0.01), ValueError),
        ((True, 0.01), TypeError),
        ((1.0, float("inf")), ValueError),
    ],
)
def test_invalid_configuration_is_rejected_before_first_write(args, error_type):
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(error_type):
        instrument.ch1.configure_voltage(*args)


def test_high_voltage_configuration_requires_closed_interlock_before_writing():
    protocol = []
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":ABORt:ALL (@1)")
    add_interlock_query(protocol, "1")
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="interlock reports open"
    ):
        instrument.ch1.configure_voltage(50, 0.05)


@pytest.mark.parametrize(
    "attribute,value,protocol",
    [
        (
            "source_voltage",
            50.0,
            [(":SYSTem:INTerlock:TRIPped?", "1"), ("SYST:ERR?", NO_ERROR)],
        ),
        (
            "voltage_limit",
            50.0,
            [(":SYSTem:INTerlock:TRIPped?", "1"), ("SYST:ERR?", NO_ERROR)],
        ),
        (
            "source_voltage_autorange",
            True,
            [
                (":SOURce1:FUNCtion:MODE?", "VOLT"),
                ("SYST:ERR?", NO_ERROR),
                (":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?", "50"),
                ("SYST:ERR?", NO_ERROR),
                (":SYSTem:INTerlock:TRIPped?", "1"),
                ("SYST:ERR?", NO_ERROR),
            ],
        ),
        (
            "output_enabled",
            True,
            [
                (":SOURce1:FUNCtion:MODE?", "VOLT"),
                ("SYST:ERR?", NO_ERROR),
                (":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?", "50"),
                ("SYST:ERR?", NO_ERROR),
                (":SYSTem:INTerlock:TRIPped?", "1"),
                ("SYST:ERR?", NO_ERROR),
            ],
        ),
    ],
)
def test_raw_high_voltage_controls_block_before_write_when_interlock_is_open(
    attribute, value, protocol
):
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="interlock reports open"
    ):
        setattr(instrument.ch1, attribute, value)


@pytest.mark.parametrize("voltage,current", [(21.0, 1.515), (210.0, 0.105), (-210.0, 0.105)])
def test_b2910bl_envelope_boundary_is_accepted(voltage, current):
    with expected_protocol(KeysightB2910BL, []) as instrument:
        instrument.ch1._validate_voltage_config(voltage, current, 0.1, "AUTO", "AUTO")


@pytest.mark.parametrize("voltage,current", [(21.0001, 0.1051), (210.0, 0.1051), (210.1, 0.01)])
def test_b2910bl_envelope_boundary_is_rejected(voltage, current):
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(ValueError):
        instrument.ch1._validate_voltage_config(voltage, current, 0.1, "AUTO", "AUTO")


def test_interlock_response_must_be_a_documented_nr1_value():
    protocol = []
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":ABORt:ALL (@1)")
    protocol.append((":SYSTem:INTerlock:TRIPped?", "2"))
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        ValueError, match="NR1 boolean"
    ):
        instrument.ch1.configure_voltage(50, 0.05)


def test_read_point_uses_one_paired_read_and_active_compliance_query():
    protocol = []
    add_read_point(
        protocol,
        "VOLT",
        "-1.25E+00,+3.5E-04,-1.2E+00",
        "1",
        source_setting=-1.2,
    )
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        reading = instrument.ch1.read_point()
    assert reading == B2910BLReading(-1.25, 3.5e-4, -1.2, True)


@pytest.mark.parametrize(
    "reply,error_type",
    [
        ("", ValueError),
        ("1,2", ValueError),
        ("1,2,3,4", ValueError),
        ("1,not-a-number,3", ValueError),
        ("1,nan,3", ValueError),
        ("+9.910000E+37,2,3", ValueError),
        ("1,+9.900000E+37,3", OverflowError),
        ("1,-9.900000E+37,3", OverflowError),
    ],
)
def test_read_point_rejects_missing_malformed_and_infinite_sentinels(reply, error_type):
    protocol = []
    add_read_point(protocol, "VOLT", reply, check_read=False)
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(error_type):
        instrument.ch1.read_point()


def test_read_point_uses_voltage_compliance_query_in_current_mode():
    protocol = []
    add_read_point(protocol, "CURR", "1,2,3", "0", source_setting=3.0)
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        reading = instrument.ch1.read_point()
    assert reading.compliance is False


@pytest.mark.parametrize(
    "points,mode,compliance,samples",
    [
        ([-1.0, 0.0, 1.0, 1.0], "VOLT", 0.01,
         [("-1,-0.1,-1", "0"), ("0,0,0", "0"), ("1,0.1,1", "0"), ("1,0.1,1", "1")]),
        ([0.2], "VOLT", 0.01, [("0.2,0.01,0.2", "0")]),
        ([0.02, 0.0, -0.02], "CURR", 10.0,
         [("1,0.02,0.02", "0"), ("0,0,0", "0"), ("-1,-0.02,-0.02", "1")]),
    ],
)
def test_host_stepped_sweeps_preserve_point_order_and_always_confirm_off(
    points, mode, compliance, samples
):
    protocol = []
    add_sweep(protocol, mode, points, compliance, samples)
    channel_sweep = "sweep_voltage" if mode == "VOLT" else "sweep_current"
    with expected_protocol(KeysightB2910BL, protocol) as instrument, patch(
        "pymeasure.instruments.keysight.keysightb2910bl.time.sleep"
    ) as sleep:
        results = getattr(instrument.ch1, channel_sweep)(points, compliance, settle=0.25)
    assert [point.requested_setpoint for point in results] == points
    assert all(isinstance(point, B2910BLSweepPoint) for point in results)
    assert [point.compliance for point in results] == [sample[1] == "1" for sample in samples]
    assert sleep.call_count == len(points)
    sleep.assert_called_with(0.25)


@pytest.mark.parametrize(
    "mode,points,compliance,sample",
    [
        ("VOLT", [0.1, 0.2], 0.01, "0.1,0.001,0.1"),
        ("CURR", [0.001, 0.002], 1.0, "1,0.001,0.001"),
    ],
)
def test_sweep_stops_when_output_is_off_before_a_point(mode, points, compliance, sample):
    protocol = []
    add_sweep_start(protocol, mode, points[0], compliance)
    add_checked_query(protocol, ":OUTPut1?", "1")
    add_read_point(protocol, mode, sample, "0", source_setting=points[0])
    add_checked_query(protocol, ":OUTPut1?", "1")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    channel_sweep = "sweep_voltage" if mode == "VOLT" else "sweep_current"
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="turned off before sweep point 2"
    ):
        getattr(instrument.ch1, channel_sweep)(points, compliance)


@pytest.mark.parametrize(
    "mode,points,compliance,sample",
    [
        ("VOLT", [0.1, 0.2], 0.01, "0.1,0.01,0.1"),
        ("CURR", [0.001, 0.002], 1.0, "1,0.001,0.001"),
    ],
)
def test_sweep_stops_when_protection_turns_output_off_after_a_read(
    mode, points, compliance, sample
):
    protocol = []
    add_sweep_start(protocol, mode, points[0], compliance)
    add_checked_query(protocol, ":OUTPut1?", "1")
    add_read_point(
        protocol,
        mode,
        sample,
        "1",
        source_setting=points[0],
    )
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    channel_sweep = "sweep_voltage" if mode == "VOLT" else "sweep_current"
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="turned off after sweep point 1"
    ):
        getattr(instrument.ch1, channel_sweep)(points, compliance)


def test_sweep_output_state_query_failure_still_requests_output_off():
    protocol = []
    add_sweep_start(protocol, "VOLT", 0.1, 0.01)
    output_state_index = len(protocol)
    protocol.append((":OUTPut1?", None))
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        adapter = instrument.adapter
        original_read = adapter.read
        query_failed = False

        def fail_output_state_query_once(**kwargs):
            nonlocal query_failed
            if not query_failed and adapter._index == output_state_index + 1:
                query_failed = True
                raise TimeoutError("output-state query timeout")
            return original_read(**kwargs)

        adapter.read = fail_output_state_query_once
        with pytest.raises(TimeoutError, match="output-state query timeout"):
            instrument.ch1.sweep_voltage([0.1], 0.01)


@pytest.mark.parametrize(
    "points,kwargs,error_type",
    [
        ([], {}, ValueError),
        ([0.0, float("nan")], {}, ValueError),
        ([0.0, True], {}, TypeError),
        ([0.0, 211.0], {}, ValueError),
        ([0.0], {"nplc": 0.001}, ValueError),
        ([0.0], {"settle": -0.1}, ValueError),
        ([0.0], {"settle": float("inf")}, ValueError),
        ([0.0], {"voltage_range": 6.0}, ValueError),
    ],
)
def test_sweep_prevalidation_rejects_bad_input_without_writing(points, kwargs, error_type):
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(error_type):
        instrument.ch1.sweep_voltage(points, 0.01, **kwargs)


def test_sweep_bounds_consumption_of_an_infinite_iterable_before_writing():
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(
        ValueError, match="at most 100000"
    ):
        instrument.ch1.sweep_voltage(itertools.repeat(0.0), 0.01)


def test_sweep_prevalidates_every_point_envelope_before_writing():
    with expected_protocol(KeysightB2910BL, []) as instrument, pytest.raises(
        ValueError, match="envelope"
    ):
        instrument.ch1.sweep_voltage([0.0, 22.0], 0.2)


def test_high_voltage_sweep_checks_interlock_before_source_configuration_and_cleans_up():
    protocol = []
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":ABORt:ALL (@1)")
    add_interlock_query(protocol, "1")
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="interlock reports open"
    ):
        instrument.ch1.sweep_voltage([50.0], 0.05)


def test_later_high_voltage_sweep_point_checks_interlock_before_output_enable():
    protocol = []
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    add_write(protocol, ":ABORt:ALL (@1)")
    add_interlock_query(protocol, "1")
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="interlock reports open"
    ):
        instrument.ch1.sweep_voltage([0.1, 50.0], 0.05)


def test_sweep_does_not_continue_after_read_failure_and_preserves_shutdown_failure():
    protocol = []
    add_config(protocol, "VOLT", 0.1, 0.01)
    add_checked_query(protocol, ":SOURce1:FUNCtion:MODE?", "VOLT")
    add_checked_query(protocol, ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?", "0.1")
    add_write(protocol, ":OUTPut1 1")
    add_checked_query(protocol, ":OUTPut1?", "1")
    add_read_point(protocol, "VOLT", "malformed", check_read=False, source_setting=0.1)
    protocol.extend(
        [
            (":OUTPut1 0", None),
            ("SYST:ERR?", '-100,"Command error"'),
            ("SYST:ERR?", NO_ERROR),
            (":OUTPut1?", "0"),
            ("SYST:ERR?", NO_ERROR),
        ]
    )
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        SweepShutdownError
    ) as error:
        instrument.ch1.sweep_voltage([0.1, 0.2], 0.01)
    assert isinstance(error.value.scan_error, ValueError)
    assert "output-off request reported an error" in str(error.value.shutdown_error)


def test_sweep_transport_timeout_still_requests_and_verifies_output_off():
    protocol = []
    add_config(protocol, "VOLT", 0.1, 0.01)
    add_checked_query(protocol, ":SOURce1:FUNCtion:MODE?", "VOLT")
    add_checked_query(protocol, ":SOURce1:VOLTage:LEVel:IMMediate:AMPLitude?", "0.1")
    add_write(protocol, ":OUTPut1 1")
    add_checked_query(protocol, ":OUTPut1?", "1")
    add_prepare_read_point(protocol, "VOLT", source_setting=0.1)
    read_pair_index = len(protocol)
    protocol.append((":READ? (@1)", None))
    add_write(protocol, ":OUTPut1 0")
    add_checked_query(protocol, ":OUTPut1?", "0")
    with expected_protocol(KeysightB2910BL, protocol) as instrument:
        adapter = instrument.adapter
        original_read = adapter.read
        timeout_used = False

        def fail_read_once(**kwargs):
            nonlocal timeout_used
            if not timeout_used and adapter._index == read_pair_index + 1:
                timeout_used = True
                raise TimeoutError("read timeout")
            return original_read(**kwargs)

        adapter.read = fail_read_once
        with pytest.raises(TimeoutError, match="read timeout"):
            instrument.ch1.sweep_voltage([0.1], 0.01)


@pytest.mark.parametrize(
    "reply",
    ["", "1,No error", "x,\"bad\"", "0,\"No error\" trailing"],
)
def test_error_queue_response_is_strictly_parsed(reply):
    with expected_protocol(KeysightB2910BL, [("SYST:ERR?", reply)]) as instrument, pytest.raises(
        ValueError
    ):
        instrument.check_errors()


def test_scpi_error_queue_is_actionable_on_a_property_set():
    protocol = [
        (":OUTPut1 0", None),
        ("SYST:ERR?", '-222,"Data out of range"'),
        ("SYST:ERR?", NO_ERROR),
    ]
    with expected_protocol(KeysightB2910BL, protocol) as instrument, pytest.raises(
        RuntimeError, match="-222: Data out of range"
    ):
        instrument.ch1.output_enabled = False
