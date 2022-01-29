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

import ctypes
import logging
import math
from enum import IntFlag
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, strict_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8

# classes for the decoding of the 5-byte status word


class Status_bytes(ctypes.Structure):
    """
    Support-Class for the 5 status byte of the HP3478A
    """
    _fields_ = [
        ("byte1", c_uint8),
        ("byte2", c_uint8),
        ("byte3", c_uint8),
        ("byte4", c_uint8),
        ("byte5", c_uint8)
    ]


class Status_bits(ctypes.LittleEndianStructure):
    """
    Support-Class with the bit assignments for the 5 status byte of the HP3478A
    """

    _fields_ = [
        # Byte 1: Function, Range and Number of Digits
        ("digits",     c_uint8, 2),  # bit 0..1
        ("range",      c_uint8, 3),  # bit 2..4
        ("function",   c_uint8, 3),  # bit 5..7

        # Byte 2: Status Bits
        ("int_trig",   c_uint8, 1),
        ("auto_range", c_uint8, 1),
        ("auto_zero",  c_uint8, 1),
        ("fifty_hz",   c_uint8, 1),
        ("front_rear", c_uint8, 1),
        ("cal_enable", c_uint8, 1),
        ("ext_trig",   c_uint8, 1),
        ("res1",       c_uint8, 1),

        # Byte 3: Serial Poll Mask (SRQ)
        ("SRQ_data_rdy",         c_uint8, 1),
        ("res2",                 c_uint8, 1),
        ("SRQ_syntax_error",     c_uint8, 1),
        ("SRQ_internal_error",   c_uint8, 1),
        ("SRQ_front_panel",      c_uint8, 1),
        ("SRQ_cal_error",        c_uint8, 1),
        ("res3",                 c_uint8, 1),
        ("SRQ_PON",              c_uint8, 1),

        # Byte 4: Error Information
        ("ERR_cal",        c_uint8, 1),
        ("ERR_RAM",        c_uint8, 1),
        ("ERR_ROM",        c_uint8, 1),
        ("ERR_slope",      c_uint8, 1),
        ("ERR_AD",         c_uint8, 1),
        ("ERR_AD_Link",    c_uint8, 1),
        ("res4",           c_uint8, 1),
        ("res5",           c_uint8, 1),

        # Byte 5: DAC Value
        ("DAC_value",       c_uint8, 8),
    ]

    def __str__(self):
        """
        Returns a pretty formatted (human readable) string showing the status of the instrument

        """
        cur_mode = HP3478A.INV_MODES["F" + str(self.function)]
        cur_range = list(HP3478A.RANGES[cur_mode].keys())[self.range - 1]
        if cur_range >= 1E6:
            r_str = str(cur_range / 1E6) + ' M'
        elif cur_range >= 1000:
            r_str = str(cur_range / 1000) + ' k'
        elif cur_range <= 1:
            r_str = str(cur_range * 1000) + ' m'
        else:
            r_str = str(cur_range) + ' '
        return (
            "function: {}, range: {}, digits: {}\
                \nStatus:\n  internal | external trigger: {} | {}\
                \n  Auto ranging: {}\n  AutoZero: {}\
                \n  50Hz mode: {}\n  Front/Rear selection: {} \
                \n  Calibration enable: {}\
                \nSerial poll mask (SRQ):\n  SRQ for Data ready: {}\
                \n  SRQ for Syntax error: {}\n  SRQ for Internal error: {}\
                \n  SRQ Front Panel button: {}\
                \n  SRQ for Cal err: {}\n  SQR for Power on: {}\
                \nError information: \n  Calibration: {} \n  RAM: {}\n  ROM: {}\
                \n  AD Slope: {}\n  AD: {}\n  AD-Link: {} \
                \nDAC value: {}".format(
                cur_mode, r_str, 6 - self.digits, self.int_trig, self.ext_trig,
                self.auto_range, self.auto_zero, self.fifty_hz,
                self.front_rear, self.cal_enable, self.SRQ_data_rdy,
                self.SRQ_syntax_error, self.SRQ_internal_error,
                self.SRQ_front_panel, self.SRQ_cal_error, self.SRQ_PON,
                self.ERR_cal, self.ERR_RAM, self.ERR_ROM, self.ERR_slope,
                self.ERR_AD, self.ERR_AD_Link, self.DAC_value)
        )


class Status(ctypes.Union):
    """Union type element for the decoding of the status bit-fields
    """
    _fields_ = [
        ("B", Status_bytes),
        ("b", Status_bits)
    ]


class HP3478A(Instrument):
    """ Represents the Hewlett Packard 3748A 5 1/2 digit multimeter
    and provides a high-level interface for interacting
    with the instrument.
    """

    def __init__(self, resourceName, **kwargs):
        kwargs.setdefault('read_termination', '\r\n')
        kwargs.setdefault('send_end', True)
        super().__init__(
            resourceName,
            "Hewlett-Packard HP3478A",
            includeSCPI=False,
            **kwargs
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

    class SRQ(IntFlag):
        """Enum element for SRQ mask bit decoding
        """
        Power_on = 128
        Calibration = 32
        Front_panel_button = 16
        Internal_error = 8
        Syntax_error = 4
        Data_ready = 1

    def get_status(self):
        """Method to read the status bytes from the instrument
        :return current_status: a byte array representing the instrument status
        :rtype current_status: bytes
        """
        self.write("B")
        current_status = self.adapter.read_bytes(5)
        return current_status

    # decoder functions
    @classmethod
    def decode_status(cls, status_bytes, field=None):
        """Method to handle the decoding of the status bytes into something meaningfull

        :param status_bytes: list of bytes to be decoded
        :param field: name of field to be returned
        :return ret_val: int status value

        """
        ret_val = Status(Status_bytes(*status_bytes))
        if field is None:
            return ret_val.b
        elif field == "SRQ":
            return cls.SRQ(getattr(ret_val.B, "byte3"))
        else:
            return getattr(ret_val.b, field)

    @classmethod
    def decode_mode(cls, function):
        """Method to decode current mode

        :param function: int indicating the measurement function selected
        :return cur_mode: string with the current measurement mode
        :rtype cur_mode: str

        """
        cur_mode = cls.INV_MODES["F" + str(function)]
        return cur_mode

    @classmethod
    def decode_range(cls, range_undecoded, function):
        """Method to decode current range

        :param range_undecoded: int to be decoded
        :param function: int indicating the measurement function selected
        :return cur_range: float value repesenting the active measurment range
        :rtype cur_range: float

        """
        cur_mode = cls.INV_MODES["F" + str(function)]
        if cur_mode == "DCV":
            correction_factor = 3
        elif cur_mode in ["ACV", "ACI", "DCI"]:
            correction_factor = 2
        else:
            correction_factor = 0
        cur_range = 3 * math.pow(10, range_undecoded - correction_factor)
        return cur_range

    @staticmethod
    def decode_trigger(status_bytes):
        """Method to decode trigger mode

        :param status_bytes: list of bytes to be decoded
        :return trigger_mode: string with the current trigger mode
        :rtype trigger_mode: str

        """
        cur_stat = Status(Status_bytes(*status_bytes))
        i_trig = cur_stat.b.int_trig
        e_trig = cur_stat.b.ext_trig
        if i_trig == 0:
            if e_trig == 0:
                trigger_mode = "hold"
            else:
                trigger_mode = "external"
        else:
            trigger_mode = "internal"
        return trigger_mode

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
        AZ_str = "Z" + str(int(strict_discrete_set(az_set, [0, 1])))
        self.write(AZ_str)

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
        # Read the error status reigster only one time for this method, as
        # the manual states that reading the error status register also clears it.
        current_errors = self.error_status
        if current_errors != 0:
            log.error("HP3478A error detected: %s", self.ERRORS(current_errors))
        return self.ERRORS(current_errors)

    error_status = Instrument.measurement(
        "E",
        """Checks the error status register

        """,
        cast=int,
    )

    def display_reset(self):
        """ Reset the display of the instrument.

        """
        self.write("D1")

    display_text = Instrument.setting(
        "D2%s",
        """Displays up to 12 upper-case ASCII characters on the display.

        """,
        set_process=(lambda x: str.upper(x[0:12])),
    )

    display_text_no_symbol = Instrument.setting(
        "D3%s",
        """Displays up to 12 upper-case ASCII characters on the display and
        disables all symbols on the display.

        """,
        set_process=(lambda x: str.upper(x[0:12])),
    )

    measure_ACI = Instrument.measurement(
        MODES["ACI"],
        """
        Returns the measured value for AC current as a float in A.

        """,
    )

    measure_ACV = Instrument.measurement(
        MODES["ACV"],
        """
        Returns the measured value for AC Voltage as a float in V.

        """,
    )

    measure_DCI = Instrument.measurement(
        MODES["DCI"],
        """
        Returns the measured value for DC current as a float in A.

        """,
    )

    measure_DCV = Instrument.measurement(
        MODES["DCV"],
        """
        Returns the measured value for DC Voltage as a float in V.

        """,
    )

    measure_R2W = Instrument.measurement(
        MODES["R2W"],
        """
        Returns the measured value for 2-wire resistance as a float in Ohm.

        """,
    )

    measure_R4W = Instrument.measurement(
        MODES["R4W"],
        """
        Returns the measured value for 4-wire resistance as a float in Ohm.

        """,
    )

    measure_Rext = Instrument.measurement(
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
        current_mode = self.decode_mode(self.status.function)
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
        current_range = self.decode_range(self.status.range, self.status.function)
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
    def status(self):
        """
        Returns an object representing the current status of the unit.

        """
        current_status = self.decode_status(self.get_status())
        return current_status

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
        mask = self.decode_status(self.get_status(), "SRQ")
        return mask

    @SRQ_mask.setter
    def SRQ_mask(self, value):
        mask_str = "M" + format(strict_range(value, [0, 63]), "2o")
        self.write(mask_str)

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
        trigger = self.decode_trigger(self.get_status())
        return trigger

    @trigger.setter
    def trigger(self, value):
        trig_set = self.TRIGGERS[strict_discrete_set(value, self.TRIGGERS)]
        self.write(trig_set)

    # Functions using low-level access via instrument.adapter.connection methods

    def GPIB_trigger(self):
        """
        Initate trigger via low-level GPIB-command (aka GET - group execute trigger)

        """
        self.adapter.connection.assert_trigger()

    def reset(self):
        """
        Initatiates a reset (like a power-on reset) of the HP3478A

        """
        self.adapter.connection.clear()

    def shutdown(self):
        """
        provides a way to gracefully close the connection to the HP3478A

        """
        self.adapter.connection.clear()
        self.adapter.connection.close()
        super().shutdown()
