#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2020 PyMeasure Developers
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


import logging
from time import sleep, time
import numpy

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_range, strict_range


# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class IPS(Instrument):
    """Represents the Oxford Superconducting Magnet Power Supply.

    .. code-block:: python

        ips = IPS("GPIB::25")        # Default channel for the IPS

        ips.control_mode = "RU"         # Set the control mode to remote
        ips.heater_gas_mode = "AUTO"    # Turn on auto heater and flow
        ips.auto_pid = True             # Turn on auto-pid

    """

    _MAX_CURRENT = 120  # Ampere
    _MAX_VOLTAGE = 10  # Volts

    control_mode = Instrument.control(
        "X", "$C%d",
        """ A string property that sets the IPS in LOCAL or REMOTE and LOCKEd,
        or UNLOCKED, the LOC/REM button. Allowed values are:
        LL: LOCAL & LOCKED
        RL: REMOTE & LOCKED
        LU: LOCAL & UNLOCKED
        RU: REMOTE & UNLOCKED. """,
        get_process=lambda v: int(v[6]),
        validator=strict_discrete_set,
        values={"LL": 0, "RL": 1, "LU": 2, "RU": 3},
        map_values=True,
    )

    current_measured = Instrument.measurement(
        "R1",
        """ A floating point property that returns the measured magnet current of
        the IPS in amps. """,
        get_process=lambda v: float(v[1:]),
    )

    demand_field = Instrument.measurement(
        "R7",
        """ A floating point property that returns the demand magnetic field of
        the IPS in Tesla. """,
        get_process=lambda v: float(v[1:]),
    )

    persistent_field = Instrument.measurement(
        "R18",
        """ A floating point property that returns the persistent magnetic field of
        the IPS in Tesla. """,
        get_process=lambda v: float(v[1:]),
    )

    field_polarity = Instrument.measurement(
        "X",
        """ A integer property that returns the magnet polarity of 
        the IPS in Tesla. """,
        get_process=lambda v: int(v[13]),
    )

    polarity_contactor = Instrument.measurement(
        "X",
        """ A integer property that returns the contactor status of
        the IPS in Tesla. """,
        get_process=lambda v: int(v[14]),
    )

    switch_heater_status = Instrument.measurement(
        "X",
        """ A integer property that returns the switch heater status of
        the IPS in Tesla. """,
        get_process=lambda v: int(v[8]),
    )

    current_setpoint = Instrument.control(
        "R0", "$I%f",
        """ A floating point property that controls the magnet current set-point of
        the IPS in ampere. """,
        get_process=lambda v: float(v[1:]),
        validator=truncated_range,
        values=[0, _MAX_CURRENT]
    )

    field_setpoint = Instrument.control(
        "R8", "$J%f",
        """ A floating point property that controls the magnetic field set-point of
        the IPS in Tesla. """,
        get_process=lambda v: float(v[1:]),
        # validator=truncated_range,
        # values=_T_RANGE
    )

    def get_field(self):
        """ Function to get the current magnetic field value in Tesla.
        """

        sw_heater = self.switch_heater_status
        pol_cont = self.polarity_contactor
        per_field = self.persistent_field
        dem_field = self.demand_field

        if pol_cont == 1:
            per_field = -abs(per_field)
            dem_field = -abs(dem_field)

        if sw_heater == 0:
            return dem_field
        elif sw_heater == 1:
            return per_field

    def __init__(self, resourceName, clear_buffer=True, **kwargs):
        super().__init__(
            resourceName,
            "Oxford IPS",
            includeSCPI=False,
            send_end=True,
            read_termination="\r",
            **kwargs
        )

        # Clear the buffer in order to prevent communication problems
        if clear_buffer:
            self.adapter.connection.clear()
