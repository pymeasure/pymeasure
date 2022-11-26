import logging
import time

from pymeasure.instruments.keithley.keithley2260B import Keithley2260B

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

    This driver inherits from the Keithley2260B one. All instructions
    implemented in the Keithley 2260B driver are also available for the
    TEXIO PSW-360L30 power supply.

    The only addition is the "output" property that is just an alias for
    the "enabled" property of the Keithley 2260B. Calling the output switch
    "enabled" is confusing because it is not clear if the whole device is
    enabled/disable or only the output.

    .. code-block:: python

        source = TexioPSW360L30("TCPIP::xxx.xxx.xxx.xxx::2268::SOCKET")
        source.voltage = 1
        print(source.voltage)
        print(source.current)
        print(source.power)
        print(source.applied)
    """

    def __init__(self, adapter, **kwargs):
        kwargs['name'] = "TEXIO PSW-360L30 Power Supply"
        super().__init__(adapter, **kwargs)

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
