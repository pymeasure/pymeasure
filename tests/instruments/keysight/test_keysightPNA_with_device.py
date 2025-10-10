#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
# The following state state file exists: 'D:/States/PyMeasurePytest.csa'
# This state meets the following conditions:
#  - Active channels: 1, 2, 5
#  - Trace numbers in channel 1: 1 (S11), 2 (S22), 4 (A,1)
#  - Trace numbers in channel 2: 3 (R1,1), 5 (S21), 6 (b2,2)
#  - Trace numbers in channel 5: 7 (S12)


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
    instr.load_state("D:/States/PyMeasurePytest.csa")
    instr.complete
    assert [] == instr.check_errors()
    return instr


class TestAttributeError:
    def test_undefined_channel(self, keysightPNA):
        with pytest.raises(AttributeError):
            measurements = keysightPNA.ch_3.measurements
            assert [1, 2] == measurements

    def test_undefined_trace(self, keysightPNA):
        with pytest.raises(AttributeError):
            unit = keysightPNA.ch_1.tr_3.x_unit
            assert "FREQ" == unit


class TestKeysightPNA:
    def test_defaults(self, keysightPNA_default):
        assert "real64" == keysightPNA_default.data_format
        assert "swapped" == keysightPNA_default.byte_order

    def test_abort(self, keysightPNA):
        keysightPNA.abort()
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("byte_order", ["normal", "swapped"])
    def test_byte_order(self, keysightPNA, byte_order):
        initial_byte_order = keysightPNA.byte_order
        keysightPNA.byte_order = byte_order
        assert byte_order == keysightPNA.byte_order
        keysightPNA.byte_order = initial_byte_order
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("data_format", ["ascii", "real32", "real64"])
    def test_data_format(self, keysightPNA, data_format):
        keysightPNA.data_format = data_format
        assert data_format == keysightPNA.data_format
        assert [] == keysightPNA.check_errors()

    def test_measurement_channels(self, keysightPNA):
        assert [1, 2, 5] == keysightPNA.measurement_channels
        assert [] == keysightPNA.check_errors()

    @pytest.mark.parametrize("output_enabled", [True, False])
    def test_output_enabled(self, keysightPNA, output_enabled):
        keysightPNA.output_enabled = output_enabled
        assert output_enabled == keysightPNA.output_enabled
        assert [] == keysightPNA.check_errors()


@pytest.mark.parametrize("channel", [1, 2, 5])
class TestMeasurementChannel:
    def test_hold(self, keysightPNA, channel):
        keysightPNA.channels[channel].hold()
        assert [] == keysightPNA.check_errors()

    def test_single(self, keysightPNA, channel):
        keysightPNA.channels[channel].single()
        keysightPNA.complete
        assert [] == keysightPNA.check_errors()

    def test_continuous(self, keysightPNA, channel):
        keysightPNA.channels[channel].continuous()
        assert [] == keysightPNA.check_errors()

    def test_number_of_points(self, keysightPNA, channel):
        number_of_points = keysightPNA.channels[channel].number_of_points
        assert type(number_of_points) is int
        assert number_of_points > 0
        assert [] == keysightPNA.check_errors()

    def test_measurements(self, keysightPNA, channel):
        measurements = keysightPNA.channels[channel].measurements
        assert type(measurements) is list
        assert [] == keysightPNA.check_errors()


@pytest.mark.parametrize("channel, trace, parameter",
                         [(1, 1, "S11"),
                          (1, 2, "S22"),
                          (1, 4, "A,1"),
                          (2, 3, "R1,1"),
                          (2, 5, "S21"),
                          (2, 6, "b2,2"),
                          (5, 7, "S12"),
                          ])
class TestTrace:
    def test_parameter(self, keysightPNA, channel, trace, parameter):
        got = keysightPNA.channels[channel].traces[trace].parameter
        assert parameter == got
        assert [] == keysightPNA.check_errors()

    def test_x_data(self, keysightPNA, channel, trace, parameter):
        x_data = keysightPNA.channels[channel].traces[trace].x_data
        assert type(x_data) is np.ndarray
        assert [] == keysightPNA.check_errors()

    def test_x_unit(self, keysightPNA, channel, trace, parameter):
        x_unit = keysightPNA.channels[channel].traces[trace].x_unit
        assert x_unit in ["FREQ", "POW", "PHAS", "DC", "POIN", "DEF"]
        assert [] == keysightPNA.check_errors()

    def test_y_data(self, keysightPNA, channel, trace, parameter):
        y_data = keysightPNA.channels[channel].traces[trace].y_data
        assert type(y_data) is np.ndarray
        assert [] == keysightPNA.check_errors()

    def test_y_data_complex(self, keysightPNA, channel, trace, parameter):
        y_data = keysightPNA.channels[channel].traces[trace].y_data_complex
        assert type(y_data) is np.ndarray
        assert y_data.ndim == 2
        assert [] == keysightPNA.check_errors()

    def test_y_unit(self, keysightPNA, channel, trace, parameter):
        y_unit = keysightPNA.channels[channel].traces[trace].y_unit
        assert y_unit in [
            "HZ", "SEC", "MIN", "HOUR", "DAY", "DB", "DBM", "DBMV", "WATT", "FAR", "HENR",
            "OHM", "MHO", "SIEM", "VOLT", "DEGR", "RAD", "MET", "DPHZ", "UNIT", "NON",
            "TNOR", "NTEM", "KELV", "CENT", "FAHR", "FEET", "INCH",
            "DBMAAMP", "VOLTA", "DBUV", "PERC", "DMVR", "DUVR", "DMAR",
            "WPHZ", "VRO", "ARO", "DBC", "DVP", "DCP", "DBP", "HZP", "PRH",
            "VPH", "DBV", "DEF"
            ]
        assert [] == keysightPNA.check_errors()


@pytest.mark.parametrize("channel, trace",
                         [(1, 1),
                          (1, 2),
                          (1, 4),
                          (2, 3),
                          (2, 5),
                          (2, 6),
                          (5, 7),
                          ])
@pytest.mark.parametrize("marker", range(1, 16))
class TestMarker:
    # keep marker activated for the following tests
    def test_enabled_true(self, keysightPNA, channel, trace, marker):
        keysightPNA.channels[channel].traces[trace].markers[marker].enabled = True
        assert keysightPNA.channels[channel].traces[trace].markers[marker].enabled

    @pytest.mark.parametrize("is_discrete", [True, False])
    def test_is_discrete(self, keysightPNA, channel, trace, marker, is_discrete):
        keysightPNA.channels[channel].traces[trace].markers[marker].is_discrete = is_discrete
        assert is_discrete == keysightPNA.channels[channel].traces[trace].markers[
            marker].is_discrete

    @pytest.mark.parametrize("x", [100E6, 2.458E9])
    def test_x(self, keysightPNA, channel, trace, marker, x):
        keysightPNA.channels[channel].traces[trace].markers[marker].x = x
        assert x == keysightPNA.channels[channel].traces[trace].markers[marker].x

    def test_y(self, keysightPNA, channel, trace, marker):
        y = keysightPNA.channels[channel].traces[trace].markers[marker].y
        assert 2 == len(y)
        assert type(y[0]) is float
        assert type(y[1]) is float

    # finally disable the marker
    def test_enabled_false(self, keysightPNA, channel, trace, marker):
        keysightPNA.channels[channel].traces[trace].markers[marker].enabled = False
        assert not keysightPNA.channels[channel].traces[trace].markers[marker].enabled
