#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
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

from time import sleep
from time import time as now

import numpy as np
from pyvisa import VisaIOError

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, truncated_range


class HP8753E(Instrument):
    """Represents the HP8753E Vector Network Analyzer
    and provides a high-level interface for taking scans of the
    scattering parameters.

    Keyword arguements:
    adapter -- <placeholder for description of pymeasure.adapter>
    name -- <str> describing the instrument
    allowable_frequency_range -- <list> defines the min and max frequency range of the instrument
    """

    def __init__(
        self,
        adapter=None,
        name=None,
        **kwargs,
    ):
        super().__init__(adapter=adapter, name=name, includeSCPI=False, **kwargs)

        self._manu = ""
        self._model = ""
        self._fw = ""
        self._sn = ""
        self._options = ""

        if name is None:
            self._manu, self._model, _, self._fw = self.id
            self._desc = "Vector Network Analyzer"
            self.name = f"{self._manu} {self._model} {self._desc}"
        else:
            self.name = name

    ALLOWED_BANDWIDTH = [10, 30, 100, 300, 1000, 3000, 3700, 6000]
    SCAN_POINT_VALUES = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
    SCATTERING_PARAMETERS = ["S11", "S12", "S21", "S22"]

    start_frequency = Instrument.control(
        "STAR?",
        "STAR %e Hz",
        f"""Control the start frequency in Hz. (float truncated from 30_000.0
        to 6_000_000_000.0).
        """,
        validator=truncated_range,
        cast=float,
        values=[30e3, 6e9],
    )

    stop_frequency = Instrument.control(
        "STOP?",
        "STOP %e Hz",
        """Control the stop frequency in Hz. (float truncated from 30_000.0
        to 6_000_000_000.0).
        """,
        validator=truncated_range,
        cast=float,
        values=[30e3, 6e9],
    )

    center_frequency = Instrument.control(
        "CENT?",
        "CENT %e Hz",
        """Control the center frequency in Hz (float truncated from 30_000.0
        to 6_000_000_000.0).
        """,
        cast=float,
        validator=truncated_range,
        values=[30e3, 6e9],
    )

    span_frequency = Instrument.control(
        "SPAN?",
        "SPAN %e Hz",
        """Control the span of the sweep frequency in Hz (float truncated from 0.0
        to 6_000_000_000.0).
        """,
        cast=float,
        validator=truncated_range,
        values=[0, 6e9],
    )

    sweep_time = Instrument.control(
        "SWET?",
        "SWET%.2e",
        """Control the sweep time in seconds. (float truncated from 0.0 to 999.0)
        """,
        validator=truncated_range,
        cast=float,
        values=[0.01, 36_400.0],
    )

    def set_sweep_time_fastest(self):
        """Set instrument scan sweep time to select fastest possible time"""
        self.write("SWEA")

    averages = Instrument.control(
        "AVERFACT?",
        "AVERFACT%d",
        """Control the number of averages for a scan sweep. (int truncated from 1 to 999).
        """,
        cast=lambda x: int(float(x)),  # need float() to convert scientific notation in strings
        validator=truncated_range,
        values=[0, 999],
    )

    averaging_enabled = Instrument.control(
        "AVERO?",
        "AVERO%d",
        """Control whether or not averaging is enabled. (boolean)""",
        cast=bool,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0, "ON": 1, "OFF": 0, "1": True, "0": False},
    )

    correction_enabled = Instrument.control(
        "CORR?",
        "CORR%d",
        """Control whether or not correction is enabled. (boolean)""",
        cast=bool,
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0, "ON": 1, "OFF": 0},
    )

    power = Instrument.control(
        "POWE?",
        "POWE%.3e",
        """Control the output RF power of the instrument's active port. (float truncated from -70.0 to 10.0 in dBm).""",
        cast=float,
        validator=truncated_range,
        values=[-70, 10],
    )

    output_enabled = Instrument.control(
        "SOUP?",
        "SOUP%s",
        """Control RF Output State (boolean)""",
        cast=bool,
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, False: 0, "ON": 1, "OFF": 0},
    )

    trigger_hold = Instrument.control(
        "HOLD?",
        "%s",
        """Control Sweep Scan Trigger State (boolean)""",
        cast=str,
        # map_values=True,
        # validator=strict_discrete_set,
        set_process=lambda x: "HOLD" if x else "CONT",
        get_process=lambda x: x == "1",
    )

    trigger_continuous = Instrument.control(
        "CONT?",
        "%s",
        """Control Sweep Scan Trigger State (boolean)""",
        cast=str,
        # map_values=True,
        # validator=strict_discrete_set,
        # values={True: "CONT", False: "HOLD"}, # , "1": True, "0": False, 1: True, 0: False},
        set_process=lambda x: "CONT" if x else "HOLD",
        get_process=lambda x: x == "1",
    )

    scan_points = Instrument.control(
        "POIN?",
        "POIN%d",
        f"""Control the number of points used for a scan sweep. From the set [{[f'"{value}"' for value in SCAN_POINT_VALUES]}]""",
        cast=lambda x: int(float(x)),
        validator=strict_discrete_set,
        values=SCAN_POINT_VALUES,
    )

    id = Instrument.measurement(
        "*IDN?",
        """Get the identification of the instrument""",
        cast=str,
    )

    sn = Instrument.measurement(
        "OUTPSERN",
        """Get the serial number for the instrument""",
    )

    options = Instrument.measurement(
        "OUTPOPTS",
        """Get the installed options for the instrument""",
    )

    @property
    def manu(self):
        """Get the manufacturer of the instrument."""
        if self._manu == "":
            self._manu, self._model, _, self._fw = self.id
        return self._manu

    @property
    def model(self):
        """Get the model of the instrument."""
        if self._model == "":
            self._manu, self._model, _, self._fw = self.id
        return self._model

    @property
    def fw(self):
        """Get the firmware of the instrument."""
        if self._fw == "":
            self._manu, self._model, _, self._fw = self.id
        return self._fw

    def set_fixed_frequency(self, frequency):
        """Set the sweep to be a fixed frequency in Hz. (float truncated from 30_000.0 to 6_000_000_000.0)"""
        self.start_frequency = frequency
        self.stop_frequency = frequency
        self.scan_points = 3

    @property
    def parameter(self):
        """Get the active Scattering Parameter being measured. (str from ['S11', 'S21', 'S12', 'S22'])"""
        for parameter in HP8753E.SCATTERING_PARAMETERS:
            if int(self.ask(f"{parameter}?")) == 1:
                return parameter
        return None

    @parameter.setter
    def parameter(self, value):
        """Set the active Scattering Parameter to be measured. (str from ['S11', 'S21', 'S12', 'S22'])"""
        if value in HP8753E.SCATTERING_PARAMETERS:
            self.write("%s" % value)
        else:
            raise Exception(
                f"Invalid value '{value}' scattering parameter requested for {self._manu} {self._model}. Valid values are: {SCATTERING_PARAMETERS}"
            )

    IFBW = Instrument.control(
        "IFBW?",
        "IFBW%d",
        f"""Control the IF Bandwidth of the instrument for a scan sweep. 
        (int from the set [{[f'"{value}"' for value in ALLOWED_BANDWIDTH]}]).""",
        cast=lambda x: int(float(x)),
        validator=strict_discrete_set,
        values=ALLOWED_BANDWIDTH,
    )

    def reset(self):
        """Reset the instrument. May cause RF Output power to be enabled!"""
        self.write("*RST")
        sleep(0.25)

    def scan(self, timeout=10):
        """Initiates a scan with the number of averages specified and
        blocks until the operation is complete.

        Args:
        timeout - a value to multiple the sweep time and averages by to timeout the function
        """

        # get time to perform sweep
        sweep_time = self.sweep_time * timeout

        # get number of averages if enabled
        if self.averaging_enabled:
            sweep_time = sweep_time * self.averages

        self.scan_single()

        # create a time limit
        start = now()

        # All queries will block until the scan is done, so use NOOP? to check.
        # These queries will time out after several seconds though,
        # so query repeatedly until the scan finishes.
        while True:
            try:
                # status = self.ask("NOOP?")
                self.ask("NOOP?")
                break
            except VisaIOError as e:
                if e.abbreviation != "VI_ERROR_TMO":
                    raise e
            # calculate time sweep should be complete by
            if now() > (start + sweep_time):
                raise TimeoutError(
                    f"VNA Scan took longer than {sweep_time} seconds to complete and timed out."
                )

    def scan_single(self):
        """Initiates a single scan or N scans averaged based on averaging
        This function is not blocking
        """
        if self.averaging_enabled:
            self.averaging_restart()
            self.write(f"NUMG{self.averages}")
        else:
            self.write("SING")

    @property
    def frequencies(self):
        """Returns a list of frequencies from the last scan.
        Does not communicate with instrument. (np.ndarray of
        frequencys sized by number of points in sweep)"""
        return np.linspace(self.start_frequency, self.stop_frequency, num=self.scan_points)

    @property
    def data_complex(self, timeout=5, points_multiplier=0.1):
        """Gets the complex s-parameter measurements from the last scan.
        This function is blocking until it is completed. (returns nparray
        sized by number of points in sweep)
        """

        # get number of points
        points = self.scan_points

        # get time to perform sweep
        sweep_time = self.sweep_time

        # Only written for ASCII data transfer
        self.write("FORM4")

        temp_data = []
        start = now()
        self.write("OUTPDATA")

        while len(temp_data) < (points):
            if self.adapter.connection.bytes_in_buffer >= 50:
                temp_data.append(self.read_bytes(50).decode("utf-8").strip("\n").split(","))
            else:
                sleep(0.001)

            # break the loop if the sweep gets interrupted or takes too long
            if now() > start + points * points_multiplier + timeout:
                raise Exception(
                    f"Failed to read data. Data transfer method timed out after {points * points_multiplier + timeout} seconds"
                )

        # process string data into complex numbers
        preformat_data = [float(point[0]) + float(point[1]) * 1j for point in temp_data]
        data = np.array(preformat_data)

        return data

    def shutdown(self):
        """Shutdown - Disables RF Output."""
        self.output_enabled = False

    def averaging_restart(self):
        """Restart sweep averaging."""
        self.write("AVERREST")

    def emit_beep(self):
        self.write("EMIB")
