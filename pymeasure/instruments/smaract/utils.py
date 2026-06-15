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


def convert_quantity_to_magnitude(val: "str | int| Q_" , unit: str) -> int|float:
    """Convert a value to its magnitude in the specified unit.

     :param val: Value as string, int, or :class:`pint.Quantity`.
     :param unit: Target unit for conversion.
     :returns: Integer magnitude when integral, otherwise float.
     :raises TypeError: If ``val`` is not one of the accepted types.
     """
    if isinstance(val, str):
        val = Q_(val)

    if isinstance(val, Q_):
        value = val.to(unit).magnitude

        if isinstance(value, float) and value.is_integer():
            return int(value)

        return value

    elif isinstance(val, int):
        return val
    else:
        raise TypeError('Invalid value for the instrument')
