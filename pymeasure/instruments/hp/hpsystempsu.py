#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

from enum import IntFlag, Enum
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8


# classes for the decoding of the 12-bit status word


class Status_bytes(ctypes.Structure):
    """
    Support-Class for the 5 status byte of the HP6632A
    """
    _fields_ = [
        ("byte1", c_uint8),
        ("byte2", c_uint8)
    ]


class Status_bits(ctypes.LittleEndianStructure):
    """
    Support-Class with the bit assignments for the 2 status byte(12bits used) of the HP6632A
    """

    _fields_ = [
        # Byte 1: Function, Range and Number of Digits
        ("CV",                  c_uint8, 1),  # bit 0
        ("CCpos",                 c_uint8, 1),  # bit 1
        ("Unregulated",         c_uint8, 1),  # bit 2
        ("Overvoltage",        c_uint8, 1),  # bit 3
        ("Overtempeature",     c_uint8, 1),  # bit 4
        ("not_assigned",        c_uint8, 1),  # bit 5
        ("Overcurrent",        c_uint8, 1),  # bit 6
        ("Error_pending",       c_uint8, 1),  # bit 7


        # Byte 2: Status Bits
        ("Inhibit_active",      c_uint8, 1),  # bit 8
        ("CCneg",                 c_uint8, 1),  # bit 9
        ("FAST",    c_uint8, 1),  # bit 10
        ("NORM",    c_uint8, 1),  # bit 11
        ("not_assigned",        c_uint8, 4),

    ]

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"

        return ret_str


class Status(ctypes.Union):
    """Union type element for the decoding of the status bit-fields
    """
    _fields_ = [
        ("B", Status_bytes),
        ("b", Status_bits)
    ]


class HP6632A(Instrument):
    """ Represents the Hewlett Packard 6632A system power supply
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            resourceName,
            "Hewlett-Packard HP6632A",
            **kwargs,
        )

    class ERRORS(Enum):
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

    class SRQ (IntFlag):
        RQS = 64
        ERR = 32
        RDY = 16
        PON = 2
        FAU = 1

    def check_errors(self):
        """
        Method to read the error status register

        :return error_status: one byte with the error status register content
        :rtype error_status: int
        """
        # Read the error status reigster only one time for this method, as
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
        # Read the error status reigster only one time for this method, as
        # the manual states that reading the error status register also clears it.
        current_errors = int(self.ask("TEST?"))
        if current_errors != 0:
            log.error("HP6632 Error detected: %s", self.ERRORS(current_errors))
        return self.ERRORS(current_errors)

    def clear(self):
        """
        Resets the instrument to Power-on default settings

        """
        self.write("CLR")

    delay = Instrument.setting(
        "DELAY %g",
        """
        A float propery that changes the reprogamming delay
        Default values:
        8 ms in FAST mode
        80 ms in NORM mode

        Values will be rounded to the next 4 ms by the instrument

        """,
        validator=strict_range,
        values=[0, 32.768],
    )

    display_active = Instrument.setting(
        "DIS %d",
        """
        A boot property which controls if the OCP (OverCurrent Protection) is enabled
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
        current_status = self.decode_status(self, self.fetch_status())
        return current_status

    def fetch_status(self):
        """Method to read the status bytes from the instrument
        :return current_status: a byte array representing the instrument status
        :rtype current_status: bytes
        """
        current_status = int(self.ask("STS?")).to_bytes(2, "little")
        return current_status

    @staticmethod
    def decode_status(self, status_bytes, field=None):
        """Method to handle the decoding of the status bytes into something meaningfull

        :param status_bytes: list of bytes to be decoded
        :param field: name of field to be returned
        :return ret_val: int status value

        """
        ret_val = Status(Status_bytes(*status_bytes))
        if field is None:
            return ret_val.b
        return getattr(ret_val.b, field)

    id = Instrument.measurement(
        "ID?",
        """
        Reads the ID of the instrument and returns this value for now

        """,
    )

    current = Instrument.control(
        "IOUT?", "ISET %g",
        """
        A floating point proptery that controls the output current of the device.

        """,
        validator=strict_range,
        values=[0, 5.1188],
    )

    over_voltage_limit = Instrument.setting(
        "OVSET %g",
        """
        A floationg point property that sets the OVP threshold.

        """,
        validator=strict_range,
        values=[0, 22.0],
    )

    OCP_enabled = Instrument.setting(
        "OCP %d",
        """
        A boot property which controls if the OCP (OverCurrent Protection) is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    output_enabled = Instrument.setting(
        "OUT %d",
        """
        A boot property which controls if the OCP (OverCurrent Protection) is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    @output_enabled.getter
    def output_enabled(self):
        output_status = bool(self.status.CV or self.status.CCpos or
                             self.status.CCneg or self.status.Unregulated)
        return(output_status)

    def reset_OVP_OCP(self):
        """
        Resets Overvoltage and Overcurrent protections

        """
        self.write("RST")

    rom_Version = Instrument.measurement(
        "ROM?",
        """
        Reads the ROM id (software version) of the instrument and returns this value for now

        """,
    )

    SRQ_enabled = Instrument.setting(
        "SRQ %d",
        """
        A boot property which controls if the SRQ (ServiceReQuest) is enabled
        """,
        validator=strict_discrete_set,
        values={False: 0, True: 1},
        map_values=True
    )

    voltage = Instrument.control(
        "VOUT?", "VSET %g",
        """
        A floating point proptery that controls the output voltage of the device.

        """,
        validator=strict_range,
        values=[0, 20.475],
    )
