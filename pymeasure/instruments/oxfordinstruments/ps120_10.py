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


from .ips120_10 import IPS120_10


def PS_custom_get_process(v):
    """Adjust the received value, for working with the PS 120-10 """
    return v * 1e-2


def PS_custom_set_process(v):
    """Convert float to proper int value, for working with the PS 120-10 """
    return int(v * 1e2)


class PS120_10(IPS120_10):
    """Represents the Oxford Superconducting Magnet Power Supply PS 120-10.

    .. code-block:: python

        ps = PS120_10("GPIB::25")   # Default channel for the IPS

        ps.enable_control()         # Enables the power supply and remote control

        ps.train_magnet([           # Train the magnet after it has been cooled-down
            (11.8, 1.0),
            (13.9, 0.4),
            (14.9, 0.2),
            (16.0, 0.1),
        ])

        ps.set_field(12)            # Bring the magnet to 12 T. The switch heater will
                                    # be turned off when the field is reached and the
                                    # current is ramped back to 0 (i.e. persistent mode).

        print(self.field)           # Print the current field (whether in persistent or
                                    # non-persistent mode)

        ps.set_field(0)             # Bring the magnet to 0 T. The persistent mode will be
                                    # turned off first (i.e. current back to set-point and
                                    # switch-heater on); afterwards the switch-heater will
                                    # again be turned off.

        ps.disable_control()        # Disables the control of the supply, turns off the
                                    # switch-heater and clamps the output.

    :param clear_buffer: A boolean property that controls whether the instrument
        buffer is clear upon initialisation.
    :param switch_heater_heating_delay: The time in seconds (default is 20s) to wait after
        the switch-heater is turned on before the heater is expected to be heated.
    :param switch_heater_cooling_delay: The time in seconds (default is 20s) to wait after
        the switch-heater is turned off before the heater is expected to be cooled down.
    :param field_range: A numeric value or a tuple of two values to indicate the
        lowest and highest allowed magnetic fields. If a numeric value is provided
        the range is expected to be from :code:`-field_range` to :code:`+field_range`.

    """

    def __init__(self,
                 adapter,
                 name="Oxford PS",
                 **kwargs):

        super().__init__(
            adapter=adapter,
            name=name,
            **kwargs,
        )

    current_measured_get_process = PS_custom_get_process

    demand_current_get_process = PS_custom_get_process

    demand_field_get_process = PS_custom_get_process

    persistent_field_get_process = PS_custom_get_process

    current_setpoint_get_process = PS_custom_get_process
    current_setpoint_set_process = PS_custom_set_process
    current_setpoint_set_command = "I%d"

    field_setpoint_get_process = PS_custom_get_process
    field_setpoint_set_process = PS_custom_set_process
    field_setpoint_set_command = "J%d"

    sweep_rate_get_process = PS_custom_get_process
    sweep_rate_set_process = PS_custom_set_process
    sweep_rate_set_command = "T%d"
