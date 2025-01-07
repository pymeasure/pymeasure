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
import math
from enum import IntFlag
from pymeasure.instruments.hp.hplegacyinstrument import HPLegacyInstrument, StatusBitsBase
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8


class SRQ(ctypes.BigEndianStructure):
    """Support class for the SRQ handling
    """
    _fields_ = [
        ("power_on", c_uint8, 1),
        ("not_assigned_1", c_uint8, 1),
        ("calibration", c_uint8, 1),
        ("front_panel_button", c_uint8, 1),
        ("internal_error", c_uint8, 1),
        ("syntax_error", c_uint8, 1),
        ("not_assigned_2", c_uint8, 1),
        ("data_ready", c_uint8, 1),
    ]

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"

        return ret_str


class Status(StatusBitsBase):
    """
    Support-Class with the bit assignments for the 5 status byte of the HP3478A
    """

    _fields_ = [
        # Byte 1: Function, Range and Number of Digits
        ("function", c_uint8, 3),  # bit 5..7
        ("range", c_uint8, 3),  # bit 2..4
        ("digits", c_uint8, 2),  # bit 0..1
        # Byte 2: Status Bits
        ("res1", c_uint8, 1),
        ("ext_trig", c_uint8, 1),
        ("cal_enable", c_uint8, 1),
        ("front_rear", c_uint8, 1),
        ("fifty_hz", c_uint8, 1),
        ("auto_zero", c_uint8, 1),
        ("auto_range", c_uint8, 1),
        ("int_trig", c_uint8, 1),
        # Byte 3: Serial Poll Mask (SRQ)
        # ("SRQ_PON", c_uint8, 1),
        # ("res3", c_uint8, 1),
        # ("SRQ_cal_error", c_uint8, 1),
        # ("SRQ_front_panel", c_uint8, 1),
        # ("SRQ_internal_error", c_uint8, 1),
        # ("SRQ_syntax_error", c_uint8, 1),
        # ("res2", c_uint8, 1),
        # ("SRQ_data_rdy", c_uint8, 1),
        ("SRQ", SRQ),
        # Byte 4: Error Information
        # ("res5", c_uint8, 1),
        # ("res4", c_uint8, 1),
        # ("ERR_AD_Link", c_uint8, 1),
        # ("ERR_AD", c_uint8, 1),
        # ("ERR_slope", c_uint8, 1),
        # ("ERR_ROM", c_uint8, 1),
        # ("ERR_RAM", c_uint8, 1),
        # ("ERR_cal", c_uint8, 1),
        ("Error_Status", c_uint8, 8),
        # Byte 5: DAC Value
        ("DAC_value", c_uint8, 8),
    ]


class HP3478A(HPLegacyInstrument):
    """ Represents the Hewlett Packard 3478A 5 1/2 digit multimeter
    and provides a high-level interface for interacting
    with the instrument.
    """
    status_desc = Status

    def __init__(self, adapter, name="Hewlett-Packard HP3478A", **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            adapter,
            name,
            **kwargs,
        )

    # Definitions for different specifics of this instrument
    MODES = {"DCV": "F1",
             "ACV": "F2",
             "R2W": "F3",
             "R4W": "F4",
             "DCI": "F5",
             "ACI": "F6",
             "Rext": "F7",
             }

    INV_MODES = {v: k for k, v in MODES.items()}

    RANGES = {"DCV": {3E-2: "R-2", 3E-1: "R-1", 3: "R0", 30: "R1", 300: "R2",
                      "auto": "RA"},
              "ACV": {3E-1: "R-1", 3: "R0", 30: "R1", 300: "R2", "auto": "RA"},
              "R2W": {30: "R1", 300: "R2", 3E3: "R3", 3E4: "R4", 3E5: "R5",
                      3E6: "R6", 3E7: "R7", "auto": "RA"},
              "R4W": {30: "R1", 300: "R2", 3E3: "R3", 3E4: "R4", 3E5: "R5",
                      3E6: "R6", 3E7: "R7", "auto": "RA"},
              "DCI": {3E-1: "R-1", 3: "R0", "auto": "RA"},
              "ACI": {3E-1: "R-1", 3: "R0", "auto": "RA"},
              "Rext": {3E7: "R7", "auto": "RA"},
              }

    TRIGGERS = {
        "auto": "T1",
        "internal": "T1",
        "external": "T2",
        "single": "T3",
        "hold": "T4",
        "fast": "T5",
    }

    class ERRORS(IntFlag):
        """Enum element for errror bit decoding
        """
        AD_LINK = 32  # AD link error
        AD_SELFCHK = 16  # AD self check error
        AD_SLOPE = 8  # AD slope error
        ROM = 4  # Control ROM error
        RAM = 2  # RAM selftest failed
        CALIBRATION = 1  # Calibration checksum error or cal range issue
        NO_ERR = 0  # Should be obvious

    # commands/properties for instrument control
    @property
    def active_connectors(self):
        """Return selected connectors ("front"/"back"), based on front-panel selector switch
        """
        selection = self.status.front_rear
        if selection == 1:
            return "front"
        else:
            return "back"

    @property
    def auto_range_enabled(self):
        """ Property describing the auto-ranging status

        ======  ============================================
        Value   Status
        ======  ============================================
        True    auto-range function activated
        False   manual range selection / auto-range disabled
        ======  ============================================

        The range can be set with the :py:attr:`range` property
        """
        selection = self.status.auto_range
        return bool(selection)

    @property
    def auto_zero_enabled(self):
        """ Return auto-zero status, this property can be set

        ======  ==================
        Value   Status
        ======  ==================
        True    auto-zero active
        False   auto-zero disabled
        ======  ==================

        """
        selection = self.status.auto_zero
        return bool(selection)

    @auto_zero_enabled.setter
    def auto_zero_enabled(self, value):
        az_set = int(value)
        az_str = "Z" + str(int(strict_discrete_set(az_set, [0, 1])))
        self.write(az_str)

    @property
    def calibration_enabled(self):
        """Return calibration enable switch setting,
        based on front-panel selector switch

        ======  ===================
        Value   Status
        ======  ===================
        True    calbration possible
        False   calibration locked
        ======  ===================

        """
        selection = self.status.cal_enable
        return bool(selection)

    def check_errors(self):
        """
        Method to read the error status register

        :return error_status: one byte with the error status register content
        :rtype error_status: int
        """
        # Read the error status register only one time for this method, as
        # the manual states that reading the error status register also clears it.
        current_errors = self.error_status
        if current_errors != 0:
            log.error("HP3478A error detected: %s", self.ERRORS(current_errors))
        return self.ERRORS(current_errors)

    error_status = HPLegacyInstrument.measurement(
        "E",
        """Checks the error status register

        """,
        cast=int,
    )

    def display_reset(self):
        """ Reset the display of the instrument.

        """
        self.write("D1")

    display_text = HPLegacyInstrument.setting(
        "D2%s",
        """Displays up to 12 upper-case ASCII characters on the display.

        """,
        set_process=(lambda x: str.upper(x[0:12])),
    )

    display_text_no_symbol = HPLegacyInstrument.setting(
        "D3%s",
        """Displays up to 12 upper-case ASCII characters on the display and
        disables all symbols on the display.

        """,
        set_process=(lambda x: str.upper(x[0:12])),
    )

    measure_ACI = HPLegacyInstrument.measurement(
        MODES["ACI"],
        """
        Returns the measured value for AC current as a float in A.

        """,
    )

    measure_ACV = HPLegacyInstrument.measurement(
        MODES["ACV"],
        """
        Returns the measured value for AC Voltage as a float in V.

        """,
    )

    measure_DCI = HPLegacyInstrument.measurement(
        MODES["DCI"],
        """
        Returns the measured value for DC current as a float in A.

        """,
    )

    measure_DCV = HPLegacyInstrument.measurement(
        MODES["DCV"],
        """
        Returns the measured value for DC Voltage as a float in V.

        """,
    )

    measure_R2W = HPLegacyInstrument.measurement(
        MODES["R2W"],
        """
        Returns the measured value for 2-wire resistance as a float in Ohm.

        """,
    )

    measure_R4W = HPLegacyInstrument.measurement(
        MODES["R4W"],
        """
        Returns the measured value for 4-wire resistance as a float in Ohm.

        """,
    )

    measure_Rext = HPLegacyInstrument.measurement(
        MODES["Rext"],
        """
        Returns the measured value for extended resistance mode (>30M, 2-wire)
        resistance as a float in Ohm.
        """,
    )

    @property
    def mode(self):
        """Return current selected measurement mode, this propery can be set.
        Allowed values are

        ====  ==============================================================
        Mode  Function
        ====  ==============================================================
        ACI   AC current
        ACV   AC voltage
        DCI   DC current
        DCV   DC voltage
        R2W   2-wire resistance
        R4W   4-wire resistance
        Rext  extended resistance method (requires additional 10 M resistor)
        ====  ==============================================================
        """
        current_mode = self.INV_MODES["F" + str(self.status.function)]
        return current_mode

    @mode.setter
    def mode(self, value):
        mode_set = self.MODES[strict_discrete_set(value, self.MODES)]
        self.write(mode_set)

    @property
    def range(self):
        """Returns the current measurement range, this property can be set.

        Valid values are :

        ====  =======================================
        Mode  Range
        ====  =======================================
        ACI   0.3, 3, auto
        ACV   0.3, 3, 30, 300, auto
        DCI   0.3, 3, auto
        DCV   0.03, 0.3, 3, 30, 300, auto
        R2W   30, 300, 3000, 3E4, 3E5, 3E6, 3E7, auto
        R4W   30, 300, 3000, 3E4, 3E5, 3E6, 3E7, auto
        Rext  3E7, auto
        ====  =======================================

        """
        cur_mode = self.INV_MODES["F" + str(self.status.function)]
        if cur_mode == "DCV":
            correction_factor = 3
        elif cur_mode in ["ACV", "ACI", "DCI"]:
            correction_factor = 2
        else:
            correction_factor = 0
        current_range = 3 * math.pow(10, self.status.range - correction_factor)
        return current_range

    @range.setter
    def range(self, value):
        cur_mode = self.mode
        value = strict_discrete_set(value, self.RANGES[cur_mode])
        set_range = self.RANGES[cur_mode][value]
        self.write(set_range)

    @property
    def resolution(self):
        """Returns current selected resolution, this property can be set.

        Possible values are 3,4 or 5 (for 3 1/2, 4 1/2 or 5 1/2 digits of resolution)
        """
        number_of_digit = 6 - self.status.digits
        return number_of_digit

    @resolution.setter
    def resolution(self, value):
        resolution_string = "N" + str(strict_discrete_set(value, [3, 4, 5]))
        self.write(resolution_string)

    @property
    def SRQ_mask(self):
        """Return current SRQ mask, this property can be set,

        bit assigment for SRQ:

        =========  ==========================
        Bit (dec)  Description
        =========  ==========================
         1         SRQ when Data ready
         4         SRQ when Syntax error
         8         SRQ when internal error
        16         front panel SQR button
        32         SRQ by invalid calibration
        =========  ==========================

        """

        return self.status.SRQ

    @SRQ_mask.setter
    def SRQ_mask(self, value):
        self.write(f"M{strict_range(value, [0, 63]):02o}")

    @property
    def trigger(self):
        """Return current selected trigger mode, this property can be set

        Possibe values are:

        ========  ===========================================
        Value     Meaning
        ========  ===========================================
        auto      automatic trigger (internal)
        internal  automatic trigger (internal)
        external  external trigger (connector on back or GET)
        hold      holds the measurement
        fast      fast trigger for AC measurements
        ========  ===========================================

        """
        status = self.status
        i_trig = status.int_trig
        e_trig = status.ext_trig
        if i_trig == 0:
            if e_trig == 0:
                trigger_mode = "hold"
            else:
                trigger_mode = "external"
        else:
            trigger_mode = "internal"
        return trigger_mode

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)

    @property
    def calibration_data(self):
        """Read or write the calibration data as an array of 256 values between 0 and 15.

        The calibration data of an HP 3478A is stored in a 256x4 SRAM that is
        permanently powered by a 3v Lithium battery. When the battery runs
        out, the calibration data is lost, and recalibration is required.

        When read, this property fetches and returns the calibration data so that it can be
        backed up.

        When assigned a value, it similarly expects an array of 256 values between 0 and 15,
        and writes the values back to the instrument.

        When writing, exceptions are raised for the following conditions:

        * The CAL ENABLE switch at the front of the instrument is not set to ON.
        * The array with values does not contain exactly 256 elements.
        * The array with values does not pass a verification check.

        IMPORTANT: changing the calibration data results in permanent loss of
        the previous data. Use with care!

        """
        cal_data = []
        for addr in range(0, 256):
            # To fetch one nibble: 'W<address>', where address is a raw 8-bit number.
            cmd = bytes([ord('W'), addr])
            self.write_bytes(cmd)
            rvalue = self.read_bytes(1)[0]
            # 'W' command reads a nibble from the SRAM, but then adds a value of 64 to return
            # it as an ASCII value.
            if rvalue < 64 or rvalue >= 80:
                raise Exception("calibration nibble out of range")
            cal_data.append(rvalue-64)

        return cal_data

    @calibration_data.setter
    def calibration_data(self, cal_data):
        """Setter to write the calibration data.

        """

        if not self.calibration_enabled:
            raise Exception("CAL ENABLE switch not set to ON")

        self.write_calibration_data(cal_data, True)

    def write_calibration_data(self, cal_data, verify_calibration_data=True):
        """Method to write calibration data.

        The cal_data parameter format is the same as the ``calibration_data`` property.

        Verification of the cal_data array can be bypassed by setting
        ``verify_calibration_data`` to ``False``.

        """
        if verify_calibration_data and not self.verify_calibration_data(cal_data):
            raise ValueError("cal_data verification fail.")

        for addr in range(0, 256):
            # To write one nibble: 'X<address><byte>', where address and byte are raw 8-bit numbers.
            cmd = bytes([ord('X'), addr, cal_data[addr]])
            self.write_bytes(cmd)
        pass

    def verify_calibration_entry(self, cal_data, entry_nr):
        """Verify the checksum of one calibration entry.

        Expects an array of 256 values with calibration data, and an entry
        number from 0 to 18.

        Returns True when the checksum of the specified calibration entry
        is correct.

        """
        if len(cal_data) != 256:
            raise Exception("cal_data must contain 256 values")

        sum = 0
        for idx in range(0, 13):
            val = cal_data[entry_nr*13 + idx + 1]
            if idx != 11:
                sum += val
            else:
                sum += val*16
        return sum == 255

    def verify_calibration_data(self, cal_data):
        """Verify the checksums of all calibration entries.

        Expects an array of 256 values with calibration data.

        :return calibration_correct: True when all checksums are correct.
        :rtype calibration_correct: boolean

        """
        for entry_nr in range(0, 19):
            if entry_nr in [5, 16, 18]:
                continue
            if not self.verify_calibration_entry(cal_data, entry_nr):
                return False
        return True
