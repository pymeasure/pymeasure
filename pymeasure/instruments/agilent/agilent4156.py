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

from pymeasure.instruments import Instrument, RangeException
from pymeasure.instruments.agilent.agilent4156_channels import smu1
from pymeasure.instruments.validators import *
import numpy as np

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
        self.smu1 = smu1(self.adapter)
        self.var1 = var1(self.adapter)
        self.var2 = var2(self.adapter)
        self.vard = vard(self.adapter)

    analyzer_mode = Instrument.control(
        ":PAGE:CHAN:MODE?", ":PAGE:CHAN:MODE %s",
        """ A string property that controls the analyzer's operating mode,
        which can take the values 'SWEEP' or 'SAMPLING'.
        """,
        validator=strict_discrete_set,
        values={'SWEEP':'SWE', 'SAMPLING':'SAMP'},
        map_values = True,
        check_set_errors=True,
        check_get_errors=True
    )

    integration_time = Instrument.control(
        ":PAGE:MEAS:MSET:ITIM?", ":PAGE:MEAS:MSET:ITIM %s",
        """ A string property that controls the integration time,
        which can take the values 'SHORT', 'MEDIUM' or 'LONG'.
        """,
        validator=strict_discrete_set,
        values={'SHORT':'SHOR', 'MEDIUM':'MED', 'LONG':'LONG'},
        map_values = True,
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
        values={'LINEAR':'LIN', 'LOG10':'L10', 'LOG25':'L25', 'LOG50':'L50'},
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

def save_in_display_list(self, name):
    """ Save the voltage or current in the instrument display list """
    self.write(':PAGE:DISP:MODE LIST')
    self.write(':PAGE:DISP:LIST ' + name)

def save_in_variable_list(self, name):
    """ Save the voltage or current in the instrument variable list """
    self.write(':PAGE:DISP:MODE LIST')
    self.write(':PAGE:DISP:DVAR ' + name)
    if channel_in_group(ch, SMU_CHANNELS) is True:
        name = check_current_voltage_name(name)
        self.write(send_to_channel(ch) + "INAM %s" % name)
    else:
        raise ValueError("Cannot set current name for non-SMU units")
