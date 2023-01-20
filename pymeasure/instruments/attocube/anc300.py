#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

import re
import time
from math import inf

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (joined_validators,
                                              strict_discrete_set,
                                              strict_range)


def strict_length(value, values):
    if len(value) != values:
        raise ValueError(
            f"Value {value} does not have an appropriate length of {values}")
    return value


def truncated_int_array(value, values):
    ret = []
    for i, v in enumerate(value):
        if values[0] <= v <= values[1]:
            if float(v).is_integer():
                ret.append(int(v))
            else:
                raise ValueError(f"Entry {v} at index {i} has no integer value")
        elif float(v).is_integer():
            ret.append(max(min(values[1], v), values[0]))
        else:
            raise ValueError(f"Entry {v} at index {i} has no integer value and"
                             f"is out of the boundaries {values}")
    return ret


truncated_int_array_strict_length = joined_validators(strict_length,
                                                      truncated_int_array)


class Axis:
    """ Represents a single open loop axis of the Attocube ANC350

    :param axis: axis identifier, integer from 1 to 7
    :param controller: ANC300Controller instance used for the communication
    """

    serial_nr = Instrument.measurement("getser",
                                       "Serial number of the axis")

    voltage = Instrument.control(
        "getv", "setv %.3f",
        """ Amplitude of the stepping voltage in volts from 0 to 150 V. This
        property can be set. """,
        validator=strict_range, values=[0, 150], check_set_errors=True)

    frequency = Instrument.control(
        "getf", "setf %.3f",
        """ Frequency of the stepping motion in Hertz from 1 to 10000 Hz.
        This property can be set. """,
        validator=strict_range, values=[1, 10000],
        cast=int, check_set_errors=True)

    mode = Instrument.control(
        "getm", "setm %s",
        """ Axis mode. This can be 'gnd', 'inp', 'cap', 'stp', 'off',
        'stp+', 'stp-'. Available modes depend on the actual axis model""",
        validator=strict_discrete_set,
        values=['gnd', 'inp', 'cap', 'stp', 'off', 'stp+', 'stp-'],
        check_set_errors=True)

    offset_voltage = Instrument.control(
        "geta", "seta %.3f",
        """ Offset voltage in Volts from 0 to 150 V.
        This property can be set. """,
        validator=strict_range, values=[0, 150], check_set_errors=True)

    pattern_up = Instrument.control(
        "getpu", "setpu %s",
        """ step up pattern of the piezo drive. 256 values ranging from 0
        to 255 representing the the sequence of output voltages within one
        step of the piezo drive. This property can be set, the set value
        needs to be an array with 256 integer values. """,
        validator=truncated_int_array_strict_length,
        values=[256, [0, 255]],
        set_process=lambda a: " ".join("%d" % v for v in a),
        separator='\r\n', cast=int, check_set_errors=True)

    pattern_down = Instrument.control(
        "getpd", "setpd %s",
        """ step down pattern of the piezo drive. 256 values ranging from 0
        to 255 representing the the sequence of output voltages within one
        step of the piezo drive. This property can be set, the set value
        needs to be an array with 256 integer values. """,
        validator=truncated_int_array_strict_length,
        values=[256, [0, 255]],
        set_process=lambda a: " ".join("%d" % v for v in a),
        separator='\r\n', cast=int, check_set_errors=True)

    output_voltage = Instrument.measurement(
        "geto",
        """ Output voltage in volts.""")

    capacity = Instrument.measurement(
        "getc",
        """ Saved capacity value in nF of the axis.""")

    stepu = Instrument.setting(
        "stepu %d",
        """ Step upwards for N steps. Mode must be 'stp' and N must be
        positive.""",
        validator=strict_range, values=[0, inf], check_set_errors=True)

    stepd = Instrument.setting(
        "stepd %d",
        """ Step downwards for N steps. Mode must be 'stp' and N must be
        positive.""",
        validator=strict_range, values=[0, inf], check_set_errors=True)

    def __init__(self, controller, axis):
        self.axis = str(axis)
        self.controller = controller

    def _add_axis_id(self, command: str):
        """ add axis id to a command string at the correct position after the
        initial command, but before a potential value

        :param command: command string
        :returns: command string with added axis id
        """
        cmdparts = command.split()
        cmdparts.insert(1, self.axis)
        return ' '.join(cmdparts)

    def ask(self, command, **kwargs):
        return self.controller.ask(self._add_axis_id(command), **kwargs)

    def write(self, command, **kwargs):
        return self.controller.write(self._add_axis_id(command), **kwargs)

    def values(self, command, **kwargs):
        return self.controller.values(self._add_axis_id(command), **kwargs)

    def stop(self):
        """ Stop any motion of the axis """
        self.write('stop')
        self.check_errors()

    def move(self, steps, gnd=True):
        """ Move 'steps' steps in the direction given by the sign of the
        argument. This method will change the mode of the axis automatically
        and ground the axis on the end if 'gnd' is True. The method returns
        only when the movement is finished.

        :param steps: finite integer value of steps to be performed. A positive
            sign corresponds to upwards steps, a negative sign to downwards
            steps.
        :param gnd: bool, flag to decide if the axis should be grounded after
            completion of the movement
        """
        self.mode = 'stp'
        # perform the movement
        if steps > 0:
            self.stepu = steps
        elif steps < 0:
            self.stepd = abs(steps)
        else:
            pass  # do not set stepu/d to 0 since it triggers a continous move
        # wait for the move to finish
        self.write('stepw')
        if gnd:
            self.mode = 'gnd'
        self.check_errors()

    def measure_capacity(self):
        """ Obtains a new measurement of the capacity. The mode of the axis
        returns to 'gnd' after the measurement.

        :returns capacity: the freshly measured capacity in nF.
        """
        self.mode = 'cap'
        # wait for the measurement to finish
        self.ask('capw')
        return self.capacity

    def check_errors(self):
        """Read after setting a setting or control."""
        self.controller.check_errors()


class ANC300Controller(Instrument):
    """ Attocube ANC300 Piezo stage controller with several axes

    :param host: host address of the instrument
    :param axisnames: a list of axis names which will be used to create
                      properties with these names
    :param passwd: password for the attocube standard console
    :param query_delay: delay between sending and reading (default 0.05 sec)
    :param kwargs: Any valid key-word argument for VISAAdapter
    """
    version = Instrument.measurement(
        "ver", """ Version number and instrument identification """
    )

    controllerBoardVersion = Instrument.measurement(
        "getcser", """ Serial number of the controller board """
    )

    _reg_value = re.compile(r"\w+\s+=\s+(\w+)")

    def check_errors(self):
        """Read after setting a value."""
        self.read()

    def ground_all(self):
        """ Grounds all axis of the controller. """
        for attr in self._axisnames:
            attribute = getattr(self, attr)
            if isinstance(attribute, Axis):
                attribute.mode = 'gnd'

    def stop_all(self):
        """ Stop all movements of the axis. """
        for attr in self._axisnames:
            attribute = getattr(self, attr)
            if isinstance(attribute, Axis):
                attribute.stop()

    def __init__(
        self,
        adapter,
        name="attocube ANC300 Piezo Controller",
        axisnames="",
        passwd="",
        query_delay=0.05,
        **kwargs,
    ):
        self.query_delay = query_delay
        self.termination_str = "\r\n"

        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            read_termination=self.termination_str,
            write_termination=self.termination_str,
            **kwargs
        )

        self._axisnames = axisnames
        for i, axis in enumerate(axisnames):
            setattr(self, axis, Axis(self, i + 1))

        time.sleep(self.query_delay)
        super().read()  # clear messages sent upon opening the connection
        # send password and check authorization
        self.write(passwd)
        time.sleep(self.query_delay)
        ret: str = super().read()
        auth_msg = ret.split(self.termination_str)[1]
        if auth_msg != 'Authorization success':
            raise Exception(f"Attocube authorization failed '{auth_msg}'")
        # switch console echo off
        self.write('echo off')
        _ = self.read()

    def extract_value(self, reply):
        """ preprocess_reply function for the Attocube console. This function
        tries to extract <value> from 'name = <value> [unit]'. If <value> can
        not be identified the original string is returned.

        :param reply: reply string
        :returns: string with only the numerical value, or the original string
        """
        r = self._reg_value.search(reply)
        if r:
            return r.groups()[0]
        else:
            return reply

    def read(self):
        """Read after setting a value."""
        raw: str = super().read()
        raw = raw.strip(self.termination_str).rsplit(sep='\n', maxsplit=1)
        if raw[-1] != 'OK':
            if raw[0] == "" or len(raw) == 1:  # clear buffer
                super().read()  # without error checking
            raise ValueError("AttocubeConsoleAdapter: Error after previous "
                             f"command with message {raw[0]}")
        return raw[0].strip('\r')  # strip possible CR char
