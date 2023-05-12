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
    (if applicable to the module).
    """

    def __init__(self, adapter, name= "ETS Lindgren EMCenter Postioning Card", slot=1, device="A", **kwargs):

        kwargs.setdefault("write_termination", "\n")
        kwargs.setdefault("read_termination", "\n")
        super().__init__(adapter, "test", **kwargs)
        self._slot = slot
        self._device = device

        type = self.values("TYPE?", separator=" ")
        type, self._subtype = (type[0], type[1:])
        self._type = "Tower" if type == "TWR" else ("Turntable" if type == "TT" else "Unknown")
        if self._type == "Unknown":
            raise ValueError("Device type not recognized")

    def write(self, command):
        super().write(f"{self._slot}{self._device}{command}")

    def values(self, command, **kwargs):
        return super().values(f"{self._slot}{self._device}{command}", **kwargs)

    acceleration = Instrument.control(
        "ACC?",
        "ACC %g",
        """Control the acceleration of the device in seconds. Settable 0.1 and 30,
        and gettable.
        """,
        values=(0.1, 30),
        validator=strict_range,
    )

    speed = Instrument.control(
        "SPEED?",
        "SPEED %g",
        """Control  the speed of the device, as a percentage of the max speed.
        Settable 0.0 to 100.0, and gettable.""",
        values=(0.0, 100.0),
        validator=strict_range,
    )

    aux1_enabled = Instrument.control(
        "AUX1?",
        "AUX1 %g",
        """Control the auxiliary input 1, Settable to ON or OFF, and gettable.""",
        values={True:"ON", False:"OFF"},
  
        map_values=True,
    )

    aux2_enabled = Instrument.control(
        "AUX2?",
        "AUX2 %g",
        """Control the auxiliary input 2, Settable to ON or OFF, and gettable.""",
        values={True:"ON", False:"OFF"},
        map_values=True,
        
    )

    polarity = Instrument.control(
        "P?",
        "P %g",
        """Control the polarity of the antenna tower. Returns either H or V.""",
        values=("H", "V"),
        validator=strict_discrete_set,
    )

    position= Instrument.control(
        "CP?",
        "SK %g",
        """Control the position of the device. settable and gettable.""",
     
    )

    direction = Instrument.measurement(
        "DIR?",
        """Get the direction of the device. Returns either -1,0 , or 1.""",
    )

    def move_to_negative_position(self, position):
        """Move the device to the given position in the down or counter clockwise direction."""
        self.write(f"SKN {position}")

    def move_to_positive_position(self, position):
        """Move the device to the given position in the up or clockwise direction."""
        self.write(f"SKP {position}")

    def move_distance(self, distance):
        """Move the device the given distance. """
        self.write(f"SKR {distance}")

    def rotate_cw(self):
        """Rotate the device clockwise. if device is a turntable else it will error."""
        if self._type == "Turntable":
            self.write("CW")
        else:
            raise ValueError("Device must be a turntable to rotate")

    def rotate_ccw(self):
        """Rotate the device counter clockwise. if device is a turntable else it will error."""
        if self._type == "Turntable":
            self.write("CCW")
        else:
            raise ValueError("Device must be a turntable to rotate")

    def move_up(self): 
        """Move the tower up. if device is an antenna tower else it will error."""
        if self._type == "Tower":
            self.write("UP")
        else:
            raise ValueError("Device must be a tower to move up")

    def move_down(self):
        """Move the tower down. if device is a antenna tower else it will error."""
        if self._type == "Tower":
            self.write("DN")
        else:
            raise ValueError("Device must be a tower to move down")

    def stop(self):
        """Stop the device."""
        self.write("ST")