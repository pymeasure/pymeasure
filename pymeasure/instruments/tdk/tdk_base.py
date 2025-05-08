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

# =============================================================================
# Libraries / modules
# =============================================================================

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_range
from pymeasure.instruments.validators import strict_discrete_set
from pymeasure.instruments.validators import strict_discrete_range
import logging
from time import sleep
import numpy as np

# =============================================================================
# Logging
# =============================================================================

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# =============================================================================
# Instrument file
# =============================================================================


class TDK_Lambda_Base(Instrument):
    """
    This is the base class for TDK Lambda Genesys Series DC power supplies.
    Do not directly instantiate an object with this class. Use one of the
    TDK-Lambda power supply instrument classes that inherit from this parent
    class. Untested commands are noted in docstrings.
    """

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Initializer and important communication methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, adapter, name="TDK-Lambda Base", address=6, **kwargs):
        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            asrl={'read_termination': "\r", 'write_termination': "\r"},
            **kwargs
        )
        self.address = address

    def check_set_errors(self):
        """
        Only use this command for setting commands, i.e. non-querying commands.

        Any non-querying commands (i.e., a command that does NOT
        have the "?" symbol in it like the instrument command "PV 10") will
        automatically return an "OK" reply for valid command or an error code.
        This is done to confirm that the instrument has received the command.
        Any querying commands (i.e., a command that does have the "?" symbol
        in it like the instrument command "PV?") will return the requested value,
        not the confirmation.
        """
        response = self.read()
        error_list = []
        if response != "OK":
            error_list.append(f"Received error: {response}")
        return error_list

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Properties
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    address = Instrument.setting(
        "ADR %d",
        """Set the address of the power supply.

        Valid values are integers between 0 - 30 (inclusive).""",
        check_set_errors=True,
        validator=strict_discrete_set,
        values=range(0, 31)
    )

    remote = Instrument.control(
        "RMT?", "RMT %s",
        """Control the current remote operation of the power supply.

        Valid values are ``'LOC'`` for local mode, ``'REM'`` for remote mode,
        and ``'LLO'`` for local lockout mode.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=["LOC", "REM", "LLO"]
    )

    multidrop_capability = Instrument.measurement(
        "MDAV?",
        """Get whether the multi-drop option is available on the power supply.

        If return value is ``False``, the option is not available, if ``True`` it is available.

        Property is UNTESTED.
        """,
        cast=bool
    )

    master_slave_setting = Instrument.measurement(
        "MS?",
        """Get the master and slave settings.

        Possible master return values are 1, 2, 3, and 4. The slave value is 0.

        Property is UNTESTED.
        """
    )

    repeat = Instrument.measurement(
        "\\",
        """Measure the last command again.

        Returns output of the last command.
        """
    )

    id = Instrument.measurement(
        "IDN?",
        """Get the identity of the instrument.

        Returns a list of instrument manufacturer and model in the format: ``["LAMBDA", "GENX-Y"]``
        """
    )

    version = Instrument.measurement(
        "REV?",
        """Get the software version on instrument.

        Returns the software version as an ASCII string.
        """
    )

    serial = Instrument.measurement(
        "SN?",
        """Get the serial number of the instrument.

        Returns the serial number of of the instrument as an ASCII string.
        """
    )

    last_test_date = Instrument.measurement(
        "DATE?",
        """Get the date of the last test, possibly calibration date.

        Returns a string in the format: yyyy/mm/dd.
        """
    )

    voltage_setpoint = Instrument.control(
        "PV?", "PV %g",
        """Control the programmed (set) output voltage.""",
        check_set_errors=True,
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.01),
        values=[0, 40],
        dynamic=True
    )

    voltage = Instrument.measurement(
        "MV?",
        """Measure the actual output voltage."""
    )

    current_setpoint = Instrument.control(
        "PC?", "PC %g",
        """Control the programmed (set) output current.""",
        check_set_errors=True,
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.01),
        values=[0, 38],
        dynamic=True
    )

    current = Instrument.measurement(
        "MC?",
        """Measure the actual output current.

        Returns a float with five digits of precision.
        """
    )

    mode = Instrument.measurement(
        "MODE?",
        """Measure the output mode of the power supply.

        When power supply is on, the returned value will be either ``'CV'`` for
        control voltage or ``'CC'`` for or control current. If the power supply
        is off, the returned value will be ``'OFF'``.
        """
    )

    display = Instrument.measurement(
        "DVC?",
        """Get the displayed voltage and current.

        Returns a list of floating point numbers in the order of [ measured voltage,
        programmed voltage, measured current, programmed current, over voltage set point,
        under voltage set point ].
        """
    )

    status = Instrument.measurement(
        "STT?",
        """Get the power supply status.

        Returns a list in the order of [ actual voltage
        (MV), the programmed voltage (PV), the actual current (MC), the
        programmed current (PC), the status register (SR), and the fault
        register (FR) ].
        """
    )

    pass_filter = Instrument.control(
        "FILTER?", "FILTER %d",
        """Control the low pass filter frequency of the A to D converter
        for voltage and current measurement.

        Valid frequency values are 18, 23, or 46 Hz. Default value is 18 Hz.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values=[18, 23, 46]
    )

    output_enabled = Instrument.control(
        "OUT?", "OUT %s",
        """Control the output of the power supply.

        Valid values are ``True`` to turn output on and ``False`` to turn output off, shutting down
        any voltage or current.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    foldback_enabled = Instrument.control(
        "FLD?", "FLD %s",
        """Control the fold back protection of the power supply.

        Valid values are ``True`` to arm the fold back protection and ``False``
        to cancel the fold back protection.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    foldback_delay = Instrument.control(
        "FBD?", "FBD %g",
        """Control the fold back delay.

        Adds an additional delay to the standard fold back delay (250 ms) by
        multiplying the set value by 0.1. Valid values are integers between
        0 to 255.
        """,
        check_set_errors=True,
        validator=strict_range,
        values=[0, 255],
        cast=int
    )

    over_voltage = Instrument.control(
        "OVP?", "OVP %g",
        """Control the over voltage protection.
        """,
        check_set_errors=True,
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.01),
        values=[2, 44],
        dynamic=True
    )

    under_voltage = Instrument.control(
        "UVL?", "UVL %g",
        """Control the under voltage limit.

        Property is UNTESTED.
        """,
        check_set_errors=True,
        validator=lambda v, vs: strict_discrete_range(v, vs, step=0.01),
        values=[0, 38],
        dynamic=True
    )

    auto_restart_enabled = Instrument.control(
        "AST?", "AST %s",
        """Control the auto restart mode, which restores the power supply to the last
        output voltage and current settings with output enabled on startup.

        Valid values are ``True`` to restore output settings with output enabled on startup
        and ``False`` to disable restoration of settings and output disabled on startup.
        """,
        check_set_errors=True,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Methods
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def clear(self):
        """Clear FEVE and SEVE registers to zero."""
        self.write("CLS")
        self.check_errors()

    def reset(self):
        """Reset the instrument to default values."""
        self.write("RST")
        self.check_errors()

    def foldback_reset(self):
        """Reset the fold back delay to 0 s, restoring the standard 250 ms
        delay.

        Property is UNTESTED.
        """
        self.write("FDBRST")
        self.check_errors()

    def save(self):
        """Save current instrument settings."""
        self.write("SAV")
        self.check_errors()

    def recall(self):
        """Recall last saved instrument settings."""
        self.write("RCL")
        self.check_errors()

    def set_max_over_voltage(self):
        """Set the over voltage protection to the maximum level for the power
        supply.
        """
        self.write("OVM")
        self.check_errors()

    def ramp_to_current(self, target_current, steps=20, pause=0.2):
        """Ramps to a target current from the set current value over
        a certain number of linear steps, each separated by a pause duration.

        :param target_current: Target current in amps
        :param steps: Integer number of steps
        :param pause: Pause duration in seconds to wait between steps
        """

        currents = [round(i, 2) for i in np.linspace(self.current_setpoint,
                                                     target_current, steps)]
        for current in currents:
            self.current_setpoint = current
            sleep(pause)

    def shutdown(self):
        """Safety shutdown the power supply.

        Ramps the power supply down to zero current using the
        ``self.ramp_to_current(0.0)`` method and turns the output off.
        """
        log.info("Shutting down %s." % self.name)
        self.ramp_to_current(0.0)
        self.output_enabled = False
        super().shutdown()
