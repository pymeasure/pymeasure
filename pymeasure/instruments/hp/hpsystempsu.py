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

import ctypes
import logging

from enum import Enum
from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument, StatusBitsBase
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8


class Status(StatusBitsBase):
    """
    Support-Class with the bit assignments for the 2 status byte(12bits used) of the HP6632A
    """

    _fields_ = [
        # Byte 1: Function, Range and Number of Digits
        ("Error_pending", c_uint8, 1),  # bit 7
        ("Overcurrent", c_uint8, 1),  # bit 6
        ("not_assigned", c_uint8, 1),  # bit 5
        ("Overtempeature", c_uint8, 1),  # bit 4
        ("Overvoltage", c_uint8, 1),  # bit 3
        ("Unregulated", c_uint8, 1),  # bit 2
        ("CCpos", c_uint8, 1),  # bit 1
        ("CV", c_uint8, 1),  # bit 0

        # Byte 2: Status Bits
        ("not_assigned", c_uint8, 4),  # bits 16..12
        ("NORM", c_uint8, 1),  # bit 11
        ("FAST", c_uint8, 1),  # bit 10
        ("CCneg", c_uint8, 1),  # bit 9
        ("Inhibit_active", c_uint8, 1),  # bit 8

    ]


limits = {
    "HP6632A": {"Volt_lim": 20.475, "OVP_lim": 22.0, "Cur_lim": 5.118},
    "HP6633A": {"Volt_lim": 51.118, "OVP_lim": 55.0, "Cur_lim": 2.0475},
    "HP6634A": {"Volt_lim": 102.38, "OVP_lim": 110.0, "Cur_lim": 1.0238}}


class HP6632A(HPLegacyInstrument):
    """ Represents the Hewlett Packard 6632A system power supply
    and provides a high-level interface for interacting
    with the instrument.
    """
    status_desc = Status

    def __init__(self, adapter, name="Hewlett-Packard HP6632A", **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

    class ERRORS(Enum):
        """
        Enum class for error messages

        """
        NO_ERR = 0
        EEPROM = 1
        PON_2ND = 2
        DCPON_2MD = 4
        NORELAY = 5
        NOTHING_SAY = 8
        HEADER_EXPECTED = 10
        UNRECOGNISED_HEADER = 11
        NUMBER_EXPECTED = 20
        NUMBER_SYNTAX = 21
        OUT_OF_RANGE = 22
        COMMA_EXPECTED = 30
        TERM_EXPECTED = 31
        PARAM_OUT = 41
        V_PGM_ERR = 42
        I_PGM_ERR = 43
        OV_PGM_ERR = 44
        DLY_PGM_ERR = 45
        MASK_PGM_ERR = 46
        MULT_CSAVE_ERR = 50
        EEPROM_CJLSUM_ERR = 51
        CALMODE_DISABLED = 52
        CAL_CHNL_ERR = 53
        CAL_FS_ERR = 54
        CAL_OFFSET = 55
        CAL_JMP_ERR = 59

    class ST_ERRORS(Enum):
        """
        Enum class for selftest errors

        """
        NO_ST_ERR = 0
        ROM_CKSSUM = 1
        RAM_TEST = 2
        HPIB_CHIP = 3
        HPIB_TIMER_SLOW = 4
        HPIB_TIMER_FAST = 5
        PSI_ROM_CHKSUM = 11
        PSI_RAM_TEST = 12
        PSI_TIMER_SLOW = 14
        PSI_TIMER_FAST = 15
        AD_TEST_HIGH = 16
        AD_TEST_LOW = 17
        CCCV_ZERO_HIGH = 18
        CCCV_ZERO_LOW = 19
        CV_REF_HIGH = 20
        CV_REF_LOW = 21
        CC_REF_HIGH = 22
        CC_REF_LOW = 23
        DAC_FAIL = 24
        EEPROM_CHKSUM = 51

    def check_errors(self):
        """
        Method to read the error status register

        :return error_status: one byte with the error status register content
        :rtype error_status: int
        """
        # Read the error status register only one time for this method, as
        # the manual states that reading the error status register also clears it.
        current_errors = int(self.ask("ERR?"))
        if current_errors != 0:
            log.error("HP6632 Error detected: %s", self.ERRORS(current_errors))
        return self.ERRORS(current_errors)

    def check_selftest_errors(self):
        """
        Method to read the error status register

        :return error_status: one byte with the error status register content
        :rtype error_status: int
        """
        # Read the error status register only one time for this method, as
        # the manual states that reading the error status register also clears it.
        current_errors = int(self.ask("TEST?"))
        if current_errors != 0:
            log.error("HP6632 Error detected: %s", self.ERRORS(current_errors))
        return self.ST_ERRORS(current_errors)

    def clear(self):
        """
        Resets the instrument to power-on default settings

        """
        self.write("CLR")

    delay = HPLegacyInstrument.setting(
        "DELAY %g",
        """
        A float property that changes the reprogamming delay
        Default values:
        8 ms in FAST mode
        80 ms in NORM mode

        Values will be rounded to the next 4 ms by the instrument

        """,
        validator=strict_range,
        values=[0, 32.768],
    )

    display_active = HPLegacyInstrument.setting(
        "DIS %d",
        """
        A boot property which controls if the display is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    @property
    def status(self):
        """
        Returns an object representing the current status of the unit.

        """
        # overloading the already existing property because of the different command
        reply = bytearray(int(self.ask("STS?")).to_bytes(
            self.status_bytes_count, "little"))
        return self.status_bits.from_buffer(reply)

    id = HPLegacyInstrument.measurement(
        "ID?",
        """
        Reads the ID of the instrument and returns this value for now

        """,
    )

    current = HPLegacyInstrument.control(
        "IOUT?", "ISET %g",
        """
        A floating point property that controls the output current of the device.

        """,
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6632A"]["Cur_lim"]],
    )

    over_voltage_limit = HPLegacyInstrument.setting(
        "OVSET %g",
        """
        A floationg point property that sets the OVP threshold.

        """,
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6632A"]["OVP_lim"]],
    )

    OCP_enabled = HPLegacyInstrument.setting(
        "OCP %d",
        """
        A bool property which controls if the OCP (OverCurrent Protection) is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    output_enabled = HPLegacyInstrument.setting(
        "OUT %d",
        """
        A bool property which controls if the outputis enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    @output_enabled.getter
    def output_enabled(self):
        """
        A bool property which controls if the output is enabled
        """
        output_status = bool(self.status.CV or self.status.CCpos or
                             self.status.CCneg or self.status.Unregulated)
        return output_status

    def reset_OVP_OCP(self):
        """
        Resets Overvoltage and Overcurrent protections

        """
        self.write("RST")

    rom_version = HPLegacyInstrument.measurement(
        "ROM?",
        """
        Reads the ROM id (software version) of the instrument and returns this value for now

        """,
    )

    SRQ_enabled = HPLegacyInstrument.setting(
        "SRQ %d",
        """
        A bool property which controls if the SRQ (ServiceReQuest) is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    voltage = HPLegacyInstrument.control(
        "VOUT?", "VSET %g",
        """
        A floating point proptery that controls the output voltage of the device.

        """,
        dynamic=True,
        validator=strict_range,
        values=[0, limits["HP6632A"]["Volt_lim"]],
    )


class HP6633A(HP6632A):
    """ Represents the Hewlett Packard 6633A system power supply
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, adapter, name="Hewlett Packard HP6633A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    current_values = [0, limits["HP6633A"]["Cur_lim"]]
    OVP_values = [0, limits["HP6633A"]["OVP_lim"]]
    voltage_values = [0, limits["HP6633A"]["Volt_lim"]]


class HP6634A(HP6632A):
    """ Represents the Hewlett Packard 6634A system power supply
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, adapter, name="Hewlett Packard HP6634A", **kwargs):
        super().__init__(adapter, name, **kwargs)

    current_values = [0, limits["HP6634A"]["Cur_lim"]]
    OVP_values = [0, limits["HP6634A"]["OVP_lim"]]
    voltage_values = [0, limits["HP6634A"]["Volt_lim"]]
