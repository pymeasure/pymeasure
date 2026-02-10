from typing import Union

from pint import Quantity as Q_
from pint.errors import DimensionalityError

def set_type(response_raw : str, index : int, unit: str = 'Hz' ):
    return Q_(response_raw[index:], unit)

"""il va falloir le genraliser avec tous les types de donnés"""
def check_quantity_unit(input: Union[str, int, Q_], unit: str):
    if isinstance(input, str):
        input = Q_(input)
    if isinstance(input, Q_):
        return input.to(unit).magnitude
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invalid input for the instrument')
