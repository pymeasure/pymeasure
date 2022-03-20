#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.validators import truncated_range

from .adapters import OxfordInstrumentsAdapter

# Setup logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MagnetError(ValueError):
    """ Exception that is raised for issues regarding the state of the magnet or power supply. """
    pass


class SwitchHeaterError(ValueError):
    """ Exception that is raised for issues regarding the state of the superconducting switch. """
    pass


class IPS120_10(Instrument):
    """Represents the Oxford Superconducting Magnet Power Supply IPS 120-10.

    .. code-block:: python

        ips = IPS120_10("GPIB::25")  # Default channel for the IPS

        ips.enable_control()         # Enables the power supply and remote control

        ips.train_magnet([           # Train the magnet after it has been cooled-down
            (11.8, 1.0),
            (13.9, 0.4),
            (14.9, 0.2),
            (16.0, 0.1),
        ])

        ips.set_field(12)           # Bring the magnet to 12 T. The switch heater will
                                    # be turned off when the field is reached and the
                                    # current is ramped back to 0 (i.e. persistent mode).

        print(self.field)           # Print the current field (whether in persistent or
                                    # non-persistent mode)

        ips.set_field(0)            # Bring the magnet to 0 T. The persistent mode will be
                                    # turned off first (i.e. current back to set-point and
                                    # switch-heater on); afterwards the switch-heater will
                                    # again be turned off.

        ips.disable_control()       # Disables the control of the supply, turns off the
                                    # switch-heater and clamps the output.

    :param clear_buffer: A boolean property that controls whether the instrument
        buffer is clear upon initialisation.
    :param switch_heater_heating_delay: The time in seconds (default is 20s) to wait after
        the switch-heater is turned on before the heater is expected to be heated.
    :param switch_heater_cooling_delay: The time in seconds (default is 20s) to wait after
        the switch-heater is turned off before the heater is expected to be cooled down.
    :param field_range: A numeric value or a tuple of two values to indicate the
        lowest and highest allowed magnetic fields. If a numeric value is provided
        the range is expected to be from :code:`-field_range` to :code:`+field_range`.
        The default range is -7 to +7 Tesla.

    """

    _SWITCH_HEATER_HEATING_DELAY = 20  # Seconds
    _SWITCH_HEATER_COOLING_DELAY = 20  # Seconds

    _SWITCH_HEATER_SET_VALUES = {
        False: 0,  # Heater off
        True: 1,  # Heater on, with safety checks
        "Force": 2,  # Heater on, without safety checks
    }
    _SWITCH_HEATER_GET_VALUES = {
        0: False,  # Heater off, Switch closed, Magnet at zero
        1: True,  # Heater on, Switch open
        2: False,  # Heater off, Switch closed, Magnet at field
        5: "Heater fault, low heater current",  # Heater on but current is low
        8: "No switch fitted",  # No switch fitted
    }

    def __init__(self,
                 adapter,
                 name="Oxford IPS",
                 clear_buffer=True,
                 switch_heater_heating_delay=None,
                 switch_heater_cooling_delay=None,
                 field_range=None,
                 **kwargs):

        if isinstance(adapter, (int, str)):
            kwargs.setdefault('read_termination', '\r')
            kwargs.setdefault('send_end', True)
            adapter = OxfordInstrumentsAdapter(
                adapter,
                asrl={
                    'baud_rate': 9600,
                    'data_bits': 8,
                    'parity': 0,
                    'stop_bits': 20,
                },
                preprocess_reply=lambda v: v[1:],
                **kwargs,
            )

        super().__init__(
            adapter=adapter,
            name=name,
            includeSCPI=False,
        )

        if switch_heater_heating_delay is not None:
            self._SWITCH_HEATER_HEATING_DELAY = switch_heater_heating_delay
        if switch_heater_cooling_delay is not None:
            self._SWITCH_HEATER_COOLING_DELAY = switch_heater_cooling_delay

        if field_range is not None:
            if isinstance(field_range, (float, int)):
                self.field_setpoint_values = [-field_range, +field_range]
            elif isinstance(field_range, (list, tuple)):
                self.field_setpoint_values = field_range

        # Clear the buffer in order to prevent communication problems
        if clear_buffer:
            self.adapter.connection.clear()

    version = Instrument.measurement(
        "V",
        """ A string property that returns the version of the IPS. """,
        preprocess_reply=lambda v: v,
    )

    control_mode = Instrument.control(
        "X", "C%d",
        """ A string property that sets the IPS in `local` or `remote` and `locked`
        or `unlocked`, locking the LOC/REM button. Allowed values are:

        =====   =================
        value   state
        =====   =================
        LL      local & locked
        RL      remote & locked
        LU      local & unlocked
        RU      remote & unlocked
        =====   =================
        """,
        preprocess_reply=lambda v: v[6],
        cast=int,
        validator=strict_discrete_set,
        values={"LL": 0, "RL": 1, "LU": 2, "RU": 3},
        map_values=True,
    )

    current_measured = Instrument.measurement(
        "R1",
        """ A floating point property that returns the measured magnet current of
        the IPS in amps. """,
        dynamic=True,
    )

    demand_current = Instrument.measurement(
        "R0",
        """ A floating point property that returns the demand magnet current of
        the IPS in amps. """,
        dynamic=True,
    )

    demand_field = Instrument.measurement(
        "R7",
        """ A floating point property that returns the demand magnetic field of
        the IPS in Tesla. """,
        dynamic=True,
    )

    persistent_field = Instrument.measurement(
        "R18",
        """ A floating point property that returns the persistent magnetic field of
        the IPS in Tesla. """,
        dynamic=True,
    )

    switch_heater_status = Instrument.control(
        "X", "H%d",
        """ An integer property that returns the switch heater status of
        the IPS. Use the :py:attr:`~switch_heater_enabled` property for controlling
        and reading the switch heater. When using this property, the user
        is referred to the IPS120-10 manual for the meaning of the integer
        values. """,
        preprocess_reply=lambda v: v[8],
        cast=int,
    )

    @property
    def switch_heater_enabled(self):
        """ A boolean property that controls whether the switch heater
        is enabled or not. When the switch heater is enabled (:code:`True`), the
        switch is closed and the switch is open and the current in the
        magnet can be controlled; when the switch heater is disabled
        (:code:`False`) the switch is closed and the current in the magnet cannot
        be controlled.

        When turning on the switch heater with :code:`True`, the switch heater is
        only activated if the current of the power supply matches the last
        recorded current in the magnet.

        .. warning::
            These checks can be omitted by using :code:`"Force"` in stead of
            :code:`True`. Caution: Not performing these checks can cause serious
            damage to both the power supply and the magnet.

        After turning on the switch heater it is necessary to wait several
        seconds for the switch the respond.

        Raises a :class:`.SwitchHeaterError` if the system reports a 'heater fault'
        or if no switch is fitted on the system upon getting the status.
        """
        status_value = self.switch_heater_status
        status = self._SWITCH_HEATER_GET_VALUES[status_value]

        if isinstance(status, str):
            raise SwitchHeaterError(
                "IPS 120-10: switch heater status reported issue with "
                "switch heater: %s" % status)

        return status

    @switch_heater_enabled.setter
    def switch_heater_enabled(self, value):

        status_value = self._SWITCH_HEATER_SET_VALUES[value]

        if status_value == 2:
            log.info("IPS 120-10: Turning on the switch heater without any safety checks.")

        self.switch_heater_status = status_value

    current_setpoint = Instrument.control(
        "R0", "I%f",
        """ A floating point property that controls the magnet current set-point of
        the IPS in ampere. """,
        validator=truncated_range,
        values=[0, 120],  # Ampere
        dynamic=True,
    )

    field_setpoint = Instrument.control(
        "R8", "J%f",
        """ A floating point property that controls the magnetic field set-point of
        the IPS in Tesla. """,
        validator=truncated_range,
        values=[-7, 7],  # Tesla
        dynamic=True,
    )

    sweep_rate = Instrument.control(
        "R9", "T%f",
        """ A floating point property that controls the sweep-rate of
        the IPS in Tesla/minute. """,
        dynamic=True,
    )

    activity = Instrument.control(
        "X", "A%d",
        """ A string property that controls the activity of the IPS. Valid values
        are "hold", "to setpoint", "to zero" and "clamp" """,
        preprocess_reply=lambda v: v[4],
        cast=int,
        values={"hold": 0, "to setpoint": 1, "to zero": 2, "clamp": 4},
        map_values=True,
    )

    sweep_status = Instrument.measurement(
        "X",
        """ A string property that returns the current sweeping mode of the IPS. """,
        preprocess_reply=lambda v: v[11],
        cast=int,
        values={"at rest": 0, "sweeping": 1, "sweep limiting": 2, "sweeping & sweep limiting": 3},
        map_values=True,
    )

    @property
    def field(self):
        """ Property that returns the current magnetic field value in Tesla.
        """

        try:
            heater_on = self.switch_heater_enabled
        except SwitchHeaterError as e:
            log.error("IPS 120-10: Switch heater status reported issue: %s" % e)
            field = self.demand_field
        else:
            if heater_on:
                field = self.demand_field
            else:
                field = self.persistent_field

        return field

    def enable_control(self):
        """ Enable active control of the IPS by setting control to remote and
        turning off the clamp.
        """
        log.debug("start enabling control")
        self.control_mode = "RU"

        # Turn off clamping if still clamping
        if self.activity == "clamp":
            self.activity = "hold"

        # Turn on switch-heater if field at zero
        if self.field == 0:
            log.debug("enabling switch heater")
            self.switch_heater_enabled = True

    def disable_control(self):
        """ Disable active control of the IPS (if at 0T) by turning off the switch heater,
        clamping the output and setting control to local.
        Raise a :class:`.MagnetError` if field not at 0T. """
        log.debug("start disabling control")
        if not self.field == 0:
            raise MagnetError("IPS 120-10: field not at 0T; cannot disable the supply. ")

        log.debug("disabling switch heater")
        self.switch_heater_enabled = False
        self.activity = "clamp"
        self.control_mode = "LU"

    def enable_persistent_mode(self):
        """ Enable the persistent magnetic field mode.
         Raise a :class:`.MagnetError` if the magnet is not at rest. """
        # Check if system idle
        log.debug("enabling persistent mode")
        if not self.sweep_status == "at rest":
            raise MagnetError("IPS 120-10: magnet not at rest; cannot enable persistent mode")

        if not self.switch_heater_enabled:
            log.debug("magnet already in persistent mode")
            return  # Magnet already in persistent mode
        else:
            self.activity = "hold"
            self.switch_heater_enabled = False
            log.info("IPS 120-10: Wait for for switch heater delay")
            sleep(self._SWITCH_HEATER_COOLING_DELAY)
            self.activity = "to zero"
            self.wait_for_idle()

    def disable_persistent_mode(self):
        """ Disable the persistent magnetic field mode.
         Raise a :class:`.MagnetError` if the magnet is not at rest. """
        # Check if system idle
        log.debug("disabling persistent mode")
        if not self.sweep_status == "at rest":
            raise MagnetError("IPS 120-10: magnet not at rest; cannot disable persistent mode")

        # Check if the setpoint equals the persistent field
        if not self.field == self.field_setpoint:
            log.warning("IPS 120-10: field setpoint and persistent field not identical; "
                        "setting the setpoint to the persistent field.")
            self.field_setpoint = self.field

        if self.switch_heater_enabled:
            log.debug("magnet already in demand mode or at 0 field")
            return  # Magnet already in demand mode or at 0 field
        else:
            log.debug("set activity to 'to setpoint'")
            self.activity = "to setpoint"
            self.wait_for_idle()
            log.debug("set activity to 'hold'")
            self.activity = "hold"
            log.debug("enable switch heater")
            self.switch_heater_enabled = True
            log.info("IPS 120-10: Wait for for switch heater delay")
            sleep(self._SWITCH_HEATER_HEATING_DELAY)

    def wait_for_idle(self, delay=1, max_wait_time=None, should_stop=lambda: False):
        """ Wait until the system is at rest (i.e. current of field not ramping).

        :param delay: Time in seconds between each query into the state of the instrument.
        :param max_wait_time: Maximum time in seconds to wait before is at rest. If the system is
            not at rest within this time a :class:`TimeoutError` is raised. :code:`None` is
            interpreted as no maximum time.
        :param should_stop: A function that returns :code:`True` when this function should return
            early.
        """
        log.debug("waiting for magnet to be idle")
        start_time = time()

        while True:
            log.debug("sleeping for %d s", delay)
            sleep(delay)

            log.debug("checking the status of the sweep")
            status = self.sweep_status

            if status == "at rest":
                log.debug("status is 'at rest', waiting is done")
                break
            if should_stop():
                log.debug("external function signals to stop waiting")
                break

            if max_wait_time is not None and time() - start_time > max_wait_time:
                raise TimeoutError("IPS 120-10: Magnet not idle within max wait time.")

    def set_field(self, field, sweep_rate=None, persistent_mode_control=True):
        """ Change the applied magnetic field to a new specified magnitude.
        If allowed (via `persistent_mode_control`) the persistent mode will be turned off
        if needed and turned on when the magnetic field is reached.
        When the new field set-point is 0, the set-point of the instrument will not be changed
        but rather the `to zero` functionality will be used. Also, the persistent mode will not
        turned on upon reaching the 0T field in this case.

        :param field: The new set-point for the magnetic field in Tesla.
        :param sweep_rate: A numeric value that controls the rate with which to change
            the magnetic field in Tesla/minute.
        :param persistent_mode_control: A boolean that controls whether the persistent mode
            may be turned off (if needed before sweeping) and on (when the field is reached);
            if set to :code:`False` but the system is in persistent mode, a :class:`.MagnetError`
            will be raised and the magnetic field will not be changed.

        """

        # Check if field needs changing
        if self.field == field:
            return

        if self.switch_heater_enabled:
            pass  # Magnet in demand mode
            log.debug("Magnet in demand mode, continuing")
        else:
            # Magnet in persistent mode
            log.debug("Magnet in persistent mode")
            if persistent_mode_control:
                log.debug("trying to disable persistent mode")
                self.disable_persistent_mode()
            else:
                raise MagnetError(
                    "IPS 120-10: magnet is in persistent mode but cannot turn off "
                    "persistent mode because persistent_mode_control == False. "
                )

        if sweep_rate is not None:
            log.debug("setting the sweep rate to %s", sweep_rate)
            self.sweep_rate = sweep_rate

        if field == 0:
            log.debug("setting activity to 'to zero' - running down the field")
            self.activity = "to zero"
        else:
            log.debug("setting activity to 'to setpoint'")
            self.activity = "to setpoint"
            log.debug("setting the field_setpoint to %d", field)
            self.field_setpoint = field

        log.debug("waiting for magnet to be finished")
        self.wait_for_idle()
        log.debug("sleeping for additional 10s (whatever the reason)")
        sleep(10)

        if persistent_mode_control and field != 0:
            log.debug(
                "persistent mode control is on, and setpoint_field !=0 - enabling persistent mode"
            )
            self.enable_persistent_mode()

    def train_magnet(self, training_scheme):
        """ Train the magnet after cooling down. Afterwards, set the field
        back to 0 tesla (at last-used ramp-rate).

        :param training_scheme: The training scheme as a list of tuples; each
            tuple should consist of a (field [T], ramp-rate [T/min]) pair.
        """

        for (field, rate) in training_scheme:
            self.set_field(field, rate, persistent_mode_control=False)

        self.set_field(0)
