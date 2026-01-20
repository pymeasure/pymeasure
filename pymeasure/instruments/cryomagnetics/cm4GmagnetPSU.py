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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_range


class Cryomagnetics4GMagnetPowerSupplyBase(Instrument):
    """
    Represents the Cryomagnetics 4G Magnet Power Supply family and provides a
    high-level interface for interacting with the instrument via GPIB.

    The below implementation is based on revision 9.3 of the Operating
    Instruction Manual (issued 02/20/2020). While the instrument is purported
    to be adherent to the 488.2 standard, it does not appear to be fully
    SCPI-compliant.

    There are four model varieties that share the same instruction set:

    +-------------------+-----------------+-------------------------+
    | Name              | Max Current (A) | Max Output Power (W)    |
    +===================+=================+=========================+
    | 4G-100            | 100             | 1000 (10 V @ 100 A)     |
    +-------------------+-----------------+-------------------------+
    | 4G-150s           | 150             | 1500 (10 V @ 150 A)     |
    +-------------------+-----------------+-------------------------+
    | 4G-200s           | 200             | 1600 (8 V @ 200 A)      |
    +-------------------+-----------------+-------------------------+
    | 4G-Dual (100/100) | 100 / 100       | 800 / 800 (8 V @ 100 A) |
    +-------------------+-----------------+-------------------------+

    The 4G-100, 4G-150s and 4G-200s have one bipolar output channel, while
    the 4G-Dual has two bipolar output channels. The four models inherit from
    the common base unit.

    The implementation does not at this time include methods for adjusting any
    of the shim magnets, only the main superconducting magnet.

    """

    current_values = [-100, 100]
    sweep_lower_limit_vaues = current_values
    sweep_upper_limit_values = current_values

    def __init__(self,
                 adapter,
                 name="Cryomagnetics 4G Magnet Power Supply",
                 **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            read_termination="\n",
            write_termination="\n",
            includeSCPI=False,
            **kwargs
        )

    identity = Instrument.measurement(
        "*IDN?",
        """Get the identity of the unit."""
    )

    usb_error_report = Instrument.control(
        "ERROR?",
        "ERROR %d",
        """
        Control whether errors messages are reported over the USB / RS-232 interface,
        takes values True of False (bool).
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    units = Instrument.control(
        "UNITS?",
        "UNITS %s",
        """
        Control the unit to be used for all input and display operations, takes the
        values 'A' for Amps or 'G' for Gauss. The unit will autorange to display Gauss,
        kiloGauss or Tesla.
        """,
        validator=strict_discrete_set,
        values=['A', 'G']
    )

    magnet_current = Instrument.control(
        "UNITS A;IMAG?",
        "UNITS A;IMAG %g",
        """Control the magnet current in Amps up to +/- the maximum current of the model.

        If the persistent switch heater is **ON**, the magnet current returned will be the same as
        the power supply output current. If the persistent switch heater is **OFF**, the magnet 
        current will be the value of the power supply output current when the persistent switch 
        heater was last turned off. The magnet current will be set to zero if the power supply 
        detects a quench.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.split(" ")[0],
        validator=truncated_range,
        values=[-100, 100],
        dynamic=True
    )

    output_current = Instrument.measurement(
        "UNITS A;IOUT?",
        """
        Get the power supply output current in Amps.

        This may or may not be the same as ``magnet_current`` depending on the state of the
        persistent switch heater (if fitted) and the output history.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.split(" ")[0],
    )

    sweep_lower_limit = Instrument.control(
        "UNITS A;LLIM?",
        "UNITS A;LLIM %g",
        """
        Control the lower limit of the current sweep in Amps in the range +/- maximum current. 

        In effect, it sets the current limit for when the next ``sweep = 'DOWN'`` command is issued.

        Must be less than ``sweep_upper_limit``.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.split(" ")[0],
        validator=truncated_range,
        values=[-100, 100],
        dynamic=True,
    )

    sweep_upper_limit = Instrument.control(
        "UNITS A;ULIM?",
        "UNITS A;ULIM %g",
        """
        Control the upper limit of the current sweep in Amps in the range +/- maximum current. 

        In effect, it sets the current limit for when the next ``sweep = 'UP'`` command is issued.

        Must be greater than ``sweep_lower_limit``.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.split(" ")[0],
        validator=truncated_range,
        values=[-100, 100],
        dynamic=True,
    )

    name = Instrument.control(
        "NAME?",
        "NAME %s",
        """Control the name of the currently selected module on the display.
        Upper and lower case area accepted; however the string is converted to upper case.

        Must be between 0 and 16 characters in length.
        """
    )


class Cryomagnetics4G100(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-100 magnet power supply.
    """
    current_values = [-100, 100]
    sweep_lower_limit_values = current_values
    sweep_upper_limit_values = current_values


class Cryomagnetics4G150s(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-150s magnet power supply.
    """
    current_values = [-150, 150]
    sweep_lower_limit_values = current_values
    sweep_upper_limit_values = current_values


class Cryomagnetics4G200s(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-200s magnet power supply.
    """
    current_values = [-200, 200]
    sweep_lower_limit_values = current_values
    sweep_upper_limit_values = current_values


class Cryomagnetics4GDual(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-Dual magnet power supply.
    """
    current_values = [-100, 100]
    sweep_lower_limit_values = current_values
    sweep_upper_limit_values = current_values

    channel = Instrument.control(
        "CHAN?",
        "CHAN %d",
        """
        Control the power module channel selected for remote commands,
        takes values 1 or 2.

        This is only applicable to the 4G-Dual model.
        """,
        validator=strict_discrete_set,
        values=[1, 2]
    )
