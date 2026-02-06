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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
)


_FREQS_HZ = [
    100,
    120,
    400,
    1_000,
    4_000,
    10_000,
    40_000,
    50_000,
    75_000,
    100_000,
]  # Allowed frequencies in Hz
_RESIS_OHM = ["auto", 10, 100, 1_000, 10_000, 100_000]  # Allowed resistance ranges in Ohm
_LEVELS_MVRMS = [300, 600]  # Allowed levels in mVrms
_IMPA = ["r", "l", "c", "z", "auto"]  # Allowed main measurement parameters
_IMPB = ["x", "q", "d", "theta", "esr"]  # Allowed secondary measurement parameters


class LCR500(SCPIMixin, Instrument):
    """Voltcraft LCR-500 LCR Meter.

    Measures impedance, inductance, and capacitance with frequencies from
    100 Hz to 100 kHz and support for secondary parameters such as quality
    factor, reactance, and phase angle.

    The device communicates via USB with an RS-232 serial interface. It must
    be configured to use line feed (LF) as the termination character for both
    read and write operations.

    The following SCPI subsystems are implemented:
        - Frequency: Control the measurement frequency.
        - Function: Control measurement function, range, level, and circuit
          mode (series/parallel).
        - Fetch: Retrieve measurement results.

    :param adapter: A PyVISA resource name or adapter instance.
    :type adapter: str or Adapter
    :param str name: Name of the instrument instance.
    :param kwargs: Additional keyword arguments passed to the parent
        Instrument class.

    **Example usage:**

    .. code-block:: python

        from pymeasure.instruments.voltcraft import LCR500

        lcr = LCR500("ASRL3::INSTR")  # Connect using a VISA address
        lcr.frequency = 1000  # Set frequency to 1 kHz
        lcr.main_parameter = "c"  # Measure capacitance
        lcr.secondary_parameter = "q"  # Quality factor
        lcr.measurement_range = "auto"  # Use automatic range
        lcr.level = 300  # Use 300 mVrms test level
        lcr.equivalent_circuit_serial_enabled = True  # Series circuit mode

        primary, secondary, range_used = lcr.fetch()
        print(f"Capacitance: {primary} F, Q: {secondary}")
    """

    def __init__(self, adapter, name="Voltcraft LCR-500", **kwargs):
        super().__init__(adapter, name, write_termination="\n", read_termination="\n", **kwargs)
        self.adapter.connection.write_termination = "\n"
        self.adapter.connection.read_termination = "\n"

    go_to_local = Instrument.setting(
        "*GTL", """Set the device to local mode and disable key lock."""
    )

    # -- Frequency Subsystem --
    frequency = Instrument.control(
        "FREQ?",
        "FREQ %d",
        """Control the measurement frequency in Hz.

        :type: int

        Allowed values: 100, 120, 400, 1000, 4000, 10000, 40000, 50000,
        75000, 100000.
        """,
        validator=strict_discrete_set,
        values=_FREQS_HZ,
    )

    # -- Function Subsystem --
    main_parameter = Instrument.control(
        "FUNC:IMPA?",
        "FUNC:IMPA %s",
        """Control the main measurement parameter.

        :type: str

        Allowed values:

        * ``'r'``: Resistance
        * ``'l'``: Inductance
        * ``'c'``: Capacitance
        * ``'z'``: Impedance
        * ``'auto'``: Automatic
        """,
        validator=strict_discrete_set,
        values=_IMPA,
        get_process=lambda v: v.split("-")[-1],
    )

    secondary_parameter = Instrument.control(
        "FUNC:IMPB?",
        "FUNC:IMPB %s",
        """Control the secondary measurement parameter.

        :type: str

        Allowed values:

        * ``'x'``: Reactance
        * ``'q'``: Quality factor
        * ``'d'``: Dissipation factor
        * ``'theta'``: Phase angle
        * ``'esr'``: Equivalent series resistance
        """,
        validator=strict_discrete_set,
        values=_IMPB,
    )

    measurement_range = Instrument.control(
        "FUNC:RANG?",
        "FUNC:RANG %s",
        """Control the measurement range in Ohm.

        :type: str or int

        Allowed values: ``'auto'``, 10, 100, 1000, 10000, 100000.
        """,
        validator=strict_discrete_set,
        values=_RESIS_OHM,
    )

    level = Instrument.control(
        "FUNC:LEV?",
        "FUNC:LEV %d",
        """Control the measurement signal level in mVrms.

        :type: int

        Allowed values: 300, 600.
        """,
        validator=strict_discrete_set,
        values=_LEVELS_MVRMS,
    )

    equivalent_circuit_serial_enabled = Instrument.control(
        "FUNC:EQUI?",
        "FUNC:EQUI %s",
        """Control the equivalent circuit type.

        :type: bool

        * ``True``: Series equivalent circuit
        * ``False``: Parallel equivalent circuit
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ser", False: "pal"},
    )

    # -- Fetch Subsystem --
    fetch = Instrument.measurement(
        "FETC?",
        """Get a measurement result from the instrument.

        :returns: A list of ``[primary_value, secondary_value, range_used]``.
        :rtype: list[float]
        """,
    )
