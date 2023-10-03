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

from pymeasure.test import expected_protocol
from pymeasure.instruments import Instrument

from pymeasure.instruments.activetechnologies import AWG401x_AFG
from pymeasure.instruments.activetechnologies.AWG401x import ChannelAFG, SequenceEntry


class SequencerInstrument(Instrument):
    """A class in order to test SequenceEntry."""

    def __init__(self, adapter, **kwargs):
        super().__init__(adapter, "SequencerInstrument", **kwargs)
        self.waveforms = {}
        self.se = SequenceEntry(self, 1, 7)


# AFG Tests
AFG_init_comm = [
    # ("*IDN?", "x,AWG4012"),
    ("SOURce1:INITDELay? MINimum", "1"),
    ("SOURce1:INITDELay? MAXimum", "2"),
    ("SOURce1:VOLTage:LEVel:IMMediate:LOW? MINimum", "1"),
    ("SOURce1:VOLTage:LEVel:IMMediate:LOW? MAXimum", "2"),
    ("SOURce1:VOLTage:LEVel:IMMediate:HIGH? MINimum", "1"),
    ("SOURce1:VOLTage:LEVel:IMMediate:HIGH? MAXimum", "2"),
    ("SOURce1:VOLTage:LEVel:IMMediate:AMPLitude? MINimum", "VPP1"),
    ("SOURce1:VOLTage:LEVel:IMMediate:AMPLitude? MAXimum", "VPP2"),
    ("SOURce1:VOLTage:LEVel:IMMediate:OFFSet? MINimum", "1"),
    ("SOURce1:VOLTage:LEVel:IMMediate:OFFSet? MAXimum", "2"),
    ("SOURce1:VOLTage:BASELINE:OFFSET? MINimum", "1"),
    ("SOURce1:VOLTage:BASELINE:OFFSET? MAXimum", "2"),
    ("SOURce1:FREQuency? MINimum", "1"),
    ("SOURce1:FREQuency? MAXimum", "2"),
    ("SOURce1:PHASe:ADJust? MINimum", "1"),
    ("SOURce1:PHASe:ADJust? MAXimum", "2"),
    ("SOURce2:INITDELay? MINimum", "1"),
    ("SOURce2:INITDELay? MAXimum", "2"),
    ("SOURce2:VOLTage:LEVel:IMMediate:LOW? MINimum", "1"),
    ("SOURce2:VOLTage:LEVel:IMMediate:LOW? MAXimum", "2"),
    ("SOURce2:VOLTage:LEVel:IMMediate:HIGH? MINimum", "1"),
    ("SOURce2:VOLTage:LEVel:IMMediate:HIGH? MAXimum", "2"),
    ("SOURce2:VOLTage:LEVel:IMMediate:AMPLitude? MINimum", "VPP1"),
    ("SOURce2:VOLTage:LEVel:IMMediate:AMPLitude? MAXimum", "VPP2"),
    ("SOURce2:VOLTage:LEVel:IMMediate:OFFSet? MINimum", "1"),
    ("SOURce2:VOLTage:LEVel:IMMediate:OFFSet? MAXimum", "2"),
    ("SOURce2:VOLTage:BASELINE:OFFSET? MINimum", "1"),
    ("SOURce2:VOLTage:BASELINE:OFFSET? MAXimum", "2"),
    ("SOURce2:FREQuency? MINimum", "1"),
    ("SOURce2:FREQuency? MAXimum", "2"),
    ("SOURce2:PHASe:ADJust? MINimum", "1"),
    ("SOURce2:PHASe:ADJust? MAXimum", "2"),
    ("*IDN?", "x,AWG4012"),
]


def test_AFG_init():
    with expected_protocol(
            AWG401x_AFG,
            AFG_init_comm,
    ) as inst:
        assert len(inst.channels) == 2
        assert isinstance(inst.ch_1, ChannelAFG)


def test_AFG_frequency_setter():
    with expected_protocol(
            AWG401x_AFG,
            [*AFG_init_comm,
             ("SOURce2:FREQuency 1.5", None),
             ],
    ) as inst:
        inst.ch_2.frequency = 1.5


def test_AFG_frequency_getter():
    with expected_protocol(
            AWG401x_AFG,
            [*AFG_init_comm,
             ("SOURce2:FREQuency?", "1.5"),
             ],
    ) as inst:
        assert inst.ch_2.frequency == 1.5


# SequenceEntry Tests
Sequence_init_comm = [
    ("SEQuence:ELEM7:LENGth? MINimum", "1"),
    ("SEQuence:ELEM7:LENGth? MAXimum", "2"),
    ("SEQuence:ELEM7:LOOP:COUNt? MINimum", "1"),
    ("SEQuence:ELEM7:LOOP:COUNt? MAXimum", "2"),
    ("SEQuence:ELEM7:AMPlitude1? MINimum", "1"),
    ("SEQuence:ELEM7:AMPlitude1? MAXimum", "2"),
    ("SEQuence:ELEM7:OFFset1? MINimum", "1"),
    ("SEQuence:ELEM7:OFFset1? MAXimum", "2"),
    ("SEQuence:ELEM7:VOLTage:HIGH1? MINimum", "1"),
    ("SEQuence:ELEM7:VOLTage:HIGH1? MAXimum", "2"),
    ("SEQuence:ELEM7:VOLTage:LOW1? MINimum", "1"),
    ("SEQuence:ELEM7:VOLTage:LOW1? MAXimum", "2"),
]


def test_SequenceEntry_init():
    with expected_protocol(
            SequencerInstrument,
            Sequence_init_comm,
    ):
        pass  # verify init


def test_SequenceEntry_voltage_amplitude_setter():
    with expected_protocol(
            SequencerInstrument,
            [*Sequence_init_comm,
             ("SEQuence:ELEM7:AMPlitude1 1.5", None)],
    ) as inst:
        inst.se.ch_1.voltage_amplitude = 1.5


def test_SequenceEntry_voltage_amplitude_getter():
    with expected_protocol(
            SequencerInstrument,
            [*Sequence_init_comm,
             ("SEQuence:ELEM7:AMPlitude1?", "1.5")],
    ) as inst:
        assert inst.se.ch_1.voltage_amplitude == 1.5
