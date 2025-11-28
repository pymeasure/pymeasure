from typing import Union

from pint import Quantity as Q_

def set_type(reponse_raw : str, index : str, unit: str = 'Hz' ):
    return

"""il va falloir le genraliser avec tous les types de donnés"""
def check_type(input: Union[int, Q_], unit='Hz'):
    if isinstance(input, Q_):
        return input.to(unit).magnitude
    elif isinstance(input, int):
        return input
    else:
        raise TypeError('Invalid input for the instrument')