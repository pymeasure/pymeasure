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
from time import sleep

from pymeasure.instruments import Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

IMPEDANCE_MODES = (
    "CPD", "CPQ", "CPG", "CPRP", "CSD", "CSQ", "CSRS", "LPQ", "LPD", "LPG", "LPRP",
    "LSD", "LSQ", "LSRS", "RX", "ZTD", "ZTR", "GB", "YTD", "YTR"
)


class Agilent4284A(SCPIMixin, Instrument):
    """Represents the Agilent 4284A precision LCR meter.

    .. code-block:: python

        agilent = Agilent4284A("GPIB::1::INSTR")

        agilent.reset()                         # Return instrument settings to default
                                                  values
        agilent.frequency = 10e3                # Set frequency to 10 kHz
        agilent.voltage = 0.02                  # Set AC voltage to 20 mV
        agilent.mode = 'ZTR'                    # Set impedance mode to measure
                                                  impedance magnitude [Ohm] and phase
                                                  [rad]
        agilent.sweep_measurement(
            'frequency', [1e4, 1e3, 100]        # Perform frequency sweep measurement
        )                                       # at 10 kHz, 1 kHz, and 100 Hz
        agilent.enable_high_power()             # Enable upper current, voltage, and
                                                  bias limits, if properly configured.
    """

    def __init__(self, adapter, name="Agilent 4284A LCR meter", **kwargs):
        kwargs.setdefault("read_termination", '\n')
        kwargs.setdefault("write_termination", '\n')
        kwargs.setdefault("timeout", 10000)
        super().__init__(adapter, name, **kwargs)
        self._set_ranges(0)

    frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """Control AC frequency in Hertz, from 20 Hz to 1 MHz.""",
        validator=strict_range,
        values=(20, 1e6),
    )

    ac_current = Instrument.control(
        "CURR:LEV?", "CURR:LEV %g",
        """Control AC current level in Amps. Valid range is 50 uA to 20 mA for default,
        50 uA to 200 mA in high-power mode.""",
        validator=strict_range,
        values=(50e-6, 0.02),
        dynamic=True
    )

    ac_voltage = Instrument.control(
        "VOLT:LEV?", "VOLT:LEV %g",
        """Control AC voltage level in Volts. Range is 5 mV to 2 V for default, 5 mV to
        20 V in high-power mode.""",
        validator=strict_range,
        values=(0.005, 2),
        dynamic=True
    )

    bias_enabled = Instrument.control(
        "BIAS:STAT?", "BIAS:STAT %d",
        """Control whether DC bias is enabled.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    bias_voltage = Instrument.control(
        "BIAS:VOLT?", "BIAS:VOLT %g",
        """Control the DC bias voltage in Volts.
        Maximum is 2 V by default, 40 V in high-power mode.""",
        validator=strict_range,
        values=(0, 2),
        dynamic=True
    )

    bias_current = Instrument.control(
        "BIAS:CURR?", "BIAS:CURR %g",
        """Control the DC bias current in Amps.
        Requires Option 001 (power amplifier / DC bias) to be installed.
        Maximum is 100 mA.""",
        validator=strict_range,
        values=(0, 0),
        dynamic=True
    )

    impedance_mode = Instrument.control(
        "FUNC:IMP?", "FUNC:IMP %s",
        """Control impedance measurement function.

        * CPD: Parallel capacitance [F] and dissipation factor [number]
        * CPQ: Parallel capacitance [F] and quality factor [number]
        * CPG: Parallel capacitance [F] and parallel conductance [S]
        * CPRP: Parallel capacitance [F] and parallel resistance [Ohm]

        * CSD: Series capacitance [F] and dissipation factor [number]
        * CSQ: Series capacitance [F] and quality factor [number]
        * CSRS: Series capacitance [F] and series resistance [Ohm]

        * LPQ: Parallel inductance [H] and quality factor [number]
        * LPD: Parallel inductance [H] and dissipation factor [number]
        * LPG: Parallel inductance [H] and parallel conductance [S]
        * LPRP: Parallel inductance [H] and parallel resistance [Ohm]

        * LSD: Series inductance [H] and dissipation factor [number]
        * LSQ: Seriesinductance [H] and quality factor [number]
        * LSRS: Series inductance [H] and series resistance [Ohm]

        * RX: Resistance [Ohm] and reactance [Ohm]
        * ZTD: Impedance, magnitude [Ohm] and phase [deg]
        * ZTR: Impedance, magnitude [Ohm] and phase [rad]
        * GB: Conductance [S] and susceptance [S]
        * YTD: Admittance, magnitude [Ohm] and phase [deg]
        * YTR: Admittance magnitude [Ohm] and phase [rad]
        """,
        validator=strict_discrete_set,
        values=IMPEDANCE_MODES
    )

    impedance_range = Instrument.control(
        "FUNC:IMP:RANG?", "FUNC:IMP:RANG %g",
        """Control the impedance measurement range. The 4284A will select an appropriate
        measurement range for the setting value."""
    )

    auto_range_enabled = Instrument.control(
        "FUNC:IMP:RANG:AUTO?", "FUNC:IMP:RANG:AUTO %d",
        """Control whether the impedance auto range is enabled.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    trigger_source = Instrument.control(
        "TRIG:SOUR?", "TRIG:SOUR %s",
        """Control trigger mode. Valid options are `INT`, `EXT`, `BUS`, or `HOLD`.""",
        validator=strict_discrete_set,
        values=('INT', 'EXT', 'BUS', 'HOLD'),
        cast=str
    )

    trigger_delay = Instrument.control(
        "TRIG:DEL?", "TRIG:DEL %g",
        """Control trigger delay in seconds. Valid range is 0 to 60, with 1 ms resolution.""",
        validator=strict_range,
        values=(0, 60)
    )

    trigger_continuous_enabled = Instrument.control(
        "TRIG:CONT?", "TRIG:CONT %d",
        """Control whether trigger state automatically returns to WAIT FOR TRIGGER
        after measurement.""",
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    def _set_ranges(self, high_power_mode):
        """Set dynamic property values and make copies for sweep_measurement to reference."""
        if high_power_mode:
            self.ac_current_values = (50e-6, 0.2)
            self.ac_voltage_values = (0.005, 20)
            self.bias_voltage_values = (0, 40)
            self.bias_current_values = (0, 0.1)
            self._ac_current_values = (50e-6, 0.2)
            self._ac_voltage_values = (0.005, 20)
            self._bias_voltage_values = (0, 40)
            self._bias_current_values = (0, 0.1)
        else:
            self.ac_current_values = (50e-6, 0.02)
            self.ac_voltage_values = (0.005, 2)
            self.bias_voltage_values = (0, 2)
            self.bias_current_values = (0, 0)
            self._ac_current_values = (50e-6, 0.02)
            self._ac_voltage_values = (0.005, 2)
            self._bias_voltage_values = (0, 2)
            self._bias_current_values = (0, 0)

    @property
    def high_power_enabled(self):
        """Control whether high power mode is enabled.
        Enabling requires option 001 (power amplifier / DC bias) to be installed.
        """
        mode = self.values("OUTP:HPOW?", cast=int)
        return bool(mode)

    @high_power_enabled.setter
    def high_power_enabled(self, val):
        if not val:
            self._set_ranges(0)
            self.write("OUTP:HPOW 0")
        elif val and self.options[0] == '0':
            raise AttributeError("Agilent 4284A power amplifier is not installed.")
        else:
            self._set_ranges(1)
            self.write("OUTP:HPOW 1")

    def sweep_measurement(self, sweep_mode, sweep_values):
        """Run list sweep measurement using sequential trigger.

        :param str sweep_mode: parameter to sweep across. Must be one of `frequency`,
            `voltage`, `current`, `bias_voltage`, or `bias_current`.
        :param sweep_values: list of parameter values to sweep across.

        :returns: values as configured with :attr:`~.Agilent4284A.impedance_mode` and
            list of sweep parameters in format ([val A], [val B], [sweep_values])
        """
        param_dict = {
            "frequency": ("FREQ", (20, 1e6)),
            "voltage": ("VOLT", self._ac_voltage_values),
            "current": ("CURR", self._ac_current_values),
            "bias_voltage": ("BIAS:VOLT", self._bias_voltage_values),
            "bias_current": ("BIAS:CURR", self._bias_current_values)
        }

        if sweep_mode not in param_dict:
            raise KeyError(
                f"Sweep mode but be one of {list(param_dict.keys())}, not '{sweep_mode}'."
            )

        low_limit = param_dict[sweep_mode][1][0]
        high_limit = param_dict[sweep_mode][1][1]
        if (min(sweep_values) < low_limit or max(sweep_values) > high_limit):
            log.warning(
                "%s values are outside valid Agilent 4284A range of %g and %g "
                "and will be truncated.", sweep_mode, low_limit, high_limit
            )
            sweep_truncated = []
            for val in sweep_values:
                if low_limit <= val <= high_limit:
                    sweep_truncated.append(val)
            sweep_values = sweep_truncated

        loops = (len(sweep_values) - 1) // 10  # 4284A sweeps 10 points at a time
        param_div = []
        for i in range(loops):
            param_div.append(sweep_values[10*i:10*(i+1)])
        param_div.append(sweep_values[loops*10:])

        self.clear()
        self.write("TRIG:SOUR BUS;:DISP:PAGE LIST;:FORM ASC;:LIST:MODE SEQ;:INIT:CONT ON")

        a_data = []
        b_data = []
        sweep_return = []
        for i in range(loops + 1):
            param_str = ",".join(['%g' % p for p in param_div[i]])
            self.write(f"LIST:{param_dict[sweep_mode][0]} {param_str};:TRIG:IMM")
            status_event_register = int(self.ask("STAT:OPER?"))
            while (status_event_register & 8) != 8:  # Sweep bit no. 3
                sleep(0.1)
                status_event_register = int(self.ask("STAT:OPER?"))
            measured = self.values("FETCH?")
            # gets 4-ples of numbers, first two are data A and B
            a_data += [measured[_] for _ in range(0, 4 * len(param_div[i]), 4)]
            b_data += [measured[_] for _ in range(1, 4 * len(param_div[i]), 4)]
            sweep_return += self.values(f"LIST:{param_dict[sweep_mode][0]}?")

        # Return to manual trigger and reset display
        self.write(":TRIG:SOUR HOLD;:DISP:PAGE MEAS")
        self.check_errors()
        return a_data, b_data, sweep_return

    def trigger(self):
        """Execute a bus trigger, regardless of trigger state.
        Can be used when :attr:`trigger_source` is set to `BUS`.
        Returns result of triggered measurement.
        """
        return self.values("*TRG")

    def trigger_immediate(self):
        """Execute a bus trigger, regardless of trigger state.
        Can be used when :attr:`trigger_source` is set to `BUS`.
        Measurement result must be retrieved with `FETCH?` command.
        """
        self.write("TRIG:IMM")

    def trigger_initiate(self):
        """Change the trigger state from IDLE to WAIT FOR TRIGGER for one trigger sequence."""
        self.write("TRIG:INIT:IMM")
