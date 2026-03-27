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

# Call signature:
# $ pytest test_keysightPNA_with_device.py --device-address "GPIB0::16::INSTR"
# $ pytest test_keysightPNA_with_device.py --device-address "TCPIP0::192.168.50.2::INSTR"
# The given device addresses are just examples. Please exchanged them to your own address.

# Requirements for the PNA:
# Channel 1 and trace 1 exist after reset.
# This is the default case if Preset is set to Factory Preset.


import pytest
import numpy as np
from pymeasure.instruments.keysight.keysightPNA import KeysightPNA


############
# FIXTURES #
############


@pytest.fixture
def keysightPNA_default(connected_device_address):
    instr = KeysightPNA(connected_device_address)
    return instr


@pytest.fixture(scope="module")
def keysightPNA(connected_device_address):
    instr = KeysightPNA(connected_device_address, timeout=10000)
    instr.clear()
    instr.reset()  # also resets data_format to ascii
    instr.complete
    assert [] == instr.check_errors()
    return instr


class TestKeysightPNA:
    def test_defaults(self, keysightPNA_default):
        assert "real64" == keysightPNA_default.data_format
        assert keysightPNA_default.byte_order_swapped is True

    def test_abort(self, keysightPNA):
        keysightPNA.abort()
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("byte_order_swapped", [False, True])
    def test_byte_order(self, keysightPNA, byte_order_swapped):
        initial_byte_order_swapped = keysightPNA.byte_order_swapped
        keysightPNA.byte_order_swapped = byte_order_swapped
        assert byte_order_swapped == keysightPNA.byte_order_swapped
        keysightPNA.byte_order_swapped = initial_byte_order_swapped
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("data_format", ["ascii", "real32", "real64"])
    def test_data_format(self, keysightPNA, data_format):
        keysightPNA.data_format = data_format
        assert data_format == keysightPNA.data_format
        assert [] == keysightPNA.check_errors()

    def test_measurement_channels(self, keysightPNA):
        assert 1 in keysightPNA.measurement_channels
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("output_enabled", [True, False])
    def test_output_enabled(self, keysightPNA, output_enabled):
        keysightPNA.output_enabled = output_enabled
        assert output_enabled == keysightPNA.output_enabled
        assert [] == keysightPNA.check_errors()


class TestMeasurementChannel:
    def test_hold(self, keysightPNA):
        keysightPNA.ch_1.hold()
        assert [] == keysightPNA.check_errors()

    def test_single(self, keysightPNA):
        keysightPNA.ch_1.single()
        keysightPNA.complete
        assert [] == keysightPNA.check_errors()

    def test_continuous(self, keysightPNA):
        keysightPNA.ch_1.continuous()
        assert [] == keysightPNA.check_errors()

    def test_number_of_points(self, keysightPNA):
        number_of_points = keysightPNA.ch_1.number_of_points
        assert type(number_of_points) is int
        assert number_of_points > 0
        assert [] == keysightPNA.check_errors()

    def test_measurements(self, keysightPNA):
        measurements = keysightPNA.ch_1.measurements
        assert type(measurements) is list
        assert [] == keysightPNA.check_errors()


class TestTrace:
    def test_parameter(self, keysightPNA):
        got = keysightPNA.ch_1.tr_1.parameter
        assert type(got) is str
        assert [] == keysightPNA.check_errors()

    def test_x_data(self, keysightPNA):
        x_data = keysightPNA.ch_1.tr_1.x_data
        assert type(x_data) is np.ndarray
        assert [] == keysightPNA.check_errors()

    def test_x_unit(self, keysightPNA):
        x_unit = keysightPNA.ch_1.tr_1.x_unit
        assert x_unit in ["FREQ", "POW", "PHAS", "DC", "POIN", "DEF"]
        assert [] == keysightPNA.check_errors()

    def test_y_data(self, keysightPNA):
        y_data = keysightPNA.ch_1.tr_1.y_data
        assert type(y_data) is np.ndarray
        assert [] == keysightPNA.check_errors()

    def test_y_data_complex(self, keysightPNA):
        y_data = keysightPNA.ch_1.tr_1.y_data_complex
        assert type(y_data) is np.ndarray
        assert y_data.ndim == 2
        assert [] == keysightPNA.check_errors()

    def test_y_unit(self, keysightPNA):
        y_unit = keysightPNA.ch_1.tr_1.y_unit
        assert y_unit in [
            "HZ", "SEC", "MIN", "HOUR", "DAY", "DB", "DBM", "DBMV", "WATT", "FAR", "HENR",
            "OHM", "MHO", "SIEM", "VOLT", "DEGR", "RAD", "MET", "DPHZ", "UNIT", "NON",
            "TNOR", "NTEM", "KELV", "CENT", "FAHR", "FEET", "INCH",
            "DBMAAMP", "VOLTA", "DBUV", "PERC", "DMVR", "DUVR", "DMAR",
            "WPHZ", "VRO", "ARO", "DBC", "DVP", "DCP", "DBP", "HZP", "PRH",
            "VPH", "DBV", "DEF"
            ]
        assert [] == keysightPNA.check_errors()


@pytest.mark.parametrize("marker", range(1, 16))
class TestMarker:
    # keep marker activated for the following tests
    def test_enabled_true(self, keysightPNA, marker):
        keysightPNA.ch_1.tr_1.markers[marker].enabled = True
        assert keysightPNA.ch_1.tr_1.markers[marker].enabled

    @pytest.mark.parametrize("is_discrete", [True, False])
    def test_is_discrete(self, keysightPNA, marker, is_discrete):
        keysightPNA.ch_1.tr_1.markers[marker].is_discrete = is_discrete
        assert is_discrete == keysightPNA.ch_1.tr_1.markers[
            marker].is_discrete

    @pytest.mark.parametrize("x", [100E6, 2.458E9])
    def test_x(self, keysightPNA, marker, x):
        keysightPNA.ch_1.tr_1.markers[marker].x = x
        assert x == keysightPNA.ch_1.tr_1.markers[marker].x

    def test_y(self, keysightPNA, marker):
        y = keysightPNA.ch_1.tr_1.markers[marker].y
        assert 2 == len(y)
        assert type(y[0]) is float
        assert type(y[1]) is float

    # finally disable the marker
    def test_enabled_false(self, keysightPNA, marker):
        keysightPNA.ch_1.tr_1.markers[marker].enabled = False
        assert not keysightPNA.ch_1.tr_1.markers[marker].enabled
