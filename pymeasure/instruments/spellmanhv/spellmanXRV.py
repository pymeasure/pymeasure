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

from enum import IntFlag

from pyvisa.constants import InterfaceType

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

# https://www.spellmanhv.com/en/high-voltage-power-supplies/XRV

STX = chr(2)
ETX = chr(3)


class StatusCode(IntFlag):
    HV_ENABLED = 2**0
    INTERLOCK_1_CLOSED = 2**1
    INTERLOCK_2_CLOSED = 2**2
    ECR_MODE_ACTIVE = 2**3  # Emission Current Regulation
    POWER_SUPPLY_FAULT = 2**4
    LOCAL_MODE = 2**5
    FILAMENT_ENABLED = 2**6
    LARGE_FILAMENT = 2**7
    XRAYS_EMINENT = 2**8
    LARGE_FILAMENT_CONFIRMATION = 2**9
    SMALL_FILAMENT_CONFIRMATION = 2**10
    RESERVED1 = 2**11
    RESERVED2 = 2**12
    RESERVED3 = 2**13
    RESERVED4 = 2**14
    POWER_SUPPLY_READY = 2**15
    INTERNAL_INTERLOCK_CLOSED = 2**16


class ErrorCode(IntFlag):
    NO_ERROR = 0
    FILAMENT_SELECT_FAULT = 2**0
    OVER_TEMP_APPROACH = 2**1
    OVER_VOLTAGE = 2**2
    UNDER_VOLTAGE = 2**3
    OVER_CURRENT = 2**4
    UNDER_CURRENT = 2**5
    OVER_TEMP_ANODE = 2**6
    OVER_TEMP_CATHODE = 2**7
    INVERTER_FAULT_ANODE = 2**8
    INVERTER_FAULT_CATHODE = 2**9
    FILAMENT_FEEDBACK_FAULT = 2**10
    ANODE_ARC = 2**11
    CATHODE_ARC = 2**12
    CABLE_CONNECT_ANODE_FAULT = 2**13
    CABLE_CONNECT_CATHODE_FAULT = 2**14
    AC_LINE_MON_ANODE_FAULT = 2**15
    AC_LINE_MON_CATHODE_FAULT = 2**16
    DC_RAIL_MON_ANODE_FAULT = 2**17
    DC_RAIL_MON_FAULT_CATHODE = 2**18
    LVPS_NEG_15_FAULT = 2**19
    LVPS_POS_15_FAULT = 2**20
    WATCH_DOG_FAULT = 2**21
    BOARD_OVER_TEMP = 2**22
    OVERPOWER_FAULT = 2**23
    KV_DIFF = 2**24
    MA_DIFF = 2**25
    INVERTER_NOT_READY = 2**26


class Filament(Channel):
    """A class representing the functions for the filament of the x-ray tube."""

    limit = Channel.control(
        "16",
        "12,%d",
        """Control the filament limit setpoint (int, strictly from 0 to 4095).""",
        check_set_errors=True,
        validator=strict_range,
        values=[0, 4095],
        get_process_list=lambda v: int(v[0]),
        )

    preheat = Channel.control(
        "17",
        "13,%d",
        """Control the filament preheat setpoint (int, strictly from 0 to 4095).""",
        check_set_errors=True,
        validator=strict_range,
        values=[0, 4095],
        get_process_list=lambda v: int(v[0]),
        )

    large_size_enabled = Channel.setting(
        "32,%d",
        """Set the large filament state (bool)""",
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        check_set_errors=True,
        )

    enabled = Channel.setting(
        "70,%d",
        """Set the filament status (bool).""",
        map_values=True,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        check_set_errors=True,
        )


class UnscaledData(Channel):
    """A class to handle the unscaled raw data of the Spellman XRV power supplies."""

    voltage_setpoint = Instrument.control(
        "14",
        "10,%d",
        """Control the voltage setpoint (int, strictly  from ``0`` to ``4095``).""",
        validator=strict_range,
        values=[0, 4095],
        check_set_errors=True,
        cast=int,
        )

    current_setpoint = Instrument.control(
        "15",
        "11,%d",
        """Control the current setpoint (int, strictly from ``0`` to ``4095``).""",
        validator=strict_range,
        values=[0, 4095],
        check_set_errors=True,
        cast=int,
        )

    analog_monitor = Instrument.measurement(
        "19",
        """Measure the analog monitor read backs.

        :return: dict of int from ``0`` to ``4095``

        :dict keys: ``voltage``,
                    ``current``,
                    ``filament``,
                    ``voltage_setpoint``,
                    ``current_setpoint``,
                    ``limit``,
                    ``preheat``,
                    ``anode_current``

        ``voltage_setpoint``, ``current_setpoint``, ``limit``
        and ``preheat``  are for local mode operation only.

        ``anode_current`` is only valid for bipolar units.

        """,
        get_process_list=lambda v: {"voltage": v[0],
                                    "current": v[1],
                                    "filament": v[2],
                                    "voltage_setpoint": v[3],
                                    "current_setpoint": v[4],
                                    "limit": v[5],
                                    "preheat": v[6],
                                    "anode_current": v[7],
                                    },
        cast=int,
        )

    voltage = Instrument.measurement(
        "60",
        """Measure the output voltage (int from ``0`` to ``4095``).""",
        cast=int,
        )

    lvps_monitor = Instrument.measurement(
        "65",
        """Measure the –15 V low voltage power supply (int from ``0`` to ``4095``)""",
        cast=int,
        )

    system_voltages = Instrument.measurement(
        "69",
        """Measure the system voltages.

        :return: dict of int from ``0`` to ``4095``

        :dict keys: ``temperature``,
                    ``reserved``,
                    ``anode``,
                    ``cathode``,
                    ``ac_line_cathode``,
                    ``dc_rail_cathode``,
                    ``ac_line_anode``,
                    ``dc_rail_anode``,
                    ``lvps_pos``,
                    ``lvps_neg``

        """,
        get_process_list=lambda v: {
             "temperature": v[0],
             "reserved": v[1],
             "anode": v[2],
             "cathode": v[3],
             "ac_line_cathode": v[4],
             "dc_rail_cathode": v[5],
             "ac_line_anode": v[6],
             "dc_rail_anode": v[7],
             "lvps_pos": v[8],
             "lvps_neg": v[9],
             },
        cast=int,
        )


class SpellmanXRV(Instrument):
    """A class representing the Spellman XRV series high voltage power supplies."""

    checksum_enabled = True  # RS232 and USB

    filament = Instrument.ChannelCreator(Filament)
    unscaled = Instrument.ChannelCreator(UnscaledData)

    def __init__(self, adapter,
                 name="Spellman XRV HV Power Supply",
                 query_delay=0.15,
                 baud_rate=9600,
                 **kwargs):
        super().__init__(
            adapter, name,
            asrl={'baud_rate': baud_rate},
            read_termination=ETX,
            write_termination=ETX,
            includeSCPI=False,
            timeout=2000,
            **kwargs)

        self.query_delay = query_delay

        # disable checksum for LAN interface
        interface_type = self.adapter.connection.interface_type
        if interface_type is InterfaceType.tcpip:
            self.checksum_enabled = False

        self.set_scaling()

    @staticmethod
    def checksum(string_to_check):
        """Calculate the checksum.

        :param string_to_check: string to calculate the checksum from

        The checksum is computed as follows:
            - Add all the bytes before <CSUM>, except <STX>, into a 16 bit (or larger) word.
              The bytes are added as unsigned integers.
            - Take the two’s complement.
            - Truncate the result down to the eight least significant bits.
            - Clear the most significant bit (bit 7) of the resultant byte, (bitwise AND with
              0x7F).
            - Set the next most significant bit (bit 6) of the resultant byte (bitwise OR with
              0x40).

        Using this method, the checksum is always a number between 0x40 and 0x7F.  The
        checksum can never be confused with the <STX> or <ETX> control characters, since
        these have non overlapping ASCII values.

        """

        ascii_sum = 0
        for char in string_to_check:
            ascii_sum += ord(char)  # add ascii values together

        csb1 = 0x100 - ascii_sum  # two's complement
        csb2 = 0x7F & csb1  # bitwise AND 0x7F: truncate to the last 7 bits
        csb3 = 0x40 | csb2  # bitwise OR 0x40: set bit 6
        return chr(csb3)

    def write(self, command):
        """Write to the instrument.

        Adds <STX> (0x02) in front and checksum + <ETX> (0x03) at end of every command before
        sending it. The checksum is omitted for TCPIP connections.
        """

        command_with_comma = command + ","
        if self.checksum_enabled:
            checksum = self.checksum(command_with_comma)
            super().write(f"{STX}{command_with_comma}{checksum}")
        else:
            super().write(f"{STX}{command_with_comma}")

    def wait_for(self, query_delay=0):
        """Wait for some time.

        :param query_delay: override the global query_delay.
        """
        super().wait_for(query_delay or self.query_delay)

    def read(self):
        """Read from the device and check for errors.

        :raise: ConnectionError if response doesn't start with <STX> or checksum is incorrect.
                The checksum check is omitted for TCPIP connections.
        """
        got = super().read()

        if not got.startswith(STX):
            raise ConnectionError("Expected <STX> at begin of received message.")

        response = got[1:].rpartition(",")

        if self.checksum_enabled:
            string_to_check = response[0] + response[1]
            calculated_checksum = self.checksum(string_to_check)
            got_checksum = response[2]

            if got_checksum is not calculated_checksum:
                string = f"Checksum error: expected '{calculated_checksum}', got '{got_checksum}'."
                raise ConnectionError(string)

        return response[0].partition(",")[2]  # remove command from response

    def check_set_errors(self):
        """Check for errors after sending a command.

        :raise: ValueError if response is not ``$``
        """
        got = self.read()
        expected = "$"
        if got == expected:
            return []
        else:
            string = f"ValueError: expected '{expected}', got '{got}'."
            raise ValueError(string)

    def set_scaling(self):
        """Set the scaling factors.

        Used to set the scaling factor for
        :attr:`analog_monitor`,
        :attr:`current_setpoint`,
        :attr:`voltage`,
        :attr:`voltage_setpoint` and
        :attr:`system_voltages`.

        """

        max_values = self.scaling
        max_voltage = max_values["voltage"]
        max_current = max_values["current"]

        # scaling for DAC
        bits_per_volt = 4095/max_voltage  # bits/Volt
        bits_per_amp = 4095/max_current  # bits/Amp

        self.voltage_setpoint_values = [0, max_voltage]
        self.voltage_setpoint_set_process = lambda volts: round(volts*bits_per_volt)
        self.voltage_setpoint_get_process = lambda bits: round(bits/bits_per_volt)

        self.current_setpoint_values = [0, max_current]
        self.current_setpoint_set_process = lambda amps: round(amps*bits_per_amp)
        self.current_setpoint_get_process = lambda bits: round(bits/bits_per_amp, 7)

        # Scaling for analog monitors, ADC has 20% overrange
        adc_volts_per_bit = 1.2*max_voltage/4095  # Volts/bit
        adc_amps_per_bit = 1.2*max_current/4095  # Amps/bit

        self.system_voltages_get_process_list = lambda v: {
             "temperature": 0.05911815*int(v[0]),
             "reserved": int(v[1]),
             "anode": adc_volts_per_bit*int(v[2]),
             "cathode": adc_volts_per_bit*int(v[3]),
             "ac_line_cathode": 0.088610*int(v[4]),
             "dc_rail_cathode": 0.11399241*int(v[5]),
             "ac_line_anode": 0.088610*int(v[6]),
             "dc_rail_anode": 0.11399241*int(v[7]),
             "lvps_pos": 0.00427407*int(v[8]),
             "lvps_neg": 0.00576703*int(v[9]),
             }

        self.voltage_get_process = lambda bits: round(bits*adc_volts_per_bit)

        self.analog_monitor_get_process_list = lambda v: {
            "voltage": adc_volts_per_bit*int(v[0]),
            "current": adc_amps_per_bit*int(v[1]),
            "filament": int(v[2]),
            "voltage_setpoint": int(v[3]),
            "current_setpoint": int(v[4]),
            "limit": int(v[5]),
            "preheat": int(v[6]),
            "anode_current": adc_amps_per_bit*int(v[7]),
            }

    baudrate = Instrument.setting(
        "07,%d",
        """
        Set the baud rate (int, strictly in ``9600``, ``19200``, ``38400``, ``57600``, ``115200``).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={9600: 1,
                19200: 2,
                38400: 3,
                57600: 4,
                115200: 5},
        check_set_errors=True,
        )

    voltage_setpoint = Instrument.control(
        "14",
        "10,%d",
        """Control the voltage setpoint in Volts (float).""",
        validator=strict_range,
        dynamic=True,
        check_set_errors=True,
        )

    current_setpoint = Instrument.control(
        "15",
        "11,%d",
        """Control the current setpoint in Amps (float).""",
        validator=strict_range,
        dynamic=True,
        check_set_errors=True,
        )

    analog_monitor = Instrument.measurement(
        "19",
        """Measure the analog monitor read backs.

        :return: dict

        :dict keys:
            ``voltage``,
            ``current``,
            ``filament``,
            ``voltage_setpoint``,
            ``current_setpoint``,
            ``limit``,
            ``preheat``,
            ``anode_current``

        """,
        dynamic=True
        )

    hv_on_timer = Instrument.measurement(
        "21",
        """Get the HV On time in hours (float).""",
        )

    status = Instrument.measurement(
        "22",
        """Get the power supply status (:code:`StatusCode` enum).""",
        get_process_list=lambda v: StatusCode(int(''.join(map(str, (v[::-1]))), 2)),
        cast=int
        )

    dsp = Instrument.measurement(
        "23",
        """Get the DSP part number and version (list).""",
        )

    configuration = Instrument.measurement(
        "27",
        """Get the power supply configuration.

        :return: dict

        :dict keys: ``reserved1``,
                    ``over_voltage_percentage``,
                    ``voltage_ramp_rate``,
                    ``current_ramp_rate``,
                    ``pre_warning_time``,
                    ``arc_count``,
                    ``reserved2``,
                    ``quench_time``,
                    ``max_kV``,
                    ``max_mA``,
                    ``watchdog_timer``

        """,
        get_process_list=lambda v: {"reserved1": v[0],
                                    "over_voltage_percentage": v[1],
                                    "voltage_ramp_rate": v[2],
                                    "current_ramp_rate": v[3],
                                    "pre_warning_time": v[4],
                                    "arc_count": v[5],
                                    "reserved2": v[6],
                                    "quench_time": v[7],
                                    "max_kV": v[9],
                                    "max_mA": v[10],
                                    "watchdog_timer": v[11],
                                    },
        )

    scaling = Instrument.measurement(
        "28",
        """Get scaling factors and polarity.

        :return: dict

        :dict keys: ``voltage``, ``current``, ``polarity``

        ``voltage`` is in V,
        ``current`` is in A,
        ``polarity`` 0: uni-polar,
        ``polarity`` 1: bipolar

        """,
        get_process_list=lambda v: {"voltage": int(v[0] * 1000),
                                    "current": float(v[1]) * 1e-3,
                                    "polarity": int(v[2]),
                                    },
        )

    def reset_hv_on_timer(self):
        self.ask("30")

    def reset_errors(self):
        self.ask("31")

    power_limits = Instrument.control(
        "38",
        "97,%d,%d",
        """Control the power limits in Watts (list of int).

        index = 0: power limit for large filament
        index = 1: power limit for small filament

        :raise: ValueError if limit is out of range
        """,
        get_process_list=lambda v: [v[0], v[1]],
        check_set_errors=True,
        cast=int,
        )

    fpga = Instrument.measurement(
        "43",
        """Get the FPGA part number and version (list).""",
        )

    errors = Instrument.measurement(
        "68",
        """Get the power supply errors (enum).""",
        get_process_list=lambda v: ErrorCode(int(''.join(map(str, (v[::-1]))), 2)),
        cast=int
        )

    output_enabled = Instrument.control(
        "22",
        "98,%d",
        """Control the high voltage output (bool).""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: 1, False: 0},
        get_process_list=lambda v: bool(v[0]),
        check_set_errors=True,
        )

    voltage = Instrument.measurement(
        "60",
        """Measure the output voltage in Volts (float).""",
        dynamic=True
        )

    system_voltages = Instrument.measurement(
        "69",
        """Measure the system voltages in Volts.

        :return: dict

        :dict keys: ``temperature``,
                    ``reserved``,
                    ``anode``,
                    ``cathode``,
                    ``ac_line_cathode``,
                    ``dc_rail_cathode``,
                    ``ac_line_anode``,
                    ``dc_rail_anode``,
                    ``lvps_pos``,
                    ``lvps_neg``

        """,
        dynamic=True
        )

    temperature = Instrument.measurement(
        "69",
        """Measure the system temperature in °C (float).""",
        get_process_list=lambda v: 0.05911815*int(v[0])
        )
