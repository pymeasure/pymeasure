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
from pymeasure.instruments.agilent.agilent34450A import Agilent34450A

INITIALIZATION = ("SYST:ERR?", "+0, No Error")


class TestCurrent:
    def test_configure_current(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:CURR", None),
             (":SENS:CURR:RES DEF", None),
             (":SENS:CURR:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_current()

    def test_configure_current_ac(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:CURR:AC", None),
             (":SENS:CURR:AC:RES DEF", None),
             (":SENS:CURR:AC:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_current(ac=True)

    def test_current(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+1.2300E-4"),
             ],
        ) as inst:
            assert inst.current == 1.23e-4

    def test_current_ac(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "-1.2400E-6"),
             ],
        ) as inst:
            assert inst.current_ac == -1.24e-6

    @pytest.mark.parametrize("current_range", [100E-6, 1E-3, 10E-3, 100E-3, 1, 10,
                                               "MIN", "DEF", "MAX"])
    def test_current_range(self, current_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:RANG:AUTO 0;:SENS:CURR:RANG {current_range}", None),
             (":SENS:CURR:RANG?", current_range),
             ],
        ) as inst:
            inst.current_range = current_range
            assert inst.current_range == current_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_current_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:RANG:AUTO {mapping}", None),
             (":SENS:CURR:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.current_auto_range = state
            assert inst.current_auto_range == state

    @pytest.mark.parametrize("current_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                    "MIN", "DEF", "MAX"])
    def test_current_resolution(self, current_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:RES {current_resolution}", None),
             (":SENS:CURR:RES?", current_resolution),
             ],
        ) as inst:
            inst.current_resolution = current_resolution
            assert inst.current_resolution == current_resolution

    @pytest.mark.parametrize("current_ac_range", [10E-3, 100E-3, 1, 10,
                                                  "MIN", "DEF", "MAX"])
    def test_current_ac_range(self, current_ac_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:AC:RANG:AUTO 0;:SENS:CURR:AC:RANG {current_ac_range}", None),
             (":SENS:CURR:AC:RANG?", current_ac_range),
             ],
        ) as inst:
            inst.current_ac_range = current_ac_range
            assert inst.current_ac_range == current_ac_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_current_ac_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:AC:RANG:AUTO {mapping}", None),
             (":SENS:CURR:AC:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.current_ac_auto_range = state
            assert inst.current_ac_auto_range == state

    @pytest.mark.parametrize("current_ac_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                       "MIN", "DEF", "MAX"])
    def test_current_ac_resolution(self, current_ac_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CURR:AC:RES {current_ac_resolution}", None),
             (":SENS:CURR:AC:RES?", current_ac_resolution),
             ],
        ) as inst:
            inst.current_ac_resolution = current_ac_resolution
            assert inst.current_ac_resolution == current_ac_resolution


class TestVoltage:
    def test_configure_voltage(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:VOLT", None),
             (":SENS:VOLT:RES DEF", None),
             (":SENS:VOLT:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_voltage()

    def test_configure_voltage_ac(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:VOLT:AC", None),
             (":SENS:VOLT:AC:RES DEF", None),
             (":SENS:VOLT:AC:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_voltage(ac=True)

    def test_voltage(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+3.2300E-4"),
             ],
        ) as inst:
            assert inst.voltage == 3.23e-4

    def test_voltage_ac(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "-5.2400E-6"),
             ],
        ) as inst:
            assert inst.voltage_ac == -5.24e-6

    @pytest.mark.parametrize("voltage_range", [100E-3, 1, 10, 100, 1000,
                                               "MIN", "DEF", "MAX"])
    def test_voltage_range(self, voltage_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:RANG:AUTO 0;:SENS:VOLT:RANG {voltage_range}", None),
             (":SENS:VOLT:RANG?", voltage_range),
             ],
        ) as inst:
            inst.voltage_range = voltage_range
            assert inst.voltage_range == voltage_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_voltage_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:RANG:AUTO {mapping}", None),
             (":SENS:VOLT:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.voltage_auto_range = state
            assert inst.voltage_auto_range == state

    @pytest.mark.parametrize("voltage_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                    "MIN", "DEF", "MAX"])
    def test_voltage_resolution(self, voltage_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:RES {voltage_resolution}", None),
             (":SENS:VOLT:RES?", voltage_resolution),
             ],
        ) as inst:
            inst.voltage_resolution = voltage_resolution
            assert inst.voltage_resolution == voltage_resolution

    @pytest.mark.parametrize("voltage_ac_range", [100E-3, 1, 10, 100, 750,
                                                  "MIN", "DEF", "MAX"])
    def test_voltage_ac_range(self, voltage_ac_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:AC:RANG:AUTO 0;:SENS:VOLT:AC:RANG {voltage_ac_range}", None),
             (":SENS:VOLT:AC:RANG?", voltage_ac_range),
             ],
        ) as inst:
            inst.voltage_ac_range = voltage_ac_range
            assert inst.voltage_ac_range == voltage_ac_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_voltage_ac_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:AC:RANG:AUTO {mapping}", None),
             (":SENS:VOLT:AC:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.voltage_ac_auto_range = state
            assert inst.voltage_ac_auto_range == state

    @pytest.mark.parametrize("voltage_ac_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                       "MIN", "DEF", "MAX"])
    def test_voltage_ac_resolution(self, voltage_ac_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:VOLT:AC:RES {voltage_ac_resolution}", None),
             (":SENS:VOLT:AC:RES?", voltage_ac_resolution),
             ],
        ) as inst:
            inst.voltage_ac_resolution = voltage_ac_resolution
            assert inst.voltage_ac_resolution == voltage_ac_resolution


class TestResistance:
    def test_configure_resistance(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:RES", None),
             (":SENS:RES:RES DEF", None),
             (":SENS:RES:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_resistance()

    def test_configure_resistance_4w(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:FRES", None),
             (":SENS:FRES:RES DEF", None),
             (":SENS:FRES:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_resistance(wires=4)

    def test_resistance(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+2.670E+4"),
             ],
        ) as inst:
            assert inst.resistance == 2.67e4

    def test_resistance_4w(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+2.690E+4"),
             ],
        ) as inst:
            assert inst.resistance_4w == 2.69e4

    @pytest.mark.parametrize("resistance_range", [100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6,
                                                  "MIN", "DEF", "MAX"])
    def test_resistance_range(self, resistance_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:RES:RANG:AUTO 0;:SENS:RES:RANG {resistance_range}", None),
             (":SENS:RES:RANG?", resistance_range),
             ],
        ) as inst:
            inst.resistance_range = resistance_range
            assert inst.resistance_range == resistance_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_resistance_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:RES:RANG:AUTO {mapping}", None),
             (":SENS:RES:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.resistance_auto_range = state
            assert inst.resistance_auto_range == state

    @pytest.mark.parametrize("resistance_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                       "MIN", "DEF", "MAX"])
    def test_resistance_resolution(self, resistance_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:RES:RES {resistance_resolution}", None),
             (":SENS:RES:RES?", resistance_resolution),
             ],
        ) as inst:
            inst.resistance_resolution = resistance_resolution
            assert inst.resistance_resolution == resistance_resolution

    @pytest.mark.parametrize("resistance_4w_range", [100, 1E3, 10E3, 100E3, 1E6, 10E6, 100E6,
                                                     "MIN", "DEF", "MAX"])
    def test_resistance_4w_range(self, resistance_4w_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FRES:RANG:AUTO 0;:SENS:FRES:RANG {resistance_4w_range}", None),
             (":SENS:FRES:RANG?", resistance_4w_range),
             ],
        ) as inst:
            inst.resistance_4w_range = resistance_4w_range
            assert inst.resistance_4w_range == resistance_4w_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_resistance_4w_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FRES:RANG:AUTO {mapping}", None),
             (":SENS:FRES:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.resistance_4w_auto_range = state
            assert inst.resistance_4w_auto_range == state

    @pytest.mark.parametrize("resistance_4w_resolution", [3.00E-5, 2.00E-5, 1.50E-6,
                                                          "MIN", "DEF", "MAX"])
    def test_voltage_ac_resolution(self, resistance_4w_resolution):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FRES:RES {resistance_4w_resolution}", None),
             (":SENS:FRES:RES?", resistance_4w_resolution),
             ],
        ) as inst:
            inst.resistance_4w_resolution = resistance_4w_resolution
            assert inst.resistance_4w_resolution == resistance_4w_resolution


class TestFrequency:
    def test_configure_frequency(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:VOLT:AC", None),
             (":configure:freq", None),
             (":SENS:FREQ:VOLT:RANG:AUTO 1", None),
             (":SENS:FREQ:APER DEF", None),
             ],
        ) as inst:
            inst.configure_frequency()

    def test_configure_frequency_from_ac_current(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:CURR:AC", None),
             (":configure:freq", None),
             (":SENS:FREQ:CURR:RANG:AUTO 1", None),
             (":SENS:FREQ:APER DEF", None),
             ],
        ) as inst:
            inst.configure_frequency(measured_from="current_ac")

    def test_frequency(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+5.680E+3"),
             ],
        ) as inst:
            assert inst.frequency == 5.68e3

    @pytest.mark.parametrize("frequency_current_range", [10E-3, 100E-3, 1, 10,
                                                         "MIN", "DEF", "MAX"])
    def test_frequency_current_range(self, frequency_current_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FREQ:CURR:RANG:AUTO 0;:SENS:FREQ:CURR:RANG {frequency_current_range}", None),
             (":SENS:FREQ:CURR:RANG?", frequency_current_range),
             ],
        ) as inst:
            inst.frequency_current_range = frequency_current_range
            assert inst.frequency_current_range == frequency_current_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_frequency_current_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FREQ:CURR:RANG:AUTO {mapping}", None),
             (":SENS:FREQ:CURR:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.frequency_current_auto_range = state
            assert inst.frequency_current_auto_range == state

    @pytest.mark.parametrize("frequency_voltage_range", [100E-3, 1, 10, 100, 750,
                                                         "MIN", "DEF", "MAX"])
    def test_frequency_voltage_range(self, frequency_voltage_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FREQ:VOLT:RANG:AUTO 0;:SENS:FREQ:VOLT:RANG {frequency_voltage_range}", None),
             (":SENS:FREQ:VOLT:RANG?", frequency_voltage_range),
             ],
        ) as inst:
            inst.frequency_voltage_range = frequency_voltage_range
            assert inst.frequency_voltage_range == frequency_voltage_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_frequency_voltage_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FREQ:VOLT:RANG:AUTO {mapping}", None),
             (":SENS:FREQ:VOLT:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.frequency_voltage_auto_range = state
            assert inst.frequency_voltage_auto_range == state

    @pytest.mark.parametrize("frequency_aperture", [100E-3, 1,
                                                    "MIN", "DEF", "MAX"])
    def test_frequency_aperture(self, frequency_aperture):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:FREQ:APER {frequency_aperture}", None),
             (":SENS:FREQ:APER?", frequency_aperture),
             ],
        ) as inst:
            inst.frequency_aperture = frequency_aperture
            assert inst.frequency_aperture == frequency_aperture


class TestTemparature:
    def test_configure_temperature(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:TEMP", None),
             ],
        ) as inst:
            inst.configure_temperature()

    def test_temperature(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+2.680E+1"),
             ],
        ) as inst:
            assert inst.temperature == 26.8


class TestDiode:
    def test_configure_diode(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:DIOD", None),
             ],
        ) as inst:
            inst.configure_diode()

    def test_diode(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+5.82E-1"),
             ],
        ) as inst:
            assert inst.diode == 0.582


class TestCapacitance:
    def test_configure_capacitance(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:CAP", None),
             (":SENS:CAP:RANG:AUTO 1", None),
             ],
        ) as inst:
            inst.configure_capacitance()

    def test_capacitance(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+3.58E-9"),
             ],
        ) as inst:
            assert inst.capacitance == 3.58e-9

    @pytest.mark.parametrize("capacitance_range",
                             [1E-9, 10E-9, 100E-9, 1E-6, 10E-6, 100E-6, 1E-3, 10E-3,
                              "MIN", "DEF", "MAX"])
    def test_capacitance_range(self, capacitance_range):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CAP:RANG:AUTO 0;:SENS:CAP:RANG {capacitance_range}", None),
             (":SENS:CAP:RANG?", capacitance_range),
             ],
        ) as inst:
            inst.capacitance_range = capacitance_range
            assert inst.capacitance_range == capacitance_range

    @pytest.mark.parametrize("state, mapping",
                             [(True, 1),
                              (False, 0),
                              ])
    def test_capacitance_auto_range(self, state, mapping):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (f":SENS:CAP:RANG:AUTO {mapping}", None),
             (":SENS:CAP:RANG:AUTO?", mapping),
             ],
        ) as inst:
            inst.capacitance_auto_range = state
            assert inst.capacitance_auto_range == state


class TestContinuity:
    def test_configure_continuity(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":configure:CONT", None),
             ],
        ) as inst:
            inst.configure_continuity()

    def test_continuity(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":READ?", "+6.70E-1"),
             ],
        ) as inst:
            assert inst.continuity == 0.67


class TestMain:
    def test_beep(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":SYST:BEEP", None),
             ],
        ) as inst:
            inst.beep()

    def test_local(self):
        with expected_protocol(
            Agilent34450A,
            [INITIALIZATION,
             (":SYST:LOC", None),
             ],
        ) as inst:
            inst.local()
