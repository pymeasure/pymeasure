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
from pymeasure.instruments.rigol import DG5000Pro


def test_init():
    with expected_protocol(
            DG5000Pro,
            [],
    ):
        pass  # Verify the expected communication.


def test_channel_1_amplitude_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage 1.000000', None)],
    ) as inst:
        inst.channel_1.amplitude = 1


def test_channel_1_amplitude_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage?', b'+1.000000200000000E+00\n')],
    ) as inst:
        assert inst.channel_1.amplitude == 1.0000002


def test_channel_1_frequency_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:FREQuency 1000.000000', None)],
    ) as inst:
        inst.channel_1.frequency = 1000


def test_channel_1_frequency_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:FREQuency?', b'+1.000000000000000E+03\n')],
    ) as inst:
        assert inst.channel_1.frequency == 1000.0


def test_channel_1_function_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:FUNCtion SIN', None)],
    ) as inst:
        inst.channel_1.function = 'SIN'


def test_channel_1_function_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:FUNCtion?', b'SIN\n')],
    ) as inst:
        assert inst.channel_1.function == 'SIN'


def test_channel_1_load_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':OUTPut1:LOAD infinity', None)],
    ) as inst:
        inst.channel_1.load = 'infinity'


def test_channel_1_load_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':OUTPut1:LOAD?', b'9.9E+37\n')],
    ) as inst:
        assert inst.channel_1.load == 9.9e+37


def test_channel_1_offset_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage:OFFset 1.000000', None)],
    ) as inst:
        inst.channel_1.offset = 1


def test_channel_1_offset_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage:OFFset?', b'+1.000000000000000E+00\n')],
    ) as inst:
        assert inst.channel_1.offset == 1.0


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':OUTPut1:STATe 1', None)],
     True),
    ([(b':OUTPut1:STATe 0', None)],
     False),
))
def test_channel_1_output_enabled_setter(comm_pairs, value):
    with expected_protocol(
            DG5000Pro,
            comm_pairs,
    ) as inst:
        inst.channel_1.output_enabled = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':OUTPut1:STATE?', b'1 \n')],
     True),
    ([(b':OUTPut1:STATE?', b'0 \n')],
     False),
))
def test_channel_1_output_enabled_getter(comm_pairs, value):
    with expected_protocol(
            DG5000Pro,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.output_enabled == value


def test_channel_1_phase_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PHASe 90.000000', None)],
    ) as inst:
        inst.channel_1.phase = 90


def test_channel_1_phase_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PHASe?', b'+9.000000000000000E+01\n')],
    ) as inst:
        assert inst.channel_1.phase == 90.0


def test_channel_1_psk_phase_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:PHASe 90.000000', None)],
    ) as inst:
        inst.channel_1.psk_phase = 90


def test_channel_1_psk_phase_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:PHASe?', b'+9.000000000000000E+01\n')],
    ) as inst:
        assert inst.channel_1.psk_phase == 90.0


def test_channel_1_psk_polarity_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:POLarity NEG', None)],
    ) as inst:
        inst.channel_1.psk_polarity = 'NEG'


def test_channel_1_psk_polarity_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:POLarity?', b'NEG\n')],
    ) as inst:
        assert inst.channel_1.psk_polarity == 'NEG'


def test_channel_1_psk_port_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:PORT REAR', None)],
    ) as inst:
        inst.channel_1.psk_port = 'REAR'


def test_channel_1_psk_port_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:PORT?', b'REAR\n')],
    ) as inst:
        assert inst.channel_1.psk_port == 'REAR'


def test_channel_1_psk_source_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:SOURce INT', None)],
    ) as inst:
        inst.channel_1.psk_source = 'INT'


def test_channel_1_psk_source_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:PSKey:SOURce?', b'INT\n')],
    ) as inst:
        assert inst.channel_1.psk_source == 'INT'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SOURce1:PSKey:STATe 1', None)],
     True),
    ([(b':SOURce1:PSKey:STATe 0', None)],
     False),
))
def test_channel_1_psk_state_setter(comm_pairs, value):
    with expected_protocol(
            DG5000Pro,
            comm_pairs,
    ) as inst:
        inst.channel_1.psk_state = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b':SOURce1:PSKey:STATe?', b'1\n')],
     True),
    ([(b':SOURce1:PSKey:STATe?', b'0\n')],
     False),
))
def test_channel_1_psk_state_getter(comm_pairs, value):
    with expected_protocol(
            DG5000Pro,
            comm_pairs,
    ) as inst:
        assert inst.channel_1.psk_state == value


def test_channel_1_voltage_unit_setter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage:UNIT VPP', None)],
    ) as inst:
        inst.channel_1.voltage_unit = 'VPP'


def test_channel_1_voltage_unit_getter():
    with expected_protocol(
            DG5000Pro,
            [(b':SOURce1:VOLTage:UNIT?', b'VPP\n')],
    ) as inst:
        assert inst.channel_1.voltage_unit == 'VPP'


