#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from pymeasure.instruments import Instrument

def on_off_command(v):
    if v:
        return "A"
    else:
        return "B"

def command_string(designators, v):
    return ''.join(on_off_command(v[i]) + designators[i] for i in range(0, len(designators)))
    
class Agilent11713A(Instrument):
    """ Represents the Agilent 11713A Attenuator / Switch Driver

    .. code-block:: python

        asd = Agilent11713A("GPIB::28")

        asd.reset()                             # Reset the instrument

        asd.attenuator_x = [0, 1, 0, 1]         # Sets the attenuator X values
        asd.attenuator_y = [1, 1, 0, 1]         # Sets the attenuator Y values
        asd.switches = [False, True]            # Sets the switch values

        asd.write("A12B34")                     # Sends command string

        Command strings are interpreted directly by the 11713A and comprise the 
        letter A followed by digits to turn on and/or the letter B followed by
        digits to turn off. For more details see the Agilent Technologies 
        11713A Attenuator/Switch Driver Operating and Service Manual.

    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent 11713A Attenuator / Switch Driver",
            includeSCPI=False,
            **kwargs
        )

    def reset(self):
        self.write("A0123456789")

    attenuator_x = Instrument.setting(
        "%s",
        """ A property that sets the attenuator X values via a four-element array.
        """,
        set_process=lambda v: command_string("1234", v)
    )

    attenuator_y = Instrument.setting(
        "%s",
        """ A property that sets the attenuator Y values via a four-element array.
        """,
        set_process=lambda v: command_string("5678", v)
    )

    switches = Instrument.setting(
        "%s",
        """ A property that sets the switch values via a two-element array.
        """,
        set_process=lambda v: command_string("90", v)
    )
