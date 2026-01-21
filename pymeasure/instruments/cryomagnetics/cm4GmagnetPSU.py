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


PERSISTENT_SWITCH_HEATER_STATES = {
    0: 'OFF',
    1: 'ON'
}

SWEEP_MODES = [
    "UP",
    "UP FAST",
    "UP SLOW",
    "DOWN",
    "DOWN FAST",
    "DOWN SLOW",
    "PAUSE",
    "PAUSE FAST",
    "PAUSE SLOW",
    "ZERO",
    "ZERO FAST",
    "ZERO SLOW"
]


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

    The primary purpose of the magnet is to perform hysteresis-type measurements,
    where the magnetic field is swept up and down between specified limits and
    at specified rates. These limits are set by ``sweep_upper_limit`` and
    ``sweep_lower_limit``.

    Additionally, the sweep function of the power supply is segmented into five
    **Ranges**, 1 to 4, as viewable on the magnet power supply. I.e., **Range 1** starts
    at ``range_boundary 0`` and extends to ``range_boundary 1``, **Range 2** starts at
    ``range_boundary 1`` and extends to ``range_boundary 2``, and so on. The boundary limits
    can be configured using ``get_range_limit`` and ``set_range_limit``. The sweep rate
    for each **Range** can be individually configured using ``get_range_rate`` and
    ``set_range_rate``. Typically you might sweep faster at lower fields, e.g. 0 to
    +/- 5 T, and then slow down at higher fields (both in a positive and negative
    sense) where the risk of magnet quench is higher, e.g. 5 to 7 T.

    The magnet power supply can be instructed to do the following:

    * ``sweep_mode = 'UP'`` to ``sweep_upper_limit``.
    * ``sweep_mode = 'DOWN'`` to ``sweep_lower_limit``.
    * ``sweep_mode = 'PAUSE'``, i.e. stop changing the current in the magnet.
    * ``sweep_mode = 'ZERO'``, i.e. go to zero, discharge the magnet.

    The magnet will attempt to respond at whatever sweep rate has been defined according
    to whichever **Range** it is currently in.

    Additionally, there is a *fast* rate that can be configured with ``get_fast_rate``
    and ``set_fast_rate``. The fast rate is invoked by appending ``'FAST'`` to any of
    the four instructions above, e.g. ``'UP FAST'``. The sweep rate of the current
    **Range** will be overridden by the fast rate. However, future instructions will
    also be executed with the fast rate unless ``'SLOW'`` is added, at which point
    the rate will once more be determined according to the present **Range**.

    .. code-block:: python

        # start sweeping to upper limit
        magnet.sweep_mode = 'UP'
        # some time later, pause the sweep
        magnet.sweep_mode = 'PAUSE'
        # continue sweeping up, but now at fast rate
        magnet.sweep_mode = 'UP FAST'
        # pause the sweep
        magnet.sweep_mode = 'PAUSE'
        # sweep down reverting to slow rate
        magnet.sweep_mode = 'DOWN SLOW'
        # sweep back to zero
        magnet.sweep_mode = 'ZERO'
    """

    _MAXIMUM_CURRENT = 100
    _MAXIMUM_VOLTAGE = 10

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
        """
        Get the identity of the unit.

        Response will be in the format:

        ``<Manufacturer>,<Model>,<Serial #>,<Firmware Level>,<build number>``
        """
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
        """Control the magnet current in Amps up to +/- the maximum supply current of the model.

        If the persistent switch heater is **ON**, the magnet current returned will be the same as
        the power supply output current. If the persistent switch heater is **OFF**, the magnet
        current will be the value of the power supply output current when the persistent switch
        heater was last turned off. The magnet current will be set to zero if the power supply
        detects a quench.

        **How does this actually work??**

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.split(" ")[0],
        validator=truncated_range,
        values=[-_MAXIMUM_CURRENT, _MAXIMUM_CURRENT],
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
        values=[-_MAXIMUM_CURRENT, _MAXIMUM_CURRENT],
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
        values=[-_MAXIMUM_CURRENT, _MAXIMUM_CURRENT],
    )

    name = Instrument.control(
        "NAME?",
        "NAME %s",
        """Control the name of the currently selected module on the display.
        Upper and lower case area accepted; however the string is converted to upper case.

        Must be between 0 and 16 characters in length.
        """
    )

    persistent_switch_heater = Instrument.control(
        "PSHTR?",
        "PSHTR %s",
        """
        Control the status of the persistent switch heater, either ``'ON'`` or ``'OFF'``.
        """,
        validator=strict_discrete_set,
        values=PERSISTENT_SWITCH_HEATER_STATES,
        get_process=lambda x: PERSISTENT_SWITCH_HEATER_STATES[int(x)]
    )

    voltage_limit = Instrument.control(
        "VLIM?",
        "VLIM %g",
        """
        Control the power supply output voltage limit in Volts, ranging from 0 to
        max supply voltage.

        Only positive values are accepted. Internally, the negative limit will be set
        to ``-voltage_limit``.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_VOLTAGE],
        preprocess_reply=lambda response: response.split(" ")[0]
    )

    magnet_voltage = Instrument.measurement(
        "VMAG?",
        """
        Get the present magnet voltage in Volts.
        """,
        preprocess_reply=lambda response: response.split(" ")[0]
    )

    output_voltage = Instrument.measurement(
        "VOUT?",
        """
        Get the present power supply output voltage in Volts.
        """,
        preprocess_reply=lambda response: response.split(" ")[0]
    )

    sweep_mode = Instrument.control(
        "SWEEP?",
        "SWEEP %s",
        """
        Control the sweep mode of the power supply.

        Possible values are ``'UP'``, ``'DOWN'``, ``'PAUSE'`` and ``'ZERO'``.

        Additionally, each may be modified by either ``'SLOW'`` or ``'FAST'``.

        For example ``sweep_mode = 'UP FAST'``.
        """,
        validator=strict_discrete_set,
        values=SWEEP_MODES,
        preprocess_reply=lambda response: response.strip("SWEEP ")
    )

    def quench_reset(self):
        """Resets the power supply quench doncition and returns it to **STANDBY**."""
        self.write("QRESET")

    def get_range_limit(self, range_boundary: int):
        """
        Get the boundary limit, in Amps, of the specified ``range_boundary``.

        :param range_boundary: The desired sweep range boundary to query, from 0 to 4.

        :return: The value of the boundary, in Amps.
        """

        if not isinstance(range_boundary, int) or \
                range_boundary not in (0, 1, 2, 3, 4):
            return -1
        else:
            self.write(
                f"RANGE? {range_boundary}"
            )
            response = self.read()
            return response

    def set_range_limit(self, range_boundary: int, limit: float):
        """
         Set the value of the boundary, in Amps, of the specified ``range_boundary``
         to be ``limit``.

        :param range_boundary: The desired boundary to set, from 0 to 4.
        :type range_boundary: int
        :param limit: The value of the boundary, in Amps, from 0 to maximum supply current.
        :type limit: float
        """
        if not isinstance(range_boundary, int) or \
                range_boundary not in (0, 1, 2, 3, 4) or \
                not isinstance(limit, float):
            return
        else:
            if limit < 0:
                limit = 0
            elif limit > self.__class__._MAXIMUM_CURRENT:
                limit = self.__class__._MAXIMUM_CURRENT

            self.write(
                f"RANGE {range_boundary} {limit:.f}"
            )

    def get_range_rate(self, sweep_range: int):
        """
        Get the sweep rate, in Amps/second, for the specified ``sweep_range``
        (i.e. **Range**), in the range 1 to 4.

        :param sweep_range: The **Range** to query.
        :type sweep_range: int
        """
        if not isinstance(sweep_range, int) or \
                sweep_range not in (1, 2, 3, 4):
            return -1
        else:
            self.write(
                f"RATE? {sweep_range-1}"
            )
            response = self.read()
            return response

    def set_range_rate(self, sweep_range: int, rate: float):
        """
        Set the sweep rate, in Amps/second, for the specified ``sweep_range``
        (i.e. **Range**), in the range 1 to 4.

        :param sweep_range: The **Range** to configure.
        :type sweep_range: int
        :param rate: The rate, in Amps/second, to set.
        :type rate: float
        """
        if not isinstance(sweep_range, int) or \
                sweep_range not in (1, 2, 3, 4) or \
                not isinstance(rate, float):
            return
        else:
            if rate < 0:
                rate = 0
            elif rate > self.__class__._MAXIMUM_CURRENT:
                rate = self.__class__._MAXIMUM_CURRENT

            self.write(
                f"RANGE {sweep_range-1} {rate:f}"
            )

    def get_fast_rate(self):
        """
        Get the fast sweep rate in Amps/second.
        """
        self.write(
            "RATE? 5"
        )
        response = self.read()
        return response

    def set_fast_rate(self, rate: float):
        """
        Set the fast sweep rate in Amps/second.

        :param rate: The fast sweep rate, in Amps/second.
        :type rate: float
        """
        if rate < 0:
            rate = 0
        elif rate > self.__class__._MAXIMUM_CURRENT:
            rate = self.__class__._MAXIMUM_CURRENT

        self.write(
            f"RANGE 5 {rate:f}"
        )

    def reset(self):
        """
        Reset the unit.
        """
        self.write("*RST")


class Cryomagnetics4G100(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-100 magnet power supply.
    """
    _MAXIMUM_CURRENT = 100
    _MAXIMUM_VOLTAGE = 10


class Cryomagnetics4G150s(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-150s magnet power supply.
    """
    _MAXIMUM_CURRENT = 150
    _MAXIMUM_VOLTAGE = 10


class Cryomagnetics4G200s(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-200s magnet power supply.
    """
    _MAXIMUM_CURRENT = 200
    _MAXIMUM_VOLTAGE = 8


class Cryomagnetics4GDual(Cryomagnetics4GMagnetPowerSupplyBase):
    """
    Represents the Cryomagnetics model 4G-Dual magnet power supply.
    """
    _MAXIMUM_CURRENT = 100
    _MAXIMUM_VOLTAGE = 8

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
