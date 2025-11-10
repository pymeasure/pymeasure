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


class DetectorChannel(Channel):
    """Represents a detector channel on the EXFO CTP10.

    A detector channel corresponds to a physical detector on a module and provides
    access to both detector-level operations (power, trigger, units, references) and
    trace data retrieval for specific trace types.

    The channel is identified by:
    - SENSe[1...20]: Module identification number (position in mainframe, left to right)
        * In Daisy chaining mode: positions 1-10 are Primary mainframe, 11-20 are Secondary
    - CHANnel[1...6]: Detector identification number (detector position on module, top to bottom)

    Trace types (TYPE parameter):
    - TYPE1: TF live trace (Transmission Function)
    - TYPE11: Raw Live trace
    - TYPE12: Raw Reference trace
    - TYPE13: Raw Quick Reference trace
    - See instrument documentation for complete list (1-23)

    Example:
        # Access detector on module 4, channel 1
        detector = ctp.detector(module=4, channel=1)

        # Detector-level operations
        detector.power_unit = 'DBM'  # Set unit to dBm
        power_dbm = detector.power  # Get optical power
        detector.trigger = 0  # Set software trigger
        detector.create_reference()  # Create reference

        # Read trace data for TF live trace (TYPE1)
        length = detector.length(trace_type=1)
        wavelengths = detector.get_data_x(trace_type=1, unit='M', format='BIN')
        powers = detector.get_data_y(trace_type=1, unit='DB', format='BIN')

        # Read Raw Live trace (TYPE11)
        raw_powers = detector.get_data_y(trace_type=11, unit='DB', format='BIN')

        # Save trace data
        detector.save(trace_type=1)
    """

    def __init__(self, parent, id=None, **kwargs):
        """Initialize detector channel with module and channel.

        :param tuple id: Tuple of (module, channel) or None for dynamic access.
            module (int): SENSe number 1-20 (module position in mainframe).
            channel (int): CHANnel number 1-6 (detector position on module).
        """
        # Accept tuple or None (for ChannelCreator pattern)
        if id is not None and not (isinstance(id, tuple) and len(id) == 2):
            raise ValueError("DetectorChannel ID must be a tuple of (module, channel)")

        # Store module and channel as separate attributes
        if id is not None:
            self.module, self.channel = id
        else:
            self.module, self.channel = None, None

        # Pass the tuple as-is to parent
        super().__init__(parent, id, **kwargs)

    def insert_id(self, command):
        """Insert the channel ID (module, channel) into the command.

        Replaces {module} and {channel} placeholders.
        """
        if self.id is None:
            return command
        return command.format(module=self.module, channel=self.channel)

    # Detector-level properties -------------------------------------------------------

    power = Channel.measurement(
        ":CTP:SENSe{module}:CHANnel{channel}:POWer?",
        """Get the optical power measurement for this detector channel (float).

        The unit (dBm or mW) depends on the unit setting configured with power_unit.

        Note: This query is not available on a PCM detector.

        On an IL RL OPM2 module:
        - Channel 3 returns the instant power measured on the TLS IN port
        - Channel 4 returns the back reflection value measured on the port

        On an IL PDL OPM2 module:
        - Channel 3 returns the instant power measured on the TLS IN port

        :return: Instant power measured on the detector (float in dBm or mW).

        Example:
            detector = ctp.detector(module=2, channel=2)
            power = detector.power  # e.g. -3.1
        """,
    )

    spectral_unit = Channel.control(
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:X?",
        ":CTP:SENSe{module}:CHANnel{channel}:UNIT:X %s",
        """Control or query the spectral unit for this detector channel.

        Allowed values when setting:
            'WAV' or 0 or '0' : wavelength in nm
            'FREQ' or 1 or '1' : frequency in THz

        :return: Current spectral unit (str): 'NM' for wavelength (nm), 'THz' for frequency.

        Example:
            detector.spectral_unit = 'WAV'      # instrument command uses WAV
            u = detector.spectral_unit          # returns 'NM'
            detector.spectral_unit = 'FREQ'
            u2 = detector.spectral_unit         # returns 'THz'
        """,
        validator=lambda v, values: v,
        map_values=False,
        cast=str,
        # Map instrument query response (0/1 or WAV/FREQ) to human readable 'NM'/'THz'
        get_process=lambda v: (
            'NM' if str(v).strip().upper() in {'0', 'WAV'} else
            'THz' if str(v).strip().upper() in {'1', 'FREQ'} else str(v)
        ),
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

        :return: Current power unit (str): 'dBm' or 'mW'.

        Example:
            detector.power_unit = 'DBM'   # instrument command uses DBM
            pu = detector.power_unit      # returns 'dBm'
            detector.power_unit = 'MW'
            pu2 = detector.power_unit     # returns 'mW'
        """,
        validator=lambda v, values: v,
        map_values=False,
        cast=str,
        # Map instrument query response (0/1 or DBM/MW) to 'dBm'/'mW'
        get_process=lambda v: (
            'dBm' if str(v).strip().upper() in {'0', 'DBM', 'DBMA'} else
            'mW' if str(v).strip().upper() in {'1', 'MW', 'MA'} else str(v)
        ),
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
            detector.trigger = 0  # software trigger
            detector.trigger = 4  # use TRIG IN port 4
            trig = detector.trigger  # returns 0-8
        """,
        validator=strict_range,
        values=[0, 8],
        cast=int,
    )

    def create_reference(self):
        """Create a reference trace for this detector channel."""
        cmd = f':REFerence:SENSe{self.module}:CHANnel{self.channel}:INITiate'
        self.write(cmd)

    # Trace data methods --------------------------------------------------------------

    def length(self, trace_type: int = 1):
        """Get the number of points in the trace (int).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        :return: Number of data points in the trace (int).
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{trace_type}:DATA:LENGth?"
        return int(self.ask(cmd))

    def sampling_pm(self, trace_type: int = 1):
        """Get the wavelength sampling resolution in pm (float).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        :return: Sampling resolution in picometers (float).
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{trace_type}:DATA:SAMPling?"
        return float(self.ask(cmd)) * 1e12

    def start_wavelength_nm(self, trace_type: int = 1):
        """Get the start wavelength in nm (float).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        :return: Start wavelength in nanometers (float).
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{trace_type}:DATA:STARt?"
        return float(self.ask(cmd)) * 1e9

    def get_data_x(self, trace_type: int = 1, unit='M', format='BIN'):
        """Get trace X-axis data (wavelength or frequency).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        :param str unit: Data unit - 'M' for meters (wavelength), 'HZ' for Hertz (frequency).
            Default 'M'.
        :param str format: Data format - 'BIN' for binary or 'ASCII' for ASCII.
            Default 'BIN' for faster transfer of large datasets.
        :return: Numpy array of trace data (binary) or list (ASCII).
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")

        if format.upper() == 'BIN':
            # Binary format - X-axis data uses float64 (8 bytes per value)
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{trace_type}:DATA:X? BIN,{unit}")
            self.write(cmd)
            return self._read_binary_trace(dtype='>f8')  # 64-bit float, big-endian
        else:
            # ASCII format
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{trace_type}:DATA:X? ASCII,{unit}")
            return self.values(cmd)

    def get_data_y(self, trace_type: int = 1, unit='DB', format='BIN'):
        """Get trace Y-axis data (power).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        :param str unit: Data unit - 'DB' for dB or 'Y' for linear (default 'DB').
        :param str format: Data format - 'BIN' for binary or 'ASCII' for ASCII
            (default 'BIN').
        :return: Numpy array of trace data (binary) or list (ASCII).
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")

        if format.upper() == 'BIN':
            # Binary format - Y-axis data uses float32 (4 bytes per value)
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{trace_type}:DATA? BIN,{unit}")
            self.write(cmd)
            return self._read_binary_trace(dtype='>f4')  # 32-bit float, big-endian
        else:
            # ASCII format
            cmd = (f":TRACe:SENSe{self.module}:CHANnel{self.channel}:"
                   f"TYPE{trace_type}:DATA? ASCII,{unit}")
            return self.values(cmd)

    def save(self, trace_type: int = 1):
        """Save trace data to internal memory (CSV format only).

        :param int trace_type: TYPE number 1-23 (depends on detector type). Default 1.
        """
        if not (1 <= int(trace_type) <= 23):
            raise ValueError("trace_type must be in 1..23")
        cmd = f":TRACe:SENSe{self.module}:CHANnel{self.channel}:TYPE{trace_type}:SAVE"
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
        header = self.parent.read_bytes(2)
        length_of_length = int(chr(header[1]))

        # Read the length value (e.g., '3760004' for 940001 floats)
        length_bytes = self.parent.read_bytes(length_of_length)
        data_length = int(length_bytes)

        # Read the actual binary data
        data_bytes = self.parent.read_bytes(data_length)

        # Convert to numpy array with specified dtype
        return np.frombuffer(data_bytes, dtype=np.dtype(dtype))


class CTP10(SCPIMixin, Instrument):
    """Represents EXFO CTP10 vector analyzer instrument.

    The CTP10 is a tunable laser source and optical component test platform
    that can measure transmission and reflection characteristics. It supports
    up to 4 TLS (Tunable Laser Source) channels and up to 10 RLASer channels.

    .. code-block:: python

        ctp = CTP10("TCPIP::192.168.1.37::5025::SOCKET")

        # Configure global resolution
        ctp.resolution_pm = 10.0

        # Configure TLS channel 1
        ctp.tls1.start_wavelength_nm = 1520.0
        ctp.tls1.stop_wavelength_nm = 1580.0
        ctp.tls1.sweep_speed_nmps = 50
        ctp.tls1.laser_power_dbm = 5.0

        # Configure reference laser
        ctp.rlaser[2].power_dbm = 1.5
        ctp.rlaser[2].wavelength_nm = 1550.0
        ctp.rlaser[2].power_state = True  # Enable laser

        # Start measurement
        ctp.initiate_sweep()
        ctp.wait_for_sweep_complete()

        # Access detector on module 4, channel 1
        detector = ctp.detector(module=4, channel=1)

        # Configure detector-level settings
        detector.power_unit = 'DBM'
        detector.spectral_unit = 'WAV'
        detector.trigger = 0  # Software trigger
        detector.create_reference()

        # Measure optical power
        power = detector.power  # Returns power in configured unit

        # Read TF live trace data (TYPE1)
        length = detector.length(trace_type=1)
        wavelengths = detector.get_data_x(trace_type=1, unit='M', format='BIN')
        powers = detector.get_data_y(trace_type=1, unit='DB', format='BIN')

        # Read Raw Live trace (TYPE11)
        raw_powers = detector.get_data_y(trace_type=11, unit='DB', format='BIN')

        # Read Raw Reference trace (TYPE12)
        ref_powers = detector.get_data_y(trace_type=12, unit='DB', format='BIN')

        # Save trace data
        detector.save(trace_type=1)

    Trace types (TYPE parameter):
        - TYPE1: TF live trace (Transmission Function)
        - TYPE11: Raw Live trace
        - TYPE12: Raw Reference trace
        - TYPE13: Raw Quick Reference trace
        - See instrument documentation for complete list (1-23)
    """

    # TLS Channel creators (up to 4 channels)
    tls1 = Instrument.ChannelCreator(TLSChannel, 1)
    tls2 = Instrument.ChannelCreator(TLSChannel, 2)
    tls3 = Instrument.ChannelCreator(TLSChannel, 3)
    tls4 = Instrument.ChannelCreator(TLSChannel, 4)

    # RLASer Channel creator (up to 10 channels)
    rlaser = Instrument.MultiChannelCreator(RLASerChannel, list(range(1, 11)))

    # Detector accessor ---------------------------------------------------------------
    def detector(self, module: int, channel: int) -> DetectorChannel:
        """Return a DetectorChannel for given module and channel.

        :param int module: SENSe number 1-20 (module position in mainframe).
        :param int channel: CHANnel number 1-6 (detector position on module).
        :return: DetectorChannel instance bound to the given identifiers.

        Example:
            # Access detector on module 4, channel 1
            detector = ctp.detector(module=4, channel=1)

            # Detector-level operations
            detector.power_unit = 'DBM'
            power = detector.power

            # Access trace data
            tf_trace = detector.tf_live_trace()
            wavelengths = tf_trace.get_data_x()
        """
        if not (1 <= int(module) <= 20):
            raise ValueError("module must be in 1..20")
        if not (1 <= int(channel) <= 6):
            raise ValueError("channel must be in 1..6")
        return DetectorChannel(self, (int(module), int(channel)))

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
