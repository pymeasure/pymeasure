from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    truncated_range,
    truncated_discrete_set,
    strict_discrete_set,
)
from pymeasure.adapters import VISAAdapter
from .buffer import KeithleyBuffer

import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Keithley2260B(Instrument, KeithleyBuffer):
    """ Represents the Keithley 2260B Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    # .. code-block:: python

    #     source = Keithley2260B("GPIB::1")
    #     source.voltage = 1
    #     print(source.voltage)
    #     print(source.current)
    #     print(source.voltage)

    """

    enabled = Instrument.control(
        "OUTPut?", "OUTPut %d",
        """A boolean property that controls whether the source is enabled, takes
        values True or False. The convenience methods :meth:`~.Keithley6221.enable_source` and
        :meth:`~.Keithley6221.disable_source` can also be used.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    current = Instrument.control(
        ":SOUR:CURR?", ":SOUR:CURR %g",
        """ A floating point property that controls the source current
        in amps. """,
        # validator=truncated_range,
        # values=[-0.105, 0.105]
    )

    voltage = Instrument.control(
        ":SOUR:VOLT?", ":SOUR:VOLT %g",
        """ A floating point property that controls the source voltage
        in volts. """,
        # validator=truncated_range,
        # values=[-0.105, 0.105]
    )

    power = Instrument.measurement(
        ":MEAS:POW?",
        """ Reads the power the dc power supply is putting out. """
    )

    def __init__(self, adapter, **kwargs):
        # 'TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET'
        super().__init__(adapter, "Keithley 2260B DC Power Supply", **kwargs)
        # Set up data transfer format
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.config(
                is_binary=False, datatype="float32", converter="f", separator=","
            )
            self.adapter.connection.read_termination = "\r"

    @property
    def apply(self):
        return self.ask("apply?")

    @apply.setter
    def apply(self, voltage, current):
        self.write("apply %g,%g".format(voltage, current))