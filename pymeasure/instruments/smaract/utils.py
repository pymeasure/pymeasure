from typing import Union

from pint import Quantity as Q_


def set_type(response_raw: str, index: int, unit: str = 'Hz'):
    return Q_(response_raw[index:], unit)


"""Lets the user check if the given quantity unit is a valid unit"""


def check_quantity_unit(input: Union[str, int, Q_], unit: str) -> int:
    if isinstance(input, str):
        input = Q_(input)
    if isinstance(input, Q_):
        return int(input.to(unit).magnitude)
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invalid input for the instrument')
