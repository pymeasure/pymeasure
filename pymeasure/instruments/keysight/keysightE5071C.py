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

# from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

# doc strings must start with “Control”, “Get”, “Measure”, or “Set” for properties

# Instrument.control
# Instrument.measurement
# Instrument.setting

MEASURING_PARAMETERS = ["S11", "S21", "S12", "S22", "A", "B", "R1", "R2"]
# MEASUREMENT_FORMAT = [
#     "SMITH",
#     "LOGMAG",
#     "PHASE",
#     "REAL",
#     "IMAG",
#     "GROUP DELAY",
#     "POLAR",
#     "LINMAG",
#     "POS PHASE",
#     "EXPAND PHASE",
#     "SWR",
# ]

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


# set the analyzer to trace averaging in single sweep mode, use the following SCPI commands to
# start the 100 average sweep and wait for the Operation Complete bit to be returned:


class TraceCommands(Channel):
    """
    Need docstring

    These first functions just read the `_active_trace` and call the parent to read its
    '_active_channel' value so that the SCPI commands do not need to be sent every time querying
    which channel and trace are active.
    """

    # these functions will allow the option to query active channel, trace, and total traces enabled
    # or trust the function to keep track of them. Hoping this speeds up operations.

    def get_active_channel(self):
        # get active channel from parent
        return self.parent.get_active_channel

    def get_active_trace(self):
        # get active trace from parent
        return self.parent.active_trace

    def get_total_traces(self):
        return self.parent.total_traces

    def make_active(self):
        self.parent.active_trace = self.id

    def is_active(self):
        """
        Check that the number of traces for the channel is greater than this trace id,
        and that the active trace is this one.
        """
        if int(self.id) > self.get_total_traces():
            self.parent.total_traces = int(self.id)

        # check parent channel has traces added to it to match its total number of traces

        return self.get_active_trace() == self.id

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
        cast=str,
    )

    absolute_measurement_port = Channel.control(
        "CALC{{ch}}:PAR{tr}:SPOR?",
        "CALC{{ch}}:PAR{tr}:SPOR %e",
        """
        Controls the output port used for absolute measurement (integer).
        """,
        cast=int,
    )

    marker_position = Instrument.control(
        "CALC{{ch}}:MARK{tr}:X %e",
        "CALC{{ch}}:MARK{tr}:X?",
        """
        Control the position of marker the marker for a specific channel and trace. (float
        frequency in Hz)
        """,
        cast=float,
    )

    marker_value = Instrument.measurement(
        "CALC{{ch}}:MARK{tr}:Y?",
        """
        Get value of the marker for a specific channel and trace. (complex)
        """,
        cast=complex,
    )

    # need trace scale

    # need trace divisions

    # need trace units

    # need trace format


# need marker class

# need window class


class ChannelCommands(Channel):
    """
    Need docstring
    """

    # trace window layout?

    # CALCulation Commands

    active_trace = Channel.control(
        "SERV:CHAN{ch}:TRAC:ACT?",
        "CALC{ch}:PAR%d:SEL",
        """
        Controls the active trace for a channel. Only displaced traces can be made into
        being the active trace. If the trace is > the total traces for the channel, set
        by `total_traces`, this command with not complete and with error (integer).
        """,
        cast=int,
    )

    total_traces = Channel.control(
        "CALC{ch}:PAR:COUN?",
        "CALC{ch}:PAR:COUN %d",
        """
        Controls the total number of traces for a channel. Up to 16 traces are allowed but
        could be lower depending on instrument configuration. (integer).
        """,
        cast=int,
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

    # need total_traces to trigger a function to change the traces
    # available to the channel

    # def update_traces(self, number_of_traces=None):
    #     """Create or remove traces to be correct with the actual number of traces.

    #     :param int number_of_traces: optional, if given defines the desired number of traces.
    #     """
    #     if number_of_traces is None:
    #         number_of_traces = self.number_of_traces

    #     if not hasattr(self, "traces"):
    #         self.traces = {}

    #     if len(self.traces) == number_of_traces:
    #         return

    #     # Remove redant channels
    #     while len(self.traces) > number_of_traces:
    #         self.remove_child(self.traces[len(self.traces)])

    #     # Remove create new channels
    #     while len(self.traces) < number_of_traces:
    #         self.add_child(Trace, len(self.traces) + 1, collection="traces", prefix="tr_")

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
        Gets the corrected data array of the active trace for a channel (array of complex).

        Formatted data array values depend on the data format set for the active trace of the
        channel queried.
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

        =======================   =============   =============================================
        Value                     Format Sent     Description
        =======================   =============   =============================================
        LOGARITHMIC MAGNITUDE     MLOG            Specifies the logarithmic magnitude format.
        PHASE                     PHAS            Specifies the phase format.
        GROUP DELAY               GDEL            Specifies the group delay format.
        SMITH CHART LINEAR        SLIN            Specifies the Smith chart format (Lin/Phase).
        SMITH CHART LOGARITHMIC   SLOG            Specifies the Smith chart format (Log/Phase).
        SMITH CHART               SCOM            Specifies the Smith chart format (Real/Imag).
        SMITH CHART COMPLEX       SCOM            Specifies the Smith chart format (Real/Imag).
        SMITH CHART IMPEDANCE     SMIT h          Specifies the Smith chart format (R+jX).
        SMITH CHART ADMITTANCE    SADM ittance    Specifies the Smith chart format (G+jB).
        POLAR LINEAR              PLIN ear        Specifies the polar format (Lin).
        POLAR LOGARITHMIC         PLOG arithmic   Specifies the polar format (Log).
        POLAR                     POL ar          Specifies the polar format (Re/Im).
        POLAR COMPLEX             POL ar          Specifies the polar format (Re/Im).
        LINEAR MAGNITUDE          MLIN ear        Specifies the linear magnitude format.
        SWR                       SWR             Specifies the SWR format.
        REAL                      REAL            Specifies the real format.
        IMAGINARY                 IMAG inary      Specifies the imaginary format.
        PHASE EXPANDED            UPH ase         Specifies the expanded phase format.
        PHASE POSITIVE            PPH ase         Specifies the positive phase format.

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

    # DISPlay Commands

    make_active = Channel.setting(  # select active channel "DISP:WIND{1-16}:ACT"
        "DISP:WIND{ch}:ACT",
        """ """,
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

    start_frequency = Channel.control(
        "SENS{ch}:FREQ:STAR?",
        "SENS{ch}:FREQ:STAR %d",
        """ """,
        cast=float,
    )

    stop_frequency = Channel.control(
        "SENS{ch}:FREQ:STOP?",
        "SENS{ch}:FREQ:STOP",
        """ """,
    )

    center_frequency = Channel.control(
        "SENS{ch}:FREQ:CENT?",
        "SENS{ch}:FREQ:CENT %d",
        """ """,
    )

    span_frequency = Channel.control(
        "SENS{ch}:FREQ:SPAN?",
        "SENS{ch}:FREQ:SPAN %d",
        """ """,
    )

    cw_frequency = Channel.control(
        "SENS{ch}:FREQ?",
        "SENS{ch}:FREQ %d",
        """ """,
    )

    sweep_frequencies = Channel.measurement(  # frequencies of sweep are read out
        "SENS{ch}:FREQ:DATA?",
        """ """,
    )

    averaging_enabled = Channel.control(
        ":SENS{ch}:AVER?",
        ":SENS{ch}:AVER %d",
        """Control the channel averaging enabled state. (bool)""",
        cast=bool,
    )

    averaging_count = Channel.control(
        ":SENS{ch}:AVER:COUN?",
        ":SENS{ch}:AVER:COUN %d",
        """Control the number of averaging counts to use. (int)""",
        cast=int,
    )

    averaging_restart = Channel.setting(
        "SENS{ch}:AVER:CLE",
        """ """,
    )

    sweep_time = Channel.control(
        "SENS{ch}:SWE:TIME?",
        "SENS{ch}:SWE:TIME %d",
        """ """,
    )

    auto_sweep_time_enabled = Channel.control(
        "SENS{ch}:SWE:TIME:AUTO?",
        "SENS{ch}:SWE:TIME:AUTO %d",
        """ """,
    )

    sweep_type = Channel.control(  # {LIN|LOG|SEG|POW}
        "SENS{ch}:SWE:TYPE?",
        "SENS{ch}:SWE:TYPE %s",
        """ """,
        cast=str,
    )

    sweep_mode = Channel.control(  # {STEPped|ANALog|FSTepped|FANalog}'
        "SENS{ch}:SWE:GEN?",
        "SENS{ch}:SWE:GEN %s",
        """ """,
        cast=str,
    )

    avoid_spurs = Channel.control(
        "SENS{ch}:SWE:ASP?",
        "SENS{ch}:SWE:ASP %d",
        """Control spurious avoidance mode (bool)""",
    )

    sweep_delay = Channel.control(
        "SENS{ch}:SWE:DELay?",
        "SENS{ch}:SWE:DELay %d",
        """ """,
    )

    scan_points = Channel.control(
        "SENS{ch}:SWE:POIN?",
        "SENS{ch}:SWE:POIN %d",
        """ """,
    )

    IFBW = Channel.control(  # 10-100000 HZ in 1, 1.5, 2, 3, 4, 5, 7 sized steps
        "SENS{ch}:BAND?",
        "SENS{ch}:BAND %d",
        """ """,
    )

    correction_enabled = Channel.control(
        "SENS{ch}:CORR:STAT?",
        "SENS{ch}:CORR:STAT %d",
        """ """,
    )

    # SOURse Commands

    # power 'SOUR{1-16}:POW:PORT{1-4}?' Sets the power level of
    # port 1 (:PORT1) to port 4 (:PORT4) of channel 1 (:SOUR1) to
    # channel 16 (:SOUR16).
    # power attenuator 'SOUR{1-16}:POW:ATT'
    # power couple ports 'SOUR{1-16}:POW:PORT:COUP?'

    get_active_trace = Channel.measurement(
        "SERV:CHAN{ch}:TRAC:ACT?",
        """ """,
        cast=int,
    )

    # Redundant Commands

    output_enabled = Channel.control(
        "OUTP?",
        "OUTP %d",
        """ """,
    )

    # trigger_continuous 'INIT{1-16}:CONT'


class KeysightE5071C(Instrument):
    """
    Need docstring
    """

    def __init__(self, adapter, name="Keysight E5071C", **kwargs):
        super().__init__(adapter, name, includeSCPI=True, **kwargs)

        self._manu = ""
        self._model = ""
        self._fw = ""
        self._sn = ""
        self._options = ""
        self._active_channel = "1"

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
        """ """,
    )

    channels = Instrument.MultiChannelCreator(
        ChannelCommands, [x + 1 for x in range(16)], prefix="ch_"
    )

    # def update_channels(self, number_of_channels=None):
    #     """Create or remove channels to be correct with the actual number of channels.

    #     :param int number_of_channels: optional, if given defines the desired number of channels.
    #     """
    #     if number_of_channels is None:
    #         number_of_channels = self.number_of_channels

    #     if not hasattr(self, "channels"):
    #         self.channels = {}

    #     if len(self.channels) == number_of_channels:
    #         return

    #     # Remove redant channels
    #     while len(self.channels) > number_of_channels:
    #         self.remove_child(self.channels[len(self.channels)])

    #     # Remove create new channels
    #     while len(self.channels) < number_of_channels:
    #         self.add_child(Trace, len(self.channels) + 1, collection="channels", prefix="ch_")

    # channel layout window?

    # class to track active channel and active trace in channel
    # ':SERV:CHAN:ACT?' query only read out of active channel
    # ':SERV:CHAN{1-16}:TRAC:ACT?' query only read out of active trace for channel

    # select active trace "CALC{1-16}:PAR{1-16}:SEL"
    # select active channel "DISP:WIND{1-16}:ACT"

    # ':SERV:CHAN:ACT?' query only read out of active channel
    # ':SERV:CHAN{1-16}:TRAC:ACT?' query only read out of active trace for channel

    # select active channel "DISP:WIND{1-16}:ACT"

    # traces

    # auto scale pg 481
    # divisions 'DISP:WIND{1-16}:TRAC{1-16}:Y:AUTO'
    # REF POS
    # REF Value
    # Scale/div

    # windows 'DISP:SPL' pg 466
    # trace layout 'DISP:WIND{1-16}:SPL' pg 475
    # disable display 'DISP:ENAB?' {ON|OFF|0|1}

    # if off you cannot read display
    # update display (used when display is off) 'DISPlay:UPDate:IMMediate'

    # markers
    # get marker position
    # get marker value

    # trigger_hold

    # trigger single 'TRIG:SING'
    # trigger source ':TRIGger[:SEQuence]:SOURce {INTernal|EXTernal|MANual|BUS}?'
    # trigger averaging 'TRIG:AVER'

    # 'TRIG:SCOP {ALL|ACTive}' select channel to be triggered
    # ''

    # options

    # scan
    # frequencies 'SENS{1-16}:FREQ:DATA?' frequencies of sweep are read out
    # scan_single
    # scan

    # write calibration coefficient data arrays "SENS{1-16}:CORR:COEF" pg 548
    # and "SENS{1-16}:CORR:COEF:SAVE"
    # save image of screen ":MMEM:STOR:IMAG" pg 512

    # error stuff
    # ':STAT:OPER?' Reads out the value of the Operation Status Event Register. (Query only)
    # 'STAT:OPER:COND?' Reads out the value of the Operation Status Condition Register. (Query only)
    # ':STAT:OPER:ENAB' Sets the value of the Operation Status Enable Register.
    # 'SYST:ERR?'
    # ':SYSTem:BACKlight {ON|OFF|1|0}?' Turns on or off LCD backlight,
    # 'SYST:TEMP' read out if warm-up satisfy specifications of VNA

    # 'SERV:PORT:COUN?'
    # ':SERV:CHAN:COUN?'
    # ':SERV:CHAN:TRAC:COUN?'
    # ':SERV:SWE:POIN?'
    # ':SERV:SWE:FREQ:MIN?'
    # ':SERV:SWE:FREQ:MAX?'

    # SERVice Commands
    get_active_channel = Instrument.measurement(
        "SERV:CHAN:ACT?",
        """ """,
        cast=int,
    )

    # SYSTem Commands

    # emit_beep ':SYST:BEEP:COMP:IMM' Generates a beep
    # emit beep on completion ':SYST:BEEP:COMP:STAT {ON|OFF|0|1}?'
    # turns on or off beeper for completion of operation
    # emit beep on warnings 'SYSTem:BEEPer:WARNing:STATe {ON|OFF|1|0}?'

    # system correction enabled 'SYST:CORR {ON|OFF|0|1}?'

    # reset

    # date 'SYST:DATE {YEAR},{MONTH},{DAY}?' ie ":SYST:DATE 2002,1,1"
    # clock 'DISP:CLOC'
    # 'SYST:TIME {Hour},{Min},{Sec}?'

    def abort(self):
        """
        Sets the trigger sequence for all channels to idle state.
        """
        self.write(":ABOR")
