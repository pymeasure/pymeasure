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
from pymeasure.instruments.korad.ka_base import Mode
from pymeasure.test import expected_protocol
from pymeasure.instruments.korad.ka30xxp import KoradKA3005P

def test_voltage_setpoint():
    """Verify the voltage setpoint setter and getter."""
    with expected_protocol(
        KoradKA3005P,
        [("VSET1:2.2", None),
         ("VSET1?", "2.2")],
    ) as inst:
        inst.ch1.voltage_setpoint = 2.2
        assert inst.ch1.voltage_setpoint == 2.2

def test_voltage_measurement():
    """Verify the voltage measurement getter."""
    with expected_protocol(
        KoradKA3005P,
        [("VOUT1?", "2.2")],
    ) as inst:
        assert inst.ch1.voltage == 2.2

def test_overvoltage_protection():
    """Verify the overvoltage protection setter and getter"""
    with expected_protocol(
        KoradKA3005P,
        [("OVP1:1", None),
         ("OVP1?", "1"),
         ("OVP1?", "0")]
    ) as inst:
        inst.ch1.over_voltage_protection = True
        assert inst.ch1.over_voltage_protection is True
        assert inst.ch1.over_voltage_protection is False

def test_current_setpoint():
    """Verify the current setpoint setter and getter."""
    with expected_protocol(
        KoradKA3005P,
        [("ISET1:1.5", None),
         ("ISET1?", "1.5")],
    ) as inst:
        inst.ch1.current_setpoint = 1.5
        assert inst.ch1.current_setpoint == 1.5

def test_current_measurement():
    """Verify the current measurement getter."""
    with expected_protocol(
        KoradKA3005P,
        [("IOUT1?", "1.5")],
    ) as inst:
        assert inst.ch1.current == 1.5

def test_overcurrent_protection():
    """Verify the overcurrent protection setter and getter."""
    with expected_protocol(
        KoradKA3005P,
        [("OCP1:1", None),
         ("OCP1?", "1"),
         ("OCP1?", "0")]
    ) as inst:
        inst.ch1.over_current_protection = True
        assert inst.ch1.over_current_protection is True
        assert inst.ch1.over_current_protection is False

def test_version():
    """Verify the version getter."""
    with expected_protocol(
        KoradKA3005P,
        [("*IDN?", "KORADKA3005PV2.0")],
    ) as inst:
        assert inst.version == [2, 0]

def test_model():
    """Verify the model getter."""
    with expected_protocol(
        KoradKA3005P,
        [("*IDN?", "KORADKA3005PV2.0")],
    ) as inst:
        assert inst.model == "KA3005P"

def test_id():
    """Verify the ID getter."""
    with expected_protocol(
        KoradKA3005P,
        [("*IDN?", "KORADKA3005PV2.0")],
    ) as inst:
        assert inst.id == "KORADKA3005PV2.0"

def test_channel_mode():
    """Verify the channel mode getter."""
    with expected_protocol(
        KoradKA3005P,
        [("STATUS?", 0x01)],
    ) as inst:
        assert inst.ch1.mode == Mode.CV

def test_output_control():
    """Verify the output control getter and setter."""
    with expected_protocol(
        KoradKA3005P,
        [("OUT1", None),
         ("OUT?", "1"),
         ("OUT?", "0")
         ],
    ) as inst:
        inst.output_enabled = True
        assert inst.output_enabled is True
        assert inst.output_enabled is False

#TODO: it would be nice to also validate write timing