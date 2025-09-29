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
from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import (
    strict_range, strict_discrete_set
)


class AnalogChannel(Channel):
    """Implementation of a SIGLENT SDS1000xHD Oscilloscope channel."""

    scale = Channel.control(
        ":CHANnel{ch}:SCALe?",
        ":CHANnel{ch}:SCALe %.3e",
        """Control the vertical scale of a channel in V/divisions
        (float strictly between 1e-3 and 10).""",
        validator=strict_range,
        values=[1e-3, 10],
    )

    coupling = Channel.control(
        ":CHANnel{ch}:COUPling?",
        ":CHANnel{ch}:COUPling %s",
        "Control the channel coupling mode (str): 'DC', 'AC', or 'GND'.",
        validator=strict_discrete_set,
        values=["DC", "AC", "GND"],
    )

    probe = Channel.control(
        ":CHANnel{ch}:PROBe?",
        ":CHANnel{ch}:PROBe %s",
        "Control the probe attenuation factor (float).",
        validator=strict_discrete_set,
        values=[0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 20, 50,
                100, 200, 500, 1000],
    )

    offset = Channel.control(
        ":CHANnel{ch}:OFFSet?",
        ":CHANnel{ch}:OFFSet %.6f",
        "Control the vertical offset of the channel in volts (float).",
    )

    visible_enabled = Channel.control(
        ":CHANnel{ch}:VISible?",
        ":CHANnel{ch}:VISible %s",
        """Control whether the channel waveform is displayed on screen (bool).
        This sets the display state only, controlling waveform visibility.
        Different from display_enabled which controls the physical channel switch.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    display_enabled = Channel.control(
        ":CHANnel{ch}:SWITch?",
        ":CHANnel{ch}:SWITch %s",
        """Control whether the channel display is turned on or off (bool).
        This turns the display of the specified channel on or off.
        Different from visible_enabled which sets the display state only.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    bandwidth_limit_enabled = Channel.control(
        ":CHANnel{ch}:BWLimit?",
        ":CHANnel{ch}:BWLimit %s",
        "Control the bandwidth limit enabled state (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    invert = Channel.control(
        ":CHANnel{ch}:INVert?",
        ":CHANnel{ch}:INVert %s",
        "Control signal inversion (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    label = Channel.control(
        ":CHANnel{ch}:LABel:TEXT?",
        ":CHANnel{ch}:LABel:TEXT '%s'",
        "Control the channel label text (str).",
        preprocess_reply=lambda v: v.strip('\r\n\t \'"'),
    )

    unit = Channel.control(
        ":CHANnel{ch}:UNIT?",
        ":CHANnel{ch}:UNIT %s",
        "Control the channel unit (str): 'V' or 'A'.",
        validator=strict_discrete_set,
        values=["V", "A"],
    )


class WaveformChannel(Channel):
    """Waveform channel for SDS1000XHD oscilloscope.

    This class provides methods to retrieve waveform data from the oscilloscope.
    The waveform record contains two portions: the preamble and waveform data.
    The preamble contains information for interpreting the waveform data, while
    the waveform data is the actual data acquired for each point in the specified source.
    Both must be read separately using dedicated commands.
    """

    source = Channel.control(
        ":WAVeform:SOURce?",
        ":WAVeform:SOURce %s",
        "Control the waveform source to be transferred from the oscilloscope (str).",
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
    )

    start_point = Channel.control(
        ":WAVeform:STARt?",
        ":WAVeform:STARt %d",
        """Control the starting data point for waveform transfer (int).

        This command specifies the starting data point for waveform transfer
        using the query :WAVeform:DATA?. The value range is related to the
        current waveform point and the value set by the command :WAVeform:POINt.
        Value in NR1 format (integer with no decimal point).""",
        cast=int,
    )

    interval = Channel.control(
        ":WAVeform:INTerval?",
        ":WAVeform:INTerval %d",
        """Control the interval between data points for waveform transfer (int).

        This controls the interval between data points for waveform transfer
        using the query :WAVeform:DATA?.
        Value in NR1 format (integer with no decimal point).
        Note: The value range is related to the values set by the commands
        :WAVeform:POINt and :WAVeform:STARt.
        """,
        cast=int,
    )

    point = Channel.control(
        ":WAVeform:POINt?",
        ":WAVeform:POINt %d",
        """Control the number of waveform points to be transferred with :WAVeform:DATA? (int).

        This controls the number of waveform points to be transferred with the
        query :WAVeform:DATA?.
        Value in NR1 format (integer with no decimal point).
        Note: The value range is related to the current waveform point.
        """,
        cast=int,
    )

    max_point = Channel.measurement(
        ":WAVeform:MAXPoint?",
        """Get the maximum points of one piece when reading waveform data in pieces (float).

        This query returns the maximum points of one piece, when it needs to read
        the waveform data in pieces. This is useful for determining how to segment
        large waveform transfers.
        """
    )

    width = Channel.control(
        ":WAVeform:WIDTh?",
        ":WAVeform:WIDTh %s",
        """Control the output format for the transfer of waveform data (str).

        This controls the current output format for the transfer of
        waveform data. Options: 'BYTE' or 'WORD'.
        """,
        validator=strict_discrete_set,
        values=["BYTE", "WORD"],
    )

    def _parse_preamble_descriptor(self, raw_data):
        """Parse the binary preamble descriptor data.

        :param bytes raw_data: Raw binary data from :WAVeform:PREamble? command
        :return: Parsed descriptor data with the same format as get_descriptor (dict)
        """
        # Locate the binary data block
        recv = raw_data[raw_data.find(b'#') + 11:]

        # Time division enumeration from the programming guide
        tdiv_enum = [200e-12, 500e-12, 1e-9,
                     2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
                     1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
                     1e-3, 2e-3, 5e-3, 10e-3, 20e-3, 50e-3, 100e-3, 200e-3, 500e-3,
                     1, 2, 5, 10, 20, 50, 100, 200, 500, 1000]

        # Extract binary data from specific offsets
        v_scale = recv[0x9c:0xa0]
        v_offset = recv[0xa0:0xa4]
        interval = recv[0xb0:0xb4]
        code_per_div = recv[0xa4:0xa8]
        adc_bit = recv[0xac:0xae]
        delay = recv[0xb4:0xbc]
        tdiv = recv[0x144:0x146]
        probe = recv[0x148:0x14c]

        # Unpack the values
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

    @property
    def preamble(self):
        """Get the waveform preamble descriptor data.

        The preamble contains binary descriptor information about the waveform data format,
        including voltage scale, offset, time interval, trigger delay, time division,
        voltage codes per division, ADC bit depth, and probe attenuation factor.
        This uses the same binary parsing approach as the get_descriptor method.

        :return: A dictionary with the following keys:

            - vdiv: Voltage per division (float)
            - voffset: Voltage offset (float)
            - interval: Time interval between points (float)
            - trdl: Trigger delay (float)
            - tdiv: Time per division (float)
            - vcode_per: Voltage codes per division (float)
            - adc_bit: ADC bit depth (int)
            - probe: Probe attenuation factor (float)
        :rtype: dict
        """
        # Get raw binary data from the instrument using the same approach as get_descriptor
        self.write(":WAVeform:PREamble?")
        raw_data = self.read_bytes(-1)
        return self._parse_preamble_descriptor(raw_data)

    def get_data(self):
        """Get the waveform data from the oscilloscope for the current source.

        This method retrieves waveform data from the oscilloscope using the preamble
        property to get descriptor information about the waveform format.

        :return: A tuple containing (time_values, volt_values) where:
            - time_values: List of time values in seconds
            - volt_values: List of voltage values in volts
        :rtype: tuple
        """
        # Constants - same as reference script
        HORI_NUM = 10

        # Set up waveform source and get preamble information
        self.start_point = 0  # Reset start point to 0

        # Get waveform descriptor information using the preamble property
        preamble_data = self.preamble
        vdiv = preamble_data['vdiv']
        offset = preamble_data['voffset']
        interval = preamble_data['interval']
        trdl = preamble_data['trdl']
        tdiv = preamble_data['tdiv']
        vcode_per = preamble_data['vcode_per']
        adc_bit = preamble_data['adc_bit']

        # Get the waveform points and confirm the number of waveform slice reads
        points = self.parent.acquisition.points
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
            if actual_points * 2 != len(recv_byte):
                # Truncate buffer to ensure it's exactly divisible by 2
                truncated_bytes = len(recv_byte) - (len(recv_byte) % 2)
                recv_byte = recv_byte[:truncated_bytes]
                actual_points = len(recv_byte) // 2

            convert_data = struct.unpack("%dh" % actual_points, recv_byte)
        else:
            # Calculate actual length of data received and adjust points if needed
            actual_points = len(recv_byte)  # 1 byte per point for BYTE format
            convert_data = struct.unpack("%db" % actual_points, recv_byte)

        # Calculate the voltage value and time value
        time_value = []
        volt_value = []
        for idx in range(0, len(convert_data)):
            volt_value.append(convert_data[idx] / vcode_per * float(vdiv) - float(offset))
            time_data = -(float(tdiv) * HORI_NUM / 2) + idx * interval + float(trdl)
            time_value.append(time_data)

        return time_value, volt_value


class AdvancedMeasurementItem(Channel):
    """Represents an advanced measurement item in the SDS1000xHD oscilloscope.

    This class provides controls for enabling/disabling the measurement item,
    setting its source, and retrieving its value.
    """

    enabled = Channel.control(
        ":MEASure:ADVanced:P{ch}?",
        ":MEASure:ADVanced:P{ch} %s",
        "Control whether the advanced measurement item is enabled (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    source1 = Channel.control(
        ":MEASure:ADVanced:P{ch}:SOURce1?",
        ":MEASure:ADVanced:P{ch}:SOURce1 %s",
        "Control the first source for the advanced measurement item (str).",
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
    )

    source2 = Channel.control(
        ":MEASure:ADVanced:P{ch}:SOURce2?",
        ":MEASure:ADVanced:P{ch}:SOURce2 %s",
        """Control the second source for the advanced measurement item (str).
        This is used for measurements that require two sources.
        """,
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "F1", "F2", "F3", "F4",
                "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15"],
    )

    statistics_all = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? ALL",
        """Get all statistics for the advanced measurement item.
        Gets all statistical data when statistics are enabled, or 'OFF' when disabled.
        """,
        preprocess_reply=lambda v: v.strip(),
        separator=None,
    )

    statistics_current = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? CURRent",
        """Get the current statistical value in NR3 format (scientific notation, e.g., 1.23E+2).""",
        get_process=lambda v: float(v) if str(v).strip() != "OFF" else str(v).strip(),
    )

    statistics_mean = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MEAN",
        """Get the mean statistical value in NR3 format (scientific notation, e.g., 1.23E+2).""",
        get_process=lambda v: float(v) if str(v).strip() != "OFF" else str(v).strip(),
    )

    statistics_maximum = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MAXimum",
        """Get the maximum statistical value in NR3 format (scientific notation, e.g., 1.23E+2).""",
        get_process=lambda v: float(v) if str(v).strip() != "OFF" else str(v).strip(),
    )

    statistics_minimum = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? MINimum",
        """Get the minimum statistical value in NR3 format (scientific notation, e.g., 1.23E+2).""",
        get_process=lambda v: float(v) if str(v).strip() != "OFF" else str(v).strip(),
    )

    statistics_stddev = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? STDev",
        """Get the standard deviation of the statistics for the advanced measurement item.
        Returns the standard deviation in NR3 format (e.g., 1.23E+2).
        """,
        get_process=lambda v: float(v) if str(v).strip() != "OFF" else str(v).strip(),
    )

    statistics_count = Channel.measurement(
        ":MEASure:ADVanced:P{ch}:STATistics? COUNt",
        """Get the count of measurements used for statistics calculation.""",
        get_process=lambda v: int(float(v)) if str(v).strip() != "OFF" else str(v).strip(),
    )

    type = Channel.control(
        ":MEASure:ADVanced:P{ch}:TYPE?",
        ":MEASure:ADVanced:P{ch}:TYPE %s",
        """Control the type of advanced measurement (str).
        This controls the type of advanced measurement to be performed.
        """,
        validator=strict_discrete_set,
        values=["PKPK", "MAX", "MIN", "AMPL", "TOP", "BASE", "LEVELX", "CMEAN", "MEAN",
                "STDEV", "VSTD", "RMS", "CRMS", "MEDIAN", "CMEDIAN", "OVSN", "FPRE",
                "OVSP", "RPRE", "PER", "FREQ", "TMAX", "TMIN", "PWID", "NWID", "DUTY",
                "NDUTY", "WID", "NBWID", "DELAY", "TIMEL", "RISE", "FALL", "RISE10T90",
                "FALL90T10", "CCJ", "PAREA", "NAREA", "AREA", "ABSAREA", "CYCLES",
                "REDGES", "FEDGES", "EDGES", "PPULSES", "NPULSES", "PHA", "SKEW",
                "FRR", "FRF", "FFR", "FFF", "LRR", "LRF", "LFR", "LFF", "PACArea",
                "NACArea", "ACArea", "ABSACArea", "PSLOPE", "NSLOPE", "TSR", "TSF", "THR", "THF"],
    )

    value = Channel.control(
        ":MEASure:ADVanced:P{ch}:VALue?",
        ":MEASure:ADVanced:P{ch}:VALue %.6e",
        """Control the value of the advanced measurement item.
        This command retrieves the current value of the advanced measurement item.
        The value is returned in NR3 format (e.g., 1.23E+2).
        """,
    )


class MeasureChannel(Channel):
    """Unified measurement class for SDS1000xHD oscilloscope.

    This class combines Simple, Advanced, Gate, and Threshold measurement functionality.
    It provides a comprehensive interface for all measurement operations on the SDS1000xHD.
    """

    advanced_measurements = Channel.MultiChannelCreator(
        AdvancedMeasurementItem,
        list(range(1, 13)),  # P1 through P12
        prefix="advanced_p"
    )

    enabled = Channel.control(
        ":MEASure?",
        ":MEASure %s",
        "Control the state of the measurement function (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    advanced_mode_enabled = Channel.control(
        ":MEASure:MODE?",
        ":MEASure:MODE %s",
        "Control whether advanced measurement mode is enabled (bool).",
        validator=strict_discrete_set,
        values={True: "ADVanced", False: "SIMPle"},
        map_values=True,
    )

    advanced_line_number = Channel.control(
        ":MEASure:ADVanced:LINenumber?",
        ":MEASure:ADVanced:LINenumber %d",
        """Control the total number of advanced measurement items displayed
        (int strictly between 1 and 12).""",
        validator=strict_range,
        values=[1, 12],
        cast=int,
    )

    statistics_enabled = Channel.control(
        ":MEASure:ADVanced:STATistics?",
        ":MEASure:ADVanced:STATistics %s",
        "Control whether statistics are enabled for measurements (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    # Simple measurement properties
    simple_source = Channel.control(
        ":MEASure:SIMPle:SOURce?",
        ":MEASure:SIMPle:SOURce %s",
        "Control the source for simple measurements.",
        validator=strict_discrete_set,
        values=["CHANnel1", "CHANnel2", "CHANnel3", "CHANnel4",
                "FUNCtion1", "FUNCtion2", "FUNCtion3", "FUNCtion4"],
    )

    def get_simple_value(self, measurement_type):
        """Get the value of a specific simple measurement type.

        This method retrieves the current value of the specified simple measurement type.

        :param str measurement_type: The measurement type to query. Valid values are:
            PKPK, MAX, MIN, AMPL, TOP, BASE, LEVELX, CMEAN, MEAN,
            STDEV, VSTD, RMS, CRMS, MEDIAN, CMEDIAN, OVSN, FPRE,
            OVSP, RPRE, PER, FREQ, TMAX, TMIN, PWID, NWID, DUTY,
            NDUTY, WID, NBWID, DELAY, TIMEL, RISE, FALL, RISE20T80,
            FALL80T20, CCJ, PAREA, NAREA, AREA, ABSAREA, CYCLES,
            REDGES, FEDGES, EDGES, PPULSES, NPULSES, PACArea,
            NACArea, ACArea, ABSACArea, ALL

            Note: "ALL" returns all measurement values of all measurement types
            except for delay measurements.
        :return: The measurement value in NR3 format (e.g., 1.23E+2) for
            individual measurements, or a string containing all values
            when measurement_type is "ALL"
        :rtype: float or str
        """
        if measurement_type == "ALL":
            # For ALL, return the raw string response
            return self.ask(f":MEASure:SIMPle:VALue? {measurement_type}").strip()
        else:
            # For individual measurements, use values() to get proper float conversion
            return self.values(f":MEASure:SIMPle:VALue? {measurement_type}")[0]

    simple_value_all = Channel.measurement(
        ":MEASure:SIMPle:VALue? ALL",
        """Get all simple measurement values.
        This command retrieves all measurement values of all measurement types
        except for delay measurements.""",
    )

    simple_item = Channel.setting(
        ":MEASure:SIMPle:ITEM %s,%s",
        """Set the simple measurement item.

        This command sets the type of simple measurement and its state.
        Takes a tuple of (item, state) where:
        - item (str): The measurement item to set. Valid values are:
        PKPK, MAX, MIN, AMPL, TOP, BASE, LEVELX, CMEAN, MEAN,
        STDEV, VSTD, RMS, CRMS, MEDIAN, CMEDIAN, OVSN, FPRE,
        OVSP, RPRE, PER, FREQ, TMAX, TMIN, PWID, NWID, DUTY,
        NDUTY, WID, NBWID, DELAY, TIMEL, RISE, FALL, RISE20T80,
        FALL80T20, CCJ, PAREA, NAREA, AREA, ABSAREA, CYCLES,
        REDGES, FEDGES, EDGES, PPULSES, NPULSES, PACArea,
        NACArea, ACArea, ABSACArea
        - state (str): The state of the measurement item (ON or OFF).
        """
    )

    # Simple measurement methods
    def clear_simple(self):
        """Clear simple measurements."""
        self.write(":MEASure:SIMPle:CLEar")

    # Advanced measurement methods
    def clear_advanced(self):
        """Clear advanced measurements."""
        self.write(":MEASure:ADVanced:CLEar")

    def reset_statistics(self):
        """Reset statistics for advanced measurements."""
        self.write(":MEASure:ADVanced:STATistics:RESet")


class AcquisitionChannel(Channel):
    """Acquisition channel for SDS1000xHD oscilloscope.

    This class provides comprehensive acquisition control for the SDS1000xHD oscilloscope
    including acquisition modes, memory management, sampling, and data format settings.
    """

    fast_mode_enabled = Channel.control(
        ":ACQuire:AMODe?",
        ":ACQuire:AMODe %s",
        """Control whether fast capture mode is enabled (bool).

        When True, uses high-speed waveform capture rate to help capture signal anomalies.
        When False, uses standard capture rate.""",
        validator=strict_discrete_set,
        values={True: "FAST", False: "SLOW"},
        map_values=True,
    )

    interpolation_enabled = Channel.control(
        ":ACQuire:INTerpolation?",
        ":ACQuire:INTerpolation %s",
        "Control whether acquisition interpolation is enabled (bool). "
        "When True, uses sinx/x (sinc) interpolation. When False, uses linear interpolation.",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    memory_management = Channel.control(
        ":ACQuire:MMANagement?",
        ":ACQuire:MMANagement %s",
        """Control memory management mode (str).

        Options:
        - 'AUTO': Maintain maximum sampling rate, automatically set memory depth and
                  sampling rate according to time base.
        - 'FSRate': Fixed Sampling Rate mode - maintain specified sampling rate and
                    automatically set memory depth according to time base.
        - 'FMDepth': Fixed Memory Depth mode - automatically set sampling rate
                     according to storage depth and time base.""",
        validator=strict_discrete_set,
        values=["AUTO", "FSRate", "FMDepth"],
    )

    plot_mode = Channel.control(
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
    )

    memory_depth = Channel.control(
        ":ACQuire:MDEPth?",
        ":ACQuire:MDEPth %s",
        """Control the memory depth for acquisition (str).
        Sets the maximum number of sample points that can be stored.""",
        validator=strict_discrete_set,
        values=["AUTO", "14K", "140K", "1.4M", "14M"],
    )

    count = Channel.control(
        ":ACQuire:NUMacq?",
        ":ACQuire:NUMacq %d",
        """Control the number of acquisitions for averaging mode
        (int strictly between 1 and 1000000).""",
        validator=strict_range,
        values=[1, 1000000],
        cast=int,
    )

    points = Channel.measurement(
        ":ACQuire:POINts?",
        "Get the number of sampled points of the current waveform on the screen (int).",
        cast=int,
    )

    resolution_high_enabled = Channel.control(
        ":ACQuire:RESolution?",
        ":ACQuire:RESolution %s",
        """Control whether high resolution mode is enabled (bool).
        When True, uses 10-bit resolution. When False, uses 8-bit resolution.""",
        validator=strict_discrete_set,
        values={True: "10Bits", False: "8Bits"},
        map_values=True,
    )

    sequence_mode = Channel.control(
        ":ACQuire:SEQuence?",
        ":ACQuire:SEQuence %s",
        "Control sequence acquisition mode (bool).",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    sequence_count = Channel.control(
        ":ACQuire:SEQuence:COUNt?",
        ":ACQuire:SEQuence:COUNt %d",
        """Control the number of acquisition segments for sequence mode (int strictly between 1 and 1000).""",
        validator=strict_range,
        values=[1, 1000],
        cast=int,
    )

    sample_rate = Channel.measurement(
        ":ACQuire:SRATe?",
        "Get the current sample rate in samples per second (float).",
    )

    type = Channel.control(
        ":ACQuire:TYPE?",
        ":ACQuire:TYPE %s",
        """Control acquisition type and averaging settings (str).

        Options:
        - 'NORMal': Normal acquisition mode
        - 'PEAK': Peak detect mode
        - 'AVERage': Averaging mode
        - 'ERES': Enhanced resolution mode""",
        validator=strict_discrete_set,
        values=["NORMal", "PEAK", "AVERage", "ERES"],
        get_process=lambda v: v.strip().split(',')[0],  # Extract base type from response
    )


class TimebaseChannel(Channel):
    """Timebase channel for SDS1000xHD oscilloscope.

    This class provides comprehensive timebase control for the SDS1000xHD oscilloscope.
    """

    delay = Channel.control(
        ":TIMebase:DELay?",
        ":TIMebase:DELay %.6e",
        "Control the horizontal trigger delay in seconds (float).",
    )

    reference = Channel.control(
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
    )

    reference_position = Channel.control(
        ":TIMebase:REFerence:POSition?",
        ":TIMebase:REFerence:POSition %d",
        """Control the horizontal reference center when the reference strategy is DELay
        (int strictly between 0 and 100).
        This controls the horizontal reference center as a percentage of the display width.
        The value represents the position from the left edge of the display.""",
        validator=strict_range,
        values=[0, 100],
        cast=int,
    )

    scale = Channel.control(
        ":TIMebase:SCALe?",
        ":TIMebase:SCALe %.6e",
        """Control the horizontal scale per division for the main window
        (float strictly between 200e-12 and 1000).
        Note: Due to the limitation of the expansion strategy, when the time base is set
        from large to small, it will automatically adjust to the minimum time base that
        can be set currently.""",
        validator=strict_range,
        values=[200e-12, 1000],
    )

    window = Channel.control(
        ":TIMebase:WINDow?",
        ":TIMebase:WINDow %s",
        """Control the zoomed window state (bool).
        This command turns on or off the zoomed window.
        The query returns the state of the zoomed window.""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    window_delay = Channel.control(
        ":TIMebase:WINDow:DELay?",
        ":TIMebase:WINDow:DELay %.6e",
        """Control the horizontal position in the zoomed view of the main sweep
        (float strictly between -5.0e5 and 5.0e5).
        This controls the horizontal delay of the zoomed window relative to the main sweep.
        The delay value must keep the zoomed view window within the main sweep range.
        When the zoomed window is off, this command is invalid.""",
        validator=strict_range,
        values=[-5.0e5, 5.0e5],
    )

    window_scale = Channel.control(
        ":TIMebase:WINDow:SCALe?",
        ":TIMebase:WINDow:SCALe %.6e",
        """Control the horizontal scale per division for the zoomed window
        (float strictly between 200e-12 and 1000).
        This controls the zoomed window horizontal scale (seconds/division).""",
        validator=strict_range,
        values=[200e-12, 1000],
    )


class TriggerChannel(Channel):
    """Trigger channel for SDS1000xHD oscilloscope.

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
        """,
    )

    mode = Channel.control(
        ":TRIGger:MODE?",
        ":TRIGger:MODE %s",
        """Control the trigger mode.

        Available options:

        - AUTO: Oscilloscope searches for trigger signal. If satisfied, shows 'Trig'd'
          and stable waveform. Otherwise shows 'Auto' with unstable waveform.
        - NORMal: Oscilloscope waits for trigger signal. If satisfied, shows 'Trig'd'
          and stable waveform. Otherwise shows 'Ready' with last triggered waveform.
        - SINGle: Single trigger mode. Oscilloscope waits for trigger, then stops
          scanning after trigger is satisfied.
        - FTRIG: Force trigger to acquire a frame regardless of trigger conditions.
        """,
        validator=strict_discrete_set,
        values=["AUTO", "NORMal", "SINGle", "FTRIG"],
    )

    status = Channel.measurement(
        ":TRIGger:STATus?",
        docs="""Get the current trigger status, such as STOP, READY, ARM, TD, WAIT, etc.""",
    )

    type = Channel.measurement(
        ":TRIGger:TYPE?",
        docs="""Get the current trigger type as a dict with keys:
        - "type": trigger type (EDGE, SLOPe, PULSe, VIDeo, WINDow, INTerval, DROPout,
        RUNT, PATTern, QUALified, DELay, NEDGe, SHOLd, IIC, SPI, UART, CAN, LIN, etc.)
        """,
    )

    # EDGE trigger specific measurements
    edge_coupling = Channel.control(
        ":TRIGger:EDGE:COUPling?",
        ":TRIGger:EDGE:COUPling %s",
        """Control the coupling mode of the edge trigger.""",
        validator=strict_discrete_set,
        values=["DC", "AC", "LFREJect", "HFREJect"],
    )

    edge_hld_event = Channel.control(
        ":TRIGger:EDGE:HLDEVent?",
        ":TRIGger:EDGE:HLDEVent %d",
        """Control the number of holdoff events for edge trigger
        (int strictly between 1 and 100000000).
        The holdoff event count determines how many trigger events to ignore
        before allowing the next trigger to occur.
        """,
        validator=strict_range,
        values=[1, 100000000],
        cast=int,
    )

    edge_hld_time = Channel.control(
        ":TRIGger:EDGE:HLDTime?",
        ":TRIGger:EDGE:HLDTime %.6e",
        """Control the holdoff time for edge trigger (float strictly between 8e-9 and 30).
        This controls the holdoff time of the edge trigger in seconds.
        The holdoff time determines how long to wait after a trigger event before
        allowing the next trigger to occur.
        """,
        validator=strict_range,
        values=[8e-9, 30],
    )

    edge_hld_off = Channel.control(
        ":TRIGger:EDGE:HOLDoff?",
        ":TRIGger:EDGE:HOLDoff %s",
        """Control the holdoff type for edge trigger (str).

        Available options:
        - 'OFF': Turn off holdoff
        - 'EVENTS': Use event count-based holdoff
        - 'TIME': Use time-based holdoff""",
        validator=strict_discrete_set,
        values=["OFF", "EVENTS", "TIME"],
        get_process=lambda v: v.upper(),
    )

    edge_hld_start = Channel.control(
        ":TRIGger:EDGE:HSTart?",
        ":TRIGger:EDGE:HSTart %s",
        """Control the initial position of the edge trigger holdoff.""",
        validator=strict_discrete_set,
        values=["LAST_TRIG", "ACQ_START"],
    )

    edge_high_impedance = Channel.control(
        ":TRIGger:EDGE:IMPedance?",
        ":TRIGger:EDGE:IMPedance %s",
        """Control whether edge trigger uses high impedance (bool).

        When True, uses 1MΩ high impedance input.
        When False, uses 50Ω low impedance input.""",
        validator=strict_discrete_set,
        values={True: "ONEMeg", False: "FIFTy"},
        map_values=True,
    )

    edge_level = Channel.control(
        ":TRIGger:EDGE:LEVel?",
        ":TRIGger:EDGE:LEVel %.6e",
        """Control the trigger level of the edge trigger.
        This controls the trigger level of the edge trigger in volts.
        For SDS1000X HD models, the range is:
        [-4.1*vertical_scale-vertical_offset, 4.1*vertical_scale-vertical_offset]
        See programming manual for other models.
        """,
    )

    edge_noise_reject = Channel.control(
        ":TRIGger:EDGE:NREJect?",
        ":TRIGger:EDGE:NREJect %s",
        """Control the noise rejection for edge trigger (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    edge_slope = Channel.control(
        ":TRIGger:EDGE:SLOPe?",
        ":TRIGger:EDGE:SLOPe %s",
        """Control the slope of the edge trigger.""",
        validator=strict_discrete_set,
        values=["RISing", "FALLing", "ALTernate"],
    )

    edge_source = Channel.control(
        ":TRIGger:EDGE:SOURce?",
        ":TRIGger:EDGE:SOURce %s",
        """Control the trigger source of the edge trigger.""",
        validator=strict_discrete_set,
        values=["C1", "C2", "C3", "C4", "D0", "D1", "D2", "D3", "D4", "D5", "D6", "D7",
                "D8", "D9", "D10", "D11", "D12", "D13", "D14", "D15", "EX", "EX5", "LINE"],
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


class SDS1000XHD(SCPIMixin, Instrument):
    """Represents the SIGLENT SDS1000xHD Oscilloscope.

    The SDS1000X-HD series are high-definition oscilloscopes with enhanced
    measurement capabilities and improved user interface. This implementation
    supports common oscilloscope operations including waveform acquisition,
    measurements, and trigger control.
    """

    # Child definitions moved to top per maintainer feedback
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

    # Acquisition subsystem
    acquisition = Instrument.ChannelCreator(AcquisitionChannel, "")

    # Measurement subsystem
    measure = Instrument.ChannelCreator(MeasureChannel, "")

    # Timebase subsystem
    timebase = Instrument.ChannelCreator(TimebaseChannel, "")

    # Trigger subsystem
    trigger = Instrument.ChannelCreator(TriggerChannel, "")

    def __init__(self, adapter, name="Siglent SDS1000xHD Oscilloscope", timeout=2000,
                 chunk_size=20*1024*1024, **kwargs):
        super().__init__(adapter, name, timeout=timeout, chunk_size=chunk_size, **kwargs)

    def auto_setup(self):
        """Perform automatic setup of the oscilloscope."""
        self.write(":AUToset")

    def clear_sweeps_acq(self):
        """Clear accumulated sweeps using ACQuire command."""
        self.write(":ACQuire:CSWeep")
