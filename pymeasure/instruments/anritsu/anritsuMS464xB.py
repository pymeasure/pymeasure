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
from enum import Enum
from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import (
    strict_range,
    strict_discrete_set,
)


class CustomEnum(Enum):
    """Provides additional methods to Enum:

    * Conversion to string automatically replaces '_' with ' ' in names
      and converts to title case

    * get classmethod to get enum reference with name or integer

    .. automethod:: __str__
    """

    def __str__(self):
        """Gives title case string of enum value."""
        return str(self.value).replace("_", " ")


class VNAChannel(Channel):
    """Implementation of an Anritsu MS464xB channel."""

    _SWEEP_TYPES = {"LIN", "LOG", "FSEGM", "ISEGM", "POW", "MFGC"}

    center_frequency = Instrument.control(
        ":FREQ:CENT?",
        ":FREQ:CENT %d",
        """Control the center frequency in Hz.""",
        validator=strict_range,
        values=[30000, 8000000000],
    )

    cw_frequency = Instrument.control(
        ":FREQ:CW?",
        ":FREQ:CW %d",
        """Control CW Frequency in Hz.""",
        validator=strict_range,
        values=[30000, 8000000000],
    )

    span_frequency = Instrument.control(
        ":FREQ:SPAN?",
        ":FREQ:SPAN %d",
        """Control Span Frequency in Hz""",
        validator=strict_range,
        values=[1, 8000000000],
    )

    start_frequency = Instrument.control(
        ":FREQ:STAR?",
        ":FREQ:STAR %d",
        """Control starting frequency in Hz.""",
        validator=strict_range,
        values=[1, 8000000000],
    )

    stop_frequency = Instrument.control(
        ":FREQ:STOP?",
        ":FREQ:STOP %d",
        """Control stop frequency in Hz.""",
        validator=strict_range,
        values=[1, 8000000000],
    )

    sweep_type = Instrument.control(
        ":SWE:TYP?",
        ":SWE:TYP %s",
        """Control sweep Type. Valid options are LIN|LOG|FSEGM|ISEGM|POW|MFGC.""",
        validator=strict_discrete_set,
        values=_SWEEP_TYPES,
    )

    sweep_mode = Instrument.control(
        ":SA:MODE?",
        ":SA:MODE %s",
        """ Sweep mode. Valid options are VNA|CLAS.""",
        validator=strict_discrete_set,
        values=["VNA", "CLAS"],
    )

    sweep_points = Instrument.control(
        ":SWE:POI?",
        ":SWE:POI %d",
        """Controls the number of measurement points.""",
        validator=strict_range,
        values=[2, 100000],
    )

    sweep_time = Instrument.control(
        ":SWE:TIME?",
        ":SWE:TIME %d",
        """Controls the sweep time of the indicated channel.""",
        validator=strict_range,
        values=[2, 100000],
    )

    num_averages = Instrument.control(
        ":AVER:COUN?",
        ":AVER:COUN %d",
        """Controls the number of averages.""",
        validator=strict_range,
        values=[1, 20000],
    )

    bandwidth = Instrument.control(
        ":BWID?",
        ":BWID %d",
        """Controls the IF bandwidth.""",
        validator=strict_range,
        values=[1, 1000000],
    )

    def insert_id(self, command):
        return f":SENS{self.id}{command}"

    def clear_averaging(self):
        """Clears and restarts the averaging sweep count"""
        self.write(":AVER:CLE")


class AnritsuMS464xB(Instrument):
    """Represents the Anritsu MS474xB VNA. Implements controls to change the analysis
    range and to retreve the data for the trace.
    """

    channels = Instrument.ChannelCreator(
        VNAChannel, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16)
    )

    class BinaryDataByteFormat(CustomEnum):
        MSB_FIRST = "NORM"
        LSB_FIRST = "SWAP"

    class DataFileParameter(CustomEnum):
        """Parameter format in a data file"""

        LINEAR_AND_PHASE = "LINPH"
        LOG_AND_PHASE = "LOGPH"
        REAL_AND_IMAGINARY_NUMBERS = "REIM"

    class BinaryDataFormat(CustomEnum):
        """Binary Data file format."""

        ASC = "ASC"
        REAL = "REAL"
        REAL32 = "REAL32"

    class DataFileFrequencyUnits(CustomEnum):
        """Binary Data file frequency units."""

        HZ = "HZ"
        KHZ = "KHZ"
        MHZ = "MHZ"
        GHZ = "GHZ"

    def __init__(self, adapter, name="Anritsu MS464xB", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def load_data_file(self, filename):
        """Loads a data file in VNA HDD.

        :param str filename: full filename including path
        """

        self.write(f":MMEM:LOAD '{filename}'")

    def delete_data_file(self, filename):
        """Deletes a file on the VNA HDD.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:DEL '{filename}'")

    def copy_data_file(self, from_filename, to_filename):
        """Copies a file on the VNA HDD.

        :param str from_filename: full filename including pat
        :param str to_filename: full filename including path
        """
        self.write(f":MMEM:COPY '{from_filename}', '{to_filename}'")

    def load_data_file_to_memory(self, filename):
        """Loads a data file to a memory trace.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:LOAD:MDATA '{filename}'")

    def create_directory(self, dir_name):
        """Create directory on the VNA HDD.

        :param str dir_name: directory name
        """
        self.write(f":MMEM:MDIR '{dir_name}'")

    def delete_directory(self, dir_name):
        """Deletes a directory on the VNA HDD.

        :param str dir_name: directory name
        """
        self.write(f":MMEM:RDIR '{dir_name}'")

    def store_image(self, filename):
        """Captures a screenshot to the file specified.

        :param str filename: full filename including path
        """
        self.write(f":MMEM:STOR:IMAG '{filename}'")

    binary_data_byte_format = Instrument.control(
        ":FORM:BORD?",
        ":FORM:BORD %s",
        """ IO Data format. NORM|SWAP = MSB First|LSB First.""",
        validator=strict_discrete_set,
        values=BinaryDataByteFormat,
    )

    binary_data_format = Instrument.control(
        ":FORM:DATA?",
        ":FORM:DATA %s",
        """ IO Data format. ASC|REAL|REAL32.""",
        validator=strict_discrete_set,
        values=BinaryDataFormat,
    )

    datafile_header = Instrument.control(
        ":FORM:DATA:HEAD?",
        ":FORM:DATA:HEAD %d",
        """Sets the on/off state of including a heading with data files.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    datafile_frequency = Instrument.control(
        ":FORM:SNP:FREQ?",
        ":FORM:SNP:FREQ %s",
        """Controls the frequency unit in a SNP data file.

        Use the DataFileFrequency enum as input values.""",
        validator=strict_discrete_set,
        values=DataFileFrequencyUnits,
    )

    datafile_parameter = Instrument.control(
        ":FORM:SNP:PAR?",
        ":FORM:SNP:PAR %s",
        """Controls the parameter format in a SNP data file.

        Use the DataFileParameter enum as input values.""",
        validator=strict_discrete_set,
        values=DataFileParameter,
    )

    def read_datafile(
        self,
        channel,
        sweep_points,
        datafile_freq,
        datafile_par,
        filename,
    ):
        """Reads a data file from the VNA

        :param int channel: Channel Index
        :param int sweep_points: number of sweep point as an integer
        :param DataFileFrequencyUnits datafile_freq: Data file frequency based on enum
        :param DataFileParameter datafile_par: Data file parameter based on enum
        :param str filename: full path of the file to be saved
        """
        cur_ch = self.channels[channel]  # type: VNAChannel
        cur_ch.sweep_points = sweep_points
        self.datafile_frequency = datafile_freq
        self.datafile_parameter = datafile_par
        self.write("TRS;WFS;OS2P")

        bytes_to_transfer = int(self.read_bytes(11)[2:11])
        data = self.read_bytes(bytes_to_transfer)
        with open(filename, "w") as textfile:
            data_list = data.split(b"\r\n")
            for s in data_list:
                textfile.write(str(s)[2 : len(s)] + "\n")  # noqa
