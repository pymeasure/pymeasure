#
# this file is intended to become part of the PyMeasure package
#
# agilent34970A.py
# module to support the HP/Agilent/Keysight 34970A multimeter
# Chris Freitag, August 20, 2019

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strickt_discrete_set,\
    strict_range, joined_validators
from time import time
from pyvisa.errors import VisaIOError

# Capitalize string arguments to allow for better conformity with other WFG's
def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class Agilent34970A(Instrument):

    """Represents the HP/Agilent/Keysight 34970A Data Acquisition/Switch Unit.
    .. code-block:: python
    Only the most simple functions  are implemented
    Implemented measurements: voltage_dc, temperature_TC
    """

    def __init__(self, adapter, delay=0.2, **kwargs):
        super(Agilent34970A, self).__init__(
            adapter, 
            "HP/Agilent/Keysight 34970A Data Acquisition/Switch Unit", 
            **kwargs
        )
    
     def check_errors(self):
        """ Read all errors from the instrument. """

        errors = []
        while True:
            err = self.values("SYST:ERR?")
            if int(err[0]) != 0:
                errmsg = "Agilent 34970A: %s: %s" % (err[0], err[1])
                log.error(errmsg + '\n')
                errors.append(errmsg)
            else:
                break

        return errors

        