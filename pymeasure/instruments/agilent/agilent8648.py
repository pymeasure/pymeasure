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


from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range


class Agilent8648(SCPIMixin, Instrument):
    """ Represents the Agilent 8648 series
    provides a high-level interface for interacting with the instrument.
    """

    BOOL_MAPPINGS = {True: 1, False: 0}
    DISP_MAPPINGS = {True: "TEXT", False: "NORM"}
    AMPL_LIMITS = [-136.0, 22]

    output_enabled = Instrument.control(
        "OUTPUT:STAT?", "OUTPUT:STAT %g",
        "Control output",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    power = Instrument.control(
        "POW:AMPL?", "POW:AMPL %g",
        "Control output power in dBm",
        validator=strict_range,
        values=AMPL_LIMITS
    )

    attenuator_automatic_enabled = Instrument.control(
        "POW:ATT:AUTO?", "OUTPUT:STAT %g",
        "Control attenuator automatic",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    power_ref = Instrument.control(
        "POW:REF?", "POW:REF %g",
        "Control power reference in dBm",
        validator=strict_range,
        values=AMPL_LIMITS
    )

    power_ref_enabled = Instrument.control(
        "POW:REF:STAT?", "POW:REF:STAT %g",
        "Control power reference",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    frequency = Instrument.control(
        "FREQ:CW?", "FREQ:CW %gHZ",
        "Control output CW frequency in Hz",
        dynamic=True,
        validator=strict_range,
        values=[]
    )

    frequency_ref = Instrument.control(
        "FREQ:REF?", "FREQ:REF %gHZ",
        "Control output CW frequency reference in Hz",
        dynamic=True,
        validator=strict_range,
        values=[],
        get_process=lambda val_mhz: val_mhz / 1000000.0
    )

    frequency_ref_enabled = Instrument.control(
        "FREQ:REF:STAT?", "FREQ:REF:STAT %g",
        "Control frequency reference enable",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    am_depth = Instrument.control(
        "AM:DEPT?", "AM:DEPT %g",
        "Control AM depth in %",
        validator=strict_range,
        values=[0, 99.9],
    )

    am_enabled = Instrument.control(
        "AM:STAT?", "AM:STAT %g",
        "Control AM enable",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    am_source = Instrument.control(
        "AM:SOUR?", "AM:SOUR %s",
        "Control AM source (str)",
        validator=strict_discrete_set,
        values={"INT", "INT2", "EXT", "INT,EXT"}
    )

    am_int_frequency = Instrument.control(
        "AM:INT:FREQ?", "AM:INT:FREQ %gHZ",
        "Control INT frequency",
        validator=strict_discrete_set,
        values={"1000", "400"}
    )

    am_ext_coupling = Instrument.control(
        "AM:EXT:COUP?", "AM:EXT:COUP %s",
        "Control external coupling for AM (str)",
        validator=strict_discrete_set,
        values={"DC", "AC"}
    )

    fm_deviation = Instrument.control(
        "FM:DEV?", "FM:DEV %gHZ",
        "Control FM deviation in Hz",
        validator=strict_range,
        values=[10000, 99900],
    )

    fm_enabled = Instrument.control(
        "FM:STAT?", "FM:STAT %g",
        "Control FM enable",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    fm_source = Instrument.control(
        "FM:SOUR?", "FM:SOUR %s",
        "Control FM source (str)",
        validator=strict_discrete_set,
        values={"INT", "INT2", "EXT", "INT,EXT"}
    )

    fm_int_frequency = Instrument.control(
        "FM:INT:FREQ?", "FM:INT:FREQ %gHZ",
        "Control INT frequency",
        validator=strict_discrete_set,
        values={"1000", "400"}
    )

    fm_ext_coupling = Instrument.control(
        "FM:EXT:COUP?", "FM:EXT:COUP %s",
        "Control external coupling for FM (str)",
        validator=strict_discrete_set,
        values={"DC", "AC"}
    )

    pm_deviation = Instrument.control(
        "PM:DEV?", "PM:DEV %gRAD",
        "Control PM deviation in radian",
        validator=strict_range,
        values=[0, 10],
    )

    fm_enabled = Instrument.control(
        "PM:STAT?", "PM:STAT %g",
        "Control PM enable",
        validator=strict_discrete_set,
        values=BOOL_MAPPINGS,
        map_values=True
    )

    pm_source = Instrument.control(
        "PM:SOUR?", "PM:SOUR %s",
        "Control PM source (str)",
        validator=strict_discrete_set,
        values={"INT", "INT2", "EXT", "INT,EXT"}
    )

    pm_int_frequency = Instrument.control(
        "PM:INT:FREQ?", "PM:INT:FREQ %gHZ",
        "Control INT frequency",
        validator=strict_discrete_set,
        values={"1000", "400"}
    )

    pm_ext_coupling = Instrument.control(
        "PM:EXT:COUP?", "PM:EXT:COUP %s",
        "Control external coupling for PM (str)",
        validator=strict_discrete_set,
        values={"DC", "AC"}
    )

    status_modulator_input = Instrument.measurement(
        "STAT:QUES:MOD:COND?",
        "Get the condition of modulation input",
        get_process=lambda status: bool(status)
    )

    status_rpp = Instrument.measurement(
        "STAT:QUES:POW:COND?",
        "Get the condition of status power protection",
        get_process=lambda status: bool(status)
    )


class Agilent8648A(Agilent8648):
    """
    Represents the Agilent 8648A signal generator
    
    .. code-block:: python

        fg = agilent8648.Agilent8648B(vxi11.Instrument("192.168.88.116", "gpib0,19"));
        fg.reset()
        fg.clear()

        fg.power = 0
        print(f'read power: {fg.power}')
        fg.attenuator_automatic_enabled = True
        print(f'read attenuator_automatic: {fg.attenuator_automatic_enabled}')
        fg.power_ref = 1
        print(f'read pwer_ref: {fg.power_ref}')
        fg.power_ref_enabled = False

        print(f'read power_ref_enabled: {fg.power_ref_enabled}')
        fg.frequency = 50000000
        print(f'read frequency: {fg.frequency}')
        fg.frequency_ref = 1000000
        print(f'read frequency_ref: {fg.frequency_ref}')
        fg.frequency_ref_enabled = False
        print(f'read frequency_ref_enabled: {fg.frequency_ref_enabled}')
        
        fg.output_enabled = True
        print(f'read output_enabled: {fg.output_enabled}')
    """
    def __init__(self, adapter, name="Agilent 8648A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    frequency_values = [9000, 1000000000]
    frequency_ref_values = [9000, 2000000000]


class Agilent8648B(Agilent8648):
    """Represents the Agilent 8648B signal generator"""
    def __init__(self, adapter, name="Agilent 8648B", **kwargs):
        super().__init__(adapter, name, **kwargs)

    frequency_values = [9000, 2000000000]
    frequency_ref_values = [9000, 2000000000]

class Agilent8648C(Agilent8648):
    """Represents the Agilent 8648C signal generator"""
    def __init__(self, adapter, name="Agilent 8648C", **kwargs):
        super().__init__(adapter, name, **kwargs)

    frequency_values = [9000, 3200000000]
    frequency_ref_values = [9000, 3200000000]


class Agilent8648D(Agilent8648):
    """Represents the Agilent 8648D signal generator"""
    def __init__(self, adapter, name="Agilent 8648D", **kwargs):
        super().__init__(adapter, name, **kwargs)

    frequency_values = [9000, 4000000000]
    frequency_ref_values = [9000, 4000000000]
