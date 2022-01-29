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

from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    truncated_discrete_set, truncated_range


class SR570(Instrument):

    def __init__(self, resourceName, **kwargs):
        super().__init__(
            resourceName,
            "Stanford Research Systems SR570 Lock-in amplifier",
            **kwargs
        )

    SENSITIVITIES = [
        1e-12, 2e-12, 5e-12, 10e-12, 20e-12, 50e-12, 100e-12, 200e-12, 500e-12,
        1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
        1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
        1e-3
    ]

    FREQUENCIES = [
        0.03, 0.1, 0.3, 1, 3, 10, 30, 100, 300, 1e3, 3e3, 1e4, 3e4,
        1e5, 3e5, 1e6
    ]

    FILT_TYPES = ['6dB Highpass', '12dB Highpass', '6dB Bandpass',
                  '6dB Lowpass', '12dB Lowpass', 'none']

    BIAS_LIMITS = [-5, 5]

    OFFSET_CURRENTS = [
        1e-12, 2e-12, 5e-12, 10e-12, 20e-12, 50e-12, 100e-12, 200e-12, 500e-12,
        1e-9, 2e-9, 5e-9, 10e-9, 20e-9, 50e-9, 100e-9, 200e-9, 500e-9,
        1e-6, 2e-6, 5e-6, 10e-6, 20e-6, 50e-6, 100e-6, 200e-6, 500e-6,
        1e-3, 2e-3, 5e-3
    ]

    GAIN_MODES = [
        'Low Noise', 'High Bandwidth', 'Low Drift'
    ]

    sensitivity = Instrument.setting(
        "SENS %d",
        """ A floating point value that sets the sensitivity of the
        amplifier, which takes discrete values in a 1-2-5 sequence.
        Values are truncated to the closest allowed value if not exact.
        Allowed values range from 1 pA/V to 1 mA/V.""",
        validators=truncated_discrete_set,
        values=SENSITIVITIES,
        map_values=True)

    filter_type = Instrument.setting(
        "FLTT %d",
        """ A string that sets the filter type.
        Allowed values are: {}""".format(FILT_TYPES),
        validators=truncated_discrete_set,
        values=FILT_TYPES,
        map_values=True)

    low_freq = Instrument.setting(
        "LFRQ %d",
        """ A floating point value that sets the lowpass frequency of the
        amplifier, which takes a discrete value in a 1-3 sequence.
        Values are truncated to the closest allowed value if not exact.
        Allowed values range from 0.03 Hz to 1 MHz.""",
        validators=truncated_discrete_set,
        values=FREQUENCIES,
        map_values=True)

    high_freq = Instrument.setting(
        "HFRQ %d",
        """ A floating point value that sets the highpass frequency of the
        amplifier, which takes a discrete value in a 1-3 sequence.
        Values are truncated to the closest allowed value if not exact.
        Allowed values range from 0.03 Hz to 1 MHz.""",
        validators=truncated_discrete_set,
        values=FREQUENCIES,
        map_values=True)

    bias_level = Instrument.setting(
        "BSLV %g",
        """ A floating point value in V that sets the bias voltage level of the
        amplifier, in the [-5V,+5V] limits.
        The values are up to 1 mV precision level.""",
        validators=truncated_range,
        values=BIAS_LIMITS,
        set_process=lambda v: int(1000 * v))

    offset_current = Instrument.setting(
        "BSLV %f",
        """ A floating point value in A that sets the absolute value
        of the offset current of the amplifier, in the [1pA,5mA] limits.
        The offset current takes discrete values in a 1-2-5 sequence.
        Values are truncated to the closest allowed value if not exact. """,
        validators=truncated_discrete_set,
        values=OFFSET_CURRENTS,
        map_values=True)

    offset_current_sign = Instrument.setting(
        "IOSN %d",
        """ An string that sets the offset current sign.
        Allowed values are: 'positive' and 'negative'. """,
        validators=strict_discrete_set,
        values={'positive': 1, 'negative': 0},
        map_values=True)

    gain_mode = Instrument.setting(
        "GNMD %d",
        """ A string that sets the gain mode.
        Allowed values are: {}""".format(GAIN_MODES),
        validators=truncated_discrete_set,
        values=GAIN_MODES,
        map_values=True)

    invert_signal_sign = Instrument.setting(
        "INVT %d",
        """ An boolean sets the signal invert sense.
        Allowed values are: True (inverted) and False (not inverted). """,
        validators=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True)

    bias_enabled = Instrument.setting(
        "BSON %d",
        """ Boolean that turns the bias on or off.
        Allowed values are: True (bias on) and False (bias off)""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True)

    offset_current_enabled = Instrument.setting(
        "IOON %d",
        """ Boolean that turns the offset current on or off.
        Allowed values are: True (current on) and False (current off).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True)

    front_blanked = Instrument.setting(
        "BLNK %d",
        """ Boolean that blanks(True) or un-blanks (False) the front panel""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True)

    signal_inverted = Instrument.setting(
        "INVT %d",
        """ Boolean that inverts the signal if True""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True)

    ####################
    # Methods        #
    ####################

    def enable_bias(self):
        """Turns the bias voltage on"""
        self.bias_enabled = True

    def disable_bias(self):
        """Turns the bias voltage off"""
        self.bias_enabled = False

    def enable_offset_current(self):
        """"Enables the offset current """
        self.offset_current_enabled = True

    def disable_offset_current(self):
        """"Disables the offset current """
        self.offset_current_enabled = False

    def clear_overload(self):
        """"Reset the filter capacitors to clear an overload condition"""
        self.write("ROLD")

    def blank_front(self):
        """"Blanks the frontend output of the device"""
        self.front_blanked = True

    def unblank_front(self):
        """Un-blanks the frontend output of the device"""
        self.front_blanked = False
