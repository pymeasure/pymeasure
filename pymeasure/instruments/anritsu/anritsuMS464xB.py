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

from pymeasure.instruments import Instrument, Channel, SCPIUnknownMixin
from pymeasure.instruments.validators import (
    strict_discrete_set,
    strict_range
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class AnritsuMS464xB(SCPIUnknownMixin, Instrument):
    """ A class representing the Anritsu MS464xB Vector Network Analyzer (VNA) series.

    This family consists of the MS4642B, MS4644B, MS4645B, and MS4647B, which are represented in
    their respective classes (:class:`~.AnritsuMS4642B`, :class:`~.AnritsuMS4644B`,
    :class:`~.AnritsuMS4645B`, :class:`~.AnritsuMS4647B`), that only differ in the available
    frequency range.

    They can contain up to 16 instances of :class:`~.MeasurementChannel` (depending on the
    configuration of the instrument), that are accessible via the `channels` dict or directly via
    `ch_` + the channel number.

    :param active_channels: defines the number of active channels (default=16); if active_channels
        is "auto", the instrument will be queried for the number of active channels.
    :type active_channels: int (1-16) or str ("auto")
    :param installed_ports: defines the number of installed ports (default=4); if "auto" is
        provided, the instrument will be queried for the number of ports
    :type installed_ports: int (1-4) or str ("auto")
    :param traces_per_channel: defines the number of traces that is assumed for each channel
        (between 1 and 16); if not provided, the maximum number is assumed; "auto" is provided,
        the instrument will be queried for the number of traces of each channel.
    :type traces_per_channel: int (1-16) or str ("auto") or None
    """
    CHANNELS_MAX = 16
    TRACES_MAX = 16
    PORTS = 4
    TRIGGER_TYPES = ["POIN", "SWE", "CHAN", "ALL"]

    FREQUENCY_RANGE = [1E7, 7E10]

    SPARAM_LIST = ["S11", "S12", "S21", "S22",
                   "S13", "S23", "S33", "S31",
                   "S32", "S14", "S24", "S34",
                   "S41", "S42", "S43", "S44", ]
    DISPLAY_LAYOUTS = ["R1C1", "R1C2", "R2C1", "R1C3", "R3C1",
                       "R2C2C1", "R2C1C2", "C2R2R1", "C2R1R2",
                       "R1C4", "R4C1", "R2C2", "R2C3", "R3C2",
                       "R2C4", "R4C2", "R3C3", "R5C2", "R2C5",
                       "R4C3", "R3C4", "R4C4"]

    def __init__(self, adapter,
                 name="Anritsu MS464xB Vector Network Analyzer",
                 active_channels=16,
                 installed_ports=4,
                 traces_per_channel=None,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            timeout=10000,
            **kwargs,
        )

        self.PORTS = self.number_of_ports if installed_ports == "auto" else installed_ports

        number_of_channels = None if active_channels == "auto" else active_channels

        self.update_channels(number_of_channels=number_of_channels,
                             traces=traces_per_channel)

    def update_channels(self, number_of_channels=None, **kwargs):
        """Create or remove channels to be correct with the actual number of channels.

        :param int number_of_channels: optional, if given, defines the desired number of channels.
        """
        if number_of_channels is None:
            number_of_channels = self.number_of_channels

        if not hasattr(self, "channels"):
            self.channels = {}

        if len(self.channels) == number_of_channels:
            return

        # Remove redundant channels
        while len(self.channels) > number_of_channels:
            self.remove_child(self.channels[len(self.channels)])

        # Create new channels
        while len(self.channels) < number_of_channels:
            self.add_child(MeasurementChannel, len(self.channels) + 1,
                           frequency_range=self.FREQUENCY_RANGE,
                           **kwargs)

    def check_errors(self):
        """ Read all errors from the instrument.

        :return: list of error entries
        """
        errors = []
        while True:
            err = self.values("SYST:ERR?")
            if err[0] != "No Error":
                log.error(f"{self.name}: {err[0]}")
                errors.append(err)
            else:
                break
        return errors

    datablock_header_format = Instrument.control(
        "FDHX?", "FDH%d",
        """Control the way the arbitrary block header for output data is formed.

        Valid values are:

        =====    ===========================================================
        value    description
        =====    ===========================================================
        0        A block header with arbitrary length will be sent.
        1        The block header will have a fixed length of 11 characters.
        2        No block header will be sent. Not IEEE 488.2 compliant.
        =====    ===========================================================
        """,
        values=[0, 1, 2],
        validator=strict_discrete_set,
        cast=int,
    )

    datafile_frequency_unit = Instrument.control(
        ":FORM:SNP:FREQ?", ":FORM:SNP:FREQ %s",
        """Control the frequency unit displayed in a SNP data file.

        Valid values are HZ, KHZ, MHZ, GHZ.
        """,
        values=["HZ", "KHZ", "MHZ", "GHZ"],
        validator=strict_discrete_set,
    )

    datablock_numeric_format = Instrument.control(
        ":FORM:DATA?", ":FORM:DATA %s",
        """Control format for numeric I/O data representation.

        Valid values are:

        =====   ==========================================================================
        value   description
        =====   ==========================================================================
        ASCII   An ASCII number of 20 or 21 characters long with floating point notation.
        8byte   8 bytes of binary floating point number representation limited to 64 bits.
        4byte   4 bytes of floating point number representation.
        =====   ==========================================================================
        """,
        values={"ASCII": "ASC", "8byte": "REAL", "4byte": "REAL32"},
        map_values=True,
    )

    datafile_include_heading = Instrument.control(
        ":FORM:DATA:HEAD?", ":FORM:DATA:HEAD %d",
        """Control whether a heading is included in the data files. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    datafile_parameter_format = Instrument.control(
        ":FORM:SNP:PAR?", ":FORM:SNP:PAR %s",
        """Control the parameter format displayed in an SNP data file.

        Valid values are:

        =====   ===========================
        value   description
        =====   ===========================
        LINPH   Linear and Phase.
        LOGPH   Log and Phase.
        REIM    Real and Imaginary Numbers.
        =====   ===========================
        """,
        values=["LINPH", "LOGPH", "REIM"],
        validator=strict_discrete_set,
    )

    data_drawing_enabled = Instrument.control(
        "DD1?", "DD%d",
        """Control whether data drawing is enabled (True) or not (False). """,
        values={True: 1, False: 0},
        map_values=True,
    )

    event_status_enable_bits = Instrument.control(
        "*ESE?", "*ESE %d",
        """Control the Standard Event Status Enable Register bits.

        The register can be queried using the :meth:`~.query_event_status_register` method. Valid
        values are between 0 and 255. Refer to the instrument manual for an explanation of the bits.
        """,
        values=[0, 255],
        validator=strict_range,
        cast=int,
    )

    def query_event_status_register(self):
        """ Query the value of the Standard Event Status Register.

        Note that querying this value, clears the register. Refer to the instrument manual for an
        explanation of the returned value.
        """
        return self.values("*ESR?", cast=int)[0]

    service_request_enable_bits = Instrument.control(
        "*SRE?", "*SRE %d",
        """Control the Service Request Enable Register bits.

        Valid values are between 0 and 255; setting 0 performs a register reset. Refer to the
        instrument manual for an explanation of the bits.
        """,
        values=[0, 255],
        validator=strict_range,
        cast=int,
    )

    def return_to_local(self):
        """ Returns the instrument to local operation. """
        self.write("RTL")

    binary_data_byte_order = Instrument.control(
        ":FORM:BORD?", ":FORM:BORD %s",
        """Control the binary numeric I/O data byte order.

        valid values are:

        =====   =========================================
        value   description
        =====   =========================================
        NORM    The most significant byte (MSB) is first
        SWAP    The least significant byte (LSB) is first
        =====   =========================================
        """,
        values=["NORM", "SWAP"],
        validator=strict_discrete_set,
    )

    max_number_of_points = Instrument.control(
        ":SYST:POIN:MAX?", ":SYST:POIN:MAX %d",
        """Control the maximum number of points the instrument can measure in a sweep.

        Note that when this value is changed, the instrument will be rebooted.
        Valid values are 25000 and 100000. When 25000 points is selected, the instrument supports 16
        channels with 16 traces each; when 100000 is selected, the instrument supports 1 channel
        with 16 traces.
        """,
        values=[25000, 100000],
        validator=strict_discrete_set,
        cast=int,
    )

    number_of_ports = Instrument.measurement(
        ":SYST:PORT:COUN?",
        """Get the number of instrument test ports. """,
        cast=int,
    )

    number_of_channels = Instrument.control(
        ":DISP:COUN?", ":DISP:COUN %d",
        """Control the number of displayed (and therefore accessible) channels.

        When the system is in 25000 points mode, the number of channels can be 1, 2, 3, 4, 6, 8, 9,
        10, 12, or 16; when the system is in 100000 points mode, the system only supports 1 channel.
        If a value is provided that is not valid in the present mode, the instrument is set to the
        next higher channel number.
        """,
        values=[1, CHANNELS_MAX],
        validator=strict_range,
        cast=int,
    )

    display_layout = Instrument.control(
        ":DISP:SPL?", ":DISP:SPL %s",
        """Control the channel display layout in a Row-by-Column format.

        Valid values are: {}. The number following the R indicates the number of rows, following the
        C the number of columns; e.g. R2C2 results in a 2-by-2 layout. The options that contain two
        C's or R's result in asymmetric layouts; e.g. R2C1C2 results in a layout with 1 channel on
        top and two channels side-by-side on the bottom row.
        """.format(", ".join(DISPLAY_LAYOUTS)),
        values=DISPLAY_LAYOUTS,
        validator=strict_discrete_set,
        cast=str,
    )

    active_channel = Instrument.control(
        ":DISP:WIND:ACT?", ":DISP:WIND%d:ACT",
        """Control the active channel. """,
        values=[1, CHANNELS_MAX],
        validator=strict_range,
        cast=int,
    )

    bandwidth_enhancer_enabled = Instrument.control(
        ":SENS:BAND:ENH?", ":SENS:BAND:ENH %d",
        """Control the state of the IF bandwidth enhancer. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    trigger_source = Instrument.control(
        ":TRIG:SOUR?", ":TRIG:SOUR %s",
        """Control the source of the sweep/measurement triggering.

        Valid values are:

        =====   ==================================================
        value   description
        =====   ==================================================
        AUTO    Automatic triggering
        MAN     Manual triggering
        EXTT    Triggering from rear panel BNC via the GPIB parser
        EXT     External triggering port
        REM     Remote triggering
        =====   ==================================================
        """,
        values=["AUTO", "MAN", "EXTT", "EXT", "REM"],
        validator=strict_discrete_set,
    )

    external_trigger_type = Instrument.control(
        ":TRIG:EXT:TYP?", ":TRIG:EXT:TYP %s",
        """Control the type of trigger that will be associated with the external trigger.

        Valid values are POIN (for point), SWE (for sweep), CHAN (for channel), and ALL.
        """,
        values=TRIGGER_TYPES,
        validator=strict_discrete_set,
    )

    external_trigger_delay = Instrument.control(
        ":TRIG:EXT:DEL?", ":TRIG:EXT:DEL %g",
        """Control the delay time of the external trigger in seconds.

        Valid values are between 0 [s] and 10 [s] in steps of 1e-9 [s] (i.e. 1 ns).
        """,
        values=[0, 10],
        validator=strict_range,
    )

    external_trigger_edge = Instrument.control(
        ":TRIG:EXT:EDG?", ":TRIG:EXT:EDG %s",
        """Control the edge type of the external trigger.

        Valid values are POS (for positive or leading edge) or NEG (for negative or trailing edge).
        """,
        values=["POS", "NEG"],
        validator=strict_discrete_set,
    )

    external_trigger_handshake = Instrument.control(
        ":TRIG:EXT:HAND?", ":TRIG:EXT:HAND %s",
        """Control status of the external trigger handshake. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    remote_trigger_type = Instrument.control(
        ":TRIG:REM:TYP?", ":TRIG:REM:TYP %s",
        """Control the type of trigger that will be associated with the remote trigger.

        Valid values are POIN (for point), SWE (for sweep), CHAN (for channel), and ALL.
        """,
        values=TRIGGER_TYPES,
        validator=strict_discrete_set,
    )

    manual_trigger_type = Instrument.control(
        ":TRIG:MAN:TYP?", ":TRIG:MAN:TYP %s",
        """Control the type of trigger that will be associated with the manual trigger.

        Valid values are POIN (for point), SWE (for sweep), CHAN (for channel), and ALL.
        """,
        values=TRIGGER_TYPES,
        validator=strict_discrete_set,
    )

    def trigger(self):
        """ Trigger a continuous sweep from the remote interface. """
        self.write("*TRG")

    def trigger_single(self):
        """ Trigger a single sweep with synchronization from the remote interface. """
        self.write(":TRIG:SING")

    def trigger_continuous(self):
        """ Trigger a continuous sweep from the remote interface. """
        self.write(":TRIG")

    hold_function_all_channels = Instrument.control(
        ":SENS:HOLD:FUNC?", ":SENS:HOLD:FUNC %s",
        """Control the hold function of all channels.

        Valid values are:

        =====   =================================================
        value   description
        =====   =================================================
        CONT    Perform continuous sweeps on all channels
        HOLD    Hold the sweep on all channels
        SING    Perform a single sweep and then hold all channels
        =====   =================================================
        """,
        values=["CONT", "HOLD", "SING"],
        validator=strict_discrete_set,
    )

    def load_data_file(self, filename):
        """Load a data file from the VNA HDD into the VNA memory.

        :param str filename: full filename including path
        """

        self.write(f":MMEM:LOAD '{filename}'")

    def delete_data_file(self, filename):
        """Delete a file on the VNA HDD.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:DEL '{filename}'")

    def copy_data_file(self, from_filename, to_filename):
        """Copy a file on the VNA HDD.

        :param str from_filename: full filename including pat
        :param str to_filename: full filename including path
        """
        self.write(f":MMEM:COPY '{from_filename}', '{to_filename}'")

    def load_data_file_to_memory(self, filename):
        """Load a data file to a memory trace.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:LOAD:MDATA '{filename}'")

    def create_directory(self, dir_name):
        """Create a directory on the VNA HDD.

        :param str dir_name: directory name
        """
        self.write(f":MMEM:MDIR '{dir_name}'")

    def delete_directory(self, dir_name):
        """Delete a directory on the VNA HDD.

        :param str dir_name: directory name
        """
        self.write(f":MMEM:RDIR '{dir_name}'")

    def store_image(self, filename):
        """Capture a screenshot to the file specified.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:STOR:IMAG '{filename}'")

    def read_datafile(
        self,
        channel,
        sweep_points,
        datafile_freq,
        datafile_par,
        filename,
    ):
        """Read a data file from the VNA.

        :param int channel: Channel Index
        :param int sweep_points: number of sweep point as an integer
        :param DataFileFrequencyUnits datafile_freq: Data file frequency unit
        :param DataFileParameter datafile_par: Data file parameter format
        :param str filename: full path of the file to be saved
        """
        cur_ch = self.channels[channel]  # type: MeasurementChannel
        cur_ch.sweep_points = sweep_points
        self.datafile_frequency_unit = datafile_freq
        self.datafile_parameter_format = datafile_par
        self.write("TRS;WFS;OS2P")

        bytes_to_transfer = int(self.read_bytes(11)[2:11])
        data = self.read_bytes(bytes_to_transfer)
        with open(filename, "w") as textfile:
            data_list = data.split(b"\r\n")
            for s in data_list:
                textfile.write(str(s)[2 : len(s)] + "\n")  # noqa


class Port(Channel):
    """Represents a port within a :class:`~.MeasurementChannel` of the Anritsu MS464xB VNA. """
    placeholder = "pt"

    power_level = Channel.control(
        ":SOUR{{ch}}:POW:PORT{pt}?", ":SOUR{{ch}}:POW:PORT{pt} %g",
        """Control the power level (in dBm) of the indicated port on the indicated channel. """,
        values=[-3E1, 3E1],
        validator=strict_range,
    )


class Trace(Channel):
    """Represents a trace within a :class:`~.MeasurementChannel` of the Anritsu MS464xB VNA. """
    placeholder = "tr"

    def activate(self):
        """ Set the indicated trace as the active one. """
        self.write(":CALC{{ch}}:PAR{tr}:SEL")

    measurement_parameter = Channel.control(
        ":CALC{{ch}}:PAR{tr}:DEF?", ":CALC{{ch}}:PAR{tr}:DEF %s",
        """Control the measurement parameter of the indicated trace.

        Valid values are any S-parameter (e.g. S11, S12, S41) for 4 ports, or one of the
        following:

        =====   ================================================================
        value   description
        =====   ================================================================
        Sxx     S-parameters (1-4 for both x)
        MIX     Response Mixed Mode
        NFIG    Noise Figure trace response (only with option 41 or 48)
        NPOW    Noise Power trace response (only with option 41 or 48)
        NTEMP   Noise Temperature trace response (only with option 41 or 48)
        AGA     Noise Figure Available Gain trace response (only with option 48)
        IGA     Noise Figure Insertion Gain trace response (only with option 48)
        =====   ================================================================
        """,
        values=AnritsuMS464xB.SPARAM_LIST + ["MIX", "NFIG", "NPOW", "NTEMP", "AGA", "IGA"],
        validator=strict_discrete_set,
    )


class MeasurementChannel(Channel):
    """Represents a channel of Anritsu MS464xB VNA.

    Contains 4 instances of :class:`~.Port` (accessible via the `ports` dict or directly `pt_` + the
    port number) and up to 16 instances of :class:`~.Trace` (accessible via the `traces` dict or
    directly `tr_` + the trace number).

    :param frequency_range: defines the number of installed ports (default=4).
    :type frequency_range: list of floats
    :param traces: defines the number of traces that is assumed for the channel
        (between 1 and 16); if not provided, the maximum number is assumed; "auto" is provided,
        the instrument will be queried for the number of traces.
    :type traces: int (1-16) or str ("auto") or None
    """

    def __init__(self, *args, frequency_range=None, traces=None, **kwargs):
        super().__init__(*args, **kwargs)

        for pt in range(self.parent.PORTS):
            self.add_child(Port, pt + 1, collection="ports", prefix="pt_")

        if traces is None:
            number_of_traces = self.parent.TRACES_MAX
        elif traces == "auto":
            number_of_traces = None
        else:
            number_of_traces = traces

        self.update_traces(number_of_traces)

        if frequency_range is not None:
            self.update_frequency_range(frequency_range)

    def update_frequency_range(self, frequency_range):
        """Update the values-attribute of the frequency-related dynamic properties.

        :param list frequency_range: the frequency range that the instrument is capable of.
        """
        self.frequency_start_values = frequency_range
        self.frequency_stop_values = frequency_range
        self.frequency_center_values = frequency_range
        self.frequency_CW_values = frequency_range

        self.frequency_span_values = [2, frequency_range[1]]

    def update_traces(self, number_of_traces=None):
        """Create or remove traces to be correct with the actual number of traces.

        :param int number_of_traces: optional, if given defines the desired number of traces.
        """
        if number_of_traces is None:
            number_of_traces = self.number_of_traces

        if not hasattr(self, "traces"):
            self.traces = {}

        if len(self.traces) == number_of_traces:
            return

        # Remove redant channels
        while len(self.traces) > number_of_traces:
            self.remove_child(self.traces[len(self.traces)])

        # Remove create new channels
        while len(self.traces) < number_of_traces:
            self.add_child(Trace, len(self.traces) + 1, collection="traces", prefix="tr_")

    def check_errors(self):
        return self.parent.check_errors()

    def activate(self):
        """ Set the indicated channel as the active channel. """
        self.write(":DISP:WIND{ch}:ACT")

    number_of_traces = Channel.control(
        ":CALC{ch}:PAR:COUN?", ":CALC{ch}:PAR:COUN %d",
        """Control the number of traces on the specified channel

        Valid values are between 1 and 16.
        """,
        values=[1, AnritsuMS464xB.TRACES_MAX],
        validator=strict_range,
        cast=int,
    )

    active_trace = Channel.setting(
        ":CALC{ch}:PAR%d:SEL",
        """Set the active trace on the indicated channel. """,
        values=[1, AnritsuMS464xB.TRACES_MAX],
        validator=strict_range,
    )

    display_layout = Channel.control(
        ":DISP:WIND{ch}:SPL?", ":DISP:WIND{ch}:SPL %s",
        """Control the trace display layout in a Row-by-Column format for the indicated channel.

        Valid values are: {}. The number following the R indicates the number of rows, following the
        C the number of columns; e.g. R2C2 results in a 2-by-2 layout. The options that contain two
        C's or R's result in asymmetric layouts; e.g. R2C1C2 results in a layout with 1 trace on top
        and two traces side-by-side on the bottom row.
        """.format(", ".join(AnritsuMS464xB.DISPLAY_LAYOUTS)),
        values=AnritsuMS464xB.DISPLAY_LAYOUTS,
        validator=strict_discrete_set,
        cast=str,
    )

    application_type = Channel.control(
        ":CALC{ch}:APPL:MEAS:TYP?", ":CALC{ch}:APPL:MEAS:TYP %s",
        """Control the application type of the specified channel.

        Valid values are TRAN (for transmission/reflection), NFIG (for noise figure measurement),
        PULS (for PulseView).
        """,
        values=["TRAN", "NFIG", "PULS"],
        validator=strict_discrete_set,
    )

    hold_function = Channel.control(
        ":SENS{ch}:HOLD:FUNC?", ":SENS{ch}:HOLD:FUNC %s",
        """Control the hold function of the specified channel.

        valid values are:

        =====   =================================================
        value   description
        =====   =================================================
        CONT    Perform continuous sweeps on all channels
        HOLD    Hold the sweep on all channels
        SING    Perform a single sweep and then hold all channels
        =====   =================================================
        """,
        values=["CONT", "HOLD", "SING"],
        validator=strict_discrete_set,
    )

    cw_mode_enabled = Channel.control(
        ":SENS{ch}:SWE:CW?", ":SENS{ch}:SWE:CW %d",
        """Control the state of the CW sweep mode of the indicated channel. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    cw_number_of_points = Channel.control(
        ":SENS{ch}:SWE:CW:POIN?", ":SENS{ch}:SWE:CW:POIN %g",
        """Control the CW sweep mode number of points of the indicated channel.

        Valid values are between 1 and 25000 or 100000 depending on the maximum points setting.
        """,
        values=[1, 100000],
        validator=strict_range,
        cast=int,
    )

    number_of_points = Channel.control(
        "SENS{ch}:SWE:POIN?", "SENS{ch}:SWE:POIN %g",
        """Control the number of measurement points in a frequency sweep of the indicated channel.

        Valid values are between 1 and 25000 or 100000 depending on the maximum points setting.
        """,
        values=[1, 100000],
        validator=strict_range,
        cast=int,
    )

    frequency_start = Channel.control(
        ":SENS{ch}:FREQ:STAR?", ":SENS{ch}:FREQ:STAR %g",
        """Control the start value of the sweep range of the indicated channel in hertz.

        Valid values are between 1E7 [Hz] (i.e. 10 MHz) and 4E10 [Hz] (i.e. 40 GHz).
        """,
        values=AnritsuMS464xB.FREQUENCY_RANGE,
        validator=strict_range,
        dynamic=True,
    )

    frequency_stop = Channel.control(
        ":SENS{ch}:FREQ:STOP?", ":SENS{ch}:FREQ:STOP %g",
        """Control the stop value of the sweep range of the indicated channel in hertz.

        Valid values are between 1E7 [Hz] (i.e. 10 MHz) and 4E10 [Hz] (i.e. 40 GHz).
        """,
        values=AnritsuMS464xB.FREQUENCY_RANGE,
        validator=strict_range,
        dynamic=True,
    )

    frequency_span = Channel.control(
        ":SENS{ch}:FREQ:SPAN?", ":SENS{ch}:FREQ:SPAN %g",
        """Control the span value of the sweep range of the indicated channel in hertz.

        Valid values are between 2 [Hz] and 4E10 [Hz] (i.e. 40 GHz).
        """,
        values=[2, AnritsuMS464xB.FREQUENCY_RANGE[1]],
        validator=strict_range,
        dynamic=True,
    )

    frequency_center = Channel.control(
        ":SENS{ch}:FREQ:CENT?", ":SENS{ch}:FREQ:CENT %g",
        """Control the center value of the sweep range of the indicated channel in hertz.

        Valid values are between 1E7 [Hz] (i.e. 10 MHz) and 4E10 [Hz] (i.e. 40 GHz).
        """,
        values=AnritsuMS464xB.FREQUENCY_RANGE,
        validator=strict_range,
        dynamic=True,
    )

    frequency_CW = Channel.control(
        ":SENS{ch}:FREQ:CW?", ":SENS{ch}:FREQ:CW %g",
        """Control the CW frequency of the indicated channel in hertz.

        Valid values are between 1E7 [Hz] (i.e. 10 MHz) and 4E10 [Hz] (i.e. 40 GHz).
        """,
        values=AnritsuMS464xB.FREQUENCY_RANGE,
        validator=strict_range,
        dynamic=True,
    )

    def clear_average_count(self):
        """ Clear and restart the averaging sweep count of the indicated channel. """
        self.write(":SENS{ch}:AVER:CLE")

    average_count = Channel.control(
        ":SENS{ch}:AVER:COUN?", ":SENS{ch}:AVER:COUN %d",
        """Control the averaging count for the indicated channel.

        The channel must be turned on. Valid values are between 1 and 1024.
        """,
        values=[1, 1024],
        validator=strict_range,
        cast=int,
    )

    average_sweep_count = Channel.measurement(
        ":SENS{ch}:AVER:SWE?",
        """Get the averaging sweep count for the indicated channel. """,
        cast=int,
    )

    average_type = Channel.control(
        ":SENS{ch}:AVER:TYP?", ":SENS{ch}:AVER:TYP %s",
        """Control the averaging type to for the indicated channel.

        Valid values are POIN (point-by-point) or SWE (sweep-by-sweep)
        """,
        values=["POIN", "SWE"],
        validator=strict_discrete_set,
    )

    averaging_enabled = Channel.control(
        ":SENS{ch}:AVER?", ":SENS{ch}:AVER %d",
        """Control whether the averaging is turned on for the indicated channel. """,
        values={True: 1, False: 0},
        map_values=True,
    )

    sweep_type = Channel.control(
        ":SENS{ch}:SWE:TYP?", ":SENS{ch}:SWE:TYP %s",
        """Control the sweep type of the indicated channel.

        Valid options are:

        =====   ===============================================================
        value   description
        =====   ===============================================================
        LIN     Frequency-based linear sweep
        LOG     Frequency-based logarithmic sweep
        FSEGM   Segment-based sweep with frequency-based segments
        ISEGM   Index-based sweep with frequency-based segments
        POW     Power-based sweep with either a CW frequency or swept-frequency
        MFGC    Multiple frequency gain compression
        =====   ===============================================================
        """,
        validator=strict_discrete_set,
        values=["LIN", "LOG", "FSEGM", "ISEGM", "POW", "MFGC"],
    )

    sweep_mode = Channel.control(
        ":SENS{ch}:SA:MODE?", ":SENS{ch}:SA:MODE %s",
        """Control the sweep mode for Spectrum Analysis on the indicated channel.

        Valid options are VNA (for a VNA-like mode where the instrument will only measure at points
        in the frequency list) or CLAS (for a classical mode, where the instrument will scan all
        frequencies in the range).""",
        validator=strict_discrete_set,
        values=["VNA", "CLAS"],
    )

    sweep_time = Channel.control(
        ":SENS{ch}:SWE:TIM?", ":SENS{ch}:SWE:TIM %d",
        """Control the sweep time of the indicated channel.

        Valid values are between 2 and 100000.""",
        validator=strict_range,
        values=[2, 100000],
    )

    bandwidth = Channel.control(
        ":SENS{ch}:BWID?", ":SENS{ch}:BWID %g",
        """Control the IF bandwidth for the indicated channel.

        Valid values are between 1 [Hz] and 1E6 [Hz] (i.e. 1 MHz). The system will automatically
        select the closest IF bandwidth from the available options (1, 3, 10 ... 1E5, 3E5, 1E6).
        """,
        values=[1, 1E6],
        validator=strict_range,
    )

    calibration_enabled = Channel.control(
        ":SENS{ch}:CORR:STAT?", ":SENS{ch}:CORR:STAT %d",
        """Control whether the RF correction (calibration) is enabled for indicated channel. """,
        values={True: 1, False: 0},
        map_values=True,
    )


class AnritsuMS4642B(AnritsuMS464xB):
    """A class representing the Anritsu MS4642B Vector Network Analyzer (VNA).

    This VNA has a frequency range from 10 MHz to 20 GHz and is part of the
    :class:`~.AnritsuMS464xB` family of instruments; for documentation, for documentation refer to
    this base class.
    """
    FREQUENCY_RANGE = [1E7, 2E10]


class AnritsuMS4644B(AnritsuMS464xB):
    """A class representing the Anritsu MS4644B Vector Network Analyzer (VNA).

    This VNA has a frequency range from 10 MHz to 40 GHz and is part of the
    :class:`~.AnritsuMS464xB` family of instruments; for documentation, for documentation refer to
    this base class.
    """
    FREQUENCY_RANGE = [1E7, 4E10]


class AnritsuMS4645B(AnritsuMS464xB):
    """A class representing the Anritsu MS4645B Vector Network Analyzer (VNA).

    This VNA has a frequency range from 10 MHz to 50 GHz and is part of the
    :class:`~.AnritsuMS464xB` family of instruments; for documentation, for documentation refer to
    this base class.
    """
    FREQUENCY_RANGE = [1E7, 5E10]


class AnritsuMS4647B(AnritsuMS464xB):
    """A class representing the Anritsu MS4647B Vector Network Analyzer (VNA).

    This VNA has a frequency range from 10 MHz to 70 GHz and is part of the
    :class:`~.AnritsuMS464xB` family of instruments; for documentation, for documentation refer to
    this base class.
    """
    FREQUENCY_RANGE = [1E7, 7E10]
