#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

import logging
from time import sleep

import numpy
import pytest

from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.hp import HP8753E

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


@pytest.fixture(scope="module")
def hp8753e(connected_device_address):
    try:
        # This allows a PrologixAdapter to be used for running the tests as well
        #  `pytest --device-address PrologixAdapter,ASRL4::INSTR,16 -k "test_hp8753e_with_device"`

        if "PrologixAdapter" not in connected_device_address:
            vna = HP8753E(connected_device_address)
        else:
            _, prologix_address, gpib_address, *other_address_info = connected_device_address.split(
                ","
            )

            prologix = PrologixAdapter(
                resource_name=prologix_address,
                visa_library="@py",
                auto=1,
                address=gpib_address,
            )

            # need to ensure `eot_enable` is set to zero otherwise you will have to read twice to
            # get rid of the extra new line character
            prologix.write("++eot_enable 0")
            vna = HP8753E(adapter=prologix)

    except IOError:
        print("Not able to connect to vna")
        assert False

    yield vna
    del vna


def test_init_HP8753E(hp8753e):
    hp8753e.reset()
    hp8753e.emit_beep()


def test_hp8753e_with_device_id(hp8753e):
    assert hp8753e.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]


def test_hp8753e_with_device_name(hp8753e):
    assert hp8753e.name == "HEWLETT PACKARD 8753E Vector Network Analyzer"


def test_hp8753e_with_device_fw(hp8753e):
    hp8753e._fw = ""
    assert hp8753e.fw == "7.10"


def test_hp8753e_with_device_manu(hp8753e):
    hp8753e._manu = ""
    assert hp8753e.manu == "HEWLETT PACKARD"


def test_hp8753e_with_device_model(hp8753e):
    hp8753e._model = ""
    assert hp8753e.model == "8753E"


def test_hp8753e_with_device_sn(hp8753e):
    assert hp8753e.sn == "US37390178"


def test_hp8753e_with_device_options(hp8753e):
    assert hp8753e.options == "1D5 002 006 010"


def test_hp8753e_with_device_sweep_time(hp8753e):
    hp8753e.reset()
    assert hp8753e.sweep_time == 0.175000059904
    hp8753e.sweep_time = 1
    assert hp8753e.sweep_time == 1.00000006144
    hp8753e.set_sweep_time_fastest()
    assert hp8753e.sweep_time == 0


def test_hp8753e_with_device_measuring_parameters(hp8753e):
    for parameter in hp8753e.MEASURING_PARAMETER_MAP:
        hp8753e.measuring_parameter = parameter
        assert hp8753e.measuring_parameter == parameter

    assert hp8753e.MEASURING_PARAMETER_MAP == {
        "S11": "S11",
        "S12": "S12",
        "S21": "S21",
        "S22": "S22",
        "A/R": "AR",
        "B/R": "BR",
        "A/B": "AB",
        "A": "MEASA",
        "B": "MEASB",
        "R": "MEASR",
    }


def test_hp8753e_with_device_scan_points(hp8753e):
    for points in hp8753e.SCAN_POINT_VALUES:
        hp8753e.scan_points = points
        assert hp8753e.scan_points == points


def test_hp8753e_with_device_ifbw(hp8753e):
    for allowed_bandwidth in hp8753e.ALLOWED_BANDWIDTH:
        hp8753e.IFBW = allowed_bandwidth
        assert hp8753e.IFBW == allowed_bandwidth

    hp8753e.IFBW = 1000
    assert hp8753e.IFBW == 1000


def test_hp8753e_with_device_start_frequency(hp8753e):
    hp8753e.start_frequency = 30_000.0
    assert hp8753e.start_frequency == 30_000.0
    hp8753e.start_frequency = 30_600.0
    assert hp8753e.start_frequency == 30_600.0
    hp8753e.start_frequency = 4_000_000.0
    assert hp8753e.start_frequency == 4_000_000.0


def test_hp8753e_with_device_stop_frequency(hp8753e):
    hp8753e.stop_frequency = 130_000.0
    assert hp8753e.stop_frequency == 130_000.0
    hp8753e.stop_frequency = 130_600.0
    assert hp8753e.stop_frequency == 130_600.0
    hp8753e.stop_frequency = 14_000_000.0
    assert hp8753e.stop_frequency == 14_000_000.0


def test_hp8753e_with_device_center_and_span_frequency(hp8753e):
    hp8753e.reset()
    assert hp8753e.start_frequency == 30_000.0
    assert hp8753e.stop_frequency == 6_000_000_000.0

    cent_freqs = [30_000, 120_306, 35_890_230, 385_239_000, 2_150_932_000, 5_907_600_000, 6e9]
    spans = [20000, 523459, 125033000, 250_000_000, 3_000_000_000, 5e9]

    for freq in cent_freqs:
        for span in spans:
            if freq - span / 2 >= 30e3 and freq + span / 2 <= 6e9:
                hp8753e.center_frequency = freq
                hp8753e.span_frequency = span
                assert hp8753e.span_frequency == span
                assert hp8753e.center_frequency == freq


def test_hp8753e_with_device_set_single_frequency_scan(hp8753e):
    for frequency in [30_000, 1_000_000, 500_000_000, 4_000_000_000, 6_000_000_000]:
        hp8753e.set_single_frequency_scan(frequency)
        assert hp8753e.start_frequency == frequency
        assert hp8753e.stop_frequency == frequency
        assert hp8753e.scan_points == 3


def test_hp8753e_with_device_scan_single(hp8753e):
    assert hp8753e.averaging_enabled is False
    hp8753e.scan_single()
    data = hp8753e.data_complex
    assert isinstance(data, numpy.ndarray)
    assert isinstance(data[12], numpy.complex128)
    hp8753e.averaging_enabled = True
    assert hp8753e.averaging_enabled is True
    hp8753e.averages = 2
    assert hp8753e.averages == 2
    hp8753e.scan_single()
    data = hp8753e.data_complex
    assert isinstance(data, numpy.ndarray)
    assert isinstance(data[12], numpy.complex128)


def test_hp8753e_with_device_scan(hp8753e):
    hp8753e.reset()
    hp8753e.averaging_enabled = False
    hp8753e.scan(timeout=10)
    hp8753e.averaging_enabled = True
    assert hp8753e.averaging_enabled is True
    hp8753e.averages = 2
    assert hp8753e.averages == 2
    hp8753e.scan(timeout=10)
    data = hp8753e.data_complex
    assert isinstance(data, numpy.ndarray)
    assert isinstance(data[12], numpy.complex128)


def test_hp8753e_with_device_data_complex(hp8753e):
    hp8753e.reset()
    assert hp8753e.averaging_enabled is False
    hp8753e.trigger_continuous = True
    assert hp8753e.trigger_continuous is True
    hp8753e.scan_single()

    data = hp8753e.data_complex
    assert len(data) == 201
    assert isinstance(data, numpy.ndarray)
    assert isinstance(data[12], numpy.complex128)

    # repeat with average of 2 enabled
    hp8753e.trigger_hold = True
    assert hp8753e.trigger_hold is True
    hp8753e.averaging_enabled = True
    assert hp8753e.averaging_enabled is True
    hp8753e.averages = 4
    assert hp8753e.averages == 4
    hp8753e.averaging_restart()
    hp8753e.scan(timeout=20)

    data = hp8753e.data_complex
    assert len(data) == 201
    assert isinstance(data, numpy.ndarray)
    assert isinstance(data[12], numpy.complex128)


def test_hp8753e_with_device_np_frequencies(hp8753e):
    hp8753e.reset()
    numpy.testing.assert_equal(
        hp8753e.frequencies, numpy.arange(30e3, 6e9 + (6e9 - 30e3) / 200, (6e9 - 30e3) / 200)
    )


def test_hp8753e_with_device_reset(hp8753e):
    frequency = 500_000_000
    hp8753e.set_single_frequency_scan(frequency)
    assert hp8753e.start_frequency == frequency
    assert hp8753e.stop_frequency == frequency
    assert hp8753e.scan_points == 3
    hp8753e.reset()
    assert hp8753e.start_frequency == 30_000
    assert hp8753e.stop_frequency == 6_000_000_000
    assert hp8753e.scan_points == 201


def test_hp8753e_with_device_averaging_enabled(hp8753e):

    hp8753e.averaging_enabled = True
    assert hp8753e.averaging_enabled is True
    hp8753e.averaging_enabled = False
    assert hp8753e.averaging_enabled is False


def test_hp8753e_with_device_averages(hp8753e):

    hp8753e.averaging_enabled = True
    hp8753e.averages = 32
    assert hp8753e.averages == 32
    hp8753e.averages = 18
    assert hp8753e.averages == 18
    hp8753e.averages = 1
    assert hp8753e.averages == 1
    hp8753e.averaging_enabled = False


@pytest.mark.skip(
    reason="This test will wear out the mechanical relays and should be run only as necessary"
)
def test_hp8753e_with_device_power(hp8753e):

    hp8753e.reset()
    assert hp8753e.output_enabled is True
    powers = [-60.14, -28.76, 5.41, 0.35]
    for power in powers:
        hp8753e.power = power
        assert hp8753e.power == power
        sleep(0.3)

    hp8753e.power = 0.0
    assert hp8753e.power == 0.0

    # test power input < -70

    # test power input > 10

    hp8753e.shutdown()


@pytest.mark.skip(
    reason="This test will wear out the mechanical relays and should be run only as necessary"
)
def test_hp8753e_with_device_output_enabled(hp8753e):

    hp8753e.reset()
    assert hp8753e.power == 0
    assert hp8753e.output_enabled is True
    hp8753e.output_enabled = False
    assert hp8753e.output_enabled is False
    hp8753e.output_enabled = True
    assert hp8753e.output_enabled is True
    hp8753e.shutdown()
    assert hp8753e.output_enabled is False


def test_hp8753e_with_device_trigger(hp8753e):
    hp8753e.reset()
    assert hp8753e.trigger_continuous is True

    hp8753e.trigger_hold = True
    assert hp8753e.trigger_hold is True
    assert hp8753e.trigger_continuous is False

    hp8753e.trigger_hold = False
    assert hp8753e.trigger_hold is False
    assert hp8753e.trigger_continuous is True

    hp8753e.trigger_continuous = True
    assert hp8753e.trigger_continuous is True
    assert hp8753e.trigger_hold is False

    hp8753e.trigger_continuous = False
    assert hp8753e.trigger_continuous is False
    assert hp8753e.trigger_hold is True

    hp8753e.reset()
