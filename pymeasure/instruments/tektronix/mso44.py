#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from pymeasure.instruments import Instrument, SCPIMixin, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pyvisa.errors import VisaIOError
from enum import Enum
import numpy as np
import time


class MeasurementType(Enum):
    ACCOMMONMODE = "ACCOMMONMODE"
    ACPR = "ACPR"
    ACRMS = "ACRMS"
    AMPLITUDE = "AMPLITUDE"
    AREA = "AREA"
    BASE = "BASE"
    BITAMPLITUDE = "BITAMPLITUDE"
    BITHIGH = "BITHIGH"
    BITLOW = "BITLOW"
    BURSTWIDTH = "BURSTWIDTH"
    CCJITTER = "CCJITTER"
    COMMONMODE = "COMMONMODE"
    CPOWER = "CPOWER"
    DATARATE = "DATARATE"
    DCD = "DCD"
    DDJ = "DDJ"
    DDRAOS = "DDRAOS"
    DDRAOSPERTCK = "DDRAOSPERTCK"
    DDRAOSPERUI = "DDRAOSPERUI"
    DDRAUS = "DDRAUS"
    DDRAUSPERTCK = "DDRAUSPERTCK"
    DDRAUSPERUI = "DDRAUSPERUI"
    DDRHOLDDIFF = "DDRHOLDDIFF"
    DDRSETUPDIFF = "DDRSETUPDIFF"
    DDRTCHABS = "DDRTCHABS"
    DDRTCHAVERAGE = "DDRTCHAVERAGE"
    DDRTCKAVERAGE = "DDRTCKAVERAGE"
    DDRTCLABS = "DDRTCLABS"
    DDRTCLAVERAGE = "DDRTCLAVERAGE"
    DDRTERRMN = "DDRTERRMN"
    DDRTERRN = "DDRTERRN"
    DDRTJITCC = "DDRTJITCC"
    DDRTJITDUTY = "DDRTJITDUTY"
    DDRTJITPER = "DDRTJITPER"
    DDRTPST = "DDRTPST"
    DDRTRPRE = "DDRTRPRE"
    DDRTWPRE = "DDRTWPRE"
    DDRVIXAC = "DDRVIXAC"
    DDRTDQSCK = "DDRTDQSCK"
    DELAY = "DELAY"
    DJ = "DJ"
    DJDIRAC = "DJDIRAC"
    DPMPSIJ = "DPMPSIJ"
    EYEHIGH = "EYEHIGH"
    EYELOW = "EYELOW"
    FALLSLEWRATE = "FALLSLEWRATE"
    FALLTIME = "FALLTIME"
    FREQUENCY = "FREQUENCY"
    F2 = "F2"
    F4 = "F4"
    F8 = "F8"
    HEIGHT = "HEIGHT"
    HEIGHTBER = "HEIGHTBER"
    HIGH = "HIGH"
    HIGHTIME = "HIGHTIME"
    HOLD = "HOLD"
    IMDAANGLE = "IMDAANGLE"
    IMDADIRECTION = "IMDADIRECTION"
    IMDADQ0 = "IMDADQ0"
    IMDAEFFICIENCY = "IMDAEFFICIENCY"
    IMDAHARMONICS = "IMDAHARMONICS"
    IMDAMECHPWR = "IMDAMECHPWR"
    IMDAPOWERQUALITY = "IMDAPOWERQUALITY"
    IMDASPEED = "IMDASPEED"
    IMDASYSEFF = "IMDASYSEFF"
    IMDATORQUE = "IMDATORQUE"
    JITTERSUMMARY = "JITTERSUMMARY"
    J2 = "J2"
    J9 = "J9"
    LOW = "LOW"
    LOWTIME = "LOWTIME"
    MAXIMUM = "MAXIMUM"
    MEAN = "MEAN"
    MINIMUM = "MINIMUM"
    NDUTY = "NDUTY"
    NOVERSHOOT = "NOVERSHOOT"
    NPERIOD = "NPERIOD"
    NPJ = "NPJ"
    NWIDTH = "NWIDTH"
    OBW = "OBW"
    PDUTY = "PDUTY"
    PERIOD = "PERIOD"
    PHASE = "PHASE"
    PHASENOISE = "PHASENOISE"
    PJ = "PJ"
    PK2PK = "PK2PK"
    POVERSHOOT = "POVERSHOOT"
    PWIDTH = "PWIDTH"
    QFACTOR = "QFACTOR"
    RISESLEWRATE = "RISESLEWRATE"
    RISETIME = "RISETIME"
    RJ = "RJ"
    RJDIRAC = "RJDIRAC"
    RMS = "RMS"
    SETUP = "SETUP"
    SKEW = "SKEW"
    SRJ = "SRJ"
    SSCFREQDEV = "SSCFREQDEV"
    SSCMODRATE = "SSCMODRATE"
    TIE = "TIE"
    TIMEOUTSIDELEVEL = "TIMEOUTSIDELEVEL"
    TIMETOMAX = "TIMETOMAX"
    TIMETOMIN = "TIMETOMIN"
    TJBER = "TJBER"
    TNTRATIO = "TNTRATIO"
    TOP = "TOP"
    UNITINTERVAL = "UNITINTERVAL"
    VDIFFXOVR = "VDIFFXOVR"
    WBGDDT = "WBGDDT"
    WBGDIODEDDT = "WBGDIODEDDT"
    WBGEOFF = "WBGEOFF"
    WBGEON = "WBGEON"
    WBGERR = "WBGERR"
    WBGIPEAK = "WBGIPEAK"
    WBGIRRM = "WBGIRRM"
    WBGQOSS = "WBGQOSS"
    WBGQRR = "WBGQRR"
    WBGTDOFF = "WBGTDOFF"
    WBGTDON = "WBGTDON"
    WBGTF = "WBGTF"
    WBGTON = "WBGTON"
    WBGTOFF = "WBGTOFF"
    WBGTR = "WBGTR"
    WBGTRR = "WBGTRR"
    WBGTDT = "WBGTDT"
    WBGVPEAK = "WBGVPEAK"
    WIDTH = "WIDTH"
    WIDTHBER = "WIDTHBER"


class Measurement:
    """Represents a single measurement on the Tektronix MSO44 oscilloscope."""

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    @property
    def type(self):
        """Get the type of the measurement."""
        return self.instrument.ask(f"MEASUrement:MEAS{self.number}:TYPe?")

    @property
    def source1(self):
        """Get the first source of the measurement."""
        return self.instrument.ask(f"MEASUrement:MEAS{self.number}:SOUrce1?")

    @property
    def source2(self):
        """Get the second source of the measurement (if applicable)."""
        return self.instrument.ask(f"MEASUrement:MEAS{self.number}:SOUrce2?")

    @property
    def value(self):
        """Get the value of the measurement."""
        return float(self.instrument.ask(f"MEASUrement:MEAS{self.number}:VALue?"))

    @property
    def xunit(self):
        """Get the units of the measurement."""
        return self.instrument.ask(f"MEASUrement:MEAS{self.number}:XUNIt?")

    @property
    def yunit(self):
        """Get the units of the measurement."""
        return self.instrument.ask(f"MEASUrement:MEAS{self.number}:YUNIt?")

    def __repr__(self):
        return (f"Measurement(type={self.type}, source1={self.source1}, source2={self.source2}, "
                f"value={self.value}, xunit={self.xunit}, yunit={self.yunit})")


class MSO44Channel(Channel):
    """A channel of the Tektronix MSO44 oscilloscope."""

    enabled = Channel.control(
        "SELect:CH{ch}?", "SELect:CH{ch} %d",
        """Control whether the channel is enabled (boolean True or False).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True
    )

    scale = Channel.control(
        "CH{ch}:SCAle?", "CH{ch}:SCAle %g",
        """Control the vertical scale of the channel in volts/div (float strictly from 500e-6
        to 10).""",
        validator=strict_range,
        values=[500e-6, 10]
    )

    position = Channel.control(
        "CH{ch}:POSition?", "CH{ch}:POSition %g",
        """Control the vertical position of the channel in divisions (float strictly from -5
        to 5).""",
        validator=strict_range,
        values=[-5, 5]
    )

    offset = Channel.control(
        "CH{ch}:OFFSet?", "CH{ch}:OFFSet %g",
        """Control the vertical offset of the channel in volts (float strictly from -10
        to 10).""",
        validator=strict_range,
        values=[-10, 10]
    )

    coupling = Channel.control(
        "CH{ch}:COUPling?", "CH{ch}:COUPling %s",
        """Control the vertical coupling of the channel (string "AC", "DC", or "DCR").""",
        validator=strict_discrete_set,
        values=["AC", "DC", "DCR"],
    )

    termination = Channel.control(
        "CH{ch}:TERmination?", "CH{ch}:TERmination %s",
        """Control the vertical termination of the channel (can be either 50 or 1e6 for
        50 Ohm and 1 MOhm respectively).""",
        validator=strict_discrete_set,
        values=[50, 1e6],
    )

    label_name = Channel.control(
        "CH{ch}:LABel:NAMe?", "CH{ch}:LABel:NAMe %s",
        """Control the label name of the channel (string)."""
    )

    parameters = Channel.measurement(
        "CH{ch}?",
        """Get the vertical parameters of the channel."""
    )

    clipping = Channel.measurement(
        "CH{ch}:CLIPping?",
        """Measure whether the specified channel’s input signal is clipping (exceeding) the
        channel vertical scale setting. 0 indicates the channel is not clipping. 1 indicates the
        channel is clipping."""
    )


class MSO44(SCPIMixin, Instrument):
    """Control the Tektronix MSO44 Oscilloscope."""

    # Create channel interfaces
    ch1 = Instrument.ChannelCreator(MSO44Channel, 1)
    ch2 = Instrument.ChannelCreator(MSO44Channel, 2)
    ch3 = Instrument.ChannelCreator(MSO44Channel, 3)
    ch4 = Instrument.ChannelCreator(MSO44Channel, 4)

    def __init__(self, adapter, name="Tektronix MSO44 Oscilloscope", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )

    def wait_for_idle(self, timeout=30, polling_interval=0.5):
        """
                Wait for the oscilloscope to become idle.

                :param timeout: Maximum time to wait in seconds (default: 30)
                :param polling_interval: Time between checks in seconds (default: 0.1)
                :return: True if the oscilloscope became idle, False if the timeout was reached
                """
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                if int(self.ask("*OPC?")) == 1:
                    return True
            except VisaIOError:
                pass  # Ignore timeout errors during polling
            time.sleep(polling_interval)
        raise TimeoutError("Oscilloscope did not become idle within the timeout period")

    @property
    def trigger_source(self):
        """Control the trigger source (e.g., "CH1", "CH2", "MATH1", etc.)."""
        return self.ask("TRIGger:A:EDGE:SOUrce?")

    @trigger_source.setter
    def trigger_source(self, value):
        valid_options = ['CH1', 'CH2', 'CH3', 'CH4', 'CH1_D', 'CH2_D', 'CH3_D', 'CH4_D', 'MATH1',
                         'MATH2', 'MATH3', 'MATH4', 'REF1', 'REF2', 'REF3', 'REF4', 'REF1_D',
                         'REF2_D', 'REF3_D', 'REF4_D']
        if value not in valid_options:
            raise ValueError(f"Invalid trigger source. Must be one of {', '.join(valid_options)}")
        self.write(f"TRIGger:A:EDGE:SOUrce {value}")

    @property
    def trigger_level(self):
        """Control the trigger level in Volts (float strictly from -5 to 5)."""
        source = self.trigger_source
        return float(self.ask(f"TRIGger:A:LEVel:{source}?"))

    @trigger_level.setter
    def trigger_level(self, value):
        if not -5 <= value <= 5:
            raise ValueError("Trigger level must be between -5V and 5V")
        source = self.trigger_source
        self.write(f"TRIGger:A:LEVel:{source} {value}")

    @property
    def trigger_slope(self):
        """Control the trigger slope (string 'RISE', 'FALL', or 'EITHER')"""
        return self.ask("SEARCH:SEARCH:TRIGger:A:EDGE:SLOpe?")

    @trigger_slope.setter
    def trigger_slope(self, value):
        valid_options = ['RISE', 'FALL', 'EITHER']
        if value not in valid_options:
            raise ValueError(f"Invalid trigger slope. Must be one of {', '.join(valid_options)}")
        self.write(f"SEARCH:SEARCH:TRIGger:A:EDGE:SLOpe {value}")

    @property
    def timebase(self):
        """Control the timebase in seconds (float strictly from 200 ps to 1 ks)."""
        return float(self.ask("HORizontal:SCAle?"))

    @timebase.setter
    def timebase(self, value):
        if not 200e-12 <= value <= 1e3:
            raise ValueError("Timebase must be between 200 ps and 1 ks")
        self.write(f"HORizontal:SCAle {value}")

    @property
    def display_mode(self):
        """Control the display mode (string 'OVErlay','OVE', 'STAcked', or 'STA')"""
        return self.ask("DISplay:WAVEView1:VIEWStyle?")

    @display_mode.setter
    def display_mode(self, value):
        valid_options = ['OVErlay', 'OVE', 'STAcked', 'STA']
        if value not in valid_options:
            raise ValueError(f"Invalid display mode. Must be one of {', '.join(valid_options)}")
        self.write(f"DISplay:WAVEView1:VIEWStyle {value}")

    def start_acquisition(self):
        self.write("ACQuire:STATE RUN")

    def stop_acquisition(self):
        self.write("ACQuire:STATE STOP")

    def get_waveforms(self, sources, start=1, stop=None, encoding="ASCII", width=2):
        """Get the waveform data from the specified sources.

        :param sources: The sources for the waveform data. Must be a list, e.g. ["CH1"] or
                ["CH1", "CH2", "MATH1"].
        :param start: The start point for waveform transfer. Ranges from 1 to the record length
                (default 1).
        :param stop: The stop point for waveform transfer. Ranges from 1 to the record length
                (default None = transfer complete waveforms).
        :param encoding: The encoding for waveform data (string "ASCII" or "BIN").
        :param width: The byte width for waveform data = number of bytes per point (1 or 2).
                Default is 2.

        :return: A tuple containing the sources, encoding, preamble (information such as the
                horizontal scale, the vertical scale, and other settings in effect when the
                waveform was created), and data of the waveforms.

        .. seealso:: :meth:`process_waveforms`
        """
        # 1. Set the waveform data source
        self.write(f"DATa:SOUrce {','.join(sources)}")

        # 2. Set the start and stop points for waveform transfer
        self.write(f"DATa:STARt {start}")
        stop = stop if stop else self.ask("HORizontal:MODe:RECOrdlength?")
        self.write(f"DATa:STOP {stop}")

        # 3. Set the encoding for waveform data
        self.write(f"DATa:ENCdg {encoding}")

        # 4. Set the byte width for waveform data
        self.write(f"DATa:WIDth {width}")

        preambles = {}
        channel_data = {}

        # 5. Query the waveform preamble and data for each channel
        for source in sources:
            self.write(f"DATa:SOUrce {source}")
            preambles[source] = self.ask("WFMOutpre?")
            channel_data[source] = self.ask("CURVe?")

        return sources, encoding, preambles, channel_data

    @staticmethod
    def process_waveforms(sources, encoding, preambles, channel_data):
        """Process the waveform data generated by :meth:`get_waveforms`.

        :param sources: The sources for the waveform data.
        :param encoding: The encoding for waveform data.
        :param preambles: The preamble information for the waveform data, one for each channel.
        :param channel_data: The channel data for the waveform data, one for each channel.

        :return: A dictionary containing the processed waveforms (times and voltages).
        """
        processed_waveforms = {}

        for source in sources:
            preamble = preambles[source]
            data = channel_data[source]

            preamble_parts = preamble.split(';')

            # Parse preamble
            preamble_dict = {
                'BYT_NR': int(preamble_parts[0]),
                'BIT_NR': int(preamble_parts[1]),
                'ENCDG': preamble_parts[2],
                'BN_FMT': preamble_parts[3],
                'BYT_OR': preamble_parts[4],
                'WFID': preamble_parts[6],
                'NR_PT': int(preamble_parts[7]),
                'PT_FMT': preamble_parts[8],
                'XUNIT': preamble_parts[10],
                'XINCR': float(preamble_parts[11]),
                'XZERO': float(preamble_parts[12]),
                'PT_OFF': int(preamble_parts[13]),
                'YUNIT': preamble_parts[14],
                'YMULT': float(preamble_parts[15]),
                'YOFF': float(preamble_parts[16]),
                'YZERO': float(preamble_parts[17]),
            }

            # Extract channel-specific information
            xincr = preamble_dict['XINCR']
            xzero = preamble_dict['XZERO']
            pt_off = preamble_dict['PT_OFF']
            ymult = preamble_dict['YMULT']
            yoff = preamble_dict['YOFF']
            yzero = preamble_dict['YZERO']

            # Process data
            if encoding == "ASCII":
                samples = np.array([float(x) for x in data.split(',')])
            else:
                raise Exception("Binary data processing not implemented")

            # Apply correct scaling
            voltages = (samples - yoff) * ymult + yzero

            # Calculate times array
            times = np.arange(len(samples)) * xincr + xzero - (pt_off * xincr)

            processed_waveforms[source] = {
                'times': times,
                'voltages': voltages
            }

        return processed_waveforms

    def add_measurement(self, measurement_type: MeasurementType, source1, source2=None):
        """
        Add a measurement to the oscilloscope.

        :param measurement_type: The type of measurement (use MeasurementType enum)
        :param source1: The source for the measurement (e.g., "CH1", "MATH1", etc.)
        :param source2: The second source for the measurement (if applicable)
        :return: Measurement object
        """
        if not isinstance(measurement_type, MeasurementType):
            raise ValueError("Measurement type must be a MeasurementType enum")

        meas_number = self.get_measurement_count() + 1
        self.write(f"MEASUrement:ADDMEAS {measurement_type.value}")
        if source2 is not None:
            self.write(f"MEASUrement:MEAS{meas_number}:SOUrce1 {source1}")
            self.write(f"MEASUrement:MEAS{meas_number}:SOUrce2 {source2}")
        else:
            self.write(f"MEASUrement:MEAS{meas_number}:SOUrce {source1}")

        measurement = Measurement(self, meas_number)
        return measurement

    def get_measurement(self, measurement_number):
        """
        Get a Measurement object.

        :param measurement_number: The measurement number
        :return: Measurement object
        """
        count = self.get_measurement_count()
        if not 1 <= measurement_number <= count:
            raise ValueError(f"Measurement number must be between 1 and {count}")

        return Measurement(self, measurement_number)

    def get_all_measurements(self):
        """
        Get all active measurements.

        :return: A list of Measurement objects
        """
        meas_list_str = self.ask("MEASUrement:LIST?").strip()
        meas_list_str = None if (meas_list_str == "" or meas_list_str == "NONE") else meas_list_str
        return meas_list_str.split(",") if meas_list_str else None

    def get_measurement_count(self):
        """Get the number of currently defined measurements."""
        measurements = self.get_all_measurements()
        return len(measurements) if measurements else 0

    def delete_measurement(self, measurement_number):
        """
        Delete a measurement.

        :param measurement_number: The measurement number
        """
        count = self.get_measurement_count()
        if not 1 <= measurement_number <= count:
            raise ValueError(f"Measurement number must be between 1 and {count}")

        self.write(f"MEASUrement:DELete {measurement_number}")

    def delete_all_measurements(self):
        """Clear all measurements."""
        self.write("MEASUrement:DELETEALL")

    def autoset(self):
        """Automatically set the oscilloscope settings."""
        self.write("AUTOSet EXECute")

    def reset(self):
        """Resets the device:
            - Recalls the default instrument setup.
            - Clears the current *DDT command.
            - Disables aliases (:ALIAS:STATE 0).
            - Disables the user password (for the *PUD command).
        """
        self.write("*RST")
