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

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RLASerChannel(Channel):
    """Represents a RLASer (Reference Laser) channel on the EXFO CTP10.

    Valid channel numbers: 1-10.

    In laser sharing mode, this query is not available on Distributed CTP10s.
    """

    idn = Channel.measurement(
        ":CTP:RLASer{ch}:IDN?",
        """Get the identification of the laser (str).

        Returns a comma-separated string with format: manufacturer,model,serial,firmware

        Example response: "EXFO,T100S-HP,0,6.06"

        Response components:
        - manufacturer: Manufacturer of the laser
        - model: Instrument model
        - serial: Instrument serial number
        - firmware: Instrument firmware version
        """,
    )

    power_dbm = Channel.control(
        ":CTP:RLASer{ch}:POWer?",
        ":CTP:RLASer{ch}:POWer %gDBM",
        """Control the laser output power in dBm (float).

        Sets the laser output power value in static control, or returns the power value
        set for the given laser in static control, or the actual laser power after an
        acquisition.

        Possible values depend on the laser specifications.

        On T500S, the maximum power is limited to 13 dBm. To avoid permanent damage
        to the CTP10 module detectors, do not apply a higher output power value than
        the maximum safe power specified for the detector to which the laser is connected
        (refer to Optical Measurement Specifications).

        The default unit is dBm.
        """,
    )

    power_mw = Channel.control(
        ":CTP:RLASer{ch}:POWer?",
        ":CTP:RLASer{ch}:POWer %gMW",
        """Control the laser output power in mW (float).

        Sets the laser output power value in static control, or returns the power value
        set for the given laser in static control, or the actual laser power after an
        acquisition.

        Possible values depend on the laser specifications.

        On T500S, the maximum power is limited to 13 dBm. To avoid permanent damage
        to the CTP10 module detectors, do not apply a higher output power value than
        the maximum safe power specified for the detector to which the laser is connected
        (refer to Optical Measurement Specifications).
        """,
    )

    power_state = Channel.control(
        ":CTP:RLASer{ch}:POWer:STATe?",
        ":CTP:RLASer{ch}:POWer:STATe %s",
        """Control the laser output state (bool or int).

        Enables or disables the laser output. This operation can take time,
        depending on the laser model.

        Set values:
        - False, 0, or 'OFF': disables the laser output
        - True, 1, or 'ON': enables the laser output

        :return: Laser output state (int): 0 if disabled, 1 if enabled.
        """,
        validator=lambda v, values: v,
        map_values=False,
        set_process=lambda v: 'ON' if v in (True, 1, '1', 'ON') else 'OFF',
        get_process=int,
    )

    wavelength_pm = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gPM",
        """Control the laser emission wavelength in picometers (float).

        Sets the laser emission wavelength (static control), or returns the wavelength
        set for the given laser in static control, or the actual laser wavelength after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
        get_process=lambda v: float(v) * 1e12,
    )

    wavelength_nm = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gNM",
        """Control the laser emission wavelength in nanometers (float).

        Sets the laser emission wavelength (static control), or returns the wavelength
        set for the given laser in static control, or the actual laser wavelength after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
        get_process=lambda v: float(v) * 1e9,
    )

    wavelength_m = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gM",
        """Control the laser emission wavelength in meters (float).

        Sets the laser emission wavelength (static control), or returns the wavelength
        set for the given laser in static control, or the actual laser wavelength after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
    )

    frequency_hz = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gHZ",
        """Control the laser emission frequency in Hz (float).

        Sets the laser emission frequency (static control), or returns the frequency
        set for the given laser in static control, or the actual laser frequency after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
    )

    frequency_ghz = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gGHZ",
        """Control the laser emission frequency in GHz (float).

        Sets the laser emission frequency (static control), or returns the frequency
        set for the given laser in static control, or the actual laser frequency after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
        get_process=lambda v: float(v) * 1e-9,
    )

    frequency_thz = Channel.control(
        ":CTP:RLASer{ch}:WAVelength?",
        ":CTP:RLASer{ch}:WAVelength %gTHZ",
        """Control the laser emission frequency in THz (float).

        Sets the laser emission frequency (static control), or returns the frequency
        set for the given laser in static control, or the actual laser frequency after
        an acquisition.

        The allowed units are: PM, NM, M, HZ, GHZ, THZ.
        The default unit is meter (M).
        """,
        get_process=lambda v: float(v) * 1e-12,
    )


class TLSChannel(Channel):
    """Represents a TLS (Tunable Laser Source) channel on the EXFO CTP10."""

    start_wavelength_nm = Channel.control(
        ":INIT:TLS{ch}:WAVelength:STARt?",
        ":INIT:TLS{ch}:WAVelength:STARt %gNM",
        """Control the TLS sweep start wavelength (float in nm).""",
        get_process=lambda v: float(v) * 1e9,
    )

    stop_wavelength_nm = Channel.control(
        ":INIT:TLS{ch}:WAVelength:STOP?",
        ":INIT:TLS{ch}:WAVelength:STOP %gNM",
        """Control the TLS sweep stop wavelength (float in nm).""",
        get_process=lambda v: float(v) * 1e9,
    )

    sweep_speed_nmps = Channel.control(
        ":INIT:TLS{ch}:SPEed?",
        ":INIT:TLS{ch}:SPEed %d",
        """Control the TLS sweep speed (int in nm/s).

        Allowed values depend on the laser model:
        - EXFO T100S-HP: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17, 18, 20,
          22, 25, 29, 33, 40, 50, 67, 100
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

    trigin = Channel.control(
        ":INIT:TLS{ch}:TRIGin?",
        ":INIT:TLS{ch}:TRIGin %d",
        """Control or query the electrical trigger input for Pulse trigger output.

        This sets the electrical trigger input to use for the given laser,
        for Pulse trigger output.

        Allowed values (int): 0 to 8
            0: No trigger input port is used
            1-8: TRIG IN port number (1 to 8 input ports)

        Note: This command does not apply to VIAVI mSWS-AISLS lasers.

        :return: Current trigger input setting (int, 0-8).

        Example:
            # Set to no trigger
            ctp.tls[1].trigin = 0

            # Set to use TRIG IN port 3
            ctp.tls[1].trigin = 3

            # Query current trigger setting
            trig = ctp.tls[1].trigin  # returns 0-8
        """,
        validator=strict_range,
        values=[0, 8],
        cast=int,
    )


class TraceChannel(Channel):
    """Base class for trace channels on the EXFO CTP10.

    The channel is identified by:
    - SENSe[1...20]: Module identification number (position in mainframe, left to right)
        * In Daisy chaining mode: positions 1-10 are Primary mainframe, 11-20 are Secondary
    - CHANnel[1...6]: Detector identification number (detector position on module, top to bottom)
        * Note: This number is not used for BR (back reflection) traces
    - TYPE[1...23]: Trace type number (depends on detector type)

    Note: Different detector types support different trace types (1-23).
    See instrument documentation for complete list.

    This base class provides common functionality for all trace types.
    Use the generic accessor on the instrument to obtain a trace channel:

        - ctp.trace(module, channel, type=1) for TF live trace (TYPE1)
        - ctp.trace(module, channel, type=11) for Raw Live trace (TYPE11)
        - ctp.trace(module, channel, type=12) for Raw Reference trace (TYPE12)
        - ctp.trace(module, channel, type=13) for Raw Quick Reference trace (TYPE13)

    Example:
        # Access TF live trace on module 4, channel 1
        trace_ch = ctp.trace(module=4, channel=1, type=1)

        # Read trace data (binary format recommended for speed)
        length = trace_ch.length
        wavelengths = trace_ch.get_data_x(unit='M', format='BIN')  # Returns wavelengths in meters
        powers = trace_ch.get_data_y(unit='DB', format='BIN')  # Returns power in dB

        # Access different trace type
        raw_live_trace = ctp.trace(module=4, channel=1, type=11)
        raw_live_powers = raw_live_trace.get_data_y(unit='DB', format='BIN')

        # Channel operations (independent of trace type)
        trace_ch.create_reference()  # Create reference for this channel
        power_dbm = trace_ch.power  # Get optical power in dBm (or mW per unit)
    """

    def __init__(self, parent, id=None, trace_type=1, **kwargs):
        """Initialize trace channel with module, channel, and trace type.

        :param tuple id: Tuple of (module, channel) or None for dynamic access.
            module (int): SENSe number 1-20 (module position in mainframe).
            channel (int): CHANnel number 1-6 (detector position on module).
        :param int trace_type: TYPE number 1-23 (depends on detector type).
        """
        # Accept tuple or None (for ChannelCreator pattern)
        if id is not None and not (isinstance(id, tuple) and len(id) == 2):
            raise ValueError("TraceChannel ID must be a tuple of (module, channel)")

        # Store module, channel, and trace type as separate attributes
        if id is not None:
            self.module, self.channel = id
        else:
            self.module, self.channel = None, None

        self.trace_type = trace_type

        # Pass the tuple as-is to parent
        super().__init__(parent, id, **kwargs)

    def insert_id(self, command):
        """Insert the channel ID (module, channel, type) into the command.

        Replaces {module}, {channel}, and {type} placeholders.
        """
        if self.id is None:
            return command
        return command.format(module=self.module, channel=self.channel, type=self.trace_type)

    length = Channel.measurement(
        ":TRACe:SENSe{module}:CHANnel{channel}:TYPE{type}:DATA:LENGth?",
        """Get the number of points in the trace (int).""",
        cast=int,
    )

    sampling_pm = Channel.measurement(
        ":TRACe:SENSe{module}:CHANnel{channel}:TYPE{type}:DATA:SAMPling?",
        """Get the wavelength sampling resolution in pm (float).""",
        get_process=lambda v: float(v) * 1e12,
    )

    start_wavelength_nm = Channel.measurement(
        ":TRACe:SENSe{module}:CHANnel{channel}:TYPE{type}:DATA:STARt?",
        """Get the start wavelength in nm (float).""",
        get_process=lambda v: float(v) * 1e9,
    )

    power = Channel.measurement(
        ":CTP:SENSe{module}:CHANnel{channel}:POWer?",
        """Get the optical power measurement for this detector channel (float).

        The unit (dBm or mW) depends on the unit setting configured with
        CTP:SENSe[1...10]:CHANnel[1...6]:UNIT:Y.

        Note: This query is not available on a PCM detector.

        On an IL RL OPM2 module:
        - Channel 3 returns the instant power measured on the TLS IN port
        - Channel 4 returns the back reflection value measured on the port

        On an IL PDL OPM2 module:
        - Channel 3 returns the instant power measured on the TLS IN port

        :return: Instant power measured on the detector (float in dBm or mW).

        Example:
            # Get power for module 2, channel 2
            power = ctp.trace(module=2, channel=2, type=1).power  # e.g. -3.1
        """,
    )

    spectral_unit = Channel.control(
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:X?",
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:X %s",
        """Control or query the spectral unit for this detector channel.

        Allowed values when setting:
            'WAV' or 0 or '0' : wavelength in nm
            'FREQ' or 1 or '1' : frequency in THz

        :return: Current spectral unit (int): 0 for wavelength (nm), 1 for frequency (THz).

        Example:
            # Set to wavelength (nm)
            ctp.trace(4, 1).spectral_unit = 'WAV'
            # Query current spectral unit
            u = ctp.trace(4, 1).spectral_unit  # returns 0 or 1
        """,
        validator=lambda v, values: v,
        map_values=False,
        get_process=lambda v: int(v),
        set_process=lambda v: (
            'WAV' if str(v).strip().upper() in {'0', 'WAV', 'WAVELENGTH', 'NM'}
            else 'FREQ' if str(v).strip().upper() in {'1', 'FREQ', 'FREQUENCY', 'THZ'}
            else str(v)
        ),
    )

    power_unit = Channel.control(
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:Y?",
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:Y %s",
        """Control or query the power/current unit for this detector channel.

        Allowed values when setting:
            'DBM' or 0 or '0' : power in dBm (default)
            'MW'  or 1 or '1' : power in mW

        :return: Current power unit (int): 0 for dBm, 1 for mW.

        Example:
            # Set power unit to mW
            ctp.trace(4, 2).power_unit = 'MW'
            # Query current power unit
            pu = ctp.trace(4, 2).power_unit  # returns 0 or 1
        """,
        validator=lambda v, values: v,
        map_values=False,
        get_process=lambda v: int(v),
        set_process=lambda v: (
            'DBM' if str(v).strip().upper() in {'0', 'DBM', 'DBMA'}
            else 'MW' if str(v).strip().upper() in {'1', 'MW', 'MA'}
            else str(v)
        ),
    )

    trigger = Channel.control(
        ":CTP:SENSe{module}:CHANnel{channel}:FUNCtion:TRIGGer?",
        ":CTP:SENSe{module}:CHANnel{channel}:FUNCtion:TRIGGer %d",
        """Control or query the incoming trigger for the logging function on this detector.

        This sets the trigger used for the logging function (power level data acquisition).

        Allowed values (int): 0 to 8
            0: Software trigger - data acquisition triggered by CTP:FUNCtion:STATe command
            1-8: TRIG IN port number - detectors wait for trigger signal from specified port
                 (acquisition starts when voltage level at port is "high")

        Note: For more details, see the instrument manual section on
        "Performing Power Level Data Acquisition".

        :return: Current trigger setting (int, 0-8).

        Example:
            # Set to software trigger
            ctp.trace(module=4, channel=3).trigger = 0

            # Set to use TRIG IN port 4
            ctp.trace(module=6, channel=1).trigger = 4

            # Query current trigger setting
            trig = ctp.trace(module=4, channel=3).trigger  # returns 0-8
        """,
        validator=strict_range,
        values=[0, 8],
        cast=int,
    )

    def get_data_x(self, unit='M', format='BIN'):
        """Get trace X-axis data (wavelength or frequency).

        :param str unit: Data unit - 'M' for meters (wavelength), 'HZ' for Hertz (frequency).
            Default 'M'.
        :param str format: Data format - 'BIN' for binary or 'ASCII' for ASCII.
            Default 'BIN' for faster transfer of large datasets.
        :return: Numpy array of trace data (binary) or list (ASCII).
        """
        if format.upper() == 'BIN':
            # Binary format - query with format and unit parameters after ?
            # X-axis data (wavelength/frequency) uses float64 (8 bytes per value)
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{self.trace_type}:DATA:X? BIN,{unit}")
            self.write(cmd)
            return self._read_binary_trace(dtype='>f8')  # 64-bit float, big-endian
        else:
            # ASCII format
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{self.trace_type}:DATA:X? ASCII,{unit}")
            return self.values(cmd)

    def get_data_y(self, unit='DB', format='BIN'):
        """Get trace Y-axis data.

        :param str unit: Data unit - 'DB' for dB or 'Y' for linear (default 'DB').
        :param str format: Data format - 'BIN' for binary or 'ASCII' for ASCII
            (default 'BIN').
        :return: Numpy array of trace data (binary) or list (ASCII).
        """
        if format.upper() == 'BIN':
            # Binary format - query with format and unit parameters after ?
            # Y-axis data (power) uses float32 (4 bytes per value)
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{self.trace_type}:DATA? BIN,{unit}")
            self.write(cmd)
            return self._read_binary_trace(dtype='>f4')  # 32-bit float, big-endian
        else:
            # ASCII format
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{self.trace_type}:DATA? ASCII,{unit}")
            return self.values(cmd)

    def save(self):
        """Save trace data to internal memory (CSV format only)."""
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{self.trace_type}:SAVE"
        self.write(cmd)

    def _read_binary_trace(self, dtype='>f4'):
        """Read binary trace data from instrument.

        The instrument returns data in IEEE 488.2 binary block format:
        #<length_of_length><length><data>

        :param dtype: Numpy dtype for the data. Default is '>f4' (big-endian float32).
            Use '>f8' for float64 (X-axis wavelength data).
        :return: Numpy array of values in the specified dtype.
        """
        import numpy as np

        # Read the '#' character and length digit (e.g., '#7')
        header = self.read_bytes(2)
        length_of_length = int(chr(header[1]))

        # Read the length value (e.g., '3760004' for 940001 floats)
        length_bytes = self.read_bytes(length_of_length)
        data_length = int(length_bytes)

        # Read the actual binary data
        # This is the large data transfer that needs adequate timeout
        data_bytes = self.read_bytes(data_length)

        # Convert to numpy array with specified dtype
        return np.frombuffer(data_bytes, dtype=np.dtype(dtype))

    def create_reference(self):
        """Create a reference trace for this channel.

        This operation is independent of the trace type.
        """
        cmd = f':REFerence:SENSe{self.module}:CHANnel{self.channel}:INITiate'
        self.write(cmd)


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

        # Get reference laser identification (up to 10 lasers)
        laser_id = ctp.rlaser[2].idn  # Returns "EXFO,T100S-HP,0,6.06"

        # Set reference laser power
        ctp.rlaser[2].power_dbm = 1.5  # Set power to 1.5 dBm
        current_power = ctp.rlaser[2].power_dbm  # Read current power setting

        # Enable/disable laser output
        ctp.rlaser[2].power_state = True  # Enable laser output
        ctp.rlaser[2].power_state = 'ON'  # Alternative: use 'ON'/'OFF'
        is_enabled = ctp.rlaser[2].power_state  # Returns True/False

        # Set laser wavelength (multiple units available)
        ctp.rlaser[2].wavelength_nm = 1550.0  # Set to 1550 nm
        current_wavelength = ctp.rlaser[2].wavelength_nm  # Read wavelength in nm
        # Alternative units: wavelength_pm, wavelength_m, frequency_hz, frequency_ghz, frequency_thz

        # Start measurement
        ctp.initiate_sweep()
        ctp.wait_for_sweep_complete()

        # Access TF live trace data (module=4, channel=1)
        tf_trace = ctp.trace(module=4, channel=1, type=1)
        length = tf_trace.length
        wavelengths = tf_trace.get_data_x(unit='M', format='BIN')  # Returns wavelengths in meters
        powers = tf_trace.get_data_y(unit='DB', format='BIN')  # Returns power in dB

        # Access different trace types
        raw_live_trace = ctp.trace(module=4, channel=1, type=11)
        raw_live_powers = raw_live_trace.get_data_y()

        raw_ref_trace = ctp.trace(module=4, channel=1, type=12)
        raw_ref_powers = raw_ref_trace.get_data_y()
    """

    # TLS Channel creators (up to 4 channels)
    tls1 = Instrument.ChannelCreator(TLSChannel, 1)
    tls2 = Instrument.ChannelCreator(TLSChannel, 2)
    tls3 = Instrument.ChannelCreator(TLSChannel, 3)
    tls4 = Instrument.ChannelCreator(TLSChannel, 4)

    # RLASer Channel creator (up to 10 channels)
    rlaser = Instrument.MultiChannelCreator(RLASerChannel, list(range(1, 11)))

    # Generic trace accessor ---------------------------------------------------------
    def trace(self, module: int, channel: int, type: int = 1) -> TraceChannel:
        """Return a TraceChannel for given module, channel and TYPE.

        :param int module: SENSe number 1-20 (module position in mainframe).
        :param int channel: CHANnel number 1-6 (detector position on module).
        :param int type: Trace TYPE number 1-23 (depends on detector type).
        :return: TraceChannel instance bound to the given identifiers.
        """
        if not (1 <= int(module) <= 20):
            raise ValueError("module must be in 1..20")
        if not (1 <= int(channel) <= 6):
            raise ValueError("channel must be in 1..6")
        if not (1 <= int(type) <= 23):
            raise ValueError("type must be in 1..23")
        return TraceChannel(self, (int(module), int(channel)), trace_type=int(type))

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

        :param int output: Activation state of the laser after scan stop.
            0 or OFF disables the laser optical output when the scan stops.
            1 or ON (default) sets the laser optical output to stay enabled after scan stop.
        :param float duration: Stabilization time in seconds (range 0 to 60, default 0).
            Period of time during which the laser stabilizes before starting acquisition.
        :return: Tuple of (output, duration) when queried.

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

        :return: Condition register value (0-65535, int)
        """,
        cast=int,
    )

    sweep_complete = Instrument.measurement(
        ":STATus:OPERation:CONDition?",
        """Get the completion status of the sweep (bool).

        :return: Sweep status (bool): True if complete, False if scanning in progress.
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

    def wait_for_sweep_complete(self, should_stop=lambda: False):
        """Wait until the sweep completes or until ``should_stop`` returns True.

        :param callable should_stop: Optional function that returns True to stop waiting.
        :return: True when sweep completed, False if stopped by should_stop (bool).
        """
        # Poll the instrument until sweep_complete is True or should_stop()
        while not self.sweep_complete:
            if should_stop():
                return False

        return True

    def check_errors(self):
        """Check for errors in the instrument error queue.

        This method queries the SCPI error queue and logs any errors found.
        Uses the inherited check_errors implementation from SCPIMixin.
        """
        super().check_errors()
