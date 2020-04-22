#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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

from time import sleep

import pytest
from pymeasure.instruments.agilent.agilent34450A import Agilent34450A
from pyvisa.errors import VisaIOError


class TestAgilent34450A:
    """
    Unit tests for Agilent34450A class.

    An Agilent34450A device should be connected to the computer.
    Indicate the resource address below.
    """

    # Resource address goes here:
    resource = "USB0::10893::45848::MY56511723::0::INSTR" # EQ0017

    # Test cases shared by multiple methods
    default_resolution_cases = [[3.00E-5, 3.00E-5], [2.00E-5, 2.00E-5], [1.50E-6, 1.50E-6],
                                ["MIN", 1.50E-6], ["MAX", 3.00E-5], ["DEF", 1.50E-6]]

    def test_dmm_initialization_bad(self):
        bad_resource = "USB0::10893::45848::MY12345678::0::INSTR"
        with pytest.raises(VisaIOError):
            dmm = Agilent34450A(bad_resource)

    def test_good_address(self):
        dmm = Agilent34450A(self.resource)
        dmm.shutdown()

    def test_reset(self):
        dmm = Agilent34450A(self.resource)
        # No error is raised
        dmm.reset()
        dmm.shutdown()

    def test_beep(self):
        dmm = Agilent34450A(self.resource)
        # Assert that a beep is audible
        dmm.beep()
        dmm.shutdown()

    def test_modes(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        cases = ['current', 'ac current', 'voltage', 'ac voltage', 'resistance',
                 '4w resistance', 'current frequency', 'voltage frequency',
                 'continuity', 'diode', 'temperature', 'capacitance']

        for case in cases:
            dmm.mode = case
            assert dmm.mode == case

        with pytest.raises(ValueError):
            dmm.mode = 'AAA'

        dmm.shutdown()

    def test_current_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        current_dc_range_cases = [[100E-6, 100E-6], [1E-3, 1E-3], [10E-3, 10E-3],
                                  [100E-3, 100E-3], [1, 1], ["MIN", 100E-6],
                                  ["MAX", 10], ["DEF", 100E-3]]
        for value, expected in current_dc_range_cases:
            dmm.current_range = value
            assert dmm.current_range == expected
        with pytest.raises(ValueError):
            dmm.current_range = "AAA"

        dmm.shutdown()

    def test_current_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.current_auto_range = True
        assert dmm.current_auto_range == 1
        dmm.current_auto_range = False
        assert dmm.current_auto_range == 0

        dmm.shutdown()

    def test_current_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.current_resolution = value
            assert dmm.current_resolution == expected
        with pytest.raises(ValueError):
            dmm.current_resolution = "AAA"

        dmm.shutdown()

    def test_current_ac_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        cases = [[10E-3, 10E-3], [100E-3, 100E-3], [1, 1],
                 ["MIN", 10E-3], ["MAX", 10], ["DEF", 100E-3]]
        for value, expected in cases:
            dmm.current_ac_range = value
            assert dmm.current_ac_range == expected
        with pytest.raises(ValueError):
            dmm.current_ac_range = "AAA"

        dmm.shutdown()

    def test_current_ac_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.current_ac_auto_range = True
        assert dmm.current_ac_auto_range == 1
        dmm.current_ac_auto_range = False
        assert dmm.current_ac_auto_range == 0

        dmm.shutdown()

    def test_current_ac_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.current_ac_resolution = value
            assert dmm.current_ac_resolution == expected
        with pytest.raises(ValueError):
            dmm.current_ac_resolution = "AAA"

        dmm.shutdown()

    def test_configure_current(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        # Test includes only what has not been tested in previous setter methods

        # No parameters specified
        dmm.configure_current()
        assert dmm.mode == "current"
        assert dmm.current_auto_range == 1
        assert dmm.current_resolution == 1.50E-6

        # Four possible paths
        dmm.configure_current(range=1, ac=True, resolution="MAX")
        assert dmm.mode == "ac current"
        assert dmm.current_ac_range == 1
        assert dmm.current_ac_auto_range == 0
        assert dmm.current_ac_resolution == 3.00E-5
        dmm.configure_current(range="AUTO", ac=True, resolution="MIN")
        assert dmm.mode == "ac current"
        assert dmm.current_ac_auto_range == 1
        assert dmm.current_ac_resolution == 1.50E-6
        dmm.configure_current(range=1, ac=False, resolution="MAX")
        assert dmm.mode == "current"
        assert dmm.current_range == 1
        assert dmm.current_auto_range == 0
        assert dmm.current_resolution == 3.00E-5
        dmm.configure_current(range="AUTO", ac=False, resolution="MIN")
        assert dmm.mode == "current"
        assert dmm.current_auto_range == 1
        assert dmm.current_resolution == 1.50E-6

        # Should raise TypeError
        with pytest.raises(TypeError):
            dmm.configure_current(ac="AAA")

        dmm.shutdown()

    def test_current_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "current"
        value = dmm.current
        assert type(value) is float

        dmm.shutdown()

    def test_current_ac_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "ac current"
        value = dmm.current_ac
        assert type(value) is float

        dmm.shutdown()

    def test_voltage_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        voltage_dc_range_cases = [[100E-3, 100E-3], [1, 1], [10, 10], [100, 100],
                                  [1000, 1000], ["MIN", 100E-3], ["MAX", 1000],
                                  ["DEF", 10]]
        for value, expected in voltage_dc_range_cases:
            dmm.voltage_range = value
            assert dmm.voltage_range == expected
        with pytest.raises(ValueError):
            dmm.voltage_range = "AAA"

        dmm.shutdown()

    def test_voltage_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.voltage_auto_range = True
        assert dmm.voltage_auto_range == 1
        dmm.voltage_auto_range = False
        assert dmm.voltage_auto_range == 0

        dmm.shutdown()

    def test_voltage_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.voltage_resolution = value
            assert dmm.voltage_resolution == expected
        with pytest.raises(ValueError):
            dmm.voltage_resolution = "AAA"

        dmm.shutdown()

    def test_voltage_ac_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        voltage_ac_range_cases = [[100E-3, 100E-3], [1, 1], [10, 10], [100, 100],
                                  [750, 750], ["MIN", 100E-3], ["MAX", 750],
                                  ["DEF", 10]]
        for value, expected in voltage_ac_range_cases:
            dmm.voltage_ac_range = value
            assert dmm.voltage_ac_range == expected
        with pytest.raises(ValueError):
            dmm.voltage_ac_range = "AAA"

        dmm.shutdown()

    def test_voltage_ac_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.voltage_ac_auto_range = True
        assert dmm.voltage_ac_auto_range == 1
        dmm.voltage_ac_auto_range = False
        assert dmm.voltage_ac_auto_range == 0

        dmm.shutdown()

    def test_voltage_ac_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.voltage_ac_resolution = value
            assert dmm.voltage_ac_resolution == expected
        with pytest.raises(ValueError):
            dmm.voltage_ac_resolution = "AAA"

        dmm.shutdown()

    def test_configure_voltage(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        # Test includes only what has not been tested in previous setter methods

        # No parameters specified
        dmm.configure_voltage()
        assert dmm.mode == "voltage"
        assert dmm.voltage_auto_range == 1
        assert dmm.voltage_resolution == 1.50E-6

        # Four possible paths
        dmm.configure_voltage(range=100, ac=True, resolution="MAX")
        assert dmm.mode == "ac voltage"
        assert dmm.voltage_ac_range == 100
        assert dmm.voltage_ac_auto_range == 0
        assert dmm.voltage_ac_resolution == 3.00E-5
        dmm.configure_voltage(range="AUTO", ac=True, resolution="MIN")
        assert dmm.mode == "ac voltage"
        assert dmm.voltage_ac_auto_range == 1
        assert dmm.voltage_ac_resolution == 1.50E-6
        dmm.configure_voltage(range=100, ac=False, resolution="MAX")
        assert dmm.mode == "voltage"
        assert dmm.voltage_range == 100
        assert dmm.voltage_auto_range == 0
        assert dmm.voltage_resolution == 3.00E-5
        dmm.configure_voltage(range="AUTO", ac=False, resolution="MIN")
        assert dmm.mode == "voltage"
        assert dmm.voltage_auto_range == 1
        assert dmm.voltage_resolution == 1.50E-6

        # Should raise TypeError
        with pytest.raises(TypeError):
            dmm.configure_voltage(ac="AAA")

        dmm.shutdown()

    def test_voltage_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "voltage"
        value = dmm.voltage
        assert type(value) is float

        dmm.shutdown()

    def test_voltage_ac_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "ac voltage"
        value = dmm.voltage_ac
        assert type(value) is float

        dmm.shutdown()

    def test_resistance_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        resistance_range_cases = [[1E2, 1E2], [1E3, 1E3], [1E4, 1E4], [1E5, 1E5],
                                  [1E6, 1E6], [1E7, 1E7], [1E8, 1E8], ["MIN", 1E2],
                                  ["MAX", 1E8], ["DEF", 1E3]]
        for value, expected in resistance_range_cases:
            dmm.resistance_range = value
            assert dmm.resistance_range == expected
        with pytest.raises(ValueError):
            dmm.resistance_range = "AAA"

        dmm.shutdown()

    def test_resistance_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.resistance_auto_range = True
        assert dmm.resistance_auto_range == 1
        dmm.resistance_auto_range = False
        assert dmm.resistance_auto_range == 0

        dmm.shutdown()

    def test_resistance_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.resistance_resolution = value
            assert dmm.resistance_resolution == expected
        with pytest.raises(ValueError):
            dmm.resistance_resolution = "AAA"

        dmm.shutdown()

    def test_resistance_4W_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        resistance_4W_range_cases = [[1E2, 1E2], [1E3, 1E3], [1E4, 1E4], [1E5, 1E5],
                                     [1E6, 1E6], [1E7, 1E7], [1E8, 1E8], ["MIN", 1E2],
                                     ["MAX", 1E8], ["DEF", 1E3]]
        for value, expected in resistance_4W_range_cases:
            dmm.resistance_4W_range = value
            assert dmm.resistance_4W_range == expected
        with pytest.raises(ValueError):
            dmm.resistance_4W_range = "AAA"

        dmm.shutdown()

    def test_resistance_4W_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.resistance_4W_auto_range = True
        assert dmm.resistance_4W_auto_range == 1
        dmm.resistance_4W_auto_range = False
        assert dmm.resistance_4W_auto_range == 0

        dmm.shutdown()

    def test_resistance_4W_resolution(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        for value, expected in self.default_resolution_cases:
            dmm.resistance_4W_resolution = value
            assert dmm.resistance_4W_resolution == expected
        with pytest.raises(ValueError):
            dmm.resistance_4W_resolution = "AAA"

        dmm.shutdown()

    def test_configure_resistance(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        # Test includes only what has not been tested in previous setter methods
        # No parameters specified
        dmm.configure_resistance()
        assert dmm.mode == "resistance"
        assert dmm.resistance_auto_range == 1
        assert dmm.resistance_resolution == 1.50E-6

        # Four possible paths
        dmm.configure_resistance(range=10E3, wires=2, resolution="MAX")
        assert dmm.mode == "resistance"
        assert dmm.resistance_range == 10E3
        assert dmm.resistance_auto_range == 0
        assert dmm.resistance_resolution == 3.00E-5
        dmm.configure_resistance(range="AUTO", wires=2, resolution="MIN")
        assert dmm.mode == "resistance"
        assert dmm.resistance_auto_range == 1
        assert dmm.resistance_resolution == 1.50E-6
        dmm.configure_resistance(range=10E3, wires=4, resolution="MAX")
        assert dmm.mode == "4w resistance"
        assert dmm.resistance_4W_range == 10E3
        assert dmm.resistance_4W_auto_range == 0
        assert dmm.resistance_4W_resolution == 3.00E-5
        dmm.configure_resistance(range="AUTO", wires=4, resolution="MIN")
        assert dmm.mode == "4w resistance"
        assert dmm.resistance_4W_auto_range == 1
        assert dmm.resistance_4W_resolution == 1.50E-6

        # Should raise ValueError
        with pytest.raises(ValueError):
            dmm.configure_resistance(wires=3)

        dmm.shutdown()

    def test_resistance_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "resistance"
        value = dmm.resistance
        assert type(value) is float

        dmm.shutdown()

    def test_resistance_4W_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "4w resistance"
        value = dmm.resistance_4W
        assert type(value) is float

        dmm.shutdown()

    def test_frequency_current_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        frequency_current_range_cases = [[10E-3, 10E-3], [100E-3, 100E-3], [1, 1],
                                         ["MIN", 10E-3], ["MAX", 10], ["DEF", 100E-3]]
        for value, expected in frequency_current_range_cases:
            dmm.frequency_current_range = value
            assert dmm.frequency_current_range == expected
        with pytest.raises(ValueError):
            dmm.frequency_current_range = "AAA"

        dmm.shutdown()

    def test_frequency_current_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.frequency_current_auto_range = True
        assert dmm.frequency_current_auto_range == 1
        dmm.frequency_current_auto_range = False
        assert dmm.frequency_current_auto_range == 0

        dmm.shutdown()

    def test_frequency_voltage_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        frequency_voltage_range_cases = [[100E-3, 100E-3], [1, 1], [10, 10], [100, 100],
                                         [750, 750], ["MIN", 100E-3], ["MAX", 750],
                                         ["DEF", 10]]
        for value, expected in frequency_voltage_range_cases:
            dmm.frequency_voltage_range = value
            assert dmm.frequency_voltage_range == expected
        with pytest.raises(ValueError):
            dmm.frequency_voltage_range = "AAA"

        dmm.shutdown()

    def test_frequency_voltage_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.frequency_voltage_auto_range = True
        assert dmm.frequency_voltage_auto_range == 1
        dmm.frequency_voltage_auto_range = False
        assert dmm.frequency_voltage_auto_range == 0

        dmm.shutdown()

    def test_frequency_aperture(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        frequency_aperture_cases = [[100E-3, 100E-3], [1, 1], ["MIN", 100E-3],
                                    ["MAX", 1], ["DEF", 1]]
        for value, expected in frequency_aperture_cases:
            dmm.frequency_aperture = value
            assert dmm.frequency_aperture == expected
        with pytest.raises(ValueError):
            dmm.frequency_aperture = "AAA"

        dmm.shutdown()

    def test_configure_frequency(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        # Test includes only what has not been tested in previous setter methods
        # No parameters specified
        dmm.configure_frequency()
        assert dmm.mode == "voltage frequency"
        assert dmm.frequency_voltage_auto_range == 1
        assert dmm.frequency_aperture == 1

        # Four possible paths
        dmm.configure_frequency(measured_from="voltage_ac", measured_from_range=1,
                                aperture=1E-1)
        assert dmm.mode == "voltage frequency"
        assert dmm.frequency_voltage_range == 1
        assert dmm.frequency_voltage_auto_range == 0
        assert dmm.frequency_aperture == 1E-1
        dmm.configure_frequency(measured_from="voltage_ac",
                                measured_from_range="AUTO", aperture=1)
        assert dmm.mode == "voltage frequency"
        assert dmm.frequency_voltage_auto_range == 1
        assert dmm.frequency_aperture == 1
        dmm.configure_frequency(measured_from="current_ac", measured_from_range=1E-1,
                                aperture=1E-1)
        assert dmm.mode == "current frequency"
        assert dmm.frequency_current_range == 1E-1
        assert dmm.frequency_current_auto_range == 0
        assert dmm.frequency_aperture == 1E-1
        dmm.configure_frequency(measured_from="current_ac",
                                measured_from_range="AUTO", aperture=1)
        assert dmm.mode == "current frequency"
        assert dmm.frequency_current_auto_range == 1
        assert dmm.frequency_aperture == 1

        # Should raise ValueError
        with pytest.raises(ValueError):
            dmm.configure_frequency(measured_from="")

        dmm.shutdown()

    def test_frequency_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "voltage frequency"
        value = dmm.frequency
        assert type(value) is float

        dmm.shutdown()

    def test_configure_temperature(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()
        dmm.configure_temperature()
        assert dmm.mode == "temperature"
        dmm.shutdown()

    def test_temperature_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "temperature"
        value = dmm.temperature
        assert type(value) is float

        dmm.shutdown()

    def test_configure_diode(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()
        dmm.configure_diode()
        assert dmm.mode == "diode"
        dmm.shutdown()

    def test_diode_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "diode"
        value = dmm.diode
        assert type(value) is float

        dmm.shutdown()

    def test_capacitance_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        capacitance_range_cases = [[1E-9, 1E-9], [1E-8, 1E-8], [1E-7, 1E-7], [1E-6, 1E-6],
                                   [1E-5, 1E-5], [1E-4, 1E-4], [1E-3, 1E-3], [1E-2, 1E-2],
                                   ["MIN", 1E-9], ["MAX", 1E-2], ["DEF", 1E-6]]
        for value, expected in capacitance_range_cases:
            dmm.capacitance_range = value
            assert dmm.capacitance_range == expected
        with pytest.raises(ValueError):
            dmm.capacitance_range = "AAA"

        dmm.shutdown()

    def test_capacitance_auto_range(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.capacitance_auto_range = True
        assert dmm.capacitance_auto_range == 1
        dmm.capacitance_auto_range = False
        assert dmm.capacitance_auto_range == 0

        dmm.shutdown()

    def test_configure_capacitance(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        # Test includes only what has not been tested in previous setter methods
        # No parameters specified
        dmm.configure_capacitance()
        assert dmm.mode == "capacitance"
        assert dmm.capacitance_auto_range == 1

        # Two possible paths
        dmm.configure_capacitance(range=1E-2)
        assert dmm.mode == "capacitance"
        assert dmm.capacitance_range == 1E-2
        assert dmm.capacitance_auto_range == 0
        dmm.configure_capacitance(range="AUTO")
        assert dmm.mode == "capacitance"
        assert dmm.capacitance_auto_range == 1

        dmm.shutdown()

    def test_capacitance_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "capacitance"
        value = dmm.capacitance
        assert type(value) is float

        dmm.shutdown()

    def test_configure_continuity(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()
        dmm.configure_continuity()
        assert dmm.mode == "continuity"
        dmm.shutdown()

    def test_continuity_reading(self):
        dmm = Agilent34450A(self.resource)
        dmm.reset()

        dmm.mode = "continuity"
        value = dmm.continuity
        assert type(value) is float

        dmm.shutdown()
