#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2017 PyMeasure Developers
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
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

from pymeasure.instruments import (Instrument,
                                   RangeException)
from pymeasure.instruments.validators import (strict_discrete_set,
                                              truncated_discrete_set,
                                              strict_range)
import numpy as np
import time
import pandas as pd
import os
import json

######
# MAIN
######


class Agilent4156(Instrument):
    """ Represents the Agilent 4155/4156 Semiconductor Parameter Analyzer
    and provides a high-level interface for taking I-V measurements.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )

        self.smu1 = smu(self.adapter, 'SMU1', **kwargs)
        self.smu2 = smu(self.adapter, 'SMU2', **kwargs)
        self.smu3 = smu(self.adapter, 'SMU3', **kwargs)
        self.smu4 = smu(self.adapter, 'SMU4', **kwargs)
        self.vmu1 = vmu(self.adapter, 'VMU1', **kwargs)
        self.vmu2 = vmu(self.adapter, 'VMU2', **kwargs)
        self.vsu1 = vsu(self.adapter, 'VSU1', **kwargs)
        self.vsu2 = vsu(self.adapter, 'VSU2', **kwargs)
        self.var1 = var1(self.adapter, **kwargs)
        self.var2 = var2(self.adapter, **kwargs)
        self.vard = vard(self.adapter, **kwargs)

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'SWEEP' or 'SAMPLING'.
        """,
        validator=strict_discrete_set,
        values={'SWEEP': 'SWE', 'SAMPLING': 'SAMP'},
        map_values=True,
        check_set_errors=True,
        check_get_errors=True
    )

    integration_time = Instrument.control(
        ":PAGE:MEAS:MSET:ITIM?", ":PAGE:MEAS:MSET:ITIM %s",
        """ A string property that controls the integration time,
        which can take the values 'SHORT', 'MEDIUM' or 'LONG'.
        """,
        validator=strict_discrete_set,
        values={'SHORT': 'SHOR', 'MEDIUM': 'MED', 'LONG': 'LONG'},
        map_values=True,
        check_set_errors=True,
        check_get_errors=True
    )

    delay_time = Instrument.control(
        ":PAGE:MEAS:DEL?", ":PAGE:MEAS:DEL %g",
        """ A floating point property that measurement delay time in seconds,
        which can take the values from 0 to 65s in 0.1s steps.
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 65.1, 0.1),
        check_set_errors=True,
        check_get_errors=True
    )

    hold_time = Instrument.control(
        ":PAGE:MEAS:HTIME?", ":PAGE:MEAS:HTIME %g",
        """ A floating point property that measurement hold time in seconds,
        which can take the values from 0 to 655s in 1s steps.
        """,
        validator=truncated_discrete_set,
        values=np.arange(0, 655, 1),
        check_set_errors=True,
        check_get_errors=True
    )

    def stop(self):
        """Stops the ongoing measurement"""
        self.write(":PAGE:SCON:STOP")

    def measure(self):
        """
        Performs a single measurement and waits for completion in sweep mode.
        In sampling mode:
            - the measurement must be stopped using :method:~`stop`.
            - the instrument is hardcoded to capture 25 data points.
        """
        if self.analyzer_mode == 'SWE':
            self.write(":PAGE:SCON:MEAS:SING")
            self.write("*WAI")

        else:
            self.write(":PAGE:MEAS:SAMP:PER INF")
            self.write(":PAGE:MEAS:SAMP:POIN 25")
            self.write(":PAGE:SCON:MEAS:SING")

    def disable_all(self):
        """ Disables all channels in the instrument
        """
        self.smu1.disable
        time.sleep(0.1)
        self.smu2.disable
        time.sleep(0.1)
        self.smu3.disable
        time.sleep(0.1)
        self.smu4.disable
        time.sleep(0.1)
        self.vmu1.disable
        time.sleep(0.1)
        self.vmu2.disable
        time.sleep(0.1)

    def configure(self, settings_dict, use_json=False):
        """ Convenience function to configure the channel setup and sweep.
        :param settings_dict: A dictionary of {Instrument object : config_dict}
        where the instrument object addresses the particular SMU or sweep
        variable, and the config_dict is a dictionary containing the properties
        of the instrument object as keys with their corresponding value setting
        as dictionary values.

        Alternately, settings_dict can be a json configuration file.

        Manually creating dictionary of instrument settings.
        .. code-block:: python
            # configure settings and sweeps
            smu1_setup = {'channel_mode' : 'V',
                          'channel_function' : 'VAR1',
                          'voltage_name' : 'VC',
                          'current_name' : 'IC',
                          'series_resistance' : '0OHM'
                         }

            smu1_sweep = {'start' : 1,
                          'stop' : 2,
                          'step' : 0.1,
                          'spacing' : 'LINEAR',
                          'compliance' : 0.1
                          }

            smu2_setup = {'channel_mode' : 'I',
                          'channel_function' : 'VAR2',
                          'voltage_name' : 'VB',
                          'current_name' : 'IB',
                          'series_resistance' : '0OHM'
                          }

            smu2_sweep = {'start' : 0,
                          'step' : 10e-6,
                          'points' : 3,
                          'compliance' : 0.1
                          }

            smu3_setup = {'channel_mode' : 'V',
                          'channel_function' : 'CONS',
                          'constant_value' : 0,
                          'voltage_name' : 'VE',
                          'current_name' : 'IE',
                          'compliance' : 0.1
                          }

            # create settings dictionary
            all_settings = {instr.smu1 : smu1_setup,
                        instr.var1 : smu1_sweep,
                        instr.smu2 : smu2_setup,
                        instr.var2 : smu2_sweep,
                        instr.smu3 : smu3_setup,
                        instr.smu4 : smu4_setup
                        }

            instr.configure(all_settings)

        Example JSON file for the same setup:
        .. code-block:: json
            {
                "SMU1": {
                    "voltage_name" : "VC",
                    "current_name" : "IC",
                    "channel_function" : "VAR1",
                    "channel_mode" : "V",
                    "series_resistance" : "0OHM"
                },
                "VAR1": {
                    "start" : 1,
                    "stop" : 2,
                    "step" : 0.1,
                    "spacing" : "LINEAR",
                    "compliance" : 0.5
                },
                "SMU2": {
                    "voltage_name" : "VB",
                    "current_name" : "IB",
                    "channel_function" : "VAR2",
                    "channel_mode" : "I",
                    "series_resistance" : "0OHM"
                },
                "VAR2": {
                    "start" : 0,
                    "step" : 10e-6,
                    "points" : 3,
                    "compliance" : 0.1
                },
                "SMU3": {
                    "voltage_name" : "VE",
                    "current_name" : "IE",
                    "channel_function" : "CONS",
                    "channel_mode" : "V",
                    "constant_value" : 0,
                    "compliance" : 0.1
                }
            }

        The instrument can then be configured using,
        .. code-block:: python
            instr.configure('config.yaml', use_yaml=True)
        """
        self.disable_all()
        obj_dict = {'SMU1': self.smu1,
                    'SMU2': self.smu2,
                    'SMU3': self.smu3,
                    'SMU4': self.smu4,
                    'VMU1': self.vmu1,
                    'VMU2': self.vmu2,
                    'VSU1': self.vsu1,
                    'VSU2': self.vsu2,
                    'VAR1': self.var1,
                    'VAR2': self.var2,
                    'VARD': self.vard
                    }
        if use_json:
            with open(settings_dict, 'r') as stream:
                try:
                    instr_settings = json.load(stream)
                except json.JSONDecodeError as e:
                    print(e)

            # replace dict keys with Instrument objects
            new_settings_dict = {}
            for key, value in instr_settings.items():
                new_settings_dict[obj_dict[key]] = value

        else:
            new_settings_dict = settings_dict

        for obj, setup in new_settings_dict.items():
            for setting, value in setup.items():
                setattr(obj, setting, value)
                time.sleep(0.1)

    def save(self, trace_list):
        """ Save the voltage or current in the instrument display list
        """
        self.write(":PAGE:DISP:MODE LIST")
        if isinstance(trace_list, list):
            try:
                len(trace_list) > 8
            except:
                raise RuntimeError('Maximum of 8 variables allowed')
            else:
                for name in trace_list:
                    self.write(":PAGE:DISP:LIST \'{}\'".format(name))
        elif isinstance(trace_list, str):
            self.write(":PAGE:DISP:LIST \'{}\'".format(trace_list))
        else:
            raise TypeError(
                'Must be a string if only one variable is saved, or else a list if'
                'multiple variables are being saved.'
            )

    def save_var(self, trace_list):
        """ Save the voltage or current in the instrument variable list
        """
        self.write(":PAGE:DISP:MODE LIST")
        if isinstance(trace_list, list):
            try:
                len(trace_list) > 2
            except:
                raise RuntimeError('Maximum of 2 variables allowed')
            else:
                for name in trace_list:
                    self.write(":PAGE:DISP:DVAR \'{}\'".format(name))
        elif isinstance(trace_list, str):
            self.write(":PAGE:DISP:DVAR \'{}\'".format(trace_list))
        else:
            raise TypeError(
                'Must be a string if only one variable is saved, or else a list if'
                'multiple variables are being saved.'
            )

    @property
    def data_variables(self):
        """
        Gets a string list of data variables for whom measured data
        is available.
        """
        dlist = self.ask(":PAGE:DISP:LIST?").split(',')
        dvar = self.ask(":PAGE:DISP:DVAR?").split(',')
        varlist = dlist + dvar
        return list(filter(None, varlist))

    def get_data(self, path=None, to_csv=False):
        """
        Gets the measurement data from the instrument.
        :param file: File name for data export
        :param path: Path for data export. Default = None
        :param to_csv: Boolean value that enables CSV export if True.
        Default = False.
        :returns: Pandas Dataframe
        """
        if self.ask("*OPC?") == '1':
            header = self.data_variables
            self.write(":FORM:DATA ASC")
            # recursively get data for each variable
            for i, listvar in enumerate(header):
                data = self.values(":DATA? \'{}\'".format(listvar))
                time.sleep(0.01)
                if i == 0:
                    lastdata = data
                else:
                    data = np.column_stack((lastdata, data))
                    lastdata = data

            df = pd.DataFrame(data=data, columns=header, index=None)
            if to_csv:
                _, ext = os.path.splitext(path)
                if ext != ".csv":
                    path = path + ".csv"
                df.to_csv(path, index=False)
            if self.analyzer_mode == "SAMPLING":
                df_mean = pd.DataFrame(df.mean(), index=None).transpose()
                return df_mean
            else:
                return df

##########
# CHANNELS
##########


class smu(Instrument):
    def __init__(self, resourceName, channel, **kwargs):
        super().__init__(
            resourceName,
            "SMU of Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self.channel = channel.upper()

    @property
    def channel_mode(self):
        value = self.ask(":PAGE:CHAN:{}:MODE?".format(self.channel))
        self.check_errors()
        return value

    @channel_mode.setter
    def channel_mode(self, mode):
        """ A string property that controls the SMU<n> channel mode.
        :param mode: Set channel mode - 'V', 'I' or 'COMM'
        VPULSE AND IPULSE are not yet supported.
        """
        validator = strict_discrete_set
        values = ["V", "I", "COMM"]
        value = validator(mode, values)
        self.write(":PAGE:CHAN:{0}:MODE {1}".format(self.channel, value))
        self.check_errors()

    @property
    def channel_function(self):
        value = self.ask(":PAGE:CHAN:{}:FUNC?".format(self.channel))
        self.check_errors()
        return value

    @channel_function.setter
    def channel_function(self, function):
        """ A string property that controls the SMU<n> channel function.
        :param function: 'VAR1', 'VAR2', 'VARD' or 'CONS'.
        """
        validator = strict_discrete_set
        values = ["VAR1", "VAR2", "VARD", "CONS"]
        value = validator(function, values)
        self.write(":PAGE:CHAN:{0}:FUNC {1}".format(self.channel, value))
        self.check_errors()

    @property
    def series_resistance(self):
        value = self.ask(":PAGE:CHAN:{}:SRES?".format(self.channel))
        self.check_errors()
        return value

    @series_resistance.setter
    def series_resistance(self, sres):
        """ This command controls the series resistance of SMU<n>.
        :param sres: '0OHM', '10KOHM', '100KOHM', or '1MOHM'
        At *RST, this value is 0 OHM.
        """
        validator = strict_discrete_set
        values = ["0OHM", "10KOHM", "100KOHM", "1MOHM"]
        value = validator(sres, values)
        self.write(":PAGE:CHAN:{0}:SRES {1}".format(self.channel, value))
        self.check_errors()

    @property
    def disable(self):
        """ This command deletes the settings of SMU<n>."""
        self.write(":PAGE:CHAN:{}:DIS".format(self.channel))
        self.check_errors()

    @property
    def constant_value(self):
        if Agilent4156.analyzer_mode == "SWEEP":
            value = self.ask(":PAGE:MEAS:CONS:{}?".format(self.channel))
        else:
            value = self.ask(":PAGE:MEAS:SAMP:CONS:{}?".format(self.channel))
        self.check_errors()
        return value

    @constant_value.setter
    def constant_value(self, const_value):
        """ This command sets the constant source value of SMU<n> for the sweep
        measurement. You use this command only if :attr:`~channels.channel_function`
        is `CONS` and :attr:`~.channels.channel_mode` is not `COMM`.
        At *RST, this value is 0 V.
        :param const_value: Voltage in (-200V, 200V) and current in (-1A, 1A) based
        on :attr:`~.channels.channel_mode` setting.
        """
        validator = strict_range
        values = self.__validate_cons()
        value = validator(const_value, values)
        if Agilent4156.analyzer_mode == 'SWEEP':
            self.write(":PAGE:MEAS:CONS:{0} {1}".format(self.channel, value))
        else:
            self.write(":PAGE:MEAS:SAMP:CONS:{0} {1}".format(
                self.channel, value))
        self.check_errors()

    @property
    def compliance(self):
        if Agilent4156.analyzer_mode == "SWEEP":
            value = self.ask(":PAGE:MEAS:CONS:{}:COMP?".format(self.channel))
        else:
            value = self.ask(
                ":PAGE:MEAS:SAMP:CONS:{}:COMP?".format(self.channel))
        self.check_errors()
        return value

    @compliance.setter
    def compliance(self, comp):
        """ This command sets the constant COMPLIANCE value of SMU<n> for the
        sweep measurement. You use this command only if :attr:`~channels.channel_function`
        is `CONS` and :attr:`~.channels.channel_mode` is not `COMM`.
        :param comp: Voltage in (-200V, 200V) and current in (-1A, 1A) based
        on :attr:`~.channels.channel_mode` setting.
        """
        validator = strict_range
        values = self.__validate_compl()
        value = validator(comp, values)
        if Agilent4156.analyzer_mode == 'SWEEP':
            self.write(":PAGE:MEAS:CONS:{0}:COMP {1}".format(
                self.channel, value))
        else:
            self.write(":PAGE:MEAS:SAMP:CONS:{0}:COMP {1}".format(
                self.channel, value))
        self.check_errors()

    @property
    def voltage_name(self):
        value = self.ask("PAGE:CHAN:{}:VNAME?".format(self.channel))
        return value

    @voltage_name.setter
    def voltage_name(self, vname):
        """ Controls the voltage name of the channel
        :param vname: Voltage name of the channel.
        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.
        """
        value = check_current_voltage_name(vname)
        self.write(":PAGE:CHAN:{0}:VNAME \'{1}\'".format(self.channel, value))

    @property
    def current_name(self):
        value = self.ask("PAGE:CHAN:{}:INAME?".format(self.channel))
        return value

    @current_name.setter
    def current_name(self, iname):
        """ Controls the current name of the channel
        :param iname: Current name of the channel.
        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.
        """
        value = check_current_voltage_name(iname)
        self.write(":PAGE:CHAN:{0}:INAME \'{1}\'".format(self.channel, value))

    def __validate_cons(self):
        """Validates the instrument settings for operation in constant mode.
        """
        try:
            not((self.channel_mode != 'COMM') and (
                self.channel_function == 'CONS'))
        except:
            raise ValueError(
                'Cannot set constant SMU function when SMU mode is COMMON, '
                'or when SMU function is not CONSTANT.')
        else:
            if self.channel_mode == 'V':
                values = [-200, 200]
            elif self.channel_mode == 'I':
                values = [-1, 1]
            else:
                raise ValueError(
                    'Channel is not in V or I mode. It might be disabled.')
        return values

    def __validate_compl(self):
        """Validates the instrument compliance for operation in constant mode.
        """
        try:
            not((self.channel_mode != 'COMM') and (
                self.channel_function == 'CONS'))
        except:
            raise ValueError(
                'Cannot set constant SMU parameters when SMU mode is COMMON, '
                'or when SMU function is not CONSTANT.')
        else:
            if self.channel_mode == 'I':
                values = [-200, 200]
            elif self.channel_mode == 'V':
                values = [-1, 1]
            else:
                raise ValueError('Channel is not in V or I mode.')
        return values


class vmu(Instrument):
    def __init__(self, resourceName, channel, **kwargs):
        super().__init__(
            resourceName,
            "VMU of Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self.channel = channel.upper()

    @property
    def voltage_name(self):
        value = self.ask("PAGE:CHAN:{}:VNAME?".format(self.channel))
        return value

    @voltage_name.setter
    def voltage_name(self, vname):
        """ Controls the voltage name of the VMU channel
        :param vname: Voltage name of the channel.
        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.
        """
        value = check_current_voltage_name(vname)
        self.write(":PAGE:CHAN:{0}:VNAME \'{1}\'".format(self.channel, value))

    @property
    def disable(self):
        """ This command deletes the settings of VMU<n>."""
        self.write(":PAGE:CHAN:{}:DIS".format(self.channel))
        self.check_errors()

    @property
    def channel_mode(self):
        value = self.ask(":PAGE:CHAN:{}:MODE?".format(self.channel))
        self.check_errors()
        return value

    @channel_mode.setter
    def channel_mode(self, mode):
        """ A string property that controls the VMU<n> channel mode.
        :param mode: Set channel mode - 'V', 'DVOL'
        """
        validator = strict_discrete_set
        values = ["V", "DVOL"]
        value = validator(mode, values)
        self.write(":PAGE:CHAN:{0}:MODE {1}".format(self.channel, value))
        self.check_errors()


class vsu(Instrument):
    def __init__(self, resourceName, channel, **kwargs):
        super().__init__(
            resourceName,
            "VSU of Agilent 4155/4156 Semiconductor Parameter Analyzer",
            **kwargs
        )
        self.channel = channel.upper()

    @property
    def voltage_name(self):
        value = self.ask("PAGE:CHAN:{}:VNAME?".format(self.channel))
        return value

    @voltage_name.setter
    def voltage_name(self, vname):
        """ Controls the voltage name of the VMU channel
        :param vname: Voltage name of the channel.
        If input is greater than 6 characters long or starts with a number,
        the name is autocorrected and prepended with 'a'. Event is logged.
        """
        value = check_current_voltage_name(vname)
        self.write(":PAGE:CHAN:{0}:VNAME \'{1}\'".format(self.channel, value))

    @property
    def disable(self):
        """ This command deletes the settings of VMU<n>."""
        self.write(":PAGE:CHAN:{}:DIS".format(self.channel))
        self.check_errors()

    @property
    def channel_mode(self):
        value = self.ask(":PAGE:CHAN:{}:MODE?".format(self.channel))
        self.check_errors()
        return value

    @property
    def constant_value(self):
        if Agilent4156.analyzer_mode == "SWEEP":
            value = self.ask(":PAGE:MEAS:CONS:{}?".format(self.channel))
        else:
            value = self.ask(":PAGE:MEAS:SAMP:CONS:{}?".format(self.channel))
        self.check_errors()
        return value

    @constant_value.setter
    def constant_value(self, const_value):
        """ This command sets the constant source value of SMU<n> for the sweep
        measurement. You use this command only if :attr:`~channels.channel_function`
        is `CONS` and :attr:`~.channels.channel_mode` is not `COMM`.
        At *RST, this value is 0 V.
        :param const_value: Voltage in (-200V, 200V) and current in (-1A, 1A) based
        on :attr:`~.channels.channel_mode` setting.
        """
        validator = strict_range
        values = [-200, 200]
        value = validator(const_value, values)
        if Agilent4156.analyzer_mode == 'SWEEP':
            self.write(":PAGE:MEAS:CONS:{0} {1}".format(self.channel, value))
        else:
            self.write(":PAGE:MEAS:SAMP:CONS:{0} {1}".format(
                self.channel, value))
        self.check_errors()

#################
# SWEEP VARIABLES
#################


class var1(Instrument):
    """ Class to handle all the definitions needed for VAR1
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Definitions for VAR1 sweep variable.",
            **kwargs
        )

    start = Instrument.control(
        ":PAGE:MEAS:VAR1:START?",
        ":PAGE:MEAS:VAR1:START %g",
        """
        This command sets the sweep START value of VAR1.
        At *RST, this value is 0 V.
        -200 to 200 V or -1 to 1 A. The range of this value
        depends on the unit type of VAR1.
        Input is only validated for voltages.
        """,
        validator=strict_range,
        values=[-200, 200],
        check_set_errors=True,
        check_get_errors=True
    )

    stop = Instrument.control(
        ":PAGE:MEAS:VAR1:STOP?",
        ":PAGE:MEAS:VAR1:STOP %g",
        """
        This command sets the sweep STOP value of VAR1.
        At *RST, this value is 1 V.
        -200 to 200 V or -1 to 1 A. The range of this value
        depends on the unit type of VAR1.
        Input is only validated for voltages.
        """,
        validator=strict_range,
        values=[-200, 200],
        check_set_errors=True,
        check_get_errors=True
    )

    step = Instrument.control(
        ":PAGE:MEAS:VAR1:STEP?",
        ":PAGE:MEAS:VAR1:STEP %g",
        """
        This command sets the sweep STEP value of VAR1 for the linear sweep.
        This parameter is not used for logarithmic sweep.
        -400 to 400 V or -2 to 2 A. Input is only validated for voltages.
        The range of this value depends on the unit type of VAR1.
        The polarity of step value is automatically determined by the relation between start
        and stop values. So, for the step value you specify, only absolute value has meaning.
        The polarity has no meaning.
        """,
        validator=strict_range,
        values=[-400, 400],
        check_set_errors=True,
        check_get_errors=True
    )

    compliance = Instrument.control(
        ":PAGE:MEAS:VAR1:COMP?",
        ":PAGE:MEAS:VAR1:COMP %g",
        """
        This command sets the COMPLIANCE value of VAR1 in Volts/Ampsself. At *RST, this value is 100 mA.
        Only current compliance is validated in function input.
        """,
        validator=strict_range,
        values=[-1, 1],
        check_set_errors=True,
        check_get_errors=True
    )

    spacing = Instrument.control(
        ":PAGE:MEAS:VAR1:SPAC?",
        ":PAGE:MEAS:VAR1:SPAC %s",
        """
        This command selects the sweep type of VAR1: linear staircase or logarithmic
        staircase. Valid inputs are 'LINEAR', 'LOG10', 'LOG25', 'LOG50'.
        """,
        validator=strict_discrete_set,
        values={'LINEAR': 'LIN', 'LOG10': 'L10',
                'LOG25': 'L25', 'LOG50': 'L50'},
        map_values=True,
        check_set_errors=True,
        check_get_errors=True
    )


class var2(Instrument):
    """ Class to handle all the definitions needed for VAR2
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Definitions for VAR2 sweep variable.",
            **kwargs
        )

    start = Instrument.control(
        ":PAGE:MEAS:VAR2:START?",
        ":PAGE:MEAS:VAR2:START %g",
        """
        This command sets the sweep START value of VAR2.
        At *RST, this value is 0 V.
        -200 to 200 V or -1 to 1 A. The range of this value
        depends on the unit type of VAR2.
        Input is only validated for voltages.
        """,
        validator=strict_range,
        values=[-200, 200],
        check_set_errors=True,
        check_get_errors=True
    )

    step = Instrument.control(
        ":PAGE:MEAS:VAR2:STEP?",
        ":PAGE:MEAS:VAR2:STEP %g",
        """
        This command sets the sweep STEP value of VAR2 for the linear sweep.
        This parameter is not used for logarithmic sweep.
        -400 to 400 V or -2 to 2 A. Input is only validated for voltages.
        The range of this value depends on the unit type of VAR2.
        The polarity of step value is automatically determined by the relation between start
        and stop values. So, for the step value you specify, only absolute value has meaning.
        The polarity has no meaning.
        """,
        validator=strict_range,
        values=[-400, 400],
        check_set_errors=True,
        check_get_errors=True
    )

    points = Instrument.control(
        ":PAGE:MEAS:VAR2:POINTS?",
        ":PAGE:MEAS:VAR2:POINTS %g",
        """
        This command sets the number of sweep steps of VAR2.
        You use this command only if there is an SMU or VSU
        whose function (FCTN) is VAR2.
        At *RST, this value is 5.
        """,
        validator=strict_discrete_set,
        values=range(1, 128),
        check_set_errors=True,
        check_get_errors=True
    )

    compliance = Instrument.control(
        ":PAGE:MEAS:VAR2:COMP?",
        ":PAGE:MEAS:VAR2:COMP %g",
        """
        This command sets the COMPLIANCE value of VAR2 in Volts/Ampsself. At *RST, this value is 100 mA.
        Only current compliance is validated in function input.
        """,
        validator=strict_range,
        values=[-1, 1],
        check_set_errors=True,
        check_get_errors=True
    )


class vard(Instrument):
    """ Class to handle all the definitions needed for VARD.
    VARD is always defined in relation to VAR1.
    """

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Definitions for VARD sweep variable.",
            **kwargs
        )

    offset = Instrument.control(
        ":PAGE:MEAS:VARD:OFFSET?",
        ":PAGE:MEAS:VARD:OFFSET %g",
        """
        This command sets the OFFSET value of VAR1'.
        For each step of sweep, the output values of VAR1' are determined by the following
        equation: VAR1’ = VAR1 X RATio + OFFSet
        You use this command only if there is an SMU or VSU whose function (FCTN) is
        VAR1'. Only voltage input is validated.
        """,
        validator=strict_range,
        values=[-400, 400],
        check_set_errors=True,
        check_get_errors=True
    )

    ratio = Instrument.control(
        ":PAGE:MEAS:VARD:RATIO?",
        ":PAGE:MEAS:VARD:RATIO %g",
        """
        This command sets the RATIO of VAR1'.
        For each step of sweep, the output values of VAR1' are determined by the following
        equation: VAR1’ = VAR1  RATio + OFFSet
        You use this command only if there is an SMU or VSU whose function (FCTN) is
        VAR1'. At *RST, this value is not defined.
        """,
    )

    compliance = Instrument.control(
        ":PAGE:MEAS:VARD:COMP?",
        ":PAGE:MEAS:VARD:COMP %g",
        """
        This command sets the COMPLIANCE value of VAR1'.
        You use this command only if there is an SMU whose function (FCTN) is VAR1'.
        Only current compliance setting is validated.
        """,
        validator=strict_range,
        values=[-1, 1],
        check_set_errors=True,
        check_get_errors=True
    )


def check_current_voltage_name(name):
    """ Checks if current and voltage names specified for channel
    conforms to the accepted naming scheme. Returns auto-corrected name
    starting with 'a' if name is unsuitable.
    """
    if (len(name) > 6) or not name[0].isalpha():
        new_name = 'a' + name[:5]
        log.info("Renaming %s to %s..." % (name, new_name))
        name = new_name
    return name
