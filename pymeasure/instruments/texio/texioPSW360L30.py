from pymeasure.instruments import Instrument
from pymeasure.instruments.keithley.keithley2260B import Keithley2260B

import time
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TexioPSW360L30(Keithley2260B):
    r""" Represents the TEXIO PSW-360L30 Power Supply (minimal implementation)
    and provides a high-level interface for interacting with the instrument.

    For a connection through tcpip, the device only accepts
    connections at port 2268, which cannot be configured otherwise.
    example connection string: 'TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET'

    For a connection through USB on Linux, the kernel is going to create
    a /dev/ttyACMX device automatically. The serial connection properties are
    fixed at 9600–8-N-1.

    The read termination for this interface is Line-Feed \n.

    This driver was based off the Keithley2260B one.

    .. code-block:: python

        source = TexioPSW360L30("TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET")
        source.voltage = 1
        print(source.voltage)
        print(source.current)
        print(source.power)
        print(source.applied)
    """

    def __init__(self, adapter, **kwargs):
        Instrument.__init__(self,
                            adapter=adapter,
                            name="TEXIO PSW-360L30 Power Supply",
                            read_termination="\n",
                            **kwargs
                            )

    def check_errors(self):
        """ Logs any system errors reported by the instrument.
        """
        code, message = self.error
        while code != 0:
            t = time.time()
            log.info("TEXIO PSW-360L30 reported error: %d, %s" % (code, message))
            code, message = self.error
            if (time.time() - t) > 10:
                log.warning("Timed out for TEXIO PSW-360L30 error retrieval.")

    @property
    def output(self):
        """Same as "enabled" property"""
        return self.enabled

    @output.setter
    def output(self, value):
        """Same as "enabled" property"""
        self.enabled = value
