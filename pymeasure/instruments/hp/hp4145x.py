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


def mode_assert_lambda(v, parent, expected_mode):
    assert parent.mode == expected_mode
    return v


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


class VS(Channel):
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
        # set_process=lambda v: mode_assert_lambda(v, super(), "USER_MODE")
    )


class VM(Channel):

    def insert_id(self, command):
        normal_id = self.id
        self.id += 4
        super().insert_id(command)
        self.id = normal_id

    voltage = Channel.measurement(
        "TV {ch}",
        """
        Measures the voltage of one of the VM channels.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """,
        # get_process=lambda v: mode_assert_lambda(v, super(), "USER_MODE")
        get_process=check_errors_user_mode_value
    )


class SMU(Channel):
    _voltage_range = 0
    _voltage_ranges = {0: 0, 20: 1, 40: 2, 100: 3}
    _current_range = 0
    _current_ranges = {0: 0, 1e-9: 1, 10e-9: 2, 100e-9: 3, 1e-6: 4, 10e-6: 5, 100e-6: 6, 1e-3: 7, 10e-3: 8, 100e-3: 9}

    _current_max = 100e-3
    _current_compliance = 0.0

    _voltage_max = 100
    _voltage_compliance = 0.0

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
        """,
        validator=strict_range,
        values=[0, 100 if _voltage_range == 0 else _voltage_range],
        dynamic=True,
        # set_process=lambda v: modeAssertLambda(v, super(HP4145x), "USER_MODE"),
        # get_process=lambda v: modeAssertLambda(v, super(HP4145x), "USER_MODE")
        get_process=check_errors_user_mode_value
    )

    current = Channel.control(
        "TI {ch}", "DI {ch}, %d, %s, %f" % (_current_range, "%f", _voltage_compliance),
        """
        Controls the output current of on of the SMU channels.
        Automatically puts the SMU into force current mode once set.

        .. warning::
            Only works with mode == 'USER_MODE' of instrument. In 'SYSTEM_MODE' no
            direct access is allowed.
        """,
        validator=strict_range,
        values=[0, 100 if _voltage_range == 0 else _voltage_range],
        dynamic=True,
        # set_process=lambda v: modeAssertLambda(v, super(HP4145x), "USER_MODE"),
        # get_process=lambda v: modeAssertLambda(v, super(HP4145x), "USER_MODE")
        get_process=check_errors_user_mode_value
    )

    @property
    def voltage_range(self):
        for k, v in self._voltage_ranges.items():
            if v == self._voltage_range:
                return k

    @voltage_range.setter
    def voltage_range(self, value):
        self._voltage_range = self._voltage_ranges[truncated_discrete_set(value, self._voltage_ranges)]
        self.voltage_set_command = "DV {ch}, %d, %s, %f" % (self._voltage_range, "%f", self._current_compliance)

    @property
    def current_range(self):
        for k, v in self._current_ranges.items():
            if v == self._current_range:
                return k

    @current_range.setter
    def current_range(self, value):
        self._current_range = self._current_ranges[truncated_discrete_set(value, self._current_ranges)]
        self.current_set_command = "DI {ch}, %d, %s, %f" % (self._current_range, "%f", self._voltage_compliance)

    @property
    def current_compliance(self):
        return self._current_compliance

    @current_compliance.setter
    def current_compliance(self, value):
        self._current_compliance = strict_range(value, [0, self._current_max])
        self.voltage_set_command = "DV {ch}, %d, %s, %f" % (self._voltage_range, "%f", self._current_compliance)

    @property
    def voltage_compliance(self):
        return self._voltage_compliance

    @voltage_compliance.setter
    def voltage_compliance(self, value):
        self._voltage_compliance = strict_range(value, [0, self._voltage_max])
        self.current_set_command = "DI {ch}, %d, %s, %f" % (self._current_range, "%f", self._voltage_compliance)


class HP4145x(Instrument):
    SMU1: SMU = Instrument.ChannelCreator(SMU, 1)
    SMU2: SMU = Instrument.ChannelCreator(SMU, 2)
    SMU3: SMU = Instrument.ChannelCreator(SMU, 3)
    SMU4: SMU = Instrument.ChannelCreator(SMU, 4)
    VS1: VS = Instrument.ChannelCreator(VS, 1)
    VS2: VS = Instrument.ChannelCreator(VS, 2)
    VM1: VM = Instrument.ChannelCreator(VM, 1)
    VM2: VM = Instrument.ChannelCreator(VM, 1)

    _mode = "SYSTEM_MODE"

    def __init__(self, adapter, name="Hewlett-Packard HP4145x", **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            send_end=True,
            **kwargs,
        )

        self.mode = self._mode

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
