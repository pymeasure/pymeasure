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
from pymeasure.instruments.siglenttechnologies.siglent_sdm3045x import SiglentSDM3045X
import pytest


def test_init():
    """
    Test initialization of the Siglent SDM3045X instrument.
    Verifies that the expected communication setup is initialized correctly.
    """
    with expected_protocol(SiglentSDM3045X, []) as _:
        pass


def test_measurement_mode_getter():
    """
    Test getting the current measurement mode of the Siglent SDM3045X.
    Verifies the response when querying the measurement mode.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'CONFigure?', b'VOLT:DC')],
    ) as inst:
        assert inst.measurement_mode == 'VOLT:DC'


def test_measurement_mode_setter():
    """
    Test setting the measurement mode of the Siglent SDM3045X.
    Verifies the response when setting the measurement mode.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'CONFigure:VOLT:DC', None)],
    ) as inst:
        inst.measurement_mode = 'VOLT:DC'


def test_measurement_mode_invalid_setter():
    """
    Test setting an invalid measurement mode for the Siglent SDM3045X.
    Ensures that an exception is raised for invalid modes.
    """
    with pytest.raises(ValueError):
        with expected_protocol(
                SiglentSDM3045X,
                [(b'CONFigure:INVALID', None)],
        ) as inst:
            inst.measurement_mode = 'INVALID'


def test_measurement_mode_valid_values():
    """
    Test the validation of valid measurement modes for the Siglent SDM3045X.
    Verifies all valid measurement modes: 'VOLT:DC', 'VOLT:AC', 'CURR:DC',
    'CURR:AC', 'TEMP', and 'RES'.
    """
    valid_modes = ['VOLT:DC', 'VOLT:AC', 'CURR:DC', 'CURR:AC', 'TEMP', 'RES']

    for mode in valid_modes:
        # Specifying expected communication pairs for each valid mode
        with expected_protocol(
            SiglentSDM3045X,
            [
                (f'CONFigure:{mode}', None),
                (f'CONFigure?', mode.encode())  # Correct f-string usage here
            ]
        ) as inst:
            inst.measurement_mode = mode  # Set the mode
            assert inst.measurement_mode == mode


def test_voltage_getter():
    """
    Test getting the current DC voltage measurement from the Siglent SDM3045X.
    Verifies the response when querying the voltage.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'MEASure:VOLT:DC?', b'5.0E+0')],
    ) as inst:
        assert inst.voltage == 5.0


def test_current_getter():
    """
    Test getting the current DC measurement from the Siglent SDM3045X.
    Verifies the response when querying the current.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'MEASure:CURR:DC?', b'1.0E-3')],
    ) as inst:
        assert inst.current == 0.001


def test_temperature_getter():
    """
    Test getting the temperature measurement from the Siglent SDM3045X.
    Verifies the response when querying the temperature.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'MEASure:TEMP?', b'25.0')],
    ) as inst:
        assert inst.temperature == 25.0


def test_dc_voltage_range_getter():
    """
    Test getting the current DC voltage range of the Siglent SDM3045X.
    Verifies the response when querying the voltage range.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'VOLT:RANGe?', b'10')],
    ) as inst:
        assert inst.dc_voltage_range == 10.0


def test_dc_voltage_range_setter():
    """
    Test setting the DC voltage range of the Siglent SDM3045X.
    Verifies the response when setting the voltage range.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'VOLT:RANGe 100', None)],
    ) as inst:
        inst.dc_voltage_range = 100.0


def test_reset():
    """
    Test the reset function of the Siglent SDM3045X.
    Verifies that the instrument is reset correctly.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'*RST', None)],
    ) as inst:
        inst.reset()


def test_identify():
    """
    Test the identity query for the Siglent SDM3045X.
    Verifies the correct identity string is returned.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [(b'*IDN?', b'Siglent,SDM3045X,123456789,1.0')],
    ) as inst:
        assert inst.identify() == 'Siglent,SDM3045X,123456789,1.0'


def test_close():
    """
    Test the closing of the connection to the Siglent SDM3045X.
    Verifies that the connection is properly closed.
    """
    with expected_protocol(
            SiglentSDM3045X,
            [],
    ) as inst:
        inst.close()
