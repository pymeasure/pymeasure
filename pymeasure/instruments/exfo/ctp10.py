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
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import strict_range
from pyvisa.util import from_binary_block

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TLSChannel(Channel):
    """Represents a TLS (Tunable Laser Source) channel on the EXFO CTP10."""

    start_wavelength_nm = Channel.control(
        ":INIT:TLS{ch}:WAV:STAR?",
        ":INIT:TLS{ch}:WAV:STAR %gNM",
        """Control the TLS sweep start wavelength (float in nm).""",
        get_process=lambda v: float(v) * 1e9,
    )

    stop_wavelength_nm = Channel.control(
        ":INIT:TLS{ch}:WAV:STOP?",
        ":INIT:TLS{ch}:WAV:STOP %gNM",
        """Control the TLS sweep stop wavelength (float in nm).""",
        get_process=lambda v: float(v) * 1e9,
    )

    sweep_speed_nmps = Channel.control(
        ":INIT:TLS{ch}:SPEed?",
        ":INIT:TLS{ch}:SPEed %d",
        """Control the TLS sweep speed (int in nm/s).

        Allowed values depend on the laser model:
        - EXFO T100S-HP: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20, 22, 25, 29, 33, 40, 50, 67, 100
        - VIAVI mSWS-AISLS: 5 to 100
        - T200S: 10, 20, 50, 100, 200 (depends on laser model)
        - T500S: 10, 20, 50, 100, 200 (depends on laser model)
        """,
    )

    laser_power_dbm = Channel.control(
        ":INIT:TLS{ch}:POWer?",
        ":INIT:TLS{ch}:POWer %gDBM",
        """Control the TLS laser output power in dBm (float).

        The allowed range depends on the laser model.
        Common range: -10.0 to 10.0 dBm.
        """,
        validator=strict_range,
        values=[-10.0, 10.0],
    )

    laser_power_mw = Channel.control(
        ":INIT:TLS{ch}:POWer?",
        ":INIT:TLS{ch}:POWer %gMW",
        """Control the TLS laser output power in milliwatts (float).

        The allowed range depends on the laser model.
        Common range: 0.1 to 10.0 mW.
        """,
        validator=strict_range,
        values=[0.1, 10.0],
    )


class TraceChannel(Channel):
    """Represents a trace channel on the EXFO CTP10.

    The channel is identified by:
    - SENSe[1...20]: Module identification number (position in mainframe, left to right)
        * In Daisy chaining mode: positions 1-10 are Primary mainframe, 11-20 are Secondary
    - CHANnel[1...6]: Detector identification number (detector position on module, top to bottom)
        * Note: This number is not used for BR (back reflection) traces

    Trace types are handled internally:
        * Processed trace (TYPE=1)
        * Raw Live trace (TYPE=11)
        * Raw Reference trace (TYPE=12)
        * Raw Quick Reference trace (TYPE=13)

    Access trace channels via: ctp.trace[module, channel]

    Example:
        trace_ch = ctp.trace[4, 1]  # Module 4, detector 1

        # Read processed trace (default)
        length = trace_ch.length
        wavelengths = trace_ch.get_wavelength_array()
        powers = trace_ch.get_data_y()

        # Access different trace types
        live_data = trace_ch.get_data_y(trace_type='live')
        ref_data = trace_ch.get_data_y(trace_type='reference')

        # Channel operations
        trace_ch.create_reference()  # Create reference for this channel
        power = trace_ch.get_power()  # Get optical power for this channel

        # Save trace
        trace_ch.save()
    """

    # Trace type definitions (internal)
    _TRACE_TYPES = {
        'processed': 1,
        'live': 11,
        'reference': 12,
        'quick_reference': 13,
    }

    def __init__(self, parent, id=None, **kwargs):
        """Initialize trace channel with module and channel.

        :param id: Tuple of (module, channel) or None for dynamic access
            - module (int): SENSe number 1-20 (module position in mainframe)
            - channel (int): CHANnel number 1-6 (detector position on module)
        """
        # Accept tuple or None (for ChannelCreator pattern)
        if id is not None and not (isinstance(id, tuple) and len(id) == 2):
            raise ValueError("TraceChannel ID must be a tuple of (module, channel)")

        # Store module and channel as separate attributes for easy access
        if id is not None:
            self.module, self.channel = id
        else:
            self.module, self.channel = None, None

        # Pass the tuple as-is to parent
        super().__init__(parent, id, **kwargs)

    def insert_id(self, command):
        """Insert the channel ID (module, channel) into the command.

        Replaces {ch} placeholder. For commands with separate module/channel,
        use string formatting with self.module and self.channel directly.
        """
        if self.id is None:
            return command

        # Standard Channel behavior - replace {ch} with the ID
        # But our commands use self.module and self.channel directly in methods
        return command.format(ch=self.id)

    @property
    def length(self):
        """Get the number of points in the processed trace (int)."""
        # SCPI format: :TRACe:SENSe[module]:CHANnel[channel]:TYPE[type]:DATA:LENGth?
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE1:DATA:LENGth?"
        return int(self.values(cmd)[0])

    @property
    def sampling_pm(self):
        """Get the wavelength sampling resolution in pm (float) for the processed trace."""
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE1:DATA:SAMPling?"
        return float(self.values(cmd)[0]) * 1e12

    @property
    def start_wavelength_nm(self):
        """Get the start wavelength in nm (float) for the processed trace."""
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE1:DATA:STARt?"
        return float(self.values(cmd)[0]) * 1e9

    def get_data_x(self, trace_type='processed'):
        """Get trace X-axis data (wavelength) in immediate ASCII format.

        :param trace_type: Type of trace - 'processed' (default), 'live', 'reference', 'quick_reference'.
        :return: List of wavelength values.
        """
        type_num = self._TRACE_TYPES[trace_type]
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{type_num}:DATA:X[:IMMediate]?"
        return self.values(cmd)

    def get_data_y(self, unit='DB', format='BIN', trace_type='processed'):
        """Get trace Y-axis data.

        :param unit: Data unit - 'DB' for dB or 'Y' for linear (default 'DB').
        :param format: Data format - 'BIN' for binary or 'ASCII' for ASCII (default 'BIN').
        :param trace_type: Type of trace - 'processed' (default), 'live', 'reference', 'quick_reference'.
        :return: Numpy array of trace data (binary) or list (ASCII).
        """
        type_num = self._TRACE_TYPES[trace_type]

        if format.upper() == 'BIN':
            # Binary format - query with format and unit parameters after ?
            cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{type_num}:DATA? BIN,{unit}"
            self.write(cmd)
            return self._read_binary_trace()
        else:
            # ASCII format
            cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{type_num}:DATA? ASCII,{unit}"
            return self.values(cmd)

    def save(self, trace_type='processed'):
        """Save trace data to internal memory (CSV format only).

        :param trace_type: Type of trace - 'processed' (default), 'live', 'reference', 'quick_reference'.
        """
        type_num = self._TRACE_TYPES[trace_type]
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{type_num}:SAVE"
        self.write(cmd)

    def get_wavelength_array(self):
        """Generate wavelength array for this trace.

        :return: Numpy array of wavelength values in nm.
        """
        start_nm = self.start_wavelength_nm
        resolution_pm = self.sampling_pm
        length = self.length
        resolution_nm = resolution_pm / 1000.0
        return np.arange(length) * resolution_nm + start_nm

    def _read_binary_trace(self):
        """Read binary trace data from instrument.

        The instrument returns data in IEEE 488.2 binary block format:
        #<length_of_length><length><data>

        Uses the same approach as the colleague's working code.

        :return: Numpy array of float32 values in big-endian format.
        """
        # Read the '#' character and length digit (e.g., '#7')
        header = self.read_bytes(2)
        length_of_length = int(chr(header[1]))

        # Read the length value (e.g., '3760004' for 940001 floats)
        length_bytes = self.read_bytes(length_of_length)
        data_length = int(length_bytes)

        # Read the actual binary data
        # This is the large data transfer that needs adequate timeout
        data_bytes = self.read_bytes(data_length)

        # Convert to numpy array (big-endian float32)
        return np.frombuffer(data_bytes, dtype=np.dtype('>f4'))

    def create_reference(self):
        """Create a reference trace for this channel.

        This operation is independent of the trace type.
        """
        cmd = f':REF:SENS{self.module}:CHAN{self.channel}:INIT'
        self.write(cmd)

    def get_power(self):
        """Get the optical power measurement for this channel.

        This operation is independent of the trace type.

        :return: Power value as string (with units).
        """
        cmd = f':CTP:SENS{self.module}:CHAN{self.channel}:POW?'
        return self.ask(cmd)


class CTP10(SCPIMixin, Instrument):
    """Represents EXFO CTP10 vector analyzer instrument.

    The CTP10 is a tunable laser source and optical component test platform
    that can measure transmission and reflection characteristics. It supports
    up to 4 TLS (Tunable Laser Source) channels.

    .. code-block:: python

        ctp = CTP10("TCPIP::192.168.1.37::5025::SOCKET")

        # Configure global resolution
        ctp.resolution_pm = 10.0

        # Configure TLS channel 1 wavelengths and power
        ctp.tls1.start_wavelength_nm = 1520.0
        ctp.tls1.stop_wavelength_nm = 1580.0
        ctp.tls1.sweep_speed_nmps = 50
        ctp.tls1.laser_power_dbm = 5.0

        # Start measurement
        ctp.initiate_sweep()
        ctp.wait_for_sweep_complete()

        # Access trace data using trace channel (module=4, channel=1)
        trace_ch = ctp.trace[4, 1]
        length = trace_ch.length
        wavelengths = trace_ch.get_wavelength_array()

        # Get processed trace (default)
        powers = trace_ch.get_data_y(unit='DB')

        # Or get different trace types
        live_powers = trace_ch.get_data_y(trace_type='live')
        ref_powers = trace_ch.get_data_y(trace_type='reference')
    """

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
            },
            gpib={
                "read_termination": "\n",
                "write_termination": "\n",
            },
            **kwargs,
        )

    # TLS Channel creators (up to 4 channels)
    tls1 = Instrument.ChannelCreator(TLSChannel, 1)
    tls2 = Instrument.ChannelCreator(TLSChannel, 2)
    tls3 = Instrument.ChannelCreator(TLSChannel, 3)
    tls4 = Instrument.ChannelCreator(TLSChannel, 4)

    # Trace Channel creator for all valid (module, channel) combinations
    # Modules: 1-20, Channels: 1-6
    trace = Instrument.MultiChannelCreator(
        TraceChannel,
        [(m, c) for m in range(1, 21) for c in range(1, 7)]
    )

    # Global sweep control properties -------------------------------------------------

    resolution_pm = Instrument.control(
        ":INIT:WAVelength:SAMPling?",
        ":INIT:WAVelength:SAMPling %gPM",
        """Control the wavelength sampling resolution (float in pm).

        The scan sampling value is in picometer. Response from query is in meters.

        Possible values:
        - Standard sampling: integers in the range 1 to 250 pm
        - High resolution sampling: 0.5, 0.2, 0.1, 0.05, or 0.02 pm
          (Note: High resolution sampling reduces possible sweep span and laser speed)
        """,
        get_process=lambda v: float(v) * 1e12,
    )

    stabilization = Instrument.control(
        ":INIT:STABilization?",
        ":INIT:STABilization %d,%g",
        """Control the output settings of the lasers used for the scan.

        Format: stabilization = (output, duration)

        Parameters:
        - output (int): Activation state of the laser after scan stop
            - 0 or OFF: disables the laser optical output when the scan stops
            - 1 or ON (default): sets the laser optical output to stay enabled after scan stop
        - duration (float): Stabilization time in seconds (range 0 to 60, default 0)
            Period of time during which the laser stabilizes before starting acquisition

        Returns:
            Tuple of (output, duration) when queried

        Example:
            ctp.stabilization = (1, 12.3)  # Set: Keep laser on, 12.3s stabilization
            output, duration = ctp.stabilization  # Get: returns (1, 5.6) for example
        """,
    )

    condition_register = Instrument.measurement(
        ":STATus:OPERation:CONDition?",
        """Get the Operational Status Condition Register value.

        Returns a unique integer in the range 0 to 65535, which represents
        the bit values of the Operational Status Condition Register.

        The zero value indicates the idle state.

        Bit meanings (register value is sum of active bits):
        - Bit 0 (weight 1): Zeroing
        - Bit 1 (weight 2): Calibrating
        - Bit 2 (weight 4): Scanning
        - Bit 3 (weight 8): Analyzing
        - Bit 4 (weight 16): Aborting
        - Bit 5 (weight 32): Armed
        - Bit 6 (weight 64): Referencing
        - Bit 7 (weight 128): Quick referencing
        - Bit 8 (weight 256): Waiting for Controller CTP10
        - Bit 9 (weight 512): Updating setup from Controller CTP10
        - Bit 10 (weight 1024): Updating setup for Daisy chaining
        - Bit 11 (weight 2048): Laser referencing
        - Bit 12 (weight 4096): Loading/Saving
        - Bits 13-15: Not used

        Returns:
            int: Condition register value (0-65535)
        """,
        cast=int,
    )

    sweep_complete = Instrument.measurement(
        ":STATus:OPERation:CONDition?",
        """Get the completion status of the sweep (bool).

        Returns True if sweep is complete (bit 2 Scanning is not set),
        False if scanning is in progress.
        """,
        get_process=lambda x: not bool(int(x) & 4),  # Check if bit 2 (weight 4) is NOT set
    )

    # Sweep methods -------------------------------------------------------------------

    def initiate_sweep(self):
        """Initiate a sweep measurement with current parameters.

        This command performs a scan with the current parameters.
        The scan can be aborted with the :ABORt command.
        When executed, bit 2 "Scanning" is set in the Operational Status Condition Register.
        """
        self.write(':INITiate:IMMediate')

    def wait_for_sweep_complete(self, should_stop=lambda: False, timeout=60.0, delay=0.02):
        """Block the program, waiting for the sweep to complete.

        :param should_stop: Optional function that returns True to stop waiting.
        :param timeout: Maximum waiting time in seconds (default 60.0).
        :param delay: Delay between checks for sweep completion in seconds (default 0.02).
        :return: True when sweep completed, False if stopped by should_stop.
        :raises TimeoutError: If the sweep does not complete within the timeout period.
        """
        t0 = time.time()

        while not self.sweep_complete:
            if should_stop():
                return False

            if time.time() - t0 > timeout:
                raise TimeoutError(f"Sweep did not complete within {timeout}s timeout")

            time.sleep(delay)

        return True

    def check_errors(self):
        """Check for errors in the instrument error queue.

        This method queries the SCPI error queue and logs any errors found.
        Uses the inherited check_errors implementation from SCPIMixin.
        """
        super().check_errors()
