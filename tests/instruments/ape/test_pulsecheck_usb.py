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

import struct

import pytest

from pymeasure.instruments.ape import PulseCheckUSB
from pymeasure.instruments.ape.pulsecheck_usb import (
    BusyStatus,
    DataError,
    FirmwareError,
    InitializationStatus,
    OperationStatus,
    parse_averages,
    parse_resolution,
)
from pymeasure.test import expected_protocol


def block(*values):
    """Pack `values` as the definite length block of doubles the software sends."""
    payload = struct.pack(f"<{len(values)}d", *values)
    length = str(len(payload))
    return f"#{len(length)}{length}".encode() + payload


@pytest.mark.parametrize("reply, resolution", [
    ("very low", 200), ("Low\r", 500), ("very high", 2000),  # the names
    ("200", 200), ("500", 500), ("2000", 2000),  # the number of samples the software answers
    ("0", 200), ("1", 500), ("4", 2000),  # the index notation documented in the manual
])
def test_parse_resolution(reply, resolution):
    assert parse_resolution(reply) == resolution


@pytest.mark.parametrize("reply", ["-1", "999"])
def test_parse_resolution_invalid(reply):
    with pytest.raises(ValueError, match="resolution"):
        parse_resolution(reply)


@pytest.mark.parametrize("reply, averages", [
    ("Off", 1), ("Low (2)", 2), ("Very high (16)", 16),  # what the software answers
    ("8", 8), ("16", 16),  # the number of measurements
    ("0", 1), ("3", 8),  # the index notation documented in the manual
])
def test_parse_averages(reply, averages):
    assert parse_averages(reply) == averages


@pytest.mark.parametrize("reply", ["-1", "5", "99"])
def test_parse_averages_invalid(reply):
    with pytest.raises(ValueError, match="averages"):
        parse_averages(reply)


def test_id():
    with expected_protocol(
        PulseCheckUSB,
        [("*IDN?", "APE GmbH;pulseLink S12345;Software 1.9.3.12;Firmware 787")],
    ) as inst:
        assert inst.id == "APE GmbH;pulseLink S12345;Software 1.9.3.12;Firmware 787"


def test_parser_error():
    with expected_protocol(
        PulseCheckUSB,
        [("*OPT?", "Parser error")],
    ) as inst, pytest.raises(ValueError, match="did not understand"):
        _ = inst.options


def test_read_strips_padding():
    with expected_protocol(
        PulseCheckUSB,
        [("SYSTEM:DEVICE?", b"\x00pulseCheck USB 15\x00")],
    ) as inst:
        assert inst.device_name == "pulseCheck USB 15"


def test_serial_number():
    with expected_protocol(
        PulseCheckUSB,
        [("SYSTEM:SNUMBER?", "S12345")],
    ) as inst:
        assert inst.serial_number == "S12345"


@pytest.mark.parametrize("command, attribute", [
    ("SYSTEM:SOFTWARE?", "software_version"),
    ("SYSTEM:HARDWARE?", "hardware_version"),
    ("SYSTEM:FIRMWARE?", "firmware_version"),
    ("SYSTEM:MOTOR?", "motor_type"),
])
def test_version_properties(command, attribute):
    with expected_protocol(
        PulseCheckUSB,
        [(command, "1.2.3")],
    ) as inst:
        assert getattr(inst, attribute) == "1.2.3"


def test_operation_status():
    with expected_protocol(
        PulseCheckUSB,
        [("*OPER?", "26")],
    ) as inst:
        assert inst.operation_status == (
            OperationStatus.VISA_CONNECTED
            | OperationStatus.DEVICE_READY
            | OperationStatus.DEVICE_BUSY
        )


def test_initialization_status():
    with expected_protocol(
        PulseCheckUSB,
        [("*INIT?", "252")],
    ) as inst:
        # the upper four bits are always set and have to be masked away
        assert inst.initialization_status == (
            InitializationStatus.LINK_OK | InitializationStatus.OPTIC_OK
        )


def test_busy_status():
    with expected_protocol(
        PulseCheckUSB,
        [("*BUSY?", "6")],
    ) as inst:
        assert inst.busy_status == BusyStatus.NEW_DATA | BusyStatus.MEASUREMENT_RUNNING


def test_data_errors():
    with expected_protocol(
        PulseCheckUSB,
        [("*ERR?", "5")],
    ) as inst:
        assert inst.data_errors == DataError.SIGNAL_TOO_LOW | DataError.NO_PEAK_FOUND


def test_check_errors():
    with expected_protocol(
        PulseCheckUSB,
        [("*FRMW?", "2")],
    ) as inst:
        assert inst.check_errors() == [FirmwareError.PARAMETER_ERROR]


def test_check_errors_lists_every_error():
    with expected_protocol(
        PulseCheckUSB,
        [("*FRMW?", "3")],
    ) as inst:
        assert inst.check_errors() == [FirmwareError.PARSER_ERROR,
                                       FirmwareError.PARAMETER_ERROR]


def test_check_errors_empty():
    with expected_protocol(
        PulseCheckUSB,
        [("*FRMW?", "0")],
    ) as inst:
        assert inst.check_errors() == []


def test_measurement_running():
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:START?", "1"), ("STATUS:START=0", None)],
    ) as inst:
        assert inst.measurement_running is True
        inst.measurement_running = False


@pytest.mark.parametrize("reply, averages", [
    ("Off", 1), ("Low (2)", 2), ("Medium (4)", 4), ("High (8)", 8), ("Very high (16)", 16),
    ("3", 8),  # the index notation documented in the manual
])
def test_averages_reply_notations(reply, averages):
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:AVERAGE?", reply)],
    ) as inst:
        assert inst.averages == averages


def test_averages_set():
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:AVERAGE=4", None)],
    ) as inst:
        inst.averages = 16


def test_averages_invalid():
    with expected_protocol(PulseCheckUSB, []) as inst, pytest.raises(ValueError):
        inst.averages = 3


@pytest.mark.parametrize("reply", ["1", "500", "low", "Low\r"])
def test_resolution_reply_notations(reply):
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:RESOLUTION?", reply)],
    ) as inst:
        assert inst.resolution == 500


def test_resolution_set():
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:RESOLUTION=4", None)],
    ) as inst:
        inst.resolution = 2000


def test_fit_type():
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:FITTYPE?", "2"), ("STATUS:FITTYPE=1", None)],
    ) as inst:
        assert inst.fit_type == "sech2"
        inst.fit_type = "gaussian"


def test_filter_enabled():
    with expected_protocol(
        PulseCheckUSB,
        [("STATUS:FILTER?", "0"), ("STATUS:FILTER=1", None)],
    ) as inst:
        assert inst.filter_enabled is False
        inst.filter_enabled = True


def test_scan_range():
    with expected_protocol(
        PulseCheckUSB,
        [("MOTOR:SCANRANGE?", "15000"), ("MOTOR:SCANRANGE=150", None)],
    ) as inst:
        assert inst.scan_range == pytest.approx(15e-12)
        inst.scan_range = 150e-15


def test_gain():
    with expected_protocol(
        PulseCheckUSB,
        [("DETECTOR:GAIN?", "450"), ("DETECTOR:GAIN=1000", None)],
    ) as inst:
        assert inst.gain == 450
        inst.gain = 1000


def test_gain_out_of_range():
    with expected_protocol(PulseCheckUSB, []) as inst, pytest.raises(ValueError):
        inst.gain = 299


def test_autogain_enabled():
    with expected_protocol(
        PulseCheckUSB,
        [("DETECTOR:AUTOGAIN?", "1"), ("DETECTOR:AUTOGAIN=0", None)],
    ) as inst:
        assert inst.autogain_enabled is True
        inst.autogain_enabled = False


def test_sensitivity():
    with expected_protocol(
        PulseCheckUSB,
        [("DETECTOR:SENSITIVITY?", "10"), ("DETECTOR:SENSITIVITY=1", None)],
    ) as inst:
        assert inst.sensitivity == 10
        inst.sensitivity = 1


def test_trigger_properties():
    with expected_protocol(
        PulseCheckUSB,
        [("TRIGGER:LEVEL?", "1200"),
         ("TRIGGER:DELAY?", "25"),
         ("TRIGGER:FREQUENCY?", "80000000"),
         ("TRIGGER:IMPEDANCE?", "50")],
    ) as inst:
        assert inst.trigger_level == pytest.approx(1.2)
        assert inst.trigger_delay == pytest.approx(25e-6)
        assert inst.trigger_frequency == pytest.approx(80e6)
        assert inst.trigger_impedance == pytest.approx(50)


def test_acf():
    with expected_protocol(
        PulseCheckUSB,
        # interleaved as [intensity, delay, ...] with the delay in ps
        [("ACF:DATA?", block(0.25, -1.5, 1.0, 0.0, 0.25, 1.5))],
    ) as inst:
        delay, intensity = inst.acf
        assert delay == pytest.approx([-1.5e-12, 0, 1.5e-12])
        assert intensity == pytest.approx([0.25, 1.0, 0.25])
        # the reply itself is read-only, the trace handed out must not be
        assert delay.flags.writeable and intensity.flags.writeable


def test_displayed_acf():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:DISPLAYED_ACF?", block(0.5, -1.0, 0.5, 1.0))],
    ) as inst:
        delay, intensity = inst.displayed_acf
        assert delay == pytest.approx([-1e-12, 1e-12])
        assert intensity == pytest.approx([0.5, 0.5])


def test_acf_without_block():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:DATA?", "Parser error")],
    ) as inst, pytest.raises(ValueError, match="data block"):
        _ = inst.acf


def test_acf_message_instead_of_data():
    with expected_protocol(
        PulseCheckUSB,
        # the software answers like this while it has no valid autocorrelation
        [("ACF:DATA?", b"#18Time out")],
    ) as inst, pytest.raises(ValueError, match="Time out"):
        _ = inst.acf


def test_acf_mean_data():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:MEANDATA?", "0.4;7.5;-7.5;1.0;0.05")],
    ) as inst:
        assert inst.acf_mean_data == {
            "average": pytest.approx(0.4),
            "delay_max": pytest.approx(7.5e-12),
            "delay_min": pytest.approx(-7.5e-12),
            "intensity_max": pytest.approx(1.0),
            "intensity_min": pytest.approx(0.05),
        }


def test_acf_mean_data_as_block():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:MEANDATA?", b"#221" + b"0.4;7.5;-7.5;1.0;0.05")],
    ) as inst:
        assert inst.acf_mean_data["delay_max"] == pytest.approx(7.5e-12)


def test_acf_mean_data_message():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:MEANDATA?", b"#18Time out")],
    ) as inst, pytest.raises(ValueError, match="Time out"):
        _ = inst.acf_mean_data


def test_acf_mean_data_parser_error():
    """The first character is read separately, so read() cannot spot the parser error."""
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:MEANDATA?", "Parser error")],
    ) as inst, pytest.raises(ValueError, match="did not understand"):
        _ = inst.acf_mean_data


def test_fwhm():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:FWHM?", "0.35"), ("ACF:FITFWHM?", "0.34")],
    ) as inst:
        assert inst.fwhm == pytest.approx(0.35e-12)
        assert inst.fit_fwhm == pytest.approx(0.34e-12)


def test_fit_fwhm_without_fit():
    with expected_protocol(
        PulseCheckUSB,
        [("ACF:FITFWHM?", "No fit data")],
    ) as inst, pytest.raises(ValueError, match="No fit data"):
        _ = inst.fit_fwhm


def test_shutters():
    with expected_protocol(
        PulseCheckUSB,
        [("SHUTTER:FIX?", "1"), ("SHUTTER:SCAN=0", None)],
    ) as inst:
        assert inst.fix_shutter_open is True
        inst.scan_shutter_open = False


def test_crystal_position():
    with expected_protocol(
        PulseCheckUSB,
        [("XTAL:TUNING?", "5000"), ("XTAL:TUNING=6000", None)],
    ) as inst:
        assert inst.crystal_position == 5000
        inst.crystal_position = 6000


def test_crystal_wavelength():
    with expected_protocol(
        PulseCheckUSB,
        [("XTAL:LAMBDATUNE=1030", None)],
    ) as inst:
        inst.crystal_wavelength = 1030


def test_crystal_status():
    with expected_protocol(
        PulseCheckUSB,
        [("XTAL:MOVE?", "0"), ("XTAL:SETXTAL?", "BBO")],
    ) as inst:
        assert inst.crystal_moving is False
        assert inst.crystal_type == "BBO"
