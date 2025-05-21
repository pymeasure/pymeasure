#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
from pymeasure.instruments.aculight.argos import Argos, State


def test_init():
    with expected_protocol(
            Argos,
            []):
        pass  # Verify init


def test_temperature_setpoint():
    with expected_protocol(
            Argos,
            [("temp 45.500", " Temperature setting changed")]
    ) as inst:
        inst.temperature_setpoint = 45.5


def test_etalon():
    with expected_protocol(
            Argos,
            [("etalon -3.450", " Etalon setting changed")]
    ) as inst:
        inst.etalon = -3.45


def test_seed():
    with expected_protocol(
            Argos,
            [("seed 2.350", " Seed setting changed")]
    ) as inst:
        inst.seed_voltage = 2.35


def test_state():
    with expected_protocol(
            Argos,
            [("state",
              " Crystal Temp Set = 55.000\n\r Etalon Angle Set = -0.020\n\r"
              " Seed Source Set  = 0.000\n\r Crystal Temp = 54.900")]
    ) as inst:
        assert inst.state == State(crystal_temperature_setpoint=55, crystal_temperature=54.9,
                                   etalon_angle=-0.02, seed_voltage=0)


def test_temperature_setpoint_getter():
    with expected_protocol(
            Argos,
            [("state",
              " Crystal Temp Set = 55.000\n\r Etalon Angle Set = -0.020\n\r"
              " Seed Source Set  = 0.000\n\r Crystal Temp = 54.900")]
    ) as inst:
        assert inst.temperature_setpoint == 55.


def test_etalon_getter():
    with expected_protocol(
            Argos,
            [("state",
              " Crystal Temp Set = 55.000\n\r Etalon Angle Set = -0.020\n\r"
              " Seed Source Set  = 0.000\n\r Crystal Temp = 54.900")]
    ) as inst:
        assert inst.etalon == -0.02


def test_seed_getter():
    with expected_protocol(
            Argos,
            [("state",
              " Crystal Temp Set = 55.000\n\r Etalon Angle Set = -0.020\n\r"
              " Seed Source Set  = 0.000\n\r Crystal Temp = 54.900")]
    ) as inst:
        assert inst.seed_voltage == 0


def test_temperature():
    with expected_protocol(
            Argos,
            [("state",
              " Crystal Temp Set = 55.000\n\r Etalon Angle Set = -0.020\n\r"
              " Seed Source Set  = 0.000\n\r Crystal Temp = 54.900")]
    ) as inst:
        assert inst.temperature == 54.9


def test_version():
    with expected_protocol(
        Argos,
        [("ver", "Software Version 38-000028-008-T03")],
    ) as inst:
        assert inst.version == "Software Version 38-000028-008-T03"
