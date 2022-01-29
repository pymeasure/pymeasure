#
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

from pymeasure.instruments import Instrument
from pymeasure.instruments.toptica.adapters import TopticaAdapter
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class IBeamSmart(Instrument):
    """ IBeam Smart laser diode

    :param port: pyvisa resource name of the instrument
    :param baud_rate: communication speed, defaults to 115200
    :param kwargs: Any valid key-word argument for VISAAdapter
    """
    def __init__(self, port, baud_rate=115200, **kwargs):
        if not isinstance(port, str):
            raise TypeError("'port' must be a pyvisa resource name string")
        super().__init__(
            TopticaAdapter(port, baud_rate, **kwargs),
            "toptica IBeam Smart laser diode",
            includeSCPI=False,
        )

    version = Instrument.measurement(
           "ver", """ Firmware version number """,
    )

    serial = Instrument.measurement(
           "serial", """ Serial number of the laser system """,
    )

    temp = Instrument.measurement(
            "sh temp",
            """ temperature of the laser diode in degree centigrade.""",
    )

    system_temp = Instrument.measurement(
            "sh temp sys",
            """ base plate (heatsink) temperature in degree centigrade.""",
    )

    laser_enabled = Instrument.control(
            "sta la", "la %s",
            """ Status of the laser diode driver.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "on" if v else "off",
    )

    channel1_enabled = Instrument.control(
            "sta ch 1", "%s",
            """ Status of Channel 1 of the laser.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "en 1" if v else "di 1",
    )

    channel2_enabled = Instrument.control(
            "sta ch 2", "%s",
            """ Status of Channel 2 of the laser.
                This can be True if the laser is on or False otherwise""",
            validator=strict_discrete_set,
            values=[True, False],
            get_process=lambda s: True if s == 'ON' else False,
            set_process=lambda v: "en 2" if v else "di 2",
    )

    power = Instrument.control(
            "sh pow", "ch pow %f mic",
            """ Actual output power in uW of the laser system. In pulse mode
            this means that the set value might not correspond to the readback
            one.""",
            validator=strict_range,
            values=[0, 200000],
    )

    def enable_continous(self):
        """ enable countinous emmission mode """
        self.write('di ext')
        self.laser_enabled = True
        self.channel2_enabled = True

    def enable_pulsing(self):
        """ enable pulsing mode. The optical output is controlled by a digital
        input signal on a dedicated connnector on the device """
        self.laser_enabled = True
        self.channel2_enabled = True
        self.write('en ext')

    def disable(self):
        """ shutdown all laser operation """
        self.write('di ext')
        self.channel2_enabled = False
        self.laser_enabled = False
