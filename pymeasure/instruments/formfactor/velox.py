#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

VELOCITY_RANGE = [0.1, 100]
PROBER_UNITS = {"microns": "Y",
                "mils": "I",
                "jogs": "J",
                "encoder": "E",
                "index": "X",
                }
PROBER_REFERENCES = {"home": "H",
                     "zero": "Z",
                     "relative": "R",
                     "center": "C",
                     "diehome": "D",
                     }
EXPECTED_ERRORS = [703]  # list of errors that do not raise a ConnectionError


class Chuck(Channel):
    """A class representing the Chuck functions of the wafer prober."""

    def move_contact(self, velocity=100):
        """Move the chuck to the contact height.

        :param  float velocity: Speed in percent, strictly from ``0.1`` to ``100``.

        """
        strict_range(velocity, VELOCITY_RANGE)
        return self.ask(f"MoveChuckContact {velocity}")

    def move_align(self, velocity=100):
        """Move the chuck to the align height.

        :param  float velocity: Speed in percent, strictly from ``0.1`` to ``100``.

        """
        strict_range(velocity, VELOCITY_RANGE)
        return self.ask(f"MoveChuckAlign {velocity}")

    def move_separation(self, velocity=100):
        """Move the chuck to the separation height.

        :param  float velocity: Speed in percent, strictly from ``0.1`` to ``100``.

        """
        strict_range(velocity, VELOCITY_RANGE)
        return self.ask(f"MoveChuckSeparation {velocity}")

    def move_index(self, x_steps, y_steps, pos_ref="home", velocity=100):
        """Move the chuck in index steps.

        :param  int x_steps: Index steps in X direction
        :param  int y_steps: Index steps in Y direction
        :param  str pos_ref: Position reference, strictly ``home``,
            ``zero``, ``center`` or ``diehome``.
        :param  float velocity: Speed in percent, strictly from ``0.1`` to ``100``.

        """
        pos_ref = pos_ref.lower()
        strict_discrete_set(pos_ref, PROBER_REFERENCES.keys())
        strict_range(velocity, VELOCITY_RANGE)
        _ref = PROBER_REFERENCES[pos_ref]
        return self.ask(f"MoveChuckIndex {x_steps} {y_steps} {_ref} {velocity}")

    def move(self, x, y, pos_ref="home", unit="microns", velocity=100):
        """Move the chuck by the specified distance.

        :param  float x: Distance in X direction
        :param  float y: Distance in Y direction
        :param  str pos_ref: Position reference, strictly ``home``,
            ``zero``, ``center`` or ``diehome``.
        :param  str unit: Unit of **x** and **y**, strictly ``micron``,
            ``mils``, ``jogs``, ``encoder`` or ``index``.
        :param  float velocity: Speed in percent, strictly from ``0.1`` to ``100``.

        """
        pos_ref = pos_ref.lower()
        strict_discrete_set(pos_ref, PROBER_REFERENCES.keys())
        _ref = PROBER_REFERENCES[pos_ref]

        unit = unit.lower()
        strict_discrete_set(unit, PROBER_UNITS.keys())
        _unit = PROBER_UNITS[unit]

        strict_range(velocity, VELOCITY_RANGE)
        return self.ask(f"MoveChuck {x} {y} {_ref} {_unit} {velocity}")

    index = Channel.control(
        "ReadChuckIndex Y",
        "SetChuckIndex %f %f Y",
        """Control the chuck index (x, y) in micrometer (float, float).""",
        separator=" ",
        check_set_errors=True,
        )


class WaferMap(Channel):
    """A class representing the functions of the Wafermap module."""

    def step_first_die(self):
        """Move the chuck to the first die and clear the the binning results.

        :return: List of the int containing the coordinates of the first die.

                    - item[0]: X coordinate
                    - item[1]: Y coordinate
                    - item[2]: Current subdie index
                    - item[3]: Total number of subdies in the die

        """
        return self.values("StepFirstDie",
                           separator=" ",
                           cast=int,
                           )

    def step_next_die(self):
        """Move the chuck to the next logical die.

        :return: List of the int containing the coordinates of the new die.

            - item[0]: X coordinate
            - item[1]: Y coordinate
            - item[2]: Current subdie index
            - item[3]: Total number of subdies in the die

        """
        return self.values("StepNextDie",
                           separator=" ",
                           cast=int,
                           )

    def step_to_die(self, x_pos, y_pos, s_pos=None):
        """Move the chuck to the specified die coordinates.

        :param int x_pos: X coordinate.
        :param int y_pos: Y coordinate.
        :param int s_pos: subdie index.

        """

        coordinates = [x_pos, y_pos]
        if s_pos:
            coordinates.append(s_pos)

        _coord = " ".join(map(str, coordinates))
        self.ask(f"StepNextDie {_coord}")

    enabled = Channel.measurement(
        "IsAppRegistered WaferMap",
        """Get whether the WaferMap module is loaded or not.""",
        map_values=True,
        values={True: 1, False: 0}
        )


class Velox(SCPIMixin, Instrument):
    """A class representing the FormFactor Velox wafer prober.

    Example for a measurement of an entire wafer:

    .. code-block:: python

        from pymeasure.instruments.formfactor.velox import Velox

        prober = Velox("GPIB0::28::INSTR")  # replace the resource to your needs
        coordinates = prober.wafermap.step_first_die()  # move to the first die in the wafermap
        while not prober.error_code:
            prober.chuck.move_contact()  # move to contact height
            # ...
            # code for measurement, processing and storing data
            # ...
            prober.chuck.move_separation()  # move to separation height
            coordinates = prober.wafermap.step_next_die()  # move to the next die in the wafermap

    """

    error_code = 0
    error_message = ""

    chuck = Instrument.ChannelCreator(Chuck)
    wafermap = Instrument.ChannelCreator(WaferMap)

    def __init__(self, adapter, name="FormFactor Velox",
                 timeout=40000,
                 **kwargs):
        super().__init__(
            adapter, name,
            timeout=timeout,
            **kwargs
        )

    @property
    def options(self):
        """Get the installed options.
        Raises *NotImplementedError* since command ``*OPT?`` is not implemented in Velox."""
        raise NotImplementedError("*OPT? is not implemented in Velox.")

    version = Instrument.measurement(
        "ReportSoftwareVersion",
        """Get the main software version of Velox (str).""",
        )

    def read(self):
        """
        Read the response and check for errors.

        :raise: *ConnectionError* if an error is detected.

        """

        self.error_code = 0
        self.error_message = ""

        got = super().read()

        # some commands like *IDN do not return '0: ...'
        # in such a case return the entire response string
        if ":" not in got:
            return got

        got = got.partition(":")
        self.error_code = int(got[0])
        response = got[2].strip()

        if self.error_code:
            self.error_message = response
            if self.error_code not in EXPECTED_ERRORS:
                raise ConnectionError(f"{self.error_code}: {self.error_message}")
            else:
                log.info(f"{self.error_code}: {self.error_message}")

        return response

    def check_errors(self):
        """Invoke  :meth:`read`. """
        return self.read()
