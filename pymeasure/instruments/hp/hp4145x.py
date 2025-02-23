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
from pymeasure.instruments.validators import strict_discrete_set, truncated_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def check_errors_user_mode_value(cmd_str):
    data_status = cmd_str[0]
    channel = cmd_str[1]
    measurement_mode = cmd_str[2]
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


def mode_assert_lambda(parent, mode):
    def func(v):
        if parent.mode != mode:
            raise RuntimeError(f"Mode must be '{mode}' but is {parent.mode}")
        return v

    return func


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

    _channel_functions = {"VAR1": 1, "VAR2": 2, "CONST": 3, "VAR1'": 4}
    _channel_function = 3

    _disabled = False

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voltage_set_process = mode_assert_lambda(self.parent, "USER_MODE")

        self._voltage_name = f"VS{self.id}"

    voltage = Channel.setting(
        "DS {ch}, %f",
        """
        Controls the output voltage of on of the VS channels.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """,
        validator=strict_range,
        values=[0, 20],
        check_set_errors=True
    )

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to VS[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._voltage_name

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        if value != True:
            raise ValueError("Channel can only be disabled, it gets enabled implicitly with the other functions")

        self._disabled = True
        self.write("DE VS {ch}")

    @voltage_name.setter
    def voltage_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._voltage_name = value.upper()
        self._disabled = False
        if not self.manual_flush:
            self.write("DE VS %d, '%s', %d" % (self.id, self._voltage_name, self._channel_function))
            self.check_errors()

    @property
    def channel_function(self):
        """
        Control the source function, values "VAR1", "VAR2", "CONST" or "VAR1'" are allowed.

        Implicitly writes/flushs :attr:`voltage_name`.
        Returns not the actual state of the instrument but the state of the object.
        """
        for k, v in self._channel_functions.items():
            if v == self._channel_function:
                return k

    @channel_function.setter
    def channel_function(self, value):
        self._channel_function = self._channel_functions[strict_discrete_set(value, self._channel_functions)]
        self._disabled = False
        if not self.manual_flush:
            self.write("DE VS %d, '%s', %d" % (self.id, self._voltage_name, self._channel_function))
            self.check_errors()

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        self.write("DE VS %d, '%s'" % (self.id, self._voltage_name))
        self.check_errors()


class VM(Channel):
    _voltage_name = "VM"
    _disabled = False

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voltage_get_process = lambda v: mode_assert_lambda(self.parent, "USER_MODE")(
            check_errors_user_mode_value(v))

        self.voltage_get_command = f"TV {self.id + 4}"

    voltage = Channel.measurement(
        "TV {ch}",
        """
        Measures the voltage of one of the VM channels.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """,
        check_get_errors=True,
        dynamic=True
    )

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        if value != True:
            raise ValueError("Channel can only be disabled, it gets enabled implicitly with the other functions")

        self._disabled = True
        self.write("DE VM {ch}")

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to VM[1..2]. Must be unique otherwise the instrument returns a 'PROGRAM_ERROR'.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._voltage_name

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
        self.write("DE VM %d, '%s'" % (self.id, self._voltage_name))
        self.check_errors()


class SMU(Channel):
    _voltage_range = 0
    _voltage_ranges = {0: 0, 20: 1, 40: 2, 100: 3}
    _current_range = 0
    _current_ranges = {0: 0, 1e-9: 1, 10e-9: 2, 100e-9: 3, 1e-6: 4, 10e-6: 5, 100e-6: 6, 1e-3: 7, 10e-3: 8, 100e-3: 9}

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

    _disabled = False

    manual_flush = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.voltage_set_process = mode_assert_lambda(self.parent, "USER_MODE")
        self.voltage_get_process = lambda v: mode_assert_lambda(self.parent, "USER_MODE")(
            check_errors_user_mode_value(v))
        self.current_set_process = mode_assert_lambda(self.parent, "USER_MODE")
        self.current_get_process = lambda v: mode_assert_lambda(self.parent, "USER_MODE")(
            check_errors_user_mode_value(v))

        self._voltage_name = f"V{self.id}"
        self._current_name = f"I{self.id}"

        self.channel_mode_set_command = (
                "DE CH {ch}, '%s', '%s', %d, %d" %
                (self._voltage_name, self._current_name, self._channel_mode, self._channel_function))

    """
    A SMU channel of the HP4145x Instrument
    """
    voltage = Channel.control(
        "TV {ch}",
        "DV {ch}, %d, %s, %f" % (_voltage_range, "%f", _current_compliance),
        """
        Controls the output voltage of on of the SMU channels.
        Automatically puts the SMU into force voltage mode once set.
        
        .. warning::

            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
            
        .. code-block:: python

            hp4145a.SMU2.current_compliance = 10e-3
            hp4145a.SMU2.voltage = 10
            
        """,
        validator=strict_range,
        values=[0, 100 if _voltage_range == 0 else _voltage_range],
        dynamic=True,
        check_set_errors=True
    )

    current = Channel.control(
        "TI {ch}", "DI {ch}, %d, %s, %f" % (_current_range, "%f", _voltage_compliance),
        """
        Controls the output current of on of the SMU channels.
        Automatically puts the SMU into force current mode once set.

        .. warning::

            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
            
        .. code-block:: python

            hp4145a.SMU2.voltage_compliance = 10
            hp4145a.SMU2.current = 10e-3
        """,
        validator=strict_range,
        values=[0, 100 if _voltage_range == 0 else _voltage_range],
        dynamic=True,
        check_set_errors=True
    )

    @property
    def disabled(self):
        return self._disabled

    @disabled.setter
    def disabled(self, value):
        if value != True:
            raise ValueError("Channel can only be disabled, it gets enabled implicitly with the other functions")

        self._disabled = True
        self.write("DE CH {ch}")

    @property
    def voltage_range(self):
        """
        Controls the voltage range used by :attr:`voltage`. Only applicable in `USER_MODE`.

        Returns not the actual state of the instrument but the state of the object.
        """
        for k, v in self._voltage_ranges.items():
            if v == self._voltage_range:
                return k

    @voltage_range.setter
    def voltage_range(self, value):
        self._voltage_range = self._voltage_ranges[truncated_discrete_set(value, self._voltage_ranges)]
        self.voltage_set_command = "DV {ch}, %d, %s, %f" % (self._voltage_range, "%f", self._current_compliance)

    @property
    def current_range(self):
        """
        Controls the current range used by :attr:`current`. Only applicable in `USER_MODE`.

        Returns not the actual state of the instrument but the state of the object.
        """
        for k, v in self._current_ranges.items():
            if v == self._current_range:
                return k

    @current_range.setter
    def current_range(self, value):
        self._current_range = self._current_ranges[truncated_discrete_set(value, self._current_ranges)]
        self.current_set_command = "DI {ch}, %d, %s, %f" % (self._current_range, "%f", self._voltage_compliance)

    @property
    def current_compliance(self):
        """
        Controls the current compliance of the channel.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._current_compliance

    @current_compliance.setter
    def current_compliance(self, value):
        self._current_compliance = strict_range(value, [0, self._current_max])
        self.voltage_set_command = "DV {ch}, %d, %s, %f" % (self._voltage_range, "%f", self._current_compliance)

    @property
    def voltage_compliance(self):
        """
        Controls the voltage compliance of the channel.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._voltage_compliance

    @voltage_compliance.setter
    def voltage_compliance(self, value):
        self._voltage_compliance = strict_range(value, [0, self._voltage_max])
        self.current_set_command = "DI {ch}, %d, %s, %f" % (self._current_range, "%f", self._voltage_compliance)

    @property
    def voltage_name(self):
        """
        Control the voltage name for `SYSTEM_MODE`'s channel definition.

        Defaults to V[1..4]. Must be unqiue otherwise the instrument returns a 'PROGRAM_ERROR'.
        Only takes affect with a setting of :attr:`channel_mode`.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._voltage_name

    @voltage_name.setter
    def voltage_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._voltage_name = value.upper()
        self._disabled = False

        if not self.manual_flush:
            self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                      (self._voltage_name, self._current_name, self._channel_mode,
                                       self._channel_function)))
            self.check_errors()

    @property
    def current_name(self):
        """
        Control the current name for `SYSTEM_MODE`'s channel definition.

        Defaults to I[1..4]. Must be unqiue otherwise the instrument returns a 'PROGRAM_ERROR'.
        Only takes affect with a setting of :attr:`channel_mode`.

        Returns not the actual state of the instrument but the state of the object.
        """
        return self._current_name

    @current_name.setter
    def current_name(self, value):
        if len(value.strip()) > 6 or len(value.strip()) < 1:
            raise ValueError("Name must be less than six and at least one characters")

        self._current_name = value
        self._disabled = False

        if not self.manual_flush:
            self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                      (self._voltage_name, self._current_name, self._channel_mode,
                                       self._channel_function)))
            self.check_errors()

    @property
    def channel_function(self):
        """
        Control the source function, values "VAR1", "VAR2", "CONST" or "VAR1'" are allowed.

        Implicitly writes/flushes :attr:`channel_mode`, :attr:`current_name` and :attr:`voltage_name`.
        Returns not the actual state of the instrument but the state of the object.
        """
        for k, v in self._channel_functions.items():
            if v == self._channel_function:
                return k

    @channel_function.setter
    def channel_function(self, value):
        self._channel_function = self._channel_functions[strict_discrete_set(value, self._channel_functions)]

        self._disabled = False
        if not self.manual_flush:
            self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                      (self._voltage_name, self._current_name, self._channel_mode,
                                       self._channel_function)))
            self.check_errors()

    @property
    def channel_mode(self):
        """
        Set the source mode of the channel.

        Implicitly writes/flushes :attr:`channel_function`, :attr:`current_name` and :attr:`voltage_name`.

        .. code-block:: python

            hp4145a.SMU2.voltage_name = "VCE2"
            hp4145a.SMU2.current_name = "ICE2"
            hp4145a.SMU2.channel_function = "VAR2"
            hp4145a.SMU2.channel_mode = "V"
        """

        for k, v in self._channel_modes.items():
            if v == self._channel_mode:
                return k

    @channel_mode.setter
    def channel_mode(self, value):
        self._channel_mode = self._channel_modes[strict_discrete_set(value, self._channel_modes)]

        self._disabled = False
        if not self.manual_flush:
            self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                      (self._voltage_name, self._current_name, self._channel_mode,
                                       self._channel_function)))
            self.check_errors()

    def flush_channel_definition(self):
        """
        Flushes the channel definition manually in case the :attr:`manual_flush` option is set.
        """
        self.write(self.insert_id("DE CH {ch}, '%s', '%s', %d, %d" %
                                  (self._voltage_name, self._current_name, self._channel_mode, self._channel_function)))
        self.check_errors()


class HP4145x(Instrument):
    SMU1: SMU = Instrument.ChannelCreator(SMU, 1)
    SMU2: SMU = Instrument.ChannelCreator(SMU, 2)
    SMU3: SMU = Instrument.ChannelCreator(SMU, 3)
    SMU4: SMU = Instrument.ChannelCreator(SMU, 4)
    VS1: VS = Instrument.ChannelCreator(VS, 1)
    VS2: VS = Instrument.ChannelCreator(VS, 2)
    VM1: VM = Instrument.ChannelCreator(VM, 1)
    VM2: VM = Instrument.ChannelCreator(VM, 2)

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
        Flushes the channel definitions of all sub channels. Only required with :attr:`manual_flush` True.
        """
        self.SMU1.flush_channel_definition()
        self.SMU2.flush_channel_definition()
        self.SMU3.flush_channel_definition()
        self.SMU4.flush_channel_definition()
        self.VM1.flush_channel_definition()
        self.VM2.flush_channel_definition()
        self.VS1.flush_channel_definition()
        self.VS2.flush_channel_definition()

    @property
    def manual_flush(self):
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

        self._manual_flush = value

    @property
    def mode(self):
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
        stb = self.adapter.connection.read_stb()
        return stb if type(stb) is int else 0

    def reset(self):
        self.adapter.connection.clear()

    def clear(self):
        """ Clears the HP-IB buffer of the device and status bit 1 (Data Ready) """
        self.write("BC")

    def check_errors(self):
        errors = []
        error_status = [Status.EMERGENCY, Status.SYNTAX_ERROR, Status.BUSY, Status.ILLEGAL_PROGRAM]
        emergency_status = [Status.POWER_FAILURE, Status.FIXTURE_LID_OPEN, Status.SMU_SHUT_DOWN]
        while (errors[0].value & Status.EMERGENCY.value) is False if len(errors) > 0 else True:
            # mask out RQS (always set with other bits)
            status = self.status & ~Status.RQS
            if any(es & status for es in error_status):
                for es in error_status:
                    if status & es and es == Status.EMERGENCY:
                        log.error(f"HP4145x: {Status(status).value} - {Status(status).name}")
                        errors.append(Status(status))
                        break
                    else:
                        log.error(f"HP4145x: {es.value} - {es.name}")
                        errors.append(es)
            else:
                break
        return errors

    integration_time = Instrument.setting(
        "IT%d",
        """
        Set the integration time. 'SHORT' no integration at all, 'MEDIUM' 16 samples per measurement and 'LONG'
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

    data_ready_srq = Instrument.setting(
        "DR%d",
        """
        Sets the data ready enablement of the bit of the status byte.
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
        return bool((not (status & Status.SELF_TEST_FAIL)) and (status & Status.END_STATUS))

    def get_trace(self, name):
        """
        Returns the list of values for the given variable name. Name is the same as defined in the channel definition.
        """
        self.write(f"DO '%s'" % name)

        result = self.read().replace("\r", "").replace("\n", "")
        removed_status = filter(None, result.replace("N", "").replace("C", "").split(","))

        return [float(x) for x in removed_status]
