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

    Most attributes are inherited from the Agilent E4980; a couple are overwritten
    to accomodate slight differences between the instruments.

    .. code-block:: python

        agilent = Agilent4284A("GPIB::1")

        agilent.reset()                         # Return instrument settings to default
                                                  values
        agilent.frequency = 10e3                # Set frequency to 10 kHz
        agilent.voltage = 0.02                  # Set AC voltage to 20 mV
        agilent.mode = 'ZTR'                    # Set impedance mode to measure
                                                  impedance magnitude [Ohm] and phase
                                                  [rad]
        agilent.trigger_on_bus()
        print(agilent.trigger())                # Trigger and print a measurement
        agilent.enable_high_power()             # Enable upper current, voltage, and
                                                  bias limits, if properly configured.

    """

    def __init__(self, adapter, name="Agilent 4284A LCR meter", **kwargs):
        super().__init__(adapter, name, **kwargs)

    frequency = Instrument.control(
        "FREQ?", "FREQ %g",
        """Control AC frequency in Hertz, from 20 Hz to 1 MHz.""",
        validator=strict_range,
        values=(20, 1e6),
    )

    ac_current = Instrument.control(
        "CURR:LEV?", "CURR:LEV %g",
        """"Control AC current level in Amps. Valid range is 50 uA to 20 mA for default,
        50 uA to 200 mA in high-power mode.""",
        validator=strict_range,
        values=(50e-6, 0.02),
        dynamic=True
    )

    ac_voltage = Instrument.control(
        "VOLT:LEV?", "VOLT:LEV %g",
        """"Control AC voltage level in Volts. Range is 5 mV to 2 V for default, 5 mV to
        20 V in high-power mode.""",
        validator=strict_range,
        values=(0.005, 2),
        dynamic=True
    )

    high_power_enabled = Instrument.measurement(
        "OUTP:HPOW?",
        """Get whether the high-power mode is enabled.
        High power requires Option 001 (power amplifier / DC bias) is installed.""",
        values={False: 0, True: 1},
        map_values=True
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
        Requires Option 001 (power amplifier / DC bias) is installed.
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
        * YTR: Admittance magnitude [Ohm] and phase [rad]""",
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
        values={False: 0, True: 1}
    )

    def enable_high_power(self):
        """Enable high power mode.

        Requires option 001 (power amplifier / DC bias) is installed.
        """
        if self.options[0] == 0:
            log.warning("Agilent 4284A power amplifier is not installed.")
            return
        self.ac_current_values = (50e-6, 0.2)
        self.ac_voltage_values = (0.005, 20)
        self.bias_voltage_values = (0, 40)
        self.bias_current_values = (0, 0.1)
        self.write("OUTP:HPOW 1")

    def disable_high_power(self):
        """Disable high power mode."""
        self.ac_current_values = (50e-6, 0.02)
        self.ac_voltage_values = (0.005, 2)
        self.bias_voltage_values = (0, 2)
        self.bias_current_values = (0, 0)
        self.write("OUTP:HPOW 0")

    def frequency_sweep(self, freq_list, return_freq=True):
        """Run frequency list sweep using sequential trigger.

        :param freq_list: list of frequencies
        :param return_freq: if True, returns the frequencies read from the instrument

        Returns values as configured with :attr:`~.Agilent4284A.impedance_mode` and list
            of frequencies in format ([val A], [val B], [frequency])
        """
        if min(freq_list) < 20 or max(freq_list) > 1e6:
            log.warning("Agilent 4284A valid frequency range is 20 Hz to 1 MHz.")
            return
        freq_str = ",".join(['%g' % f for f in freq_list])
        self.reset()
        self.clear()
        self.write(f"TRIG:SOUR BUS;FORM ASC;LIST:MODE SEQ;LIST:FREQ {freq_str}")
        self.write("INIT:CONT ON")
        self.write("TRIG:IMM")
        # TODO: see if this while block is necessary
        # while True:
        #     if (self.status & 8) == 8:  # bit 3 is list sweep measurement complete bit
        #         break
        #     else:
        #         sleep(1)
        #         continue
        measured = self.values("FETCH?")
        # at the end return to manual trigger
        self.write(":TRIG:SOUR HOLD")
        # gets 4-ples of numbers, first two are data A and B
        a_data = [measured[_] for _ in range(0, 4 * len(freq_list), 4)]
        b_data = [measured[_] for _ in range(1, 4 * len(freq_list), 4)]
        if return_freq:
            read_freqs = self.values("LIST:FREQ?")
            self.check_errors()
            return a_data, b_data, read_freqs
        else:
            self.check_errors()
            return a_data, b_data, freq_list

    def trigger(self):
        """Execute a bus trigger, which can be used when :meth:`~.trigger_on_bus`
        is configured. Returns result of triggered measurement.
        """
        return self.write("*TRG")

    def trigger_on_bus(self):
        """Configure the trigger to detect events based on the bus trigger, which can be
        activated by :meth:`~.trigger`.
        """
        self.write("TRIG:SOUR BUS")
