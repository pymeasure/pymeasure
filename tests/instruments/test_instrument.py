#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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
from pymeasure.adapters import FakeAdapter
from pymeasure.instruments.instrument import Instrument, FakeInstrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range, truncated_range


def test_fake_instrument():
    fake = FakeInstrument()
    fake.write("Testing")
    assert fake.read() == "Testing"
    assert fake.read() == ""
    assert fake.values("5") == [5]


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_doc(dynamic):
    doc = """ X property """

    class Fake(Instrument):
        x = Instrument.control(
            "", "%d", doc,
            dynamic=dynamic
        )

    assert Fake.x.__doc__ == doc


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=range(10),
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '5'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError) as e_info:
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_validator_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values=[4, 5, 6, 7],
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    with pytest.raises(ValueError) as e_info:
        fake.x = 20


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={5: 1, 10: 2, 20: 3},
            map_values=True,
            dynamic=dynamic
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == '1'
    fake.x = 5
    assert fake.x == 5
    fake.x = 20
    assert fake.read() == '3'


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_dict_str_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_discrete_set,
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 'X'
    assert fake.read() == '1'
    fake.x = 'Y'
    assert fake.x == 'Y'
    fake.x = 'Z'
    assert fake.read() == '3'


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "%d", "",
            validator=strict_range,
            values=[5e-3, 120e-3],
            get_process=lambda v: v * 1e-3,
            set_process=lambda v: v * 1e3,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 10e-3
    assert fake.read() == '10'
    fake.x = 30e-3
    assert fake.x == 30e-3


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_get_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "JUNK%d", "",
            validator=strict_range,
            values=[0, 10],
            get_process=lambda v: int(v.replace('JUNK', '')),
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    fake.x = 5
    assert fake.x == 5


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_preprocess_reply_property(dynamic):
    # test setting preprocess_reply at property-level
    class Fake(FakeInstrument):
        x = Instrument.control(
            "", "JUNK%d",
            "",
            preprocess_reply=lambda v: v.replace('JUNK', ''),
            dynamic=dynamic,
            cast=int,
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    # notice that read returns the full reply since preprocess_reply is only
    # called inside Adapter.values()
    fake.x = 5
    assert fake.x == 5
    fake.x = 5
    assert type(fake.x) == int


@pytest.mark.parametrize("dynamic", [False, True])
def test_control_preprocess_reply_adapter(dynamic):
    # test setting preprocess_reply at Adapter-level
    class Fake(FakeInstrument):
        def __init__(self):
            super().__init__(preprocess_reply=lambda v: v.replace('JUNK', ''))

        x = Instrument.control(
            "", "JUNK%d", "",
            dynamic=dynamic,
            cast=int
        )

    fake = Fake()
    fake.x = 5
    assert fake.read() == 'JUNK5'
    # notice that read returns the full reply since preprocess_reply is only
    # called inside Adapter.values()
    fake.x = 5
    assert fake.x == 5


@pytest.mark.parametrize("dynamic", [False, True])
def test_measurement_dict_str_map(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.measurement(
            "", "",
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values=True,
            dynamic=dynamic,
        )

    fake = Fake()
    fake.write('1')
    assert fake.x == 'X'
    fake.write('2')
    assert fake.x == 'Y'
    fake.write('3')
    assert fake.x == 'Z'


@pytest.mark.parametrize("dynamic", [False, True])
def test_setting_process(dynamic):
    class Fake(FakeInstrument):
        x = Instrument.setting(
            "OUT %d", "",
            set_process=lambda v: int(bool(v)),
            dynamic=dynamic,
        )

    fake = Fake()
    fake.x = False
    assert fake.read() == 'OUT 0'
    fake.x = 2
    assert fake.read() == 'OUT 1'

def test_instrument_dynamic_parameter():
    class GenericInstrument(FakeInstrument):
        fake_ctrl = Instrument.control(
            ":PARAM?;", ":PARAM %e Hz;",
            """ A property that represents ...
            """,
            validator=strict_range,
            values=(1, 10),
            dynamic = True
        )
        fake_setting = Instrument.setting(
            ":PARAM1 %e Hz;",
            """ A property that represents ...
            """,
            validator=strict_range,
            values=(1, 10),
            dynamic = True
        )
        fake_measurement = Instrument.measurement(
            "",
            """ A property that represents ...
            """,
            values={'X': 1, 'Y': 2, 'Z': 3},
            map_values = True,
            dynamic = True
        )
    class SpecificInstrument1(GenericInstrument):
        fake_ctrl_values = (1, 10) # Set values parameter for SpecificInstrument1
        fake_setting_values = (1, 10) # Set values parameter for SpecificInstrument1
        fake_measurement_values={'X': 1, 'Y': 2, 'Z': 3} # Set values parameter for SpecificInstrument1

    class SpecificInstrument2(GenericInstrument):
        fake_ctrl_values = (10, 20) # Set values parameter for SpecificInstrument2
        fake_setting_values = (10, 20) # Set values parameter for SpecificInstrument2
        fake_measurement_values={'X': 4, 'Y': 5, 'Z': 6} # Set values parameter for SpecificInstrument2
    
    s1 = SpecificInstrument1()
    s2 = SpecificInstrument2()
    
    s2.fake_ctrl = 15
    with pytest.raises(ValueError) as e_info:
        s1.fake_ctrl = 15

    s2.fake_setting = 15
    with pytest.raises(ValueError) as e_info:
        s1.fake_setting = 15

    s1.read()
    s2.read()
    s1.write('1')
    s2.write('4')
    assert s1.fake_measurement == 'X'
    assert s2.fake_measurement == 'X'

    s1.fake_ctrl_validator=truncated_range # Try truncated range
    s1.fake_ctrl = 15
    s1.fake_ctrl_validator=strict_range # Back to strict_range
    with pytest.raises(ValueError) as e_info:
        s1.fake_ctrl = 15
