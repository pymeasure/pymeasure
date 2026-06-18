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

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from decimal import Decimal
from typing import TYPE_CHECKING, Any, Literal, TypeVar, overload
from warnings import warn

T = TypeVar("T")
NumericT = TypeVar("NumericT", bound=(float | int | Decimal))
ValidatorFunc = Callable[[Any, Any], Any]


if TYPE_CHECKING:
    import numpy as np

    NumericSeq = Sequence[NumericT] | np.ndarray


def strict_range(value: NumericT, values: NumericSeq) -> NumericT:
    """Provides a validator function that returns the value
    if its value is less than or equal to the maximum and
    greater than or equal to the minimum of ``values``.
    Otherwise it raises a ValueError.

    :param value: A value to test
    :param values: A range of values (range, list, etc.)
    :raises: ValueError if the value is out of the range
    """
    if min(values) <= value <= max(values):
        return value
    else:
        raise ValueError(f'Value of {value:g} is not in range [{min(values):g},{max(values):g}]')


@overload
def strict_discrete_range(
    value: int, values: list[int] | tuple[int, int], step: int
) -> int: ...


@overload
def strict_discrete_range(
    value: NumericT, values: NumericSeq, step: NumericT
) -> NumericT: ...


def strict_discrete_range(
    value: NumericT, values: NumericSeq, step: NumericT
) -> NumericT:
    """Provides a validator function that returns the value
    if its value is less than the maximum and greater than the
    minimum of the range and is a multiple of step.
    Otherwise it raises a ValueError.

    :param value: A value to test
    :param values: A range of values (range, list, etc.)
    :param step: Minimum stepsize (resolution limit)
    :raises: ValueError if the value is out of the range
    """
    # use Decimal type to provide correct decimal compatible floating
    # point arithmetic compared to binary floating point arithmetic
    if (strict_range(value, values) == value and
            Decimal(str(value)) % Decimal(str(step)) == 0):
        return value
    else:
        raise ValueError(f'Value of {value:g} is not a multiple of {step:g}')


def strict_discrete_set(value: T, values: Iterable[T] | dict[T, Any]) -> T:
    """ Provides a validator function that returns the value
    if it is in the discrete set. Otherwise it raises a ValueError.

    :param value: A value to test
    :param values: A set of values that are valid
    :raises: ValueError if the value is not in the set
    """
    if value in values:
        return value
    else:
        raise ValueError(f'Value of {value} is not in the discrete set {values}')


def truncated_range(value: NumericT, values: NumericSeq) -> NumericT:
    """ Provides a validator function that returns the value
    if it is in the range. Otherwise it returns the closest
    range bound.

    :param value: A value to test
    :param values: A set of values that are valid
    """
    if min(values) <= value <= max(values):
        return value
    elif value > max(values):
        return max(values)
    else:
        return min(values)


def modular_range(value: NumericT, values: NumericSeq) -> NumericT:
    """ Provides a validator function that returns the value
    if it is in the range. Otherwise it returns the value,
    modulo the max of the range.

    :param value: a value to test
    :param values: A set of values that are valid
    """
    return value % max(values)


def modular_range_bidirectional(value: NumericT, values: NumericSeq) -> NumericT:
    """ Provides a validator function that returns the value
    if it is in the range. Otherwise it returns the value,
    modulo the max of the range. Allows negative values.

    :param value: a value to test
    :param values: A set of values that are valid
    """
    if value > 0:
        return value % max(values)
    else:
        return -1 * (abs(value) % max(values))


def truncated_discrete_set(value: NumericT, values: Iterable[NumericT]) -> NumericT:
    """ Provides a validator function that returns the value
    if it is in the discrete set. Otherwise, it returns the smallest
    value that is larger than the value.

    :param value: A value to test
    :param values: A set of values that are valid
    """
    # Force the values to be sorted
    values = sorted(values)
    for v in values:
        if value <= v:  # type: ignore[operator]
            return v

    return values[-1]


def joined_validators(*validators: ValidatorFunc) -> ValidatorFunc:
    """Returns a validator function that represents a list of validators joined together.

    A value passed to the validator is returned if it passes any validator (not all of them).
    Otherwise it raises a ValueError.

    Note: the joined validator expects ``values`` to be a sequence of ``values``
    appropriate for the respective validators (often sequences themselves).

    :Example:

    >>> from pymeasure.instruments.validators import strict_discrete_set, strict_range
    >>> from pymeasure.instruments.validators import joined_validators
    >>> joined_v = joined_validators(strict_discrete_set, strict_range)
    >>> values = [['MAX','MIN'], range(10)]
    >>> joined_v(5, values)
    5
    >>> joined_v('MAX', values)
    'MAX'
    >>> joined_v('NONSENSE', values)
    Traceback (most recent call last):
    ...
    ValueError: Value of NONSENSE does not match any of the joined validators

    :param validators: an iterable of other validators
    """

    def validate(value: Any, values: Any) -> Any:
        for validator, vals in zip(validators, values):
            try:
                return validator(value, vals)
            except (ValueError, TypeError):
                pass
        raise ValueError(f"Value of {value} does not match any of the joined validators")

    return validate


def truncated_discrete_set_positive(
    number: NumericT, discrete_set: NumericSeq
) -> NumericT | Literal[False]:
    """Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.
    """
    if number < 0:
        return False
    discrete_set = sorted(discrete_set)
    for item in discrete_set:
        if number <= item:
            return item
    return False


def discreteTruncate(number: NumericT, discreteSet: NumericSeq) -> NumericT | Literal[False]:
    """Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.

    .. deprecated:: 0.17.0
        Use :func:`truncated_discrete_set_positive` instead.
    """
    warn(
        "'discreteTruncate' validator is deprecated, use 'discrete_truncate' instead.",
        FutureWarning,
    )
    return truncated_discrete_set_positive(number=number, discrete_set=discreteSet)
