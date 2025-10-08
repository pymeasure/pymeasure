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

import logging
import time
import numpy as np

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_range
from pyvisa.util import from_binary_block

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class CTP10(SCPIMixin, Instrument):
    """Represents EXFO CTP10 vector analyzer instrument.

    The CTP10 is a tunable laser source and optical component test platform
    that can measure transmission and reflection characteristics.

    .. code-block:: python

        ctp = CTP10("TCPIP::192.168.1.100::10001::SOCKET")

        # Configure scan parameters
        ctp.start_wavelength_nm = 1520.0
        ctp.stop_wavelength_nm = 1580.0
        ctp.resolution_pm = 10.0
        ctp.sweep_speed_nmps = 50
        ctp.laser_power_dbm = 5.0

        # Start measurement
        ctp.initiate_sweep()
        ctp.wait_for_sweep_complete()

        # Get trace data
        trace = ctp.get_trace(channel=1)
    """

    # Module and trace type constants
    MODULE = 4
    TRACE_TYPE = 1
    LIVE_RAW_TRACE_TYPE = 11
    REF_RAW_TRACE_TYPE = 12

    CONDITION_LOOP_DELAY = 0.02

    def __init__(
        self,
        adapter,
        name="EXFO CTP10",
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            tcpip={
                "read_termination": "\r\n",
                "write_termination": "\r\n",
                "port": 10001,
            },
            gpib={
                "read_termination": "\n",
                "write_termination": "\n",
            },
            **kwargs,
        )

    # Sweep control properties --------------------------------------------------------

    start_wavelength_nm = Instrument.control(
        ":INIT:WAV:STAR?",
        ":INIT:WAV:STOP %gNM",
        """Control the sweep start wavelength (float in nm).""",
        validator=strict_range,
        values=[1520.0, 1630.0],
        get_process=lambda v: float(v.split(',')[0]) * 1e9,
    )

    stop_wavelength_nm = Instrument.control(
        ":INIT:WAV:STOP?",
        ":INIT:WAV:STOP %gNM",
        """Control the sweep stop wavelength (float in nm).""",
        validator=strict_range,
        values=[1520.0, 1630.0],
        get_process=lambda v: float(v.split(',')[0]) * 1e9,
    )

    resolution_pm = Instrument.control(
        ":INIT:WAV:SAMP?",
        ":INIT:WAV:SAMP %dPM",
        """Control the wavelength sampling resolution (int in pm).""",
        validator=strict_range,
        values=[1, 1000],
        get_process=lambda v: int(float(v.split(',')[0]) * 1e12),
    )

    sweep_speed_nmps = Instrument.control(
        ":INIT:TLS1:SPE?",
        ":INIT:TLS1:SPE %d",
        """Control the sweep speed (int in nm/s).""",
        validator=strict_range,
        values=[1, 100],
        get_process=lambda v: int(float(v.split('.')[0]) * 10),
    )

    laser_power_dbm = Instrument.control(
        ":INIT:TLS1:POW?",
        ":INIT:TLS1:POW %gDBM",
        """Control the laser output power (float in dBm).""",
        validator=strict_range,
        values=[-10.0, 10.0],
        get_process=lambda v: float(v.split(',')[0]),
    )

    condition_register = Instrument.measurement(
        ":STAT:OPER:COND?",
        """Get the operation condition register value (int).""",
        cast=int,
    )

    # Sweep methods -------------------------------------------------------------------

    def initiate_sweep(self):
        """Initiate a sweep measurement."""
        self.write(':INIT:STAB ON')
        self.write(':INIT:SMOD SING')
        self.write(':INIT')

    def wait_for_sweep_complete(self, condition_number=0, timeout=30.0):
        """Wait for sweep to complete by polling condition register.

        :param condition_number: Expected condition register value when complete (default 0).
        :param timeout: Maximum time to wait in seconds (default 30.0).
        :return: 0 if successful, -1 if timeout.
        :raises TimeoutError: If sweep does not complete within timeout.
        """
        time_start = time.time()
        while True:
            time.sleep(self.CONDITION_LOOP_DELAY)
            if self.condition_register == condition_number:
                return 0
            if time.time() - time_start > timeout:
                raise TimeoutError(f"Sweep did not complete within {timeout}s timeout")

    def check_errors(self, timeout=30):
        """Check for errors by waiting for condition register and querying error queue.

        :param timeout: Maximum time to wait for condition register (default 30).
        :return: 0 if no errors, error code otherwise.
        """
        try:
            self.wait_for_sweep_complete(condition_number=0, timeout=timeout)
            return self.query_error()
        except TimeoutError:
            return -1

    def query_error(self):
        """Query the error queue for any errors.

        :return: Error code (0 if no error).
        """
        error = self.ask(':SYST:ERR?').split(',')
        error_code = int(error[0])
        if error_code:
            log.error(f"Instrument error: {error}")
        return error_code

    def clear_errors(self):
        """Clear the error queue and status registers.

        :return: Error code after clearing.
        """
        self.write('*CLS')
        return self.query_error()

    # Trace retrieval methods ---------------------------------------------------------

    def get_trace_length(self, channel, module=None, trace_type=None):
        """Get the number of points in a trace.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :param trace_type: Trace type (default TRACE_TYPE constant).
        :return: Number of points in trace (int).
        """
        module = module or self.MODULE
        trace_type = trace_type or self.TRACE_TYPE
        return int(self.ask(f':TRAC:SENS{module}:CHAN{channel}:TYPE{trace_type}:DATA:LENG?'))

    def get_trace_resolution_pm(self, channel, module=None, trace_type=None):
        """Get the wavelength resolution of a trace.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :param trace_type: Trace type (default TRACE_TYPE constant).
        :return: Resolution in pm (float).
        """
        module = module or self.MODULE
        trace_type = trace_type or self.TRACE_TYPE
        return float(
            self.ask(f':TRAC:SENS{module}:CHAN{channel}:TYPE{trace_type}:DATA:SAMP?')
        ) * 1e12

    def get_trace_start_wavelength_nm(self, channel, module=None, trace_type=None):
        """Get the start wavelength of a trace.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :param trace_type: Trace type (default TRACE_TYPE constant).
        :return: Start wavelength in nm (float).
        """
        module = module or self.MODULE
        trace_type = trace_type or self.TRACE_TYPE
        return float(
            self.ask(f':TRAC:SENS{module}:CHAN{channel}:TYPE{trace_type}:DATA:STAR?')
        ) * 1e9

    def get_trace(self, channel, module=None, trace_type=None):
        """Get processed trace data.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :param trace_type: Trace type (default TRACE_TYPE constant).
        :return: Numpy array of trace data in dB.
        """
        module = module or self.MODULE
        trace_type = trace_type or self.TRACE_TYPE
        self.write(f':TRAC:SENS{module}:CHAN{channel}:TYPE{trace_type}:DATA? BIN,DB')
        return self._read_binary_trace()

    def get_live_trace(self, channel, module=None):
        """Get live raw trace data.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :return: Numpy array of live trace data.
        """
        module = module or self.MODULE
        return self.get_trace(channel, module, self.LIVE_RAW_TRACE_TYPE)

    def get_reference_trace(self, channel, module=None):
        """Get reference trace data.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :return: Numpy array of reference trace data.
        """
        module = module or self.MODULE
        return self.get_trace(channel, module, self.REF_RAW_TRACE_TYPE)

    def _read_binary_trace(self):
        """Read binary trace data from instrument.

        The instrument returns data in IEEE 488.2 binary block format:
        #<length_of_length><length><data>

        :return: Numpy array of float32 values in big-endian format.
        """
        # Read the '#' character and length digit
        header = self.read_bytes(2)
        length_of_length = int(chr(header[1]))

        # Read the length value
        length_bytes = self.read_bytes(length_of_length)
        data_length = int(length_bytes)

        # Read the actual data
        data_bytes = self.read_bytes(data_length)

        # Convert to numpy array (big-endian float32)
        return np.frombuffer(data_bytes, dtype=np.dtype('>f4'))

    # Calibration/Reference methods ---------------------------------------------------

    def create_reference(self, channel, module=None):
        """Create a reference trace for a channel.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :return: Error code.
        """
        module = module or self.MODULE
        self.write(f':REF:SENS{module}:CHAN{channel}:INIT')
        return self.check_errors()

    # Power measurement ---------------------------------------------------------------

    def get_power(self, channel, module=None):
        """Get the optical power measurement for a channel.

        :param channel: Channel number (1-based).
        :param module: Module number (default MODULE constant).
        :return: Power value as string (with units).
        """
        module = module or self.MODULE
        return self.ask(f':CTP:SENS{module}:CHAN{channel}:POW?')

    # Utility methods -----------------------------------------------------------------

    def get_wavelength_array(self, channel=None):
        """Generate wavelength array for trace data.

        :param channel: Channel number to get parameters from (default uses settings).
        :return: Numpy array of wavelength values in nm.
        """
        if channel is not None:
            start_nm = self.get_trace_start_wavelength_nm(channel)
            resolution_pm = self.get_trace_resolution_pm(channel)
            length = self.get_trace_length(channel)
        else:
            start_nm = self.start_wavelength_nm
            resolution_pm = self.resolution_pm
            stop_nm = self.stop_wavelength_nm
            length = int((stop_nm - start_nm) * 1000 / resolution_pm) + 1

        resolution_nm = resolution_pm / 1000.0
        return np.arange(length) * resolution_nm + start_nm
