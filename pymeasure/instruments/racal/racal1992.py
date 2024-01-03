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

import logging
import time

from pymeasure.instruments import Instrument

log = logging.getLogger(__name__)   # https://docs.python.org/3/howto/logging.html#library-config
log.addHandler(logging.NullHandler())


class ReturnValueError(Exception):
    pass


class Racal1992(Instrument):
    """Represents the Racal-Dana 1992 Universal counter

    .. code-block:: python

        from pymeasure.instruments.racal import Racal1992
        counter = Racal1992("GPIB0::10")

    This class should also work for Racal-Dana 1991, it has the same
    product manual, as long as you don't use functionality that requires
    channel B.
    """

    def __init__(self, adapter, name="Racal-Dana 1992", **kwargs):
        kwargs.setdefault('write_termination', '\r\n')

        super().__init__(
            adapter,
            name,
            includeSCPI=False,
            **kwargs
        )

    int_types = ['SF', 'RS', 'UT', 'MS', 'TA']
    float_types = ['CK', 'FA', 'PA', 'TI', 'PH', 'RA',
                   'MX', 'MZ', 'LA', 'LB', 'FC', 'RC', 'DT', 'GS']

    channel_params = {
        'A' : {                                                         # noqa
            'coupling'      : { 'AC'   : 'AAC',  'DC'     : 'ADC' },    # noqa
            'attenuation'   : { 'X1'   : 'AAD',  'X10'    : 'AAE' },    # noqa
            'trigger'       : { 'auto' : 'AAU',  'manual' : 'AMN' },    # noqa
            'impedance'     : { '50'   : 'ALI',  '1M'     : 'AHI' },    # noqa
            'slope'         : { 'pos'  : 'APS',  'neg'    : 'ANS' },    # noqa
            'filtering'     : { True   : 'AFE',  False    : 'AFD' },    # noqa
            'trigger_level' : None,                                     # noqa
            },
        'B' : {                                                         # noqa
            'coupling'      : { 'AC'        : 'BAC',  'DC'     : 'BDC' },    # noqa
            'attenuation'   : { 'X1'        : 'BAD',  'X10'    : 'BAE' },    # noqa
            'trigger'       : { 'auto'      : 'BAU',  'manual' : 'BMN' },    # noqa
            'impedance'     : { '50'        : 'BLI',  '1M'     : 'BHI' },    # noqa
            'slope'         : { 'pos'       : 'BPS',  'neg'    : 'BNS' },    # noqa
            'input_select'  : { 'separate'  : 'BCS',  'common' : 'BCC' },    # noqa
            'trigger_level' : None,                                     # noqa
            },
    }

    operating_modes = {
        'self_check'      : 'CK',    # noqa
        'frequency_a'     : 'FA',    # noqa
        'period_a'        : 'PA',    # noqa
        'phase_a_rel_b'   : 'PH',    # noqa
        'ratio_a_to_b'    : 'RA',    # noqa
        'ratio_c_to_b'    : 'RC',    # noqa
        'interval_a_to_b' : 'TI',    # noqa
        'total_a_by_b'    : 'TA',    # noqa
        'frequency_c'     : 'FC',    # noqa
    }

    @staticmethod
    def decode(v, allowed_types=None):
        """Decode received message.

        All values returned follow the same format: 2 letters to indicate
        the type of the value returned, followed by a floating point number
        (which could be an integer, of course.)
        This here, for example, is math constant Z: MZ+001.00000000E+00
        """
        if len(v) != 19:
            raise ReturnValueError("Length of instrument response must always be 19 characters")

        val_type = v[0:2]
        val = float(v[2:19])

        if allowed_types and val_type not in allowed_types:
            raise ValueError(f"Unexpected value type returned: '{val_type}'")

        if val_type in Racal1992.int_types:
            return int(val)
        elif val_type in Racal1992.float_types:
            return val
        else:
            raise ValueError("Unsupported return type")

    operating_mode = Instrument.setting(
            "%s",
            """Set operating mode.

            Permitted modes are:
                'self_check',
                'frequency_a',
                'period_a',
                'phase_a_rel_b',
                'ratio_a_to_b',
                'ratio_c_to_b',
                'interval_a_to_b',
                'total_a_by_b',
                'frequency_c'
            """,
            set_process=(lambda mode: Racal1992.operating_modes[mode]),
        )

    resolution = Instrument.control(
            "RRS",
            "SRS %d",
            """Control the resolution of the counter with an integer from 3 to 10 that
            specifies the number of significant digits. """,
            get_process=(lambda v: Racal1992.decode(v, "RS"))
        )

    delay_enable = Instrument.setting(
            "D%s",
            """Control delay. True=enable, False=disable""",
            values={True: "E", False: "D"},
            map_values=True
        )

    delay_time = Instrument.control(
            "RDT",
            "SDT %f",
            """Control delay time.""",
            get_process=(lambda v: Racal1992.decode(v, "DT"))
        )

    special_function_enable = Instrument.setting(
            "SF%s",
            """Control special function. True=enable, False=disable""",
            values={True: "E", False: "D"},
            map_values=True
        )

    # FIXME: not tested on real instrument!
    special_function_number = Instrument.control(
            "RSF",
            "S%d",
            """Control special function.""",
            get_process=(lambda v: Racal1992.decode(v, "SF"))
        )

    # FIXME: not tested on real instrument!
    total_so_far = Instrument.measurement(
            "RF",
            """Get total number of events so far.""",
            get_process=(lambda v: Racal1992.decode(v, "RF"))
        )

    software_version = Instrument.measurement(
            "RMS",
            "Get instrument software version",
            get_process=(lambda v: Racal1992.decode(v, "MS"))
        )

    gpib_software_version = Instrument.measurement(
            "RGS",
            "Get GPIB software version",
            get_process=(lambda v: Racal1992.decode(v, "GS"))
        )

    device_type = Instrument.measurement(
            "RUT",
            """Get unit device type. Should return 1992 for a Racal-Dana 1992
            or 1991 for a Racal-Dana 1991.""",
            get_process=(lambda v: Racal1992.decode(v, "UT"))
        )

    math_mode = Instrument.setting(
            "M%s",
            """Set math mode. True=enable, False=disable""",
            values={True: "E", False: "D"},
            map_values=True
        )

    math_x = Instrument.control(
            "RMX",
            "SMX %f",
            """Control math constant X.""",
            get_process=(lambda v: Racal1992.decode(v, "MX"))
        )

    math_z = Instrument.control(
            "RMZ",
            "SMZ %f",
            """Control math constant Z.""",
            get_process=(lambda v: Racal1992.decode(v, "MZ"))
        )

    trigger_level_a = Instrument.control(
            "RLA",
            "SLA %f",
            """Control trigger level for channel A""",
            get_process=(lambda v: Racal1992.decode(v, "LA"))
        )

    trigger_level_b = Instrument.control(
            "RLB",
            "SLB %f",
            """Control trigger level for channel B""",
            get_process=(lambda v: Racal1992.decode(v, "LB"))
        )

    def read(self):
        return self.read_bytes(21).decode('utf-8')

    def write(self, s):
        """Add a space in front of all commands that are sent to the
        instrument to work around weird model issue.

        It shouldn't be needed on almost all devices, but it also doesn't hurt.
        And it fixes a real issue that's seen on a few devices."""
        super().write(' ' + s)

    def read_and_decode(self, allowed_types=None):
        v = self.read_bytes(21).decode('utf-8')
        return Racal1992.decode(v, allowed_types)

    # ============================================================
    # Channel-specific settings
    # ============================================================
    def channel_settings(self, channel_name, **settings):
        """Set channel configuration paramters.

        :param channel_name: 'A' or 'B'
        :param settings: one or multiple of the following:

            'coupling'      : 'AC' or 'DC'
            'attenuation'   : 'X1' or 'X10'
            'trigger'       : 'auto' or 'manual'
            'impedance'     : '50' or '1M'
            'slope'         : 'pos' or 'neg'
            'filtering'     : True or False (only allowed for channel A)
            'input_select'  : 'separate' or 'common' (only allowed for channel B)
            'trigger_level' : <floating point number>

        """
        if channel_name not in Racal1992.channel_params:
            raise ValueError("Channel name must by 'A' or 'B'")

        commands = []
        trigger_str = ""

        for setting, value in settings.items():
            if setting not in Racal1992.channel_params[channel_name]:
                raise ValueError(f"Channel {channel_name} does not support a {setting} setting")

            accepted_values = Racal1992.channel_params[channel_name][setting]
            if accepted_values is None:
                # Trigger level has a float parameter...
                # Use special string for that because it's used the
                # last setting of all.
                if value < -51 or value > 51:
                    raise ValueError(f"{value} is out of range for {setting}")
                trigger_str = f"SL{channel_name} {value}"
                continue

            if value not in accepted_values:
                raise ValueError(f"{value} is not an acceptable value for {setting}")

            command = accepted_values[value]
            commands.append(command)

        if trigger_str != "":
            commands.append(trigger_str)

        self.write(" ".join(c for c in commands))

    # ============================================================
    # IP - Instrument Preset
    # ============================================================
    def preset(self):
        """Configure instrument with default presets."""
        self.write('IP')

    # ============================================================
    # RE - Reset measurement
    # ============================================================
    def reset_measurement(self):
        """Reset ongoing measurement."""
        self.write('RE')

    # ============================================================
    # Wait for measurement value
    # ============================================================
    def wait_for_measurement(self, timeout=None, progressDots=False):
        """Wait until a new measurement is available.

        :param timeout: number of seconds to wait before timeout exception.
        :param progressDots: when true, print '.' after each ready-check

        """
        if timeout is not None:
            end_time = time.time() + timeout

        while True:
            if progressDots:
                log.info(".")

            stb = self.adapter.connection.read_stb()
            if stb & 0x10:
                break

            if timeout is not None and time.time() > end_time:
                raise Exception("Timeout while waiting for measurement")

        return stb

    # ============================================================
    # Measured value
    # ============================================================
    @property
    def measured_value(self):
        """Get measured value.

        A Racal-Dana 1992 doesn't return measurement data after a request for
        measurement data. Instead, it fills a FIFO with data whenever it completes
        a measurement. When the FIFO is full, the oldest measurement is removed.

        The FIFO buffer gets cleared when a command is received that requires
        an immediate reply, such reading a setting. It also gets cleared when
        an operating mode is cleared.

        When there is no measurement data, this property will stall until data
        is available. It will also timeout after a time that can be set with the standard
        pyvisa API.

        One can make sure that measurement data is available by first calling
        `wait_for_measurement()`.
        """
        return self.read_and_decode(allowed_types=Racal1992.operating_modes.values())
