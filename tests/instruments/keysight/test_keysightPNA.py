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

import pytest
import numpy as np

from pymeasure.test import expected_protocol
from pymeasure.instruments.keysight import KeysightPNA

# communication during class initialization:
# - set the data format to real64
# - use swapped byte order for data transfer
# - represent 1 channel with 1 trace
INITIALIZATION = [("FORM REAL,64", None),
                  ("FORM:BORD SWAP", None),
                  ("SYST:CHAN:CAT?", "1"),
                  ("SYST:MEAS:CAT? 1", "1"),
                  ]

UPDATE = [("SYST:CHAN:CAT?", "2"),
          ("SYST:MEAS:CAT? 2", "3"),
          ]

# binary data representing '1.e+7'
REAL32_DATA = b"\x80\x96\x18\x4b"
REAL64_DATA = b"\x00\x00\x00\x00\xd0\x12\x63\x41"


class TestAttributeError:
    def test_undefined_channel(self):
        with pytest.raises(AttributeError):
            with expected_protocol(
                KeysightPNA,
                INITIALIZATION + [
                 ("SYST:MEAS:CAT? 3", "6,8"),
                 ],
            ) as inst:
                assert [6, 8] == inst.ch_3.measurements

    def test_undefined_trace(self):
        with pytest.raises(AttributeError):
            with expected_protocol(
                KeysightPNA,
                INITIALIZATION + [
                 ("CALC1:MEAS3:X:AXIS:UNIT?", "FREQ"),
                 ],
            ) as inst:
                assert "FREQ" == inst.ch_1.tr_3.x_unit


class TestMarker:
    @pytest.mark.parametrize("enabled, mapping", [
                             (True, 1),
                             (False, 0),
                             ])
    def test_enabled(self, enabled, mapping):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"CALC1:MEAS1:MARK1:STATE {mapping}", None),
             ("CALC1:MEAS1:MARK1:STATE?", mapping),
             ],
        ) as inst:
            inst.ch_1.tr_1.mkr_1.enabled = enabled
            assert enabled == inst.ch_1.tr_1.mkr_1.enabled

    @pytest.mark.parametrize("is_discrete, mapping", [
                             (True, 1),
                             (False, 0),
                             ])
    def test_is_discrete(self, is_discrete, mapping):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"CALC1:MEAS1:MARK1:DISC {mapping}", None),
             ("CALC1:MEAS1:MARK1:DISC?", mapping),
             ],
        ) as inst:
            inst.ch_1.tr_1.mkr_1.is_discrete = is_discrete
            assert is_discrete == inst.ch_1.tr_1.mkr_1.is_discrete

    @pytest.mark.parametrize("x", [1, 1.4e7, -2.4])
    def test_x(self, x):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"CALC1:MEAS1:MARK1:X {x:f}", None),
             ("CALC1:MEAS1:MARK1:X?", x),
             ],
        ) as inst:
            inst.ch_1.tr_1.mkr_1.x = x
            assert x == inst.ch_1.tr_1.mkr_1.x

    def test_y(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("CALC1:MEAS1:MARK1:Y?", "2.3,-4.76E+2"),
             ],
        ) as inst:
            assert [2.3, -4.76E+2] == inst.ch_1.tr_1.mkr_1.y


class TestTrace:
    def test_parameter(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("CALC1:MEAS1:PAR?", '"S11"'),
             ],
        ) as inst:
            assert "S11" == inst.ch_1.tr_1.parameter

    def test_x_data_ascii(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", "ASC,0"),
             ("CALC1:MEAS1:X?", "1.2,3,5E+4"),
             ],
        ) as inst:
            x_data = inst.ch_1.tr_1.x_data
            assert type(x_data) is np.ndarray
            assert ["1.2", "3", "5E+4"] == list(x_data)

    # also indirect test of read_buffer
    @pytest.mark.parametrize("data_format, response",
                             [("REAL,32", b"#14" + REAL32_DATA + b"\n"),
                              ("REAL,64", b"#18" + REAL64_DATA + b"\n"),
                              ])
    def test_x_data_real(self, data_format, response):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", data_format),
             ("CALC1:MEAS1:X?", response),
             ],
        ) as inst:
            x_data = inst.ch_1.tr_1.x_data
            assert type(x_data) is np.ndarray
            assert [1.e+07] == x_data

    def test_x_unit(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("CALC1:MEAS1:X:AXIS:UNIT?", "FREQ"),
             ],
        ) as inst:
            assert "FREQ" == inst.ch_1.tr_1.x_unit

    def test_y_data_ascii(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", "ASC,0"),
             ("CALC1:MEAS1:DATA:FDATA?", "1.2,3,5E+4"),
             ],
        ) as inst:
            y_data = inst.ch_1.tr_1.y_data
            assert type(y_data) is np.ndarray
            assert ["1.2", "3", "5E+4"] == list(y_data)

    # also indirect test of read_buffer
    @pytest.mark.parametrize("data_format, response",
                             [("REAL,32", b"#14" + REAL32_DATA + b"\n"),
                              ("REAL,64", b"#18" + REAL64_DATA + b"\n"),
                              ])
    def test_y_data_real(self, data_format, response):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", data_format),
             ("CALC1:MEAS1:DATA:FDATA?", response),
             ],
        ) as inst:
            y_data = inst.ch_1.tr_1.y_data
            assert type(y_data) is np.ndarray
            assert [1.e+07] == y_data

    def test_y_data_complex_ascii(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", "ASC,0"),
             ("CALC1:MEAS1:DATA:SDATA?", "1.2,3"),
             ],
        ) as inst:
            y_data = inst.ch_1.tr_1.y_data_complex
            assert type(y_data) is np.ndarray
            assert "1.2" == y_data[0][0]
            assert "3" == y_data[0][1]

    # also indirect test of read_buffer
    @pytest.mark.parametrize("data_format, response",
                             [("REAL,32", b"#18" + 2*REAL32_DATA + b"\n"),
                              ("REAL,64", b"#216" + 2*REAL64_DATA + b"\n"),
                              ])
    def test_y_data_complex_real(self, data_format, response):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("FORM?", data_format),
             ("CALC1:MEAS1:DATA:SDATA?", response),
             ],
        ) as inst:
            y_data = inst.ch_1.tr_1.y_data_complex
            assert type(y_data) is np.ndarray
            assert 1.e7 == y_data[0][0]
            assert 1.e7 == y_data[0][1]

    def test_y_unit(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("CALC1:MEAS1:Y:AXIS:UNIT?", "DBM"),
             ],
        ) as inst:
            assert "DBM" == inst.ch_1.tr_1.y_unit


class TestMeasurementChannel():
    def test_initiate(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("INIT1:IMM", None),
             ],
        ) as inst:
            inst.ch_1.initiate()

    def test_single(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SENS1:SWE:MODE SING", None),
             ],
        ) as inst:
            inst.ch_1.single()

    def test_continuous(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SENS1:SWE:MODE CONT", None),
             ],
        ) as inst:
            inst.ch_1.continuous()

    def test_hold(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SENS1:SWE:MODE HOLD", None),
             ],
        ) as inst:
            inst.ch_1.hold()

    def test_number_of_points(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SENS1:SWE:POIN?", "201"),
             ],
        ) as inst:
            assert 201 == inst.ch_1.number_of_points

    def test_measurements(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SYST:MEAS:CAT? 1", "1,2,3,6,8"),
             ],
        ) as inst:
            assert [1, 2, 3, 6, 8] == inst.ch_1.measurements


class TestKeysightPNA():
    def test_abort(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("ABOR", None),
             ],
        ) as inst:
            inst.abort()

    def test_load_state(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("MMEM:LOAD 'MyState.csa'", None),
             ] + UPDATE,
        ) as inst:
            inst.load_state("MyState.csa")

    @pytest.mark.parametrize("byte_order_swapped, mapping", [
                             (False, "NORM"),
                             (True, "SWAP"),
                             ])
    def test_byte_order_swapped(self, byte_order_swapped, mapping):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"FORM:BORD {mapping}", None),
             ("FORM:BORD?", mapping),
             ],
        ) as inst:
            inst.byte_order_swapped = byte_order_swapped
            assert byte_order_swapped == inst.byte_order_swapped

    @pytest.mark.parametrize("data_format, mapping",
                             [("ascii", "ASC,0"),
                              ("real32", "REAL,32"),
                              ("real64", "REAL,64"),
                              ])
    def test_data_format(self, data_format, mapping):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"FORM {mapping}", None),
             ("FORM?", mapping),
             ],
        ) as inst:
            inst.data_format = data_format
            assert data_format == inst.data_format

    def test_measurement_channels(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("SYST:CHAN:CAT?", "1,2,3,6,99,300"),
             ],
        ) as inst:
            assert [1, 2, 3, 6, 99, 300] == inst.measurement_channels

    def test_options(self):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             ("*OPT?", '"086,UNY,P04"'),
             ],
        ) as inst:
            assert ["086", "UNY", "P04"] == inst.options

    @pytest.mark.parametrize("output_enabled, mapping", [(True, 1), (False, 0)])
    def test_output_enabled(self, output_enabled, mapping):
        with expected_protocol(
            KeysightPNA,
            INITIALIZATION + [
             (f"OUTP {mapping}", None),
             ("OUTP?", mapping),
             ],
        ) as inst:
            inst.output_enabled = output_enabled
            assert output_enabled == inst.output_enabled
