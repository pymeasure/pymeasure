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

import logging
from time import time

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range
from pyvisa.util import from_binary_block

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Trace(Channel):
    def delete(self):
        """Delete data of the trace."""
        self.write(":TRACe:DELETE {ch}")

    mode = Channel.control(
        ":TRACe:ATTRibute:{ch}?",
        ":TRACe:ATTRibute:{ch} %s",
        """Control the mode of the trace.""",
        values=["WRITE", "FIX", "MAX", "MIN", "RAVG", "CALC"],
        cast=int,
        get_process=lambda v: ["WRITE", "FIX", "MAX", "MIN", "RAVG", "CALC"][v],
    )

    sample_number = Channel.measurement(
        ":TRACe:DATA:SNUMber? {ch}",
        """Get the number of samples.""",
        cast=int,
    )

    def get_axis_data(self, axis="Y", samples=None):
        """Get the data of an axi in m (X) or displayed units (Y).

        :param samples: Optionally tuple of the slice to retrieve, e.g. [0, 10]
        """
        if samples is None:
            area = ""
        else:
            area = f",{samples[0]+1},{samples[1]}"
        return self.values(f":TRACE:{axis}? {{ch}}{area}")


class AQ6370Series(SCPIMixin, Instrument):
    """Represents Yokogawa AQ6370 Series of optical spectrum analyzer."""

    def __init__(
        self,
        adapter,
        name="Yokogawa AQ3670D OSA",
        baud_rate=115200,
        **kwargs,
    ):
        super().__init__(
            adapter,
            name,
            asrl={
                "read_termination": "\r\n",
                "write_termination": "\r\n",
                "baud_rate": baud_rate,
            },
            gpib={"read_termination": "\n", "write_termination": "\n"},
            tcpip={
                "read_termination": "\r\n",
                "write_termination": "\r\n",
                "port": 10001,  # configurable
            },
            **kwargs,
        )

    TRA = Instrument.ChannelCreator(Trace, "TRA")
    TRB = Instrument.ChannelCreator(Trace, "TRB")
    TRC = Instrument.ChannelCreator(Trace, "TRC")
    TRD = Instrument.ChannelCreator(Trace, "TRD")
    TRE = Instrument.ChannelCreator(Trace, "TRE")
    TRF = Instrument.ChannelCreator(Trace, "TRF")
    TRG = Instrument.ChannelCreator(Trace, "TRG")

    def authenticate_ethernet(self, username, password=""):
        """Authenticate for an ethernet connection."""
        # Open the connection. It has to be closed at the end.
        assert self.ask(f'OPEN "{username}"') == "AUTHENTICATE CRAM-MD5."
        # Encrypted password transfer is possible.
        assert self.ask(password) == "READY"

    # Control sweep status -------------------------------------------------------------------------

    def trigger(self):
        """Perform a single sweep according to previous conditions."""
        self.write("*TRG")  # "Trigger"

    def abort(self):
        """Stop operations such as measurements and calibration."""
        self.write(":ABORt")

    def initiate_sweep(self):
        """Initiate a sweep."""
        self.write(":INITiate:IMMediate")

    sweep_complete = Instrument.measurement(
        ":STATus:OPERation:CONDition?",
        """Get the completion status of the sweep (bool, True if complete).""",
        get_process=lambda x: bool(int(x) & 1),
    )

    def wait_for_sweep_complete(self, should_stop=lambda: False, timeout=3600):
        """Block the program, waiting for the sweep to complete.

        :param should_stop: Function that returns True to stop waiting.
        :param timeout: Maximum waiting time, in seconds.
        :return: True when sweep completed, False if stopped by should_stop.
        :raises TimeoutError: If the sweep does not complete within the timeout period.
        """

        t0 = time()
        while not self.sweep_complete:

            if should_stop():
                return False

            if time() - t0 > timeout:
                raise TimeoutError("Timed out waiting for sweep to run.")

        return True

    # Leveling -------------------------------------------------------------------------------------

    reference_level = Instrument.control(
        ":DISPlay:TRACe:Y1:SCALe:RLEVel?",
        ":DISPlay:TRACe:Y1:SCALe:RLEVel %g",
        "Control the reference level of main scale of level axis (float in dBm).",
        validator=strict_range,
        values=[-90, 30],
    )

    level_position = Instrument.control(
        ":DISPlay:TRACe:Y1:RPOSition?",
        ":DISPlay:TRACe:Y1:RPOSition %g",
        """Control the reference level position regarding divisions
        (int, smaller than total number of divisions which is either 8, 10 or 12).""",
        validator=strict_range,
        values=[0, 12],
        dynamic=True,
        get_process=lambda x: int(x),
    )

    def set_level_position_to_max(self):
        """Set the reference level position to the maximum value."""
        self.write(":CALCulate:MARKer:MAXimum:SRLevel")

    # Sweep settings -------------------------------------------------------------------------------

    sweep_mode = Instrument.control(
        ":INITiate:SMODe?",
        ":INITiate:SMODe %s",
        "Control the sweep mode (str 'SINGLE', 'REPEAT', 'AUTO', 'SEGMENT').",
        validator=strict_discrete_set,
        map_values=True,
        values={"SINGLE": 1, "REPEAT": 2, "AUTO": 3, "SEGMENT": 4},
    )

    sweep_time_interval = Instrument.control(
        ":SENSe:SWEep:TIME:INTerval?",
        ":SENSe:SWEep:TIME:INTerval %g",
        "Control the sweep time interval (int from 0 to 99999 s).",
        validator=strict_range,
        values=[0, 99999],
    )

    automatic_sample_number = Instrument.control(
        ":SENSe:SWEep:POINts:AUTO?",
        ":SENSe:SWEep:POINts:AUTO %d",
        "Control the automatic sample number (bool).",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0, True: 1},
    )

    sample_number = Instrument.control(
        ":SENSe:SWEep:POINts?",
        ":SENSe:SWEep:POINts %d",
        "Control the sample number (int from 51 to 50001).",
        validator=strict_range,
        values=[101, 50001],
        get_process=lambda x: int(x),
    )

    sensitivity = Instrument.control(
        ":SENSe:SENSe?",
        ":SENSe:SENSe %s",
        """Control the sweep sensitivity
        (str 'NHLD', 'NAUT', 'NORM', 'MID', 'HIGH1', 'HIGH2', 'HIGH3')""",
        validator=strict_discrete_set,
        map_values=True,
        values={"NHLD": 0, "NAUT": 1, "MID": 2, "HIGH1": 3, "HIGH2": 4, "HIGH3": 5, "NORM": 6},
    )

    # Wavelength settings (all assuming wavelength mode, not frequency mode) -----------------------

    wavelength_center = Instrument.control(
        ":SENSe:WAVelength:CENTer?",
        ":SENSe:WAVelength:CENTer %g",
        "Control measurement condition center wavelength (float in m).",
        validator=strict_range,
        values=[600e-9, 1700e-9],
        dynamic=True,
    )

    wavelength_span = Instrument.control(
        ":SENSe:WAVelength:SPAN?",
        ":SENSe:WAVelength:SPAN %g",
        "Control wavelength span (float from 0 to 1100e-9 m).",
        validator=strict_range,
        values=[0, 1100e-9],
        dynamic=True,
    )

    wavelength_start = Instrument.control(
        ":SENSe:WAVelength:STARt?",
        ":SENSe:WAVelength:STARt %g",
        "Control the measurement start wavelength (float from 50e-9 to 2250e-9 in m).",
        validator=strict_range,
        values=[50e-9, 1700 - 9],
        dynamic=True,
    )

    wavelength_stop = Instrument.control(
        ":SENSe:WAVelength:STOP?",
        ":SENSe:WAVelength:STOP %g",
        "Control the measurement stop wavelength (float from 50e-9 to 2250e-9 in m).",
        validator=strict_range,
        values=[600e-9, 2250e-9],
        dynamic=True,
    )

    wavelength_automatic_center = Instrument.control(
        ":calc:mark:max:scenter:auto?",
        ":calc:mark:max:scenter:auto %s",
        """Control whether the wavelength center follows the maximum (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
    )

    resolution_bandwidth = Instrument.control(
        ":SENSe:BWIDth:RESolution?",
        ":SENSe:BWIDth:RESolution %g",
        """Control the measurement resolution
        (float in m, discrete values: [0.02e-9, 0.05e-9, 0.1e-9, 0.2e-9, 0.5e-9, 1e-9, 2e-9] m).""",
        validator=strict_discrete_set,
        values=[0.02e-9, 0.05e-9, 0.1e-9, 0.2e-9, 0.5e-9, 1e-9, 2e-9],
        dynamic=True,
    )

    # Trace operations -----------------------------------------------------------------------------

    active_trace = Instrument.control(
        ":TRACe:ACTive?",
        ":TRACe:ACTive %d",
        "Control the active trace (str 'A', 'B', 'C', ...).",
    )

    def copy_trace(self, source, destination):
        """
        Copy the data of specified trace to the another trace.

        :param source: Source trace (str 'A', 'B', 'C', ...).
        :param destination: Destination trace (str 'A', 'B', 'C', ...).
        """

        self.write(f":TRACe:COPY TR{source.replace('TR', '')},TR{destination.replace('TR', '')}")

    def delete_trace(self, trace):
        """
        Delete the specified trace.

        :param trace: Trace to be deleted (str 'ALL', 'A', 'B', 'C', ...).
        """

        if trace == "ALL":
            self.write(":TRACe:DELete:ALL")
        else:
            self.write(f":TRACe:DELete TR{trace.replace('TR', '')}")

    def get_xdata(self, trace="TRA"):
        """
        Measure the x-axis data of specified trace, output wavelength in m.

        :param trace: Trace to measure (str 'A', 'B', 'C', ...).
        :return: The x-axis data of specified trace.
        """

        return self.values(f":TRACe:X? TR{trace.replace('TR', '')}")

    def get_ydata(self, trace="TRA"):
        """
        Measure the y-axis data of specified trace, output power in dBm.

        :param trace: Trace to measure (str 'A', 'B', 'C', ...).
        :return: The y-axis data of specified trace.
        """

        return self.values(f":TRACe:Y? TR{trace.replace('TR', '')}")

    # Analysis -------------------------------------------------------------------------------------

    def execute_analysis(self):
        """Execute the analysis with the current analysis settings."""
        self.write(":CALCulate")

    def get_analysis(self):
        """
        Query the analysis results of latest analysis. If no analysis has been
        performed, returns query error.
        """
        return self.write(":CALCulate:DATA?")

    # Calculate
    calc_result = Instrument.measurement(
        ":CALCulate:DATA?",
        """Get the results of the last analysis.""",
    )

    transfer_format = Instrument.control(
        ":FORMat:DATA?",
        ":FORMat:DATA %s",
        """Control the data transfer format. It returns to default ASCII at reset.""",
        values=["ASCII", "REAL,32", "REAL,64"],
    )

    def get_binary_data(self, bitness=64):
        header = self.read_bytes(2)
        assert (
            chr(header[0]) == "#"
        ), f"header does not start with #, but with {header!r}"
        length_of_length_indicator = int(chr(header[1]))
        length = int(self.read_bytes(length_of_length_indicator).decode())
        data = self.read_bytes(length)
        return from_binary_block(
            data, datatype="d" if bitness == 64 else "f", is_big_endian=False
        )


# subclasses of specific instruments ---------------------------------------------------------------


class AQ6370E(AQ6370Series):
    """Represents Yokogawa AQ6370E optical spectrum analyzer."""

    sweep_speed = Instrument.control(
        ":SENSe:SWEep:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )

    sensitivity_level = Instrument.control(
        ":SENSe:SENSe:LEVel?",
        ":SENSe:SENSe:LEVel %g",
        """Control the sweep sensitivity by specifying the sensitivity level you want to measure at,
        in dBm. The sensitivity closest to that level, and the sweep speed are automatically
        selected.""",
    )

    pass


class AQ6370D(AQ6370Series):
    """Represents Yokogawa AQ6370D optical spectrum analyzer."""

    sweep_speed = Instrument.control(
        ":SENSe:SWEep:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )


class AQ6370C(AQ6370Series):
    """Represents Yokogawa AQ6370C optical spectrum analyzer."""

    sweep_speed = Instrument.control(
        ":SENSe:SWEep:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )


class AQ6373(AQ6370Series):
    """Represents Yokogawa AQ6373 optical spectrum analyzer."""

    wavelength_center_values = [350e-9, 1200e-9]  # 0.001 steps
    wavelength_start_values = [1e-9, 1200e-9]  # 0.001 steps
    wavelength_stop_values = [350e-9, 1625e-9]  # 0.001 steps
    wavelength_span_values = [0, 850e-9]  # 0.1 steps
    resolution_bandwidth_values = [
        0.01e-9,
        0.02e-9,
        0.05e-9,
        0.1e-9,
        0.2e-9,
        0.5e-9,
        1e-9,
        2e-9,
        5e-9,
        10e-9,
    ]


class AQ6373B(AQ6373):
    """Represents Yokogawa AQ6373B variant optical spectrum analyzer."""

    sweep_speed = Instrument.control(
        ":SENSe:SWEep:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )


class AQ6375(AQ6370Series):
    """Represents Yokogawa AQ6375 optical spectrum analyzer."""

    wavelength_center_values = [1200e-9, 2400e-9]  # 0.001 steps
    wavelength_start_values = [600e-9, 2400e-9]  # 0.001 steps
    wavelength_stop_values = [1200e-9, 3000e-9]  # 0.001 steps
    wavelength_span_values = [0, 1200e-9]  # 0.1 steps
    resolution_bandwidth_values = [
        0.05e-9,
        0.1e-9,
        0.2e-9,
        0.5e-9,
        1e-9,
        2e-9,
    ]


class AQ6375B(AQ6375):
    """Represents Yokogawa AQ6375B variant optical spectrum analyzer."""

    sweep_speed = Instrument.control(
        ":SENSe:SWEep:SPEed?",
        ":SENSe:SWEep:SPEed %d",
        "Control the sweep speed (str '1x' or '2x' for double speed).",
        validator=strict_discrete_set,
        map_values=True,
        values={"1x": 0, "2x": 1},
    )
