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

from pymeasure.instruments import Instrument, Channel, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class KeysightE364XAChannel(Channel):
    """ Class representing a single channel of Keysights E364xA series dual output models.

    The Channel supports `HIGH` and a `LOW` output range that can be changed during operation.
    However switching to different range while the output is set to parameters that the newly
    selected range does not support will automatically alter those to match the maximum
    allowed values of the new range setting.
    """
    voltage_setpoint = Channel.control(
        "INST:NSEL {ch};:VOLT?",
        "INST:NSEL {ch};:VOLT %g",
        """Control output voltage setpoint. Range depends on selected LOW or HIGH mode.""",
        validator=strict_range,
        dynamic=True,
    )

    current_limit = Channel.control(
        "INST:NSEL {ch};:CURR?",
        "INST:NSEL {ch};:CURR %g",
        """Control current limit of this channel. Range depends on selected LOW or HIGH mode.""",
        validator=strict_range,
        dynamic=True,
    )

    voltage = Channel.measurement(
        "INST:NSEL {ch};:MEAS:VOLT?",
        """Measure voltage at the channel output.""",
    )

    current = Channel.measurement(
        "INST:NSEL {ch};:MEAS:CURR?",
        """Measure current at the channel output.""",
    )

    range = Channel.control(
        "INST:NSEL {ch};:VOLT:RANG?",
        "INST:NSEL {ch};:VOLT:RANG %s",
        """Set channel in LOW or HIGH output voltage range.""",
        validator=strict_discrete_set,
        map_values=True,
        dynamic=True,
        cast=str,
    )

    def update_validator_range(self, value):
        """Update the validator ranges after switching the output range.

        When the output range is switched, the maximum values of `voltage_setpoint`
        and `current_limit` have to be adjusted. So we use this callback to update
        the dynamic `values` fields of `voltage_setpoint` resp. `current_limit`.
        """
        self.voltage_setpoint_values = [0, self.parent._max_voltage[value]]
        self.current_limit_values = [0, self.parent._max_current[value]]
        return value


class KeysightE364XASingleOutput(SCPIMixin, Instrument):
    """ Base class representing the single output channel PSUs of the Keysight E364xA series.

    The single output channel models are E3640A, E3641A, E3642A, E3643A, E3644A and E3645A
    which are represented in their respective classes (:class:`~.KeysightE3640A`,
    :class:`~.KeysightE3641A`, :class:`~.KeysightE3642A`, :class:`~.KeysightE3643A`,
    :class:`~.KeysightE3644A`, :class:`~.KeysightE3645A`), that vary in their output voltage
    and current limit ranges.
    The device has two output ranges: A `HIGH` and a `LOW` output range that can be changed
    during operation. However switching to different range while the output is set to parameters
    that the newly selected range does not support will automatically alter those to match the
    maximum allowed values of the new range setting.

    :param voltage_range: select the initial output range (default="LOW") during initialization.
    :type voltage_range: str ("LOW") or str ("HIGH")
    """

    _default_name = "KeysightE364XASingleOutput"

    def __init__(self, adapter, name=None, voltage_range="LOW", **kwargs):
        super().__init__(
            adapter,
            name if name is not None else self._default_name,
            **kwargs,
        )
        """Dynamically set 'update_validator_range' as a set process for the range command.

        This callback will update the 'voltage_setpoint_values' and 'current_limit_values' each time
        the range property is modified. The setpoint/limit values are class attributes of the
        specific model of the device series.
        During instantiation the range attribute is set to reflect the 'voltage_range' passed to the
        constructor. This will initially setup said validator ranges and put the device in the
        desired output range.
        """

        self.range_set_process = self.update_validator_range
        self.range_values = self._range_map
        self.range = voltage_range

    voltage_setpoint = Instrument.control(
        "VOLT?",
        "VOLT %g",
        """Control output voltage setpoint. Range depends on selected LOW or HIGH mode.""",
        validator=strict_range,
        dynamic=True,
    )

    current_limit = Instrument.control(
        "CURR?",
        "CURR %g",
        """Control current limit of device. Range depends on selected LOW or HIGH mode.""",
        validator=strict_range,
        dynamic=True,
    )

    voltage = Instrument.measurement(
        "MEAS:VOLT?",
        """Measure voltage at the device output.""",
    )

    current = Instrument.measurement(
        "MEAS:CURR?",
        """Measure current at the device output.""",
    )

    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """Control outputs of the device (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        dynamic=True,
    )

    range = Instrument.control(
        "VOLT:RANG?",
        "VOLT:RANG %s",
        """Set device in LOW or HIGH output voltage range.""",
        validator=strict_discrete_set,
        map_values=True,
        dynamic=True,
        cast=str,
    )

    def update_validator_range(self, value):
        """Update the validator ranges after switching the output range.

        When the output range is switched, the maximum values of `voltage_setpoint`
        and `current_limit` have to be adjusted. So we use this callback to update
        the dynamic `values` fields of `voltage_setpoint` resp. `current_limit`.
        """
        self.voltage_setpoint_values = [0, self._max_voltage[value]]
        self.current_limit_values = [0, self._max_current[value]]
        return value


class KeysightE364XADualOutput(SCPIMixin, Instrument):
    """ Base class representing the dual output channel PSUs of the Keysight E364xA series.

    The dual output channel models are E3646A, E3647A, E3648A and E3649A represented by
    their respective classes (:class:`~.KeysightE3646A`, :class:`~.KeysightE3647A`,
    :class:`~.KeysightE3648A`, :class:`~.KeysightE3649A`), that vary in their output
    voltage and current limit ranges.
    The device has two output channels of :class:`~.KeysightE364XAChannel` named
    `ch_1` and `ch_2` that each support two output voltage ranges:
    A `HIGH` and a `LOW` output range that can be changed during operation. However
    switching to different range while the output is set to parameters that the newly
    selected range does not support will automatically alter those to match the maximum
    allowed values of the new range setting.

    :param voltage_range: select the initial output range (default=("LOW", "LOW")) during
        initialization.
    :type voltage_range: tuple(str, str) with any combination of "LOW" or "HIGH"
    """
    _default_name = "KeysightE364XADualOutput"
    ch_1 = Instrument.ChannelCreator(KeysightE364XAChannel, 1)
    ch_2 = Instrument.ChannelCreator(KeysightE364XAChannel, 2)

    def __init__(self, adapter, name=None, voltage_range=("LOW", "LOW"), **kwargs):
        super().__init__(
            adapter,
            name if name is not None else self._default_name,
            **kwargs,
        )
        """ Dynamically set 'update_validator_range' as a set process for the range command.

        This callback will update the 'voltage_setpoint_values' and 'current_limit_values' each time
        the range property is modified. The setpoint/limit values are class attributes of the
        specific model of the device series.
        During instantiation the range attribute is set to reflect the 'voltage_range' passed to the
        constructor. This will initially setup said validator ranges and put the channels in the
        desired output ranges.
        """
        self.ch_1.range_set_process = self.ch_1.update_validator_range
        self.ch_2.range_set_process = self.ch_2.update_validator_range
        self.ch_1.range_values = self._range_map
        self.ch_2.range_values = self._range_map
        self.ch_1.range = voltage_range[0]
        self.ch_2.range = voltage_range[1]

    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """Control outputs of the device (boolean).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        dynamic=True,
    )

    tracking_enabled = Instrument.control(
        ":OUTP:TRAC?",
        ":OUTP:TRAC %d",
        """Control whether the power supply operates in the track mode (boolean)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )


class KeysightE3640A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3640A 30W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3640A"
    _max_voltage = {"LOW": 8.0, "HIGH": 20.0}
    _max_current = {"LOW": 3.0, "HIGH": 1.5}
    _range_map = {"LOW": "P8V", "HIGH": "P20V"}


class KeysightE3641A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3641A 30W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3641A"
    _max_voltage = {"LOW": 35.0, "HIGH": 60.0}
    _max_current = {"LOW": 0.8, "HIGH": 0.5}
    _range_map = {"LOW": "P35V", "HIGH": "P60V"}


class KeysightE3642A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3642A 50W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3642A"
    _max_voltage = {"LOW": 8.0, "HIGH": 20.0}
    _max_current = {"LOW": 5.0, "HIGH": 2.5}
    _range_map = {"LOW": "P8V", "HIGH": "P20V"}


class KeysightE3643A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3643A 50W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3643A"
    _max_voltage = {"LOW": 35.0, "HIGH": 60.0}
    _max_current = {"LOW": 1.4, "HIGH": 0.8}
    _range_map = {"LOW": "P35V", "HIGH": "P60V"}


class KeysightE3644A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3644A 80W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3644A"
    _max_voltage = {"LOW": 8.0, "HIGH": 20.0}
    _max_current = {"LOW": 8.0, "HIGH": 4.0}
    _range_map = {"LOW": "P8V", "HIGH": "P20V"}


class KeysightE3645A(KeysightE364XASingleOutput):
    """ Class representing the single output Keysight E3645A 80W power supply.

    For documentation refer to the :class:`~.KeysightE364XASingleOutput` base class.
    """
    _default_name = "KeysightE3645A"
    _max_voltage = {"LOW": 35.0, "HIGH": 60.0}
    _max_current = {"LOW": 2.2, "HIGH": 1.3}
    _range_map = {"LOW": "P35V", "HIGH": "P60V"}


class KeysightE3646A(KeysightE364XADualOutput):
    """ Class representing the dual output Keysight E3646A 60W power supply.

    For documentation refer to the :class:`~.KeysightE364XADualOutput` base class.
    """
    _default_name = "KeysightE3646A"
    _max_voltage = {"LOW": 8.0, "HIGH": 20.0}
    _max_current = {"LOW": 3.0, "HIGH": 1.5}
    _range_map = {"LOW": "P8V", "HIGH": "P20V"}


class KeysightE3647A(KeysightE364XADualOutput):
    """ Class representing the dual output Keysight E3647A 60W power supply.

    For documentation refer to the :class:`~.KeysightE364XADualOutput` base class.
    """
    _default_name = "KeysightE3647A"
    _max_voltage = {"LOW": 35.0, "HIGH": 60.0}
    _max_current = {"LOW": 0.8, "HIGH": 0.5}
    _range_map = {"LOW": "P35V", "HIGH": "P60V"}


class KeysightE3648A(KeysightE364XADualOutput):
    """ Class representing the dual output Keysight E3648A 100W power supply.

    For documentation refer to the :class:`~.KeysightE364XADualOutput` base class.
    """
    _default_name = "KeysightE3648A"
    _max_voltage = {"LOW": 8.0, "HIGH": 20.0}
    _max_current = {"LOW": 5.0, "HIGH": 2.5}
    _range_map = {"LOW": "P8V", "HIGH": "P20V"}


class KeysightE3649A(KeysightE364XADualOutput):
    """ Class representing the dual output Keysight E3649A 100W power supply.

    For documentation refer to the :class:`~.KeysightE364XADualOutput` base class.
    """
    _default_name = "KeysightE3649A"
    _max_voltage = {"LOW": 35.0, "HIGH": 60.0}
    _max_current = {"LOW": 1.4, "HIGH": 0.8}
    _range_map = {"LOW": "P35V", "HIGH": "P60V"}
