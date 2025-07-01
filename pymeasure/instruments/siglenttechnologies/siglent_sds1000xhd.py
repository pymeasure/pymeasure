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


import struct
import math
import gc
from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import (
    truncated_discrete_set, truncated_range, strict_discrete_set
)


class AnalogChannel(Channel):
    """
    ===========================================================
    Implementation of a SIGLENT SDS1000xHD Oscilloscope channel
    ===========================================================
    """

    scale = Channel.control(
        ":CHANnel{ch}:SCALe?",
        ":CHANnel{ch}:SCALe %.3e",
        "Control the vertical scale of a channel in V/divisions.",
        validator=truncated_range,
        values=[1e-3, 10],
        get_process=lambda v: float(v),
    )

    coupling = Channel.control(
        ":CHANnel{ch}:COUPling?",
        ":CHANnel{ch}:COUPling %s",
        "Control the channel coupling mode (DC, AC, or GND).",
        validator=strict_discrete_set,
        values=["DC", "AC", "GND"],
        get_process=lambda v: v.strip(),
    )

    probe = Channel.control(
        ":CHANnel{ch}:PROBe?",
        ":CHANnel{ch}:PROBe %s",
        "Control the probe attenuation factor.",
        validator=truncated_discrete_set,
        values=[0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50, 100, 200,
                500, 1000],
        get_process=lambda v: float(v),
    )

    offset = Channel.control(
        ":CHANnel{ch}:OFFSet?",
        ":CHANnel{ch}:OFFSet %.6f",
        "Control the vertical offset of the channel in volts.",
        get_process=lambda v: float(v),
    )

    visible = Channel.control(
        ":CHANnel{ch}:VISible?",
        ":CHANnel{ch}:VISible %s",
        "Control whether the channel is visible (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    switch = Channel.control(
        ":CHANnel{ch}:SWITch?",
        ":CHANnel{ch}:SWITch %s",
        "Control the channel display switch (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    bandwidth_limit = Channel.control(
        ":CHANnel{ch}:BWLimit?",
        ":CHANnel{ch}:BWLimit %s",
        "Control the bandwidth limit (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    invert = Channel.control(
        ":CHANnel{ch}:INVert?",
        ":CHANnel{ch}:INVert %s",
        "Control signal inversion (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    label = Channel.control(
        ":CHANnel{ch}:LABel:TEXT?",
        ":CHANnel{ch}:LABel:TEXT '%s'",
        "Control the channel label text.",
        get_process=lambda v: v.strip().strip('"\''),
    )

    unit = Channel.control(
        ":CHANnel{ch}:UNIT?",
        ":CHANnel{ch}:UNIT %s",        "Control the channel unit (V, A).",
        validator=strict_discrete_set,
        values=["V", "A"],        get_process=lambda v: v.strip(),
    )


class WaveformChannel(Channel):
    """
    Waveform channel for SDS1000xHD oscilloscope.
    ===========================================================
    This class provides methods to retrieve waveform data from the oscilloscope.
    The waveform record contains two portions: the preamble and waveform data.
    The preamble contains information for interpreting the waveform data, while
    the waveform data is the actual data acquired for each point in the specified source.
    Both must be read separately using dedicated commands.
    """

    def __init__(self, parent, id):
        """Initialize the WaveformChannel with automatic source setting.
        
        Args:
            parent: Parent instrument instance
            id: Channel identifier (e.g., "C1", "C2", "F1", "D0", etc.)
        """
        super().__init__(parent, id)
        # Store the ID for later automatic source setting
        # We'll set the source automatically when first accessed, not during initialization
        self._auto_source_id = id

    source = Channel.control(
        ":WAVeform:SOURce?",
        ":WAVeform:SOURce %s",
        "Control the waveform source to be transferred from the oscilloscope.",
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
        get_process=lambda v: v.strip(),
    )

    @property
    def source_with_auto_set(self):
        """Get the source, automatically setting it if needed."""
        self._ensure_source_set()
        return self.source

    @source_with_auto_set.setter
    def source_with_auto_set(self, value):
        """Set the source."""
        self.source = value

    start_point = Channel.control(
        ":WAVeform:STARt?",
        ":WAVeform:STARt %d",
        """Control the starting data point for waveform transfer.
        This command specifies the starting data point for waveform transfer 
        using the query :WAVeform:DATA?. The value range is related to the 
        current waveform point and the value set by the command :WAVeform:POINt.
        Value in NR1 format (integer with no decimal point).""",
        validator=truncated_range,
        values=[0, 1000000000],  # Range depends on current waveform points and :WAVeform:POINt
        get_process=lambda v: int(v),
    )

    interval = Channel.control(
        ":WAVeform:INTerval?",
        ":WAVeform:INTerval %d",
        """Control the interval between data points for waveform transfer.
        This command sets the interval between data points for waveform transfer 
        using the query :WAVeform:DATA?. The query returns the interval between 
        data points for waveform transfer.
        Value in NR1 format (integer with no decimal point).
        Note: The value range is related to the values set by the commands 
        :WAVeform:POINt and :WAVeform:STARt.
        """,
        get_process=lambda v: int(v),
    )

    point = Channel.control(
        ":WAVeform:POINt?",
        ":WAVeform:POINt %d",
        """Control the number of waveform points to be transferred with :WAVeform:DATA?.
        This command sets the number of waveform points to be transferred with the 
        query :WAVeform:DATA?. The query returns the number of waveform points to be 
        transferred.
        Value in NR1 format (integer with no decimal point).
        Note: The value range is related to the current waveform point.
        """,
        get_process=lambda v: int(v),
    )

    max_point = Channel.measurement(
        ":WAVeform:MAXPoint?",
        """Get the maximum points of one piece when reading waveform data in pieces.
        This query returns the maximum points of one piece, when it needs to read 
        the waveform data in pieces. This is useful for determining how to segment
        large waveform transfers.
        Returns:
            int: Maximum points of one piece in NR1 format (integer with no decimal point).
        """,
        get_process=lambda v: float(v)
    )

    width = Channel.control(
        ":WAVeform:WIDTh?",
        ":WAVeform:WIDTh %s",
        """Control the output format for the transfer of waveform data.
        This command sets the current output format for the transfer of
        waveform data. The query returns the current output format.
        
        Values:
            - "BYTE": 8-bit data transfer format
            - "WORD": 16-bit data transfer format (upper byte transmitted first)
        
        Note: When the vertical resolution is set to 10 bit or the ADC bit is
        more than 8bit, it must be set to WORD before transferring waveform data.
        """,
        validator=strict_discrete_set,
        values=["BYTE", "WORD"],
        get_process=lambda v: v.strip(),
    )

    def _parse_preamble_descriptor(self, raw_data):
        """Parse the binary preamble descriptor data.
        
        Args:
            raw_data (bytes): Raw binary data from :WAVeform:PREamble? command
            
        Returns:
            dict: Parsed descriptor data with the same format as get_descriptor
        """
        try:
            # Find the start of the binary data after the header
            if isinstance(raw_data, str):
                raw_data = raw_data.encode('latin-1')
            
            # Check if we have a proper binary data block
            if b'#' not in raw_data:
                raise ValueError("No binary data block found in response")
                
            recv = raw_data[raw_data.find(b'#') + 11:]
            
            # Check if we have enough data
            min_required_length = 0x14c  # Minimum length needed for all fields
            if len(recv) < min_required_length:
                raise ValueError(f"Insufficient data: got {len(recv)} bytes, "
                                 f"need at least {min_required_length}")
            
            # Time division enumeration from the programming guide
            tdiv_enum = [200e-12, 500e-12, 1e-9,
                         2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
                         1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
                         1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3,
                         1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]
            
            # Extract binary data from specific offsets with bounds checking
            def safe_extract(data, start, end):
                if end >= len(data):
                    raise ValueError(f"Data truncated: trying to read bytes {start}:{end} "
                                     f"from {len(data)} bytes")
                return data[start:end + 1]
            
            v_scale = safe_extract(recv, 0x9c, 0x9f)
            v_offset = safe_extract(recv, 0xa0, 0xa3)
            interval = safe_extract(recv, 0xb0, 0xb3)
            code_per_div = safe_extract(recv, 0xa4, 0xa7)
            adc_bit = safe_extract(recv, 0xac, 0xad)
            delay = safe_extract(recv, 0xb4, 0xbb)
            tdiv = safe_extract(recv, 0x144, 0x145)
            probe = safe_extract(recv, 0x148, 0x14b)
            
            # Unpack the values with error checking
            interval_val = struct.unpack('f', interval)[0]
            delay_val = struct.unpack('d', delay)[0]
            tdiv_index = struct.unpack('h', tdiv)[0]
            probe_val = struct.unpack('f', probe)[0]
            vdiv = struct.unpack('f', v_scale)[0] * probe_val
            voffset = struct.unpack('f', v_offset)[0] * probe_val
            vcode_per = struct.unpack('f', code_per_div)[0]
            adc_bit_val = struct.unpack('h', adc_bit)[0]
            tdiv_val = tdiv_enum[tdiv_index] if 0 <= tdiv_index < len(tdiv_enum) else 1e-6
            
            return {
                'vdiv': vdiv,
                'voffset': voffset,
                'interval': interval_val,
                'trdl': delay_val,
                'tdiv': tdiv_val,
                'vcode_per': vcode_per,
                'adc_bit': adc_bit_val,
                'probe': probe_val
            }
            
        except (struct.error, IndexError, KeyError, ValueError) as e:
            # Fallback values if parsing fails
            print(f"Warning: Failed to parse preamble descriptor: {e}")
            return {
                'vdiv': 1.0,
                'voffset': 0.0,
                'interval': 1e-6,
                'trdl': 0.0,
                'tdiv': 1e-6,
                'vcode_per': 25.0,
                'adc_bit': 8,
                'probe': 1.0
            }

    def _ensure_source_set(self):
        """Ensure the source is set to match the channel ID if it's a valid source."""
        if hasattr(self, '_auto_source_id') and self._auto_source_id and \
           self._auto_source_id in ["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                                    "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                                    "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"]:
            try:
                # Always set the source to the channel ID without checking current value
                # This avoids potential issues with reading the current source state
                self.source = self._auto_source_id
            except Exception:
                # If setting source fails, continue without error
                pass

    @property
    def preamble(self):
        """Get the waveform preamble descriptor data.
        The preamble contains binary descriptor information about the waveform data format,
        including voltage scale, offset, time interval, trigger delay, time division,
        voltage codes per division, ADC bit depth, and probe attenuation factor.
        This uses the same binary parsing approach as the get_descriptor method.
        Returns:
            dict: A dictionary with the following keys:
                - vdiv: Voltage per division (float)
                - voffset: Voltage offset (float)
                - interval: Time interval between points (float)
                - trdl: Trigger delay (float)
                - tdiv: Time per division (float)
                - vcode_per: Voltage codes per division (float)
                - adc_bit: ADC bit depth (int)
                - probe: Probe attenuation factor (float)
        """
        self._ensure_source_set()
        try:
            # Get raw binary data from the instrument using the same approach as get_descriptor
            self.write(":WAVeform:PREamble?")
            raw_data = self.read_bytes(-1)
            return self._parse_preamble_descriptor(raw_data)
        except Exception as e:
            print(f"Warning: Failed to get preamble data: {e}")
            return {
                'vdiv': 1.0,
                'voffset': 0.0,
                'interval': 1e-6,
                'trdl': 0.0,
                'tdiv': 1e-6,
                'vcode_per': 25.0,
                'adc_bit': 8,
                'probe': 1.0
            }

    def get_data(self):
        """Get the waveform data from the oscilloscope for the current source.

        This method retrieves waveform data from the oscilloscope using the preamble
        property to get descriptor information about the waveform format.
        
        Returns:
            tuple: A tuple containing (time_values, volt_values) where:
                - time_values: List of time values in seconds
                - volt_values: List of voltage values in volts
        """
        self._ensure_source_set()
        try:
            # Constants - same as reference script
            HORI_NUM = 10

            # Set up waveform source and get preamble information
            self.start_point = 0  # Reset start point to 0
            
            # Get waveform descriptor information using the preamble property
            preamble_data = self.preamble
            vdiv = preamble_data['vdiv']
            ofst = preamble_data['voffset']
            interval = preamble_data['interval']
            trdl = preamble_data['trdl']
            tdiv = preamble_data['tdiv']
            vcode_per = preamble_data['vcode_per']
            adc_bit = preamble_data['adc_bit']
            
            # print(f"Preamble data: vdiv={vdiv}, offset={ofst}, interval={interval}, "
            #       f"trdl={trdl}, tdiv={tdiv}, vcode_per={vcode_per}, adc_bit={adc_bit}")
            
            # Get the waveform points and confirm the number of waveform slice reads
            points = self.parent.acq_points
            one_piece_num = self.max_point
            read_times = math.ceil(points / one_piece_num)

            # Set the number of read points per slice, if the waveform points is
            # greater than the maximum number of slice reads
            if points > one_piece_num:
                self.point = one_piece_num
                
            # Choose the format of the data returned
            self.width = "BYTE"
            if adc_bit > 8:
                self.width = "WORD"

            # Get the waveform data for each slice
            recv_byte = b''
            for i in range(0, read_times):
                start = i * one_piece_num
                # Set the starting point of each slice
                self.start_point = start
                # Get the waveform data of each slice
                self.write("WAV:DATA?")
                recv_rtn = self.read_bytes(-1, break_on_termchar=True).rstrip()
                # Splice each waveform data based on data block information
                block_start = recv_rtn.find(b'#')
                data_digit = int(recv_rtn[block_start + 1:block_start + 2])
                data_start = block_start + 2 + data_digit
                recv_byte += recv_rtn[data_start:]

            # Unpack signed byte data
            if adc_bit > 8:
                # Calculate actual length of data received and adjust points if needed
                actual_points = len(recv_byte) // 2  # 2 bytes per point for WORD format
                # print(f"Expected points: {int(points)}, Actual points from data: {actual_points}")
                if actual_points * 2 != len(recv_byte):
                    # warning_msg = (f"Warning: Buffer size {len(recv_byte)} is not exactly "
                    #                f"twice the number of points {actual_points}")
                    # print(warning_msg)
                    # Truncate buffer to ensure it's exactly divisible by 2
                    truncated_bytes = len(recv_byte) - (len(recv_byte) % 2)
                    recv_byte = recv_byte[:truncated_bytes]
                    actual_points = len(recv_byte) // 2

                convert_data = struct.unpack("%dh" % actual_points, recv_byte)
            else:
                # Calculate actual length of data received and adjust points if needed
                actual_points = len(recv_byte)  # 1 byte per point for BYTE format
                # print(f"Expected points: {int(points)}, Actual points from data: {actual_points}")
                convert_data = struct.unpack("%db" % actual_points, recv_byte)
            del recv_byte
            gc.collect()

            # Calculate the voltage value and time value
            time_value = []
            volt_value = []
            for idx in range(0, len(convert_data)):
                volt_value.append(convert_data[idx] / vcode_per * float(vdiv) - float(ofst))
                time_data = -(float(tdiv) * HORI_NUM / 2) + idx * interval + float(trdl)
                time_value.append(time_data)

            return time_value, volt_value

        except Exception as e:
            print(f"Error during waveform data acquisition: {e}")
            raise


class AdvancedMeasurementItem(Channel):
    """
    Represents an advanced measurement item in the SDS1000xHD oscilloscope.
    
    This class provides controls for enabling/disabling the measurement item,
    setting its source, and retrieving its value.
    """

    enabled = Channel.control(
        ":MEASure:ADVanced:P{ch}?",
        ":MEASure:ADVanced:P{ch} %s",
        "Control whether the advanced measurement item is enabled (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    source1 = Channel.control(
        ":MEASure:ADVanced:P{ch}:SOURce1?",
        ":MEASure:ADVanced:P{ch}:SOURce1 %s",
        "Control the first source for the advanced measurement item.",
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
        get_process=lambda v: v.strip(),
    )

    source2 = Channel.control(
        ":MEASure:ADVanced:P{ch}:SOURce2?",
        ":MEASure:ADVanced:P{ch}:SOURce2 %s",
        """Control the second source for the advanced measurement item.
        This is used for measurements that require two sources.
        """,
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
        get_process=lambda v: v.strip(),
    )

    statistics_all = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? ALL",
        "Returns all the statistics",
        get_process=lambda v: v.strip(),
    )

    # Individual statistics measurements
    statistics_all = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? ALL",
        """Get all statistics for the advanced measurement item.
        Returns all statistical data when statistics are enabled, or 'OFF' when disabled.
        """,
        get_process=lambda v: v.strip(),
    )

    statistics_current = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? CURRent",
        """Get the current value of the statistics for the advanced measurement item.
        Returns the current statistical value in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: (float(v.strip())
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    statistics_mean = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MEAN",
        """Get the mean value of the statistics for the advanced measurement item.
        Returns the mean statistical value in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: (float(v.strip())
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    statistics_maximum = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MAXimum",
        """Get the maximum value of the statistics for the advanced measurement item.
        Returns the maximum statistical value in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: (float(v.strip())
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    statistics_minimum = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MINimum",
        """Get the minimum value of the statistics for the advanced measurement item.
        Returns the minimum statistical value in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: (float(v.strip())
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    statistics_stddev = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? STDev",
        """Get the standard deviation of the statistics for the advanced measurement item.
        Returns the standard deviation in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: (float(v.strip())
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    statistics_count = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? COUNt",
        """Get the count of measurements used for statistics calculation.
        Returns the number of measurements used to calculate the statistical data.
        """,
        get_process=lambda v: (int(float(v.strip()))
                               if isinstance(v, str) and v.strip() != "OFF" 
                               else (v.strip() if isinstance(v, str) else v)),
    )

    type = Channel.control(
        ":MEASure:ADVanced:P{ch}:TYPE?",
        ":MEASure:ADVanced:P{ch}:TYPE %s",
        """Control the type of advanced measurement.
        This command sets the type of advanced measurement to be performed.
        The query returns the current measurement type.
        Values:
            PKPK|MAX|MIN|AMPL|TOP|BASE|LEVELX|CMEAN|MEAN|
            STDEV|VSTD|RMS|CRMS|MEDIAN|CMEDIAN|OVSN|FPRE|
            OVSP|RPRE|PER|FREQ|TMAX|TMIN|PWID|NWID|DUTY|
            NDUTY|WID|NBWID|DELAY|TIMEL|RISE|FALL|RISE10T90|
            FALL90T10|CCJ|PAREA|NAREA|AREA|ABSAREA|CYCLES|
            REDGES|FEDGES|EDGES|PPULSES|NPULSES|PHA|SKEW
            |FRR|FRF|FFR|FFF|LRR|LRF|LFR|LFF|PACArea|NACArea|
            ACArea|ABSACArea|PSLOPE|NSLOPE|TSR|TSF|THR|THF
        """,
        validator=strict_discrete_set,
        values=[f"P{i}" for i in range(1, 13)],
        get_process=lambda v: v.strip(),
    )

    value = Channel.control(
        ":MEASure:ADVanced:P{ch}:VALue?",
        ":MEASure:ADVanced:P{ch}:VALue %.6e",
        """Get the value of the advanced measurement item.
        This command retrieves the current value of the advanced measurement item.
        The value is returned in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: float(v.strip()) if isinstance(v, str) else float(v)
    )


class MeasureChannel(Channel):
    """
    Unified measurement class for SDS1000xHD oscilloscope.
    
    This class combines Simple, Advanced, Gate, and Threshold measurement functionality.
    It provides a comprehensive interface for all measurement operations on the SDS1000xHD.
    """

    enabled = Channel.control(
        ":MEASure?",
        ":MEASure %s",
        "Control the state of the measurement function (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    mode = Channel.control(
        ":MEASure:MODE?",
        ":MEASure:MODE %s",
        "Control the measurement mode (SIMPle or ADVanced).",
        validator=strict_discrete_set,
        values=["SIMPle", "ADVanced"],
        get_process=lambda v: v.strip(),
    )

    advanced_line_number = Channel.control(
        ":MEASure:ADVanced:LINenumber?",
        ":MEASure:ADVanced:LINenumber %d",
        "Control the total number of advanced measurement items displayed.",
        validator=truncated_range,
        values=[1, 12],
        get_process=lambda v: int(v),
    )

    advanced_measurements = Channel.MultiChannelCreator(
        AdvancedMeasurementItem,
        list(range(1, 13)),  # P1 through P12
        prefix="advanced_p"
    )

    statistics_enabled = Channel.control(
        ":MEASure:ADVanced:STATistics?",
        ":MEASure:ADVanced:STATistics %s",
        "Control whether statistics are enabled for measurements.",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    # Simple measurement properties
    simple_source = Channel.control(
        ":MEASure:SIMPle:SOURce?",
        ":MEASure:SIMPle:SOURce %s",
        "Control the source for simple measurements.",
        validator=strict_discrete_set,
        values=["CHANnel1", "CHANnel2", "CHANnel3", "CHANnel4",
                "FUNCtion1", "FUNCtion2", "FUNCtion3", "FUNCtion4"],
        get_process=lambda v: v.strip(),
    )

    def get_simple_value(self, measurement_type):
        """Get the value of a specific simple measurement type.
        This method retrieves the current value of the specified simple measurement type.
        Args:
            measurement_type (str): The measurement type to query. Valid values are:
                PKPK, MAX, MIN, AMPL, TOP, BASE, LEVELX, CMEAN, MEAN,
                STDEV, VSTD, RMS, CRMS, MEDIAN, CMEDIAN, OVSN, FPRE,
                OVSP, RPRE, PER, FREQ, TMAX, TMIN, PWID, NWID, DUTY,
                NDUTY, WID, NBWID, DELAY, TIMEL, RISE, FALL, RISE20T80,
                FALL80T20, CCJ, PAREA, NAREA, AREA, ABSAREA, CYCLES,
                REDGES, FEDGES, EDGES, PPULSES, NPULSES, PACArea,
                NACArea, ACArea, ABSACArea, ALL
                
                Note: ALL returns all measurement values of all measurement types 
                except for delay measurements.
        
        Returns:
            float or str: The measurement value in NR3 format (e.g., 1.23E+2) for 
                         individual measurements, or a string containing all values 
                         when measurement_type is "ALL".
        
        Example:
            # Get maximum value
            max_val = measure.get_simple_value("MAX")
            # Get all measurements
            all_vals = measure.get_simple_value("ALL")
        """
        response = self.ask(f":MEASure:SIMPle:VALue? {measurement_type}")
        if measurement_type == "ALL":
            return response.strip()
        else:
            return float(response.strip()) if isinstance(response, str) else float(response)

    simple_value_all = Channel.measurement(
        ":MEASure:SIMPle:VALue? ALL",
        """Get all simple measurement values.
        This command retrieves all measurement values of all measurement types 
        except for delay measurements.
        Returns:
            str: All measurement values in a formatted string.
        """,
        get_process=lambda v: v.strip(),
    )

    # Simple measurement methods
    def clear_simple(self):
        """Clear simple measurements."""
        self.write(":MEASure:SIMPle:CLEar")
    
    def set_simple_item(self, item, state="ON"):
        """Set the simple measurement item.
        
        This command sets the type of simple measurement and its state.
        
        Args:
            item (str): The measurement item to set. Valid values are:
                PKPK, MAX, MIN, AMPL, TOP, BASE, LEVELX, CMEAN, MEAN,
                STDEV, VSTD, RMS, CRMS, MEDIAN, CMEDIAN, OVSN, FPRE,
                OVSP, RPRE, PER, FREQ, TMAX, TMIN, PWID, NWID, DUTY,
                NDUTY, WID, NBWID, DELAY, TIMEL, RISE, FALL, RISE20T80,
                FALL80T20, CCJ, PAREA, NAREA, AREA, ABSAREA, CYCLES,
                REDGES, FEDGES, EDGES, PPULSES, NPULSES, PACArea,
                NACArea, ACArea, ABSACArea
            state (str): The state of the measurement item (ON or OFF).
                        Defaults to "ON".
        
        Example:
            # Add maximum measurement to the simple measurements window
            measure.set_item("MAX", "ON")
            # Remove frequency measurement from the simple measurements window  
            measure.set_item("FREQ", "OFF")
        """
        self.write(f":MEASure:SIMPle:ITEM {item},{state}")
    
    # Advanced measurement methods
    def clear_advanced(self):
        """Clear advanced measurements."""
        self.write(":MEASure:ADVanced:CLEar")

    def reset_statistics(self):
        """Reset statistics for advanced measurements."""
        self.write(":MEASure:ADVanced:STATistics:RESet")


class TriggerChannel(Channel):
    """
    Trigger channel for SDS1000xHD oscilloscope.
    This class provides comprehensive trigger control for the SDS1000xHD oscilloscope
    using SCPI commands. It handles type-specific trigger configuration where different
    trigger types (EDGE, SLOPe, etc.) have their own source, level, and coupling settings.
    The source parameter values are: C1, C2, C3, C4, EX, EX5, LINE where:
    - C1-C4: Channel inputs
    - EX: External trigger input
    - EX5: External trigger input divided by 5
    - LINE: Line frequency trigger
    """

    frequency = Channel.measurement(
        ":TRIGger:FREQuency?",
        docs="""Get the current trigger frequency from the hardware frequency counter.
        Returns the value of hardware frequency counter in hertz if available. 
        The default precision is 3 digits, maximum valid precision is 7 digits.
        Use ":FORMat:DATA" command to set the data precision.
        Returns:
            float: Trigger frequency in Hz (NR3 format with decimal point and exponent)
        """,
        get_process=lambda v: float(v.strip()) if isinstance(v, str) else float(v),
    )

    mode = Channel.control(
        ":TRIGger:MODE?",
        ":TRIGger:MODE %s",
        """Control the trigger mode.
        AUTO: The oscilloscope begins to search for the trigger signal that meets the 
              conditions. If the trigger signal is satisfied, the running state shows 
              Trig'd, and the interface shows stable waveform. Otherwise, the running 
              state always shows Auto, and the interface shows unstable waveform.
        NORMal: The oscilloscope enters the wait trigger state and begins to search for 
                trigger signals that meet the conditions. If the trigger signal is 
                satisfied, the running state shows Trig'd, and the interface shows 
                stable waveform. Otherwise, the running state shows Ready, and the 
                interface displays the last triggered waveform (previous trigger) or 
                does not display the waveform (no previous trigger).
        SINGle: The backlight of SINGLE key lights up, the oscilloscope enters the 
                waiting trigger state and begins to search for the trigger signal that 
                meets the conditions. If the trigger signal is satisfied, the running 
                state shows Trig'd, and the interface shows stable waveform. Then, the 
                oscilloscope stops scanning, the RUN/STOP key becomes red, and the 
                running status shows Stop. Otherwise, the running state shows Ready, 
                and the interface does not display the waveform.
        FTRIG: Force to acquire a frame regardless of whether the input signal meets 
               the trigger conditions or not.
        """,
        validator=strict_discrete_set,
        values=["AUTO", "NORMal", "SINGle", "FTRIG"],
        get_process=lambda v: v.strip(),
    )

    status = Channel.measurement(
        ":TRIGger:STATus?",
        docs="""Get the current trigger status.
        Returns the current trigger state such as STOP, READY, ARM, TD, WAIT, etc.
        """,
        get_process=lambda v: v.strip(),
    )

    type = Channel.measurement(
        ":TRIGger:TYPE?",
        docs="""Get the current trigger type as a dict with keys:
        - "type": trigger type (EDGE, SLOPe, PULSe, VIDeo, WINDow, INTerval, DROPout,
        RUNT, PATTern, QUALified, DELay, NEDGe, SHOLd, IIC, SPI, UART, CAN, LIN, etc.)
        """,
        get_process=lambda v: v.strip(),
    )

    # EDGE trigger specific measurements
    edge_coupling = Channel.control(
        ":TRIGger:EDGE:COUPling?",
        ":TRIGger:EDGE:COUPling %s",
        """Control the coupling mode of the edge trigger.
        - DC: DC coupling allows dc and ac signals into the trigger path.
        - AC: AC coupling places a high-pass filter in the trigger path, removing 
              dc offset voltage from the trigger waveform. Use AC coupling to get 
              a stable edge trigger when your waveform has a large dc offset.
        - HFREJect: High-frequency rejection filter that adds a low-pass filter 
                    in the trigger path to remove high-frequency components from 
                    the trigger waveform. Use to remove high-frequency noise, such 
                    as AM or FM broadcast stations, from the trigger path.
        - LFREJect: Low frequency rejection filter adds a high-pass filter in 
                    series with the trigger waveform to remove any unwanted 
                    low-frequency components from a trigger waveform, such as 
                    power line frequencies, that can interfere with proper triggering.
        """,
        validator=strict_discrete_set,
        values=["DC", "AC", "LFREJect", "HFREJect"],
        get_process=lambda v: v.strip(),
    )

    edge_hld_event = Channel.control(
        ":TRIGger:EDGE:HLDEVent?",
        ":TRIGger:EDGE:HLDEVent %d",
        """Control the number of holdoff events for edge trigger.
        This command sets the number of holdoff events of the edge trigger.
        The holdoff event count determines how many trigger events to ignore
        before allowing the next trigger to occur.
        Range: 1 to 100000000 (NR1 format - integer with no decimal point)
        """,
        validator=truncated_range,
        values=[1, 100000000],
        get_process=lambda v: int(v),
    )

    edge_hld_time = Channel.control(
        ":TRIGger:EDGE:HLDTime?",
        ":TRIGger:EDGE:HLDTime %.6e",
        """Control the holdoff time for edge trigger.
        This command sets the holdoff time of the edge trigger in seconds.
        The holdoff time determines how long to wait after a trigger event before 
        allowing the next trigger to occur.
        Range: 8.00E-09 to 3.00E+01 seconds (NR3 format - float with decimal point and exponent)
        """,
        validator=truncated_range,
        values=[8e-9, 30],
        get_process=lambda v: float(v),
    )

    edge_hld_off = Channel.control(
        ":TRIGger:EDGE:HOLDoff?",
        ":TRIGger:EDGE:HOLDoff %s",
        """Control the holdoff type for edge trigger.
        This command selects the holdoff type of the edge trigger.
        - OFF: Turn off the holdoff
        - EVENts: The number of trigger events that the oscilloscope counts 
                  before re-arming the trigger circuitry
        - TIME: The amount of time that the oscilloscope waits before 
                re-arming the trigger circuitry
        """,
        validator=strict_discrete_set,
        values=["OFF", "EVENts", "TIME"],
        get_process=lambda v: v.strip(),
    )

    edge_hld_start = Channel.control(
        ":TRIGger:EDGE:HSTart?",
        ":TRIGger:EDGE:HSTart %s",
        """Control the initial position of the edge trigger holdoff.
        This command defines the initial position of the edge trigger holdoff.
        - LAST_TRIG: The initial position of holdoff is the first time point 
                     satisfying the trigger condition.
        - ACQ_START: The initial position of holdoff is time of the last trigger.
        """,
        validator=strict_discrete_set,
        values=["LAST_TRIG", "ACQ_START"],
        get_process=lambda v: v.strip(),
    )

    edge_impedance = Channel.control(
        ":TRIGger:EDGE:IMPedance?",
        ":TRIGger:EDGE:IMPedance %s",
        """Control the impedance of the edge trigger source.
        This command sets the edge trigger source impedance, which is only 
        valid when the source is EXT or EXT/5.
        - ONEMeg: 1 MOhm impedance
        - FIFTy: 50 Ohm impedance
        """,
        validator=strict_discrete_set,
        values=["ONEMeg", "FIFTy"],
        get_process=lambda v: v.strip(),
    )

    edge_level = Channel.control(
        ":TRIGger:EDGE:LEVel?",
        ":TRIGger:EDGE:LEVel %.6e",
        """Control the trigger level of the edge trigger.
        This command sets the trigger level of the edge trigger in volts.
        The query returns the current trigger level value of the edge trigger.
        For SDS1000X HD models, the range is:
        [-4.1*vertical_scale-vertical_offset, 4.1*vertical_scale-vertical_offset]
        Value in NR3 format (float with decimal point and exponent).
        """,
        get_process=lambda v: float(v.strip()) if isinstance(v, str) else float(v),
    )

    edge_noise_reject = Channel.control(
        ":TRIGger:EDGE:NREJect?",
        ":TRIGger:EDGE:NREJect %s",
        """Control the noise rejection for edge trigger.
        This command sets the state of the noise rejection for the edge trigger.
        - ON: Enable noise rejection
        - OFF: Disable noise rejection
        """,
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    edge_slope = Channel.control(
        ":TRIGger:EDGE:SLOPe?",
        ":TRIGger:EDGE:SLOPe %s",
        """Control the slope of the edge trigger.
        - RISing: Triggers on rising edge
        - FALLing: Triggers on falling edge  
        - ALTernate: Triggers on alternating edges
        """,
        validator=strict_discrete_set,
        values=["RISing", "FALLing", "ALTernate"],
        get_process=lambda v: v.strip(),
    )

    edge_source = Channel.control(
        ":TRIGger:EDGE:SOURce?",
        ":TRIGger:EDGE:SOURce %s",
        """Control the trigger source of the edge trigger.
        - C1, C2, C3, C4: Analog channel inputs
        - D0-D15: Digital channel inputs (if available)
        - EX: External trigger input
        - EX5: External trigger input divided by 5
        - LINE: Line frequency trigger
        """,
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7", 
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "EX", "EX5", "LINE"],
        get_process=lambda v: v.strip(),
    )

    def force_trigger(self):
        """Force a trigger event."""
        self.write(":TRIGger:FORce")

    def run(self):
        """Set the oscilloscope to run state.
        This command starts the oscilloscope acquisition and puts it in running mode.
        The oscilloscope will continuously acquire and display waveforms.
        """
        self.write(":TRIGger:RUN")

    def stop(self):
        """Set the oscilloscope to stop state.
        This command stops the oscilloscope acquisition. The oscilloscope will
        stop acquiring new waveforms and display the last acquired waveform.
        """
        self.write(":TRIGger:STOP")


class SDS1000xHD(SCPIMixin, Instrument):
    """
    ==============================================
    Represents the SIGLENT SDS1000xHD Oscilloscope
    ==============================================
    The SDS1000X-HD series are high-definition oscilloscopes with enhanced
    measurement capabilities and improved user interface. This implementation
    supports common oscilloscope operations including waveform acquisition,
    measurements, and trigger control.
    """

    def __init__(self, adapter, name="Siglent SDS1000xHD Oscilloscope", timeout=2000, 
                 chunk_size=20*1024*1024, **kwargs):
        super().__init__(adapter, name, timeout=timeout, chunk_size=chunk_size, **kwargs)

    channel_1 = Instrument.ChannelCreator(AnalogChannel, "1")
    channel_2 = Instrument.ChannelCreator(AnalogChannel, "2")
    channel_3 = Instrument.ChannelCreator(AnalogChannel, "3")  # For 4-channel models
    channel_4 = Instrument.ChannelCreator(AnalogChannel, "4")  # For 4-channel models
    
    # Waveform channels for all sources: analog channels (C1-C4), function channels (F1-F4),
    # and digital channels (D0-D15)
    waveform_channels = Instrument.MultiChannelCreator(
        WaveformChannel,
        ["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
         "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
         "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
        prefix="wf_"
    )
    
    # Measurement subsystem
    measure = Instrument.ChannelCreator(MeasureChannel, "")
    # Trigger subsystem
    trigger = Instrument.ChannelCreator(TriggerChannel, "")

    acq_acquisition_mode = Instrument.control(
        ":ACQuire:AMODe?",
        ":ACQuire:AMODe %s",
        """Control sets the rate of waveform capture.
        This command can provide a high-speed waveform capture rate to help capture signal 
        anomalies""",
        validator=strict_discrete_set,
        values=["FAST", "SLOW"],
        get_process=lambda v: v.strip(),
    )

    acq_interpolation = Instrument.control(
        ":ACQuire:INTerpolation?",
        ":ACQuire:INTerpolation %s",
        "Control acquisition interpolation method (ON selects sinx/x (sinc) "
        "interpolation, OFF selects linear interpolation).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    acq_memory_mgmt = Instrument.control(
        ":ACQuire:MMANagement?",
        ":ACQuire:MMANagement %s",
        """Control memory management mode.
        
        AUTO: Maintain maximum sampling rate, automatically set memory depth and 
              sampling rate according to time base.
        FSRate: Fixed Sampling Rate mode - maintain specified sampling rate and 
                automatically set memory depth according to time base.
        FMDepth: Fixed Memory Depth mode - automatically set sampling rate 
                 according to storage depth and time base.""",
        validator=strict_discrete_set,
        values=["AUTO", "FSRate", "FMDepth"],
        get_process=lambda v: v.strip(),
    )

    acq_plot_mode = Instrument.control(
        ":ACQuire:MODE?",
        ":ACQuire:MODE %s",
        """Control the acquisition mode of the oscilloscope.
        
        YT mode plots amplitude (Y) vs. time (T).
        XY mode plots channel X vs. channel Y, commonly referred to as a Lissajous curve.
        ROLL mode plots amplitude (Y) vs. time (T) as in YT mode, but begins to write 
        the waveforms from the right-hand side of the display. This is similar to a 
        "strip chart" recording and is ideal for low-frequency signals.""",
        validator=strict_discrete_set,
        values=["YT", "XY", "ROLL"],
        get_process=lambda v: v.strip(),
    )

    acq_memory_depth = Instrument.control(
        ":ACQuire:MDEPth?",
        ":ACQuire:MDEPth %s",
        """Control the memory depth.
        For SDS1000X HD:
        - Single Channel: 10k, 100k, 1M, 10M, 100M
        - Dual-Channel: 10k, 100k, 1M, 10M, 50M
        - Four-Channel: 10k, 100k, 1M, 10M, 25M
        AUTO mode automatically selects appropriate depth based on timebase and channels.
        Note: Turning on digital channels or setting acquisition type to AVERage/ERES 
        or setting acquisition mode to roll will limit the memory depth. Refer to the 
        user manual for single and dual channel mode definitions.""",
        validator=strict_discrete_set,
        values=["AUTO", "10k", "100k", "1M", "10M", "25M", "50M", "100M"],
        get_process=lambda v: v.strip(),
    )

    acq_num_acquisitions = Instrument.control(
        ":ACQuire:NUMAcq?",
        ":ACQuire:NUMAcq %d",
        """Controls the number of waveform acquisitions that
        have occurred since starting acquisition. This value is reset to
        zero when any acquisition,horizontal, or vertical arguments
        that affect the waveform are changed.""",
        validator=truncated_range,
        values=[1, 1000000],
        get_process=lambda v: int(v),
    )

    acq_points = Instrument.measurement(
        ":ACQuire:POINts?",
        "Get the number of sampled points of the current waveform on the screen.",
        get_process=lambda v: int(v),
    )

    acq_resolution = Instrument.control(
        ":ACQuire:RESolution?",
        ":ACQuire:RESolution %s",
        "Control the ADC resolution for SDS1000X HD oscilloscope (8Bits or 10Bits).",
        validator=strict_discrete_set,
        values=["8Bits", "10Bits"],
        get_process=lambda v: v.strip(),
    )

    acq_sequence_mode = Instrument.control(
        ":ACQuire:SEQuence?",
        ":ACQuire:SEQuence %s",
        "Control sequence acquisition mode (ON/OFF).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    acq_sequence_count = Instrument.control(
        ":ACQuire:SEQuence:COUNt?",
        ":ACQuire:SEQuence:COUNt %d",
        """Control the number of memory segments to acquire.
        The command sets the number of memory segments to acquire. The maximum number 
        of segments may be limited by the memory depth of your oscilloscope.
        The query returns the current count setting.
        Value in NR1 format (integer, no decimal point). The range varies by model 
        and current timebase - see user manual for details.""",
        validator=truncated_range,
        values=[1, 10000],
        get_process=lambda v: int(v),
    )

    acq_sample_rate = Instrument.control(
        ":ACQuire:SRATe?",
        ":ACQuire:SRATe %.3e",
        """Control the sampling rate in samples per second.
        This command sets the sampling rate when in the fixed sampling rate mode.
        If the set value is greater than the settable value, it will automatically 
        match to the settable value. The query returns the current sampling rate.""",
        get_process=lambda v: float(v),
    )

    acq_type = Instrument.control(
        ":ACQuire:TYPE?",
        ":ACQuire:TYPE %s",
        """Control the acquisition type.
        - NORMal: Normal acquisition mode
        - PEAK: Peak detect mode
        - AVERage: Averaging mode (can specify number of averages)
        - ERES: Enhanced resolution mode (can specify enhanced bits)
        For AVERage mode, append comma and times (4,16,32,64,128,256,512,1024,2048,4096,8192)
        For ERES mode, append comma and bits (0.5,1.0,1.5,2.0,2.5,3.0,3.5,4.0)
        Note: AVERage and ERES types are not available in sequence mode.""",
        validator=strict_discrete_set,
        values=["NORMal", "PEAK", "AVERage", "ERES"],
        get_process=lambda v: v.strip().split(',')[0],  # Extract base type from response
    )

    # Timebase control properties
    timebase_delay = Instrument.control(
        ":TIMebase:DELay?",
        ":TIMebase:DELay %.6e",
        "Control the horizontal trigger delay in seconds.",
        get_process=lambda v: float(v),
    )

    timebase_reference = Instrument.control(
        ":TIMebase:REFerence?",
        ":TIMebase:REFerence %s",
        """Control the horizontal reference strategy for delay value changes.
        
        DELay: When the time base is changed, the horizontal delay value remains fixed.
               The waveform expands/contracts around the center of the display.
        POSition: When the time base is changed, the horizontal delay remains fixed 
                  to the grid position on the display. The waveform expands/contracts 
                  around the position of the horizontal display.""",
        validator=strict_discrete_set,
        values=["DELay", "POSition"],
        get_process=lambda v: v.strip(),
    )

    timebase_reference_position = Instrument.control(
        ":TIMebase:REFerence:POSition?",
        ":TIMebase:REFerence:POSition %d",
        """Control the horizontal reference center when the reference strategy is DELay.
        This command sets the horizontal reference center as a percentage of the display width.
        The value represents the position from the left edge of the display (0-100%).""",
        validator=truncated_range,
        values=[0, 100],
        get_process=lambda v: int(v),
    )

    timebase_scale = Instrument.control(
        ":TIMebase:SCALe?",
        ":TIMebase:SCALe %.6e",
        """Control the horizontal scale per division for the main window in seconds per division.
        Note: Due to the limitation of the expansion strategy, when the time base is set
        from large to small, it will automatically adjust to the minimum time base that
        can be set currently.""",
        validator=truncated_range,
        values=[200e-12, 1000],
        get_process=lambda v: float(v),
    )

    timebase_window = Instrument.control(
        ":TIMebase:WINDow?",
        ":TIMebase:WINDow %s",
        """Control the zoomed window state.
        This command turns on or off the zoomed window.
        The query returns the state of the zoomed window.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        get_process=lambda v: v.strip(),
    )

    timebase_window_delay = Instrument.control(
        ":TIMebase:WINDow:DELay?",
        ":TIMebase:WINDow:DELay %.6e",
        """Control the horizontal position in the zoomed view of the main sweep.
        This command sets the horizontal delay of the zoomed window relative to the main sweep.
        The delay value must keep the zoomed view window within the main sweep range.
        If the delay is set outside the legal range, it will be automatically adjusted
        to the nearest legal value.
        The valid range is determined by the main sweep range and horizontal position.""",
        get_process=lambda v: float(v),
    )

    timebase_window_scale = Instrument.control(
        ":TIMebase:WINDow:SCALe?",
        ":TIMebase:WINDow:SCALe %.6e",
        """Control the horizontal scale per division for the zoomed window in seconds per division.
        This command sets the zoomed window horizontal scale (seconds/division).
        The query returns the current zoomed window scale setting.
        Note: The scale of the zoomed window cannot be greater than that of the main window. 
        If you set the value greater than the main window scale, it will automatically be 
        set to the same value as the main window.""",
        validator=truncated_range,
        values=[200e-12, 1000],
        get_process=lambda v: float(v),
    )

    def auto_setup(self):
        """Perform automatic setup of the oscilloscope."""
        self.write(":AUToset")

    def clear_sweeps_acq(self):
        """Clear accumulated sweeps using ACQuire command."""
        self.write(":ACQuire:CSWeep")
