#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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
import time
import os
import json
from enum import IntFlag

import numpy as np
import pandas as pd

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_discrete_set,
                                              strict_range)

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


######
# MAIN
######


def check_errors_user_mode_value(cmd_str):
    data_status = cmd_str[0]
    channel = cmd_str[1]
    value = float(cmd_str[4:])

    errors = {
        'N': "Normal",
        'L': "Interval is too short",
        'V': "A-D converter saturation",
        'X': "Oscillation",
        'C': "This channel compliance error",
        'T': "Other channel compliance error"
    }

    channels = {
        'A': "SMU1",
        'B': "SMU2",
        'C': "SMU3",
        'D': "SMU4",
        'E': "VM1",
        'F': "VM2"
    }

    if data_status != 'N':
        log.error(f"HP4145x: Measurement Error - {data_status}, {errors[data_status]} "
                  f"on channel {channels[channel]}")
    return value


class Status(IntFlag):
    DATA_READY = 0b00000001
    SYNTAX_ERROR = 0b00000010
    END_STATUS = 0b00000100
    ILLEGAL_PROGRAM = 0b00001000
    BUSY = 0b00010000
    SELF_TEST_FAIL = 0b00100000
    RQS = 0b01000000
    EMERGENCY = 0b10000000
    FIXTURE_LID_OPEN = 0b10000010
    SMU_SHUT_DOWN = 0b10001000
    POWER_FAILURE = 0b10100000




def check_current_voltage_name(name):
    if (len(name) > 6) or not name[0].isalpha():
        new_name = 'a' + name[:5]
        log.info(f"Renaming {name} to {new_name}...")
        name = new_name
    return name.upper()


##########
# CHANNELS
##########

class HpMeasurementChannel(Channel):
    """Offers some COMon properties."""

    def __init__(self, parent, id):
        super().__init__(parent, int(str(id)[-1]))
        self.manual_flush = False

        self._voltage_name = "VS"
        self._disabled = False
        self._value = 0

        self._channel_mode = "COM"
        self._channel_modes = {'V': 1, 'I': 2, 'COM': 3}

        self._channel_functions = {"VAR1": 1, "VAR2": 2, "CONST": 3, "VARD": 4}
        self._channel_function = "CONST"

        self._voltage_values = [-100, 100]
        self._current_values = [-100e-3, 100e-3]

        self._voltage_write_command = None
        self._voltage_read_command = None

        self._current_write_command = None
        self._current_read_command = None

        self._disable_command = None

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to VS[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.

        .. code-block:: python

            instr.smu1.voltage_name = "Vbase"
        """
        raise LookupError("Property can not be read.")

    @voltage_name.setter
    def voltage_name(self, value):
        self._voltage_name = check_current_voltage_name(value)
        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

    def reset_settings(self):
        """Reset the settings of this channel to default value.

        .. code-block:: python

            instr.smu1.reset_settings()
        """
        self.write(f"DE {self._disable_command} {'{ch}'}")
        self._disabled = True
        self.check_set_errors()

    def disable(self):
        """Set the settings of this channel to default value.

        .. code-block:: python

            instr.smu1.disable
        """
        self.reset_settings()

    @property
    def channel_mode(self):
        """
        Set the source mode of the channel.

        Not applicable in 'USER_MODE'.

        Implicitly writes/flushes :attr:`channel_function`, :attr:`current_name`
        and :attr:`voltage_name`.

        .. code-block:: python

            hp4145a.SMU2.voltage_name = "VCE2"
            hp4145a.SMU2.current_name = "ICE2"
            hp4145a.SMU2.channel_function = "VAR2"
            hp4145a.SMU2.channel_mode = "V"
        """
        raise LookupError("Property can not be read.")

    @channel_mode.setter
    def channel_mode(self, value):
        self._channel_mode = strict_discrete_set(value, self._channel_modes)

        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def channel_function(self):
        """
        Set the source function, values "VAR1", "VAR2", "CONST" or "VAR1'" are allowed.

        Implicitly writes/flushs :attr:`voltage_name`.
        """
        raise LookupError("Property can not be read.")

    @channel_function.setter
    def channel_function(self, value):
        self._disabled = False
        self._channel_function = strict_discrete_set(
            value, self._channel_functions)

        if value == 'VAR1':
            self.parent.var1.disabled = False
        elif value == 'VAR2':
            self.parent.var2.disabled = False
        elif value == "VARD":
            self.parent.vard.disabled = False

        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def voltage(self):
        """
        Measure the voltage of one of the VM channels.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """
        if self._voltage_read_command is not None:
            if self.parent.mode == 'USER_MODE':
                value = float(self.ask(f"{self._voltage_read_command}"))
            else:
                raise RuntimeError("Property can't be read in 'SYSTEM_MODE'")

            self.check_get_errors()
            return value
        else:
            raise LookupError("Property can not be read.")

    @property
    def voltage_setpoint(self):
        """
        Set the voltage of one of the channels.
        """
        raise LookupError("Property can not be read.")

    @voltage_setpoint.setter
    def voltage_setpoint(self, value):
        if self._voltage_write_command is not None:
            value = strict_range(value, [0, self._max_voltage])
            if self.parent.mode == 'USER_MODE':
                self.write(f"{self._voltage_write_command}" % value)
            else:
                raise RuntimeError("Property can't be set in 'SYSTEM_MODE'")

            self.check_set_errors()
        else:
            raise LookupError("Property can not be set.")

    @property
    def current(self):
        """
        Measure the output current of on of the SMU channels.
        Automatically puts the SMU into force current mode once set.

        .. code-block:: python

            hp4145a.SMU2.voltage_compliance = 10
            hp4145a.SMU2.current = 10e-3

        """
        if self._current_read_value is not None:
            if self.parent.mode == 'USER_MODE':
                value = self.ask(f"{self._current_read_command}")
            else:
                raise RuntimeError("Property can't be read in 'SYSTEM_MODE'")

            self.check_get_errors()
            return value
        else:
            raise LookupError("Property can not be read.")

    @property
    def current_setpoint(self):
        """
        Set the current of one of the channels.
        """
        raise LookupError("Property can not be read.")

    @current_setpoint.setter
    def current_setpoint(self, value):
        if self._current_write_value is not None:
            value = strict_range(value, [0, self._max_current])
            if self.parent.mode == 'USER_MODE':
                self.write(f"{self._current_write_command}" % value)
            else:
                raise RuntimeError("Property can't be set in 'SYSTEM_MODE'")
            self.check_set_errors()
        else:
            raise LookupError("Property can not be set.")


class SMU(HpMeasurementChannel):
    """SMU of hp 4145A/4145B Semiconductor Parameter Analyzer"""

    def __init__(self, parent, id):
        super().__init__(
            parent,
            id
        )

        self._compliance = 0.0
        self._value = 0.0
        self._voltage_name = f"V{self.id}"
        self._current_name = f"I{self.id}"

        self._current_read_command = "TI {ch}"
        self._voltage_read_command = "TV {ch}"

        self._disable_command = "CH"

    def flush_channel_definition(self):
        """
        Flush the channel definition manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self._disabled:
            channel_mode_id = self._channel_modes[self._channel_mode]
            channel_function_id = self._channel_functions[self._channel_function]
            self.write(
                self.insert_id(
                    f"DE CH {'{ch}'}, '{self._voltage_name}', '{self._current_name}', "
                    f"{channel_mode_id}, {channel_function_id}"))

            self.check_errors()

    def flush_source_setup(self):
        """
        Flush the source setup manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self._disabled:
            if self._channel_mode == 'V':
                self.write(f"SS VC {'{ch}'}, {self._value:f}, {self._compliance:f}")
            elif self._channel_mode == 'I':
                self.write(f"SS IC {'{ch}'}, {self._value:f}, {self._compliance:f}")
            self.check_errors()

    @property
    def constant_value(self):
        """Control the constant source value of SMU<n>.

        You use this COMand only if :meth:`~.SMU.channel_function`
        is :code:`CONST` and also :meth:`~.SMU.channel_mode` should not be :code:`COM`.
        .. code-block:: python

            instr.smu1.constant_value = 1
        """
        raise LookupError("Property can't be read")

    @constant_value.setter
    def constant_value(self, const_value):
        validator = strict_range
        values = self.__validate_cons()
        value = validator(const_value, values)

        self._value = value
        self._disabled = False
        self.flush_source_setup()

    @property
    def compliance(self):
        """Control the *constant* compliance value of SMU<n>.

        If the SMU channel is setup as a variable (VAR1, VAR2, VARD) then compliance limits are
        set by the variable definition.

        - Value: Voltage in (-100V, 100V) and current in (-100mA, 100mA) based
          on :meth:`~.SMU.channel_mode`.

        .. code-block:: python

            instr.smu1.compliance = 0.1
        """
        raise LookupError("Property can't be read")

    @compliance.setter
    def compliance(self, comp):
        validator = strict_range
        values = self.__validate_compl()
        value = validator(comp, values)

        self._compliance = value
        self._disabled = False
        if not self.manual_flush:
            self.flush_source_setup()

    @property
    def current_name(self):
        """
        Control the current name for `SYSTEM_MODE`'s channel definition.

        Defaults to VS[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.

        .. code-block:: python

            instr.smu1.current_name = "Vbase"
        """
        raise LookupError("Property can not be read.")

    @current_name.setter
    def current_name(self, value):
        self._current_name = check_current_voltage_name(value)
        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def voltage(self):
        """
        Measure the output voltage in 'USER_MODE'.
        """
        return super().voltage

    @property
    def voltage_setpoint(self):
        """
        Set the output voltage in 'USER_MODE'.
        """
        raise LookupError("Property can not be read.")

    @voltage_setpoint.setter
    def voltage_setpoint(self, value):
        self._voltage_write_command = f"DV {'{ch}'}, 0, %f, {self.compliance:f}"
        super().voltage_setpoint = value

    @property
    def current(self):
        """
        Measure the output current in 'USER_MODE'.
        """
        return super().current

    @property
    def current_setpoint(self):
        """
        Set the output current in 'USER_MODE'.
        """
        raise LookupError("Property can not be read.")

    @current_setpoint.setter
    def current_setpoint(self, value):
        self._current_write_command = f"DI {'{ch}'}, 0, %f, {self.compliance:f}"
        super().current_setpoint = value

    def __validate_cons(self):
        """Validates the instrument settings for operation in constant mode.
        """
        if not ((self._channel_mode != 'COM') and (
                self._channel_function == 'CONST')):
            raise ValueError(
                'Cannot set constant SMU function when SMU mode is COMON, '
                'or when SMU function is not CONSTANT.'
            )
        else:
            values = valid_iv(self._channel_mode, self._voltage_values, self._current_values)
        return values

    def __validate_compl(self):
        """Validates the instrument compliance for operation in constant mode.
        """
        if not ((self._channel_mode != 'COM') and (
                self._channel_function == 'CONST')):
            raise ValueError(
                'Cannot set constant SMU parameters when SMU mode is COMON, '
                'or when SMU function is not CONSTANT.'
            )
        else:
            values = valid_compliance(self._channel_mode)
        return values


class VMU(HpMeasurementChannel):
    """VMU of hp 4155/4156 Semiconductor Parameter Analyzer"""

    def __init__(self, parent, id):
        super().__init__(
            parent,
            id
        )
        self._channel_modes = {'V': 1}
        self._voltage_name = f"VM{self.id}"
        self._voltage_read_command = f"TV {self.id + 4}, %f"

        self._disable_command = "VM"

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            self.write(f"DE VM {self.id}, '{self._voltage_name}'")
            self.check_errors()


class VSU(HpMeasurementChannel):
    """VSU of hp 4145A/4145B Semiconductor Parameter Analyzer"""

    def __init__(self, parent, id, **kwargs):
        super().__init__(
            parent,
            id,
            **kwargs
        )
        self._channel_modes = {'V': 1}
        self._voltage_name = f"VS{self.id}"
        self._voltage_write_command = "DS {ch}, %f"

        self._disable_command = "VS"

    def flush_source_setup(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            if self._channel_function == 'CONST':
                self.write(f"SS SC {'{ch}'}, {self._value:f}")

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            channel_function_id = self._channel_functions[self._channel_function]
            self.write(f"DE VS {self.id}, '{self._voltage_name}', {channel_function_id}")
            self.check_errors()


#################
# SWEEP VARIABLES
#################

class VARX(Channel):
    """ Base class to define sweep variable settings."""

    def __init__(self, parent, id):
        super().__init__(
            parent,
            id
        )

        self._start = 0
        self._stop = 0
        self._step = 0

        self._sweep_mode = 'LINEAR'
        self._sweep_modes = {'LINEAR': 1, 'LOG10': 2, 'LOG25': 3, 'LOG50': 4}

        self._channel_mode = "V"
        if self.id == 1:
            self._channel_modes = {'V': 'VR', 'I': 'IR'}
        else:
            self._channel_modes = {'V': 'VP', 'I': 'IP'}
        self._compliance = 0

        self.manual_flush = False
        self.disabled = True

    @property
    def channel_mode(self):
        """Control the channel mode."""
        raise LookupError("Property can't be read")

    @channel_mode.setter
    def channel_mode(self, value):
        self._channel_mode = strict_discrete_set(value, self._channel_modes)

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def start(self):
        """
        Set the start value for this sweep axis.

        .. code-block:: python

            instr.var1.start = 0
        """
        raise LookupError("Property can not be read.")

    @start.setter
    def start(self, value):
        self._start = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def step(self):
        """
        Set the step value for this sweep axis. Not applicable with :attr:`sweep_mode` != 'LINEAR'

        .. code-block:: python

            instr.var1.step = 0.1
        """
        raise LookupError("Property can not be read.")

    @step.setter
    def step(self, value):
        self._step = value

        self.disabled = False

        if self._sweep_mode != 'LINEAR':
            raise RuntimeError("Step not allowed with logarithmic sweep modes.")

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def compliance(self):
        """Control the sweep COMPLIANCE value. Either current or voltage depending on the set
        :attr:`channel_function`.

        .. code-block:: python

            instr.var1.compliance = 0.1
        """
        raise LookupError("Property can not be read.")

    @compliance.setter
    def compliance(self, value):
        self._compliance = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    def flush_source_setup(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        pass


class VAR1(VARX):
    """ Class to handle all the specific definitions needed for VAR1.
    Most COMon methods are inherited from base class.
    """

    def __init__(self, parent, id):
        super().__init__(
            parent,
            id
        )

    @property
    def sweep_mode(self):
        """
        Set the sweep mode for the respective variable 'LINEAR', 'LOG10', 'LOG25' and 'LOG50' are
        allowed.
        """
        raise LookupError("Property can not be read.")

    @sweep_mode.setter
    def sweep_mode(self, value):
        self._sweep_mode = strict_discrete_set(value, self._sweep_modes)

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def stop(self):
        """
        Set the stop value for this sweep axis.
        """
        raise LookupError("Property can not be read.")

    @stop.setter
    def stop(self, value):
        self._stop = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    def flush_source_setup(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self.disabled:
            if self._sweep_mode == "LINEAR":
                self.write(self.insert_id(f"SS {self._channel_modes[self._channel_mode]}"
                                          f"{self._sweep_modes[self._sweep_mode]},{self._start:f},"
                                          f"{self._stop:f},{self._step:f},{self._compliance:f}"))
            else:
                self.write(self.insert_id(f"SS {self._channel_modes[self._channel_mode]}"
                                          f"{self._sweep_modes[self._sweep_mode]},{self._start:f},"
                                          f"{self._stop:f},{self._compliance:f}"))
            self.check_set_errors()


class VAR2(VARX):
    """ Class to handle all the specific definitions needed for VAR2.
    COMon methods are imported from base class.
    """

    def __init__(self, parent, id):
        super().__init__(
            parent,
            id
        )
        self._steps = 1

    def flush_source_setup(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self.disabled:
            self.write(f"SS {self._channel_modes[self._channel_mode]}{self._start:f},"
                       f"{self._step:f},{self._steps:f},{self._compliance:f}")
            self.check_set_errors()

    @property
    def steps(self):
        """
        Set the steps value for this sweep axis.
        """
        raise LookupError("Property can not be read.")

    @steps.setter
    def steps(self, value):
        self._steps = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()


class VARD(Channel):
    """ Class to handle all the definitions needed for VARD.
    VARD is always defined in relation to VAR1.
    """

    def __init__(self, parent, id):
        super().__init__(
            parent,
            "VARD"
        )

    offset = Instrument.setting(
        "FS %f",
        """
        Control the OFFSET value of VARD.
        For each step of sweep, the output values of VAR1' are determined by the
        following equation: VAR1' = VAR1 + OFFSet
        You use this COMand only if there is an SMU or VSU whose function is VARD.

        .. code-block:: python

            instr.vard.offset = 1
        """)

    ratio = Instrument.setting(
        "RT %f",
        """
        Control the RATIO of VAR1'.
        For each step of sweep, the output values of VAR1' are determined by the
        following equation: VAR1' = VAR1 * RATio
        You use this COMand only if there is an SMU or VSU whose function
        (FCTN) is VAR1'.

        .. code-block:: python

            instr.vard.ratio = 1
        """
    )


def valid_iv(channel_mode, voltagevalues, currentvalues):
    if channel_mode == 'V':
        values = voltagevalues
    elif channel_mode == 'I':
        values = currentvalues
    else:
        raise ValueError(
            'Channel is not in V or I mode. It might be disabled.')
    return values


def valid_compliance(channel_mode):
    if channel_mode == 'I':
        values = [-100, 100]
    elif channel_mode == 'V':
        values = [-100e-3, 100e-3]
    else:
        raise ValueError(
            'Channel is not in V or I mode. It might be disabled.')
    return values


class HP4145x(Instrument):
    """ Represents the HP 4145A/4145B Semiconductor Parameter Analyzer
    and provides a high-level interface for taking current-voltage (I-V) measurements.

    .. code-block:: python

        from pymeasure.instruments.hp import HP4145x

        # explicitly define r/w terminations; set sufficiently large timeout or None.
        smu = HP4145x("GPIB0::25", read_termination = '\\n', write_termination = '\\n',
                          timeout=None)

        # reset the instrument
        smu.reset()

        # define configuration file for instrument and load config
        smu.configure("configuration_file.json")

        # measured data is a pandas dataframe and can be exported to csv.
        data = smu.get_data(path='./t1.csv')

    The JSON file is an ascii text configuration file that defines the settings of each channel
    on the instrument. The JSON file is used to configure the instrument using the convenience
    function :meth:`~.HP4145x.configure` as shown in the example above. For example, the
    instrument setup for a bipolar transistor measurement is shown below.

    .. code-block:: json

         {
                "SMU1": {
                    "voltage_name" : "VC",
                    "current_name" : "IC",
                    "channel_function" : "VAR1",
                    "channel_mode" : "V"
                },

                "SMU2": {
                    "voltage_name" : "VB",
                    "current_name" : "IB",
                    "channel_function" : "VAR2",
                    "channel_mode" : "I"
                },

                "SMU3": {
                    "voltage_name" : "VE",
                    "current_name" : "IE",
                    "channel_function" : "CONST",
                    "channel_mode" : "V",
                    "constant_value" : 0,
                    "compliance" : 0.1
                },

                 "SMU4": {
                    "voltage_name" : "VS",
                    "current_name" : "IS",
                    "channel_function" : "CONST",
                    "channel_mode" : "V",
                    "constant_value" : 0,
                    "compliance" : 0.1
                },

                "VAR1": {
                    "start" : 1,
                    "stop" : 2,
                    "step" : 0.1,
                    "spacing" : "LINEAR",
                    "compliance" : 0.1
                },

                "VAR2": {
                    "start" : 0,
                    "step" : 10e-6,
                    "steps" : 5
                    "compliance" : 2
                }
            }

    """

    smu1: SMU = Instrument.ChannelCreator(SMU, "smu1")
    smu2: SMU = Instrument.ChannelCreator(SMU, "smu2")
    smu3: SMU = Instrument.ChannelCreator(SMU, "smu3")
    smu4: SMU = Instrument.ChannelCreator(SMU, "smu4")

    vmu1: VMU = Instrument.ChannelCreator(VMU, "vmu1")
    vmu2: VMU = Instrument.ChannelCreator(VMU, "vmu2")

    vsu1: VSU = Instrument.ChannelCreator(VSU, "vsu1")
    vsu2: VSU = Instrument.ChannelCreator(VSU, "vsu2")

    var1: VAR1 = Instrument.ChannelCreator(VAR1, "var1")
    var2: VAR2 = Instrument.ChannelCreator(VAR2, "var2")
    vard: VARD = Instrument.ChannelCreator(VARD, "vard")


    def __init__(self, adapter, name="HP 4145A/4145B Semiconductor Parameter Analyzer",
                 **kwargs):
        kwargs.setdefault('timeout', 100000)
        super().__init__(
            adapter,
            name,
            **kwargs
        )

        self._mode = None
        self._manual_flush = False

        print(self.channels)

    @property
    def manual_flush(self):
        """
        Control the manual flushing of channels 'channel definition'
        """
        return self._manual_flush

    @manual_flush.setter
    def manual_flush(self, value):
        for channel in self.channels:
            channel.manual_flush = value
        self._manual_flush = value

    def flush_channel_definition(self):
        """
        Flush the channel definitions of all sub channels.
        Only required with :attr:`manual_flush` True.
        """
        for channel in self.channels:
            if hasattr(channel, 'flush_channel_definition'):
                channel.flush_channel_definition()

    def flush_source_setup(self):
        """
        Flush the channel definitions of all sub channels.
        Only required with :attr:`manual_flush` True.
        """
        for channel in self.channels:
            if hasattr(channel, 'flush_source_setup'):
                channel.flush_source_setup()

    integration_time = Instrument.setting(
        "SS %s",
        """Set the integration time.

        Values: :code:`SHORT` for no averages, :code:`MEDIUM` for 16 averages and :code:`LONG`
        for 256 averages

        .. code-block:: python

            instr.integration_time = "MEDIUM"
        """,
        validator=strict_discrete_set,
        values={'SHORT': 'IT1', 'MEDIUM': 'IT2', 'LONG': 'IT3'},
        map_values=True,
        check_set_errors=True
    )

    delay_time = Instrument.setting(
        "DT %f",
        """Set the measurement delay time in seconds,
        which can take the values from 0 to 6.5s in 1ms steps.

        .. code-block:: python

            instr.delay_time = 1 # delay time of 1-sec
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 6.5, 0.001),
        check_set_errors=True
    )

    hold_time = Instrument.setting(
        "HT %f",
        """Set the measurement hold time in seconds,
        which can take the values from 0 to 650s in 10ms steps.

        .. code-block:: python

            instr.hold_time = 2 # hold time of 2-secs.
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 650, 0.01),
        check_set_errors=True
    )

    auto_calibrate = Instrument.setting(
        "CA%d",
        """
        Set the instrument to automatically calibrate internally every 15minutes.
        """,
        values=[True, False],
        validator=strict_discrete_set,
        check_set_errors=True
    )

    def self_test(self):
        """
        Execute the self test and return pass/fail.
        """
        self.write("SF")
        status = self.status
        return (not (status & Status.SELF_TEST_FAIL)) and (status & Status.END_STATUS)

    def stop(self):
        """Stop the ongoing measurement.

        .. code-block:: python

            instr.stop()
        """
        self.write("MD ME4")

    def measure(self, continuous=False):
        """
        Perform a measurement.

        .. code-block::python

            instr.measure() # for normale measurement (single)
            instr.measure(continuous=True) # for repeated infinite measurement
        """
        if continuous:
            self.write("MD ME2")
        else:
            self.write("MD ME1")

    def disable_all(self):
        """ Disable all channels in the instrument.

        .. code-block:: python

            instr.disable_all()
        """
        for channel in self.channels:
            if hasattr(channel, 'reset_settings'):
                channel.reset_settings()

    def configure(self, config_file):
        """ Configure the channel setup and sweep using a JSON configuration file.

        (JSON is the `JavaScript Object Notation`_)

        .. _`JavaScript Object Notation`: https://www.json.org/

        :param config_file: JSON file to configure instrument channels.

        .. code-block:: python

            instr.configure('config.json')
        """
        self.disable_all()
        obj_dict = {'SMU1': self.smu1,
                    'SMU2': self.smu2,
                    'SMU3': self.smu3,
                    'SMU4': self.smu4,
                    'VMU1': self.vmu1,
                    'VMU2': self.vmu2,
                    'VSU1': self.vsu1,
                    'VSU2': self.vsu2,
                    'VAR1': self.var1,
                    'VAR2': self.var2,
                    'VARD': self.vard
                    }
        with open(config_file) as stream:
            try:
                instr_settings = json.load(stream)
            except json.JSONDecodeError as e:
                print(e)

        # replace dict keys with Instrument objects
        new_settings_dict = {}
        for key, value in instr_settings.items():
            new_settings_dict[obj_dict[key]] = value

        for obj, setup in new_settings_dict.items():
            for setting, value in setup.items():
                setattr(obj, setting, value)
                time.sleep(0.1)

    def set_graphics_mode(self, mode, **kwargs):
        """
        Set and configure 'MATRIX' graphics mode.
        """
        channel_name = kwargs.get("channel_name")
        self.write(f"SM DM3 MX '{channel_name}'")

    @property
    def data_ready_srq(self):
        """
        Set the data ready enablement of the bit of the status byte.
        """
        raise LookupError("Property can not be read.")

    @data_ready_srq.setter
    def data_ready_srq(self, value):
        value = strict_discrete_set(value, [True, False])
        self.write("DR%d" % value)
        # retrieve status once
        # (instrument issues for unknown reasons returns illegal program sometimes)
        self.adapter.connection.read_stb()

    def get_data(self, name, number=1, header=None, index=None, path=None):
        """
        Return the dataframe of values for the given variable name.
        Name is the same as defined in the channel definition.

        Returns measurement data in the same order as executed.
        In case a VAR2 is used, there is VAR1 steps * VAR2 steps
        results, that you have to split.

        If you provide a :code:`number=n` it will stack the columns of
        into a 2D data frame with 'n' number of columns.

        Requires the analyzer to be in MATRIX grahpics mode :attr:`select_grahpics_mode`.

        :param path: Path for optional data export to CSV.
        :param name: Name of axis to dump
        :param header: List of headers in case multiple values are given (overwrites number)
        :param number: Number of columns for VAR2 usage.
        """
        self.write(f"DO '{name}'")

        result = self.read().replace("\r", "").replace("\n", "")
        removed_status = filter(None, result.replace("N", "").replace("C", "")
                                .replace("T", "").replace("X", "").replace("L", "").split(","))

        data = np.array([float(x) for x in removed_status])

        if number != 1 and header is None:
            data = data.reshape(number, int(len(data) / number))
            header = np.arange(number)
            df = pd.DataFrame(data=dict(zip(header, data)))
        elif header is not None:
            data = data.reshape(len(header), int(len(data) / len(header)))
            df = pd.DataFrame(data=dict(zip(header, data)), index=index)
        else:
            df = pd.DataFrame(data=data)

        if path is not None:
            _, ext = os.path.splitext(path)
            if ext != ".csv":
                path = path + ".csv"
            df.to_csv(path, index=True)

        return df

    @property
    def mode(self):
        """
        Control the mode of the instrument. Either 'USER_MODE' -
        user controls manually all SMUs and voltage sources
        or 'SYSTEM_MODE' where the analyzer gets configured to sweep
        automatically the resources on it's own.
        """
        return self._mode

    @mode.setter
    def mode(self, value):
        self._mode = strict_discrete_set(value, ['USER_MODE', 'SYSTEM_MODE'])
        if self._mode == 'USER_MODE':
            self.write("US")
        else:
            self.write("DE")

    @property
    def status(self):
        """
        Get the VISA status byte.
        """
        stb = self.adapter.connection.read_stb()
        return stb if type(stb) is int else 0

    def reset(self):
        """
        Reset the device of all user config.
        """
        self.adapter.connection.clear()

    def clear(self):
        """ Clear the HP-IB buffer of the device and status bit 1 (Data Ready) """
        self.write("BC")

    def check_errors(self):
        errors = []
        error_status = [Status.EMERGENCY, Status.SYNTAX_ERROR, Status.BUSY, Status.ILLEGAL_PROGRAM]
        while (Status.EMERGENCY not in errors[0]) is False if len(errors) > 0 else True:
            # mask out RQS (always set with other bits)
            status = self.status & ~Status.RQS
            if any(es & status for es in error_status):
                for es in error_status:
                    if status & es and es == Status.EMERGENCY:
                        log.error(f"HP4145x: {Status(status).value} - {Status(status).name}")
                        errors.append(Status(status))
                        break
                    elif status & es:
                        log.error(f"HP4145x: {es.value} - {es.name}")
                        errors.append(es)
            else:
                break
        return errors