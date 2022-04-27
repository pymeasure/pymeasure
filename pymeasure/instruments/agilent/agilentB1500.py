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

import logging
import weakref
import time
import re
import numpy as np
import pandas as pd
from enum import IntEnum
from collections import Counter, namedtuple, OrderedDict
from pymeasure.instruments.validators import (strict_discrete_set,
                                              strict_range,
                                              strict_discrete_range)
from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

######################################
# Agilent B1500 Mainframe
######################################


class AgilentB1500(Instrument):
    """ Represents the Agilent B1500 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking different kinds of
    measurements.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent B1500 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self._smu_names = {}
        self._smu_references = {}

    @property
    def smu_references(self):
        """Returns all SMU instances.
        """
        return self._smu_references.values()

    @property
    def smu_names(self):
        """Returns all SMU names.
        """
        return self._smu_names

    def query_learn(self, query_type):
        """Queries settings from the instrument (``*LRN?``).
        Returns dict of settings.

        :param query_type: Query type (number according to manual)
        :type query_type: int or str
        """
        return QueryLearn.query_learn(self.ask, query_type)

    def query_learn_header(self, query_type, **kwargs):
        """Queries settings from the instrument (``*LRN?``).
        Returns dict of settings in human readable format for debugging
        or file headers.
        For optional arguments check the underlying definition of
        :meth:`QueryLearn.query_learn_header`.

        :param query_type: Query type (number according to manual)
        :type query_type: int or str
        """
        return QueryLearn.query_learn_header(
            self.ask, query_type, self._smu_references, **kwargs)

    def reset(self):
        """ Resets the instrument to default settings (``*RST``)
        """
        self.write("*RST")

    def query_modules(self):
        """ Queries module models from the instrument.
        Returns dictionary of channel and module type.

        :return: Channel:Module Type
        :rtype: dict
        """
        modules = self.ask('UNT?')
        modules = modules.split(';')
        module_names = {
            'B1525A': 'SPGU',
            'B1517A': 'HRSMU',
            'B1511A': 'MPSMU',
            'B1511B': 'MPSMU',
            'B1510A': 'HPSMU',
            'B1514A': 'MCSMU',
            'B1520A': 'MFCMU'
        }
        out = {}
        for i, module in enumerate(modules):
            module = module.split(',')
            if not module[0] == '0':
                try:
                    out[i + 1] = module_names[module[0]]
                    # i+1: channels start at 1 not at 0
                except Exception:
                    raise NotImplementedError(
                        f'Module {module[0]} is not implented yet!')
        return out

    def initialize_smu(self, channel, smu_type, name):
        """ Initializes SMU instance by calling :class:`.SMU`.

        :param channel: SMU channel
        :type channel: int
        :param smu_type: SMU type, e.g. ``'HRSMU'``
        :type smu_type: str
        :param name: SMU name for pymeasure (data output etc.)
        :type name: str
        :return: SMU instance
        :rtype: :class:`.SMU`
        """
        if channel in (
                list(range(101, 1101, 100))
                + list(range(102, 1102, 100))):
            channel = int(str(channel)[0:-2])
            # subchannels not relevant for SMU/CMU
        channel = strict_discrete_set(channel, range(1, 11))
        self._smu_names[channel] = name
        smu_reference = SMU(self, channel, smu_type, name)
        self._smu_references[channel] = smu_reference
        return smu_reference

    def initialize_all_smus(self):
        """ Initialize all SMUs by querying available modules and creating
        a SMU class instance for each.
        SMUs are accessible via attributes ``.smu1`` etc.
        """
        modules = self.query_modules()
        i = 1
        for channel, smu_type in modules.items():
            if 'SMU' in smu_type:
                setattr(self, 'smu' + str(i),
                        self.initialize_smu(
                            channel, smu_type, 'SMU' + str(i)))
                i += 1

    def pause(self, pause_seconds):
        """ Pauses Command Excecution for given time in seconds (``PA``)

        :param pause_seconds: Seconds to pause
        :type pause_seconds: int
        """
        self.write("PA %d" % pause_seconds)

    def abort(self):
        """ Aborts the present operation but channels may still output
        current/voltage (``AB``)
        """
        self.write("AB")

    def force_gnd(self):
        """ Force 0V on all channels immediately. Current Settings can
        be restored with RZ. (``DZ``)
        """
        self.write("DZ")

    def check_errors(self):
        """ Check for errors (``ERRX?``)
        """
        error = self.ask("ERRX?")
        error = re.match(
            r'(?P<errorcode>[+-]?\d+(?:\.\d+)?),"(?P<errortext>[\w\s.]+)',
            error).groups()
        if int(error[0]) == 0:
            return
        else:
            raise OSError(
                f"Agilent B1500 Error {error[0]}: {error[1]}")

    def check_idle(self):
        """ Check if instrument is idle (``*OPC?``)
        """
        self.ask("*OPC?")

    def clear_buffer(self):
        """ Clear output data buffer (``BC``) """
        self.write("BC")

    def clear_timer(self):
        """ Clear timer count (``TSR``) """
        self.write("TSR")

    def send_trigger(self):
        """ Send trigger to start measurement (except High Speed Spot)
        (``XE``)"""
        self.write("XE")

    @property
    def auto_calibration(self):
        """ Enable/Disable SMU auto-calibration every 30 minutes. (``CM``)

        :type: bool
        """
        response = self.query_learn(31)['CM']
        response = bool(int(response))
        return response

    @auto_calibration.setter
    def auto_calibration(self, setting):
        setting = int(setting)
        self.write('CM %d' % setting)
        self.check_errors()

    ######################################
    # Data Formatting
    ######################################

    class _data_formatting_generic():
        """ Format data output head of measurement value into user
        readable values

        :param str output_format_str: Format string of measurement value
        :param dict smu_names: Dictionary of channel and SMU name
        """

        channels = {"A": 101, "B": 201, "C": 301, "D": 401, "E": 501,
                    "F": 601, "G": 701, "H": 801, "I": 901, "J": 1001,
                    "a": 102, "b": 202, "c": 302, "d": 402, "e": 502,
                    "f": 602, "g": 702, "h": 802, "i": 902, "j": 1002,
                    "V": "GNDU", "Z": "MISC"}
        status = {
            'W': 'First or intermediate sweep step data',
            'E': 'Last sweep step data',
            'T': 'Another channel reached its compliance setting.',
            'C': 'This channel reached its compliance setting',
            'V': ('Measurement data is over the measurement range/Sweep was '
                  'aborted by automatic stop function or power compliance. '
                  'D will be 199.999E+99 (no meaning).'),
            'X': ('One or more channels are oscillating. Or source output did '
                  'not settle before measurement.'),
            'F': 'SMU is in the force saturation condition.',
            'G': ('Linear/Binary search measurement: Target value was not '
                  'found within the search range. '
                  'Returns source output value. '
                  'Quasi-pulsed spot measurement: '
                  'The detection time was over the limit.'),
            'S': ('Linear/Binary search measurement: The search measurement '
                  'was stopped. Returns source output value. '
                  'Quasi-pulsed spot measurement: Output slew rate was too '
                  'slow to perform the settling detection. '
                  'Or quasi-pulsed source channel reached compliance before '
                  'the source output voltage changed 10V '
                  'from the start voltage.'),
            'U': 'CMU is in the NULL loop unbalance condition.',
            'D': 'CMU is in the IV amplifier saturation condition.'
        }
        smu_status = {
            1: 'A/D converter overflowed.',
            2: 'Oscillation of force or saturation current.',
            4: 'Antoher unit reached its compliance setting.',
            8: 'This unit reached its compliance setting.',
            16: 'Target value was not found within the search range.',
            32: 'Search measurement was automatically stopped.',
            64: 'Invalid data is returned. D is not used.',
            128: 'End of data'
        }
        cmu_status = {
            1: 'A/D converter overflowed.',
            2: 'CMU is in the NULL loop unbalance condition.',
            4: 'CMU is in the IV amplifier saturation condition.',
            64: 'Invalid data is returned. D is not used.',
            128: 'End of data'
        }
        data_names_int = {"Sampling index"}  # convert to int instead of float

        def __init__(self, smu_names, output_format_str):
            """ Stores parameters of the chosen output format
            for later usage in reading and processing instrument data.

            Data Names: e.g. "Voltage (V)" or "Current Measurement (A)"
            """
            sizes = {"FMT1": 16, "FMT11": 17, "FMT21": 19}
            try:
                self.size = sizes[output_format_str]
            except Exception:
                raise NotImplementedError(
                    ("Data Format {} is not "
                     "implemented so far.").format(output_format_str))
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
                "T": "Time (s)"
            }
            data_names_G = {
                "V": "Voltage Measurement (V)",
                "I": "Current Measurement (A)",
                "v": "Voltage Output (V)",
                "i": "Current Output (A)",
                "f": "Frequency (Hz)",
                "z": "invalid data"
            }
            if output_format_str in ['FMT1', 'FMT5', 'FMT11', 'FMT15']:
                self.data_names = {**data_names_C, **data_names_CG}
            elif output_format_str in ['FMT21', 'FMT25']:
                self.data_names = {**data_names_G, **data_names_CG}
            else:
                self.data_names = {}  # no header
            self.smu_names = smu_names

        def check_status(self, status_string, name=False, cmu=False):
            """Check returned status of instrument. If not null or end of
            data, message is written to log.info.

            :param status_string: Status string returned by the instrument
                                  when reading data.
            :type status_string: str
            :param cmu: Whether or not channel is CMU, defaults to False (SMU)
            :type cmu: bool, optional
            """
            def log_failed():
                log.info(
                    ('Agilent B1500: check_status not '
                     'possible for status {}').format(status_string))

            if name is False:
                name = ''
            else:
                name = f' {name}'

            status = re.search(
                r'(?P<number>[0-9]*)(?P<letter>[ A-Z]*)',
                status_string)
            # depending on FMT, status may be a letter or up to 3 digits
            if len(status.group('number')) > 0:
                status = int(status.group('number'))
                if status in (0, 128):
                    # 0: no error; 128: End of data
                    return
                if cmu is True:
                    status_dict = self.cmu_status
                else:
                    status_dict = self.smu_status
                for index, digit in enumerate(bin(status)[2:]):
                    # [2:] to chop off 0b
                    if digit == '1':
                        log.info('Agilent B1500{}: {}'.format(
                            name, status_dict[2**index]))
            elif len(status.group('letter')) > 0:
                status = status.group('letter')
                status = status.strip()  # remove whitespaces
                if status not in ['N', 'W', 'E']:
                    try:
                        status = self.status[status]
                        log.info(f'Agilent B1500{name}: {status}')
                    except KeyError:
                        log_failed()
            else:
                log_failed()

        def format_channel_check_status(self, status_string, channel_string):
            """Returns channel number for given channel letter.
            Checks for not null status of the channel and writes according
            message to log.info.

            :param status_string: Status string returned by the instrument
                                  when reading data.
            :type status_string: str
            :param channel_string: Channel string returned by the instrument
            :type channel_string: str
            :return: Channel name
            :rtype: str
            """
            channel = self.channels[channel_string]
            if isinstance(channel, int):
                channel = int(str(channel)[0:-2])
                # subchannels not relevant for SMU/CMU
            try:
                smu_name = self.smu_names[channel]
                if 'SMU' in smu_name:
                    self.check_status(status_string, name=smu_name, cmu=False)
                if 'CMU' in smu_name:
                    self.check_status(status_string, name=smu_name, cmu=True)
                return smu_name
            except KeyError:
                self.check_status(status_string)
                return channel

    class _data_formatting_FMT1(_data_formatting_generic):
        """ Data formatting for FMT1 format
        """

        def __init__(self, smu_names={}, output_format_string="FMT1"):
            super().__init__(smu_names, output_format_string)

        def format_single(self, element):
            """ Format single measurement value

            :param element: Single measurement value read from the instrument
            :type element: str
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
        """ Data formatting for FMT11 format (based on FMT1)
        """

        def __init__(self, smu_names={}):
            super().__init__(smu_names, "FMT11")

    class _data_formatting_FMT21(_data_formatting_generic):
        """ Data formatting for FMT21 format
        """

        def __init__(self, smu_names={}):
            super().__init__(smu_names, "FMT21")

        def format_single(self, element):
            """ Format single measurement value

            :param element: Single measurement value read from the instrument
            :type element: str
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
        """ Return data formatting class for given data format string

        :param output_format_str: Data output format, e.g. ``FMT21``
        :type output_format_str: str
        :param smu_names: Dictionary of channels and SMU names, defaults to {}
        :type smu_names: dict, optional
        :return: Corresponding formatting class
        :rtype: class
        """
        classes = {
            "FMT1": self._data_formatting_FMT1,
            "FMT11": self._data_formatting_FMT11,
            "FMT21": self._data_formatting_FMT21
        }
        try:
            format_class = classes[output_format_str]
        except KeyError:
            log.error((
                "Data Format {} is not implemented "
                "so far. Please set appropriate Data Format."
            ).format(output_format_str))
            return
        else:
            return format_class(smu_names=smu_names)

    def data_format(self, output_format, mode=0):
        """ Specifies data output format. Check Documentation for parameters.
        Should be called once per session to set the data format for
        interpreting the measurement values read from the instrument.
        (``FMT``)

        Currently implemented are format 1, 11, and 21.

        :param output_format: Output format string, e.g. ``FMT21``
        :type output_format: str
        :param mode: Data output mode, defaults to 0 (only measurement
                     data is returned)
        :type mode: int, optional
        """
        # restrict to implemented formats
        output_format = strict_discrete_set(
            output_format, [1, 11, 21])
        # possible: [1, 2, 3, 4, 5, 11, 12, 13, 14, 15, 21, 22, 25]
        mode = strict_range(mode, range(0, 11))
        self.write("FMT %d, %d" % (output_format, mode))
        self.check_errors()
        if self._smu_names == {}:
            print(
                'No SMU names available for formatting, '
                'instead channel numbers will be used. '
                'Call data_format after initializing all SMUs.'
            )
            log.info(
                'No SMU names available for formatting, '
                'instead channel numbers will be used. '
                'Call data_format after initializing all SMUs.'
            )
        self._data_format = self._data_formatting(
            "FMT%d" % output_format, self._smu_names)

    ######################################
    # Measurement Settings
    ######################################

    @property
    def parallel_meas(self):
        """ Enable/Disable parallel measurements.
            Effective for SMUs using HSADC and measurement modes 1,2,10,18.
            (``PAD``)

        :type: bool
        """
        response = self.query_learn(110)['PAD']
        response = bool(int(response))
        return response

    @parallel_meas.setter
    def parallel_meas(self, setting):
        setting = int(setting)
        self.write('PAD %d' % setting)
        self.check_errors()

    def query_meas_settings(self):
        """Read settings for ``TM``, ``AV``, ``CM``, ``FMT`` and ``MM``
        commands (31) from the instrument.
        """
        return self.query_learn_header(31)

    def query_meas_mode(self):
        """Read settings for ``MM`` command (part of 31) from the instrument.
        """
        return self.query_learn_header(31, single_command='MM')

    def meas_mode(self, mode, *args):
        """ Set Measurement mode of channels. Measurements will be taken in
        the same order as the SMU references are passed. (``MM``)

        :param mode: Measurement mode

            * Spot
            * Staircase Sweep
            * Sampling

        :type mode: :class:`.MeasMode`
        :param args: SMU references
        :type args: :class:`.SMU`
        """
        mode = MeasMode.get(mode)
        cmd = "MM %d" % mode.value
        for smu in args:
            if isinstance(smu, SMU):
                cmd += ", %d" % smu.channel
        self.write(cmd)
        self.check_errors()

    # ADC Setup: AAD, AIT, AV, AZ

    def query_adc_setup(self):
        """Read ADC settings (55, 56) from the intrument.
        """
        return {**self.query_learn_header(55), **self.query_learn_header(56)}

    def adc_setup(self, adc_type, mode, N=''):
        """ Set up operation mode and parameters of ADC for each ADC type.
        (``AIT``)
        Defaults:

            - HSADC: Auto N=1, Manual N=1, PLC N=1, Time N=0.000002(s)
            - HRADC: Auto N=6, Manual N=3, PLC N=1

        :param adc_type: ADC type
        :type adc_type: :class:`.ADCType`
        :param mode: ADC mode
        :type mode: :class:`.ADCMode`
        :param N: additional parameter, check documentation, defaults to ``''``
        :type N: str, optional
        """

        adc_type = ADCType.get(adc_type)
        mode = ADCMode.get(mode)
        if (adc_type == ADCType['HRADC']) and (mode == ADCMode['TIME']):
            raise ValueError("Time ADC mode is not available for HRADC")
        command = "AIT %d, %d" % (adc_type.value, mode.value)
        if not N == '':
            if mode == ADCMode['TIME']:
                command += (", %g" % N)
            else:
                command += (", %d" % N)
        self.write(command)
        self.check_errors()

    def adc_averaging(self, number, mode='Auto'):
        """ Set number of averaging samples of the HSADC. (``AV``)

        Defaults: N=1, Auto

        :param number: Number of averages
        :type number: int
        :param mode: Mode (``'Auto','Manual'``), defaults to 'Auto'
        :type mode: :class:`.AutoManual`, optional
        """
        if number > 0:
            number = strict_range(number, range(1, 1024))
            mode = AutoManual.get(mode).value
            self.write("AV %d, %d" % (number, mode))
        else:
            number = strict_range(number, range(-1, -101, -1))
            self.write("AV %d" % number)
        self.check_errors()

    @property
    def adc_auto_zero(self):
        """ Enable/Disable ADC zero function. Halfs the
        integration time, if off. (``AZ``)

        :type: bool
        """
        response = self.query_learn(56)['AZ']
        response = bool(int(response))
        return response

    @adc_auto_zero.setter
    def adc_auto_zero(self, setting):
        setting = int(setting)
        self.write('AZ %d' % setting)
        self.check_errors()

    @property
    def time_stamp(self):
        """ Enable/Disable Time Stamp function. (``TSC``)

        :type: bool
        """
        response = self.query_learn(60)['TSC']
        response = bool(int(response))
        return response

    @time_stamp.setter
    def time_stamp(self, setting):
        setting = int(setting)
        self.write('TSC %d' % setting)
        self.check_errors()

    def query_time_stamp_setting(self):
        """Read time stamp settings (60) from the instrument.
        """
        return self.query_learn_header(60)

    def wait_time(self, wait_type, N, offset=0):
        """Configure wait time. (``WAT``)

        :param wait_type: Wait time type
        :type wait_type: :class:`.WaitTimeType`
        :param N: Coefficient for initial wait time, default: 1
        :type N: float
        :param offset: Offset for wait time, defaults to 0
        :type offset: int, optional
        """
        wait_type = WaitTimeType.get(wait_type).value
        self.write('WAT %d, %g, %d' % (wait_type, N, offset))
        self.check_errors()

    ######################################
    # Sweep Setup
    ######################################

    def query_staircase_sweep_settings(self):
        """Reads Staircase Sweep Measurement settings (33)
        from the instrument.
        """
        return self.query_learn_header(33)

    def sweep_timing(self, hold, delay, step_delay=0, step_trigger_delay=0,
                     measurement_trigger_delay=0):
        """ Sets Hold Time, Delay Time and Step Delay Time for
        staircase or multi channel sweep measurement. (``WT``)
        If not set, all parameters are 0.

        :param hold: Hold time
        :type hold: float
        :param delay: Delay time
        :type delay: float
        :param step_delay: Step delay time, defaults to 0
        :type step_delay: float, optional
        :param step_trigger_delay: Trigger delay time, defaults to 0
        :type step_trigger_delay: float, optional
        :param measurement_trigger_delay: Measurement trigger delay time,
                                          defaults to 0
        :type measurement_trigger_delay: float, optional
        """
        hold = strict_discrete_range(hold, (0, 655.35), 0.01)
        delay = strict_discrete_range(delay, (0, 65.535), 0.0001)
        step_delay = strict_discrete_range(step_delay, (0, 1), 0.0001)
        step_trigger_delay = strict_discrete_range(
            step_trigger_delay, (0, delay), 0.0001)
        measurement_trigger_delay = strict_discrete_range(
            measurement_trigger_delay, (0, 65.535), 0.0001)
        self.write("WT %g, %g, %g, %g, %g" %
                   (hold, delay, step_delay, step_trigger_delay,
                    measurement_trigger_delay))
        self.check_errors()

    def sweep_auto_abort(self, abort, post='START'):
        """ Enables/Disables the automatic abort function.
        Also sets the post measurement condition. (``WM``)

        :param abort: Enable/Disable automatic abort
        :type abort: bool
        :param post: Output after measurement, defaults to 'Start'
        :type post: :class:`.StaircaseSweepPostOutput`, optional
        """
        abort_values = {True: 2, False: 1}
        abort = strict_discrete_set(abort, abort_values)
        abort = abort_values[abort]
        post = StaircaseSweepPostOutput.get(post)
        self.write("WM %d, %d" % (abort, post.value))
        self.check_errors()

    ######################################
    # Sampling Setup
    ######################################

    def query_sampling_settings(self):
        """Reads Sampling Measurement settings (47) from the instrument.
        """
        return self.query_learn_header(47)

    @property
    def sampling_mode(self):
        """ Set linear or logarithmic sampling mode. (``ML``)

        :type: :class:`.SamplingMode`
        """
        response = self.query_learn(47)
        response = response['ML']
        return SamplingMode(response)

    @sampling_mode.setter
    def sampling_mode(self, mode):
        mode = SamplingMode.get(mode).value
        self.write("ML %d" % mode)
        self.check_errors()

    def sampling_timing(self, hold_bias, interval, number, hold_base=0):
        """ Sets Timing Parameters for the Sampling Measurement (``MT``)

        :param hold_bias: Bias hold time
        :type hold_bias: float
        :param interval: Sampling interval
        :type interval: float
        :param number: Number of Samples
        :type number: int
        :param hold_base: Base hold time, defaults to 0
        :type hold_base: float, optional
        """
        n_channels = self.query_meas_settings()['Measurement Channels']
        n_channels = len(n_channels.split(', '))
        if interval >= 0.002:
            hold_bias = strict_discrete_range(hold_bias, (0, 655.35), 0.01)
            interval = strict_discrete_range(interval, (0, 65.535), 0.001)
        else:
            try:
                hold_bias = strict_discrete_range(
                    hold_bias, (-0.09, -0.0001), 0.0001)
            except ValueError as error1:
                try:
                    hold_bias = strict_discrete_range(
                        hold_bias, (0, 655.35), 0.01)
                except ValueError as error2:
                    raise ValueError(
                        'Bias hold time does not match either '
                        + 'of the two possible specifications: '
                        + f'{error1} {error2}')
            if interval >= 0.0001 + 0.00002 * (n_channels - 1):
                interval = strict_discrete_range(interval,
                                                 (0, 0.00199), 0.00001)
            else:
                raise ValueError(
                    f'Sampling interval {interval} is too short.')
        number = strict_discrete_range(number, (0, int(100001 / n_channels)), 1)
        # ToDo: different restrictions apply for logarithmic sampling!
        hold_base = strict_discrete_range(hold_base, (0, 655.35), 0.01)

        self.write("MT %g, %g, %d, %g" %
                   (hold_bias, interval, number, hold_base))
        self.check_errors()

    def sampling_auto_abort(self, abort, post='Bias'):
        """ Enables/Disables the automatic abort function.
        Also sets the post measurement condition. (``MSC``)

        :param abort: Enable/Disable automatic abort
        :type abort: bool
        :param post: Output after measurement, defaults to 'Bias'
        :type post: :class:`.SamplingPostOutput`, optional
        """
        abort_values = {True: 2, False: 1}
        abort = strict_discrete_set(abort, abort_values)
        abort = abort_values[abort]
        post = SamplingPostOutput.get(post).value
        self.write("MSC %d, %d" % (abort, post))
        self.check_errors()

    ######################################
    # Read out of data
    ######################################

    def read_data(self, number_of_points):
        """ Reads all data from buffer and returns Pandas DataFrame.
        Specify number of measurement points for correct splitting of
        the data list.

        :param number_of_points: Number of measurement points
        :type number_of_points: int
        :return: Measurement Data
        :rtype: pd.DataFrame
        """
        data = self.read()
        data = data.split(',')
        data = np.array(data)
        data = np.split(data, number_of_points)
        data = pd.DataFrame(data=data)
        data = data.applymap(self._data_format.format_single)
        heads = data.iloc[[0]].applymap(lambda x: ' '.join(x[1:3]))
        # channel & data_type
        heads = heads.to_numpy().tolist()  # 2D List
        heads = heads[0]  # first row
        data = data.applymap(lambda x: x[3])
        data.columns = heads
        return data

    def read_channels(self, nchannels):
        """ Reads data for 1 measurement point from the buffer. Specify number
        of measurement channels + sweep sources (depending on data
        output setting).

        :param nchannels: Number of channels which return data
        :type nchannels: int
        :return: Measurement data
        :rtype: tuple
        """
        data = self.adapter.read_bytes(self._data_format.size * nchannels)
        data = data.decode("ASCII")
        data = data.rstrip('\r,')
        # ',' if more data in buffer, '\r' if last data point
        data = data.split(',')
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


class SMU():
    """ Provides specific methods for the SMUs of the Agilent B1500 mainframe

    :param parent: Instance of the B1500 mainframe class
    :type parent: :class:`.AgilentB1500`
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
            ['HRSMU', 'MPSMU', 'HPSMU', 'MCSMU', 'HCSMU',
             'DHCSMU', 'HVSMU', 'UHCU', 'HVMCU', 'UHVU'])
        self.voltage_ranging = SMUVoltageRanging(smu_type)
        self.current_ranging = SMUCurrentRanging(smu_type)
        self.name = name

    ##########################################
    # Wrappers of B1500 communication methods
    ##########################################
    def write(self, string):
        """Wraps :meth:`.Instrument.write` method of B1500.
        """
        self._b1500.write(string)

    def ask(self, string):
        """Wraps :meth:`~.Instrument.ask` method of B1500.
        """
        return self._b1500.ask(string)

    def query_learn(self, query_type, command):
        """Wraps :meth:`~.AgilentB1500.query_learn` method of B1500.
        """
        response = self._b1500.query_learn(query_type)
        # query_learn returns settings of all smus
        # pick setting for this smu only
        response = response[command + str(self.channel)]
        return response

    def check_errors(self):
        """Wraps :meth:`~.AgilentB1500.check_errors` method of B1500.
        """
        return self._b1500.check_errors()
    ##########################################

    def _query_status_raw(self):
        return self._b1500.query_learn(str(self.channel))

    @property
    def status(self):
        """Query status of the SMU."""
        return self._b1500.query_learn_header(str(self.channel))

    def enable(self):
        """ Enable Source/Measurement Channel (``CN``)"""
        self.write("CN %d" % self.channel)

    def disable(self):
        """ Disable Source/Measurement Channel (``CL``)"""
        self.write("CL %d" % self.channel)

    def force_gnd(self):
        """ Force 0V immediately. Current Settings can be restored with
        ``RZ`` (not implemented). (``DZ``)"""
        self.write("DZ %d" % self.channel)

    @property
    def filter(self):
        """ Enables/Disables SMU Filter. (``FL``)

        :type: bool
        """
        # different than other SMU specific settings (grouped by setting)
        # read via raw command
        response = self._b1500.query_learn(30)
        if 'FL' in response.keys():
            # only present if filters of all channels are off
            return False
        else:
            if str(self.channel) in response['FL0']:
                return False
            elif str(self.channel) in response['FL1']:
                return True
            else:
                raise NotImplementedError('Filter Value cannot be read!')

    @filter.setter
    def filter(self, setting):
        setting = strict_discrete_set(int(setting), (0, 1))
        self.write("FL %d, %d" % (setting, self.channel))
        self.check_errors()

    @property
    def series_resistor(self):
        """ Enables/Disables 1MOhm series resistor. (``SSR``)

        :type: bool
        """
        response = self.query_learn(53, 'SSR')
        response = bool(int(response))
        return response

    @series_resistor.setter
    def series_resistor(self, setting):
        setting = strict_discrete_set(int(setting), (0, 1))
        self.write("SSR %d, %d" % (self.channel, setting))
        self.check_errors()

    @property
    def meas_op_mode(self):
        """ Set SMU measurement operation mode. (``CMM``)

        :type: :class:`.MeasOpMode`
        """
        response = self.query_learn(46, 'CMM')
        response = int(response)
        return MeasOpMode(response)

    @meas_op_mode.setter
    def meas_op_mode(self, op_mode):
        op_mode = MeasOpMode.get(op_mode)
        self.write("CMM %d, %d" % (self.channel, op_mode.value))
        self.check_errors()

    @property
    def adc_type(self):
        """ADC type of individual measurement channel. (``AAD``)

        :type: :class:`.ADCType`
        """
        response = self.query_learn(55, 'AAD')
        response = int(response)
        return ADCType(response)

    @adc_type.setter
    def adc_type(self, adc_type):
        adc_type = ADCType.get(adc_type)
        self.write("AAD %d, %d" % (self.channel, adc_type.value))
        self.check_errors()

    ######################################
    # Force Constant Output
    ######################################
    def force(self, source_type, source_range, output, comp='',
              comp_polarity='', comp_range=''):
        """ Applies DC Current or Voltage from SMU immediately.
        (``DI``, ``DV``)

        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param source_range: Output range index or name
        :type source_range: int or str
        :param output: Source output value in A or V
        :type outout: float
        :param comp: Compliance value, defaults to previous setting
        :type comp: float, optional
        :param comp_polarity: Compliance polairty, defaults to auto
        :type comp_polarity: :class:`.CompliancePolarity`
        :param comp_range: Compliance ranging type, defaults to auto
        :type comp_range: int or str, optional
        """
        if source_type.upper() == "VOLTAGE":
            cmd = "DV"
            source_range = self.voltage_ranging.output(source_range).index
            if not comp_range == '':
                comp_range = self.current_ranging.meas(comp_range).index
        elif source_type.upper() == "CURRENT":
            cmd = "DI"
            source_range = self.current_ranging.output(source_range).index
            if not comp_range == '':
                comp_range = self.voltage_ranging.meas(comp_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")
        cmd += " %d, %d, %g" % (self.channel, source_range, output)
        if not comp == '':
            cmd += ", %g" % comp
            if not comp_polarity == '':
                comp_polarity = CompliancePolarity.get(comp_polarity).value
                cmd += ", %d" % comp_polarity
                if not comp_range == '':
                    cmd += ", %d" % comp_range
        self.write(cmd)
        self.check_errors()

    def ramp_source(self, source_type, source_range, target_output, comp='',
                    comp_polarity='', comp_range='',
                    stepsize=0.001, pause=20e-3):
        """ Ramps to a target output from the set value with a given
        step size, each separated by a pause.

        :param source_type: Source type (``'Voltage'`` or ``'Current'``)
        :type source_type: str
        :param target_output: Target output voltage or current
        :type: target_output: float
        :param irange: Output range index
        :type irange: int
        :param comp: Compliance, defaults to previous setting
        :type comp: float, optional
        :param comp_polarity: Compliance polairty, defaults to auto
        :type comp_polarity: :class:`.CompliancePolarity`
        :param comp_range: Compliance ranging type, defaults to auto
        :type comp_range: int or str, optional
        :param stepsize: Maximum size of steps
        :param pause: Duration in seconds to wait between steps
        """
        if source_type.upper() == "VOLTAGE":
            source_type = 'VOLTAGE'
            cmd = 'DV%d' % self.channel
            source_range = self.voltage_ranging.output(source_range).index
            unit = 'V'
            if not comp_range == '':
                comp_range = self.current_ranging.meas(comp_range).index
        elif source_type.upper() == "CURRENT":
            source_type = 'CURRENT'
            cmd = 'DI%d' % self.channel
            source_range = self.current_ranging.output(source_range).index
            unit = 'A'
            if not comp_range == '':
                comp_range = self.voltage_ranging.meas(comp_range).index
        else:
            raise ValueError("Source Type must be Current or Voltage.")

        status = self._query_status_raw()
        if 'CL' in status:  # SMU is OFF
            start = 0
        elif cmd in status:
            start = float(status[cmd][1])  # current output value
        else:
            log.info(
                ("{} in different state. "
                 "Changing to {} Source.").format(self.name, source_type))
            start = 0

        # calculate number of points based on maximum stepsize
        nop = np.ceil(abs((target_output - start) / stepsize))
        nop = int(nop)
        log.info("{0} ramping from {1}{2} to {3}{2} in {4} steps".format(
            self.name, start, unit, target_output, nop
        ))
        outputs = np.linspace(start, target_output, nop, endpoint=False)

        for output in outputs:
            # loop is only executed if target_output != start
            self.force(
                source_type, source_range, output,
                comp, comp_polarity, comp_range)
            time.sleep(pause)
        # call force even if start==target_output
        # to set compliance
        self.force(
            source_type, source_range, target_output,
            comp, comp_polarity, comp_range)

    ######################################
    # Measurement Range
    # implemented: RI, RV
    # not implemented: RC, TI, TTI, TV, TTV, TIV, TTIV, TC, TTC
    ######################################

    @property
    def meas_range_current(self):
        """ Current measurement range index. (``RI``)

        Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging:
        :class:`.SMUCurrentRanging`
        """
        response = self.query_learn(32, 'RI')
        response = self.current_ranging.meas(response)
        return response

    @meas_range_current.setter
    def meas_range_current(self, meas_range):
        meas_range_index = self.current_ranging.meas(meas_range).index
        self.write("RI %d, %d" % (self.channel, meas_range_index))
        self.check_errors()

    @property
    def meas_range_voltage(self):
        """ Voltage measurement range index. (``RV``)

        Possible settings depend on SMU type, e.g. ``0`` for Auto Ranging:
        :class:`.SMUVoltageRanging`
        """
        response = self.query_learn(32, 'RV')
        response = self.voltage_ranging.meas(response)
        return response

    @meas_range_voltage.setter
    def meas_range_voltage(self, meas_range):
        meas_range_index = self.voltage_ranging.meas(meas_range).index
        self.write("RV %d, %d" % (self.channel, meas_range_index))
        self.check_errors()

    def meas_range_current_auto(self, mode, rate=50):
        """ Specifies the auto range operation. Check Documentation. (``RM``)

        :param mode: Range changing operation mode
        :type mode: int
        :param rate: Parameter used to calculate the *current* value,
                     defaults to 50
        :type rate: int, optional
        """
        mode = strict_range(mode, range(1, 4))
        if mode == 1:
            self.write("RM %d, %d" % (self.channel, mode))
        else:
            self.write("RM %d, %d, %d" % (self.channel, mode, rate))
        self.write

    ######################################
    # Staircase Sweep Measurement: (WT, WM -> Instrument)
    # implemented:
    #   WV, WI,
    #   WSI, WSV (synchronous output)
    # not implemented: BSSI, BSSV, LSSI, LSSV
    ######################################

    def staircase_sweep_source(self, source_type, mode, source_range,
                               start, stop, steps, comp, Pcomp=''):
        """ Specifies Staircase Sweep Source (Current or Voltage) and
        its parameters. (``WV`` or ``WI``)

        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param mode: Sweep mode
        :type mode: :class:`.SweepMode`
        :param source_range: Source range index
        :type source_range: int
        :param start: Sweep start value
        :type start: float
        :param stop: Sweep stop value
        :type stop: float
        :param steps: Number of sweep steps
        :type steps: int
        :param comp: Compliance value
        :type comp: float
        :param Pcomp: Power compliance, defaults to not set
        :type Pcomp: float, optional
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
                raise ValueError(
                    "For Log Sweep Start and Stop Values must "
                    "have the same polarity."
                )
        steps = strict_range(steps, range(1, 10002))
        # check on comp value not yet implemented
        cmd += ("%d, %d, %d, %g, %g, %g, %g" %
                (self.channel, mode, source_range, start, stop, steps, comp))
        if not Pcomp == '':
            cmd += ", %g" % Pcomp
        self.write(cmd)
        self.check_errors()

    # Synchronous Output: WSI, WSV, BSSI, BSSV, LSSI, LSSV

    def synchronous_sweep_source(self, source_type, source_range,
                                 start, stop, comp, Pcomp=''):
        """ Specifies Synchronous Staircase Sweep Source (Current or Voltage)
        and its parameters. (``WSV`` or ``WSI``)

        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param source_range: Source range index
        :type source_range: int
        :param start: Sweep start value
        :type start: float
        :param stop: Sweep stop value
        :type stop: float
        :param comp: Compliance value
        :type comp: float
        :param Pcomp: Power compliance, defaults to not set
        :type Pcomp: float, optional
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
        cmd += ("%d, %d, %g, %g, %g" %
                (self.channel, source_range, start, stop, comp))
        if not Pcomp == '':
            cmd += ", %g" % Pcomp
        self.write(cmd)
        self.check_errors()

    ######################################
    # Sampling Measurements: (ML, MT -> Instrument)
    # implemented: MV, MI
    # not implemented: MSP, MCC, MSC
    ######################################

    def sampling_source(self, source_type, source_range, base, bias, comp):
        """ Sets DC Source (Current or Voltage) for sampling measurement.
        DV/DI commands on the same channel overwrite this setting.
        (``MV`` or ``MI``)

        :param source_type: Source type (``'Voltage','Current'``)
        :type source_type: str
        :param source_range: Source range index
        :type source_range: int
        :param base: Base voltage/current
        :type base: float
        :param bias: Bias voltage/current
        :type bias: float
        :param comp: Compliance value
        :type comp: float
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
        cmd += ("%d, %d, %g, %g, %g" %
                (self.channel, source_range, base, bias, comp))
        self.write(cmd)
        self.check_errors()

###############################################################################
# Additional Classes / Constants
###############################################################################


class Ranging():
    """Possible Settings for SMU Current/Voltage Output/Measurement ranges.
    Transformation of available Voltage/Current Range Names to Index and back.

    :param supported_ranges: Ranges which are supported (list of range indizes)
    :type supported_ranges: list
    :param ranges: All range names ``{Name: Indizes}``
    :type ranges: dict
    :param fixed_ranges: add fixed ranges (negative indizes); defaults to False
    :type inverse_ranges: bool, optional

    .. automethod:: __call__
    """

    _Range = namedtuple('Range', 'name index')

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
        inverse_ranges = {0: 'Auto Ranging'}
        for key, value in ranges.items():
            if isinstance(value, tuple):
                for v in value:
                    inverse_ranges[v] = (key + ' limited auto ranging', key)
                    inverse_ranges[-v] = (key + ' range fixed')
            else:
                inverse_ranges[value] = (key + ' limited auto ranging', key)
                inverse_ranges[-value] = (key + ' range fixed')

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
        """Gives named tuple (name/index) of given Range.
        Throws error if range is not supported by this SMU.

        :param input: Range name or index
        :type input: str or int
        :return: named tuple (name/index) of range
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
                    ('Specified Range Name {} is not valid or '
                     'not supported by this SMU').format(input_value.upper()))
        # get name
        try:
            name = self.ranges[index]
        except Exception:
            raise ValueError(
                ('Specified Range {} is not supported '
                 'by this SMU').format(index))
        return self._Range(name=name, index=index)


class SMUVoltageRanging():
    """ Provides Range Name/Index transformation for voltage
    measurement/sourcing.
    Validity of ranges is checked against the type of the SMU.

    Omitting the 'limited auto ranging'/'range fixed' specification in
    the range string for voltage measurement defaults to
    'limited auto ranging'.

    Full specification: '2 V range fixed' or '2 V limited auto ranging'

    '2 V' defaults to '2 V limited auto ranging'
    """

    def __init__(self, smu_type):
        supported_ranges = {
            'HRSMU': [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
            'MPSMU': [0, 5, 11, 20, 50, 12, 200, 13, 400, 14, 1000],
            'HPSMU': [0, 11, 20, 12, 200, 13, 400, 14, 1000, 15, 2000],
            'MCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
            'HCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
            'DHCSMU': [0, 2, 11, 20, 12, 200, 13, 400],
            'HVSMU': [0, 15, 2000, 5000, 15000, 30000],
            'UHCU': [0, 14, 1000],
            'HVMCU': [0, 15000, 30000],
            'UHVU': [0, 103]
        }
        supported_ranges = supported_ranges[smu_type]

        ranges = {
            '0.2 V': 2,
            '0.5 V': 5,
            '2 V': (11, 20),
            '5 V': 50,
            '20 V': (12, 200),
            '40 V': (13, 400),
            '100 V': (14, 1000),
            '200 V': (15, 2000),
            '500 V': 5000,
            '1500 V': 15000,
            '3000 V': 30000,
            '10 kV': 103
        }

        # set range attributes
        self.output = Ranging(supported_ranges, ranges)
        self.meas = Ranging(supported_ranges, ranges,
                            fixed_ranges=True)


class SMUCurrentRanging():
    """ Provides Range Name/Index transformation for current
    measurement/sourcing.
    Validity of ranges is checked against the type of the SMU.

    Omitting the 'limited auto ranging'/'range fixed' specification in
    the range string for current measurement defaults to
    'limited auto ranging'.

    Full specification: '1 nA range fixed' or '1 nA limited auto ranging'

    '1 nA' defaults to '1 nA limited auto ranging'
    """

    def __init__(self, smu_type):
        supported_output_ranges = {
            # in combination with ASU also 8
            'HRSMU': [0, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            # in combination with ASU also 8,9,10
            'MPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19],
            'HPSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20],
            'MCSMU': [0, 15, 16, 17, 18, 19, 20],
            'HCSMU': [0, 15, 16, 17, 18, 19, 20, 22],
            'DHCSMU': [0, 15, 16, 17, 18, 19, 20, 21, 23],
            'HVSMU': [0, 11, 12, 13, 14, 15, 16, 17, 18],
            'UHCU': [0, 26, 28],
            'HVMCU': [],
            'UHVU': []
        }
        supported_meas_ranges = {
            **supported_output_ranges,
            # overwrite output ranges:
            'HVMCU': [0, 19, 21],
            'UHVU': [0, 15, 16, 17, 18, 19]
        }
        supported_output_ranges = supported_output_ranges[smu_type]
        supported_meas_ranges = supported_meas_ranges[smu_type]

        ranges = {
            '1 pA': 8,  # for ASU
            '10 pA': 9,
            '100 pA': 10,
            '1 nA': 11,
            '10 nA': 12,
            '100 nA': 13,
            '1 uA': 14,
            '10 uA': 15,
            '100 uA': 16,
            '1 mA': 17,
            '10 mA': 18,
            '100 mA': 19,
            '1 A': 20,
            '2 A': 21,
            '20 A': 22,
            '40 A': 23,
            '500 A': 26,
            '2000 A': 28
        }

        # set range attributes
        self.output = Ranging(supported_output_ranges, ranges)
        self.meas = Ranging(supported_meas_ranges, ranges,
                            fixed_ranges=True)


class CustomIntEnum(IntEnum):
    """Provides additional methods to IntEnum:

    * Conversion to string automatically replaces '_' with ' ' in names
      and converts to title case

    * get classmethod to get enum reference with name or integer

    .. automethod:: __str__
    """

    def __str__(self):
        """Gives title case string of enum value
        """
        return str(self.name).replace("_", " ").title()
        # str() conversion just because of pylint bug

    @classmethod
    def get(cls, input_value):
        """Gives Enum member by specifying name or value.

        :param input_value: Enum name or value
        :type input_value: str or int
        :return: Enum member
        """
        if isinstance(input_value, int):
            return cls(input_value)
        else:
            return cls[input_value.upper()]


class ADCType(CustomIntEnum):
    """ADC Type"""
    HSADC = 0,  #: High-speed ADC
    HRADC = 1,  #: High-resolution ADC
    HSADC_PULSED = 2,  #: High-resolution ADC for pulsed measurements

    def __str__(self):
        return str(self.name).replace("_", " ")
        # .title() str() conversion just because of pylint bug


class ADCMode(CustomIntEnum):
    """ADC Mode"""
    AUTO = 0  #:
    MANUAL = 1  #:
    PLC = 2  #:
    TIME = 3  #:


class AutoManual(CustomIntEnum):
    """Auto/Manual selection"""
    AUTO = 0  #:
    MANUAL = 1  #:


class MeasMode(CustomIntEnum):
    """Measurement Mode"""
    SPOT = 1  #:
    STAIRCASE_SWEEP = 2  #:
    SAMPLING = 10  #:


class MeasOpMode(CustomIntEnum):
    """Measurement Operation Mode"""
    COMPLIANCE_SIDE = 0  #:
    CURRENT = 1  #:
    VOLTAGE = 2  #:
    FORCE_SIDE = 3  #:
    COMPLIANCE_AND_FORCE_SIDE = 4  #:


class SweepMode(CustomIntEnum):
    """Sweep Mode"""
    LINEAR_SINGLE = 1  #:
    LOG_SINGLE = 2  #:
    LINEAR_DOUBLE = 3  #:
    LOG_DOUBLE = 4  #:


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
            2: "Log 10 data/decade", 3: "Log 25 data/decade",
            4: "Log 50 data/decade", 5: "Log 100 data/decade",
            6: "Log 250 data/decade", 7: "Log 5000 data/decade"}
        return names[self.value]


class SamplingPostOutput(CustomIntEnum):
    """Output after sampling"""
    BASE = 1  #:
    BIAS = 2  #:


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
    SMU_SOURCE = 1  #:
    SMU_MEASUREMENT = 2  #:
    CMU_MEASUREMENT = 3  #:

###############################################################################
# Query Learn: Parse Instrument settings into human readable format
###############################################################################


class QueryLearn():
    """Methods to issue and process ``*LRN?`` (learn) command and response."""

    @staticmethod
    def query_learn(ask, query_type):
        """ Issues ``*LRN?`` (learn) command to the instrument to read
        configuration.
        Returns dictionary of commands and set values.

        :param query_type: Query type according to the programming guide
        :type query_type: int
        :return: Dictionary of command and set values
        :rtype: dict
        """
        response = ask("*LRN? " + str(query_type))
        # response.split(';')
        response = re.findall(
            r'(?P<command>[A-Z]+)(?P<parameter>[0-9,\+\-\.E]+)',
            response)
        # check if commands are unique -> suitable as keys for dict
        counts = Counter([item[0] for item in response])
        # responses that start with a channel number
        # the channel number should always be included in the key
        include_chnum = [
            'DI', 'DV',  # Sourcing
            'RI', 'RV',  # Ranging
            'WV', 'WI', 'WSV', 'WSI',  # Staircase Sweep
            'PV', 'PI', 'PWV', 'PWI',  # Pulsed Source
            'MV', 'MI', 'MSP',  # Sampling
            'SSR', 'RM', 'AAD'  # Series Resistor, Auto Ranging, ADC
        ]  # probably not complete yet...
        response_dict = {}
        for element in response:
            parameters = element[1].split(',')
            name = element[0]
            if (counts[name] > 1) or (name in include_chnum):
                # append channel (first parameter) to command as dict key
                name += parameters[0]
                parameters = parameters[1:]
            if len(parameters) == 1:
                parameters = parameters[0]
            # skip second AAD entry for each channel -> contains no information
            if 'AAD' in name and name in response_dict.keys():
                continue
            response_dict[name] = parameters
        return response_dict

    @classmethod
    def query_learn_header(cls, ask, query_type, smu_references,
                           single_command=False):
        """Issues ``*LRN?`` (learn) command to the instrument to
        read configuration.
        Processes information to human readable values for debugging
        purposes or file headers.

        :param ask: ask method of the instrument
        :type ask: Instrument.ask
        :param query_type: Number according to Programming Guide
        :type query_type: int or str
        :param smu_references: SMU references by channel
        :type smu_references: dict
        :param single_command: if only a single command should be returned,
                               defaults to False
        :type single_command: str
        :return: Read configuration
        :rtype: dict
        """
        response = cls.query_learn(ask, query_type)
        if single_command is not False:
            response = response[single_command]
        ret = {}
        for key, value in response.items():
            # command without channel
            command = re.findall(r'(?P<command>[A-Z]+)', key)[0]
            new_dict = getattr(cls, command)(
                key, value, smu_references=smu_references)
            ret = {**ret, **new_dict}
        return ret

    @staticmethod
    def to_dict(parameters, names, *args):
        """ Takes parameters returned by :meth:`query_learn` and ordered list
        of corresponding parameter names (optional function) and returns
        dict of parameters including names.

        :param parameters: Parameters for one command returned
                           by :meth:`query_learn`
        :type parameters: dict
        :param names: list of names or (name, function) tuples, ordered
        :type names: list
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
        command = re.findall(r'(?P<command>[A-Z]+)', key)[0]
        channel = key[len(command):]
        return smu_references[int(channel)]

    # SMU Modes
    @classmethod
    def DI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ('Current Range',
                lambda parameter:
                smu.current_ranging.output(int(parameter)).name),
            'Current Output (A)', 'Compliance Voltage (V)',
            ('Compliance Polarity',
                lambda parameter: str(CompliancePolarity.get(int(parameter)))),
            ('Voltage Compliance Ranging Type',
                lambda parameter:
                smu.voltage_ranging.meas(int(parameter)).name)
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Constant Current'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def DV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ('Voltage Range',
                lambda parameter:
                smu.voltage_ranging.output(int(parameter)).name),
            'Voltage Output (V)', 'Compliance Current (A)',
            ('Compliance Polarity',
                lambda parameter: str(CompliancePolarity.get(int(parameter)))),
            ('Current Compliance Ranging Type',
                lambda parameter:
                smu.current_ranging.meas(int(parameter)).name)
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Constant Voltage'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def CL(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key + parameters, smu_references)
        return {smu.name: 'OFF'}

    # Instrument Settings: 31
    @classmethod
    def TM(cls, key, parameters, smu_references={}):
        names = ['Trigger Mode']  # enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def AV(cls, key, parameters, smu_references={}):
        names = [
            'ADC Averaging Number',
            ('ADC Averaging Mode',
                lambda parameter: str(AutoManual(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def CM(cls, key, parameters, smu_references={}):
        names = [
            ('Auto Calibration Mode',
                lambda parameter: bool(int(parameter)))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def FMT(cls, key, parameters, smu_references={}):
        names = ['Output Data Format', 'Output Data Mode']
        # enum + setting not implemented yet
        return cls.to_dict(parameters, names)

    @classmethod
    def MM(cls, key, parameters, smu_references={}):
        names = [
            ('Measurement Mode',
                lambda parameter: str(MeasMode(int(parameter))))
        ]
        ret = cls.to_dict(parameters[0], names)
        smu_names = []
        for channel in parameters[1:]:
            smu_names.append(smu_references[int(channel)].name)
        ret['Measurement Channels'] = ', '.join(smu_names)
        return ret

    # Measurement Ranging: 32
    @classmethod
    def RI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (smu.name + ' Current Measurement Range',
                lambda parameter:
                smu.current_ranging.meas(int(parameter)).name)
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def RV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (smu.name + ' Voltage Measurement Range',
                lambda parameter:
                smu.voltage_ranging.meas(int(parameter)).name)
        ]
        return cls.to_dict(parameters, names)

    # Sweep: 33
    @classmethod
    def WM(cls, key, parameters, smu_references={}):
        names = [
            ('Auto Abort Status',
                lambda parameter:
                {2: True, 1: False}[int(parameter)]),
            ('Output after Measurement',
                lambda parameter:
                str(StaircaseSweepPostOutput(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def WT(cls, key, parameters, smu_references={}):
        names = [
            'Hold Time (s)', 'Delay Time (s)', 'Step Delay Time (s)',
            'Step Source Trigger Delay Time (s)',
            'Step Measurement Trigger Delay Time (s)'
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def WV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Sweep Mode",
                lambda parameter: str(SweepMode(int(parameter)))),
            ("Voltage Range",
                lambda parameter:
                smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)", "Stop Voltage (V)", "Number of Steps",
            "Current Compliance (A)", "Power Compliance (W)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Voltage Sweep Source'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Sweep Mode", lambda parameter: str(SweepMode(int(parameter)))),
            ("Current Range",
                lambda parameter:
                smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)", "Stop Current (A)", "Number of Steps",
            "Voltage Compliance (V)", "Power Compliance (W)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Current Sweep Source'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WSV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Voltage Range",
                lambda parameter:
                smu.voltage_ranging.output(int(parameter)).name),
            "Start Voltage (V)", "Stop Voltage (V)",
            "Current Compliance (A)", "Power Compliance (W)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Synchronous Voltage Sweep Source'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def WSI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Current Range",
                lambda parameter:
                smu.current_ranging.output(int(parameter)).name),
            "Start Current (A)", "Stop Current (A)",
            "Voltage Compliance (V)", "Power Compliance (W)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Synchronous Current Sweep Source'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    # SMU Measurement Operation Mode: 46
    @classmethod
    def CMM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (smu.name + ' Measurement Operation Mode',
                lambda parameter:
                str(MeasOpMode(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    # Sampling: 47
    @classmethod
    def MSC(cls, key, parameters, smu_references={}):
        names = [
            ('Auto Abort Status',
                lambda parameter:
                {2: True, 1: False}[int(parameter)]),
            ('Output after Measurement',
                lambda parameter:
                str(SamplingPostOutput(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def MT(cls, key, parameters, smu_references={}):
        names = [
            'Hold Bias Time (s)', 'Sampling Interval (s)',
            'Number of Samples', 'Hold Base Time (s)'
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def ML(cls, key, parameters, smu_references={}):
        names = [
            ('Sampling Mode',
                lambda parameter: str(SamplingMode(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def MV(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Voltage Range",
                lambda parameter:
                smu.voltage_ranging.output(int(parameter)).name),
            "Base Voltage (V)", "Bias Voltage (V)",
            "Current Compliance (A)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Voltage Source Sampling'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    @classmethod
    def MI(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            ("Current Range",
                lambda parameter:
                smu.current_ranging.output(int(parameter)).name),
            "Base Current (A)", "Bias Current (A)",
            "Voltage Compliance (V)"
        ]
        ret = cls.to_dict(parameters, names)
        ret['Source Type'] = 'Current Source Sampling'
        ret.move_to_end('Source Type', last=False)  # make first entry
        return {smu.name: ret}

    # SMU Series Resistor: 53
    @classmethod
    def SSR(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (smu.name + ' Series Resistor',
                lambda parameter: bool(int(parameter)))
        ]
        return cls.to_dict(parameters, names)

    # Auto Ranging Mode: 54
    @classmethod
    def RM(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            smu.name + ' Ranging Mode',
            smu.name + ' Ranging Mode Parameter'
        ]
        return cls.to_dict(parameters, names)

    # ADC: 55, 56
    @classmethod
    def AAD(cls, key, parameters, smu_references={}):
        smu = cls._get_smu(key, smu_references)
        names = [
            (smu.name + ' ADC',
                lambda parameter:
                str(ADCType(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def AIT(cls, key, parameters, smu_references={}):
        adc_type = key[3:]
        adc_name = str(ADCType(int(adc_type)))
        names = [
            (adc_name + ' Mode',
                lambda parameter:
                str(ADCMode(int(parameter)))),
            adc_name + ' Parameter'
        ]
        return cls.to_dict(parameters, names)

    @classmethod
    def AZ(cls, key, parameters, smu_references={}):
        names = [
            ('ADC Auto Zero',
                lambda parameter: str(bool(int(parameter))))
        ]
        return cls.to_dict(parameters, names)

    # Time Stamp: 60
    @classmethod
    def TSC(cls, key, parameters, smu_references={}):
        names = [
            ('Time Stamp',
                lambda parameter: str(bool(int(parameter))))
        ]
        return cls.to_dict(parameters, names)
