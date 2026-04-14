from typing import Union

from pint import Quantity as Q_


def set_type(response_raw: str, index: int, unit: str = 'Hz'):
    """Parse a device response substring into a Quantity with the given unit.

    :param response_raw: Raw response string from the device.
    :param index: Starting index for the substring to parse.
    :param unit: Unit string for the resulting Quantity.
    :returns: Quantity parsed from the response substring.
    """
    return Q_(response_raw[index:], unit)


def check_quantity_unit(input: Union[str, int, Q_], unit: str) -> int:
    """Lets the user check if the given quantity unit is a valid unit"""
    if isinstance(input, str):
        input = Q_(input)
    if isinstance(input, Q_):
        return int(input.to(unit).magnitude)
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invalid input for the instrument')
