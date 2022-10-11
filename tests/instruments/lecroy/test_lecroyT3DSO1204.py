#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments.lecroy.lecroyT3DSO1204 import LeCroyT3DSO1204
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None)]
    ):
        pass  # Verify the expected communication.


def test_bwlimit():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:BWL?", b"OFF"),
             (b"BWL C1,OFF", None),
             (b"C1:BWL?", b"ON"),
             (b"BWL C1,ON", None)
             ]
    ) as instr:
        assert instr.ch1.bwlimit is False
        instr.ch1.bwlimit = False
        assert instr.ch1.bwlimit is True
        instr.ch1.bwlimit = True


def test_coupling():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:CPL?", b"D1M"),
             (b"C1:CPL D1M", None),
             (b"C1:CPL?", b"A1M"),
             (b"C1:CPL A1M", None),
             (b"C1:CPL?", b"GND"),
             (b"C1:CPL GND", None)
             ],
    ) as instr:
        assert instr.ch1.coupling == "dc 1M"
        instr.ch1.coupling = "dc 1M"
        assert instr.ch1.coupling == "ac 1M"
        instr.ch1.coupling = "ac 1M"
        assert instr.ch1.coupling == "ground"
        instr.ch1.coupling = "ground"


def test_offset():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:OFST?", b"1.00E+00"),
             (b"C1:OFST 1.00E+00V", None)
             ]
    ) as instr:
        assert instr.ch1.offset == 1.
        instr.ch1.offset = 1.


def test_attenuation():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:ATTN?", b"100"),
             (b"C1:ATTN 100", None),
             (b"C1:ATTN?", b"0.1"),
             (b"C1:ATTN 0.1", None)
             ]
    ) as instr:
        assert instr.ch1.probe_attenuation == 100
        instr.ch1.probe_attenuation = 100
        assert instr.ch1.probe_attenuation == 0.1
        instr.ch1.probe_attenuation = 0.1


def test_skew_factor():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:SKEW?", b"1.00E-07S"),
             (b"C1:SKEW 1.00E-07S", None),
             ]
    ) as instr:
        assert instr.ch1.skew_factor == 1e-7
        instr.ch1.skew_factor = 1e-7


def test_channel_setup():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"C1:ATTN?", b"1"),
             (b"C1:BWL?", b"OFF"),
             (b"C1:CPL?", b"D1M"),
             (b"C1:OFST?", b"-1.50E-01"),
             (b"C1:SKEW?", b"0.00E+00S"),
             (b"C1:TRA?", b"ON"),
             (b"C1:UNIT?", b"V"),
             (b"C1:VDIV?", b"5.00E-02"),
             (b"C1:INVS?", b"OFF"),
             (b"C1:TRCP?", b"DC"),
             (b"C1:TRLV?", b"1.50E-01"),
             (b"C1:TRLV2?", b"1.50E-01"),
             (b"C1:TRSL?", b"POS"),
             ]
    ) as instr:
        assert instr.ch1.current_configuration == {"channel": 1,
                                                   "attenuation": 1.,
                                                   "bandwidth_limit": False,
                                                   "coupling": "dc 1M",
                                                   "offset": -0.150,
                                                   "skew_factor": 0.,
                                                   "display": True,
                                                   "unit": "V",
                                                   "volts_div": 0.05,
                                                   "inverted": False,
                                                   "trigger_coupling": "dc",
                                                   "trigger_level": 0.150,
                                                   "trigger_level2": 0.150,
                                                   "trigger_slope": "positive"
                                                   }


def test_memory_size():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"MSIZ?", b"14M"),
             (b"MSIZ 14M", None),
             (b"MSIZ?", b"1.4M"),
             (b"MSIZ 1.4M", None),
             (b"MSIZ?", b"7K"),
             (b"MSIZ 7K", None)
             ]
    ) as instr:
        assert instr.memory_size == 14e6
        instr.memory_size = 14e6
        assert instr.memory_size == 14e5
        instr.memory_size = 14e5
        assert instr.memory_size == 7e3
        instr.memory_size = 7e3


def test_sample_size():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"SANU? C1", b"3.50E+06"),
             (b"SANU? C1", b"3.50E+06"),
             (b"SANU? C3", b"3.50E+06"),
             (b"SANU? C3", b"3.50E+06"),
             ]
    ) as instr:
        assert instr.acquisition_sample_size_c1 == 3.5e6
        assert instr.acquisition_sample_size_c2 == 3.5e6
        assert instr.acquisition_sample_size_c3 == 3.5e6
        assert instr.acquisition_sample_size_c4 == 3.5e6


def test_waveform_preamble():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"WFSU?", b"SP,1,NP,0,FP,0"),
             (b"ACQW?", b"SAMPLING"),
             (b"AVGA?", b"16"),
             (b"SARA?", b"1.00E+09"),
             (b"SAST?", b"Trig'd"),
             (b"TDIV?", b"5.00E-04"),
             (b"TRDL?", b"-0.00E+00"),
             (b"C1:VDIV?", b"5.00E-02"),
             (b"C1:OFST?", b"-1.50E-01"),
             ]
    ) as instr:
        assert instr.waveform_preamble == {
            "sparsing": 1,
            "points": 0,
            "first_point": 0,
            "source": "C1",
            "type": "normal",
            "average": 16,
            "sampling_rate": 1e9,
            "grid_number": 14,
            "status": "triggered",
            "xdiv": 5e-4,
            "xoffset": 0,
            "ydiv": 0.05,
            "yoffset": -0.150
        }


def test_trigger():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"TRSE?", b"EDGE,SR,C1,HT,OFF"),
             (b"TRMD?", b"AUTO"),
             (b"C1:TRCP?", b"DC"),
             (b"C1:TRLV?", b"1.50E-01"),
             (b"C1:TRLV2?", b"1.50E-01"),
             (b"C1:TRSL?", b"POS"),
             ]
    ) as instr:
        assert instr.trigger == {
            "mode": "auto",
            "trigger_type": "edge",
            "source": "c1",
            "hold_type": "off",
            "hold_value1": None,
            "hold_value2": None,
            "coupling": "dc",
            "level": 0.150,
            "level2": 0.150,
            "slope": "positive",
        }


def test_math_define():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"DEF EQN,C2*C4", None),
             (b"DEF?", b"C2*C4"),
             ]
    ) as instr:
        instr.math_define = ("channel2", "*", "channel4")
        assert instr.math_define == "C2*C4"


def test_math_vdiv():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"MTVD 1.00E+00V", None),
             (b"MTVD?", b"1.00E+00"),
             ]
    ) as instr:
        instr.math_vdiv = 1.0
        assert instr.math_vdiv == 1.0


def test_math_vpos():
    with expected_protocol(
            LeCroyT3DSO1204,
            [("CHDR OFF", None),
             (b"MTVP 120", None),
             (b"MTVP?", b"120"),
             ]
    ) as instr:
        instr.math_vpos = 120
        assert instr.math_vpos == 120


if __name__ == '__main__':
    pytest.main()
