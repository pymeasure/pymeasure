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

import pint

ureg = pint.get_application_registry()


def assume_units(value, units):
    """
    If units are not provided for ``value`` (that is, if it is a raw
    `float`), then returns a `~pint.Quantity` with magnitude
    given by ``value`` and units given by ``units``.

    :param value: A value that may or may not be unitful.
    :param units: Units to be assumed for ``value`` if it does not already
        have units.

    :return: A unitful quantity that has either the units of ``value`` or
        ``units``, depending on if ``value`` is unitful.
    :rtype: `Quantity`
    """
    if isinstance(value, ureg.Quantity):
        return value
    elif isinstance(value, str):
        value = ureg.Quantity(value)
        if value.dimensionless:
            return ureg.Quantity(value.magnitude, units)
        return value
    return ureg.Quantity(value, units)


def assume_or_convert_units(value, units):
    """
    If units are not provided for ``value`` (that is, if it is a raw
    `float`), then pass through the given magnitude, otherwise convert to
    the specified units and return the resulting magnitude

    :param value: A value that may or may not be unitful.
    :param units: Units to be assumed for ``value`` if it does not already
        have units, or to be converted to if it does

    :return: Magnitude resulting from conversion to specified units,
        or assuming input has specified units, if input has no units specified
    """
    if isinstance(value, ureg.Quantity):
        return value.m_as(units)
    elif isinstance(value, str):
        value = ureg.Quantity(value)
        if value.dimensionless:
            return value.magnitude
        return value.m_as(units)
    return value
