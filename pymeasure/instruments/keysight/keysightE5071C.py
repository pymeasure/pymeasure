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


import logging

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# doc strings must start with “Control”, “Get”, “Measure”, or “Set” for properties

# Instrument.control
# Instrument.measurement
# Instrument.setting

MEASURING_PARAMETERS = ["S11", "S21", "S12", "S22", "A", "B", "R1", "R2"]

MEASUREMENT_FORMAT = {
    "LOGARITHMIC MAGNITUDE": "MLOG",
    "PHASE": "PHAS",
    "GROUP DELAY": "GDEL",
    "SMITH CHART LINEAR": "SLIN",
    "SMITH CHART LOGARITHMIC": "SLOG",
    "SMITH CHART": "SCOM",
    "SMITH CHART COMPLEX": "SCOM",
    "SMITH CHART IMPEDANCE": "SMIT",
    "SMITH CHART ADMITTANCE": "SADM",
    "POLAR LINEAR": "PLIN",
    "POLAR LOGARITHMIC": "PLOG",
    "POLAR": "POL",
    "POLAR COMPLEX": "POL",
    "LINEAR MAGNITUDE": "MLIN",
    "SWR": "SWR",
    "REAL": "REAL",
    "IMAGINARY": "IMAG",
    "PHASE EXPANDED": "UPH",
    "PHASE POSITIVE": "PPH",
}

OPTION_VALUES = {
    "240": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "440": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "245": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "445": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "260": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "460": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "265": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "465": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "280": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "480": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "285": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "485": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "2D5": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "4D5": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "2K5": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "4K5": {"Minimum Frequency": 9e3, "Maximum Frequeney": 4.5e9, "Has Bias Tee": False},
    "1E5": {
        "Time Base": "High Stability Time Base",
        "CW accuracy": "+/-1 ppm (specification)",
        "Source stability": "+/-0.05 ppm (5C to 40C typical), +/-0.5 ppm/year",
    },
    "UNQ": {
        "Time Base": "Standard Stability Time Base",
        "CW accuracy": "+/-5 ppm (specification)",
        "Source stability": "+/-5 ppm (5C to 40C typical)",
    },
    "017": {"Harddisk": "Removable"},
    "019": {"Harddisk": "Standard"},
    "008": {"Additional Options": "Frequency offset mode"},
    "TDR": {"Additional Options": "Enhanced time domain analysis"},
    "010": {"Additional Options": "Time domain analysis"},
    "790": {"Additional Options": "Measurement Wizard Assistant software"},
}

# used to identify if the channel layout is showing the channel
WINDOW_GRAPH_LAYOUT = {
    1: ["D1"],
    2: ["D12", "D1_2", "D112", "D1_1_2"],
    3: ["D123", "D1_2_3", "D12_33", "D11_23", "D13_23", "D12_13"],
    4: ["D1234", "D1_2_3_4", "D12_34"],
    6: ["D123_456", "D12_34_56"],
    8: ["D1234_5678", "D12_34_56_78"],
    9: ["D123_456_789"],
    12: ["D123__ABC", "D1234__9ABC"],
    16: [
        "D1234__CDEF",
    ],
}

WINDOW_GRAPH_OPTIONS = [
    "D1",
    "D12",
    "D1_2",
    "D112",
    "D1_1_2",
    "D123",
    "D1_2_3",
    "D12_33",
    "D11_23",
    "D13_23",
    "D12_13",
    "D1234",
    "D1_2_3_4",
    "D12_34",
    "D123_456",
    "D12_34_56",
    "D1234_5678",
    "D12_34_56_78",
    "D123_456_789",
    "D123__ABC",
    "D1234__9ABC",
    "D1234__CDEF",
]


class TraceException(Exception):
    """
    Trace Exception raised when trace called isn't active or displayed.
    """


class ChannelException(Exception):
    """
    Channel Exception raised when channel called isn't active or displayed.
    """


class MarkerException(Exception):
    """
    Marker Exception raised when marker called isn't active or displayed.
    """


# set the analyzer to trace averaging in single sweep mode, use the following SCPI commands to
# start the 100 average sweep and wait for the Operation Complete bit to be returned:


class TraceCommands(Channel):
    """
    Commands to control traces for a specific channel.

    Need docstring

    These first functions just read the `_active_trace` and call the parent to read its
    '_active_channel' value so that the SCPI commands do not need to be sent every time querying
    which channel and trace are active.
    """

    # these functions will allow the option to query active channel, trace, and total traces enabled
    # or trust the function to keep track of them. Hoping this speeds up operations.

    placeholder = "tr"

    def make_active(self):
        self.parent.active_trace = self.id

    def is_active(self):
        """
        Check that the number of traces for the channel is greater than this trace id,
        and that the active trace is this one.
        """
        if int(self.id) > self.parent.total_traces:  # pylint: disable=consider-using-max-builtin
            self.parent.total_traces = int(self.id)

        # check parent channel has traces added to it to match its total number of traces

        # check trace is shown
        if self.displayed is not True:
            self.displayed = True

        return self.parent.active_trace == self.id

    # double nest `{ch}` to have the command use the parent channel
    # measurement_parameter = Channel.control(
    #    ":CALC{{ch}}:PAR{tr}:DEF?"
    # for more examples look at https://github.com/pymeasure/pymeasure/pull/827/files
    # need to ensure the parameter selected is of {S11|S21|S12|S22|A|B|R1|R2}

    measuring_parameter = Channel.control(  # {S11|S21|S12|S22|A|B|R1|R2},
        "CALC{{ch}}:PAR{tr}:DEF?",
        "CALC{{ch}}:PAR{tr}:DEF %s",
        """
        Controls the measurement parameter of the trace and channel. If not specifying
        a scattering parameter, this command must be used with `absolute_measurement_port`
        for the same trace on the same channel. (string).
        """,
        # cast=str,
    )

    absolute_measurement_port = Channel.control(
        "CALC{{ch}}:PAR{tr}:SPOR?",
        "CALC{{ch}}:PAR{tr}:SPOR %e",
        """
        Controls the output port used for absolute measurement. This command must be used
        with `measuring_parameter` for the same trace on the same channel (integer).
        """,
        cast=int,
    )

    displayed = Channel.control(
        "DISP:WIND{{ch}}:TRAC{tr}:STAT?",
        "DISP:WIND{{ch}}:TRAC{tr}:STAT %b",
        """
        Controls the trace being displayed on the screen (boolean).
        """,
        cast=bool,
    )

    # trace scale
    # :DISP:WIND{1-16}:TRAC{1-16}:Y:PDIV

    # trace auto scale
    # :DISP:WIND{1-16}:TRAC{1-16}:Y:AUTO

    # need trace divisions

    # need trace units

    # need trace format

    @property
    def measurement_format(self):
        """
        Control the data format of the active trace of a channel. Valid values to use are given
        below (case insensitive string):

        =======================   =============   ===============================
        Value                     Format Sent     Description
        =======================   =============   ===============================
        LOGARITHMIC MAGNITUDE     MLOG            Logarithmic magnitude format.
        PHASE                     PHAS            Phase format.
        GROUP DELAY               GDEL            Group delay format.
        SMITH CHART LINEAR        SLIN            Smith chart format (Lin/Phase).
        SMITH CHART LOGARITHMIC   SLOG            Smith chart format (Log/Phase).
        SMITH CHART               SCOM            Smith chart format (Real/Imag).
        SMITH CHART COMPLEX       SCOM            Smith chart format (Real/Imag).
        SMITH CHART IMPEDANCE     SMIT h          Smith chart format (R+jX).
        SMITH CHART ADMITTANCE    SADM ittance    Smith chart format (G+jB).
        POLAR LINEAR              PLIN ear        Polar format (Lin).
        POLAR LOGARITHMIC         PLOG arithmic   Polar format (Log).
        POLAR                     POL ar          Polar format (Re/Im).
        POLAR COMPLEX             POL ar          Polar format (Re/Im).
        LINEAR MAGNITUDE          MLIN ear        Linear magnitude format.
        SWR                       SWR             SWR format.
        REAL                      REAL            Real format.
        IMAGINARY                 IMAG inary      Imaginary format.
        PHASE EXPANDED            UPH ase         Expanded phase format.
        PHASE POSITIVE            PPH ase         Positive phase format.

        """
        if not self.is_active():
            self.make_active()

        return self.parent.measurement_format

    @measurement_format.setter
    def measurement_format(self, value):
        # check if trace is active and set trace to be active if not
        if not self.is_active():
            self.make_active()

        self.parent.measurement_format = value


class MarkerCommands(Channel):
    """
    Commands to control markers for a specific channel.
    """

    placeholder = "mkr"

    position = Instrument.control(
        "CALC{{ch}}:MARK{mkr}:X %e",
        "CALC{{ch}}:MARK{mkr}:X?",
        """
        Control the position of marker the marker for a specific channel (float frequency in Hz).
        """,
        cast=float,
    )

    value = Instrument.measurement(
        "CALC{{ch}}:MARK{mkr}:Y?",
        """
        Get value of the marker for the active trace. (complex).
        """,
        cast=complex,
    )

    enabled = Channel.control(
        "CALC{{ch}}:MARK{mkr}?",
        "CALC{{ch}}:MARK{mkr} %i",
        """
        Control the display of a marker on a channel (boolean).
        """,
        map_values=True,
        values={True: 1, False: 0},
    )

    # may need to change to be a function instead since no values get passed to it
    active = Channel.setting(
        "CALC{{ch}}:MARK{mkr}:ACT %d",
        """
        Sets the marker for the active trace to be the active marker (boolean).
        """,
    )

    # ref marker position
    # ref marker value
    # ref marker enabled
    # ref marker active


# need window class (each channel gets a window)

# Sets the number of divisions of all the graphs of a channel
# valid value 4-30 preset to 10
# :DISP:WIND{1-16}:Y:DIV

# need channel window class (channel window gets again divided into subwindows)

# need port power class


class PortCommands(Channel):
    """
    Need docstring
    """

    placeholder = "port_"

    output_power = Channel.control(
        "SOUR{{ch}}:POW:PORT{port_}?",
        "SOUR{{ch}}:POW:PORT{port_} %d",
        """
        Control the output power in dBm for a port of a channel (float). This property is dynamic.
        """,
        validator=strict_range,
        values=(-60, 10),
        cast=float,
        dynamic=True,
    )

    # power 'SOUR{1-16}:POW:PORT{1-4}?' Sets the power level of
    # port 1 (:PORT1) to port 4 (:PORT4) of channel 1 (:SOUR1) to
    # channel 16 (:SOUR16).
    # power attenuator 'SOUR{1-16}:POW:ATT'


class ChannelCommands(Channel):
    """
    Need docstring
    """

    # trace window layout?

    # CALCulation Commands

    placeholder = "ch"

    # Traces

    traces = Instrument.MultiChannelCreator(TraceCommands, [x + 1 for x in range(1)], prefix="tr_")

    def update_number_of_traces(self, number_of_traces=None):
        """
        Create or remove traces to be correct with the actual number of traces.

        Up to 16 traces are allowed but could be lower depending on instrument configuration
        (integer).

        :param int number_of_traces: optional, if given defines the desired number of traces.
        """
        if number_of_traces is None:
            number_of_traces = self.total_traces

        # Set limits to active trace
        self.active_trace_values = range(1, number_of_traces, 1)  # pylint: disable=W0201

        if len(self.traces) == number_of_traces:
            return

        # Remove redant channels
        while len(self.traces) > number_of_traces:
            self.remove_child(self.traces[len(self.traces)])  # pylint: disable =E1136

        # Remove create new channels
        while len(self.traces) < number_of_traces:
            self.add_child(TraceCommands, len(self.traces) + 1, collection="traces", prefix="tr_")

    active_trace = Channel.control(
        "SERV:CHAN{ch}:TRAC:ACT?",
        "CALC{ch}:PAR%d:SEL",
        """
        Controls the active trace for a channel. Only displaced traces can be made into
        being the active trace. If the trace is > the total traces for the channel, set
        by `total_traces`, this command with not complete and with error (integer).
        """,
        cast=int,
        validator=strict_discrete_set,
        values=range(1, 1, 1),
        dynamic=True,
    )

    total_traces = Channel.control(
        "CALC{ch}:PAR:COUN?",
        "CALC{ch}:PAR:COUN %d",
        """
        Controls the total number of traces for a channel. Up to 16 traces are allowed but
        could be lower depending on instrument configuration (integer).

        Make sure to call `update_number_of_traces()` to update the range of values for
        `active_trace`.
        """,
        cast=int,
        validator=strict_discrete_set,
        values=range(1, 17, 1),
    )

    measurement_conversion = Channel.control(
        ":CALC{ch}:CONV:FUNC?",
        ":CALC{ch}:CONV:FUNC %s",
        """
        For the active trace of channel, select the parameter after conversion using the
        parameter conversion function.

        ===========================   ============================================================
        Function Conversion           Description
        ===========================   ============================================================
        ZREF lection (preset value)   Specifies the equivalent impedance in reflection
                                      measurement.
        ZTR ansmit                    Specifies the equivalent impedance (series) in transmission
                                      measurement.
        YREF lection                  Specifies the equivalent admittance in reflection
                                      measurement.
        YTR ansmit                    Specifies the equivalent admittance (series) in transmission
                                      measurement.
        INV ersion                    Specifies the inverse S-parameter.

        ZTSH unt                      Specifies the equivalent impedance (shunt) in transmission
                                      measurement.
        YTSH unt                      Specifies the equivalent admittance (shunt) in transmission
                                      measurement.
        CONJ ugation                  Specifies the conjugate.

        (string).
        """,
        cast=str,
    )

    # absolute_measurement_source set output port for absolute measurement
    # ":CALC{1-16}:PAR{1-16}:SPOR?" {1|2}

    # CALC{1-16}:DATA:FDAT
    # """
    # sets/reads out the formatted data array for the active trace of the channel selected
    # """
    # data_complex 'CALC{1-16}:DATA:FDAT' for active trace

    # :CALC{1-16}:DATA:FMEM
    # """
    # For the active trace of channel sets/reads out the formatted memory array.
    # """

    measurement_data = Channel.measurement(
        "CALC{ch}:DATA:SDAT?",  # read out real/imag data for active trace with corrections
        # "CALC{ch}:DATA:SDAT %e",
        """
        Gets the corrected scattering parameter array of the active trace for a channel by
        performing error correction, port extension compensation (calibration), and fixture
        simulator operations on the raw measured data specified for the trace of each channel if
        enabled (array of complex).

        `measurement_data` always returns the real/imaginary complex number array. To have the data
        formated, use `formatted_measurement_data` instead.

        Formatted data array values depend on the data format set for the active trace of the
        channel queried.
        """,
        cast=complex,
        preprocess_reply=lambda x: ",".join(
            [
                f"{float(i)}+{float(j)}j".replace("+-", "-")
                for i, j in zip(x.split(",")[0::2], x.split(",")[1::2])
            ],
        ),
        # get_process=lambda x: [i+1j*j for i,j in zip(x[0::2], x[1::2])],
        # separator=',',
        # command_process=
    )

    formatted_measurement_data = Channel.measurement(
        "CALC{ch}:DATA:FDAT?",  # read out real/imag data for active trace with corrections
        # "CALC{ch}:DATA:SDAT %e",
        """
        Gets a formatted data array contains the formatted data (values displayed on VNA) obtained
        by performing data math operations, measurement parameter conversion, and smoothing on a
        particular corrected data array. Regardless of the data format, it contains two data
        elements per measurement point as shown in the following table (array of complex).

        `formatted_measurement_data` always returns a complex number array based on the format set
        by using `measurement_format` and the currently active trace for the channel.

        ===================     ==================================   ========================
        Data format             Data element (real)                  Data element (imaginary)
        ===================     ==================================   ========================
        LOGARITHMIC MAGNITUDE   Log magnitude                        Always 0
        PHASE                   Phase                                Always 0
        GROUP DELAY             Group delay                          Always 0
        SMITH CHART LINEAR      Linear magnitude                     Phase
        SMITH CHART LOGARITHMIC log magnitude                        Phase
        SMITH CHART             Real part of a complex number        Imaginary part of a complex
                                                                     number
        SMITH CHART COMPLEX     Real part of a complex number        Imaginary part of a complex
                                                                     number
        SMITH CHART IMPEDANCE   Resistance                           Reactance
        SMITH CHART ADMITTANCE  Conductance                          Susceptance
        POLAR LINEAR            Linear magnitude                     Phase
        POLAR LOGARITHMIC       log magnitude                        Phase
        POLAR                   Real part of a complex number        Imaginary part of a complex
                                                                     number
        POLAR COMPLEX           Real part of a complex number        Imaginary part of a complex
                                                                     number
        LINEAR MAGNITUDE        Linear magnitude                     Always 0
        SWR                     SWR                                  Always 0
        REAL                    Real part of a complex number        Always 0
        IMAGINARY               Imaginary part of a complex number   Always 0
        PHASE EXPANDED          Expanded phase                       Always 0
        PHASE POSITIVE          Phase                                Always 0
        """,
        cast=complex,
        preprocess_reply=lambda x: ",".join(
            [f"{float(i)}+{float(j)}j" for i, j in zip(x.split(",")[0::2], x.split(",")[1::2])],
        ),
        # get_process=lambda x: [i+1j*j for i,j in zip(x[0::2], x[1::2])],
        # separator=',',
        # command_process=
    )

    measurement_format = Channel.control(
        "CALC{ch}:FORM?",
        "CALC{ch}:FORM %s",
        """
        Control the data format of the active trace of a channel. Valid values to use are given
        below (case insensitive string):

        =======================   =============   ===============================
        Value                     Format Sent     Description
        =======================   =============   ===============================
        LOGARITHMIC MAGNITUDE     MLOG            Logarithmic magnitude format.
        PHASE                     PHAS            Phase format.
        GROUP DELAY               GDEL            Group delay format.
        SMITH CHART LINEAR        SLIN            Smith chart format (Lin/Phase).
        SMITH CHART LOGARITHMIC   SLOG            Smith chart format (Log/Phase).
        SMITH CHART               SCOM            Smith chart format (Real/Imag).
        SMITH CHART COMPLEX       SCOM            Smith chart format (Real/Imag).
        SMITH CHART IMPEDANCE     SMIT            Smith chart format (R+jX).
        SMITH CHART ADMITTANCE    SADM            Smith chart format (G+jB).
        POLAR LINEAR              PLIN            Polar format (Lin).
        POLAR LOGARITHMIC         PLOG            Polar format (Log).
        POLAR                     POL             Polar format (Re/Im).
        POLAR COMPLEX             POL             Polar format (Re/Im).
        LINEAR MAGNITUDE          MLIN            Linear magnitude format.
        SWR                       SWR             SWR format.
        REAL                      REAL            Real format.
        IMAGINARY                 IMAG            Imaginary format.
        PHASE EXPANDED            UPH             Expanded phase format.
        PHASE POSITIVE            PPH             Positive phase format.

        """,
        cast=str,
        values=MEASUREMENT_FORMAT,
        map_values=True,
        set_process=lambda x: x.upper(),
    )

    measurement_data_to_memory = Channel.setting(
        "CALC{ch}:MATH:MEM",
        """
        Sets a copy the measurement data at the execution to the memory of the channel's active
        trace. (no input).
        """,
    )

    def check_channel_displayed(self, display_code):
        """
        Identify if a channel or trace is displayed for a provided layout.
        """

        for key, values in WINDOW_GRAPH_LAYOUT.items():
            if display_code in values:
                return self.id <= key
        return False

    def make_active(self):
        """
        Check display layout to ensure channel is displayed.
        """

        if self.check_channel_displayed(self.parent.display_layout):
            self.write(f"DISP:WIND{self.id}:ACT")  # noqa
        else:
            raise ChannelException(
                "Channel not currently displayed! Call `parent.display_layout` with \
                proper layout value."
            )

    # SENSe Commands

    # needs to be rewritten to a function
    # calibration_coefficient = Channel.control(
    #     "SENS{ch}:CORR:COEF? %s, %i, %i",
    #     "SENS{ch}:CORR:COEF %s, %i, %i",
    #     """
    #     Control the calibration coefficient data for a channel. Requires a tuple in the format of
    #     `tuple[str, int, int]` for getting the calibration coefficient values or in the format of
    #     `tuple[str, int, int, list[complex]]` for setting the calibration coefficient.

    #     The first element in the tuple is the coefficient type, being one of the following:
    #     ES Source match
    #     ER Reflection tracking
    #     ED Directivity
    #     EL Load match
    #     ET Transmission tracking
    #     EX Isolation

    #     The second element is the response port (int).

    #     The third element is the stimulus port (int).

    #     The last element is only needed for writing an array of coefficient values to a channel
    #     (complex).

    #     If the first element is ES Source match, ER Reflection tracking, or ED Directivity, both
    #     the second and third elements must be the same integer.

    #     If the first element is EL Load match, ET Transmission tracking, or EX Isolation, both
    #     the second and third elements must be different integers.

    #     Example:

    #     KeysightE5071C.ch_1.calibration_coefficient("EL",1,2)

    #     Returns:

    #     """,
    #     )

    # needs validator
    # dynamic=True,
    # values=() # based on options or updated to new values

    start_frequency = Channel.control(
        "SENS{ch}:FREQ:STAR?",
        "SENS{ch}:FREQ:STAR %d",
        """

        """,
        cast=float,
    )

    stop_frequency = Channel.control(
        "SENS{ch}:FREQ:STOP?",
        "SENS{ch}:FREQ:STOP",
        """

        """,
        cast=float,
    )

    center_frequency = Channel.control(
        "SENS{ch}:FREQ:CENT?",
        "SENS{ch}:FREQ:CENT %d",
        """

        """,
        cast=float,
    )

    span_frequency = Channel.control(
        "SENS{ch}:FREQ:SPAN?",
        "SENS{ch}:FREQ:SPAN %d",
        """

        """,
        cast=float,
    )

    cw_frequency = Channel.control(
        "SENS{ch}:FREQ?",
        "SENS{ch}:FREQ %d",
        """

        """,
        cast=float,
    )

    sweep_frequencies = Channel.measurement(  # frequencies of sweep are read out
        "SENS{ch}:FREQ:DATA?",
        """
        Get a list of frequencies measured in Hertz (float).
        """,
        cast=float,
    )

    averaging_enabled = Channel.control(
        "SENS{ch}:AVER?",
        "SENS{ch}:AVER %d",
        """
        Control the averaging enabled state for the channel (boolean).
        """,
        cast=bool,
    )

    averaging_count = Channel.control(
        "SENS{ch}:AVER:COUN?",
        "SENS{ch}:AVER:COUN %d",
        """
        Control the number of averaging counts to use (int).
        """,
        cast=int,
    )

    # may need to change to be a function
    def restart_averaging(self, channel):
        """
        Restart the measurement averaging for a given channel (integer).
        """
        self.write(f"SENS{channel}:AVER:CLE")  # noqa

    sweep_time = Channel.control(
        "SENS{ch}:SWE:TIME?",
        "SENS{ch}:SWE:TIME %d",
        """
        Control the time taken to perform a measurement sweep (float).
        """,
        cast=float,
    )

    auto_sweep_time_enabled = Channel.control(
        "SENS{ch}:SWE:TIME:AUTO?",
        "SENS{ch}:SWE:TIME:AUTO %d",
        """
        Control the sweep measurement time being automatically optimized (boolean).
        """,
    )

    sweep_type = Channel.control(  # {LIN|LOG|SEG|POW}
        "SENS{ch}:SWE:TYPE?",
        "SENS{ch}:SWE:TYPE %s",
        """
        Control the sweep type for a specific channel for how the number of points are spaced
        over frequency. Acceptable types are LIN, LOG, SEG, POW (string).

        ========================   =============   ===============================
        Value                      Format Sent     Description
        ========================   =============   ===============================

        Linear Sweep               LIN
        Logrithmic Sweep           LOG
        Sequential Segment Sweep   SEG
        Power Sweep                POW
        """,
        cast=str,
    )

    sweep_mode = Channel.control(  # {STEPped|ANALog|FSTepped|FANalog}'
        "SENS{ch}:SWE:GEN?",
        "SENS{ch}:SWE:GEN %s",
        """
        Control the sweep mode for a specific channel. Acceptable modes are STEPped, ANALog,
        FSTepped, or FANalog (string).
        """,
        cast=str,
    )

    avoid_spurs = Channel.control(
        "SENS{ch}:SWE:ASP?",
        "SENS{ch}:SWE:ASP %d",
        """
        Control spurious avoidance mode (bool)
        """,
    )

    sweep_delay = Channel.control(
        "SENS{ch}:SWE:DELay?",
        "SENS{ch}:SWE:DELay %d",
        """
        Control the delay in seconds before performing each measurement sweep (float 0.1-999).
        """,
        cast=float,
        validator=strict_range,
        values=(0.1, 999),
    )

    scan_points = Channel.control(
        "SENS{ch}:SWE:POIN?",
        "SENS{ch}:SWE:POIN %d",
        """
        Control the number of points measured per sweep. Can between either 1 and 1601 or 1
        to 20001 depending on the settings of the VNA for the maximum number of channels and
        traces (integer).
        """,
    )

    IFBW = Channel.control(  # 10-100000 HZ in 1, 1.5, 2, 3, 4, 5, 7 sized steps
        "SENS{ch}:BAND?",
        "SENS{ch}:BAND %d",
        """
        Control the IFBW in Hz from 10-100000 in step sizes of 1, 1.5, 2, 3, 4, 5, 7 (float).
        """,
        cast=float,
        validator=strict_range,
        values=(10, 100000),
        dynamic=True,
    )

    correction_enabled = Channel.control(
        "SENS{ch}:CORR:STAT?",
        "SENS{ch}:CORR:STAT %d",
        """
        Control whether corrections are applied to `measurement_data` and
        `formated_measurement_data` (boolean).
        """,
    )

    # SOURse Commands

    @property
    def total_ports(self):
        """
        Get list of available ports for initializing PortCommands to control their associated
        output power in dBm (list of integers).
        """
        return [x + 1 for x in range(0, int(self.parent.port_count))]

    ports = Instrument.MultiChannelCreator(PortCommands, total_ports, prefix="port_")

    couple_ports_power = Channel.control(
        "SOUR{ch}:POW:PORT:COUP?",
        "SOUR{ch}:POW:PORT:COUP %d",
        """
        Control whether the output power of the ports for the channel are coupled or independent
        (boolean).
        """,
        cast=bool,
    )

    get_active_trace = Channel.measurement(
        "SERV:CHAN{ch}:TRAC:ACT?",
        """
        Get the active trace for a given channel (int).
        """,
        cast=int,
    )

    # Redundant Commands

    output_enabled = Channel.control(
        "OUTP?",
        "OUTP %d",
        """

        """,
        cast=bool,
    )

    trigger_continuous = Channel.control(
        "INIT{ch}:CONT?",
        "INIT{ch}:CONT %d",
        """
        Control whether to trigger a channel continuously or to have it hold (boolean).
        """,
        cast=int,
        map_values=True,
        values={True: 1, False: 0},
    )

    # def trigger_continuous(self):
    #     self.write("INIT{self.id}:CONT")

    # write calibration coefficient data arrays "SENS{1-16}:CORR:COEF" pg 548
    # and "SENS{1-16}:CORR:COEF:SAVE"

    # might be better to move this to in the trace channel

    markers = Instrument.MultiChannelCreator(
        MarkerCommands, [x + 1 for x in range(1)], prefix="mkr_"
    )

    total_markers = 1

    def update_number_of_markers(self, number_of_markers=None):
        """
        Create or remove markers to be correct with the actual number of markers.

        Up to 9 markers are allowed (integer).

        If making comparison measurements using markers, Marker #0 is the reference marker.

        :param int number_of_markers: optional, if given defines the desired number of markers.
        """
        if number_of_markers is None:
            number_of_markers = self.total_markers

        # Set limits to active markers
        self.active_trace_values = range(1, number_of_markers, 1)  # pylint: disable=W0201

        if len(self.markers) == number_of_markers:
            return

        # Remove reduant markers
        while len(self.markers) > number_of_markers:
            self.remove_child(self.markers[len(self.markers)])  # pylint: disable =E1136

        # Remove create new markers
        while len(self.markers) < number_of_markers:
            self.add_child(
                MarkerCommands, len(self.markers) + 1, collection="markers", prefix="mkr_"
            )


class KeysightE5071C(Instrument):
    """
    Need docstring
    """

    # pylint: disable=too-many-instance-attributes
    # Nine is reasonable in this case.

    def __init__(self, adapter, name="Keysight E5071C", **kwargs):
        super().__init__(adapter, name, includeSCPI=True, **kwargs)

        self._manu = ""
        self._model = ""
        self._fw = ""
        self._sn = ""
        self._options = ""
        self.number_of_channels = 1

        if name is None:
            # written this way to pass 'test_all_instruments.py' while allowing the
            # *IDN? to populate the name of the VNA
            try:
                self._manu, self._model, self._sn, self._fw = self.id
            except ValueError:
                self._manu = "Keysight"
                self._model = "E5071C"
            self._desc = "Vector Network Analyzer"
            name = self.name = f"{self._manu} {self._model} {self._desc}"
        else:
            self.name = name

    id = Instrument.measurement(
        "*IDN?",
        """Get the identification of the instrument""",
        cast=str,
    )

    @property
    def manu(self):
        """Get the manufacturer of the instrument."""
        if self._manu == "":
            self._manu, self._model, self._sn, self._fw = self.id
        return self._manu

    @property
    def model(self):
        """Get the model of the instrument."""
        if self._model == "":
            self._manu, self._model, self._sn, self._fw = self.id
        return self._model

    @property
    def fw(self):
        """Get the firmware of the instrument."""
        if self._fw == "":
            self._manu, self._model, self._sn, self._fw = self.id
        return self._fw

    @property
    def sn(self):
        """Get the serial number of the instrument."""
        if self._sn == "":
            self._manu, self._model, self._sn, self._fw = self.id
        return self._sn

    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """

        """,
    )

    channels = Instrument.MultiChannelCreator(
        ChannelCommands, [x + 1 for x in range(1)], prefix="ch_"
    )

    # windows ...

    def update_channels(self, number_of_channels=None):
        """Create or remove channels to be correct with the actual number of channels.

        :param int number_of_channels: optional, if given defines the desired number of channels.
        """
        if number_of_channels is None:
            number_of_channels = self.number_of_channels
        else:
            if number_of_channels > self.maximum_channels:
                raise ChannelException(
                    "Cannot update channels to be > maximum_channels VNA is configured for!"
                )

        if not hasattr(self, "channels"):
            self.channels = {}

        if len(self.channels) == number_of_channels:
            return

        # Remove redant channels
        while len(self.channels) > number_of_channels:
            self.remove_child(self.channels[len(self.channels)])

        # Remove create new channels
        while len(self.channels) < number_of_channels:
            self.add_child(
                ChannelCommands, len(self.channels) + 1, collection="channels", prefix="ch_"
            )

    # channel layout window?

    # select active channel "DISP:WIND{1-16}:ACT"

    display_layout = Instrument.control(
        "DISP:SPL?",
        "DISP:SPL %s",
        """
        Control the channel layout displayed on the screen (str).

        There are a multitude of channel layouts:

        For only one channel:

        =========   =====================
        Channels    Layout Representation
        =========   =====================

                     _____
        One         |  1  |
                    |_____|
                      D1
                     ___________     ___________     ___________     ___________
                    |     |     |   |     1     |   |       |   |   |           |
        Two         |  1  |  2  |   |___________|   |   1   | 2 |   |     1     |
                    |     |     |   |     2     |   |       |   |   |___________|
                    |_____|_____|   |___________|   |_______|___|   |_____2_____|
                         D12            D1_2            D112           D1_1_2
                     ___________     ___________     ___________
                    |   |   |   |   |     1     |   |     |     |
        Three       |   |   |   |   |___________|   |  1  |  2  |
                    | 1 | 2 | 3 |   |     2     |   |_____|_____|
                    |   |   |   |   |___________|   |           |
                    |   |   |   |   |     3     |   |     3     |
                    |___|___|___|   |___________|   |___________|
                         D123           D1_2_3          D12_33
                     ___________     ___________     ___________
        Three       |     1     |   |  1  |     |   |     |  2  |
                    |___________|   |_____|  3  |   |  1  |_____|
                    |  2  |  3  |   |  2  |     |   |     |  3  |
                    |_____|_____|   |_____|_____|   |_____|_____|
                       D11_23           D13_23          D12_13
                     ___________     ___________     ___________
                    |  |  |  |  |   |___________|   |  1  |  2  |
        Four        |  |  |  |  |   |___________|   |_____|_____|
                    |  |  |  |  |   |___________|   |  3  |  4  |
                    |__|__|__|__|   |___________|   |_____|_____|
                        D1234         D1_2_3_4         D12_34
                     ___________     ___________
                    |   |   |   |   |  1  |  2  |
        Six         | 1 | 2 | 3 |   |_____|_____|
                    |___|___|___|   |  3  |  4  |
                    |   |   |   |   |_____|_____|
                    | 4 | 5 | 6 |   |  5  |  6  |
                    |___|___|___|   |_____|_____|
                      D123_456        D12_34_56
                     ___________     ___________
                    |  |  |  |  |   |_____|_____|
        Eight       |__|__|__|__|   |_____|_____|
                    |  |  |  |  |   |_____|_____|
                    |__|__|__|__|   |_____|_____|
                    D1234_5678       D12_34_56_78
                     ___________
                    | 1 | 2 | 3 |
        Nine        |___|___|___|
                    | 4 | 5 | 6 |
                    |___|___|___|
                    | 7 | 8 | 9 |
                    |___|___|___|
                    D123_456_789
                     ___________
                    |_1_|_2_|_3_|    _______________
        Twelve      |_4_|_5_|_6_|   |_1_|_2_|_3_|_4_|
                    |_7_|_9_|_9_|   |_5_|_6_|_7_|_8_|
                    |_A_|_B_|_C_|   |_9_|_A_|_B_|_C_|
                      D123__ABC        D1234__9ABC
                     _______________
                    |_1_|_2_|_3_|_4_|
        Sixteen     |_5_|_6_|_7_|_8_|
                    |_9_|_A_|_B_|_C_|
                    |_D_|_E_|_F_|_G_|
                       D1234__CDEF     (not a typo, as-is from the programming manual)

        """,
        cast=str,
        validator=strict_discrete_set,
        values=WINDOW_GRAPH_OPTIONS,
    )

    # trace layout 'DISP:WIND{1-16}:SPL' pg 475

    # disable display 'DISP:ENAB?' {ON|OFF|0|1}

    # Display

    display_enabled = Instrument.control(
        "DISP:ENAB?",
        "DISP:ENAB %i",
        """
        Control if the display state (boolean).
        """,
        map_values=True,
        values={True: 1, False: 0},
    )

    display_backlight_enabled = Instrument.control(
        "SYST:BACK?",
        "SYST:BACK %d",
        """
        Control whether the display backlight is enabled (boolean).
        """,
        cast=int,
        map_values=True,
        values={True: 1, False: 0},
    )

    # if off you cannot read display
    # update display (used when display is off) 'DISPlay:UPDate:IMMediate'

    # trigger_hold

    # trigger single 'TRIG:SING'
    # trigger source ':TRIGger[:SEQuence]:SOURce {INTernal|EXTernal|MANual|BUS}?'
    # trigger averaging 'TRIG:AVER'

    # 'TRIG:SCOP {ALL|ACTive}' select channel to be triggered
    # ''

    # options

    # scan

    # scan_single
    # scan

    # save image of screen ":MMEM:STOR:IMAG" pg 512

    # SERVice Commands

    port_count = Instrument.measurement(
        "SERV:PORT:COUN?",
        """
        Get the total number of ports on VNA (integer).
        """,
        cast=int,
    )

    maximum_channels = Instrument.measurement(
        "SERV:CHAN:COUN?",
        """
        Get the total number of channels configured on the VNA (integer).
        """,
        cast=int,
    )

    maximum_traces = Instrument.measurement(
        "SERV:CHAN:TRAC:COUN?",
        """
        Get the total number of traces allowed per channel configured on the VNA (integer).
        """,
        cast=int,
    )

    maximum_points = Instrument.measurement(
        "SERV:SWE:POIN?",
        """
        Get the maximum number of points measured as configured on the VNA (integer).
        """,
        cast=int,
    )

    minimum_frequency = Instrument.measurement(
        "SERV:SWE:FREQ:MIN?",
        """
        Get the minimum frequency the VNA can measure (float).
        """,
        cast=float,
    )

    maximum_frequency = Instrument.measurement(
        "SERV:SWE:FREQ:MAX?",
        """
        Get the maximum frequency the VNA can measure (float).
        """,
        cast=float,
    )

    active_channel = Instrument.measurement(
        "SERV:CHAN:ACT?",
        """
        Get the channel that is currently active (integer).
        """,
        cast=int,
    )

    # class to track active channel and active trace in channel
    # ':SERV:CHAN:ACT?' query only read out of active channel
    # ':SERV:CHAN{1-16}:TRAC:ACT?' query only read out of active trace for channel

    # SYSTem Commands

    def emit_beep(self):
        """
        Command VNA to emit a beep. This command takes no inputs and returns nothing.
        """
        self.write("SYST:BEEP:COMP:IMM")

    emit_beep_on_warnings = Instrument.control(
        "SYST:BEEP:WARN:STAT?",
        "SYST:BEEP:WARN:STAT %d",
        """
        Control if VNA will emit a beep on warnings and errors (boolean).
        """,
        cast=bool,
        map_values=True,
        values={True: 1, False: 0},
    )

    emit_beep_on_completions = Instrument.control(
        "SYST:BEEP:COMP:STAT?",
        "SYST:BEEP:COMP:STAT %d",
        """
        Control if VNA will emit a beep on completion of operations (boolean).
        """,
        cast=bool,
        map_values=True,
        values={True: 1, False: 0},
    )

    # error stuff
    # ':STAT:OPER?' Reads out the value of the Operation Status Event Register. (Query only)
    # 'STAT:OPER:COND?' Reads out the value of the Operation Status Condition Register. (Query only)
    # ':STAT:OPER:ENAB' Sets the value of the Operation Status Enable Register.
    # 'SYST:ERR?'
    # ':SYSTem:BACKlight {ON|OFF|1|0}?' Turns on or off LCD backlight,
    # 'SYST:TEMP' read out if warm-up satisfy specifications of VNA

    # system correction enabled 'SYST:CORR {ON|OFF|0|1}?'

    # :FORM:DATA
    # Specifies the format of data transfered
    # Description
    # ASCii (preset value) Specifies the ASCII transfer format.
    # REAL Specifies the IEEE 64-bit floating point binary transfer format.
    # REAL32 Specifies the IEEE 32-bit floating point binary transfer format

    # :FORM:BORD NORMal or SWAPped
    # data transfer format is set to the binary transfer format, sets the transfer order of
    # each byte in data (byte order)
    # Normal MSB first
    # Swapped LSB first

    # reset

    # date 'SYST:DATE {YEAR},{MONTH},{DAY}?' ie ":SYST:DATE 2002,1,1"
    # clock 'DISP:CLOC'
    # 'SYST:TIME {Hour},{Min},{Sec}?'

    options = Instrument.measurement(
        "*OPT?",
        """
        Get the identification number(s) of an option installed (string).
        """,
        cast=str,
    )

    def abort(self):
        """
        Sets the trigger sequence for all channels to idle state.
        """
        self.write(":ABOR")
