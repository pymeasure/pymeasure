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

import pytest

from pymeasure.instruments import Instrument
from pymeasure.instruments.generic_types import IEEE4882Mixin, SCPIMixin
from pymeasure.test import expected_protocol


class Test_IEEE4882Mixin:
    class IEEE4882Instrument(IEEE4882Mixin, Instrument):
        pass

    @pytest.mark.parametrize("method, write, reply", (
        ("id", "*IDN?", "xyz, abc"),
        ("complete", "*OPC?", "1"),
        ("status", "*STB?", "189"),
        ("options", "*OPT?", "a9"),
    ))
    def test_IEEE4882_properties(self, method, write, reply):
        with expected_protocol(
                self.IEEE4882Instrument,
                [(write, reply)],
                name="test") as inst:
            assert getattr(inst, method) == reply

    @pytest.mark.parametrize("method, write", (
        ("clear", "*CLS"),
        ("reset", "*RST"),
    ))
    def test_IEEE4882_write_commands(self, method, write):
        with expected_protocol(
                self.IEEE4882Instrument,
                [(write, None)],
                name="test") as inst:
            getattr(inst, method)()


class Test_SCPIMixin:
    class SCPIInstrument(SCPIMixin, Instrument):
        pass

    @pytest.mark.parametrize("method, write, reply", (
        ("id", "*IDN?", "xyz, abc"),
        ("complete", "*OPC?", "1"),
        ("status", "*STB?", "189"),
        ("options", "*OPT?", "a9"),
    ))
    def test_SCPI_properties(self, method, write, reply):
        with expected_protocol(
                self.SCPIInstrument,
                [(write, reply)],
                name="test") as inst:
            assert getattr(inst, method) == reply

    def test_next_error(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("SYST:ERR?", '-100,"Command error"')],
                name="test") as inst:
            assert inst.next_error == [-100, '"Command error"']

    @pytest.mark.parametrize("method, write", (("clear", "*CLS"),
                                               ("reset", "*RST"),
                                               ))
    def test_SCPI_write_commands(self, method, write):
        with expected_protocol(
                self.SCPIInstrument,
                [(write, None)],
                name="test") as inst:
            getattr(inst, method)()

    def test_check_errors(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("SYST:ERR?", '-100,"Command error"'),
                 ("SYST:ERR?", '-222,"Data out of range"'),
                 ("SYST:ERR?", '0,"No error"'),
                 ],
                name="test") as inst:
            assert inst.check_errors() == [[-100, '"Command error"'],
                                           [-222, '"Data out of range"']]

    def test_close_does_not_raise(self):
        with expected_protocol(self.SCPIInstrument, [], name="test") as inst:
            inst.close()  # Adapter.close() is a no-op for ProtocolAdapter — must not raise


def test_SCPIMixin_inherits_IEEE4882Mixin():
    assert issubclass(SCPIMixin, IEEE4882Mixin)


class Test_GetDeviceInfo:
    """Tests for SCPIMixin.get_device_info()."""

    class SCPIInstrument(SCPIMixin, Instrument):
        """Minimal SCPI instrument used in get_device_info tests."""

    def test_sets_name_from_idn(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP804,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            assert inst.name == "NGP804"

    def test_sets_vendor_from_idn(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP804,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            assert inst.vendor == "Rohde&Schwarz"

    def test_sets_serial_number_from_idn(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP804,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            assert inst.serial_number == "12345"

    def test_sets_firmware_ref_from_idn(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP804,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            assert inst.firmware_ref == "V1.0"


class Test_CheckIsDevSupported:
    """Tests for SCPIMixin.check_is_dev_supported()."""

    class SCPIInstrument(SCPIMixin, Instrument):
        """Minimal SCPI instrument used in check_is_dev_supported tests."""

    def test_supported_model_does_not_raise(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP804,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            inst.check_is_dev_supported(["NGP804", "NGP814"], ": not supported")

    def test_unsupported_model_raises_assertion_error(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,NGP402,12345,V1.0")],
                name="test") as inst:
            inst.get_device_info()
            with pytest.raises(AssertionError, match="NGP402"):
                inst.check_is_dev_supported(["NGP804", "NGP814"], ": not supported")

    def test_error_includes_custom_message(self):
        with expected_protocol(
                self.SCPIInstrument,
                [("*IDN?", "Rohde&Schwarz,UNKNOWN,SN,FW")],
                name="test") as inst:
            inst.get_device_info()
            with pytest.raises(AssertionError, match="Instrument not supported"):
                inst.check_is_dev_supported(["NGP804"], ": Instrument not supported")

    def test_none_name_raises_assertion_error(self):
        with expected_protocol(self.SCPIInstrument, [], name="test") as inst:
            inst.name = None
            with pytest.raises(AssertionError, match="not opened"):
                inst.check_is_dev_supported(["NGP804"], "")
