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
    # Force the values to be sorted
    values = list(values)
    values.sort()
    for v in values:
        if value <= v:
            return v
    return v

def joined_validators(*validators):
    """ Join a list of validators together as a single.  Expects a list of validator functions and values.

    :param validators: an iterable of other validators
    """
    def validate(value, values):
        for validator, vals in zip(validators, values):
            try:
                return validator(value, vals)
            except (ValueError, TypeError):
                pass
        raise ValueError("Value of {} not in chained validator set".format(value))
    return validate
