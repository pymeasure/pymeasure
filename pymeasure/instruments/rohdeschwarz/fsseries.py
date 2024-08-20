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
import warnings

import numpy as np
import pyvisa

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_range, strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def _number_or_auto(value):
    # helper for the bandwidth setting
    if isinstance(value, str) and value.upper() == "AUTO":
        return ":AUTO ON"
    else:
        # There is no space in the set commands, so we have to add it
        return " " + str(value)


class FSSeries(SCPIMixin, Instrument):
    """
    Represents a Rohde&Schwarz FS Series of spectrum analyzers like FSL and FSW.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    def __init__(self, adapter, name="Rohde&Schwarz FSL", **kwargs):
        super().__init__(adapter, name, **kwargs)

    # Frequency settings ---------------------------------------------------------------------------

    freq_span = Instrument.control(
        "FREQ:SPAN?",
        "FREQ:SPAN %s",
        "Frequency span in Hz.",
    )

    freq_center = Instrument.control(
        "FREQ:CENT?",
        "FREQ:CENT %s",
        "Center frequency in Hz.",
    )

    freq_start = Instrument.control(
        "FREQ:STAR?",
        "FREQ:STAR %s",
        "Start frequency in Hz.",
    )

    freq_stop = Instrument.control(
        "FREQ:STOP?",
        "FREQ:STOP %s",
        "Stop frequency in Hz.",
    )

    attenuation = Instrument.control(
        "INP:ATT?",
        "INP:ATT %s",
        "Attenuation in dB.",
    )

    res_bandwidth = Instrument.control(
        "BAND:RES?",
        # There is no space between RES and %s on purpose, see _number_or_auto.
        "BAND:RES%s",
        "Resolution bandwidth in Hz. Can be set to 'AUTO'",
        set_process=_number_or_auto,
    )

    video_bandwidth = Instrument.control(
        "BAND:VID?",
        "BAND:VID%s",
        "Video bandwidth in Hz. Can be set to 'AUTO'",
        set_process=_number_or_auto,
    )

    # Sweeping -------------------------------------------------------------------------------------

    sweep_time = Instrument.control(
        "SWE:TIME?",
        # No space between TIME and %s on purpose, see _number_or_auto.
        "SWE:TIME%s",
        "Sweep time in s. Can be set to 'AUTO'.",
        set_process=_number_or_auto,
    )

    continuous_sweep = Instrument.control(
        "INIT:CONT?",
        "INIT:CONT %s",
        "Continuous (True) or single sweep (False)",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
    )

    def single_sweep(self):
        """Perform a single sweep with synchronization."""
        self.write("INIT; *WAI")

    def continue_single_sweep(self):
        """Continue with single sweep with synchronization."""
        self.write("INIT:CONM; *WAI")

    # Helper properties ----------------------------------------------------------------------------
    # Since devices are equipped differently, we need helper to determine the nr of channels
    # which then determines whether the switching channel command is supported and how to read
    # out the traces

    @property
    def instrument_channels(self):
        try:
            response = self.ask("INST:LIST?")
            print("Raw response (in format 'CHANNEL TYPE', 'CHANNEL NAME', ...):", response)

            channels = [channel.strip().strip("'") for channel in response.split(",")]
            num_channels = len(channels) // 2

            print(
                f"Number of available channels: {num_channels}\nYou can use read_trace to "
                "read data from the active channels and use the other channel functions."
            )
        except AttributeError:
            warnings.simplefilter("always")
            warnings.warn("The instrument object does not support 'query' or 'ask'.")
            # print("The instrument object does not support 'query' or 'ask'.")
        except pyvisa.VisaIOError as e:
            if e.error_code == pyvisa.constants.StatusCode.error_timeout:
                warnings.simplefilter("always")
                warnings.warn(
                    "Timeout while waiting for 'INST:LIST?' command.\n "
                    "INST:LIST? command not supported or can't establish connection.\n "
                    "Assuming non-multi channel device. "
                    "You are likely unable to use channel functions."
                )
            else:
                raise

    # Same function but only returns the number of channels
    @property
    def get_instrument_channels(self):
        try:
            response = self.ask("INST:LIST?")
            channels = [channel.strip().strip("'") for channel in response.split(",")]
            num_channels = len(channels) // 2
            return num_channels
        except AttributeError:
            return 0
        except pyvisa.VisaIOError:
            return 0

    # Traces ---------------------------------------------------------------------------------------

    def read_trace(self, n_trace=1):
        """
        Read trace data from the active channel.

        Multi channel devices require a certain software add-on, e.g. FPL-K40 for phase noise
        measurements, that is added to a device on request. Therefore, not every device has this and
        can change between channels. Remember to "open" the desired channel with create_channel
        first if not already done to be able to activate this channel.

        :param n_trace: The trace number (1-6). Default is 1.
        :return: 2d numpy array of the trace data, [[frequency], [amplitude]].
        """
        try:
            # multi channel devices
            if self.get_instrument_channels > 1:
                trace_data = np.array(self.values(f"TRAC? TRACE{n_trace}"))
                if (
                    self.active_channel == ("PNO")
                    or self.available_channels.get(self.active_channel) == "PNOISE"
                ):
                    y = trace_data[1::2]
                    x = trace_data[0::2]

                elif (
                    self.active_channel == ("SAN")
                    or self.available_channels.get(self.active_channel) == "SANALYZER"
                ):
                    y = trace_data
                    x = np.linspace(self.freq_start, self.freq_stop, len(y))

                return np.array([x, y])

            # single channel devices
            else:
                y = np.array(self.values(f"TRAC{n_trace}? TRACE{n_trace}"))
                x = np.linspace(self.freq_start, self.freq_stop, len(y))
            return np.array([x, y])

        except pyvisa.VisaIOError as e:
            if e.error_code == pyvisa.constants.StatusCode.error_timeout:
                warnings.simplefilter("always")
                warnings.warn(
                    f"Visa Timeout Error occurred: {e} There might not be any data in the trace.",
                    RuntimeWarning,
                )
                return None
            else:
                warnings.simplefilter("always")
                warnings.warn(f"VisaIOError occurred: {e}", RuntimeWarning)
                return None
            raise

    trace_mode = Instrument.control(
        "DISP:TRAC:MODE?",
        "DISP:TRAC:MODE %s",
        "Trace mode ('WRIT', 'MAXH', 'MINH', 'AVER' or 'VIEW')",
        validator=strict_discrete_set,
        values=["WRIT", "MAXH", "MINH", "AVER", "VIEW"],
    )

    # Markers --------------------------------------------------------------------------------------

    def create_marker(self, num=1, is_delta_marker=False):
        """
        Create a marker.

        :param num: The marker number (1-4)
        :param is_delta_marker: True if the marker is a delta marker, default is False.
        :return: The marker object.
        """
        return self.Marker(self, num, is_delta_marker)

    class Marker:
        def __init__(self, instrument, num, is_delta_marker):
            """
            Marker and Delta Marker class.

            :param instrument: The FSL instrument.
            :param num: The marker number (1-4)
            :param is_delta_marker: True if the marker is a delta marker, defaults to False.
            """
            self.instrument = instrument
            self.is_delta_marker = is_delta_marker
            # Building the marker name for the commands.
            if self.is_delta_marker:
                # Smallest delta marker number is 2.
                self.name = "DELT" + str(max(2, num))
            else:
                self.name = "MARK"
                if num > 1:
                    # Marker 1 doesn't get a number.
                    self.name = self.name + str(num)

            self.activate()

        def read(self):
            return self.instrument.read()

        def write(self, command):
            self.instrument.write(f"CALC:{self.name}:{command}")

        def ask(self, command):
            return self.instrument.ask(f"CALC:{self.name}:{command}")

        def values(self, command, **kwargs):
            """
            Read a set of values from the instrument through the adapter, passing on any keyword
            arguments.
            """
            return self.instrument.values(f"CALC:{self.name}:{command}", **kwargs)

        def activate(self):
            """Activate a marker."""
            self.write("STAT ON")

        def disable(self):
            """Disable a marker."""
            self.write("STAT OFF")

        x = Instrument.control("X?", "X %s", "Position of marker on the frequency axis in Hz.")

        y = Instrument.control("Y?", "Y %s", "Amplitude of the marker position in dBm.")

        peak_excursion = Instrument.control(
            "PEXC?",
            "PEXC %s",
            "Peak excursion in dB.",
        )

        def to_trace(self, n_trace=1):
            """
            Set marker to trace.

            :param n_trace: The trace number (1-6). Default is 1.
            """
            self.write(f"TRAC {n_trace}")

        def to_peak(self):
            """Set marker to highest peak within the span."""
            self.write("MAX")

        def to_next_peak(self, direction="right"):
            """
            Set marker to next peak.

            :param direction: Direction of the next peak ('left' or 'right' of the current position)
            """
            self.write(f"MAX:{direction}")

        def zoom(self, value):
            """
            Zoom in to a frequency span or by a factor.

            :param value: The value to zoom in by. If a number is passed it is interpreted as a
            factor. If a string (number with unit) is passed it is interpreted as a frequency span.
            """
            self.write(f"FUNC:ZOOM {value}; *WAI")

    # Channels -------------------------------------------------------------------------------------
    # Please check whether your device supports these functionalities. You can use the helper
    # property available_channels to check if the device supports them.

    def create_channel(self, channel_type, channel_name):
        """Create a new channel.

        :param channel_type: Type of channel to be created.For example "PNOISE" or "SANALYZER"
        :param channel_name: Name of the channel to be added.
        """

        strict_discrete_set(channel_type, ["PNOISE", "SANALYZER"])
        self.write(f"INST:CRE:NEW {channel_type}, '{channel_name}'")

    def _channel_list_to_dict(raw):
        """
        Convert a list of available channels to a dictionary of form {channel_name: channel_type}.

        :param raw: List of channel types and channel names
        :type raw: list of string
        :return: dictionary of form {channel_name : channel_type}
        :rtype: dict
        """
        d = {
            set_keys.strip("'"): set_values.strip("'")
            for (set_values, set_keys) in zip(raw[0::2], raw[1::2])
        }

        return d

    available_channels = Instrument.measurement(
        "INST:LIST?",
        "Measure open channel names and corresponding types",
        get_process=_channel_list_to_dict,
    )

    def delete_channel(self, channel_name):
        """Deletes an active channel."""
        strict_discrete_set(channel_name, list((self.available_channels).keys()))
        self.write(f"INST:DEL '{channel_name}'")

    def select_channel(self, channel_name):
        """Select an open channel

        :param channel_name: Channel to be selected.
        """
        self.write(f"INST:SEL '{channel_name}'")

    @property
    def active_channel(self):
        """Return the name of the active channel.

        :return: active channel name
        :rtype: string
        """
        return self.values("INST?")[0]

    @active_channel.setter
    def activate_channel(self, channel):
        """Activate another open channel. Note: The channel needs to be open on the device!

        :param channel: Name of the channel to be activated
        """
        availabel_channels = [chan for chan in self.available_channels.keys()]
        channel = strict_discrete_set(channel, availabel_channels)
        self.write(f"INST '{channel}'")

    split_view = Instrument.control(
        "DISP:FORM?",
        "DISP:FORM %s",
        "Control the viewmode of the device: True for split view or False for single channel view",
        values={True: "SPL", False: "SING"},
        map_values=True,
    )

    def rename_channel(self, current_name, new_name):
        """Rename current_name of a channel to a new_name.

        :param current_name: Channel to be renamed
        :param new_name: New name of the channel
        """
        current_name = strict_discrete_set(current_name, list((self.available_channels).keys()))
        self.write(f"INST:REN '{current_name}', '{new_name}'")

    # Phase noise limit lines ----------------------------------------------------------------------

    def phase_noise_trace(self, trace):
        strict_discrete_range(trace, range(1, 7), 1)
        self.write(f"CALC:PNL:TRAC {trace}")

    def select_trace(self, trace):
        strict_discrete_range(trace, range(1, 7), 1)

        self.write(f"DISP:TRAC:SEL {trace}")

    # Overview -------------------------------------------------------------------------------------

    nominal_level = Instrument.control(
        "POW:RLEV?", "POW:RLEV %s", "Control the nominal level of the instrument"
    )


class FSL(FSSeries):
    """
    Represents a Rohde&Schwarz FSL spectrum analyzer.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    pass


class FSW(FSSeries):
    """
    Represents a Rohde&Schwarz FSW spectrum analyzer.

    All physical values that can be set can either be as a string of a value
    and a unit (e.g. "1.2 GHz") or as a float value in the base units (Hz,
    dBm, etc.).
    """

    pass
