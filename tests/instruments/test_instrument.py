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


import time
from unittest import mock

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument, Channel
from pymeasure.adapters import FakeAdapter, ProtocolAdapter
from pymeasure.instruments.fakes import FakeInstrument
from pymeasure.instruments.validators import truncated_range


class GenericInstrument(FakeInstrument):
    #  Use truncated_range as this easily lets us test for the range boundaries
    fake_ctrl = Instrument.control(
        "", "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = Instrument.setting(
        "%d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = Instrument.measurement(
        "", "docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )


@pytest.fixture()
def generic():
    return GenericInstrument()


class GenericChannel(Channel):
    #  Use truncated_range as this easily lets us test for the range boundaries
    fake_ctrl = Instrument.control(
        "C{ch}:control?", "C{ch}:control %d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_setting = Instrument.setting(
        "C{ch}:setting %d", "docs",
        validator=truncated_range,
        values=(1, 10),
        dynamic=True,
    )
    fake_measurement = Instrument.measurement(
        "C{ch}:measurement?", "docs",
        values={'X': 1, 'Y': 2, 'Z': 3},
        map_values=True,
        dynamic=True,
    )
    special_control = Instrument.control(
        "SOUR{ch}:special?", "OUTP{ch}:special %s",
        """A special control with different channel specifiers for get and set.""",
        cast=str,
    )


class ChannelInstrument(Instrument):
    def __init__(self, adapter, name="ChannelInstrument", **kwargs):
        super().__init__(adapter, name, **kwargs)
        self.add_child(GenericChannel, "A")
        self.add_child(GenericChannel, "B")


def test_fake_instrument():
    fake = FakeInstrument()
    fake.write("Testing")
    assert fake.read() == "Testing"
    assert fake.read() == ""
    assert fake.values("5") == [5]


class Test_includeSCPI_parameter:
    def test_not_defined_includeSCPI_raises_warning(self):
        with pytest.warns(FutureWarning) as record:
            Instrument(name="test", adapter=ProtocolAdapter())
        msg = str(record[0].message)
        assert msg == ("It is deprecated to specify `includeSCPI` implicitly, use "
                       "`includeSCPI=False` or inherit the `SCPIMixin` class instead.")

    def test_not_defined_includeSCPI_is_interpreted_as_true(self):
        inst = Instrument(name="test", adapter=ProtocolAdapter())
        assert inst.SCPI is True


@pytest.mark.parametrize("adapter", (("COM1", 87, "USB")))
def test_init_visa(adapter):
    Instrument(adapter, "def", visa_library="@sim")
    pass  # Test that no error is raised


@pytest.mark.xfail()  # I do not know, when this error is raised
def test_init_visa_fail():
    with pytest.raises(Exception, match="Invalid adapter"):
        Instrument("abc", "def", visa_library="@xyz")


def test_init_includeSCPI_implicit_warning():
    with pytest.warns(FutureWarning, match="includeSCPI"):
        Instrument("COM1", "def", visa_library="@sim")


def test_init_includeSCPI_explicit_warning():
    with pytest.warns(FutureWarning, match="includeSCPI"):
        Instrument("COM1", "def", visa_library="@sim", includeSCPI=True)


def test_global_preprocess_reply():
    with pytest.warns(FutureWarning, match="deprecated"):
        inst = Instrument(FakeAdapter(), "name", preprocess_reply=lambda v: v.strip("x"))
        assert inst.values("x5x") == [5]


def test_instrument_in_context():
    with Instrument("abc", "def", visa_library="@sim") as instr:
        pass
    assert instr.isShutdown is True


def test_with_statement():
    """ Test the with-statement-behaviour of the instruments. """
    with FakeInstrument() as fake:
        # Check if fake is an instance of FakeInstrument
        assert isinstance(fake, FakeInstrument)

        # Check whether the shutdown function is already called
        assert fake.isShutdown is False

    # Check whether the shutdown function is called upon
    assert fake.isShutdown is True


class TestInstrumentCommunication:
    @pytest.fixture()
    def instr(self):
        a = mock.MagicMock(return_value="5")
        return Instrument(a, "abc")

    def test_write(self, instr):
        instr.write("abc")
        assert instr.adapter.method_calls == [mock.call.write('abc')]

    def test_read(self, instr):
        instr.read()
        assert instr.adapter.method_calls == [mock.call.read()]

    def test_write_bytes(self, instr):
        instr.write_bytes(b"abc")
        assert instr.adapter.method_calls == [mock.call.write_bytes(b"abc")]

    def test_read_bytes(self, instr):
        instr.read_bytes(5)
        assert instr.adapter.method_calls == [mock.call.read_bytes(5)]

    def test_write_binary_values(self, instr):
        instr.write_binary_values("abc", [5, 6, 7])
        assert instr.adapter.method_calls == [mock.call.write_binary_values("abc", [5, 6, 7])]


class TestWaiting:
    @pytest.fixture()
    def instr(self):
        class Faked(Instrument):
            def wait_for(self, query_delay=None):
                self.waited = query_delay
        return Faked(ProtocolAdapter(), name="faked")

    def test_waiting(self):
        instr = Instrument(ProtocolAdapter(), "faked")
        stop = time.perf_counter() + 100
        instr.wait_for(0.1)
        assert time.perf_counter() < stop

    def test_ask_calls_wait(self, instr):
        instr.adapter.comm_pairs = [("abc", "resp")]
        instr.ask("abc")
        assert instr.waited is None

    def test_ask_calls_wait_with_delay(self, instr):
        instr.adapter.comm_pairs = [("abc", "resp")]
        instr.ask("abc", query_delay=10)
        assert instr.waited == 10

    def test_binary_values_calls_wait(self, instr):
        instr.adapter.comm_pairs = [("abc", "abcdefgh")]
        instr.binary_values("abc")
        assert instr.waited is None


@pytest.mark.parametrize("method, write, reply", (("id", "*IDN?", "xyz"),
                                                  ("complete", "*OPC?", "1"),
                                                  ("status", "*STB?", "189"),
                                                  ("options", "*OPT?", "a9"),
                                                  ))
def test_SCPI_properties(method, write, reply):
    with expected_protocol(
            Instrument,
            [(write, reply)],
            name="test") as instr:
        assert getattr(instr, method) == reply


@pytest.mark.parametrize("method, write", (("clear", "*CLS"),
                                           ("reset", "*RST")
                                           ))
def test_SCPI_write_commands(method, write):
    with expected_protocol(
            Instrument,
            [(write, None)],
            name="test") as instr:
        getattr(instr, method)()


def test_instrument_check_errors():
    with expected_protocol(
            Instrument,
            [("SYST:ERR?", "17,funny stuff"),
             ("SYST:ERR?", "0")],
            name="test") as instr:
        assert instr.check_errors() == [[17, "funny stuff"]]


@pytest.mark.parametrize("method", ("id", "complete", "status", "options",
                                    "clear", "reset", "check_errors"
                                    ))
def test_SCPI_false_raises_errors(method):
    with pytest.raises(NotImplementedError):
        getattr(Instrument(FakeAdapter(), "abc", includeSCPI=False), method)()


# Channel
class TestMultiFunctionality:
    """Test the usage of children for different functionalities."""
    class SomeFunctionality(Channel):
        """This Functionality needs a prepended `id`."""

        def insert_id(self, command, **kwargs):
            return f"{self.id}:{command}"

        voltage = Channel.control("Volt?", "Volt %f", "Set voltage in Volts.")

    class InstrumentWithFunctionality(ChannelInstrument):
        """Instrument with some functionality."""

        def __init__(self, adapter, **kwargs):
            super().__init__(adapter, **kwargs)
            self.add_child(TestMultiFunctionality.SomeFunctionality, "X",
                           collection="functions", prefix="f_")

    def test_functionality_dict(self):
        inst = TestMultiFunctionality.InstrumentWithFunctionality(ProtocolAdapter())
        assert isinstance(inst.functions["X"], TestMultiFunctionality.SomeFunctionality)
        assert inst.functions["X"] == inst.f_X

    def test_functions_voltage_getter(self):
        with expected_protocol(
                TestMultiFunctionality.InstrumentWithFunctionality,
                [("X:Volt?", "123.456")]
        ) as inst:
            assert inst.f_X.voltage == 123.456

    def test_functions_voltage_setter(self):
        with expected_protocol(
                TestMultiFunctionality.InstrumentWithFunctionality,
                [("X:Volt 123.456000", None)]
        ) as inst:
            inst.f_X.voltage = 123.456
