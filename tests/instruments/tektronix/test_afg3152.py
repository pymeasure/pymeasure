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

from pymeasure.test import expected_protocol
from pymeasure.instruments.tektronix.afg3152c import AFG3152C

import pytest


@pytest.mark.parametrize("channel", [1, 2])
def test_shape(channel):
    # Demonstrate message prefix identifying the channel
    # Note how the implementation of the shape property does not show that
    # prefix (it is added in the Channel class)
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:function:shape?", "LOR"),
         (f"source{channel}:function:shape HAV", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.shape == 'lorentz'
        ch.shape = 'haversine'


def test_beep():
    # A message common to all channels does not have a prefix
    with expected_protocol(
        AFG3152C,
        [("system:beep", None)],
    ) as inst:
        inst.beep()


def test_enable():
    with expected_protocol(
        AFG3152C,
        [("output1:state on", None)],
    ) as inst:
        inst.ch1.enable()


def test_disable():
    with expected_protocol(
        AFG3152C,
        [("output1:state off", None)],
    ) as inst:
        inst.ch1.disable()


@pytest.mark.parametrize("channel", [1, 2])
def test_unit(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:voltage:unit?", "VPP"),
         (f"source{channel}:voltage:unit DBM", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.unit == "VPP"
        ch.unit = "DBM"


@pytest.mark.parametrize("channel", [1, 2])
def test_amp_vpp(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:voltage:amplitude?", "1.000000e+00"),
         (f"source{channel}:voltage:amplitude 2.000000e+00VPP", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.amp_vpp == 1
        ch.amp_vpp = 2


@pytest.mark.parametrize("channel", [1, 2])
def test_amp_dbm(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:voltage:amplitude?", "1.000000e+00"),
         (f"source{channel}:voltage:amplitude 2.000000e+00DBM", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.amp_dbm == 1
        ch.amp_dbm = 2


@pytest.mark.parametrize("channel", [1, 2])
def test_amp_vrms(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:voltage:amplitude?", "1.000000e+00"),
         (f"source{channel}:voltage:amplitude 2.000000e+00VRMS", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.amp_vrms == 1
        ch.amp_vrms = 2


@pytest.mark.parametrize("channel", [1, 2])
def test_offset(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:voltage:offset?", "0.000000e+00"),
         (f"source{channel}:voltage:offset 5.000000e-01", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.offset == 0
        ch.offset = 0.5


@pytest.mark.parametrize("channel", [1, 2])
def test_frequency(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:frequency:fixed?", "1.000000e+06"),
         (f"source{channel}:frequency:fixed 1.000000e+03", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.frequency == 1e6
        ch.frequency = 1e3


@pytest.mark.parametrize("channel", [1, 2])
def test_duty(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:pulse:dcycle?", "50.000"),
         (f"source{channel}:pulse:dcycle 25.000", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.duty == 50
        ch.duty = 25


@pytest.mark.parametrize("channel", [1, 2])
def test_impedance(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:output:impedance?", "50"),
         (f"source{channel}:output:impedance 1000", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        assert ch.impedance == 50
        ch.impedance = 1000


@pytest.mark.parametrize("channel", [1, 2])
def test_waveform(channel):
    with expected_protocol(
        AFG3152C,
        [(f"source{channel}:function:shape SIN", None),
         (f"source{channel}:frequency:fixed 1.000000e+06", None),
         (f"source{channel}:voltage:unit VPP", None),
         (f"source{channel}:voltage:amplitude 1.000000e+00VPP", None),
         (f"source{channel}:voltage:offset 0.000000e+00V", None),
         ],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        ch.waveform(shape="SIN", frequency=1e6, units="VPP", amplitude=1, offset=0)


def test_opc():
    with expected_protocol(
        AFG3152C,
        [("*OPC?", "1")],
    ) as inst:
        assert inst.opc() == 1


@pytest.mark.parametrize("channel", [1, 2])
def test_frequency_out_of_range_raises(channel):
    with expected_protocol(
        AFG3152C,
        [],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        with pytest.raises(ValueError):
            ch.frequency = 0
        with pytest.raises(ValueError):
            ch.frequency = 200e6


@pytest.mark.parametrize("channel", [1, 2])
def test_amp_vpp_out_of_range_raises(channel):
    with expected_protocol(
        AFG3152C,
        [],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        with pytest.raises(ValueError):
            ch.amp_vpp = 0
        with pytest.raises(ValueError):
            ch.amp_vpp = 20


@pytest.mark.parametrize("channel", [1, 2])
def test_duty_out_of_range_raises(channel):
    with expected_protocol(
        AFG3152C,
        [],
    ) as inst:
        ch = getattr(inst, f"ch{channel}")
        with pytest.raises(ValueError):
            ch.duty = 0
        with pytest.raises(ValueError):
            ch.duty = 100
