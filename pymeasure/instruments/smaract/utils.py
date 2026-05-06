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

from typing import Union

from pymeasure.units import ureg

Q_ = ureg.Quantity

def set_type(response_raw: str, index: int, unit: str = 'Hz'):
    """Parse a device response substring into a Quantity with the given unit.

    :param response_raw: Raw response string from the device.
    :param index: Starting index for the substring to parse.
    :param unit: Unit string for the resulting Quantity.
    :returns: Quantity parsed from the response substring.
    """
    return Q_(response_raw[index:], unit)


def convert_quantity_to_magnitude(input: Union[str, int, Q_], unit: str) -> Union[int, float]:
    """Lets the user convert the given quantity unit to a valid unit"""
    if isinstance(input, str):
        input = Q_(input)
    if isinstance(input, Q_):
        value = input.to(unit).magnitude
        return int(value) if value.is_integer() else value
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invalid input for the instrument')
