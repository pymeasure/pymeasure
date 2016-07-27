#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2016 PyMeasure Developers
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


def strict_range(value, values):
    """ Provides a validator function that returns the value
    if its value is less than the maximum and greater than the
    minimum of the range. Otherwise it raises a ValueError.

    :param value: A value to test
    :param values: A range of values (range, list, etc.)
    :raises: ValueError if the value is out of the range
    """
    if value <= max(values) and value >= min(values):
        return value
    else:
        raise ValueError('Value of {:g} is not in range [{:g},{:g}]'.format(
            value, min(values), max(values)
        ))

def strict_discrete_set(value, values):
    """ Provides a validator function that returns the value
    if it is in the discrete set. Otherwise it raises a ValueError.

    :param value: A value to test
    :param values: A set of values that are valid
    :raises: ValueError if the value is not in the set
    """
    if value in values:
        return value
    else:
        raise ValueError('Value of {} is not in the discrete set {}'.format(
            value, values
        ))

def strict_map(value, values):
    """ Provides a validator function that returns a value
    from a corresponding map, and raises a ValueError if the value
    is not contained in the map. If the map is a dictionary, the keys
    are used as the valid values and the associated value is returned. 
    If the map is a list or range, the index of the item is returned.

    :param value: A value to test
    :param values: A map of valid values in either dictionary, list, or range format
    """
    if type(values) == dict:
        value = strict_discrete_set(value, values.keys())
        return values[value]
    elif type(values) in (list, range):
        value = strict_discrete_set(value, values)
        return values.index(value)

def truncated_range(value, values):
    """ Provides a validator function that returns the value
    if it is in the range. Otherwise it returns the closest
    range bound.

    :param value: A value to test
    :param values: A set of values that are valid
    """
    if value <= max(values) and value >= min(values):
        return value
    elif value > max(values):
        return max(values)
    else:
        return min(values)

def truncated_discrete_set(value, values):
    """ Provides a validator function that returns the value
    if it is in the discrete set. Otherwise, it returns the smallest
    value that is larger than the value.

    :param value: A value to test
    :param values: A set of values that are valid
    """
    if hasattr(values, 'sort'):
        values.sort()
    for v in values:
        if value <= v:
            return v
    return v

def truncated_map(value, values):
    """ Provides a validator function that returns a value
    from a corresponding map, and uses :func:`~.truncate_discrete_set`
    to determine valid values. If the map is a dictionary, the keys
    are used as the valid values and the associated value is returned. 
    If the map is a list or range, the index of the item is returned.

    :param value: A value to test
    :param values: A map of valid values in either dictionary, list, or range format
    """
    if type(values) == dict:
        keys = list(values.keys())
        keys.sort()
        value = truncated_discrete_set(value, keys)
        return values[value]
    elif type(values) in (list, range):
        value = truncated_discrete_set(value, values)
        return values.index(value)
