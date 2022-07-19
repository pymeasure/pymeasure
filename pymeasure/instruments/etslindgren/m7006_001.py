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
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class M7006_001(Instrument):
    """Position control card of EMCenter modular system.
    Allows for controll and feedback of the positioner card.
    Comunication happes transparently through the EMCenter mainframe.
    devices share the resource name of the mainframe, and
    are identified by the slot number and the device number
    (if applicable to the modual).
    """

    def __init__(self, resource_name, slot=1, device="A", **kwargs):

        kwargs.setdefault("write_termination", "\n")
        super().__init__(resource_name, "test", **kwargs)
        self._slot = slot
        self._device = device

    def write(self, command):
        super().write(f"{self._slot}{self._device}{command}")

    def values(self, command, **kwargs):
        return super().values(f"{self._slot}{self._device}{command}", **kwargs)

    acceleration = Instrument.control(
        "ACC?",
        "ACC %g",
        """Acceleration of the device in seconds. Settable 0.1 and 30,
        and gettable.
        """,
        values=(0.1, 30),
        validator=strict_range,
    )

    speed = Instrument.control(
        "SPEED?",
        "SPEED %g",
        """Speed of the device, as a percentage of the max speed.
        Settable 0.0 to 100.0, and gettable.""",
        values=(0.0, 100.0),
        validator=strict_range,
    )

    aux1 = Instrument.control(
        "AUX1?",
        "AUX1 %g",
        """Auxiliary input 1, Settable to ON or OFF, and gettable.""",
        values=("ON", "OFF"),
        validator=strict_discrete_set,
    )

    aux2 = Instrument.control(
        "AUX2?",
        "AUX2 %g",
        """Auxiliary input 2, Settable to ON or OFF, and gettable.""",
        values=("ON", "OFF"),
        validator=strict_discrete_set,
    )

    rotation = Instrument.setting(
        "%g",
        """Rotate the device in the given direction. CW or CCW.""",
        values=("CW", "CCW"),
        validator=strict_discrete_set,
    )

    movement = Instrument.setting(
        "%g",
        """Move the tower up or down.""",
        values={"up": "UP", "down": "DN"},
        map_values=True,
    )

    def stop(self):
        """Stop the device."""
        self.write("ST")

    polarity = Instrument.control(
        "P?",
        "P %g",
        """Polarity of the antenna boom. Returns either H or V.""",
        values=("H", "V"),
        validator=strict_discrete_set,
    )

    position = Instrument.control(
        "CP?",
        "CP %g",
        """Current position of the device. Settable and gettable.
        does not move the device.
        """,
    )

    direction = Instrument.measurement(
        "DIR?",
        """Direction of the device. Returns either -1,0 , or 1.""",
    )

    target_position = Instrument.setting(
        "SK %g",
        """Move the device to the given position, by the shortest distance.""",
    )

    target_negative_positon = Instrument.setting(
        "SKN %g",
        """Moves the device to the given position, in the down or
        counter clockwise direction.
        """,
    )

    target_positive_position = Instrument.setting(
        "SKP %g",
        """Moves the device to the given position, in the up or
        clockwise direction.
        """,
    )

    target_relative_postion = Instrument.setting(
        "SKR %g",
        """Moves the device to the given position relative to the current
        position.
        """,
    )
