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
import re
import time
import weakref
from collections import Counter, OrderedDict, namedtuple
from enum import IntEnum

import numpy as np
import pandas as pd

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.channel import Channel
from pymeasure.instruments.validators import (
    strict_discrete_range,
    strict_discrete_set,
    strict_range,
)

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

######################################
# Agilent B1500 Mainframe
######################################


class AgilentB1500(SCPIMixin, Instrument):
    """Represent the Agilent B1500 Semiconductor Parameter Analyzer
    and provide a high-level interface for taking different kinds of
    measurements.
    """

    def __init__(self, adapter, name="Agilent B1500 Semiconductor Parameter Analyzer", **kwargs):
        super().__init__(adapter, name, read_termination="\r\n", write_termination="\r\n", **kwargs)
        self._smu_names = {}
        self._smu_references = {}

    @property
    def smu_references(self):
        """Get all SMU instances as dict_values."""
        return self._smu_references.values()

    @property
    def smu_names(self):
        """Get all SMU names as dict."""
        return self._smu_names

    def query_learn(self, query_type):
        """Query settings from the instrument. (``*LRN?``)
        Return dict of settings.

        :param int or str query_type: Query type (number according to manual)
        :rtype: dict
        """
        return QueryLearn.query_learn(self.ask, query_type)

    def query_learn_header(self, query_type, **kwargs):
        """Query settings from the instrument. (``*LRN?``)

        Return dict of settings in human-readable format for debugging
        or file headers.
        For optional arguments check the underlying definition of
        :meth:`QueryLearn.query_learn_header`.

        :param int or str query_type: Query type (number according to manual)
        :rtype: dict
        """
        return QueryLearn.query_learn_header(self.ask, query_type, self._smu_references, **kwargs)

    def query_modules(self):
        """Query module models from the instrument.

        Return dictionary of channel and module type.

        :return: Channel:Module Type
        :rtype: dict
        """
        modules = self.ask("UNT?")
        modules = modules.split(";")
        module_names = {
            "B1525A": "SPGU",
            "B1517A": "HRSMU",
            "B1511A": "MPSMU",
            "B1511B": "MPSMU",
            "B1510A": "HPSMU",
            "B1514A": "MCSMU",
            "B1520A": "MFCMU",
            "B1530A": "WGFMU",
            "B1520A/N1301A": "MFCMU",
        }
        out = {}
        for i, module in enumerate(modules):
            module = module.split(",")
            if not module[0] == "0":
                try:
                    out[i + 1] = module_names[module[0]]
                    # i+1: channels start at 1 not at 0
                except Exception:
                    raise NotImplementedError(f"Module {module[0]} is not implemented yet!")
        return out

    def initialize_smu(self, channel, smu_type, name):
        """Initialize a :class:`SMU` instance.

        :param int channel: SMU channel
        :param str smu_type: SMU type, e.g. ``'HRSMU'``
        :param str name: SMU name for pymeasure (data output etc.)
        :return: SMU instance
        :rtype: :class:`.SMU`
        """
        if channel in (list(range(101, 1101, 100)) + list(range(102, 1102, 100))):
            channel = int(str(channel)[0:-2])
            # subchannels not relevant for SMU/CMU
        channel = strict_discrete_set(channel, range(1, 11))
        self._smu_names[channel] = name
        smu_reference = SMU(self, channel, smu_type, name)
        self._smu_references[channel] = smu_reference
        return smu_reference

    def initialize_all_smus(self):
        """Initialize all SMUs.

        Query available modules and create a :class:`.SMU` instance for each.
        SMUs are accessible via attributes such as ``.smu1``, etc.
        """
        modules = self.query_modules()
        i = 1
        for channel, smu_type in modules.items():
            if "SMU" in smu_type:
                setattr(
                    self, "smu" + str(i), self.initialize_smu(channel, smu_type, "SMU" + str(i))
                )
                i += 1

    def initialize_all_spgus(self):
        """Initialize all SPGUs.

        Query available modules and create a :class:`.SPGU` instance for each.
        SPGUs are accessible via attributes such as ``.spgu1``, etc.
        """
        modules = self.query_modules()
        for channel, module_type in modules.items():
            if module_type == "SPGU":
                self.add_child(SPGU, channel, collection="spgus", prefix="spgu")

    def pause(self, pause_seconds):
        """Pause command execution for given time in seconds. (``PA``)

        :param int pause_seconds: Seconds to pause
        """
        self.write(f"PA {pause_seconds}")

    def abort(self):
        """Abort the present operation but channels may still output current/voltage. (``AB``)"""
        self.write("AB")

    def force_gnd(self):
        """Force 0 V on all channels immediately. Current settings can
        be restored with :meth:`restore_settings`. (``DZ``)
        """
        self.write("DZ")

    def restore_settings(self):
        """Restore the settings of all channels to the state before
        using :meth:`force_gnd`. (``RZ``)
        """
        self.write("RZ")

    io_control_mode = Instrument.control(
        "ERMOD?",
        "ERMOD %s",
        "Control the control mode for the digital I/O ports (:class:`ControlMode`). (``ERMOD``)",
        get_process=lambda v: ControlMode(v),
        set_process=lambda v: ControlMode(v).value,
    )

    def set_port_connection(self, port, status):
        """Set the connection status for a specific port. (``ERSSP``)

        :param PgSelectorPort port: Port number
        :param PgSelectorConnectionStatus status: Connection status
        """
        self.write(f"ERSSP {port.value}, {status.value}")

    def check_errors(self):
        """Check for errors. (``ERRX?``)"""
        error = self.ask("ERRX?")
        error = re.match(
            r'(?P<errorcode>[+-]?\d+(?:\.\d+)?),"(?P<errortext>[\w\s.]+)', error
        ).groups()
        if int(error[0]) == 0:
            return
        else:
            raise OSError(f"Agilent B1500 Error {error[0]}: {error[1]}")

    def check_idle(self):
        """Check if instrument is idle. (``*OPC?``)

        Alias for :meth:`~.SCPIMixin.complete`.
        """
        return self.complete

    def clear_buffer(self):
        """Clear output data buffer. (``BC``)"""
        self.write("BC")

    def clear_timer(self):
        """Clear timer count. (``TSR``)"""
        self.write("TSR")

    def send_trigger(self):
        """Send trigger to start measurement (except High Speed Spot). (``XE``)"""
        self.write("XE")

    @property
    def auto_calibration(self):
        """Control SMU auto-calibration every 30 minutes (bool). (``CM``)"""
        response = self.query_learn(31)["CM"]
        response = bool(int(response))
        return response

    @auto_calibration.setter
    def auto_calibration(self, setting):
        setting = int(setting)
        self.write(f"CM {setting}")
        self.check_errors()

    ######################################
    # Data Formatting
    ######################################

    class _data_formatting_generic:
        """Format data output head of measurement value into user-readable values.

        :param str output_format_str: Format string of measurement value
        :param dict smu_names: Dictionary of channel and SMU name
        """

        channels = {
            "A": 101,
            "B": 201,
            "C": 301,
            "D": 401,
            "E": 501,
            "F": 601,
            "G": 701,
            "H": 801,
            "I": 901,
            "J": 1001,
            "a": 102,
            "b": 202,
            "c": 302,
            "d": 402,
            "e": 502,
            "f": 602,
            "g": 702,
            "h": 802,
            "i": 902,
            "j": 1002,
            "V": "GNDU",
            "Z": "MISC",
        }
        status = {
            "W": "First or intermediate sweep step data",
            "E": "Last sweep step data",
            "T": "Another channel reached its compliance setting.",
            "C": "This channel reached its compliance setting",
            "V": (
                "Measurement data is over the measurement range/Sweep was "
                "aborted by automatic stop function or power compliance. "
                "D will be 199.999E+99 (no meaning)."
            ),
            "X": (
                "One or more channels are oscillating. Or source output did "
                "not settle before measurement."
            ),
            "F": "SMU is in the force saturation condition.",
            "G": (
                "Linear/Binary search measurement: Target value was not "
                "found within the search range. "
                "Returns source output value. "
                "Quasi-pulsed spot measurement: "
                "The detection time was over the limit."
            ),
            "S": (
                "Linear/Binary search measurement: The search measurement "
                "was stopped. Returns source output value. "
                "Quasi-pulsed spot measurement: Output slew rate was too "
                "slow to perform the settling detection. "
                "Or quasi-pulsed source channel reached compliance before "
                "the source output voltage changed 10 V "
                "from the start voltage."
            ),
            "U": "CMU is in the NULL loop unbalance condition.",
            "D": "CMU is in the IV amplifier saturation condition.",
        }
        smu_status = {
            1: "A/D converter overflowed.",
            2: "Oscillation of force or saturation current.",
            4: "Another unit reached its compliance setting.",
            8: "This unit reached its compliance setting.",
            16: "Target value was not found within the search range.",
            32: "Search measurement was automatically stopped.",
            64: "Invalid data is returned. D is not used.",
            128: "End of data",
        }
        cmu_status = {
            1: "A/D converter overflowed.",
            2: "CMU is in the NULL loop unbalance condition.",
            4: "CMU is in the IV amplifier saturation condition.",
            64: "Invalid data is returned. D is not used.",
            128: "End of data",
        }
        data_names_int = {"Sampling index"}  # convert to int instead of float

        def __init__(self, smu_names, output_format_str):
            """Store parameters of the chosen output format for later usage in data processing.

            Data Names: e.g. "Voltage (V)" or "Current Measurement (A)"
            """
            sizes = {"FMT1": 16, "FMT11": 17, "FMT21": 19}
            try:
                self.size = sizes[output_format_str]
            except Exception:
                raise NotImplementedError(
                    f"Data Format {output_format_str} is not implemented so far."
                )
            self.format = output_format_str
            data_names_C = {
                "V": "Voltage (V)",
                "I": "Current (A)",
                "F": "Frequency (Hz)",
            }
            data_names_CG = {
                "Z": "Impedance (Ohm)",
                "Y": "Admittance (S)",
                "C": "Capacitance (F)",
                "L": "Inductance (H)",
                "R": "Phase (rad)",
                "P": "Phase (deg)",
                "D": "Dissipation factor",
                "Q": "Quality factor",
                "X": "Sampling index",
                "T": "Time (s)",
            }
            data_names_G = {
                "V": "Voltage Measurement (V)",
                "I": "Current Measurement (A)",
                "v": "Voltage Output (V)",
                "i": "Current Output (A)",
                "f": "Frequency (Hz)",
                "z": "invalid data",
            }
            if output_format_str in ["FMT1", "FMT5", "FMT11", "FMT15"]:
                self.data_names = {**data_names_C, **data_names_CG}
            elif output_format_str in ["FMT21", "FMT25"]:
                self.data_names = {**data_names_G, **data_names_CG}
            else:
                self.data_names = {}  # no header
            self.smu_names = smu_names

        def check_status(self, status_string, name=None, cmu=False):
            """Check returned status of instrument.

            If not null or end of data, message is written to log.info.

            :param str status_string: Status string returned by the instrument when reading data.
            :param str name: Name of the SMU channel, defaults to None
            :param bool cmu: Whether or not channel is CMU, defaults to False (SMU)
            """

            def log_failed():
                log.info("Agilent B1500: check_status not possible for status %s", status_string)

            if name is None:
                name = ""
            else:
                name = f" {name}"

            status = re.search(r"(?P<number>[0-9]*)(?P<letter>[ A-Z]*)", status_string)
            # depending on FMT, status may be a letter or up to 3 digits
            if len(status.group("number")) > 0:
                status = int(status.group("number"))
                if status in (0, 128):
                    # 0: no error; 128: End of data
                    return
                if cmu is True:
                    status_dict = self.cmu_status
                else:
                    status_dict = self.smu_status
                for index, digit in enumerate(bin(status)[2:]):
                    # [2:] to chop off 0b
                    if digit == "1":
                        log.info("Agilent B1500%s: %s", name, status_dict[2**index])
            elif len(status.group("letter")) > 0:
                status = status.group("letter")
                status = status.strip()  # remove whitespaces
                if status not in ["N", "W", "E"]:
                    try:
                        status = self.status[status]
                        log.info("Agilent B1500%s: %s", name, status)
                    except KeyError:
                        log_failed()
            else:
                log_failed()

        def format_channel_check_status(self, status_string, channel_string):
            """Return channel number for given channel letter.

            Check for not null status of the channel and write according
            message to log.info.

            :param str status_string: Status string returned by the instrument when reading data.
            :param str channel_string: Channel string returned by the instrument
            :return: Channel name
            :rtype: str
            """
            channel = self.channels[channel_string]
            if isinstance(channel, int):
                channel = int(str(channel)[0:-2])
                # subchannels not relevant for SMU/CMU
            try:
                smu_name = self.smu_names[channel]
                if "SMU" in smu_name:
                    self.check_status(status_string, name=smu_name, cmu=False)
                if "CMU" in smu_name:
                    self.check_status(status_string, name=smu_name, cmu=True)
                return smu_name
            except KeyError:
                self.check_status(status_string)
                return channel

    class _data_formatting_FMT1(_data_formatting_generic):
        """Data formatting for FMT1 format"""

        def __init__(self, smu_names={}, output_format_string="FMT1"):
            super().__init__(smu_names, output_format_string)

        def format_single(self, element):
            """Format single measurement value.

            :param str element: Single measurement value read from the instrument
            :return: Status, channel, data name, value
            :rtype: (str, str, str, float)
            """
            status = element[0]  # one character
            channel = element[1]
            data_name = element[2]
            data_name = self.data_names[data_name]
            if data_name in self.data_names_int:
                value = int(float(element[3:]))
            else:
                value = float(element[3:])
            channel = self.format_channel_check_status(status, channel)

            return (status, channel, data_name, value)

    class _data_formatting_FMT11(_data_formatting_FMT1):
        """Data formatting for FMT11 format (based on FMT1)"""

        def __init__(self, smu_names={}):
            super().__init__(smu_names, "FMT11")

    class _data_formatting_FMT21(_data_formatting_generic):
        """Data formatting for FMT21 format"""

        def __init__(self, smu_names={}):
            super().__init__(smu_names, "FMT21")

        def format_single(self, element):
            """Format single measurement value.

            :param str element: Single measurement value read from the instrument
            :return: Status (three digits), channel, data name, value
            :rtype: (str, str, str, float)
            """
            status = element[0:3]  # three digits
            channel = element[3]
            data_name = element[4]
            data_name = self.data_names[data_name]
            if data_name in self.data_names_int:
                value = int(float(element[5:]))
            else:
                value = float(element[5:])
            channel = self.format_channel_check_status(status, channel)

            return (status, channel, data_name, value)

    def _data_formatting(self, output_format_str, smu_names={}):
        """Return data formatting class for given data format string.

        :param str output_format_str: Data output format, e.g. ``FMT21``
        :param dict smu_names: Dictionary of channels and SMU names, defaults to {}
        :return: Corresponding formatting class
        :rtype: class
        """
        classes = {
            "FMT1": self._data_formatting_FMT1,
            "FMT11": self._data_formatting_FMT11,
            "FMT21": self._data_formatting_FMT21,
        }
        try:
            format_class = classes[output_format_str]
        except KeyError:
            log.error(
                "Data Format %s is not implemented so far. Please set appropriate Data Format.",
                output_format_str,
            )
            return
        else:
            return format_class(smu_names=smu_names)

    def data_format(self, output_format, mode=0):
        """Specify data output format. Check documentation for parameters. (``FMT``)

        Should be called once per session to set the data format for
        interpreting the measurement values read from the instrument.

        Currently implemented are format 1, 11, and 21.

        :param str output_format: Output format string, e.g. ``FMT21``
        :param int mode: Data output mode, defaults to 0 (only measurement data is returned)
        """
        # restrict to implemented formats
        output_format = strict_discrete_set(output_format, [1, 11, 21])
        # possible: [1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 21, 22, 25]
        mode = strict_range(mode, range(0, 11))
        self.write(f"FMT {output_format}, {mode}")
        self.check_errors()
        if self._smu_names == {}:
            print(
                "No SMU names available for formatting, "
                "instead channel numbers will be used. "
                "Call data_format after initializing all SMUs."
            )
            log.info(
                "No SMU names available for formatting, "
                "instead channel numbers will be used. "
                "Call data_format after initializing all SMUs."
            )
        self._data_format = self._data_formatting(f"FMT{output_format}", self._smu_names)

    ######################################
    # Measurement Settings
    ######################################

    @property
    def parallel_meas(self):
        """Control whether parallel measurements are enabled (bool). (``PAD``)

        Effective for SMUs using HSADC and measurement modes 1, 2, 10, 18.

        :type: bool
        """
        response = self.query_learn(110)["PAD"]
        response = bool(int(response))
        return response

    @parallel_meas.setter
    def parallel_meas(self, setting):
        setting = int(setting)
        self.write(f"PAD {setting}")
        self.check_errors()

    def query_meas_settings(self):
        """Read settings for ``TM``, ``AV``, ``CM``, ``FMT`` and ``MM``
        commands (31) from the instrument.
        """
        return self.query_learn_header(31)

    def query_meas_mode(self):
        """Read settings for ``MM`` command (part of 31) from the instrument."""
        return self.query_learn_header(31, single_command="MM")

    def meas_mode(self, mode, *args):
        """Set measurement mode of channels. (``MM``)

        Measurements will be taken in the same order as the SMU references are passed.

        :param MeasMode mode: Measurement mode

            * Spot
            * Staircase Sweep
            * Sampling

        :param SMU args: SMU references
        """
        mode = MeasMode.get(mode)
        cmd = f"MM {mode.value}"
        for smu in args:
            if isinstance(smu, SMU):
                cmd += f", {smu.channel}"
        self.write(cmd)
        self.check_errors()

    # ADC Setup: AAD, AIT, AV, AZ

    def query_adc_setup(self):
        """Read ADC settings (55, 56) from the instrument."""
        return {**self.query_learn_header(55), **self.query_learn_header(56)}

    def adc_setup(self, adc_type, mode, N=""):
        """Set up operation mode and parameters of ADC for each ADC type.
        (``AIT``)

        Defaults:

            - HSADC: Auto N=1, Manual N=1, PLC N=1, Time N=0.000002(s)
            - HRADC: Auto N=6, Manual N=3, PLC N=1

        :param ADCType adc_type: ADC type
        :param ADCMode mode: ADC mode
        :param str N: additional parameter, check documentation, defaults to ``''``
        """

        adc_type = ADCType.get(adc_type)
        mode = ADCMode.get(mode)
        if (adc_type == ADCType["HRADC"]) and (mode == ADCMode["TIME"]):
            raise ValueError("Time ADC mode is not available for HRADC")
        command = f"AIT {adc_type.value}, {mode.value}"
        if not N == "":
            if mode == ADCMode["TIME"]:
                command += f", {N}"
            else:
                command += f", {N}"
        self.write(command)
        self.check_errors()

    def adc_averaging(self, number, mode="Auto"):
        """Set number of averaging samples of the HSADC. (``AV``)

        Defaults: N=1, Auto

        :param int number: Number of averages
        :param AutoManual mode: Mode (``'Auto','Manual'``), defaults to 'Auto'
        """
        if number > 0:
            number = strict_range(number, range(1, 1024))
            mode = AutoManual.get(mode).value
            self.write(f"AV {number}, {mode}")
        else:
            number = strict_range(number, range(-1, -101, -1))
            self.write(f"AV {number}")
        self.check_errors()

    @property
    def adc_auto_zero(self):
        """Control ADC zero function (bool). (``AZ``)

        Halves the integration time when disabled.
        """
        response = self.query_learn(56)["AZ"]
        response = bool(int(response))
        return response

    @adc_auto_zero.setter
    def adc_auto_zero(self, setting):
        setting = int(setting)
        self.write(f"AZ {setting}")
        self.check_errors()

    @property
    def time_stamp(self):
        """Control Time Stamp function (bool). (``TSC``)"""
        response = self.query_learn(60)["TSC"]
        response = bool(int(response))
        return response

    @time_stamp.setter
    def time_stamp(self, setting):
        setting = int(setting)
        self.write(f"TSC {setting}")
        self.check_errors()

    def query_time_stamp_setting(self):
        """Read time stamp settings (60) from the instrument."""
        return self.query_learn_header(60)

    def wait_time(self, wait_type, N, offset=0):
        """Configure wait time. (``WAT``)

        :param WaitTimeType wait_type: Wait time type
        :param float N: Coefficient for initial wait time, default: 1
        :param int offset: Offset for wait time, defaults to 0
        """
        wait_type = WaitTimeType.get(wait_type).value
        self.write(f"WAT {wait_type}, {N}, {offset}")
        self.check_errors()

    ######################################
    # Sweep Setup
    ######################################

    def query_staircase_sweep_settings(self):
        """Read Staircase Sweep Measurement settings (33) from the instrument."""
        return self.query_learn_header(33)

    def sweep_timing(
        self, hold, delay, step_delay=0, step_trigger_delay=0, measurement_trigger_delay=0
    ):
        """Set timing parameters for staircase or multi channel sweep. (``WT``)

        :param float hold: Hold time
        :param float delay: Delay time
        :param float step_delay: Step delay time, defaults to 0
        :param float step_trigger_delay: Trigger delay time, defaults to 0
        :param float measurement_trigger_delay: Measurement trigger delay time,
                                                          defaults to 0
        """
        hold = strict_discrete_range(hold, (0, 655.35), 0.01)
        delay = strict_discrete_range(delay, (0, 65.535), 0.0001)
        step_delay = strict_discrete_range(step_delay, (0, 1), 0.0001)
        step_trigger_delay = strict_discrete_range(step_trigger_delay, (0, delay), 0.0001)
        measurement_trigger_delay = strict_discrete_range(
            measurement_trigger_delay, (0, 65.535), 0.0001
        )
        self.write(
            "WT %g, %g, %g, %g, %g"
            % (hold, delay, step_delay, step_trigger_delay, measurement_trigger_delay)
        )
        self.check_errors()

    def sweep_auto_abort(self, abort, post="START"):
        """Enable/Disable the automatic abort function. (``WM``)

        Also set the post measurement condition.

        :param bool abort: Enable/Disable automatic abort
        :param StaircaseSweepPostOutput post:
            Output after measurement, defaults to 'Start'
        """
        abort_values = {True: 2, False: 1}
        abort = strict_discrete_set(abort, abort_values)
        abort = abort_values[abort]
        post = StaircaseSweepPostOutput.get(post)
        self.write(f"WM {abort}, {post.value}")
        self.check_errors()

    ######################################
    # Sampling Setup
    ######################################

    def query_sampling_settings(self):
        """Read sampling measurement settings (47) from the instrument."""
        return self.query_learn_header(47)

    @property
    def sampling_mode(self):
        """Control sampling mode, linear or logarithmic. (``ML``)

        :type: :class:`.SamplingMode`
        """
        response = self.query_learn(47)
        response = response["ML"]
        return SamplingMode(response)

    @sampling_mode.setter
    def sampling_mode(self, mode):
        mode = SamplingMode.get(mode).value
        self.write(f"ML {mode}")
        self.check_errors()

    def sampling_timing(self, hold_bias, interval, number, hold_base=0):
        """Set timing parameters for the sampling measurement. (``MT``)

        :param float hold_bias: Bias hold time
        :param float interval: Sampling interval
        :param int number: Number of Samples
        :param float hold_base: Base hold time, defaults to 0
        """
        n_channels = self.query_meas_settings()["Measurement Channels"]
        n_channels = len(n_channels.split(", "))
        if interval >= 0.002:
            hold_bias = strict_discrete_range(hold_bias, (0, 655.35), 0.01)
            interval = strict_discrete_range(interval, (0, 65.535), 0.001)
        else:
            try:
                hold_bias = strict_discrete_range(hold_bias, (-0.09, -0.0001), 0.0001)
            except ValueError as error1:
                try:
                    hold_bias = strict_discrete_range(hold_bias, (0, 655.35), 0.01)
                except ValueError as error2:
                    raise ValueError(
                        "Bias hold time does not match either "
                        + "of the two possible specifications: "
                        + f"{error1} {error2}"
                    )
            if interval >= 0.0001 + 0.00002 * (n_channels - 1):
                interval = strict_discrete_range(interval, (0, 0.00199), 0.00001)
            else:
                raise ValueError(f"Sampling interval {interval} is too short.")
        number = strict_discrete_range(number, (0, int(100001 / n_channels)), 1)
        # ToDo: different restrictions apply for logarithmic sampling!
        hold_base = strict_discrete_range(hold_base, (0, 655.35), 0.01)

        self.write(f"MT {hold_bias}, {interval}, {number}, {hold_base}")
        self.check_errors()

    def sampling_auto_abort(self, abort, post="Bias"):
        """Enable/Disable the automatic abort function. (``MSC``)

        Also set the post measurement condition.

        :param bool abort: Enable/Disable automatic abort
        :param SamplingPostOutput post: Output after measurement, defaults to 'Bias'
        """
        abort_values = {True: 2, False: 1}
        abort = strict_discrete_set(abort, abort_values)
        abort = abort_values[abort]
        post = SamplingPostOutput.get(post).value
        self.write(f"MSC {abort}, {post}")
        self.check_errors()

    ######################################
    # Read out of data
    ######################################

    def read_data(self, number_of_points):
        """Read all data from buffer and return Pandas DataFrame.

        Specify number of measurement points for correct splitting of the data list.

        :param int number_of_points: Number of measurement points
        :return: Measurement Data
        :rtype: pd.DataFrame
        """
        data = self.read()
        data = data.split(",")
        data = np.array(data)
        data = np.split(data, number_of_points)
        data = pd.DataFrame(data=data)
        data = data.applymap(self._data_format.format_single)
        heads = data.iloc[[0]].applymap(lambda x: " ".join(x[1:3]))
        # channel & data_type
        heads = heads.to_numpy().tolist()  # 2D List
        heads = heads[0]  # first row
        data = data.applymap(lambda x: x[3])
        data.columns = heads
        return data

    def read_channels(self, nchannels):
        """Read data for 1 measurement point from the buffer for the specified number of channels.

        :param int nchannels: Number of channels which return data (includes measurement
            channels and sweep sources, depending on data output settings)
        :return: Measurement data
        :rtype: tuple
        """
        data = self.read_bytes(self._data_format.size * nchannels)
        data = data.decode("ASCII")
        data = data.rstrip("\r,")
        # ',' if more data in buffer, '\r' if last data point
        data = data.split(",")
        data = map(self._data_format.format_single, data)
        data = tuple(data)
        return data

    ######################################
    # Queries on all SMUs
    ######################################

    def query_series_resistor(self):
        """Read series resistor status (53) for all SMUs."""
        return self.query_learn_header(53)

    def query_meas_range_current_auto(self):
        """Read auto ranging mode status (54) for all SMUs."""
        return self.query_learn_header(54)

    def query_meas_op_mode(self):
        """Read SMU measurement operation mode (46) for all SMUs."""
        return self.query_learn_header(46)

    def query_meas_ranges(self):
        """Read measruement ranging status (32) for all SMUs."""
        return self.query_learn_header(32)


######################################
# SMU Setup
######################################


class SMU:
    """Provide specific methods for the SMUs of the Agilent B1500 mainframe.

    :param AgilentB1500 parent: Instance of the B1500 mainframe class
    :param int channel: Channel number of the SMU
    :param str smu_type: Type of the SMU
    :param str name: Name of the SMU
    """

    def __init__(self, parent, channel, smu_type, name, **kwargs):
        # to allow garbage collection for cyclic references
        self._b1500 = weakref.proxy(parent)
        channel = strict_discrete_set(channel, range(1, 11))
        self.channel = channel
        smu_type = strict_discrete_set(
            smu_type,
            [
                "HRSMU",
                "MPSMU",
                "HPSMU",
                "MCSMU",
                "HCSMU",
                "DHCSMU",
                "HVSMU",
                "UHCU",
                "HVMCU",
                "UHVU",
            ],
        )
        self.voltage_ranging = SMUVoltageRanging(smu_type)
        self.current_ranging = SMUCurrentRanging(smu_type)
        self.name = name

    ##########################################
    # Wrappers of B1500 communication methods
    ##########################################
    def write(self, string):
        """Wrap :meth:`.Instrument.write` method of B1500."""
        self._b1500.write(string)

    def ask(self, string):
        """Wrap :meth:`~.Instrument.ask` method of B1500."""
        return self._b1500.ask(string)

    def query_learn(self, query_type, command):
        """Wrap :meth:`~.AgilentB1500.query_learn` method of B1500."""
        response = self._b1500.query_learn(query_type)
        # query_learn returns settings of all smus
        # pick setting for this smu only
        response = response[command + str(self.channel)]
        return response

    def check_errors(self):
        """Wrap :meth:`~.AgilentB1500.check_errors` method of B1500."""
        return self._b1500.check_errors()

    ##########################################

    def _query_status_raw(self):
        return self._b1500.query_learn(str(self.channel))

    @property
    def status(self):
        """Get status of the SMU."""
        return self._b1500.query_learn_header(str(self.channel))

    def enable(self):
        """Enable source/measurement channel. (``CN``)"""
        self.write(f"CN {self.channel}")

    def disable(self):
        """Disable source/measurement channel. (``CL``)"""
        self.write(f"CL {self.channel}")

    def force_gnd(self):
        """Force output to 0 V immediately. (``DZ``)

        Current settings can be restored with :meth:`restore_settings`.
        """
        self.write(f"DZ {self.channel}")

    def restore_settings(self):
        """Restore the settings of the channel to the state before
        using :meth:`force_gnd`. (``RZ``)
        """
        self.write(f"RZ {self.channel}")

    @property
    def filter(self):
        """Control SMU filter enable/disable state (bool). (``FL``)"""
        # different than other SMU specific settings (grouped by setting)
        # read via raw command
        response = self._b1500.query_learn(30)
        if "FL" in response.keys():
            # only present if filters of all channels are off
            return False
        else:
            if str(self.channel) in response["FL0"]:
                return False
            elif str(self.channel) in response["FL1"]:
                return True
            else:
                raise NotImplementedError("Filter Value cannot be read!")

    @filter.setter
    def filter(self, setting):
        setting = strict_discrete_set(int(setting), (0, 1))
        self.write(f"FL {setting}, {self.channel}")
        self.check_errors()

    @property
    def series_resistor(self):
        """Control 1 MOhm series resistor enable/disable state (bool). (``SSR``)"""
        response = self.query_learn(53, "SSR")
        response = bool(int(response))
        return response

    @series_resistor.setter
    def series_resistor(self, setting):
        setting = strict_discrete_set(int(setting), (0, 1))
        self.write(f"SSR {self.channel}, {setting}")
        self.check_errors()

    @property
    def meas_op_mode(self):
        """Control SMU measurement operation mode. (``CMM``)

        :type: :class:`.MeasOpMode`
        """
        response = self.query_learn(46, "CMM")
        response = int(response)
        return MeasOpMode(response)

    @meas_op_mode.setter
    def meas_op_mode(self, op_mode):
        op_mode = MeasOpMode.get(op_mode)
        self.write(f"CMM {self.channel}, {op_mode.value}")
        self.check_errors()

    @property
    def adc_type(self):
        """Control ADC type of individual measurement channel. (``AAD``)

        :type: :class:`.ADCType`
        """
        response = self.query_learn(55, "AAD")
        response = int(response)
        return ADCType(response)

    @adc_type.setter
    def adc_type(self, adc_type):
        adc_type = ADCType.get(adc_type)
        self.write(f"AAD {self.channel}, {adc_type.value}")
        self.check_errors()

    ######################################
    # Force Constant Output
    ######################################
    def force(self, source_type, source_range, output, comp="", comp_polarity="", comp_range=""):
        """Apply DC current or voltage from SMU immediately. (``DI``, ``DV``)

        :param str source_type: Source type (``'Voltage','Current'``)
        :param int or str source_range: Output range index or name
        :param float output: Source output value in A or V
        :param float comp: Compliance value, defaults to previous setting
        :param CompliancePolarity comp_polarity: Compliance polairty, defaults to auto
        :param int or str comp_range: Compliance ranging type, defaults to auto
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "DV"
            source_range = self.voltage_ranging.output(source_range).index
            if not comp_range == "":
                comp_range = self.current_ranging.meas(comp_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "DI"
            source_range = self.current_ranging.output(source_range).index
            if not comp_range == "":
                comp_range = self.voltage_ranging.meas(comp_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        cmd += f" {self.channel}, {source_range}, {output}"
        if not comp == "":
            cmd += f", {comp}"
            if not comp_polarity == "":
                comp_polarity = CompliancePolarity.get(comp_polarity).value
                cmd += f", {comp_polarity}"
                if not comp_range == "":
                    cmd += f", {comp_range}"
        self.write(cmd)
        self.check_errors()

    def ramp_source(
        self,
        source_type,
        source_range,
        target_output,
        comp="",
        comp_polarity="",
        comp_range="",
        stepsize=0.001,
        pause=20e-3,
    ):
        """Ramp to a target output from the set value with a given step size.

        Each step is separated by a pause duration.

        :param str source_type: Source type (``'Voltage'`` or ``'Current'``)
        :param float target_output: Target output voltage or current
        :param int irange: Output range index
        :param float comp: Compliance, defaults to previous setting
        :param CompliancePolarity comp_polarity: Compliance polairty, defaults to auto
        :param int or str comp_range: Compliance ranging type, defaults to auto
        :param float stepsize: Maximum size of steps
        :param float pause: Duration in seconds to wait between steps
        """
        if source_type.upper() == "VOLTAGE":
            source_type = "VOLTAGE"
            cmd = f"DV{self.channel}"
            source_range = self.voltage_ranging.output(source_range).index
            unit = "V"
            if not comp_range == "":
                comp_range = self.current_ranging.meas(comp_range).index
        elif source_type.upper() == "CURRENT":
            source_type = "CURRENT"
            cmd = f"DI{self.channel}"
            source_range = self.current_ranging.output(source_range).index
            unit = "A"
            if not comp_range == "":
                comp_range = self.voltage_ranging.meas(comp_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")

        status = self._query_status_raw()
        if "CL" in status:  # SMU is OFF
            start = 0
        elif cmd in status:
            start = float(status[cmd][1])  # current output value
        else:
            log.info("%s in different state. Changing to %s Source.", self.name, source_type)
            start = 0

        # calculate number of points based on maximum stepsize
        nop = np.ceil(abs((target_output - start) / stepsize))
        nop = int(nop)
        log.info(
            "%s ramping from %g%s to %g%s in %d steps",
            self.name,
            start,
            unit,
            target_output,
            unit,
            nop,
        )
        outputs = np.linspace(start, target_output, nop, endpoint=False)

        for output in outputs:
            # loop is only executed if target_output != start
            self.force(source_type, source_range, output, comp, comp_polarity, comp_range)
            time.sleep(pause)
        # call force even if start==target_output
        # to set compliance
        self.force(source_type, source_range, target_output, comp, comp_polarity, comp_range)

    ######################################
    # Measurement Range
    # implemented: RI, RV
    # not implemented: RC, TI, TTI, TV, TTV, TIV, TTIV, TC, TTC
    ######################################

    @property
    def meas_range_current(self):
        """Control current measurement range index. (``RI``)

        Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging:
        :class:`.SMUCurrentRanging`
        """
        response = self.query_learn(32, "RI")
        response = self.current_ranging.meas(response)
        return response

    @meas_range_current.setter
    def meas_range_current(self, meas_range):
        meas_range_index = self.current_ranging.meas(meas_range).index
        self.write(f"RI {self.channel}, {meas_range_index}")
        self.check_errors()

    @property
    def meas_range_voltage(self):
        """Control voltage measurement range index. (``RV``)

        Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging:
        :class:`.SMUVoltageRanging`
        """
        response = self.query_learn(32, "RV")
        response = self.voltage_ranging.meas(response)
        return response

    @meas_range_voltage.setter
    def meas_range_voltage(self, meas_range):
        meas_range_index = self.voltage_ranging.meas(meas_range).index
        self.write(f"RV {self.channel}, {meas_range_index}")
        self.check_errors()

    def meas_range_current_auto(self, mode, rate=50):
        """Specify the auto range operation. Check Documentation. (``RM``)

        :param int mode: Range changing operation mode
        :param int rate: Parameter used to calculate the *current* value, defaults to 50
        """
        mode = strict_range(mode, range(1, 4))
        if mode == 1:
            self.write(f"RM {self.channel}, {mode}")
        else:
            self.write(f"RM {self.channel}, {mode}, {rate}")
        self.write

    ######################################
    # Staircase Sweep Measurement: (WT, WM -> Instrument)
    # implemented:
    #   WV, WI,
    #   WSI, WSV (synchronous output)
    # not implemented: BSSI, BSSV, LSSI, LSSV
    ######################################

    def staircase_sweep_source(
        self, source_type, mode, source_range, start, stop, steps, comp, Pcomp=""
    ):
        """Specify staircase sweep source parameters. (``WV`` or ``WI``)

        :param str source_type: Source type (``'Voltage', 'Current'``)
        :param SweepMode mode: Sweep mode
        :param int source_range: Source range index
        :param float start: Sweep start value
        :param float stop: Sweep stop value
        :param int steps: Number of sweep steps
        :param float comp: Compliance value
        :param float Pcomp: Power compliance, defaults to not set
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "WV"
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "WI"
            source_range = self.current_ranging.output(source_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        mode = SweepMode.get(mode).value
        if mode in [2, 4]:
            if start >= 0 and stop >= 0:
                pass
            elif start <= 0 and stop <= 0:
                pass
            else:
                raise ValueError("For Log Sweep Start and Stop Values must have the same polarity.")
        steps = strict_range(steps, range(1, 10002))
        # check on comp value not yet implemented
        cmd += f"{self.channel}, {mode}, {source_range}, {start}, {stop}, {steps}, {comp}"
        if not Pcomp == "":
            cmd += f", {Pcomp}"
        self.write(cmd)
        self.check_errors()

    # Synchronous Output: WSI, WSV, BSSI, BSSV, LSSI, LSSV

    def synchronous_sweep_source(self, source_type, source_range, start, stop, comp, Pcomp=""):
        """Specify synchronous staircase sweep source (current or voltage)
        and its parameters. (``WSV`` or ``WSI``)

        :param str source_type: Source type (``'Voltage','Current'``)
        :param int source_range: Source range index
        :param float start: Sweep start value
        :param float stop: Sweep stop value
        :param float comp: Compliance value
        :param float Pcomp: Power compliance, defaults to not set
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "WSV"
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "WSI"
            source_range = self.current_ranging.output(source_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        # check on comp value not yet implemented
        cmd += f"{self.channel}, {source_range}, {start}, {stop}, {comp}"
        if not Pcomp == "":
            cmd += f", {Pcomp}"
        self.write(cmd)
        self.check_errors()

    ######################################
    # Sampling Measurements: (ML, MT -> Instrument)
    # implemented: MV, MI
    # not implemented: MSP, MCC, MSC
    ######################################

    def sampling_source(self, source_type, source_range, base, bias, comp):
        """Set DC source (current or voltage) for sampling measurement. (``MV`` or ``MI``)

        :meth:`force` commands on the same channel overwrite this setting.

        :param str source_type: Source type (``'Voltage','Current'``)
        :param int source_range: Source range index
        :param float base: Base voltage/current
        :param float bias: Bias voltage/current
        :param float comp: Compliance value
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "MV"
            source_range = self.voltage_ranging.output(source_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "MI"
            source_range = self.current_ranging.output(source_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        # check on comp value not yet implemented
        cmd += f"{self.channel}, {source_range}, {base}, {bias}, {comp}"
        self.write(cmd)
        self.check_errors()


###############################################################################
# Additional Classes / Constants
###############################################################################


class Ranging:
    """Possible Settings for SMU current/voltage output/measurement ranges.

    Transformation of available voltage/current range names to index and back.

    :param list supported_ranges: Ranges which are supported (list of range indices)
    :param dict ranges: All range names ``{Name: Indices}``
    :param bool fixed_ranges: Add fixed ranges (negative indices), defaults to False

    .. automethod:: __call__
    """

    _Range = namedtuple("Range", "name index")

    def __init__(self, supported_ranges, ranges, fixed_ranges=False):
        if fixed_ranges:
            # add negative indizes for measurement ranges (fixed ranging)
            supported_ranges += [-i for i in supported_ranges]
            # remove duplicates (0)
            supported_ranges = list(dict.fromkeys(supported_ranges))

        # create dictionary {Index: Range Name}
        # distinguish between limited and fixed ranging
        # omitting 'limited auto ranging'/'range fixed'
        # defaults to 'limited auto ranging'
        inverse_ranges = {0: "Auto Ranging"}
        for key, value in ranges.items():
            if isinstance(value, tuple):
                for v in value:
                    inverse_ranges[v] = (key + " limited auto ranging", key)
                    inverse_ranges[-v] = key + " range fixed"
            else:
                inverse_ranges[value] = (key + " limited auto ranging", key)
                inverse_ranges[-value] = key + " range fixed"

        ranges = {}
        indizes = {}
        # only take ranges supported by SMU
        for i in supported_ranges:
            name = inverse_ranges[i]
            # check if multiple names exist for index i
            if isinstance(name, tuple):
                ranges[i] = name[0]  # first entry is main name (unique) and
                # returned as .name attribute,
                # additional entries are just synonyms and can
                # be used to get the range tuple
                # e.g. '1 nA limited auto ranging' is identifier and
                # returned as range name
                # but '1 nA' also works to get the range tuple
                for name2 in name:
                    indizes[name2] = i
            else:
                # only one name per index
                ranges[i] = name  # Index -> Name, Name not unique
                indizes[name] = i  # Name -> Index, only one Index per Name

        # convert all string type keys to uppercase, to avoid case-sensitivity
        indizes = {key.upper(): value for key, value in indizes.items()}
        self.indizes = indizes  # Name -> Index
        self.ranges = ranges  # Index -> Name

    def __call__(self, input_value):
        """Give named tuple (name/index) of given Range.

        Throws error if range is not supported by this SMU.

        :param str or int input_value: Range name or index
        :return: Named tuple (name/index) of range
        :rtype: namedtuple
        """
        # set index
        if isinstance(input_value, int):
            index = input_value
        else:
            try:
                index = self.indizes[input_value.upper()]
            except Exception:
                raise ValueError(
                    f"Specified Range Name {input_value.upper()} is not valid or not supported by"
                    f" this SMU"
                )
        # get name
        try:
            name = self.ranges[index]
        except Exception:
            raise ValueError(f"Specified Range {index} is not supported by this SMU")
        return self._Range(name=name, index=index)


class SMUVoltageRanging:
    """Provide Range Name/Index transformation for voltage measurement/sourcing.

    Validity of ranges is checked against the type of the SMU.

    Omitting the 'limited auto ranging'/'range fixed' specification in
    the range string for voltage measurement defaults to
    'limited auto ranging'.

    Full specification: ``'2 V range fixed'`` or ``'2 V limited auto ranging'``

    ``'2 V'`` defaults to ``'2 V limited auto ranging'``
    """

    def __init__(self, smu_type):
        supported_ranges = {
            "HRSMU": [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
            "MPSMU": [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
            "HPSMU": [0, 11, 20, 12, 200, 13, 400, 14, 1000, 15, 2000],
            "MCSMU": [0, 2, 11, 20, 12, 200, 13, 400],
            "HCSMU": [0, 2, 11, 20, 12, 200, 13, 400],
            "DHCSMU": [0, 2, 11, 20, 12, 200, 13, 400],
            "HVSMU": [0, 15, 2000, 5000, 15000, 30000],
            "UHCU": [0, 14, 1000],
            "HVMCU": [0, 15000, 30000],
            "UHVU": [0, 103],
        }
        supported_ranges = supported_ranges[smu_type]

        ranges = {
            "0.2 V": 2,
            "0.5 V": 5,
            "2 V": (11, 20),
            "5 V": 50,
            "20 V": (12, 200),
            "40 V": (13, 400),
            "100 V": (14, 1000),
            "200 V": (15, 2000),
            "500 V": 5000,
            "1500 V": 15000,
            "3000 V": 30000,
            "10 kV": 103,
        }

        # set range attributes
        self.output = Ranging(supported_ranges, ranges)
        self.meas = Ranging(supported_ranges, ranges, fixed_ranges=True)


class SMUCurrentRanging:
    """Provide Range Name/Index transformation for current measurement/sourcing.

    Validity of ranges is checked against the type of the SMU.

    Omitting the 'limited auto ranging'/'range fixed' specification in
    the range string for current measurement defaults to
    'limited auto ranging'.

    Full specification: ``'1 nA range fixed'`` or ``'1 nA limited auto ranging'``

    ``'1 nA'`` defaults to ``'1 nA limited auto ranging'``
    """

    def __init__(self, smu_type):
        supported_output_ranges = {
            # in combination with ASU also 8
            "HRSMU": [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            # in combination with ASU also 8,9,10
            "MPSMU": [0, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            "HPSMU": [0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            "MCSMU": [0, 15, 16, 17, 18, 19, 20],
            "HCSMU": [0, 15, 16, 17, 18, 19, 20, 22],
            "DHCSMU": [0, 15, 16, 17, 18, 19, 20, 21, 23],
            "HVSMU": [0, 11, 12, 13, 14, 15, 16, 17, 18],
            "UHCU": [0, 26, 28],
            "HVMCU": [],
            "UHVU": [],
        }
        supported_meas_ranges = {
            **supported_output_ranges,
            # overwrite output ranges:
            "HVMCU": [0, 19, 21],
            "UHVU": [0, 15, 16, 17, 18, 19],
        }
        supported_output_ranges = supported_output_ranges[smu_type]
        supported_meas_ranges = supported_meas_ranges[smu_type]

        ranges = {
            "1 pA": 8,  # for ASU
            "10 pA": 9,
            "100 pA": 10,
            "1 nA": 11,
            "10 nA": 12,
            "100 nA": 13,
            "1 uA": 14,
            "10 uA": 15,
            "100 uA": 16,
            "1 mA": 17,
            "10 mA": 18,
            "100 mA": 19,
            "1 A": 20,
            "2 A": 21,
            "20 A": 22,
            "40 A": 23,
            "500 A": 26,
            "2000 A": 28,
        }

        # set range attributes
        self.output = Ranging(supported_output_ranges, ranges)
        self.meas = Ranging(supported_meas_ranges, ranges, fixed_ranges=True)


######################################
# SPGU Setup
######################################


class SPGU(Channel):
    """Provide specific methods for the SPGU module of the Agilent B1500 mainframe.

    :param AgilentB1500 parent: Instance of the B1500 mainframe class
    :param int channel: Channel number of the SPGU
    """

    def __init__(self, parent, channel, **kwargs):
        super().__init__(parent, channel, **kwargs)
        self.ch1 = self.add_child(SPGUChannel, int(f"{self.id}01"), prefix="ch")
        self.ch2 = self.add_child(SPGUChannel, int(f"{self.id}02"), prefix="ch")

    output = Channel.setting(
        "%s",
        """Set SPGU output state. (``SRP``, ``SPP``)
        When enabled, starts SPGU output. When disabled, stops output and channels output
        base voltage.""",
        validator=strict_discrete_set,
        values={False: "SPP", True: "SRP"},
        map_values=True,
    )

    operation_mode = Channel.control(
        "SIM?",
        "SIM %d",
        """Control mode for the Semiconductor Pulse Generator Unit (SPGU). (``SIM``)
        The setting is effective for the all SPGU modules installed in the B1500. This
        command also triggers 0 V output of the SPGU channels which output switch has been ON.""",
        get_process=lambda v: SPGUOperationMode(v),
        set_process=lambda v: SPGUOperationMode(v).value,
    )

    period = Channel.control(
        "SPPER?",
        "SPPER %f",
        """Control the pulse period for SPGU channels (``SPPER``) in seconds (float).
        Applies to all installed SPGU modules""",
        validator=strict_range,
        values=[2e-8, 10],
    )

    def set_output_mode(self, mode, condition=None):
        """Set the operating mode for SPGU channel outputs. (``SPRM``)

        This setting applies to all SPGU modules installed in the B1500.

        :param SPGUOperationMode mode: SPGU operation mode
        :param int or float or None condition: Number of pulses for :attr:`SPGUOutputMode.COUNT` or
            output duration for :attr:`SPGUOutputMode.DURATION`.
            Not used for :attr:`SPGUOutputMode.FREE_RUN`
        """
        mode = SPGUOutputMode.get(mode)

        if mode == SPGUOutputMode.FREE_RUN:
            self.write(f"SPRM {mode.value}")
            return

        if condition is None:
            raise ValueError(f"Condition must be specified when mode is {mode}")

        if mode == SPGUOutputMode.COUNT:
            if not (1 <= condition <= 1_000_000):
                raise ValueError("Condition must be between 1 and 1,000,000 when mode is COUNT.")

        elif mode == SPGUOutputMode.DURATION:
            if not (1e-6 <= condition <= 31_556_926):
                raise ValueError(
                    "Condition must be between 0.000001 and 31,556,926 seconds (1 year) "
                    "when mode is DURATION."
                )

        self.write(f"SPRM {mode.value}, {int(condition)}")

    def get_output_mode(self):
        """Get the current operating mode and condition for SPGU channel outputs. (``SPRM?``)

        :return: Tuple of (mode, condition)
        :rtype: tuple
        """
        response = self.ask("SPRM?")
        mode, condition = response.split(",")
        return SPGUOutputMode(int(mode)), float(condition) if condition else None

    complete = Channel.measurement(
        "SPST?",
        """Get whether the SPGU output has finished. (``SPST?``)""",
        get_process=lambda v: not bool(v),
    )


class SPGUChannel(Channel):
    """SPGU Channel of the Agilent B1500 mainframe."""

    enabled = Channel.setting(
        "%s {ch}",
        """Control SPGU channel enable/disable state. (``CN``, ``CL``)""",
        validator=strict_discrete_set,
        values={False: "CL", True: "CN"},
        map_values=True,
    )

    load_impedance = Channel.control(
        "SER? {ch}",
        "SER {ch}, %f",
        """Control the load impedance (``SER``) in Ohm (float).""",
    )

    def set_output_voltage(self, source=1, base_voltage=0, peak_voltage=0):
        """Set the output voltage of the SPGU channel. (``SPV``)

        :param SPGUSignalSource or int source: Signal source for the output voltage,
            defaults to :attr:`SPGUSignalSource.PULSE_SIGNAL_1`
        :param float base_voltage: Pulse base voltage or DC output voltage in V,
            defaults to 0
        :param float peak_voltage: Pulse peak voltage in V, defaults to 0
        """
        source = SPGUSignalSource.get(source).value
        base_voltage = strict_range(base_voltage, (-40, 40))
        peak_voltage = strict_range(peak_voltage, (-40, 40))
        self.write(f"SPV {self.id}, {source}, {base_voltage}, {peak_voltage}")

    def get_output_voltage(self, source=1):
        """Get the output voltage of the specified signal source. (``SPV?``)

        :param SPGUSignalSource or int source: Signal source
        :return: Tuple of (base_voltage, peak_voltage)
        :rtype: tuple
        """
        source = SPGUSignalSource.get(source).value
        response = self.ask(f"SPV? {self.id}, {source}")
        base_voltage, peak_voltage = map(float, response.split(","))
        return base_voltage, peak_voltage

    output_mode = Channel.control(
        "SPM? {ch}",
        "SPM {ch}, %d",
        """Control the output mode of the SPGU channel. (``SPM``)
        The SPGU operating mode must be set to PG with the SIM 0 command before setting the
        output mode.""",
        get_process=lambda v: SPGUChannelOutputMode(int(v)),
        set_process=lambda v: SPGUChannelOutputMode.get(v).value,
    )

    def set_pulse_timings(
        self,
        source=1,
        delay=0,
        width=1e-7,
        rise_time=2e-8,
        fall_time=None,
    ):
        """Set the timing parameters for the SPGU channel. (``SPT``)

        The SPGU operating mode must be set to PG with the ``SIM 0`` command before setting
        the pulse timings.

        :param SPGUSignalSource or int source: Signal source for the pulse timings,
            defaults to :attr:`SPGUSignalSource.PULSE_SIGNAL_1`
        :param float delay: Pulse delay in seconds, defaults to 0
        :param float width: Pulse width in seconds, defaults to 1e-7
        :param float rise_time: Pulse rise time in seconds, defaults to 2e-8
        :param float fall_time: Pulse fall time in seconds, defaults to rise_time if None
        """
        source = SPGUSignalSource.get(source).value
        if source == SPGUSignalSource.DC:
            raise ValueError("Pulse timings can only be set for pulse sources.")
        command = f"SPT {self.id}, {source}, {delay}, {width}, {rise_time}"
        if fall_time is not None:
            command += f", {fall_time}"
        self.write(command)

    def get_pulse_timings(self, source=1):
        """Get the timing parameters for the SPGU channel. (``SPT?``)
        The SPGU operating mode must be set to PG with the ``SIM 0`` command before getting the
        pulse timings.

        :param SPGUSignalSource or int source: Signal source for the pulse timings,
            defaults to :attr:`SPGUSignalSource.PULSE_SIGNAL_1`
        :return: Tuple of (delay, width, rise_time, fall_time)
        :rtype: tuple
        """
        source = SPGUSignalSource.get(source).value
        response = self.ask(f"SPT? {self.id}, {source}")
        return tuple(map(float, response.split(",")))

    def apply_setup(self):
        """Apply the current setup to the SPGU channel. (``SPUPD``)

        Depends on the :attr:`SPGU.operation_mode` (``SIM``):

        * PG mode: output base voltage set by ``SPV`` command
        * ALWG mode: output initial value of waveform
        """
        self.write(f"SPUPD {self.id}")


class CustomIntEnum(IntEnum):
    """Provide additional methods to IntEnum:

    * Conversion to string automatically replaces '_' with ' ' in names
      and converts to title case

    * get classmethod to get enum reference with name or integer

    .. automethod:: __str__
    """

    def __str__(self):
        """Give title case string of enum value"""
        return str(self.name).replace("_", " ").title()
        # str() conversion just because of pylint bug

    @classmethod
    def get(cls, input_value):
        """Give Enum member by specifying name or value.

        :param str or int input_value: Enum name or value
        :return: Enum member
        """
        if isinstance(input_value, int):
            return cls(input_value)
        else:
            return cls[input_value.upper()]


class ADCType(CustomIntEnum):
    """ADC Type"""

    HSADC = (0,)  #: High-speed ADC
    HRADC = (1,)  #: High-resolution ADC
    HSADC_PULSED = (2,)  #: High-speed ADC for pulsed measurements

    def __str__(self):
        return str(self.name).replace("_", " ")
        # .title() str() conversion just because of pylint bug


class ADCMode(CustomIntEnum):
    """ADC Mode"""

    AUTO = 0  #:
    MANUAL = 1  #:
    PLC = 2  #: Power line cycle mode
    TIME = 3  #: Measurement time mode


class AutoManual(CustomIntEnum):
    """Auto/Manual selection"""

    AUTO = 0  #:
    MANUAL = 1  #:


class ControlMode(CustomIntEnum):
    """Control mode for the digital I/O ports"""

    GENERAL = 0  #: General purpose control mode (default)
    SMU_PGU_SELECTOR = 1  #: 16440A SMU/PGU selector (B1500A-A04) control mode
    N1258A_N1259A = 2  #: N1258A/N1259A module selector control mode
    N1265A = 4  #: N1265A Ultra High Current Expander/Fixture control mode
    N1266A = 8  #: N1266A High Voltage Source Monitor Unit Current Expander control mode
    N1268A = 16  #: N1268A Ultra High Voltage Expander control mode
    N1272A = 32  #: N1272A Device Capacitance Selector control mode


class MeasMode(CustomIntEnum):
    """Measurement Mode"""

    SPOT = 1  #:
    STAIRCASE_SWEEP = 2  #:
    SAMPLING = 10  #:


class MeasOpMode(CustomIntEnum):
    """Measurement Operation Mode"""

    COMPLIANCE_SIDE = 0
    """
    Measure current in the voltage source operation or voltage in the current source operation.
    """
    CURRENT = 1  #:
    VOLTAGE = 2  #:
    FORCE_SIDE = 3  #:
    """
    Measure current in the current sourceoperation or voltage in the voltage source operation.
    """
    COMPLIANCE_AND_FORCE_SIDE = 4
    """
    Current and voltage synchronous measurement. Measurement result contains the compliance side
    data and the force side data in this order.
    """


class PgSelectorPort(CustomIntEnum):
    """Output port of SMU/PG selector"""

    OUTPUT_1_FIRST = 0  #: Output 1 on the first selector
    OUTPUT_2_FIRST = 1  #: Output 2 on the first selector
    OUTPUT_1_SECOND = 2  #: Output 1 on the second selector
    OUTPUT_2_SECOND = 3  #: Output 2 on the second selector


class PgSelectorConnectionStatus(CustomIntEnum):
    """Connection status of I/O port"""

    NO_CONNECTION = 0  #: All open. Breaks connection. Initial setting
    SMU_ON = 1  #: SMU on. Makes connection to the SMU input.
    PGU_ON = 2  #: PGU on. Makes connection to the PGU input.
    PGU_OPEN = 3  #: PGU open. Made by opening the semiconductor relay installed on the PGU on port.


class SweepMode(CustomIntEnum):
    """Sweep Mode"""

    LINEAR_SINGLE = 1  #: Linear sweep (single stair, start to stop.)
    LOG_SINGLE = 2  #: Log sweep (single stair, start to stop.)
    LINEAR_DOUBLE = 3  #: Linear sweep (double stair, start to stop to start.)
    LOG_DOUBLE = 4  #: Log sweep (double stair, start to stop to start.)


class SamplingMode(CustomIntEnum):
    """Sampling Mode"""

    LINEAR = 1  #:
    LOG_10 = 2  #: Logarithmic 10 data points/decade
    LOG_25 = 3  #: Logarithmic 25 data points/decade
    LOG_50 = 4  #: Logarithmic 50 data points/decade
    LOG_100 = 5  #: Logarithmic 100 data points/decade
    LOG_250 = 6  #: Logarithmic 250 data points/decade
    LOG_5000 = 7  #: Logarithmic 5000 data points/decade

    def __str__(self):
        names = {
            1: "Linear",
            2: "Log 10 data/decade",
            3: "Log 25 data/decade",
            4: "Log 50 data/decade",
            5: "Log 100 data/decade",
            6: "Log 250 data/decade",
            7: "Log 5000 data/decade",
        }
        return names[self.value]


class SamplingPostOutput(CustomIntEnum):
    """Output after sampling"""

    BASE = 1  #:
    BIAS = 2  #:


class SPGUChannelOutputMode(CustomIntEnum):
    """Output mode of SPGU channel"""

    DC = 0  #: DC output mode
    SIGNAL_SOURCE_1 = 1  #: 2-level pulse output mode using pulse signal source 1
    SIGNAL_SOURCE_2 = 2  #: 2-level pulse output mode using pulse signal source 2
    SIGNAL_SOURCE_1_2 = 3  #: 3-level pulse output mode using pulse signal source 1 and 2


class SPGUSignalSource(CustomIntEnum):
    """Signal source for SPGU"""

    DC = 0  #:
    PULSE_SIGNAL_1 = 1  #:
    PULSE_SIGNAL_2 = 2  #:


class SPGUOperationMode(CustomIntEnum):
    """Operation mode of Semiconductor Pulse Generator Unit (SPGU)"""

    PG = 0  #: PG (pulse output) mode
    ALWG = 1  #: ALWG (arbitrary linear wave output) mode


class SPGUOutputMode(CustomIntEnum):
    """Operating mode for SPGU channel outputs"""

    FREE_RUN = 0
    """
    Free Run mode. Continues outputting until the ``SPP`` command is executed. The condition
    parameter is not required.
    """
    COUNT = 1
    """
    Count mode. Outputs the number of pulses (when set to PG mode with the ``SIM 0`` command), or
    the number of sequences (when set to ALWG mode with the ``SIM 1`` command) specified by
    the condition parameter.
    """
    DURATION = 2
    """
    Duration mode. Outputs for a duration specified by the condition parameter.
    """


class StaircaseSweepPostOutput(CustomIntEnum):
    """Output after staircase sweep"""

    START = 1  #:
    STOP = 2  #:


class CompliancePolarity(CustomIntEnum):
    """Compliance polarity"""

    AUTO = 0  #:
    MANUAL = 1  #:


class WaitTimeType(CustomIntEnum):
    """Wait time type"""

    SMU_SOURCE = 1  #: wait before changing the output value
    SMU_MEASUREMENT = 2  #: wait before starting the measurement
    CMU_MEASUREMENT = 3  #: wait before starting the measurement


###############################################################################
# Query Learn: Parse Instrument settings into human readable format
###############################################################################


class QueryLearn:
    """Methods to issue and process ``*LRN?`` (learn) command and response."""

    @staticmethod
    def query_learn(ask, query_type):
        """Issue ``*LRN?`` (learn) command to the instrument to read
        configuration.
        Return dictionary of commands and set values.

        :param int query_type: Query type according to the programming guide
        :return: Dictionary of command and set values
        :rtype: dict
        """
        response = ask("*LRN? " + str(query_type))
        # response.split(';')
        response = re.findall(r"(?P<command>[A-Z]+)(?P<parameter>[0-9,\+\-\.E]+)", response)
        # check if commands are unique -> suitable as keys for dict
        counts = Counter([item[0] for item in response])
        # responses that start with a channel number
        # the channel number should always be included in the key
        include_chnum = [
            "DI",
            "DV",  # Sourcing
            "RI",
            "RV",  # Ranging
            "WV",
            "WI",
            "WSV",
            "WSI",  # Staircase Sweep
            "PV",
            "PI",
            "PWV",
            "PWI",  # Pulsed Source
            "MV",
            "MI",
            "MSP",  # Sampling
            "SSR",
            "RM",
            "AAD",  # Series Resistor, Auto Ranging, ADC
        ]  # probably not complete yet...
        response_dict = {}
        for element in response:
            parameters = element[1].split(",")
            name = element[0]
            if (counts[name] > 1) or (name in include_chnum):
                # append channel (first parameter) to command as dict key
                name += parameters[0]
                parameters = parameters[1:]
            if len(parameters) == 1:
                parameters = parameters[0]
            # skip second AAD entry for each channel -> contains no information
            if "AAD" in name and name in response_dict.keys():
                continue
            response_dict[name] = parameters
        return response_dict

    @classmethod
    def query_learn_header(cls, ask, query_type, smu_references, single_command=False):
        """Issue ``*LRN?`` (learn) command to the instrument to
        read configuration.
        Processes information to human readable values for debugging
        purposes or file headers.

        :param Instrument.ask ask: ask method of the instrument
        :param int or str query_type: Number according to Programming Guide
        :param dict smu_references: SMU references by channel
        :param str single_command: if only a single command should be returned,
                                   defaults to False
        :return: Read configuration
        :rtype: dict
        """
        response = cls.query_learn(ask, query_type)
        if single_command is not False:
            response = response[single_command]
        ret = {}
        for key, value in response.items():
            # command without channel
            command = re.findall(r"(?P<command>[A-Z]+)", key)[0]
            new_dict = getattr(cls, command)(key, value, smu_references=smu_references)
            ret = {**ret, **new_dict}
        return ret

    @staticmethod
    def to_dict(parameters, names, *args):
        """Take parameters returned by :meth:`query_learn` and ordered list
        of corresponding parameter names (optional function) and return
        dict of parameters including names.

        :param dict parameters: Parameters for one command returned
                                by :meth:`query_learn`
        :param list names: list of names or (name, function) tuples, ordered
        :return: Parameter name and (processed) parameter
        :rtype: dict
        """
        ret = OrderedDict()
        if isinstance(parameters, str):
            # otherwise string is enumerated
            parameters_iter = [(0, parameters)]
        else:
            parameters_iter = enumerate(parameters)
        for i, parameter in parameters_iter:
            if isinstance(names[i], tuple):
                ret[names[i][0]] = names[i][1](parameter, *args)
            else:
                ret[names[i]] = parameter
        return ret

    @staticmethod
    def _get_smu(key, smu_references):
        # command without channel
        command = re.findall(r"(?P<command>[A-Z]+)", key)[0]
        channel = key[len(command) :]  # noqa: E203
        return smu_references[int(channel)]

    # SMU Modes
    @classmethod
    def DI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Current Range", lambda parameter: smu.current_ranging.output(int(parameter)).name),
            "Current Output (A)",
            "Compliance Voltage (V)",
            ("Compliance Polarity", lambda parameter: str(CompliancePolarity.get(int(parameter)))),
            (
                "Voltage Compliance Ranging Type",
                lambda parameter: smu.voltage_ranging.meas(int(parameter)).name,
            ),
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Constant Current"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def DV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Voltage Range", lambda parameter: smu.voltage_ranging.output(int(parameter)).name),
            "Voltage Output (V)",
            "Compliance Current (A)",
            ("Compliance Polarity", lambda parameter: str(CompliancePolarity.get(int(parameter)))),
            (
                "Current Compliance Ranging Type",
                lambda parameter: smu.current_ranging.meas(int(parameter)).name,
            ),
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Constant Voltage"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def CL(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key + parameters, smu_references)
        return {smu.name: "OFF"}

    # Instrument Settings: 31
    @classmethod
    def TM(cls, key, parameters, smu_references={}):
        names = ["Trigger Mode"]  # enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def AV(cls, key, parameters, smu_references={}):
        names = [
            "ADC Averaging Number",
            ("ADC Averaging Mode", lambda parameter: str(AutoManual(int(parameter)))),
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def CM(cls, key, parameters, smu_references={}):
        names = [("Auto Calibration Mode", lambda parameter: bool(int(parameter)))]
        return cls.to_dict(parameters, names)

    @classmethod
    def FMT(cls, key, parameters, smu_references={}):
        names = ["Output Data Format", "Output Data Mode"]
        # enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def MM(cls, key, parameters, smu_references={}):
        names = [("Measurement Mode", lambda parameter: str(MeasMode(int(parameter))))]
        ret = cls.to_dict(parameters[0], names)
        smu_names = []
        for channel in parameters[1:]:
            smu_names.append(smu_references[int(channel)].name)
        ret["Measurement Channels"] = ", ".join(smu_names)
        return ret

    # Measurement Ranging: 32
    @classmethod
    def RI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (
                smu.name + " Current Measurement Range",
                lambda parameter: smu.current_ranging.meas(int(parameter)).name,
            )
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def RV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (
                smu.name + " Voltage Measurement Range",
                lambda parameter: smu.voltage_ranging.meas(int(parameter)).name,
            )
        ]
        return cls.to_dict(parameters, names)

    # Sweep: 33
    @classmethod
    def WM(cls, key, parameters, smu_references={}):
        names = [
            ("Auto Abort Status", lambda parameter: {2: True, 1: False}[int(parameter)]),
            (
                "Output after Measurement",
                lambda parameter: str(StaircaseSweepPostOutput(int(parameter))),
            ),
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def WT(cls, key, parameters, smu_references={}):
        names = [
            "Hold Time (s)",
            "Delay Time (s)",
            "Step Delay Time (s)",
            "Step Source Trigger Delay Time (s)",
            "Step Measurement Trigger Delay Time (s)",
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def WV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Sweep Mode", lambda parameter: str(SweepMode(int(parameter)))),
            ("Voltage Range", lambda parameter: smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)",
            "Stop Voltage (V)",
            "Number of Steps",
            "Current Compliance (A)",
            "Power Compliance (W)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Voltage Sweep Source"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Sweep Mode", lambda parameter: str(SweepMode(int(parameter)))),
            ("Current Range", lambda parameter: smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)",
            "Stop Current (A)",
            "Number of Steps",
            "Voltage Compliance (V)",
            "Power Compliance (W)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Current Sweep Source"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WSV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Voltage Range", lambda parameter: smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)",
            "Stop Voltage (V)",
            "Current Compliance (A)",
            "Power Compliance (W)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Synchronous Voltage Sweep Source"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WSI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Current Range", lambda parameter: smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)",
            "Stop Current (A)",
            "Voltage Compliance (V)",
            "Power Compliance (W)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Synchronous Current Sweep Source"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    # SMU Measurement Operation Mode: 46
    @classmethod
    def CMM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (
                smu.name + " Measurement Operation Mode",
                lambda parameter: str(MeasOpMode(int(parameter))),
            )
        ]
        return cls.to_dict(parameters, names)

    # Sampling: 47
    @classmethod
    def MSC(cls, key, parameters, smu_references={}):
        names = [
            ("Auto Abort Status", lambda parameter: {2: True, 1: False}[int(parameter)]),
            ("Output after Measurement", lambda parameter: str(SamplingPostOutput(int(parameter)))),
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def MT(cls, key, parameters, smu_references={}):
        names = [
            "Hold Bias Time (s)",
            "Sampling Interval (s)",
            "Number of Samples",
            "Hold Base Time (s)",
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def ML(cls, key, parameters, smu_references={}):
        names = [("Sampling Mode", lambda parameter: str(SamplingMode(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def MV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Voltage Range", lambda parameter: smu.voltage_ranging.output(int(parameter)).name),
            "Base Voltage (V)",
            "Bias Voltage (V)",
            "Current Compliance (A)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Voltage Source Sampling"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def MI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Current Range", lambda parameter: smu.current_ranging.output(int(parameter)).name),
            "Base Current (A)",
            "Bias Current (A)",
            "Voltage Compliance (V)",
        ]
        ret = cls.to_dict(parameters, names)
        ret["Source Type"] = "Current Source Sampling"
        ret.move_to_end("Source Type", last=False)  # make first entry
        return {smu.name: ret}

    # SMU Series Resistor: 53
    @classmethod
    def SSR(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + " Series Resistor", lambda parameter: bool(int(parameter)))]
        return cls.to_dict(parameters, names)

    # Auto Ranging Mode: 54
    @classmethod
    def RM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [smu.name + " Ranging Mode", smu.name + " Ranging Mode Parameter"]
        return cls.to_dict(parameters, names)

    # ADC: 55, 56
    @classmethod
    def AAD(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [(smu.name + " ADC", lambda parameter: str(ADCType(int(parameter))))]
        return cls.to_dict(parameters, names)

    @classmethod
    def AIT(cls, key, parameters, smu_references={}):
        adc_type = key[3:]
        adc_name = str(ADCType(int(adc_type)))
        names = [
            (adc_name + " Mode", lambda parameter: str(ADCMode(int(parameter)))),
            adc_name + " Parameter",
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def AZ(cls, key, parameters, smu_references={}):
        names = [("ADC Auto Zero", lambda parameter: str(bool(int(parameter))))]
        return cls.to_dict(parameters, names)

    # Time Stamp: 60
    @classmethod
    def TSC(cls, key, parameters, smu_references={}):
        names = [("Time Stamp", lambda parameter: str(bool(int(parameter))))]
        return cls.to_dict(parameters, names)
