from typing import Union

from pint import Quantity as Q_


def check_type(input: Union[int, Q_], unit='Hz'):
    if isinstance(input, Q_):
        return input.to(unit).magnitude
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invqlid input for the instrument')