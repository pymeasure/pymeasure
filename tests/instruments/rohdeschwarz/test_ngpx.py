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

from pymeasure.test import expected_protocol
from pymeasure.instruments.rohdeschwarz.ngpx import NGPx

# ``NGPx.__init__`` always calls ``*IDN?`` first and verifies the model.
IDN = ("*IDN?", "Rohde&Schwarz,NGP804,1234,01.42")


def test_init_populates_identity_and_channels():
    with expected_protocol(NGPx, [IDN], name="mock") as inst:
        assert inst.vendor == "Rohde&Schwarz"
        assert inst.name == "NGP804"
        assert inst.serial_number == "1234"
        assert inst.firmware_ref == "01.42"
        assert set(inst.channels.keys()) == {1, 2, 3, 4}
        # channels are also exposed as ``ch1``..``ch4``
        assert inst.ch1 is inst.channels[1]
        assert inst.ch4 is inst.channels[4]


def test_init_rejects_unsupported_model():
    with pytest.raises(AssertionError, match="Instrument not supported"):
        with expected_protocol(
            NGPx,
            [("*IDN?", "Foo,BadModel,0,0")],
            name="mock",
        ):
            pass


def test_channel_voltage_setpoint_set_and_measure():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("VOLT 5.000,(@1)", None),
            ("MEAS:VOLT? (@1)", "4.998"),
        ],
        name="mock",
    ) as inst:
        inst.ch1.voltage_setpoint = 5.0
        assert inst.ch1.voltage == pytest.approx(4.998)


def test_channel_output_toggle():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("OUTP 1,(@2)", None),
            ("OUTP? (@2)", "1"),
        ],
        name="mock",
    ) as inst:
        inst.ch2.output = True
        assert inst.ch2.output is True


def test_channel_ovp_clear():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("VOLT:PROT:CLE (@3)", None),
        ],
        name="mock",
    ) as inst:
        inst.ch3.ovp_clear()


def test_channel_ocp_clear():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("FUSE:TRIP:CLE (@4)", None),
        ],
        name="mock",
    ) as inst:
        inst.ch4.ocp_clear()


def test_output_general():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("OUTP:GEN 1", None),
            ("OUTP:GEN?", "1"),
        ],
        name="mock",
    ) as inst:
        inst.output_general = True
        assert inst.output_general is True


def test_master_output_requires_selection():
    """Without any ``select``ed channel, the master ``output`` is a no-op."""
    with expected_protocol(NGPx, [IDN], name="mock") as inst:
        # Nothing selected -> getter returns False without I/O
        assert inst.output is False
        # Setter without selection logs a warning and sends no SCPI command
        inst.output = True


def test_master_output_with_selection():
    with expected_protocol(
        NGPx,
        [
            IDN,
            # Mark ch1 and ch3 as selected
            ("OUTP:SEL 1,(@1)", None),
            ("OUTP:SEL 1,(@3)", None),
            # Master ON -> sends to the selected channels
            ("OUTP 1, (@1,3)", None),
            # Master query -> all selected channels report ON
            ("OUTP? (@1,3)", "1,1"),
        ],
        name="mock",
    ) as inst:
        inst.ch1.select = True
        inst.ch3.select = True
        inst.output = True
        assert inst.output is True


def test_link_and_get_ocp_linked_channels():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("INST (@1);FUSE:LINK 2,3,4", None),
            ("INST (@1);FUSE:LINK?", "2,3,4"),
        ],
        name="mock",
    ) as inst:
        inst.link_ocp(1, 2, 3, 4)
        assert inst.get_ocp_linked_channels(1) == [2, 3, 4]


def test_unlink_ocp_single_and_all():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("INST (@1);FUSE:UNL 3", None),
            ("INST (@1);FUSE:UNL 0", None),
        ],
        name="mock",
    ) as inst:
        inst.unlink_ocp(1, 3)
        inst.unlink_ocp(1)


def test_tracking_general_enabled():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("TRAC:GEN 1", None),
            ("TRAC:GEN?", "1"),
        ],
        name="mock",
    ) as inst:
        inst.tracking_general_enabled = True
        assert inst.tracking_general_enabled is True


def test_set2local_set2remote():
    with expected_protocol(
        NGPx,
        [
            IDN,
            ("SYST:REM", None),
            ("SYST:LOC", None),
        ],
        name="mock",
    ) as inst:
        inst.set2remote()
        inst.set2local()
