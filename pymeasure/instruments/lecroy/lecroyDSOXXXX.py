"""
Author: Paul Haigh
email: paul.haigh@nubis-communications.com
"""

import logging
import time
import numpy as np
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import truncated_range, strict_discrete_set

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2600(Instrument):
    pass
