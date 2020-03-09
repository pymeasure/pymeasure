#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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

from pymeasure.instruments import Instrument, RangeException
from .adapters import DanfysikAdapter

from time import sleep
import numpy as np
import re


class Danfysik8500(Instrument):
    """ Represents the Danfysik 8500 Electromanget Current Supply
    and provides a high-level interface for interacting with the
    instrument

    To allow user access to the Prolific Technology PL2303 Serial port adapter
    in Linux, create the file:
    :code:`/etc/udev/rules.d/50-danfysik.rules`, with contents:

    .. code-block:: none

        SUBSYSTEMS=="usb",ATTRS{idVendor}=="067b",ATTRS{idProduct}=="2303",MODE="0666",SYMLINK+="danfysik"

    Then reload the udev rules with:

    .. code-block:: bash

        sudo udevadm control --reload-rules
        sudo udevadm trigger

    The device will be accessible through the port :code:`/dev/danfysik`.
    """

    id = Instrument.measurement(
        "PRINT", """ Reads the idenfitication information. """
    )

    def __init__(self, port):
        super(Danfysik8500, self).__init__(
            DanfysikAdapter(port),
            "Danfysik 8500 Current Supply",
            includeSCPI=False
        )
        self.write("ERRT")  # Use text error messages
        self.write("UNLOCK")  # Unlock from remote or local mode

    def local(self):
        """ Sets the instrument in local mode, where the front
        panel can be used.
        """
        self.write("LOC")

    def remote(self):
        """ Sets the instrument in remote mode, where the the
        front panel is disabled.
        """
        self.write("REM")

    @property
    def polarity(self):
        """ The polarity of the current supply, being either
        -1 or 1. This property can be set by suppling one of
        these values.
        """
        return 1 if self.ask("PO").strip() == '+' else -1

    @polarity.setter
    def polarity(self, value):
        polarity = "+" if value > 0 else "-"
        self.write("PO %s" % polarity)

    def reset_interlocks(self):
        """ Resets the instrument interlocks.
        """
        self.write("RS")

    def enable(self):
        """ Enables the flow of current.
        """
        self.write("N")

    def disable(self):
        """ Disables the flow of current.
        """
        self.write("F")

    def is_enabled(self):
        """ Returns True if the current supply is enabled.
        """
        return self.status_hex & 0x800000 == 0

    @property
    def status_hex(self):
        """ The status in hexadecimal. This value is parsed in
        :attr:`~.Danfysik8500.status` into a human-readable list.
        """
        status = self.ask("S1H")
        match = re.search(r'(?P<hex>[A-Z0-9]{6})', status)
        if match is not None:
            return int(match.groupdict()['hex'], 16)
        else:
            raise Exception("Danfysik status not properly returned. Instead "
                            "got '%s'" % status)

    @property
    def current(self):
        """ The actual current in Amps. This property can be set through
        :attr:`~.current_ppm`.
        """
        return int(self.ask("AD 8"))*1e-2*self.polarity

    @current.setter
    def current(self, amps):
        if amps > 160 or amps < -160:
            raise RangeException("Danfysik 8500 is only capable of sourcing "
                                 "+/- 160 Amps")
        self.current_ppm = int((1e6/160)*amps)

    @property
    def current_ppm(self):
        """ The current in parts per million. This property can be set.
        """
        return int(self.ask("DA 0")[2:])

    @current_ppm.setter
    def current_ppm(self, ppm):
        if abs(ppm) < 0 or abs(ppm) > 1e6:
            raise RangeException("Danfysik 8500 requires parts per million "
                                 "to be an appropriate integer")
        self.write("DA 0,%d" % ppm)

    @property
    def current_setpoint(self):
        """ The setpoint for the current, which can deviate from the actual current
        (:attr:`~.Danfysik8500.current`) while the supply is in the process of setting the value.
        """
        return self.current_ppm*(160/1e6)

    @property
    def slew_rate(self):
        """ The slew rate of the current sweep.
        """
        return float(self.ask("R3"))

    def wait_for_current(self, has_aborted=lambda: False, delay=0.01):
        """ Blocks the process until the current has stabilized. A
        provided function :code:`has_aborted` can be supplied, which
        is checked after each delay time (in seconds) in addition to the
        stability check. This allows an abort feature to be integrated.

        :param has_aborted: A function that returns True if the process should stop waiting
        :param delay: The delay time in seconds between each check for stability
        """
        self.wait_for_ready(has_aborted, delay)
        while not has_aborted() and not self.is_current_stable():
            sleep(delay)

    def is_current_stable(self):
        """ Returns True if the current is within 0.02 A of the
        setpoint value.
        """
        return abs(self.current - self.current_setpoint) <= 0.02

    def is_ready(self):
        """ Returns True if the instrument is in the ready state.
        """
        return self.status_hex & 0b10 == 0

    def wait_for_ready(self, has_aborted=lambda: False, delay=0.01):
        """ Blocks the process until the instrument is ready. A
        provided function :code:`has_aborted` can be supplied, which
        is checked after each delay time (in seconds) in addition to the
        readiness check. This allows an abort feature to be integrated.

        :param has_aborted: A function that returns True if the process should stop waiting
        :param delay: The delay time in seconds between each check for readiness
        """
        while not has_aborted() and not self.is_ready():
            sleep(delay)

    @property
    def status(self):
        """ A list of human-readable strings that contain
        the instrument status information, based on :attr:`~.status_hex`.
        """
        status = []
        indicator = self.ask("S1")
        if indicator[0] == "!":
            status.append("Main Power OFF")
        else:
            status.append("Main Power ON")
        # Skipping 5, 6 and 7 (from Appendix Manual on command S1)
        messages = {
            1: "Polarity Normal",
            2: "Polarity Reversed",
            3: "Regulation Transformer is not equal to zero",
            7: "Spare Interlock",
            8: "One Transistor Fault",
            9: "Sum - Interlock",
            10: "DC Overcurrent (OCP)",
            11: "DC Overload",
            12: "Regulation Module Failure",
            13: "Preregulator Failure",
            14: "Phase Failure",
            15: "MPS Waterflow Failure",
            16: "Earth Leakage Failure",
            17: "Thermal Breaker/Fuses",
            18: "MPS Overtemperature",
            19: "Panic Button/Door Switch",
            20: "Magnet Waterflow Failure",
            21: "Magnet Overtemperature",
            22: "MPS Not Ready"
        }
        for index, message in messages.items():
            if indicator[index] == "!":
                status.append(message)
        return status

    def clear_ramp_set(self):
        """ Clears the ramp set.
        """
        self.write("RAMPSET C")

    def set_ramp_delay(self, time):
        """ Sets the ramp delay time in seconds.

        :param time: The time delay time in seconds
        """
        self.write("RAMPSET %f" % time)

    def start_ramp(self):
        """ Starts the current ramp.
        """
        self.write("RAMP R")

    def add_ramp_step(self, current):
        """ Adds a current step to the ramp set.

        :param current: A current in Amps
        """
        self.write("R %.6f" % (current/160.))

    def stop_ramp(self):
        """ Stops the current ramp.
        """
        self.ask("RAMP S")

    def set_ramp_to_current(self, current, points, delay_time=1):
        """ Sets up a linear ramp from the initial current to a different
        current, with a number of points, and delay time.

        :param current: The final current in Amps
        :param points: The number of linear points to traverse
        :param delay_time: A delay time in seconds 
        """
        initial_current = self.current
        self.clear_ramp_set()
        self.set_ramp_delay(delay_time)
        steps = np.linspace(initial_current, current, num=points)
        cmds = ["R %.6f" % (step/160.) for step in steps]
        self.write("\r".join(cmds))

    def ramp_to_current(self, current, points, delay_time=1):
        """ Executes :meth:`~.set_ramp_to_current` and starts the ramp.
        """
        self.set_ramp_to_current(current, points, delay_time)
        self.start_ramp()

    # self.setSequence(0, [0, 10], [0.01])
    def set_sequence(self, stack, currents, times, multiplier=999999):
        """ Sets up an arbitrary ramp profile with a list of currents (Amps)
        and a list of interval times (seconds) on the specified stack number
        (0-15)
        """
        self.clear_sequence(stack)
        if min(times) >= 1 and max(times) <= 65535:
            self.write("SLOW %i" % stack)
        elif min(times) >= 0.1 and max(times) <= 6553.5:
            self.write("FAST %i" % stack)
            times = [0.1*x for x in times]
        else:
            raise RangeException("Timing for Danfysik 8500 ramp sequence is"
                                 " out of range")
        for i in range(len(times)):
            self.write("WSA %i,%i,%i,%i" % (
                stack,
                int(6250*abs(currents[i])),
                int(6250*abs(currents[i+1])), times[i])
            )
        self.write("MULT %i,%i" % (stack, multiplier))

    def clear_sequence(self, stack):
        """ Clears the sequence by the stack number.
        
        :param stack: A stack number between 0-15 
        """
        self.write("CSS %i" % stack)

    def sync_sequence(self, stack, delay=0):
        """ Arms the ramp sequence to be triggered by a hardware
        input to pin P33 1&2 (10 to 24 V) or a TS command. If a
        delay is provided, the sequence will start after the delay.

        :param stack: A stack number between 0-15
        :param delay: A delay time in seconds
        """
        self.write("SYNC %i, %i" % (stack, delay))

    def start_sequence(self, stack):
        """ Starts a sequence by the stack number.

        :param stack: A stack number between 0-15 
        """
        self.write("TS %i" % stack)

    def stop_sequence(self):
        """ Stops the currently running sequence.
        """
        self.write("STOP")

    def is_sequence_running(self, stack):
        """ Returns True if a sequence is running with a given stack number

        :param stack: A stack number between 0-15 
        """
        return re.search("R%i," % stack, self.ask("S2")) is not None
