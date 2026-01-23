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


class Cryomagnetics4G100(Instrument):
    """
    Represents the Cryomagnetics 4G-100 Magnet Power Supply and family,
    and provides a high-level interface for interacting with the instrument
    via GPIB.

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
    the 4G-Dual has two bipolar output channels. The 4G-100 model acts as a
    base for the three other models.

    The implementation does not at this time include methods for adjusting any
    of the shim magnets, only the main superconducting magnet.

    The primary purpose of the magnet is to perform hysteresis-type measurements,
    where the magnetic field is swept up and down between specified limits and
    at specified rates. These limits are set by ``sweep_upper_limit`` and
    ``sweep_lower_limit``.

    Additionally, the sweep function of the power supply is segmented into five
    **Ranges**, 1 to 5 as viewable on the magnet power supply:

    * **Range 1** starts at ``range_boundary_0`` and extends to ``range_boundary_1``
    * **Range 2** starts at ``range_boundary_1`` and extends to ``range_boundary_2`` etc...


    The exception is **Range 5** which begins at ``range_boundary_4`` and extends to the
    maximum supply current.

    The sweep rate for each **Range** can be individually configured with e.g. ``range_1_rate``
    for **Range 1**. The sweep rates can take values from 0 to max supply current,
    e.g. 100 Amps/second for the 4G-100. However, this is likely not a realistic sweep rate.
    It is strongly advised not to attempt to sweep faster than your magnet can handle. This
    should be specified by the manufacturer. Typically you might sweep faster at lower fields,
    e.g. 0 to +/- 5 T, and then slow down at higher fields (both in a positive and negative
    sense) where the risk of magnet quench is higher, e.g. 5 to 7 T. Generally, once these
    have been initially configured then there shouldn't be a need to adjust them any further
    during your measurements

    The magnet power supply can be instructed to do the following:

    * ``sweep_mode = 'UP'`` to ``sweep_upper_limit``.
    * ``sweep_mode = 'DOWN'`` to ``sweep_lower_limit``.
    * ``sweep_mode = 'PAUSE'``, i.e. stop changing the current in the magnet.
    * ``sweep_mode = 'ZERO'``, i.e. go to zero, discharge the magnet.

    The magnet will attempt to respond at whatever sweep rate has been defined according
    to whichever **Range** it is currently in.

    Additionally, there is a *fast* rate (``fast_rate``). The fast rate is invoked by
    appending ``'FAST'`` to any of the four instructions above, e.g. ``'UP FAST'``.
    The sweep rate of the current **Range** will be overridden by the fast rate. However,
    future instructions will also be executed with the fast rate unless ``'SLOW'`` is added,
    at which point the rate will once more be determined according to the present **Range**.

    As an example:

    .. code-block:: python

        # Instantiate the power supply
        magnet = Cryomagnetics4G100("GPIB::1")

        # Give it a name
        magnet.name = "my magnet"

        # Set up a sweep between 0 and 10 Amps, or 0 and 2 Tesla
        # The magnet has a calibration 0.2 Tesla per Amp
        # or 5 Amps per Tesla
        magnet.sweep_lower_limit = 0
        magnet.sweep_upper_limit = 10

        # Set up two sweep ranges:
        # 0 to 5 Amps (boundaries 0 and 1)
        # 5 to 10 Amps (boundaries 1 and 2)
        magnet.range_boundary_0 = 0
        magnet.range_boundary_1 = 5
        magnet.range_boundary_2 = 10

        # Set the sweep rate for range 1 to be 1 Amps/second
        # and for range 2 to be 0.5 Amps/second
        magnet.range_1_rate = 1
        magnet.range_2_rate = 0.5

        # Additionally, configure the fast rate
        magnet.fast_rate = 2

        # Assume magnet is already at zero field
        # start sweeping to upper limit
        magnet.sweep_mode = 'UP'
        # ...
        # some time later, pause the sweep
        magnet.sweep_mode = 'PAUSE'
        # continue sweeping up, but now at fast rate
        magnet.sweep_mode = 'UP FAST'
        # pause the sweep
        magnet.sweep_mode = 'PAUSE'
        # sweep down reverting to rate determined by current range
        magnet.sweep_mode = 'DOWN SLOW'
        # sweep back to zero
        magnet.sweep_mode = 'ZERO'
    """

    _MAXIMUM_CURRENT = 100
    _MAXIMUM_VOLTAGE = 10

    def __init__(self,
                 adapter,
                 name="Cryomagnetics 4G-100 Magnet Power Supply",
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

    magnet_current = Instrument.measurement(
        "UNITS A;IMAG?",
        """
        Get the magnet current in Amps.

        If the persistent switch heater is **ON**, the magnet current returned will be the same as
        the power supply output current. If the persistent switch heater is **OFF**, the magnet
        current will be the value of the power supply output current when the persistent switch
        heater was last turned off. The magnet current will be set to zero if the power supply
        detects a quench.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.replace("A", ""),
    )

    output_current = Instrument.measurement(
        "UNITS A;IOUT?",
        """
        Get the power supply output current in Amps.

        This may or may not be the same as ``magnet_current`` depending on the state of the
        persistent switch heater (if fitted) and the output history.

        N.B. The ``units`` will always be switched to Amps when using this command.
        """,
        preprocess_reply=lambda response: response.replace("A", ""),
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
        preprocess_reply=lambda response: response.replace("A", ""),
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
        preprocess_reply=lambda response: response.replace("A", ""),
        validator=truncated_range,
        values=[-_MAXIMUM_CURRENT, _MAXIMUM_CURRENT],
    )

    magnet_name = Instrument.control(
        "NAME?",
        "NAME %s",
        """
        Control the name of the currently selected module on the display.
        Upper and lower case area accepted; however the string is converted to upper case.

        Must be between 0 and 16 characters in length. Longer names will be truncated.
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
        preprocess_reply=lambda response: response.replace("V", "")
    )

    magnet_voltage = Instrument.measurement(
        "VMAG?",
        """
        Get the present magnet voltage in Volts.
        """,
        preprocess_reply=lambda response: response.replace("V", ""),
        cast=float
    )

    output_voltage = Instrument.measurement(
        "VOUT?",
        """
        Get the present power supply output voltage in Volts.
        """,
        preprocess_reply=lambda response: response.replace("V", ""),
        cast=float
    )

    sweep_mode = Instrument.control(
        "SWEEP?",
        "SWEEP %s",
        """
        Control the sweep mode of the power supply.

        Possible values are ``'UP'``, ``'DOWN'``, ``'PAUSE'`` and ``'ZERO'``.

        Additionally, each may be modified by either ``'SLOW'`` or ``'FAST'`` 
        (see main class description for full explanation.)

        For example ``sweep_mode = 'UP FAST'``.

        Return values are ``'STANDBY'``, ``'SWEEPING UP'``, ``'SWEEPING DOWN'``,
        ``'SWEEPING PAUSED'`` or ``'SWEEPING TO ZERO'``.
        """,
        validator=strict_discrete_set,
        values=SWEEP_MODES,
        preprocess_reply=lambda response: response.upper()
    )

    range_1_rate = Instrument.control(
        "RATE? 0",
        "RATE 0 %g",
        """
        Control the rate, in Amps/second, of Range 1.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_2_rate = Instrument.control(
        "RATE? 1",
        "RATE 1 %g",
        """
        Control the rate, in Amps/second, of Range 2.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_3_rate = Instrument.control(
        "RATE? 2",
        "RATE 2 %g",
        """
        Control the rate, in Amps/second, of Range 3.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_4_rate = Instrument.control(
        "RATE? 3",
        "RATE 3 %g",
        """
        Control the rate, in Amps/second, of Range 4.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_5_rate = Instrument.control(
        "RATE? 4",
        "RATE 4 %g",
        """
        Control the rate, in Amps/second, of Range 5.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    fast_rate = Instrument.control(
        "RATE? 5",
        "RATE 5 %g",
        """
        Control the fast sweep rate, in Amps/second.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_boundary_0 = Instrument.control(
        "RANGE? 0",
        "RANGE 0 %g",
        """
        Control the value, in Amps, of range boundary 0.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_boundary_1 = Instrument.control(
        "RANGE? 1",
        "RANGE 1 %g",
        """
        Control the value, in Amps, of range boundary 1.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_boundary_2 = Instrument.control(
        "RANGE? 2",
        "RANGE 2 %g",
        """
        Control the value, in Amps, of range boundary 2.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_boundary_3 = Instrument.control(
        "RANGE? 3",
        "RANGE 3 %g",
        """
        Control the value, in Amps, of range boundary 3.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    range_boundary_4 = Instrument.control(
        "RANGE? 4",
        "RANGE 4 %g",
        """
        Control the value, in Amps, of range boundary 4.
        """,
        validator=truncated_range,
        values=[0, _MAXIMUM_CURRENT]
    )

    def quench_reset(self):
        """Resets the power supply quench doncition and returns it to **STANDBY**."""
        self.write("QRESET")

    def reset(self):
        """
        Reset the unit.
        """
        self.write("*RST")


class Cryomagnetics4G150s(Cryomagnetics4G100):
    """
    Represents the Cryomagnetics model 4G-150s magnet power supply.
    """
    _MAXIMUM_CURRENT = 150
    _MAXIMUM_VOLTAGE = 10

    def __init__(self,
                 adapter,
                 name="Cryomagnetics 4G-150s Magnet Power Supply",
                 **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            **kwargs
        )


class Cryomagnetics4G200s(Cryomagnetics4G100):
    """
    Represents the Cryomagnetics model 4G-200s magnet power supply.
    """
    _MAXIMUM_CURRENT = 200
    _MAXIMUM_VOLTAGE = 8

    def __init__(self,
                 adapter,
                 name="Cryomagnetics 4G-200s Magnet Power Supply",
                 **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            **kwargs
        )


class Cryomagnetics4GDual(Cryomagnetics4G100):
    """
    Represents the Cryomagnetics model 4G-Dual magnet power supply.
    """
    _MAXIMUM_CURRENT = 100
    _MAXIMUM_VOLTAGE = 8

    def __init__(self,
                 adapter,
                 name="Cryomagnetics 4G-Dual Magnet Power Supply",
                 **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            **kwargs
        )

    channel = Instrument.control(
        "CHAN?",
        "CHAN %d",
        """
        Control the power module channel selected for remote commands,
        takes values 1 or 2.
        """,
        validator=strict_discrete_set,
        values=[1, 2]
    )
