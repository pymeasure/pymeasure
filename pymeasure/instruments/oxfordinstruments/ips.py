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

        ips.enable_control()         # Enables the power supply and remote control



    """

    _MAX_CURRENT = 120  # Ampere
    _MAX_VOLTAGE = 10  # Volts
    _SWITCH_HEATER_DELAY = 20  # Seconds

    _TRAINING_SCHEME = [  # (field, field-rate)-pairs
        (11.8, 1.0),
        (13.9, 0.4),
        (14.9, 0.2),
        (16.0, 0.1),
    ]

    version = Instrument.measurement(
        "V",
        """ A string property that returns the version of the IPS. """
    )

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

    demand_current = Instrument.measurement(
        "R0",
        """ A floating point property that returns the demand magnet current of
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

    switch_heater_status = Instrument.control(
        "X", "$H%d",
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

    sweep_rate = Instrument.control(
        "R9", "$T%f",
        """ A floating point property that controls the sweep-rate of
        the IPS in Tesla/minute. """,
        get_process=lambda v: float(v[1:]),
        # validator=truncated_range,
        # values=_T_RANGE
    )

    activity = Instrument.control(
        "X", "$A%d",
        """ A string property that controls the activity of the IPS. Valid values
        are "hold", "to setpoint", "to zero" and "clamp" """,
        get_process=lambda v: int(v[4]),
        values={"hold": 0, "to setpoint": 1, "to zero": 2, "clamp": 4},
        map_values=True,
    )

    sweep_status = Instrument.measurement(
        "X",
        """ A string property that returns the current sweeping mode of
        the IPS. """,
        get_process=lambda v: int(v[11]),
        values={"at rest": 0, "sweeping": 1, "sweep limiting": 2, "sweeping & sweep limiting": 3},
        map_values=True,
    )

    @property
    def field(self):
        """ Property that returns the current magnetic field value in Tesla.
        """

        sw_heater = self.switch_heater_status

        if sw_heater in [0, 2]:
            field = self.persistent_field
        elif sw_heater in [1]:
            field = self.demand_field
        else:
            log.error("IPS: Switch status returned %d" % switch_status)
            field = self.demand_field

        return field

    def enable_control(self):
        """ Method that enables active control of the IPS.
        Sets control to remote and turns off the clamp. """
        self.control_mode = "RU"

        # Turn off clamping if still clamping
        if self.activity == "clamp":
            self.activity = "hold"

        # Turn on switch-heater if field at zero
        if self.field == 0:
            self.switch_heater_status = 1

    def disable_control(self):
        if not self.field == 0:
            raise Exception("IPS not at 0T, not disabling the supply")

        self.switch_heater_status = 0
        self.activity = "clamp"

    def enable_persistent_mode(self):
        """ Methods that enables the persistent magnetic field mode. """
        # Check if system idle
        if not self.sweep_status == "at rest":
            raise Exception("Magnet not at rest")

        switch_status = self.switch_heater_status
        if switch_status in [0, 2]:
            return  # Magnet already in persistent mode
        elif switch_status == 1:
            self.activity = "hold"
            self.switch_heater_status = 0
            log.info("IPS: Wait for 20s for switch heater")
            sleep(self._SWITCH_HEATER_DELAY)
            self.activity = "to zero"
            self.wait_for_idle()
        else:
            raise Exception("Switch status returned %d" % switch_status)

    def disable_persistent_mode(self):
        """ Methods that disables the persistent magnetic field mode. """
        # Check if system idle
        if not self.sweep_status == "at rest":
            raise Exception("Magnet not at rest")

        # Check if the setpoint equals the persistent field
        if not self.field == self.field_setpoint:
            log.warning("IPS: field setpoint and persistent field not identical; "
                        "setting the setpoint to the persistent field.")
            self.field_setpoint = self.field

        switch_status = self.switch_heater_status
        if switch_status == 1:
            return  # Magnet already in demand mode or at 0 field
        elif switch_status in [0, 2]:
            self.activity = "to setpoint"
            self.wait_for_idle()
            self.activity = "hold"
            self.switch_heater_status = 1
            log.info("IPS: Wait for 20s for switch heater")
            sleep(self._SWITCH_HEATER_DELAY)
        else:
            raise Exception("Switch status returned %d" % switch_status)

    def wait_for_idle(self, max_errors=10, delay=1):
        error_ct = 0
        status = None
        while True:
            sleep(delay)

            try:
                status = self.sweep_status
            except Exception as e:
                log.error("IPS: Issue with getting status (#%d): %s" % (error_ct, e))
                error_ct = 0

            if status == "at rest":
                break

            if error_ct > max_errors:
                raise Exception("Too many exceptions occured during getting IPS status.")


    def clear_buffer(self):
        self.adapter.connection.clear()

    def set_field(self, field, sweep_rate=None, persistent_mode_control=True):
        # Check if field needs changing
        if self.field == field:
            return

        switch_status = self.switch_heater_status
        if switch_status == 1:
            pass  # Magnet in demand mode
        elif switch_status in [0, 2]:
            # Magnet in persistent mode
            if persistent_mode_control:
                self.disable_persistent_mode()
            else:
                raise Exception("IPS in persistent mode and control of persistent mode not allowed")

        if sweep_rate is not None:
            self.sweep_rate = sweep_rate

        if field == 0:
            self.activity = "to zero"
        else:
            self.activity = "to setpoint"
            self.field_setpoint = field

        self.wait_for_idle()
        sleep(10)

        if persistent_mode_control and field != 0:
            self.enable_persistent_mode()

    def train_magnet(self, training_scheme=None):
        """ Method that trains the magnet after cooling down """

        if training_scheme is not None:
            self._TRAINING_SCHEME = training_scheme

        for (field, rate) in self._TRAINING_SCHEME:
            self.set_field(field, rate, persistent_mode_control=False)

    def __init__(self, resourceName, clear_buffer=True, switch_heater_delay=None, **kwargs):
        super().__init__(
            resourceName,
            "Oxford IPS",
            includeSCPI=False,
            send_end=True,
            read_termination="\r",
            **kwargs
        )

        if switch_heater_delay is not None:
            self._SWITCH_HEATER_DELAY = switch_heater_delay

        # Clear the buffer in order to prevent communication problems
        if clear_buffer:
            self.clear_buffer()
