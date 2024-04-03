#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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
from contextlib import contextmanager
from time import sleep

import numpy
import pytest
from pyvisa.errors import VisaIOError

from pymeasure.adapters import PrologixAdapter
from pymeasure.instruments.hp import HP8753E

pytest.skip("Only works with connected hardware", allow_module_level=True)


@contextmanager
def init_prologix_adapter():
    try:
        prologix = PrologixAdapter(
            resource_name="ASRL4::INSTR",
            address=16,
            visa_library="@py",
            auto=1,
        )
        yield prologix
    except ValueError as e:
        raise (ValueError(e))
    finally:
        prologix.close()
        del prologix


@contextmanager
def init_HP8753E(**kwargs):
    with init_prologix_adapter() as prologix:
        vna = HP8753E(adapter=prologix, **kwargs)
        yield vna
        del vna


def test_sanity():
    assert 1 + 1 == 2


def test_init_prologix_adapter():
    with init_prologix_adapter() as prologix:
        test_sanity()


def test_init_HP8753E():
    with init_HP8753E() as hp8753e:
        test_sanity()
        hp8753e.reset()
        hp8753e.emit_beep()


def test_hp8753e_id():
    with init_HP8753E() as hp8753e:
        assert hp8753e.id == ["HEWLETT PACKARD", "8753E", "0", "7.10"]


def test_hp8753e_name():
    with init_HP8753E() as hp8753e:
        assert hp8753e.name == "HEWLETT PACKARD 8753E Vector Network Analyzer"

    with init_HP8753E(name="Something snarky") as hp8753e:
        assert hp8753e.name == "Something snarky"


def test_hp8753e_fw():
    with init_HP8753E() as hp8753e:
        hp8753e._fw = ""
        assert hp8753e.fw == "7.10"


def test_hp8753e_manu():
    with init_HP8753E() as hp8753e:
        hp8753e._manu = ""
        assert hp8753e.manu == "HEWLETT PACKARD"


def test_hp8753e_model():
    with init_HP8753E() as hp8753e:
        hp8753e._model = ""
        assert hp8753e.model == "8753E"


def test_hp8753e_sn():
    with init_HP8753E() as hp8753e:
        assert hp8753e.sn == "US37390178"


def test_hp8753e_options():
    with init_HP8753E() as hp8753e:
        assert hp8753e.options == "1D5 002 006 010"


def test_hp8753e_sweep_time():
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        assert hp8753e.sweep_time == 0.175000059904
        hp8753e.sweep_time = 1
        assert hp8753e.sweep_time == 1.00000006144
        hp8753e.set_sweep_time_fastest()
        assert hp8753e.sweep_time == 0


def test_hp8753e_measuring_parameters():
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        for parameter in hp8753e.MEASURING_PARAMETERS:
            hp8753e.measuring_parameter = parameter
            assert hp8753e.measuring_parameter == parameter

        assert hp8753e.MEASURING_PARAMETERS == [
            "S11",
            "S12",
            "S21",
            "S22",
            "A/R",
            "B/R",
            "A/B",
            "A",
            "B",
            "R",
        ]


def test_hp8753e_scan_points():
    with init_HP8753E() as hp8753e:
        for points in hp8753e.SCAN_POINT_VALUES:
            hp8753e.scan_points = points
            assert hp8753e.scan_points == points


def test_hp8753e_ifbw():
    with init_HP8753E() as hp8753e:
        for allowed_bandwidth in hp8753e.ALLOWED_BANDWIDTH:
            hp8753e.IFBW = allowed_bandwidth
            assert hp8753e.IFBW == allowed_bandwidth

        hp8753e.IFBW = 1000
        assert hp8753e.IFBW == 1000


def test_hp8753e_start_frequency():
    with init_HP8753E() as hp8753e:
        hp8753e.start_frequency = 30_000.0
        assert hp8753e.start_frequency == 30_000.0
        hp8753e.start_frequency = 30_600.0
        assert hp8753e.start_frequency == 30_600.0
        hp8753e.start_frequency = 4_000_000.0
        assert hp8753e.start_frequency == 4_000_000.0


def test_hp8753e_stop_frequency():
    with init_HP8753E() as hp8753e:
        hp8753e.stop_frequency = 130_000.0
        assert hp8753e.stop_frequency == 130_000.0
        hp8753e.stop_frequency = 130_600.0
        assert hp8753e.stop_frequency == 130_600.0
        hp8753e.stop_frequency = 14_000_000.0
        assert hp8753e.stop_frequency == 14_000_000.0


def test_hp8753e_center_and_span_frequency():
    with init_HP8753E() as hp8753e:
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


def test_hp8753e_set_fixed_frequency():
    with init_HP8753E() as hp8753e:
        for frequency in [30_000, 1_000_000, 500_000_000, 4_000_000_000, 6_000_000_000]:
            hp8753e.set_fixed_frequency(frequency)
            assert hp8753e.start_frequency == frequency
            assert hp8753e.stop_frequency == frequency
            assert hp8753e.scan_points == 3


def test_hp8753e_scan_single():
    with init_HP8753E() as hp8753e:
        hp8753e.scan_single()


def test_hp8753e_scan():
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        # with and without averaging
        hp8753e.averaging_enabled = False
        hp8753e.scan()
        hp8753e.averaging_enabled = True
        hp8753e.averages = 2
        hp8753e.scan(timeout=50)


def test_hp8753e_data_complex():
    sleep(3)
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        hp8753e.trigger_continuous = True
        hp8753e.scan_single()
        data = hp8753e.data_complex
        assert len(data) == 201
        assert isinstance(data, numpy.ndarray)
        assert isinstance(data[12], numpy.complex128)

        # repeat with average of 2 enabled
        hp8753e.trigger_hold = True
        assert hp8753e.averaging_enabled is False
        hp8753e.averaging_enabled = True
        hp8753e.averages = 2
        assert hp8753e.averages == 2

        assert hp8753e.averaging_enabled is True

        hp8753e.averaging_restart()
        hp8753e.scan()

        data = hp8753e.data_complex
        assert len(data) == 201
        assert isinstance(data, numpy.ndarray)
        assert isinstance(data[12], numpy.complex128)


def test_hp8753e_np_frequencies():
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        numpy.testing.assert_equal(
            hp8753e.frequencies, numpy.arange(30e3, 6e9 + (6e9 - 30e3) / 200, (6e9 - 30e3) / 200)
        )


def test_hp8753e_reset():
    with init_HP8753E() as hp8753e:
        frequency = 500_000_000
        hp8753e.set_fixed_frequency(500_000_000)
        assert hp8753e.start_frequency == frequency
        assert hp8753e.stop_frequency == frequency
        assert hp8753e.scan_points == 3
        hp8753e.reset()
        assert hp8753e.start_frequency == 30_000
        assert hp8753e.stop_frequency == 6_000_000_000
        assert hp8753e.scan_points == 201


def test_hp8753e_averaging_enabled():
    with init_HP8753E() as hp8753e:
        hp8753e.averaging_enabled = True
        assert hp8753e.averaging_enabled is True
        hp8753e.averaging_enabled = False
        assert hp8753e.averaging_enabled is False

        hp8753e.averaging_enabled = "ON"
        assert hp8753e.averaging_enabled is True
        hp8753e.averaging_enabled = "OFF"
        assert hp8753e.averaging_enabled is False

        hp8753e.averaging_enabled = "1"
        assert hp8753e.averaging_enabled is True
        hp8753e.averaging_enabled = "0"
        assert hp8753e.averaging_enabled is False


def test_hp8753e_averages():
    with init_HP8753E() as hp8753e:
        hp8753e.averaging_enabled = True
        hp8753e.averages = 32
        assert hp8753e.averages == 32
        hp8753e.averages = 18
        assert hp8753e.averages == 18
        hp8753e.averages = 1
        assert hp8753e.averages == 1
        hp8753e.averaging_enabled = False


# this test will wear out the mechanical relays and should be run only as necessary
@pytest.mark.skip
def test_hp8753e_power():
    with init_HP8753E() as hp8753e:
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


# this test will wear out the mechanical relays and should be run only as necessary
@pytest.mark.skip
def test_hp8753e_output_enabled():
    with init_HP8753E() as hp8753e:
        hp8753e.reset()
        assert hp8753e.power == 0
        assert hp8753e.output_enabled is True
        hp8753e.output_enabled = False
        assert hp8753e.output_enabled is False
        hp8753e.output_enabled = True
        assert hp8753e.output_enabled is True
        hp8753e.shutdown()
        assert hp8753e.output_enabled is False


def test_hp8753e_trigger():
    with init_HP8753E() as hp8753e:
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
