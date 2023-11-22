import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())
from time import sleep

from pymeasure.adapters import VISAAdapter

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.validators import truncated_discrete_set, truncated_range, \
    modular_range_bidirectional, strict_discrete_set,strict_range

class Temptronic3010(Instrument):
    """Represents Temptronic3010 Temperature Controller"""

    MAX_TEMP = 200
    temperature_setpoint = Instrument.control("SS", f"Rs%g",
                                    """Set the temperature setpoint. from 20.0 to 200.0 to TMAX""")
    # returns current temp setpoint, and set temp setpoint

  

    temperature_actual = Instrument.measurement("ST", "Current temperature in C")
    
    def __init__(self, adapter, **kwargs):
        super(Temptronic3010, self).__init__(
            adapter, "Temptronic heater controller", **kwargs)

        
 # should search by GPIB::9::INSTR


 