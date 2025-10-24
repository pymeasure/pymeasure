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

import numpy as np

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set


class Marker(Channel):
    """A class representing a marker on a measurement trace."""

    placeholder = "mkr"

    enabled = Channel.control(
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:STATE?",
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:STATE %d",
        """Control the status of the marker (bool).""",
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        )

    is_discrete = Channel.control(
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:DISC?",
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:DISC %d",
        """Control the discrete status of the marker (bool).

        - ``True``: The marker snaps to the closest actual data point.
        - ``False``: The data is interpolated between data points.

        """,
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        )

    x = Channel.control(
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:X?",
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:X %f",
        """Control the marker's X value (float).""",
        )

    y = Channel.measurement(
        "CALC{{{{ch}}}}:MEAS{{tr}}:MARK{mkr}:Y?",
        """Get the marker's Y value ([float, float]).""",
        )


class Trace(Channel):
    """A class representing a Keysight PNA measurement trace."""

    # add the 15 markers to the trace
    markers = Instrument.MultiChannelCreator(Marker, list(range(1, 16)), prefix="mkr_")

    placeholder = "tr"

    def read_buffer(self, data_format="ascii"):
        """
        Read the data buffer of the PNA.

        :param data_format: str, strictly ``ascii``, ``real32`` or ``real64``
        :return: ndarray
        """

        if data_format == "ascii":
            got = np.array(self.read().split(","))
            return got
        else:  # 'real32' and 'real64' format
            got = self.read_bytes(1)
            expected = b"#"
            if got != expected:
                raise ConnectionError(f"Expected '{expected}', but got '{got}'")

            number_of_digits = int(self.read_bytes(1))
            buffer_length = int(self.read_bytes(number_of_digits))
            buffer = self.read_bytes(buffer_length)
            self.read_bytes(1)  # read the termination byte

            data_type = np.float64
            if data_format == "real32":
                data_type = np.float32

            return np.frombuffer(buffer, dtype=data_type)

    parameter = Channel.measurement(
        "CALC{{ch}}:MEAS{tr}:PAR?",
        """Get the measurement parameter of the trace (str).""",
        preprocess_reply=lambda v: v.strip('"'),
        maxsplit=0,
        )

    @property
    def x_data(self):
        """Get the X data of the trace (ndarray).

        The data type of the array elements is equal to the currently set
        :attr:`~pymeasure.instruments.keysight.KeysightPNA.data_format`.
        """
        data_format = self.parent.parent.data_format
        self.write("CALC{{ch}}:MEAS{tr}:X?")
        return self.read_buffer(data_format)

    x_unit = Channel.measurement(
        "CALC{{ch}}:MEAS{tr}:X:AXIS:UNIT?",
        """Get the X unit of the trace (str).

        :return: ``FREQ``, ``POW``, ``PHAS``, ``DC``, ``POIN`` or ``DEF``
        """,
        )

    @property
    def y_data(self):
        """Get the Y data of the trace in the displayed format (ndarray).

        The data type of the array elements is equal to the currently set
        :attr:`~pymeasure.instruments.keysight.KeysightPNA.data_format`.
        The method returns the data from access point 2.
        Please check PNA help for further information about the data access map.
        """
        data_format = self.parent.parent.data_format
        self.write("CALC{{ch}}:MEAS{tr}:DATA:FDATA?")  # data access point 2
        return self.read_buffer(data_format)

    @property
    def y_data_complex(self):
        """Get the complex Y data of the trace (2D ndarray).

        The data type of the array elements is equal to the currently set
        :attr:`~pymeasure.instruments.keysight.KeysightPNA.data_format`.
        The method returns the data from access point 1.
        Please check PNA help for further information about the data access map.
        """
        data_format = self.parent.parent.data_format
        self.write("CALC{{ch}}:MEAS{tr}:DATA:SDATA?")  # data access point 1
        got = self.read_buffer(data_format)
        return np.reshape(got, (-1, 2))

    y_unit = Channel.measurement(
        "CALC{{ch}}:MEAS{tr}:Y:AXIS:UNIT?",
        """Get the Y unit of the trace (str).

        :return: ``HZ``, ``SEC``, ``MIN``, ``HOUR``, ``DAY``, ``DB``, ``DBM``,
            ``DBMV``, ``WATT``, ``FAR``, ``HENR``, ``OHM``, ``MHO``, ``SIEM``,
            ``VOLT``, ``DEGR``, ``RAD``, ``MET``, ``DPHZ``, ``UNIT``, ``NON``,
            ``TNOR``, ``NTEM``, ``KELV``, ``CENT``, ``FAHR``, ``FEET``, ``INCH``,
            ``DBMAAMP``, ``VOLTA``, ``DBUV``, ``PERC``, ``DMVR``, ``DUVR``, ``DMAR``,
            ``WPHZ``, ``VRO``, ``ARO``, ``DBC``, ``DVP``, ``DCP``, ``DBP``, ``HZP``,
            ``PRH``, ``VPH``, ``DBV`` or ``DEF``

        """,
        )


class MeasurementChannel(Channel):
    """A class representing a Keysight PNA measurement channel."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.update_traces()

    def initiate(self):
        """Initiate an immidiate trigger.

        .. note::
            The trigger source has to be set to `MANUAL` for this command.
            One trigger signal is sent each time :meth:`initiate()` is executed.

        """
        self.write("INIT{ch}:IMM")

    def single(self):
        """Trigger a single sweep."""
        self.write("SENS{ch}:SWE:MODE SING")

    def continuous(self):
        """Set the channel to `CONTINUOUS` mode."""
        self.write("SENS{ch}:SWE:MODE CONT")

    def hold(self):
        """Set the channel on `HOLD` mode."""
        self.write("SENS{ch}:SWE:MODE HOLD")

    def update_traces(self):
        """Update the traces of the measurement channel."""

        if not hasattr(self, "traces"):
            self.traces = {}

        # remove all traces
        for trace in list(self.traces.keys()):
            self.remove_child(self.traces[trace])

        # add the new traces
        for trace in self.measurements:
            self.add_child(Trace,
                           id=trace,
                           collection="traces",
                           prefix="tr_",
                           )

    number_of_points = Channel.measurement(
        "SENS{ch}:SWE:POIN?",
        """Get the number of points of the channel (int).""",
        cast=int,
        )

    measurements = Channel.measurement(
        "SYST:MEAS:CAT? {ch}",
        """Get the measurement trace numbers of the channel (list of int).""",
        preprocess_reply=lambda v: v.strip('"'),
        get_process=lambda v: [v],  # always return a list, even if only one trace exists
        cast=int,
        )


class KeysightPNA(SCPIMixin, Instrument):
    """A class representing a Keysight PNA vector network analyzer.

    :param str data_format: strictly ``ascii``, ``real32`` or ``real64``
    :param bool byte_order_swapped:

    See :attr:`.data_format` and :attr:`.byte_order_swapped` for more information.

    .. code-block:: python

        pna = KeysightPNA("GPIB0::16::INSTR",
                          timeout=5000,
                          )

        pna.load_state("D:/States/MyState.csa")
        pna.adapter.connection.timeout = 20000  # set a new timeout to 20 sec
        pna.ch_1.single()  # execute a single trigger of channel 1
        pna.complete  # wait till the sweep has finished
        x_data = pna.ch_1.tr_1.x_data  # get the X data of trace 1 in channel 1
        y_data = pna.ch_2.tr_5.y_data  # get the Y data of trace 5 in channel 2
        y_complex = pna.ch_2.tr_5.y_data_complex  # get the complex Y data of trace 5 in channel 2
        pna.ch_1.tr_1.mkr_1.enabled = True  # Activate marker 1 on trace 1 in channel 1
        pna.ch_1.tr_1.mkr_1.x = 123e6  # Set marker 1 to 123 MHz
        mkr_y = pna.ch_1.tr_1.mkr_1.y  # Read the marker 1 y data

    Workflow:
        - Configure the channels/measurements directly on the PNA
        - Calibrate the PNA
        - Save the state as csa file
        - Perform single triggers for the different channels
        - Measurement data can be accessed with the channel and trace numbers

    """

    def __init__(self, adapter,
                 name="Keysight PNA",
                 data_format="real64",
                 byte_order_swapped=True,
                 **kwargs):
        super().__init__(
            adapter,
            name,
            read_termination="\n",
            **kwargs
        )

        self.data_format = data_format
        self.byte_order_swapped = byte_order_swapped
        self.update_channels()

    def abort(self):
        """Stop all sweeps.

        Note that the configured trigger will restart the sweeps.
        """
        self.write("ABOR")

    def load_state(self, file_name):
        """Load an instrument state from file.

        :param str file_name: e.g. ``D:/my_pna_state.csa``
        """
        self.write(f"MMEM:LOAD '{file_name}'")
        self.update_channels()

    def update_channels(self):
        """Update the measurement channels of the PNA."""

        if not hasattr(self, "channels"):
            self.channels = {}

        # remove all channels
        for channel in list(self.channels.keys()):
            self.remove_child(self.channels[channel])

        # add the new channels
        for channel in self.measurement_channels:
            self.add_child(MeasurementChannel,
                           id=channel,
                           )

    byte_order_swapped = Instrument.control(
        "FORM:BORD?",
        "FORM:BORD %s",
        """
        Control whether the byte order is swapped for data transfer (bool).

        Some computers read data from the analyzer in the reverse order. This property is only
        effective if :attr:`.data_format` set to ``real32`` or ``real64``. If :attr:`.data_format`
        is set to ``ascii``, :attr:`.byte_order_swapped` is ignored.

        - ``True``: Use for IBM compatible computers.
        - ``False``: The controller is anything other than an IBM compatible computers
            or when using VEE, LabView, or T&M Tool kit.

        """,
        map_values=True,
        validator=strict_discrete_set,
        values={False: "NORM",
                True: "SWAP",
                },
        )

    data_format = Instrument.control(
        "FORM?",
        "FORM %s",
        """
        Control the data format (strictly ``ascii``, ``real32`` or ``real64``).

        - ``ascii`` is but slow. Use it when you have to transfer
          small amounts data.
        - ``real32`` is  best for transferring large amounts of measurement data.
          It can cause rounding errors in frequency data.
        - ``real64`` is slower than ``real32`` but has more significant digits.
          It is required to accurately represent frequency data.

        In the PNA, measurement data is stored as 32 bit and frequencies stored as 64 bit.
        Therefore, use ``real32`` when getting data and ``real64`` when getting frequencies.
        It avoids losing any precision as well as getting the maximum speed on the data transfer.

        .. note::
            Executing :meth:`~pymeasure.instruments.Instrument.reset`
            sets :attr:`data_format` to ``ascii``.

        """,
        map_values=True,
        validator=strict_discrete_set,
        values={"ascii": "ASC,0",
                "real32": "REAL,32",
                "real64": "REAL,64",
                },
        maxsplit=0,
        )

    measurement_channels = Instrument.measurement(
        "SYST:CHAN:CAT?",
        """Get the channel numbers that are currently in use (list of int).""",
        preprocess_reply=lambda v: v.strip('"'),
        get_process=lambda v: [v],  # always return a list, even if only one channel exists
        cast=int,
        )

    options = Instrument.measurement(
        "*OPT?",
        """Get the device options installed.""",
        preprocess_reply=lambda v: v.strip('"'),
        cast=str,
        )

    output_enabled = Instrument.control(
        "OUTP?",
        "OUTP %d",
        """Control whether the RF power output of the sources is enabled (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        )
