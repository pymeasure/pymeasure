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
# clear

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.thorlabs import (
    ThorlabsPM100USB,
    ThorlabsPM100A,
    ThorlabsPM100D,
    ThorlabsPM100D2,
    ThorlabsPM100D3,
)
from pymeasure.instruments.thorlabs.thorlabspm100usb import SensorTypes

PM100D_S130C_INIT_COMMS = ("SYST:SENSOR:IDN?", "S130C,210921324,21-SEP-2021,1,3,33")
PM100D2_S130C_INIT_COMMS = ("SYST:SENSOR:IDN?", '"S130C","210921324","21-SEP-2021",1,3,2147484069')

INSTR_CLS_PROTOCOL_LIST = [
    (ThorlabsPM100USB, [PM100D_S130C_INIT_COMMS]),
    (ThorlabsPM100A, [PM100D_S130C_INIT_COMMS]),
    (ThorlabsPM100D, [PM100D_S130C_INIT_COMMS]),
    (ThorlabsPM100D2, [PM100D2_S130C_INIT_COMMS]),
    (ThorlabsPM100D3, [PM100D2_S130C_INIT_COMMS]),
]


def test_configure_sensor():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        with expected_protocol(instr_cls, init_protocol) as inst:
            assert inst.sensor_name == "S130C"
            assert inst.sensor_sn == "210921324"
            assert inst.sensor_cal_msg == "21-SEP-2021"
            assert inst.sensor_type == 1
            assert inst.sensor_subtype == 3
            assert type(inst.sensor_flags) is int
            assert inst.is_power_sensor
            assert inst.is_current_sensor
            assert not inst.is_energy_sensor
            assert not inst.is_voltage_sensor
            assert not inst.is_temperature_sensor


def test_wavelength_setter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [
            ("SENS:CORR:WAV? MIN", 500),
            ("SENS:CORR:WAV? MAX", 2000),
            ("SENSE:CORR:WAV 1500", None),
        ]
        with expected_protocol(instr_cls, protocol) as inst:
            inst.wavelength = 1500


def test_wavelength_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("SENSE:CORR:WAV?", 1500)]
        with expected_protocol(instr_cls, protocol) as inst:
            assert inst.wavelength == 1500


def test_power_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:POW?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            assert inst.power == 1e-3


def test_power_density_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:PDEN?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            assert inst.power_density == 1e-3


def test_energy_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:ENER?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            inst.sensor_type = SensorTypes.PYROELECTRIC  # Override for test
            assert inst.energy == 1e-3


def test_energy_raises():
    for instr_cls, protocol in INSTR_CLS_PROTOCOL_LIST:
        with expected_protocol(instr_cls, protocol) as inst:
            with pytest.raises(AttributeError):
                assert inst.energy == 1e-3


def test_energy_density_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:EDEN?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            inst.sensor_type = SensorTypes.PYROELECTRIC  # Override for test
            assert inst.energy_density == 1e-3


def test_current_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:CURR?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            assert inst.current == 1e-3


def test_voltage_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:VOLT?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            inst.sensor_type = SensorTypes.PYROELECTRIC  # Override for test
            assert inst.voltage == 1e-3


def test_temperature_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:TEMP?", 1e-3)]
        with expected_protocol(instr_cls, protocol) as inst:
            inst.is_temperature_sensor = True  # Override for test
            assert inst.temperature == 1e-3


def test_frequency_getter():
    for instr_cls, init_protocol in INSTR_CLS_PROTOCOL_LIST:
        protocol = init_protocol + [("MEAS:FREQ?", 100)]
        with expected_protocol(instr_cls, protocol) as inst:
            assert inst.frequency == 100
