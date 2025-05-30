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
import re
from math import inf, isfinite, isinf
from warnings import warn

from pymeasure.adapters import Adapter
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (joined_validators,
                                              strict_discrete_set,
                                              strict_range)


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def deprecated_strict_range(value, values):
    warn("This property is deprecated, use meth:`move_raw` instead.",
         FutureWarning)
    return strict_range(value, values)


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


class Axis(Channel):
    """ Represents a single open loop axis of the Attocube ANC350

    :param axis: axis identifier, integer from 1 to 7
    :param controller: ANC300Controller instance used for the communication
    """

    serial_nr = Instrument.measurement("getser",
                                       "Get the serial number of the axis.")

    voltage = Instrument.control(
        "getv", "setv %.3f",
        """Control the amplitude of the stepping voltage in volts from 0 to 150 V.""",
        validator=strict_range, values=[0, 150], check_set_errors=True)

    frequency = Instrument.control(
        "getf", "setf %.3f",
        """Control the frequency of the stepping motion in Hertz from 1 to 10000 Hz.""",
        validator=strict_range, values=[1, 10000],
        cast=int, check_set_errors=True)

    mode = Instrument.control(
        "getm", "setm %s",
        """Control axis mode. This can be 'gnd', 'inp', 'cap', 'stp', 'off',
        'stp+', 'stp-'. Available modes depend on the actual axis model.""",
        validator=strict_discrete_set,
        values=['gnd', 'inp', 'cap', 'stp', 'off', 'stp+', 'stp-'],
        check_set_errors=True)

    offset_voltage = Instrument.control(
        "geta", "seta %.3f",
        """Control offset voltage in Volts from 0 to 150 V.""",
        validator=strict_range, values=[0, 150], check_set_errors=True)

    pattern_up = Instrument.control(
        "getpu", "setpu %s",
        """Control step up pattern of the piezo drive. 256 values ranging from 0
        to 255 representing the sequence of output voltages within one
        step of the piezo drive. This property can be set, the set value
        needs to be an array with 256 integer values. """,
        validator=truncated_int_array_strict_length,
        values=[256, [0, 255]],
        set_process=lambda a: " ".join("%d" % v for v in a),
        separator='\r\n', cast=int, check_set_errors=True)

    pattern_down = Instrument.control(
        "getpd", "setpd %s",
        """Control step down pattern of the piezo drive. 256 values ranging from 0
        to 255 representing the sequence of output voltages within one
        step of the piezo drive. This property can be set, the set value
        needs to be an array with 256 integer values. """,
        validator=truncated_int_array_strict_length,
        values=[256, [0, 255]],
        set_process=lambda a: " ".join("%d" % v for v in a),
        separator='\r\n', cast=int, check_set_errors=True)

    output_voltage = Instrument.measurement(
        "geto",
        """Measure the output voltage in volts.""")

    capacity = Instrument.measurement(
        "getc",
        """Measure the saved capacity value in nF of the axis.""")

    stepu = Instrument.setting(
        "stepu %d",
        """Set the steps upwards for N steps. Mode must be 'stp' and N must be
        positive. 0 causes a continuous movement until stop is called.

        .. deprecated:: 0.13.0 Use meth:`move_raw` instead.
        """,
        validator=deprecated_strict_range,
        values=[0, inf],
        check_set_errors=True,
    )

    stepd = Instrument.setting(
        "stepd %d",
        """Set the steps downwards for N steps. Mode must be 'stp' and N must be
        positive. 0 causes a continuous movement until stop is called.

        .. deprecated:: 0.13.0 Use meth:`move_raw` instead.
        """,
        validator=deprecated_strict_range,
        values=[0, inf],
        check_set_errors=True,
    )

    def insert_id(self, command):
        """Insert the channel id in a command replacing `placeholder`.

        Add axis id to a command string at the correct position after the
        initial command, but before a potential value.
        """
        cmdparts = command.split()
        cmdparts.insert(1, self.id)
        return ' '.join(cmdparts)

    def stop(self):
        """ Stop any motion of the axis """
        self.write('stop')
        self.check_set_errors()

    def move_raw(self, steps):
        """Move 'steps' steps in the direction given by the sign of the
        argument. This method assumes the mode of the axis is set to 'stp' and
        it is non-blocking, i.e. it will return immediately after sending the
        command.

        :param steps: integer value of steps to be performed. A positive
            sign corresponds to upwards steps, a negative sign to downwards
            steps. The values of +/-inf trigger a continuous movement. The axis
            can be halted by the stop method.
        """
        if isfinite(steps) and abs(steps) > 0:
            if steps > 0:
                self.write(f"stepu {steps:d}")
            else:
                self.write(f"stepd {abs(steps):d}")
        elif isinf(steps):
            if steps > 0:
                self.write("stepu c")
            else:
                self.write("stepd c")
        else:  # ignore zero and nan values
            return
        self.check_set_errors()

    def move(self, steps, gnd=True):
        """Move 'steps' steps in the direction given by the sign of the
        argument. This method will change the mode of the axis automatically
        and ground the axis on the end if 'gnd' is True. The method is blocking
        and returns only when the movement is finished.

        :param steps: finite integer value of steps to be performed. A positive
            sign corresponds to upwards steps, a negative sign to downwards
            steps.
        :param gnd: bool, flag to decide if the axis should be grounded after
            completion of the movement
        """
        if not isfinite(steps):
            raise ValueError("Only finite number of steps are allowed.")
        self.mode = 'stp'
        # perform the movement
        self.move_raw(steps)
        # wait for the move to finish
        self.wait_for(abs(steps) / self.frequency)
        # ask if movement finished
        self.ask('stepw')
        if gnd:
            self.mode = 'gnd'

    def measure_capacity(self):
        """ Obtains a new measurement of the capacity. The mode of the axis
        returns to 'gnd' after the measurement.

        :returns capacity: the freshly measured capacity in nF.
        """
        self.mode = 'cap'
        # wait for the measurement to finish
        self.wait_for(1)
        # ask if really finished
        self.ask('capw')
        return self.capacity


class ANC300Controller(Instrument):
    """ Attocube ANC300 Piezo stage controller with several axes

    :param adapter: The VISA resource name of the controller
        (e.g. "TCPIP::<address>::<port>::SOCKET") or a created Adapter.
        The instruments default communication port is 7230.
    :param axisnames: a list of axis names which will be used to create
        properties with these names
    :param passwd: password for the attocube standard console
    :param query_delay: default delay between sending and reading in s (default 0.05)
    :param host: host address of the instrument (e.g. 169.254.0.1)

        .. deprecated:: 0.11.2
            The 'host' argument is deprecated. Use 'adapter' argument instead.

    :param kwargs: Any valid key-word argument for VISAAdapter
    """
    version = Instrument.measurement(
        "ver", """ Get the version number and instrument identification. """
    )

    controllerBoardVersion = Instrument.measurement(
        "getcser", """ Get the serial number of the controller board. """
    )

    _reg_value = re.compile(r"\w+\s+=\s+([\w\.]+)")

    def __init__(
        self,
        adapter=None,
        name="attocube ANC300 Piezo Controller",
        axisnames="",
        passwd="",
        query_delay=0.05,
        **kwargs,
    ):
        adapter = self.handle_deprecated_host_arg(adapter, kwargs)

        if not isinstance(name, str):
            warn(
                f"ANC300Controller.__init__: `name` was provided was {type(name)} but should be a "
                + "string. This is likely because `name` was added as a keyword argument. "
                + "All positional arguments after `adapter` should be provided as keyword argument"
                + " (i.e. `axisnames=['x', 'y']`).",
                FutureWarning
            )

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
            setattr(self, axis, self.add_child(Axis, id=str(i + 1)))

        self.wait_for()
        # clear messages sent upon opening the connection,
        # this contains some non-ascii characters!
        self.adapter.flush_read_buffer()
        # send password and check authorization
        self.write(passwd)
        self.wait_for()
        super().read()  # ignore echo of password
        auth_msg = super().read()
        if auth_msg != 'Authorization success':
            raise Exception(f"Attocube authorization failed '{auth_msg}'")
        # switch console echo off
        self.ask('echo off')

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        :return: List of error entries.
        """
        try:
            self.read()
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

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

    def handle_deprecated_host_arg(self, adapter, kwargs):
        """
        This function formats user input to the __init__ function to be compatible with the
        current definition of the __init__ function. This is used to support outdated (deprecated)
        code. and separated out to make it easier to remove in the future. To whoever removes this:
        This function should be removed and the `adapter` argument in the __init__ method should
        be made non-optional.

        :param dict kwargs: keyword arguments passed to the __init__ function,
            including the deprecated `host` argument.
        :return str: resource string for the VISAAdapter
        """
        host = kwargs.pop("host", None)
        if not (host or adapter):
            raise TypeError("ANC300Controller: missing 'adapter' argument")

        if not adapter:
            # because the host argument is deprecated, prompt for the desired
            # argument which is the adapter argument.
            warn("The 'host' argument is deprecated. Use 'adapter' instead.", FutureWarning)
            adapter = host

        if isinstance(adapter, str):
            if adapter.find("::") > -1:
                # adapter is a resource string, so use it
                return adapter
            # otherwise, `adapter` can only be a (deprecated) hostname, so display a
            # deprecation warning and create the resource string
            warn(
                "Using a hostname is deprecated. Use a full VISA resource string instead.",
                FutureWarning,
            )
            return f"TCPIP::{adapter}::7230::SOCKET"
        elif isinstance(adapter, Adapter):
            return adapter
        raise TypeError("ANC300Controller: 'adapter' argument must be a string or Adapter")

    def _extract_value(self, reply):
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
        lines = []
        while True:
            lines.append(super().read())
            if lines[-1] in ["OK", "ERROR"]:
                break
        msg = self.termination_str.join(lines[:-1])
        if lines[-1] != 'OK':
            self.adapter.flush_read_buffer()
            raise ValueError("ANC300Controller: Error after previous "
                             f"command with message {msg}")
        return self._extract_value(msg)

    def wait_for(self, query_delay=None):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds.
            None means :attr:`query_delay`.
        """
        super().wait_for(self.query_delay if query_delay is None else query_delay)
