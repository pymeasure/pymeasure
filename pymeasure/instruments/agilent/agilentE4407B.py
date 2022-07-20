#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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


from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import (
    strict_discrete_range,
    strict_discrete_set,
    truncated_discrete_set,
    truncated_range,
)

from io import StringIO
import numpy as np
import pandas as pd


class AgilentE4407B(Instrument):
    """Represents the AgilentE4407B Spectrum Analyzer
    and provides a high-level interface for taking scans of
    high-frequency spectrums
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(resourceName, "Agilent E4407B Spectrum Analyzer", **kwargs)

    # frequency Setting commands
    start_frequency = Instrument.control(
        ":SENS:FREQ:STAR?",
        ":SENS:FREQ:STAR %g",
        """ A floating point property that represents the start frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
        cast=int,
    )
    stop_frequency = Instrument.control(
        ":SENS:FREQ:STOP?",
        ":SENS:FREQ:STOP %g",
        """ A floating point property that represents the stop frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
        cast=int,
    )

    frequency_step = Instrument.control(
        ":SENS:FREQ:CENT:STEP:INCR?",
        ":SENS:FREQ:CENT:STEP:INCR %g",
        """ A floating point property that represents the frequency step
        in Hz. This property can be set.
        """,
    )
    center_frequency = Instrument.control(
        ":SENS:FREQ:CENT?",
        ":SENS:FREQ:CENT %g",
        """ A floating point property that represents the center frequency
        in Hz. This property can be set.
        """,
        validator=truncated_range,
        values=[9000, 26500000000],
        cast=int,
    )

    span = Instrument.control(
        ":SENS:FREQ:SPAN?",
        ":SENS:FREQ:SPAN %g",
        """ A floating point property that represents the span
        in Hz. This property can be set.
        """,
    )

    def full_span(self):
        """Sets the span to the full span of the instrument."""
        self.write(":SENS:FREQ:SPAN:FULL")

    def last_span(self):
        """
        A command that sets the span to the previous span.
        """
        self.write(":SENS:FREQ:SPAN:PREV")

    # sweep commands
    frequency_points = Instrument.control(
        ":SENSe:SWEEp:POINts?",
        ":SENSe:SWEEp:POINts %g",
        """ An integer property that represents the number of frequency
        points in the sweep. This property can take values from 101 to 8192.
        """,
        validator=truncated_range,
        values=[101, 8192],
        cast=int,
    )
    sweep_time = Instrument.control(
        ":SENS:SWE:TIME?",
        ":SENS:SWE:TIME %g",
        """ A floating point property that represents the sweep time
        in seconds. This property can be set.
        """,
    )
    number_of_segments = Instrument.measurement(
        ":SENS:SWEep:SEGMent:COUNT?",
        """ An integer property that represents the number of segments
        in the sweep. This property is read-only.
        """,
    )
    set_all_segments_sst = Instrument.control(
        ":SENS:SWE:SEGM:DATA? SST",
        ":SENS:SWE:SEGM:DATA SST,%g",
        """ A command that sets all the segments of a sweep, at once, with a string.
        format is start, stop, rbw, vbw, points, time
        """,
    )
    set_all_segments_csp = Instrument.control(
        ":SENS:SWE:SEGM:DATA? CSP",
        ":SENS:SWE:SEGM:DATA CSP,%g",
        """ A command that sets all the segments of a sweep, at once, with a string.
        format is center, span, rbw, vbw, points, time
        """,
    )
    merge_segments_sst = Instrument.setting(
        ":SENS:SWE:SEGM:DATA:MERge SST %g",
        """
        A command that merges the data with current the segments of a sweep with a string.
        format is start, stop, rbw, vbw, points, time
        """,
    )
    merge_segments_csp = Instrument.setting(
        ":SENS:SWE:SEGM:DATA:MERge CSP %g",
        """
        A command that merges the data with current the segments of a sweep with a string.
        format is center, span, rbw, vbw, points, time
        """,
    )

    def delete_segments(self):
        """Deletes all the segmented sweep data."""
        self.write(":SENS:SWE:SEGM:DEL")

    delete_segment = Instrument.setting(
        ":SENS:SWE:SEGM:DEL %g",
        """
        Deletes the specifed segment of a sweep.""",
    )

    # Sensor commands
    resolution_bandwidth = Instrument.control(
        ":SENS:BAND:RES?",
        ":SENS:BAND:RES %g",
        """ A floating point property that represents the resolution bandwidth
        in Hz. This property can be set.
        """,
    )
    video_bandwidth = Instrument.control(
        ":SENS:BAND:VID?",
        ":SENS:BAND:VID %g",
        """ A floating point property that represents the video bandwidth
        in Hz. This property can be set.
        """,
    )
    resolution_bandwidth_auto = Instrument.control(
        ":SENS:BAND:RES:AUTO?",
        ":SENS:BAND:RES:AUTO %g",
        """ A boolean property that represents the resolution bandwidth
        auto mode. This property can be set.
        """,
    )
    video_bandwidth_auto = Instrument.control(
        ":SENS:BAND:VID:AUTO?",
        ":SENS:BAND:VID:AUTO %g",
        """ A boolean property that represents the video bandwidth
        auto mode. This property can be set.
        """,
    )
    video_resolution_bandwidth_ratio = Instrument.control(
        ":SENS:BAND:VID:RAT?",
        ":SENS:BAND:VID:RAT %g",
        """ A floating point property that represents the video to resolution
        bandwidth ratio. This property can be set.
        """,
    )
    video_resolution_bandwidth_ratio_auto = Instrument.control(
        ":SENS:BAND:VID:RAT:AUTO?",
        ":SENS:BAND:VID:RAT:AUTO %g",
        """ A boolean property that represents the video to resolution
        bandwidth ratio auto mode. This property can be set.
        """,
    )
    detector_auto = Instrument.control(
        ":SENS:DET:AUTO?",
        ":SENS:DET:AUTO %g",
        """ A boolean property that represents the detector auto mode.
        This property can be set.
        """,
    )
    detector_type = Instrument.control(
        ":SENS:DET:?",
        ":SENS:DET %g",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["NEG", "POS", "SAMPL", "AVER", "RMS"],
    )
    average_type = Instrument.control(
        ":SENS:AVER:TYPE?",
        ":SENS:AVER:TYPE %g",
        """ A string property that represents the average type. LPOW is log power
        and POW is linear power. This property can be set.
        """,
        validator=strict_discrete_set,
        values=["LPOW", "POW"],
    )

    emi_detector_type = Instrument.control(
        ":SENS:DET:EMI?",
        ":SENS:DET:EMI %g",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["QPE", "AVER", "OFF"],
    )
    emi_view_type = Instrument.control(
        ":SENS:DET:EMI:VIEW?",
        ":SENS:DET:EMI:VIEW %g",
        """ A string property that represents the detector type.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=["POS", "EMI"],
    )
    qp_detector_gain = Instrument.control(
        ":SENS:POW:QPG?",
        ":SENS:POW:QPG %g",
        """ Turn on or off the linear x10 gain stage in the quasi-peak and emi average detector only valid with the emi detector enabled.
        This property can be set.
        """,
        validator=strict_discrete_set,
        values=[0, 1, " ON", "OFF"],
    )
    input_attenuation = Instrument.control(
        ":SENS:POW:ATT?",
        ":SENS:POW:ATT %g",
        """ A floating point property that represents the input attenuation
        in dB. This property can be set.
        """,
        validator=truncated_discrete_set,
        values=[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65],
    )
    input_attenuation_auto = Instrument.control(
        ":SENS:POW:ATT:AUTO?",
        ":SENS:POW:ATT:AUTO %g",
        """ A boolean property that represents the input attenuation
        auto mode. This property can be set.
        """,
    )
    max_mixer_power = Instrument.control(
        ":SENS:POW:MIX:RANG?",
        ":SENS:POW:MIX:RANG %g",
        """ A floating point property that represents the maximum mixer power
        in dBm. This property can be set.
        """,
    )
    # system commands

    def reset(self):
        """
        A command that resets the instrument.
        """
        self.write("*RST")

    def preset(self):
        """Reset the instrument to the preset conditions."""
        self.write("SYST:PRES")

    def persistant_reset(self):
        """Reset the instrument persistant state vakues to there factory defaults."""
        self.write("SYST:PRES:PERS")

    def save_user_preset(self):
        """Save the current instrument state as a user preset."""
        self.write("SYST:PRES:USER:SAVE")

    def abort(self):
        """
        A command that aborts the sweep or measurement in progress.
        """
        self.write("ABOR")

    def hardware_configuration(self):
        """
        A command that returns information about the current hardware in the instrument.
        """
        self.write("SYS:CONF:HARD?")

    def system_configuration(self):
        """
        A command that returns information about the configuration in the instrument.
        """
        self.write("SYS:CONF:SYST?")

    recall = Instrument.setting(
        "*RCL %g",
        """Recall the instrument state from specified memory resgister.""",
        validator=strict_discrete_range,
        values=[2, 30],
    )
    SAVE = Instrument.setting(
        "*SAV %g",
        """Save the instrument state to specified memory register.""",
        validator=strict_discrete_range,
        values=[2, 30],
    )

    time = Instrument.control(
        ":SENS:SWE:TIME?",
        ":SENS:SWE:TIME %g",
        """Set the real time clock of the instrument. <hours>,<minutes>,<seconds>""",
    )

    date = Instrument.control(
        "SYS:DATE?",
        "SYS:DATE %g",
        """Set the date of the instrument. <year>,<month>,<day> ####,##,##""",
    )

    error_queue = Instrument.measurement(
        ":SYST:ERR?",
        """A string property that returns the error queue of the instrument.
        """,
    )

    options = Instrument.measurement(
        "SYS:OPT?",
        """A string property that returns the options of the instrument.
        """,
    )

    preset_type = Instrument.setting(
        ":SYST:PRES:TYPE %g",
        """ A string property that represents the preset type.
         can be set to FACT, USER, or MODE.
         """,
        validator=strict_discrete_set,
        values=["FACT", "USER", "MODE"],
    )
    # Calibration commands
    align_all = Instrument.control(
        ":CAL:ALL?",
        ":CAL:ALL",
        """align all the circuits of the instrument.
        requires cable to be connected from amot ref out
        """,
    )

    align_rf = Instrument.control(
        ":CAL:RF?",
        ":CAL:RF",
        """align the rf circuits of the instrument.
        requires cable to be connected from amot ref out
        """,
    )

    auto_rf_align = Instrument.control(
        ":CAL:AUTO:MODE?",
        ":CAL:AUTO:MODE %g",
        """ Detemines whether or not the RF alignment is included in the auto calibration.""",
        validator=strict_discrete_set,
        values=["ALL", "NRF"],
    )

    auto_align = Instrument.control(
        ":CAL:AUTO?",
        ":CAL:AUTO %g",
        """ Turns auto alignment on or off.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", 0, 1],
    )
    # configuration commands
    # display commands
    viewing_angle = Instrument.control(
        ":DISP:ANGL?",
        ":DISP:ANGL %g",
        """ A property that changes the veiwing angle of the instrument.""",
        validator=strict_discrete_range,
        values=[1, 7],
    )

    display_time_format = Instrument.control(
        ":DISP:ANN:CLOCK:DATE:FORMAT?",
        ":DISP:ANN:CLOCK:DATE:FORMAT %g",
        """ A property that represents the date format of the instrument.""",
        validator=strict_discrete_set,
        values=["MDY", "DMY"],
    )

    display_time = Instrument.control(
        ":DISP:ANN:CLOCK?",
        ":DISP:ANN:CLOCK %g",
        """Turn off or on the time display on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", 0, 1],
    )

    display_title = Instrument.control(
        ":DISP:ANN:TITLE:DATA?",
        ":DISP:ANN:TITLE:DATA %g",
        """Set the text of the title display on the instrument.""",
    )

    display = Instrument.setting(
        ":DISP:ENABLE %g",
        """Turn off or on the display on the instrument.""",
        validator=strict_discrete_set,
        values=["ON", "OFF", 0, 1],
    )
    # Mesurement commands
    # Fetch commands
    # Mass memory commands
    catalog = Instrument.measurement(
        ":MMEM:CAT? %g",
        """A command that returns the list of mass memory files in specified drive.""",
        validator=strict_discrete_set,
        values=["A:", "C:"],
    )

    def copy_file(self, source, destination):
        """
        A command that copies a file to another.
        """
        self.write(":MMEM:COPY %s,%s" % (source, destination))

    def send_file(self, filename, data_block):
        """
        A command that sends a file to the instrument.
        """
        self.write(f":MMEM:DATA {filename},{data_block}")

    recive_file = Instrument.measurement(
        ":MMEM:DATA? %g",
        """A command that returns the contents of a file.""",
    )
    delet_file = Instrument.setting(
        ":MMEM:DEL %g",
        """A command that deletes a file from the mass memory.""",
    )

    save_screen = Instrument.setting(
        ":MMEM:STOR:SCR %g",
        """Save the current screen to the specified mass memory. eg C:myscreen.gif""",
    )

    def get_screen(self):
        """
        A command that returns the contents of the screen.
        """
        self.save_screen("C:tempScreen.gif")
        data = self.recive_file("C:tempScreen.gif")
        self.delet_file("C:tempScreen.gif")
        return data

    # Format commands
    byte_order = Instrument.control(
        ":FORM:BORD?",
        ":FORM:BORD %g",
        """ A property that controls the binary data byte order for transfer.""",
        validator=strict_discrete_set,
        values=["NORM", "SWAP"],
    )

    num_format = Instrument.control(
        ":FORM:DATA?",
        ":FORM:DATA %g",
        """ A property that controls the numerical data format for transfer.""",
        validator=strict_discrete_set,
        values=["ASC", "ASCII", "INT,32", "REAL,32", "REAL,64"],
    )
    # hard copy commands
    # initaite commands
    # input commands
    # unit commands
    mesure_units = Instrument.control(
        ":UNIT:POW?",
        ":UNIT:POW %g",
        """ A property that controls the units for input, output, and display.""",
        validator=strict_discrete_set,
        values=["DBM", "DBMV", "DBUV", "V", "W"],
    )
    # trigger commands
    trigger_source = Instrument.control(
        ":TRIG:SOUR?",
        ":TRIG:SOUR %g",
        """ A property that controls the trigger source.""",
        validator=strict_discrete_set,
        values=["IMM", "VID", "LINE", "EXT"],
    )

    video_trigger_level = Instrument.control(
        ":TRIG:VID:LEV?",
        ":TRIG:VID:LEV %g",
        """ A property that controls the video trigger level.""",
    )

    # trace commands

    def copy_trace(self, source, destination):
        """Copy a trace from one trace to another."""
        source = strict_discrete_set(source, [1, 2, 3])
        destination = strict_discrete_set(destination, [1, 2, 3])
        self.write(f":COPY:TRAC TRACE{source},TRACE{destination}")

    # def transfer_trace(self, destination, trace_data):
    #     """Transfer a trace from the controller to the instrument."""

    #     destination = strict_discrete_set(destination, [1,2 , 3,])

    #     self.write(f":TRAC TRACE{source})

    def get_trace(self, trace):
        """Get a trace from the instrument."""
        trace = strict_discrete_set(trace, [1, 2, 3])
        return self.ask(f":TRAC? TRACE{trace}")

    get_raw_trace = Instrument.measurement(
        ":TRAC? rawtrace",
        """Get raw trace from the instrument.""",
    )
    peaks = Instrument.measurement(
        ":TRAC:MATH:PEAK?",
        """Get peaks from the instrument.""",
    )
    peaks_number = Instrument.measurement(
        ":TRAC:MATH:PEAK:POIN?",
        """Get the number of peaks from the instrument.""",
    )
    peak_sorting = Instrument.control(
        ":TRAC:MATH:PEAK:SORT?",
        ":TRAC:MATH:PEAK:SORT %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["FREQ", "AMPL"],
    )
    peak_threshold = Instrument.control(
        ":TRAC:MATH:PEAK:THRES?",
        ":TRAC:MATH:PEAK:THRES %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["FREQ", "AMPL"],
    )
    peak_width = Instrument.control(
        ":TRAC:MATH:PEAK:WID?",
        ":TRAC:MATH:PEAK:WID %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["FREQ", "AMPL"],
    )
    peak_width_units = Instrument.control(
        ":TRAC:MATH:PEAK:WID:UNIT?",
        ":TRAC:MATH:PEAK:WID:UNIT %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["POINTS", "SECONDS"],
    )
    peak_width_type = Instrument.control(
        ":TRAC:MATH:PEAK:WID:TYPE?",
        ":TRAC:MATH:PEAK:WID:TYPE %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["PEAK", "RMS"],
    )
    peak_width_type = Instrument.control(
        ":TRAC:MATH:PEAK:WID:TYPE?",
        ":TRAC:MATH:PEAK:WID:TYPE %g",
        """ determine werther to sort peaks by frequency or amplitude""",
        validator=strict_discrete_set,
        values=["PEAK", "RMS"],
    )

    @property
    def frequencies(self):
        """Returns a numpy array of frequencies in Hz that
        correspond to the current settings of the instrument.
        """
        return np.linspace(
            self.start_frequency,
            self.stop_frequency,
            self.frequency_points,
            dtype=np.float64,
        )

    def trace(self, number=1):
        """Returns a numpy array of the data for a particular trace
        based on the trace number (1, 2, or 3).
        """
        self.write(":FORMat:TRACe:DATA ASCII")
        data = np.loadtxt(
            StringIO(self.ask(":TRACE:DATA? TRACE%d" % number)),
            delimiter=",",
            dtype=np.float64,
        )
        return data

    def trace_df(self, number=1):
        """Returns a pandas DataFrame containing the frequency
        and peak data for a particular trace, based on the
        trace number (1, 2, or 3).
        """
        return pd.DataFrame(
            {
                "Frequency (GHz)": self.frequencies * 1e-9,
                "Peak (dB)": self.trace(number),
            }
        )
