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

import pytest

from pymeasure.instruments.tektronix.tektronixMsoSeries import sanitize_source
from pymeasure.instruments.tektronix.tektronixMsoSeries import TektronixMSO58
from pymeasure.test import expected_protocol

INVALID_CHANNELS = ["INVALID_SOURCE", "C1 C2", "C1 MATH", "C1234567", "CHANNEL"]
VALID_CHANNELS = [('C1', '1'), ('CHANNEL2', '2'), ('ch 3', '3'), ('chan 4', '4'),
                  ('\tC3\t', '3'), ("C8", "8")]


@pytest.mark.parametrize("channel", INVALID_CHANNELS)
def test_invalid_source(channel):
    with pytest.raises(ValueError):
        sanitize_source(channel)


@pytest.mark.parametrize("channel", VALID_CHANNELS)
def test_sanitize_valid_source(channel):
    assert sanitize_source(channel[0]) == channel[1]


def test_bwl():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:BANdwidth 2E+07", None),
             (b"CH1:BANdwidth?", b"2E+07"),
             (b"CH1:BANdwidth 2.5E+08", None),
             (b"CH1:BANdwidth?", b"2.5E+08")
             ],
    ) as instr:
        instr.ch_1.bwlimit = 2E+7
        assert instr.ch_1.bwlimit == 2E+7
        instr.ch_1.bwlimit = 2.5E+8
        assert instr.ch_1.bwlimit == 2.5E+8


def test_coupling():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:COUPling AC", None),
             (b"CH1:COUPling?", b"AC"),
             (b"CH1:COUPling DC", None),
             (b"CH1:COUPling?", b"DC"),
             (b"CH1:COUPling DCREJ", None),
             (b"CH1:COUPling?", b"DCREJ")
             ],
    ) as instr:
        instr.ch_1.coupling = "ac"
        assert instr.ch_1.coupling == "ac"
        instr.ch_1.coupling = "dc"
        assert instr.ch_1.coupling == "dc"
        instr.ch_1.coupling = "dcrej"
        assert instr.ch_1.coupling == "dcrej"


def test_offset():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:OFFSet 0.001", None),
             (b"CH1:OFFSet?", b"1E-03")
             ],
    ) as instr:
        instr.ch_1.offset = 1E-3
        assert instr.ch_1.offset == 1E-3


def test_label():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:LABel:NAMe \"Channel 1\"", None),
             (b"CH1:LABel:NAMe?", b"Channel 1")
             ],
    ) as instr:
        instr.ch_1.label = "Channel 1"
        assert instr.ch_1.label == "Channel 1"


def test_scale():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:SCAle 1", None),
             (b"CH1:SCAle?", b"1")
             ],
    ) as instr:
        instr.ch_1.scale = 1
        assert instr.ch_1.scale == 1


def test_trigger_level():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"TRIGger:A:LEVel:CH1 0.1", None),
             (b"TRIGger:A:LEVel:CH1?", b"0.1")
             ],
    ) as instr:
        instr.ch_1.trigger_level = 0.1
        assert instr.ch_1.trigger_level == 0.1


def test_channel_setup():
    with expected_protocol(
            TektronixMSO58,
            [(b"HEADer OFF", None),
             (b"VERBose ON", None),
             (b"CH1:BANdwidth?", b"1.0E+9"),
             (b"CH1:COUPling?", b"DC"),
             (b"CH1:OFFSet?", b"0.0"),
             (b"DISplay:GLObal:CH1:STATE?", b"1"),
             (b"CH1:PRObe:UNIts?", b"\"V\""),
             (b"CH1:LABel:NAMe?", b"\"\""),
             (b"CH1:SCAle?", b"0.1"),
             (b"TRIGger:A:LEVel:CH1?", b"0.0")
             ]
    ) as instr:
        assert instr.ch_1.current_configuration == {"channel": 1,
                                                    "bandwidth_limit": 1.0E+9,
                                                    "coupling": "dc",
                                                    "offset": 0.0,
                                                    "display": True,
                                                    "unit": "V",
                                                    "label": '\"\"',
                                                    "volts_div": 100.0000E-3,
                                                    "trigger_level": 0.0,
                                                    }
