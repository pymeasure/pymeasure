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

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_range, strict_discrete_range


class VNAChannel(Channel):
    """ Implementation of a Anritsu MS464xB channel. """

    _SWEEP_TYPES = ["LIN", "LOG", "FSEGM", "ISEGM", "POW", "MFGC"]

    center_frequency = Instrument.control(
        ":SENS<ch>:FREQ:CENT?", ":SENS<ch>:FREQ:CENT %d",
        """Center Frequency in Hz""",
        validator=strict_range,
        values=[30000, 8000000000]
    )

    cw_frequency = Instrument.control(
        ":SENS<ch>:FREQ:CW?", ":SENS<ch>:FREQ:CW %d",
        """Center Frequency in Hz""",
        validator=strict_range,
        values=[300000, 8000000000]
    )

    span_frequency = Instrument.control(
        ":SENS<ch>:FREQ:SPAN?", ":SENS<ch>:FREQ:SPAN %d",
        """Span Frequency in Hz""",
        validator=strict_range,
        values=[1, 8000000000]
    )

    start_frequency = Instrument.control(
        ":SENS<ch>:FREQ:STAR?", ":SENS<ch>:FREQ:STAR %d",
        """ Starting frequency in Hz """,
        validator=strict_range,
        values=[1, 8000000000]
    )

    stop_frequency = Instrument.control(
        ":SENS<ch>:FREQ:STOP?", ":SENS<ch>:FREQ:STOP %d",
        """ Stop frequency in Hz """,
        validator=strict_range,
        values=[1, 8000000000]
    )

    sweep_type = Instrument.control(
        ":SENS<ch>:SWE:TYP?", ":SENS<ch>:SWE:TYP %s",
        """ Sweep Type. Valid options are LIN|LOG|FSEGM|ISEGM|POW|MFGC""",
        validator=strict_discrete_range,
        values=_SWEEP_TYPES
    )

    sweep_mode = Instrument.control(
        ":SENS<ch>:SA:MODE?", ":SENS<ch>:SA:MODE %s",
        """ Sweep mode. Valid options are VNA|CLAS """,
        validator=strict_discrete_range,
        values=["VNA", "CLAS"]
    )

    sweep_point = Instrument.control(
        ":SENS<ch>:SWE:POI?", ":SENS<ch>:SWE:POI %d",
        """ Sweep point""",
        validator=strict_range,
        values=[2, 100000]
    )

    num_averages = Instrument.control(
        "SENS<ch>:AVER:COUN?", "SENS<ch>:AVER:COUN %d",
        """ Sets the number of averages""",
        validator=strict_range,
        values=[1, 20000]
    )

    bandwidth = Instrument.control(
        "SENS<ch>:BWID?", "SENS<ch>:BWID %d",
        """ Sets the IF bandwidth""",
        validator=strict_range,
        values=[1, 1000000]
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        return self.instrument.values(command.replace("<ch>", str(self.number)),
                                      **kwargs)

    def write(self, command):
        self.instrument.write(command.replace("<ch>", str(self.number)))


class AnritsuMS464xB(Instrument):
    """ Represents the Anritsu MS474xB VNA. Implements controls to change the analysis
        range and to retreve the data for the trace.
    """
    channels = Instrument.ChannelCreator(
        VNAChannel, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15))

    def __init__(self, adapter, **kwargs):
        super().__init__(
            adapter,
            "Anritsu MS464xB",
            **kwargs
        )

    def load_data_file(self, filename: str):
        self.write(f":MMEM:LOAD '{filename}'")

    def delete_data_file(self, filename: str):
        self.write(f":MMEM:DEL '{filename}'")

    def copy_data_file(self, from_filename: str, to_filename: str):
        self.write(f":MMEM:COPY '{from_filename}', '{to_filename}'")

    def load_data_file_to_memory(self, filename: str):
        self.write(f":MMEM:LOAD:MDATA '{filename}'")

    def create_directory(self, dir_name: str):
        self.write(f":MMEM:MDIR '{dir_name}'")

    def delete_directory(self, dir_name: str):
        self.write(f":MMEM:RDIR '{dir_name}'")

    def store_image(self, filename: str):
        self.write(f":MMEM:STOR:IMAG '{filename}'")
