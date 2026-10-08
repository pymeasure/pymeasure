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

"""Tests requiring a pulseCheck USB attached to a PC running the pulseLink software.

Enable the TCP/IP port in the software under ``Extras`` → ``TCP``, then run::

    pytest tests/instruments/ape/test_pulsecheck_usb_with_device.py \
        --device-address TCPIP::192.168.0.10::51123::SOCKET

The settings the tests change are read at the start and written back afterwards. The delay
drive and the crystal motor are only read, never moved. Tests needing a real autocorrelation
are skipped if no pulse train reaches the detector.
"""

import time

import numpy as np
import pytest

from pymeasure.instruments.ape import PulseCheckUSB
from pymeasure.instruments.ape.pulsecheck_usb import (
    AVERAGES,
    RESOLUTIONS,
    BusyStatus,
    DataError,
    FirmwareError,
    InitializationStatus,
    OperationStatus,
)

#: Settings the tests below write, and which are restored when they are done.
RESTORED_SETTINGS = ("measurement_running", "autogain_enabled", "averages", "resolution",
                     "fit_type", "filter_enabled", "gain", "sensitivity")


@pytest.fixture(scope="module")
def instrument(connected_device_address):
    inst = PulseCheckUSB(connected_device_address)
    settings = {name: getattr(inst, name) for name in RESTORED_SETTINGS}
    yield inst
    for name, value in settings.items():
        assert set_and_read(inst, name, value, timeout=20) == value, f"could not restore {name}"


def set_and_read(instrument, name, value, timeout=5):
    """Write a property and read it back, waiting for the software to apply the setting.

    The detector settings reach the controller only once a further command arrives, so the
    value is written repeatedly instead of only being polled.

    :param instrument: the instrument to write to.
    :param name: name of the property.
    :param value: value to write.
    :param timeout: how long to wait for the read back to agree, in s.
    :returns: the value read back.
    """
    deadline = time.monotonic() + timeout
    while True:
        setattr(instrument, name, value)
        time.sleep(0.5)
        read_back = getattr(instrument, name)
        if read_back == value or time.monotonic() > deadline:
            return read_back


def running_with_signal(instrument, timeout=10):
    """Start a measurement and skip the test if the software has no valid autocorrelation.

    :param instrument: the instrument to measure with.
    :param timeout: how long to wait for valid data, in s.
    """
    instrument.measurement_running = True
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            _ = instrument.acf
            return
        except ValueError:
            time.sleep(1)
    pytest.skip(f"no valid autocorrelation ({instrument.data_errors!r}), is a laser connected?")


def test_id(instrument):
    assert instrument.id.startswith("APE")


def test_system_information(instrument):
    assert instrument.device_name
    assert instrument.serial_number.startswith("S")
    assert instrument.software_version
    assert instrument.hardware_version
    assert instrument.firmware_version
    assert instrument.motor_type


def test_status_registers(instrument):
    assert isinstance(instrument.operation_status, OperationStatus)
    assert isinstance(instrument.initialization_status, InitializationStatus)
    assert isinstance(instrument.busy_status, BusyStatus)
    assert isinstance(instrument.data_errors, DataError)
    assert isinstance(instrument.firmware_errors, FirmwareError)


def test_device_initialized(instrument):
    assert InitializationStatus.LINK_OK in instrument.initialization_status
    assert OperationStatus.DISCONNECTED not in instrument.operation_status


def test_check_errors(instrument):
    assert isinstance(instrument.check_errors(), list)


@pytest.mark.parametrize("averages", AVERAGES)
def test_averages(instrument, averages):
    assert set_and_read(instrument, "averages", averages) == averages


@pytest.mark.parametrize("resolution", RESOLUTIONS)
def test_resolution(instrument, resolution):
    assert set_and_read(instrument, "resolution", resolution) == resolution


@pytest.mark.parametrize("fit_type", ["none", "gaussian", "sech2", "lorentz"])
def test_fit_type(instrument, fit_type):
    assert set_and_read(instrument, "fit_type", fit_type) == fit_type


@pytest.mark.parametrize("enabled", [True, False])
def test_filter_enabled(instrument, enabled):
    assert set_and_read(instrument, "filter_enabled", enabled) is enabled


@pytest.mark.parametrize("gain", [500, 660])
def test_gain(instrument, gain):
    instrument.autogain_enabled = False
    assert set_and_read(instrument, "gain", gain) == gain


def test_gain_out_of_range(instrument):
    with pytest.raises(ValueError):
        instrument.gain = 1001


@pytest.mark.parametrize("sensitivity", [10, 1])
def test_sensitivity(instrument, sensitivity):
    # the software hands a new sensitivity to the detector only while it is measuring,
    # and takes several seconds to do so
    instrument.measurement_running = True
    time.sleep(1)
    assert set_and_read(instrument, "sensitivity", sensitivity, timeout=20) == sensitivity


@pytest.mark.parametrize("running", [True, False])
def test_measurement_running(instrument, running):
    assert set_and_read(instrument, "measurement_running", running) is running


def test_scan_range(instrument):
    assert instrument.scan_range in (0, 150e-15, 500e-15, 1.5e-12, 5e-12, 15e-12,
                                     50e-12, 150e-12)


def test_trigger(instrument):
    assert 0.2 <= instrument.trigger_level <= 5
    assert 1e-6 <= instrument.trigger_delay <= 50e-6
    assert instrument.trigger_frequency >= 0
    assert instrument.trigger_impedance > 0


def test_shutters(instrument):
    assert isinstance(instrument.fix_shutter_open, bool)
    assert isinstance(instrument.scan_shutter_open, bool)


def test_crystal(instrument):
    assert 500 <= instrument.crystal_position <= 11000
    assert isinstance(instrument.crystal_moving, bool)
    assert instrument.crystal_type


def test_unsupported_scpi_commands(instrument):
    """The software answers "Parser error" to the standard commands it does not implement."""
    with pytest.raises(ValueError):
        _ = instrument.options
    with pytest.raises(ValueError):
        _ = instrument.next_error


def test_acf_without_measurement(instrument):
    instrument.measurement_running = False
    time.sleep(1)
    with pytest.raises(ValueError, match="measurement"):
        _ = instrument.acf


def test_acf(instrument):
    running_with_signal(instrument)
    delay, intensity = instrument.acf

    assert len(delay) == len(intensity)
    assert len(delay) == instrument.resolution
    # the delay axis has to come out sorted, otherwise the two interleaved arrays are swapped
    assert np.all(np.diff(delay) > 0)
    assert max(abs(delay)) <= instrument.scan_range


def test_displayed_acf(instrument):
    running_with_signal(instrument)
    delay, intensity = instrument.displayed_acf

    assert len(delay) == len(intensity)
    assert np.all(np.diff(delay) > 0)


def test_acf_mean_data(instrument):
    running_with_signal(instrument)
    mean_data = instrument.acf_mean_data

    assert set(mean_data) == {"average", "delay_max", "delay_min",
                              "intensity_max", "intensity_min"}
    assert mean_data["delay_min"] < mean_data["delay_max"]
    assert mean_data["intensity_min"] <= mean_data["intensity_max"]


def test_fwhm(instrument):
    running_with_signal(instrument)
    assert 0 < instrument.fwhm < instrument.scan_range


def test_fit_fwhm(instrument):
    running_with_signal(instrument)
    instrument.fit_type = "gaussian"
    time.sleep(2)
    assert 0 < instrument.fit_fwhm < instrument.scan_range
