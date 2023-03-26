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
from pymeasure.test import expected_protocol

from pymeasure.instruments.ipgphotonics.yar import YAR


init_comm = [("RNP", "RNP: 0.200"), ("RMP", "RMP: 10.5"), ("RDPT", "RDPT: 0.100")]

################################
# Values according to the manual


def test_init():
    """This test tests already getting min/max output power."""
    with expected_protocol(
            YAR,
            init_comm
    ):
        pass


def test_status_emission():
    with expected_protocol(
            YAR,
            init_comm + [("STA", "STA: 1")]
    ) as inst:
        assert inst.status == YAR.Status.EMISSION


def test_status_backreflection():
    with expected_protocol(
            YAR,
            init_comm + [("STA", "STA: 131072")]
    ) as inst:
        assert inst.status == YAR.Status.HIGH_BACKREFLECTION


def test_emission_enabled_getter():
    with expected_protocol(
            YAR,
            init_comm + [("STA", "STA:1")]
    ) as inst:
        assert inst.emission_enabled is True


def test_emission_enabled_setter_on():
    with expected_protocol(
            YAR,
            init_comm + [("EMON", "EMON")]
    ) as inst:
        inst.emission_enabled = True


def test_emission_enabled_setter_off():
    with expected_protocol(
            YAR,
            init_comm + [("EMOFF", "EMOFF")]
    ) as inst:
        inst.emission_enabled = False


def test_power():
    with expected_protocol(
            YAR,
            init_comm + [("ROP", "ROP: 3.45")]
    ) as inst:
        assert inst.power == 3.45


def test_power_off():
    """Verify, that power 'Off' is translated to 0."""
    with expected_protocol(
            YAR,
            init_comm + [("ROP", "ROP: Off")]
    ) as inst:
        assert inst.power == 0


def test_power_low():
    """Verify, that power 'Low' is translated to the default minimum 0.1."""
    with expected_protocol(
            YAR,
            init_comm + [("ROP", "ROP: Low")]
    ) as inst:
        assert inst.power == 0.1


def test_init_sets_minimum_display_power():
    """Test, that a different minimum power is shown in the translation of 'Low'."""
    # not in the manual!
    with expected_protocol(
            YAR,
            # init_comm is modified
            [("RNP", "RNP: 0.200"), ("RMP", "RMP: 10.5"), ("RDPT", "RDPT: 5"),
             ("ROP", "ROP: Low")]
    ) as inst:
        assert inst.power == 5


def test_power_setpoint_getter():
    with expected_protocol(
            YAR,
            init_comm + [("RPS", "RPS: 1.23")]
    ) as inst:
        assert inst.power_setpoint == 1.23


def test_power_setpoint_setter():
    with expected_protocol(
            YAR,
            init_comm + [("SPS 9.7", "SPS: 9.7")]
    ) as inst:
        inst.power_setpoint = 9.7


def test_power_setpoint_setter_out_of_range_driver():
    with expected_protocol(
            YAR,
            # init_comm is modified
            [("RNP", "RNP: 0.200"), ("RMP", "RMP: 10.5"), ("RDPT", "RDPT: 0.100")]
    ) as inst:
        with pytest.raises(ValueError):
            inst.power_setpoint = 20


def test_power_setpoint_setter_out_of_range_device():
    with expected_protocol(
            YAR,
            init_comm + [("SPS 5", "ERR: Out of Range")]
    ) as inst:
        with pytest.raises(ConnectionError):
            inst.power_setpoint = 5


def test_current():
    with expected_protocol(
            YAR,
            init_comm + [("RDC", "RDC: 2.34")]
    ) as inst:
        assert inst.current == 2.34


def test_temperature():
    with expected_protocol(
            YAR,
            init_comm + [("RCT", "RCT: 28.9")]
    ) as inst:
        assert inst.temperature == 28.9


def test_wavelength_temperature_getter():
    with expected_protocol(
            YAR,
            init_comm + [("RWA", "RWA: 31.345")]
    ) as inst:
        assert inst.wavelength_temperature == 31.345


def test_wavelength_temperature_setter():
    with expected_protocol(
            YAR,
            init_comm + [("SWA 35.658", "SWA: 35.658")]
    ) as inst:
        inst.wavelength_temperature = 35.658


def test_seed_temperature():
    with expected_protocol(
            YAR,
            init_comm + [("RST", "RST: 31.345")]
    ) as inst:
        assert inst.temperature_seed == 31.345


def test_clear():
    with expected_protocol(
            YAR,
            init_comm + [("RERR", "RERR")]
    ) as inst:
        inst.clear()


def test_model():
    with expected_protocol(
            YAR,
            init_comm + [("RMN", "RMN: YLM-10-SF")]
    ) as inst:
        assert inst.id == "YLM-10-SF"


def test_firmware():
    with expected_protocol(
            YAR,
            init_comm + [("RFV", "RFV: 1.0.114")]
    ) as inst:
        assert inst.firmware == "1.0.114"


def test_minimum_display_power():
    with expected_protocol(
            YAR,
            init_comm + [("RDPT", "RDPT: 0.100")]
    ) as inst:
        assert inst.minimum_display_power == 0.1
