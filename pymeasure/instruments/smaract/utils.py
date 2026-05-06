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
