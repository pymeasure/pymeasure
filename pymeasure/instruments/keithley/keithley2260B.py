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

    #     meter = Keithley2000("GPIB::1")
    #     meter.measure_voltage()
    #     print(meter.voltage)

    """

    def __init__(self, adapter, **kwargs):
        # 'TCPIP::192.168.2.104::1865::SOCKET'
        # 'TCPIP::192.168.3.102::2268::SOCKET'
        # 'TCPIP::192.168.3.5::2268::SOCKET'
        super().__init__(adapter, "Keithley 2260B DC Power Supply", **kwargs)
        # Set up data transfer format
        if isinstance(self.adapter, VISAAdapter):
            self.adapter.config(
                is_binary=False, datatype="float32", converter="f", separator=","
            )
