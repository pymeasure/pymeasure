#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from pymeasure.instruments.teledyne.teledyne_oscilloscope import sanitize_source
from pymeasure.instruments.lecroy.lecroyT3DSO1204 import LeCroyT3DSO1204
from pymeasure.test import expected_protocol

INVALID_CHANNELS = ["INVALID_SOURCE", "C1 C2", "C1 MATH", "C1234567", "CHANNEL"]
VALID_CHANNELS = [('C1', 'C1'), ('CHANNEL2', 'C2'), ('ch 3', 'C3'), ('chan 4', 'C4'),
                  ('\tC3\t', 'C3'), (' math ', 'MATH')]


def test_init():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None)]
    ):
        pass  # Verify the expected communication.


@pytest.mark.parametrize("channel", INVALID_CHANNELS)
def test_invalid_source(channel):
    with pytest.raises(ValueError):
        sanitize_source(channel)


@pytest.mark.parametrize("channel", VALID_CHANNELS)
def test_sanitize_valid_source(channel):
    assert sanitize_source(channel[0]) == channel[1]


def test_bwlimit():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"BWL C1,OFF", None),
             (b"C1:BWL?", b"OFF"),
             (b"BWL C1,ON", None),
             (b"C1:BWL?", b"ON")
             ]
    ) as instr:
        instr.ch_1.bwlimit = False
        assert instr.ch_1.bwlimit is False
        instr.ch_1.bwlimit = True
        assert instr.ch_1.bwlimit is True


def test_coupling():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"C1:CPL D1M", None),
             (b"C1:CPL?", b"D1M"),
             (b"C1:CPL A1M", None),
             (b"C1:CPL?", b"A1M"),
             (b"C1:CPL GND", None),
             (b"C1:CPL?", b"GND")
             ],
    ) as instr:
        instr.ch_1.coupling = "dc 1M"
        assert instr.ch_1.coupling == "dc 1M"
        instr.ch_1.coupling = "ac 1M"
        assert instr.ch_1.coupling == "ac 1M"
        instr.ch_1.coupling = "ground"
        assert instr.ch_1.coupling == "ground"


def test_offset():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"C1:OFST 1.00E+00V", None),
             (b"C1:OFST?", b"1.00E+00")
             ]
    ) as instr:
        instr.ch_1.offset = 1.
        assert instr.ch_1.offset == 1.


def test_attenuation():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"C1:ATTN 100", None),
             (b"C1:ATTN?", b"100"),
             (b"C1:ATTN 0.1", None),
             (b"C1:ATTN?", b"0.1")
             ]
    ) as instr:
        instr.ch_1.probe_attenuation = 100
        assert instr.ch_1.probe_attenuation == 100
        instr.ch_1.probe_attenuation = 0.1
        assert instr.ch_1.probe_attenuation == 0.1


def test_skew_factor():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"C1:SKEW 1.00E-07S", None),
             (b"C1:SKEW?", b"1.00E-07S"),
             ]
    ) as instr:
        instr.ch_1.skew_factor = 1e-7
        assert instr.ch_1.skew_factor == 1e-7


def test_channel_setup():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
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
        assert instr.ch_1.current_configuration == {"channel": 1,
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
            [(b"CHDR OFF", None),
             (b"MSIZ 14M", None),
             (b"MSIZ?", b"14M"),
             (b"MSIZ 1.4M", None),
             (b"MSIZ?", b"1.4M"),
             (b"MSIZ 7K", None),
             (b"MSIZ?", b"7K")
             ]
    ) as instr:
        instr.memory_size = 14e6
        assert instr.memory_size == 14e6
        instr.memory_size = 14e5
        assert instr.memory_size == 14e5
        instr.memory_size = 7e3
        assert instr.memory_size == 7e3


def test_sample_size():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
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
            [(b"CHDR OFF", None),
             (b"WFSU?", b"SP,1,NP,0,FP,0"),
             (b"ACQW?", b"SAMPLING"),
             (b"SARA?", b"1.00E+09"),
             (b"SAST?", b"Trig'd"),
             (b"MSIZ?", b"7M"),
             (b"TDIV?", b"5.00E-04"),
             (b"TRDL?", b"-0.00E+00"),
             (b"SANU? C1", b"1.75E+06"),
             (b"C1:VDIV?", b"5.00E-02"),
             (b"C1:OFST?", b"-1.50E-01"),
             (b"C1:UNIT?", b"V"),
             ]
    ) as instr:
        assert instr.waveform_preamble == {
            "sparsing": 1,
            "requested_points": 0,
            "transmitted_points": None,
            "sampled_points": 1.75e6,
            "first_point": 0,
            "memory_size": 7e6,
            "source": "C1",
            "type": "normal",
            "average": None,
            "sampling_rate": 1e9,
            "grid_number": 14,
            "status": "triggered",
            "xdiv": 5e-4,
            "xoffset": 0,
            "ydiv": 0.05,
            "yoffset": -0.150,
            "unit": "V"
        }


def test_download_one_point():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"WFSU SP,1", None),
             (b"WFSU NP,1", None),
             (b"WFSU FP,0", None),
             (b"SANU? C1", b"7.00E+06"),
             (b"WFSU NP,1", None),
             (b"WFSU FP,0", None),
             (b"C1:WF? DAT2", b"DAT2,#9000000001" + b"\x01" + b"\n\n"),
             (b"WFSU?", b"SP,1,NP,2,FP,0"),
             (b"ACQW?", b"SAMPLING"),
             (b"SARA?", b"1.00E+09"),
             (b"SAST?", b"Stop"),
             (b"MSIZ?", b"7M"),
             (b"TDIV?", b"5.00E-04"),
             (b"TRDL?", b"-0.00E+00"),
             (b"SANU? C1", b"7.00E+06"),
             (b"C1:VDIV?", b"5.00E-02"),
             (b"C1:OFST?", b"-1.50E-01"),
             (b"C1:UNIT?", b"V")
             ],
            connection_attributes={'chunk_size': 0},
    ) as instr:
        y, x, preamble = instr.download_waveform(source="c1", requested_points=1, sparsing=1)
        assert preamble == {
            "sparsing": 1,
            "requested_points": 1,
            "memory_size": 7e6,
            "sampled_points": 7e6,
            "transmitted_points": 1,
            "first_point": 0,
            "source": "C1",
            "type": "normal",
            "average": None,
            "sampling_rate": 1e9,
            "grid_number": 14,
            "status": "stopped",
            "xdiv": 5e-4,
            "xoffset": 0,
            "ydiv": 0.05,
            "yoffset": -0.150,
            "unit": "V"
        }
        assert len(x) == 1
        assert len(y) == 1
        assert y[0] == 1 * 0.05 / 25. + 0.150


def test_download_two_points():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"WFSU SP,1", None),
             (b"WFSU NP,2", None),
             (b"WFSU FP,0", None),
             (b"SANU? C1", b"7.00E+06"),
             (b"WFSU NP,2", None),
             (b"WFSU FP,0", None),
             (b"C1:WF? DAT2", b"DAT2,#9000000002" + b"\x01\x01" + b"\n\n"),
             (b"WFSU?", b"SP,1,NP,2,FP,0"),
             (b"ACQW?", b"SAMPLING"),
             (b"SARA?", b"1.00E+09"),
             (b"SAST?", b"Stop"),
             (b"MSIZ?", b"7M"),
             (b"TDIV?", b"5.00E-04"),
             (b"TRDL?", b"-0.00E+00"),
             (b"SANU? C1", b"7.00E+06"),
             (b"C1:VDIV?", b"5.00E-02"),
             (b"C1:OFST?", b"-1.50E-01"),
             (b"C1:UNIT?", b"V")
             ],
            connection_attributes={'chunk_size': 0},
    ) as instr:
        y, x, preamble = instr.download_waveform(source="c1", requested_points=2, sparsing=1)
        assert preamble == {
            "sparsing": 1,
            "requested_points": 2,
            "memory_size": 7e6,
            "sampled_points": 7e6,
            "transmitted_points": 2,
            "first_point": 0,
            "source": "C1",
            "type": "normal",
            "average": None,
            "sampling_rate": 1e9,
            "grid_number": 14,
            "status": "stopped",
            "xdiv": 5e-4,
            "xoffset": 0,
            "ydiv": 0.05,
            "yoffset": -0.150,
            "unit": "V"
        }
        assert len(x) == 2
        assert len(y) == 2
        assert x[0] == -5e-4 * 14 / 2.
        assert y[0] == 1 * 0.05 / 25. + 0.150
        assert x[1] == x[0] + 1 / 1e9
        assert y[1] == y[0]


def test_trigger():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
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
            [(b"CHDR OFF", None),
             (b"DEF EQN,'C2*C4'", None),
             (b"DEF?", b"EQN,'C2*C4'"),
             ]
    ) as instr:
        instr.math_define = ("channel2", "*", "channel4")
        assert instr.math_define == ["EQN", "'C2*C4'"]


def test_math_vdiv():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"MTVD 1.00E+00V", None),
             (b"MTVD?", b"1.00E+00"),
             ]
    ) as instr:
        instr.math_vdiv = 1.0
        assert instr.math_vdiv == 1.0


def test_math_vpos():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"MTVP 120", None),
             (b"MTVP?", b"120"),
             ]
    ) as instr:
        instr.math_vpos = 120
        assert instr.math_vpos == 120


def test_display_parameter():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"PACU PKPK,C1", None),
             (b"PACU MEAN,C2", None)
             ]
    ) as instr:
        instr.display_parameter(parameter="PKPK", channel=1)
        instr.ch(2).display_parameter = "MEAN"


def test_measure_parameter():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"C2:PAVA? RISE", b"RISE,3.600000E-9"),
             (b"C3:PAVA? MEAN", b"MEAN,3.600000E-9"),
             ]
    ) as instr:
        assert instr.measure_parameter("RISE", "channel2") == 3.6e-9
        assert instr.ch_3.measure_parameter("MEAN") == 3.6e-9


def test_menu():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"MENU ON", None),
             (b"MENU?", b"ON"),
             (b"MENU OFF", None),
             (b"MENU?", b"OFF"),
             ]
    ) as instr:
        instr.menu = True
        assert instr.menu is True
        instr.menu = False
        assert instr.menu is False


def test_grid_display():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"GRDS FULL", None),
             (b"GRDS?", b"FULL"),
             ]
    ) as instr:
        instr.grid_display = "full"
        assert instr.grid_display == "full"


def test_intensity():
    with expected_protocol(
            LeCroyT3DSO1204,
            [(b"CHDR OFF", None),
             (b"INTS GRID,50,TRACE,100", None),
             (b"INTS?", b"GRID,50,TRACE,100"),
             ]
    ) as instr:
        instr.intensity = 50, 100
        assert instr.intensity == {"GRID": 50, "TRACE": 100}


if __name__ == '__main__':
    pytest.main()
