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
import logging
from enum import IntEnum

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (strict_discrete_set, truncated_discrete_set,
                                              strict_range)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


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


class Status(IntEnum):
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


class VS(Channel):
    _voltage_name = "VS"
    _disabled = False
    _voltage = 0

    _channel_functions = {"VAR1": 1, "VAR2": 2, "CONST": 3, "VAR1'": 4}
    _channel_function = 3

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._voltage_name = f"VS{self.id}"

    @property
    def voltage(self):
        """
        Set the output voltage of one of the VS channels.

        In 'USER_MODE' directly sets the output voltage.
        In 'SYSTEM_MODE' only allowed with :attr:`channel_function` = 'CONST'.
        """
        raise LookupError("Property can not be read.")

    @voltage.setter
    def voltage(self, value):
        value = strict_range(value, [0, 20])

        self._disabled = False
        if self.parent.mode == 'USER_MODE':
            self.write("DS {ch}, %f" % value)
        else:
            # SYSTEM_MODE
            if self._channel_function == self._channel_functions['CONST']:
                self._voltage = value
                if not self.manual_flush:
                    self.flush_source_setup()
            else:
                raise RuntimeError("In SYSTEM_MODE only allowed with channel_function = 'CONST'")

        self.check_set_errors()

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to VS[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @voltage_name.setter
    def voltage_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._voltage_name = value.upper()
        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def disabled(self):
        """
        Set the disabling of the respective channel.
        """
        raise LookupError("Property can not be read.")

    @disabled.setter
    def disabled(self, value):
        if not value:
            raise ValueError(
                "Channel can only be disabled, it gets enabled implicitly with the other functions")
        self._disabled = True
        self.write("DE VS {ch}")
        self.check_set_errors()

    @property
    def channel_function(self):
        """
        Set the source function, values "VAR1", "VAR2", "CONST" or "VAR1'" are allowed.

        Implicitly writes/flushs :attr:`voltage_name`.
        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @channel_function.setter
    def channel_function(self, value):
        self._disabled = False
        self._channel_function = self._channel_functions[strict_discrete_set(
            value, self._channel_functions)]

        if value == 'VAR1':
            self.parent.VAR1.disabled = False
        elif value == 'VAR2':
            self.parent.VAR2.disabled = False

        if not self.manual_flush:
            self.flush_channel_definition()

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            self.write("DE VS %d, '%s', %d" % (self.id, self._voltage_name, self._channel_function))
            self.check_errors()

    def flush_source_setup(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            if self._channel_function == self._channel_functions['CONST']:
                self.write("SS SC {ch}, %f" % self._voltage)


class VM(Channel):
    _voltage_name = "VM"
    _disabled = False

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._voltage_name = f"VM{self.id}"

    @property
    def voltage(self):
        """
        Measure the voltage of one of the VM channels.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """
        if self.parent.mode == 'USER_MODE':
            value = float(self.ask(f"TV {self.id + 4}"))
        else:
            raise RuntimeError("In SYSTEM_MODE not allowed")

        self.check_get_errors()
        return value

    @voltage.setter
    def voltage(self, value):
        raise LookupError("Property can not be set.")

    @property
    def disabled(self):
        """
        Set the disabling of the respective channel.
        """
        raise LookupError("Property can not be read.")

    @disabled.setter
    def disabled(self, value):
        self._disabled = True
        if not value:
            raise ValueError(
                "Channel can only be disabled, it gets enabled implicitly with the other functions")

        self.write("DE VM {ch}")

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to VM[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @voltage_name.setter
    def voltage_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._voltage_name = value.upper()
        self._disabled = False

        if not self.manual_flush:
            self.write("DE VM %d, '%s'" % (self.id, self._voltage_name))
            self.check_errors()

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        if not self._disabled:
            self.write("DE VM %d, '%s'" % (self.id, self._voltage_name))
            self.check_errors()


class SMU(Channel):
    _voltage_range = 0
    _voltage_ranges = {0: 0, 20: 1, 40: 2, 100: 3}
    _current_range = 0
    _current_ranges = {0: 0, 1e-9: 1, 10e-9: 2, 100e-9: 3,
                       1e-6: 4, 10e-6: 5, 100e-6: 6, 1e-3: 7, 10e-3: 8, 100e-3: 9}

    _current_max = 100e-3
    _current_compliance = 0.0

    _voltage_max = 100
    _voltage_compliance = 0.0

    _voltage_name = ''
    _current_name = ''

    _channel_function = 3
    _channel_functions = {"VAR1": 1, "VAR2": 2, "CONST": 3, "VAR1'": 4}

    _channel_mode = 3
    _channel_modes = {'V': 1, 'I': 2, 'COM': 3}

    _voltage = 0
    _current = 0

    _disabled = False

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._voltage_name = f"V{self.id}"
        self._current_name = f"I{self.id}"

    @property
    def voltage(self):
        """
        Controls the output voltage of on of the SMU channels.
        Automatically puts the SMU into force voltage mode once set.

        .. code-block:: python

            hp4145a.SMU2.current_compliance = 10e-3
            hp4145a.SMU2.voltage = 10

        """
        if self.parent.mode == 'USER_MODE':
            value = self.ask("TV {ch}")
        else:
            raise LookupError("Property can't be read in 'SYSTEM_MODE'")

        self.check_get_errors()
        return value

    @voltage.setter
    def voltage(self, value):
        max_voltage = 100 if self._voltage_range == 0 else self._voltage_ranges[self._voltage_range]
        value = strict_range(value, [0, max_voltage])

        if self.parent.mode == 'USER_MODE':
            self.write("DV {ch}, %d, %f, %f" %
                       (self._voltage_range, value, self._current_compliance))
        else:
            # SYSTEM_MODE
            if self._channel_function == self._channel_functions['CONST']:
                self._voltage = value
                if not self.manual_flush:
                    self.flush_source_setup()
            else:
                raise RuntimeError("In SYSTEM_MODE only allowed with channel_function = 'CONST'")
        self.check_set_errors()

    @property
    def current(self):
        """
        Controls the output current of on of the SMU channels.
        Automatically puts the SMU into force current mode once set.

        .. code-block:: python

            hp4145a.SMU2.voltage_compliance = 10
            hp4145a.SMU2.current = 10e-3

        """
        if self.parent.mode == 'USER_MODE':
            value = self.ask("TI {ch}")
        else:
            raise LookupError("Property can't be read in 'SYSTEM_MODE'")

        self.check_get_errors()
        return value

    @current.setter
    def current(self, value):
        max_current = 100 if self._current_range == 0 else self._current_ranges[self._current_range]
        value = strict_range(value, [0, max_current])

        if self.parent.mode == 'USER_MODE':
            self.write("DI {ch}, %d, %f, %f" %
                       (self._current_range, value, self._voltage_compliance))
        else:
            # SYSTEM_MODE
            if self._channel_function == self._channel_functions['CONST']:
                self._current = value
                if not self.manual_flush:
                    self.flush_source_setup()
            else:
                raise RuntimeError("In SYSTEM_MODE only allowed with channel_function = 'CONST'")
        self.check_set_errors()

    @property
    def disabled(self):
        """
        Set the disabling of the respective channel. Returns only the internal state (can't read
        the instrument).
        """
        raise LookupError("Property can not be read.")

    @disabled.setter
    def disabled(self, value):
        if not value:
            raise ValueError(
                "Channel can only be disabled, it gets enabled implicitly with the other functions")

        self._disabled = True
        self.write("DE CH {ch}")

    @property
    def voltage_range(self):
        """
        Controls the voltage range used by :attr:`voltage`. Only applicable in `USER_MODE`.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @voltage_range.setter
    def voltage_range(self, value):
        self._voltage_range = self._voltage_ranges[truncated_discrete_set(
            value, self._voltage_ranges)]

    @property
    def current_range(self):
        """
        Controls the current range used by :attr:`current`. Only applicable in `USER_MODE`.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @current_range.setter
    def current_range(self, value):
        self._current_range = self._current_ranges[truncated_discrete_set(
            value, self._current_ranges)]

    @property
    def current_compliance(self):
        """
        Set the current compliance of the channel.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @current_compliance.setter
    def current_compliance(self, value):
        self._current_compliance = strict_range(value, [0, self._current_max])

        if self.parent.mode != 'USER_MODE':
            # SYSTEM_MODE
            if self._channel_function == self._channel_functions['CONST']:
                if not self.manual_flush:
                    self.flush_source_setup()
            else:
                raise RuntimeError("In SYSTEM_MODE only allowed with channel_function = 'CONST'")

    @property
    def voltage_compliance(self):
        """
        Set the voltage compliance of the channel.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @voltage_compliance.setter
    def voltage_compliance(self, value):
        self._voltage_compliance = strict_range(value, [0, self._voltage_max])

        if self.parent.mode != 'USER_MODE':
            # SYSTEM_MODE
            if self._channel_function == self._channel_functions['CONST']:
                if not self.manual_flush:
                    self.flush_source_setup()
            else:
                raise RuntimeError("In SYSTEM_MODE only allowed with channel_function = 'CONST'")

    @property
    def voltage_name(self):
        """
        Set the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to V[1..4]. Must be unqiue otherwise the instrument returns a 'PROGRAM_ERROR'.
        Only takes affect with a setting of :attr:`channel_mode`.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @voltage_name.setter
    def voltage_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._voltage_name = value.upper()
        self._disabled = False

        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def current_name(self):
        """
        Set the current name for `SYSTEM_MODE`'s channel definition.

        Defaults to I[1..4]. Must be unqiue otherwise the instrument returns a 'PROGRAM_ERROR'.
        Only takes affect with a setting of :attr:`channel_mode`.

        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @current_name.setter
    def current_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._current_name = value
        self._disabled = False

        if not self.manual_flush:
            self.flush_channel_definition()

    @property
    def channel_function(self):
        """
        Set the source function, values "VAR1", "VAR2", "CONST" or "VAR1'" are allowed.

        Not applicable in 'USER_MODE'.

        Implicitly writes/flushes :attr:`channel_mode`,
        :attr:`current_name` and :attr:`voltage_name`.
        Returns not the actual state of the instrument but the state of the object.
        """
        raise LookupError("Property can not be read.")

    @channel_function.setter
    def channel_function(self, value):
        self._channel_function = self._channel_functions[strict_discrete_set(
            value, self._channel_functions)]

        if value == 'VAR1':
            self.parent.VAR1.disabled = False
        elif value == 'VAR2':
            self.parent.VAR2.disabled = False

        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

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
        self._channel_mode = self._channel_modes[strict_discrete_set(value, self._channel_modes)]

        self._disabled = False
        if not self.manual_flush:
            self.flush_channel_definition()

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self._disabled:
            self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                      (self._voltage_name, self._current_name, self._channel_mode,
                                       self._channel_function)))
            self.check_errors()

    def flush_source_setup(self):
        """
        Flushes the source setup manually in case the :attr:`manual_flush` option is set.

        Not applicable in 'USER_MODE'.
        """
        if not self._disabled:
            if self._channel_mode == self._channel_modes['V']:
                self.write("SS VC {ch}, %f, %f" % (self._voltage, self._current_compliance))
            elif self._channel_mode == self._channel_modes['I']:
                self.write("SS IC {ch}, %f, %f" % (self._current, self._voltage_compliance))


class VAR1(Channel):
    _start = 0
    _stop = 0
    _step = 0

    _sweep_mode = 1
    _sweep_modes = {'LINEAR': 1, 'LOG10': 2, 'LOG25': 3, 'LOG50': 4}

    _source_mode = "V"
    _source_modes = {}
    _compliance = 0

    manual_flush = False
    disabled = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.id == 1:
            self._source_modes = {'V': 'VR', 'I': 'IR'}
        else:
            self._source_modes = {'V': 'VP', 'I': 'IP'}

    @property
    def source_mode(self):
        """
        Set the source mode of the channel. Either 'V' or 'I'. Select the resource to sweep.
        """
        raise LookupError()

    @source_mode.setter
    def source_mode(self, value):
        self._source_mode = strict_discrete_set(value, self._source_modes)

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def sweep_mode(self):
        """
        Set the sweep mode for the respective variable 'LINEAR', 'LOG10', 'LOG25' and 'LOG50' are
        allowed.
        """
        raise LookupError("Property can not be read.")

    @sweep_mode.setter
    def sweep_mode(self, value):
        self._sweep_mode = self._sweep_modes[strict_discrete_set(value, self._sweep_modes)]

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def start(self):
        """
        Set the start value for this sweep axis.
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

    @property
    def step(self):
        """
        Set the step value for this sweep axis. Not applicable with :attr:`sweep_mode` != 'LINEAR'
        """
        raise LookupError("Property can not be read.")

    @step.setter
    def step(self, value):
        self._step = value

        self.disabled = False

        if self._sweep_mode != self._sweep_modes['LINEAR']:
            raise RuntimeError("Step not allowed with logarithmic sweep modes.")

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def compliance(self):
        """
        Set the compliance value for this sweep axis.
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
        if not self.disabled:
            if self._sweep_mode == self._sweep_modes['LINEAR']:
                self.write(self.insert_id("SS %s%d,%f,%f,%f,%f" %
                                          (self._source_modes[self._source_mode],
                                           self._sweep_mode,
                                           self._start,
                                           self._stop,
                                           self._step,
                                           self._compliance)))
            else:
                self.write(self.insert_id("SS %s%d,%f,%f,%f" %
                                          (self._source_modes[self._source_mode],
                                           self._sweep_mode,
                                           self._start,
                                           self._stop,
                                           self._compliance)))
            self.check_set_errors()


class VAR2(Channel):
    _start = 0
    _step = 0
    _steps = 0

    _enabled = False

    _source_mode = "V"
    _source_modes = {'V': 'VP', 'I': 'IP'}
    _compliance = 0

    manual_flush = False
    disabled = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def source_mode(self):
        """
        Set the source mode of the channel. Either 'V' or 'I'. Select the resource to sweep.
        """
        raise LookupError()

    @source_mode.setter
    def source_mode(self, value):
        self._source_mode = strict_discrete_set(value, self._source_modes)

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def start(self):
        """
        Set the start value for this sweep axis.
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
        Set the step value for this sweep axis.
        """
        raise LookupError("Property can not be read.")

    @step.setter
    def step(self, value):
        self._step = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def steps(self):
        """
        Set the amount of steps.
        """
        raise LookupError("Property can not be read.")

    @steps.setter
    def steps(self, value):
        self._steps = value

        self.disabled = False

        if not self.manual_flush:
            self.flush_source_setup()

        self.check_set_errors()

    @property
    def compliance(self):
        """
        Set the compliance value for this sweep axis.
        """
        raise LookupError("Property can not be read.")

    @compliance.setter
    def compliance(self, value):
        self._compliance = value
        self._enabled = True
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
            self.write(self.insert_id("SS %s%f,%f,%d,%f" %
                                      (self._source_modes[self._source_mode],
                                       self._start,
                                       self._step,
                                       self._steps,
                                       self._compliance)))

            self.check_set_errors()


class HP4145x(Instrument):
    SMU1: SMU = Instrument.ChannelCreator(SMU, 1)
    SMU2: SMU = Instrument.ChannelCreator(SMU, 2)
    SMU3: SMU = Instrument.ChannelCreator(SMU, 3)
    SMU4: SMU = Instrument.ChannelCreator(SMU, 4)
    VS1: VS = Instrument.ChannelCreator(VS, 1)
    VS2: VS = Instrument.ChannelCreator(VS, 2)
    VM1: VM = Instrument.ChannelCreator(VM, 1)
    VM2: VM = Instrument.ChannelCreator(VM, 2)

    VAR1: VAR1 = Instrument.ChannelCreator(VAR1, 1)
    VAR2: VAR2 = Instrument.ChannelCreator(VAR2, 2)

    _mode = "SYSTEM_MODE"

    _manual_flush = False

    def __init__(self, adapter, name="Hewlett-Packard HP4145x", **kwargs):
        kwargs.setdefault('timeout', 100000)
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

    def flush_channel_definition(self):
        """
        Flush the channel definitions of all sub channels.
        Only required with :attr:`manual_flush` True.
        """
        self.SMU1.flush_channel_definition()
        self.SMU2.flush_channel_definition()
        self.SMU3.flush_channel_definition()
        self.SMU4.flush_channel_definition()
        self.VM1.flush_channel_definition()
        self.VM2.flush_channel_definition()
        self.VS1.flush_channel_definition()
        self.VS2.flush_channel_definition()

    def flush_source_setup(self):
        """
        Flush the channel definitions of all sub channels.
        Only required with :attr:`manual_flush` True.
        """
        self.VAR1.flush_source_setup()
        self.VAR2.flush_source_setup()
        self.SMU1.flush_source_setup()
        self.SMU2.flush_source_setup()
        self.SMU3.flush_source_setup()
        self.SMU4.flush_source_setup()
        self.VS1.flush_source_setup()
        self.VS2.flush_source_setup()

    @property
    def manual_flush(self):
        """
        Control the manual flushing of channels 'channel definition'
        """
        return self._manual_flush

    @manual_flush.setter
    def manual_flush(self, value):
        self.SMU1.manual_flush = value
        self.SMU2.manual_flush = value
        self.SMU3.manual_flush = value
        self.SMU4.manual_flush = value
        self.VM1.manual_flush = value
        self.VM2.manual_flush = value
        self.VS1.manual_flush = value
        self.VS2.manual_flush = value
        self.VAR1.manual_flush = value
        self.VAR2.manual_flush = value
        self._manual_flush = value

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
        """ Clears the HP-IB buffer of the device and status bit 1 (Data Ready) """
        self.write("BC")

    def check_errors(self):
        errors = []
        error_status = [Status.EMERGENCY, Status.SYNTAX_ERROR, Status.BUSY, Status.ILLEGAL_PROGRAM]
        while (errors[0].value & Status.EMERGENCY.value) is False if len(errors) > 0 else True:
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

    integration_time = Instrument.setting(
        "IT%d",
        """
        Set the integration time. 'SHORT' no integration at all,
        'MEDIUM' 16 samples per measurement and 'LONG'
        256 samples per measurement.
        """,
        map_values=True,
        values={"SHORT": 1, "MEDIUM": 2, "LONG": 3},
        validator=strict_discrete_set,
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
        self.status()

    def self_test(self):
        """
        Execute the self test and return pass/fail.
        """
        self.write("SF")
        status = self.status
        return bool((not (status & Status.SELF_TEST_FAIL)) and (status & Status.END_STATUS))

    def get_trace(self, name):
        """
        Return the list of values for the given variable name.
        Name is the same as defined in the channel definition.

        Returns measurement data in the same order as executed.
        In case a VAR2 is used, there is VAR1 steps * VAR2 steps
        results, that you have to split.
        """
        self.write("DO '%s'" % name)

        result = self.read().replace("\r", "").replace("\n", "")
        removed_status = filter(None, result.replace("N", "").replace("C", "")
                                .replace("T", "").replace("X", "").replace("L", "").split(","))

        return [float(x) for x in removed_status]

    hold_time = Instrument.setting(
        "HT %f",
        """
        Set the wait time before sweep begins.
        """,
        validator=strict_range,
        values=[0, 650],
        check_set_errors=True
    )

    delay_time = Instrument.setting(
        "DT %f",
        """
        Set the wait time before measurement is made at each step.
        """,
        validator=strict_range,
        values=[0, 6.5],
        check_set_errors=True
    )

    def select_graphics_mode(self, mode, **kwargs):
        """
        Selects and configures the respective graphics mode.

        For mode == 'MATRIX' provide parameter 'channel_name'.
        """

        if mode != "MATRIX":
            raise ValueError("No graphics mode apart of matrix is supported")

        if mode == "MATRIX":
            channel_name = kwargs.get("channel_name")
            self.write("SM DM3 MX '%s'" % channel_name)

    def measure(self):
        """
        Measure once
        """
        self.write("MD ME1")
