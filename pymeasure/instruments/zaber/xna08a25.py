#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
# zaber_motion library: Copyright 2018-2022 Zaber Technologies Inc.
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
# Requires 'zaber-motion' package:
# https://gitlab.com/ZaberTech/zaber-motion-lib/-/tree/master/py/zaber_motion

import logging
from pymeasure.instruments import Instrument, Channel
from enum import Enum

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    # Requires 'zaber_motion' package:
    # https://gitlab.com/ZaberTech/zaber-motion-lib/-/tree/master/py/zaber_motion
    from zaber_motion import Units
    from zaber_motion.ascii import Connection
    from zaber_motion.ascii import Axis as Axis
except ModuleNotFoundError as err:
    log.info('Failed loading the zaber_motion package. '
             + 'Check the Zaber X-NA08A25 documentation on how to '
             + 'install this external dependency. '
             + f'ImportError: {err}')
    raise

class XNA08A25(Instrument):
    """ Represents the axes of Zaber X-NA08A25 micro linear actuator.

    This class provides direct access to zaber-motion-lib/py/zaber_motion.ascii.axis Python wrapper.

    e.g.
        connection = XNA08A25("COM3", axisnames="x")

        # Move to the mechanical home
        connection.x.home()

        # Move to 10mm
        connection.x.move_absolute(10, Units.LENGTH_MILLIMETRES)
        or
        connection.x.move_absolute(10, "mm")

        # Move by an additional 5mm
        connection.x.move_relative(5, Units.LENGTH_MILLIMETRES)
        or
        connection.x.move_relative(5, "mm")

        # Get the current position
        connection.x.get_position("mm")

        Units for the length should be "", "m", "cm", "mm", "µm", "um", "nm", or "in".
    """

    def __init__(self,
                 adapter=None,
                 name='Zaber X-NA08A25',
                 axisnames="",
                 ):
        """
        Initializes an instance of the Class.

        :param adapter: The VISA resource name of the controller
            (e.g. "COM3") or a created Adapter.
        :param axisnames: a list of axis names which will be used to create
            properties with these names (e.g. "x")
        :param name: The name of the device. Default is 'Zaber X-NA08A25'.
        :return: None
        """
        self.port_name = adapter
        self.name = name
        connection = Connection.open_serial_port(self.port_name)

        device_list = connection.detect_devices()
        log.info("Found {} devices".format(len(device_list)))
        log.info("Initializing %s." % self.name)

        self._axisnames = axisnames
        i = 0
        for device in device_list:
            for _ in range(device.axis_count):
                setattr(self, axisnames[i], device_list[i].get_axis(1))
                i += 1
