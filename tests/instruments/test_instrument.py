#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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
from pymeasure.instruments.instrument import Instrument, FakeInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


def test_fake_instrument():
    fake = FakeInstrument()
    fake.write("Testing")
    assert fake.read() == "Testing"
    assert fake.read() == ""
    assert fake.values("5") == [5]


def test_control_doc():
    doc = """ X property """

    class Fake(Instrument):
        x = Instrument.control(
            "", "%d", doc
        )

    assert Fake.x.__doc__ == doc


def test_control_validator():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=range(10),
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '5'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError) as e_info:
        fake.x = 20


def test_control_validator_map():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=[4, 5, 6, 7],
            map_values=True,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError) as e_info:
        fake.x = 20


def test_control_dict_map():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={5: 1, 10: 2, 20: 3},
            map_values=True,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    fake.x = 20
    assert fake.read() == '3'


def test_control_dict_str_map():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
        )

    fake = Fake()
    fake.x = 'X'
    assert fake.read() == '1'
    fake.x = 'Y'
    assert fake.x == 'Y'
    fake.x = 'Z'
    assert fake.read() == '3'


def test_control_process():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_range,
            values=[5e-3, 120e-3],
            get_process=lambda v: v * 1e-3,
            set_process=lambda v: v * 1e3,
        )

    fake = Fake()
    fake.x = 10e-3
    assert fake.read() == '10'
    fake.x = 30e-3
    assert fake.x == 30e-3


def test_control_get_process():
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "JUNK%d", "",
            validator=strict_range,
            values=[0, 10],
            get_process=lambda v: int(v.replace('JUNK', '')),
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    fake.x = 5
    assert fake.x == 5


def test_measurement_dict_str_map():
    class Fake(FakeInstrument):
        x = Instrument.measurement(
            "", "",
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
        )

    fake = Fake()
    fake.write('1')
    assert fake.x == 'X'
    fake.write('2')
    assert fake.x == 'Y'
    fake.write('3')
    assert fake.x == 'Z'


def test_setting_process():
    class Fake(FakeInstrument):
        x = Instrument.setting(
            "OUT %d", "",
            set_process=lambda v: int(bool(v)),
        )

    fake = Fake()
    fake.x = False
    assert fake.read() == 'OUT 0'
    fake.x = 2
    assert fake.read() == 'OUT 1'
