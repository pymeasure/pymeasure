#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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
from typing import Literal

from pymeasure.instruments import Instrument, SCPIUnknownMixin
from pymeasure.instruments.common_base import cast_or_str
from pymeasure.instruments.validators import strict_discrete_set

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def check_read_not_empty(value: Literal[""] | float) -> float:
    """Called by some properties to check if the reply is not an empty string
    that would mean the properties is currently invalid (probably because the reference mode
    is on single or dual)"""
    if value == "":
        raise ValueError(
            "Invalid response from measurement call, "
            "probably because the reference mode is set on single or dual"
        )
    else:
        return value


class Ametek5210(SCPIUnknownMixin, Instrument):
    """
    This is the class for the
    Ametek (EG&G Princeton Applied Research) Signal Recovery 5210 Dual Phase lock-in amplifier.

    Many commands depend on other parameters or may have additional constraints,
    please refer to the documentation for more details.
    """

    SENSITIVITIES = {
        "100 nV": 0,
        "300 nV": 1,
        "1 uV": 2,
        "3 uV": 3,
        "10 uV": 4,
        "30 uV": 5,
        "100 uV": 6,
        "300 uV": 7,
        "1 mV": 8,
        "3 mV": 9,
        "10 mV": 10,
        "30 mV": 11,
        "100 mV": 12,
        "300 mV": 13,
        "1 V": 14,
        "3 V": 15,
    }

    TIME_CONSTANTS = {
        "1 ms": 0,
        "3 ms": 1,
        "10 ms": 2,
        "30 ms": 3,
        "100 ms": 4,
        "300 ms": 5,
        "1 s": 6,
        "3 s": 7,
        "10 s": 8,
        "30 s": 9,
        "100 s": 10,
        "300 s": 11,
        "1 ks": 12,
        "3 ks": 13,
    }

    STATUS_ARRAY = [
        "command complete",
        "invalid command",
        "command parameter error",
        "reference unlock",
        "overload",
        "new output values available after external trigger, or auto function in progress",
        "SRQ asserted",
        "data available",
    ]

    OVERLOAD_ARRAY = [
        "not used",
        "current mode set to 10^8 A/V",
        "current mode set to 10^6 A/V",
        "Y channel output overload",
        "X channel output overload",
        "PSD overload",
        "input overload",
        "reference unlock",
    ]

    sensitivity = Instrument.control(
        "SEN",
        "SEN %d",
        """Control the sensitivity range in Volts
        (float truncated to values from 100 nV to 3 V).""",
        validator=strict_discrete_set,
        values=SENSITIVITIES,
        map_values=True,
        check_set_errors=True,
        dynamic=True,
    )

    time_constant = Instrument.control(
        "XTC",
        "XTC %d",
        """Control the time constant in seconds
        (float truncated to values from 1 millisecond to 3,000 seconds).""",
        validator=strict_discrete_set,
        values=TIME_CONSTANTS,
        map_values=True,
        check_set_errors=True,
    )

    def __init__(
        self, adapter, name="5210", read_termination="\x00", write_termination="\x00", **kwargs
    ):

        super().__init__(
            adapter,
            name,
            read_termination=read_termination,
            write_termination=write_termination,
            **kwargs,
        )

    def check_set_errors(self):
        """mandatory to be used for property setter

        The Ametek protocol expect the default null character to be read to check the property
        has been correctly set. With default termination character set as Null character,
        this turns out as an empty string to be read.
        """
        if self.read() == "":
            return []
        else:
            return ["Incorrect return from previously set property"]

    def ask(self, command, query_delay=1):
        """Send a command and read the response, stripping white spaces.

        Usually the properties use the
        :meth:`~pymeasure.instruments.common_base.CommonBase.values`
        method that adds a strip call, however several methods use directly the result from ask to
        be cast into some other types. It should therefore also add the strip here, as all responses
        end with a newline character.
        """
        return super().ask(command, query_delay).strip()

    def auto_sensitivity(self):
        """Perform an auto sensitivity operation.

        The instrument adjusts its full-scale sensitivity so that the magnitude output lies
        between 25 % and 95 % of full-scale.
        """

        self.ask("AS")

    def auto_normalize(self):
        """Perform an auto normalize operation.

        The AN command causes the vernier mode to be activated the sensitivity to be adjusted
        to achieve an X-output of 100% (full-scale).

        The auto-normalize operation always begins with an auto-sensitivity function.
        If none of the sensitivity ranges yields an output magnitude
        between 25% and 95% of full scale,
        the sensitivity is set to one extreme or the other and normalization is not attempted.
        """

        self.ask("AN")

    def abandon_auto(self):
        """Abandon auto-function.

        This command terminates any auto-function in progress, except the auto-measure function,
        when it should be sent twice.
        """

        self.ask("AA")

    def auto_measure(self):
        """Perform an auto-measure operation.

        The instrument adjusts its full-scale sensitivity so that the magnitude output lies
        between 25 % and 95 % of full-scale,
        and then performs an auto-phase operation to maximize the X-channel output and
        minimize the Y-channel output.
        """

        self.ask("ASM")

    def auto_tune(self):
        """Perform an automatic frequency tune.

        The ATC command causes the filter frequency to be tuned to the reference frequency,
        by setting the filter track mode on and then off.
        """
        self.ask("ATC")

    def auto_phase(self):
        """Perform an auto phase (auto quadrature null) operation.

        The instrument adjusts the reference phase to maximize the X channel output and
        minimize the Y channel output signals.
        """
        self.ask("AQN")

    def auto_offset(self):
        """Perform an auto offset operation.

        The instrument adjusts the X and Y channel output offsets to minimize the
        X and Y channel output signals.
        """
        self.ask("AXO")

    def status(self) -> list[str]:
        """Get the instrument status.

        :return: list of all status errors received.
        """
        status_code = int(self.ask("ST"))
        status = [self.STATUS_ARRAY[i] for i in range(8) if status_code & (1 << i)]

        return status

    def report_overload(self):
        """Reports the overload byte status.

        :return: list of all overload errors received.
        """
        overload_code = int(self.ask("OL"))
        overload = [self.OVERLOAD_ARRAY[i] for i in range(8) if overload_code & (1 << i)]

        return overload

    @property
    def id(self):
        """Get the instrument ID and firmware version"""
        return f"{self.ask('ID')}/{self.ask('VER')}"

    @property
    def filter_op_mode(self):
        """Control the filter operation mode (int).

        :param setval: 0 is Flat/No filter, 1 is Notch/Band-rejection,
            2 is Low-pass, 3 is High-pass.
        """
        return int(self.ask("FLT"))

    @property
    def filter_tuning_mode(self):
        """Control the filter frequency tuning mode (int).

        :param setval: 0 is Manual (frequency set by front-panel keys or by the FF command),
            1 is Auto (filter frequency set to reference channel frequency).
        """
        return int(self.ask("ATC"))

    @property
    def filter_frequency(self):
        """Control the filter frequency.

        :param (n1,n2): tuple of two integers, where n1 is the frequency within the band and
            n2 is the band number.

        The value of parameter n2 sets or reads the filter frequency band according to
        the following table:

            n2.  frequency band
            0.  0.5 Hz to 12 Hz
            1.  10 Hz to 120 Hz
            2.  100 Hz to 1200 Hz
            3.  1 kHz to 12 kHz
            4.  10 kHz to 120 kHz

        The value of parameter n1 sets or reads the frequency within each band in the range
        100 to 1200, except in the bottom band (n2 = 0) where the range is 50 to 1200
        """
        response = self.ask("FF")
        # Parse the response to extract n1 and n2
        n1, n2 = map(int, response.split())
        return (n1, n2)

    @property
    def line_frequency_reject_mode(self):
        """Control the line frequency reject mode (int).

        The value of parameter sets or reads the mode of the line frequency notch filter.

            n.  selection
            0.  Off
            1.  Enable 100 or 120 Hz notch filter
            2.  Enable 50 or 60 Hz notch filter
            3.  Enable both filters

        :param setval: integer to select the mode: 0 is Off, 1/2/3 is On accordingly.

        """
        return int(self.ask("LFR"))

    @property
    def reference_internal(self):
        """Control whether the instrument internal reference is enabled, otherwise it will
        be external (bool).

        :param setval: integer to enable the mode: 0 for External, 1 for Internal
        """
        return int(self.ask("IE")) == 1

    @property
    def reference_mode(self):
        """Control whether the instrument frequency reference order is in second harmonic mode.

        :param mode: integer to enable the mode: 0 for First harmonic,
        1 for Second harmonic reference.
        """
        return int(self.ask("F2F"))

    @property
    def reference_phase(self):
        """Control the reference phase in degrees (float).

        Minimum resolution of 5 m°.
        Note: The instrument uses an intricate quadrants system but I have handled this for you.

        :param setval: float to set the reference phase in degrees, modular range from 0 to 360.
        """
        ref_phase_read = self.ask("P")
        quad_str, mdeg_str = ref_phase_read.split()
        read_quad = int(quad_str)
        read_millidegrees = int(mdeg_str)
        read_degrees = read_millidegrees / 1000
        read_ref_phase = read_degrees + read_quad * 90
        return read_ref_phase

    @property
    def reference_frequency_meter(self):
        """If the lock-in amplifier is in the external reference source modes,
        this responds with 0 if the reference channel is unlocked,
        or with the reference input frequency if it is locked.

        If the lock-in amplifier is in the internal reference source mode,
        it responds with the frequency of the internal oscillator.

        :return 0: if the reference channel is unlocked.
        :return Reference frequency (mHz): if the reference channel is locked.
        """
        return int(self.ask("FRQ"))

    @property
    def second_order_filter(self):
        """Control whether the second order filter is enabled (bool).

        :param setval: 0 is First order (slope 6 dB/octave),
        1 is Second order (slope 12 dB/octave).
        """
        return int(self.ask("XDB")) == 1

    @property
    def dynamic_reserve(self):
        Dynamic_Reserves = {
            "HI STAB": 0,
            "NORM": 1,
            "HI RES": 2,
        }
        inverse = {v: k for k, v in Dynamic_Reserves.items()}
        return inverse[int(self.ask("DR"))]

    @property
    def x_channel_offset(self):
        """X channel output offset control

        The value of parameter n1 sets or reads the status and
        level of the X offset facility according to the following table:

            n1 selection
            0 Disables X offset facility
            1 Enables X offset facility

        The range of n2 is +/-1500 corresponding to +/-150% of the full-scale output.

        :param (n1,n2): tuple of two integers, where n1 is the status and
        n2 is the level of the X offset facility.
        :param n1:  integer where n1 is the selection.
        """
        return self.ask("XOF")

    @property
    def y_channel_offset(self):
        """Y channel output offset control

        The value of parameter n1 sets or reads the status and
        level of the Y offset facility according to the following table:

            n1 selection
            0 Disables Y offset facility
            1 Enables Y offset facility

        The range of n2 is +/-1500 corresponding to +/-150% of the full-scale output.

        :param (n1,n2): tuple of two integers, where n1 is the status and
        n2 is the level of the Y offset facility.
        :param n1:  integer where n1 is the selection.
        """
        return self.ask("YOF")

    @property
    def output_expansion(self):
        """Control the output expansion (bool).

        The value of parameter n sets or reads the X-channel output expansion mode.

            n. expand mode
            0. Off
            1. Expand X channel output by x10

        :param setval: 0 is Normal, 1 is Expanded output range.
        """
        return int(self.ask("EX")) == 1

    @property
    def oscillator_amplitude(self):
        """Control the oscillator amplitude in Volts (float).

        The value of parameter sets or reads the oscillator amplitude.
        The range is 0 to 2000 representing 0 to 2 V rms, but the value 5000 may also be used,
        which corresponds to an output amplitude of 5.000 V rms.

        :param setval: float to set the oscillator amplitude in Volts,
            truncated range from 0 to 5 V.
        """
        return float(self.ask("OA"))

    @property
    def oscillator_frequency(self):
        """Control the oscillator frequency in Hz (n1,n2).

        The value of parameter n2 sets or reads the oscillator frequency band
        according to the following table:

            n2   frequency band
            0   0.5 Hz to 2 Hz
            1   2.0 Hz to 20 Hz
            2   20 Hz to 200 Hz
            3   200 Hz to 2 kHz
            4   2 kHz to 20 kHz
            5   20 kHz to 120 kHz

        The value of parameter n1 sets or reads the frequency within each band
        in the range 2000 to 20000
        Hence, for example, to set the frequency to 1 kHz, send the command OF 1000 3.

        :param setval: tuple to set the oscillator frequency in Hz.
        """
        return float(self.ask("OF"))

    @property
    def trigger_mode(self):
        """Control the ADC trigger mode (int).

        The value of parameter sets or reads the trigger mode according to the following table:

            n   Trigger mode
            0   Reference trigger mode
            1   External trigger mode
            2   Asynchronous trigger mode
            4   Ratio trigger mode
            8   "8F" trigger mode

        :param setval: integer to set the trigger mode: 0 is Reference, 1 is External,
            2 is Asynchronous, 4 is Ratio, 8 is "8F".
        """
        return int(self.ask("TRIG"))

    @property
    def remote_only_mode(self):
        """Control the remote only mode (bool).

        The value of parameter sets or reads the remote mode according to the following table:

            n   Mode
            0   Local mode, front panel keys active
            1   Remote mode, frontpanel keys locked out, except for LOCAL

        :param setval: integer to set the remote mode: 0 is Local, 1 is Remote.
        """
        return int(self.ask("REMOTE")) == 1

    @property
    def display1_selection(self):
        """Control the display 1 selection (int).

        The value of parameter sets or reads the display 1 selection
        according to the following table:

            n   Display 1 selection
            0   SET REF PH (Reference Phase)
            1   SET OSC LVL (Oscillator Amplitude)
            2   SET OSC F (Oscillator Frequency)
            3   FIL FRQ (Filter Frequency)
            4   REF F (Reference Frequency)
            5   DISP (As selected by Display 2 selection control)

        :param setval: integer to set the display 1 selection:
            0 is Reference Phase,
            1 is Oscillator Amplitude,
            2 is Oscillator Frequency,
            3 is Filter Frequency,
            4 is Reference Frequency,
            5 is As selected by Display 2 selection control.
        """
        return int(self.ask("D1"))

    @property
    def display2_selection(self):
        """Control the display 2 selection (int).

        The value of parameter sets or reads the display 2 selection
        according to the following table:

            n   Display 2 selection
            0   XY % (X and Y as a voltage: 10.000 V = 100%)
            1   XY V (X and Y in volts)
            2   R-Theta (Magnitude and Phase)
            3   OFFSET
            4   NOISE
            5   SPEC (Depends on special display modes)

        :param setval: integer to set the display 2 selection: 0 is XY %, 1 is XY V,
            2 is R-Theta, 3 is OFFSET, 4 is NOISE, 5 is SPEC.
        """
        return int(self.ask("D2"))

    @property
    def display_update_rate(self):
        """Control the display update rate (float).

        Range 0.1 to 1.0 s in 0.1 s increments.

        :param setval: float to set the display update rate in seconds, from 0.1 to 1.0 s.
        """
        return float(self.ask("DISP"))

    @property
    def lights_enabled(self):
        """Control whether the front panel lights are enabled (bool).

        :param setval: integer to set the lights mode: 0 is Off, 1 is On.
        """
        return int(self.ask("LTS")) == 1

    x = Instrument.measurement(
        "X",
        """Get X value in millivolts (float).

        Responds with the X-channel output in the range ‡15000, full-scale being ‡10000""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    y = Instrument.measurement(
        "Y",
        """Get Y value in millivolts (float).

        Responds with the Y-channel output in the range ‡15000, full-scale being ‡10000""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    xy = Instrument.measurement(
        "XY",
        """Get both X and Y values in millivolts, equivalent to reading X and Y separately.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    magnitude = Instrument.measurement(
        "MAG",
        """Get magnitude in millivolts (float).

        Responds with the magnitude output in the range 0 to +15000, full-scale being +10000.
        """,
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    signal_phase = Instrument.measurement(
        "PHA",
        """Get signal phase in millidegrees (float).

        Responds with the signal phase in millidegrees, in the range +180000, corresponding to 180°.
        """,
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    magpha = Instrument.measurement(
        "MP",
        """Get both magnitude and phase in millivolts and millidegrees,
        equivalent to reading MAG and PHA separately.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    ratio = Instrument.measurement(
        "RT",
        """Reports a number equivalent to (1000*X)/ADC1 where X is the value
        that would be returned by the X command and ADC1 is the value
        that would be returned by the ADC1 command.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    log_ratio = Instrument.measurement(
        "LR",
        """Reports a number equivalent to 1000 * log10(X/ADC1) where X is the value
        that would be returned by the X command and ADC1 is the value
        that would be returned by the ADC1 command. The response range is 3000 to +2000.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    noise = Instrument.measurement(
        "NN",
        """Responds with the noise, expressed as a percentage of the present full scale sensitivity,
        with 10000 corresponding to 100%.
        The noise is measured in a bandwidth defined by the output filter time constant and slope,
        centered about the reference frequency.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    dac = Instrument.measurement(
        "DAC",
        """Reads the voltage in millivolts appearing at the rear panel DAC AUX OUT output,
        in the range -15000 to +15000.,
        """,
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    adc1 = Instrument.measurement(
        "ADC 1",
        """Reads the voltage in millivolts appearing at the CH1 input, as an integer
        in the range -15000 to +15000.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    adc2 = Instrument.measurement(
        "ADC 2",
        """Reads the voltage in millivolts appearing at the CH2 input, as an integer
        in the range -15000 to +15000.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    adc3 = Instrument.measurement(
        "ADC 3",
        """Reads the voltage in millivolts appearing at the CH3 input, as an integer
        in the range -15000 to +15000.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    adc4 = Instrument.measurement(
        "ADC 4",
        """Reads the voltage in millivolts appearing at the CH4 input, as an integer
        in the range -15000 to +15000.""",
        cast=cast_or_str(float),
        get_process=check_read_not_empty,
    )

    @filter_op_mode.setter
    def filter_op_mode(self, setval: int):
        if setval not in [0, 1, 2, 3]:
            raise ValueError("Invalid filter operation mode")
        self.ask(f"FLT {setval}")

    @filter_tuning_mode.setter
    def filter_tuning_mode(self, setval: int):
        if setval not in [0, 1]:
            raise ValueError("Invalid filter tuning mode")
        self.ask(f"ATC {setval}")

    @filter_frequency.setter
    def filter_frequency(self, setval: tuple[int, int]):
        n1, n2 = setval
        if n2 not in [0, 1, 2, 3, 4]:
            raise ValueError("Invalid filter frequency band")
        if n2 == 1 and not (50 <= n1 <= 1200):
            raise ValueError("Invalid filter frequency for band 0")
        elif n2 != 1 and not (100 <= n1 <= 1200):
            raise ValueError(f"Invalid filter frequency for band {n2}")
        self.ask(f"FF {n1} {n2}")

    @line_frequency_reject_mode.setter
    def line_frequency_reject_mode(self, setval: int):
        if setval not in [0, 1, 2, 3]:
            raise ValueError("Invalid line frequency reject mode")
        self.ask(f"LFR {setval}")

    @reference_internal.setter
    def reference_internal(self, setval: int):
        if setval not in [0, 1]:
            raise ValueError("Invalid reference internal mode")
        self.ask(f"IE {setval}")

    @reference_mode.setter
    def reference_mode(self, setval: int):
        if setval not in [0, 1]:
            raise ValueError("Invalid reference mode")
        self.ask(f"F2F {setval}")

    @reference_phase.setter
    def reference_phase(self, setval: float):
        setval = setval % 360

        # Reference phase control
        if 0 <= setval <= 90:
            # quad 1 = 0
            quad_less1 = 0
        elif 90 < setval <= 180:
            # quad 2 = 1
            quad_less1 = 1
        elif 180 < setval <= 270:
            # quad 3 = 2
            quad_less1 = 2
        else:
            # quad 4 = 3
            quad_less1 = 3

        ref_degrees = setval - (quad_less1 * 90)
        ref_millidegrees = int(ref_degrees * 1000)

        self.ask(f"P {quad_less1} {ref_millidegrees}")

    @second_order_filter.setter
    def second_order_filter(self, setval: bool):
        if setval:
            self.ask("XDB 1")
        else:
            self.ask("XDB 0")

    @dynamic_reserve.setter
    def dynamic_reserve(self, setval: str):
        Dynamic_Reserves = {
            "HI STAB": 0,
            "NORM": 1,
            "HI RES": 2,
        }
        if setval not in Dynamic_Reserves:
            raise ValueError(
                f"Invalid dynamic reserve value: {setval}. "
                f"Valid values are: {list(Dynamic_Reserves.keys())}"
            )
        self.ask(f"DR {Dynamic_Reserves[setval]}")

    @x_channel_offset.setter
    def x_channel_offset(self, setval: tuple[int, int] | int):
        if isinstance(setval, (tuple, list)):
            n1, n2 = setval
            if n1 not in [0, 1]:
                raise ValueError("Invalid X channel offset status")
            if not (-1500 <= n2 <= 1500):
                raise ValueError("Invalid X channel offset level")
            self.ask(f"XOF {n1} {n2}")
        else:
            n1 = setval
            if n1 not in [0, 1]:
                raise ValueError("Invalid X channel offset status")
            self.ask(f"XOF {n1}")

    @y_channel_offset.setter
    def y_channel_offset(self, setval: tuple[int, int] | int):
        if isinstance(setval, (tuple, list)):
            n1, n2 = setval
            if n1 not in [0, 1]:
                raise ValueError("Invalid Y channel offset status")
            if not (-1500 <= n2 <= 1500):
                raise ValueError("Invalid Y channel offset level")
            self.ask(f"YOF {n1} {n2}")
        else:
            n1 = setval
            if n1 not in [0, 1]:
                raise ValueError("Invalid Y channel offset status")
            self.ask(f"YOF {n1}")

    @oscillator_amplitude.setter
    def oscillator_amplitude(self, setval: float):
        if not (0 <= setval <= 5):
            raise ValueError("Invalid oscillator amplitude, should be in [0, 5]")
        self.ask(f"OA {setval}")

    @oscillator_frequency.setter
    def oscillator_frequency(self, setval: tuple[int, int]):
        n1, n2 = setval
        if n2 not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Invalid oscillator frequency band")
        if not (500 <= n1 <= 20000):
            raise ValueError("Invalid oscillator frequency within band")
        self.ask(f"OF {n1} {n2}")

    @trigger_mode.setter
    def trigger_mode(self, setval: int):
        if setval not in [0, 1, 2, 4, 8]:
            raise ValueError("Invalid trigger mode")
        self.ask(f"TRIG {setval}")

    @remote_only_mode.setter
    def remote_only_mode(self, setval: bool):
        if setval:
            self.ask("REMOTE 1")
        else:
            self.ask("REMOTE 0")

    @display1_selection.setter
    def display1_selection(self, setval: int):
        if setval not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Invalid display 1 selection")
        self.ask(f"D1 {setval}")

    @display2_selection.setter
    def display2_selection(self, setval: int):
        if setval not in [0, 1, 2, 3, 4, 5]:
            raise ValueError("Invalid display 2 selection")
        self.ask(f"D2 {setval}")

    @display_update_rate.setter
    def display_update_rate(self, setval: float):
        if not (0.1 <= setval <= 1.0):
            raise ValueError("Invalid display update rate, should be in [0.1, 1.0]")
        self.ask(f"DISP {setval}")

    @lights_enabled.setter
    def lights_enabled(self, setval: bool):
        if setval:
            self.ask("LTS 1")
        else:
            self.ask("LTS 0")

    def shutdown(self):
        """Ensures the instrument in a safe state to close."""
        log.info(f"Shutting down {self.name}")
        self.oscillator_amplitude = 0.0
        self.remote_only_mode = False
        super().shutdown()
