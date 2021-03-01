from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2260B(Instrument):
    """ Represents the Keithley 2260B Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    For a connection through tcpip, the socket is hardcoded to 2268,
        example connection string: 'TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET'
        the read termination is \n

    .. code-block:: python

        source = Keithley2260B("GPIB::1")
        source.voltage = 1
        print(source.voltage)
        print(source.current)
        print(source.power)
        print(source.applied)

    """

    enabled = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False (1 or 0). """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR %g",
        """ A floating point property that controls the source current
        in amps. The allowed range is not fixed. """,
    )

    voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """ A floating point property that controls the source voltage
        in volts. The allowed range is not fixed. """,
    )

    power = Instrument.measurement(
        ":MEAS:POW?",
        """ Reads the power (in watts) the dc power supply is putting out.  """
    )

    applied = Instrument.control(
        ":APPly?",
        ":APPly %g,%g",
        """Simultaneous control of voltage (volts) and current (amps).
        Values need to be supplied as tuple of (voltage, current)""",
    )
