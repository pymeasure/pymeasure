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
from pymeasure.instruments import Instrument


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

c_uint8 = ctypes.c_uint8
c_uint16 = ctypes.c_uint16
c_uint32 = ctypes.c_uint32


class StatusBitsBase(ctypes.BigEndianStructure):
    """
    A bitfield structure containing the assignments for the status decoding
    """
    _pack_ = 1
    _get_process_ = {}

    # decoder functions
    # decimal to BCD & BCD to decimal conversion copied from
    # https://pymodbus.readthedocs.io/en/latest/source/example/bcd_payload.html
    @staticmethod
    def _convert_from_bcd(bcd):
        """Converts a bcd value to a decimal value

        :param value: The value to unpack from bcd
        :returns: The number in decimal form
        """
        place, decimal = 1, 0
        while bcd > 0:
            nibble = bcd & 0xF
            decimal += nibble * place
            bcd >>= 4
            place *= 10
        return decimal

    @staticmethod
    def _convert_to_bcd(decimal):
        """Converts a decimal value to a bcd value

        :param value: The decimal value to to pack into bcd
        :returns: The number in bcd form
        """
        place, bcd = 0, 0
        while decimal > 0:
            nibble = decimal % 10
            bcd += nibble << place
            decimal //= 10
            place += 4
        return bcd

    def __str__(self):
        """
        Returns a pretty formatted string showing the status of the instrument

        """
        ret_str = ""
        for field in self._fields_:
            ret_str = ret_str + f"{field[0]}: {hex(getattr(self, field[0]))}\n"

        return ret_str

    def __getattribute__(self, name):
        val = super().__getattribute__(name)
        if name == "fields":
            return val
        if name in self.fields():
            process = super().__getattribute__('_get_process_')
            if name in process:
                val = process[name](val)

        return val

    def fields(self):
        return [desc[0] for desc in super().__getattribute__('_fields_')]


class HPLegacyInstrument(Instrument):
    """
    Class for legacy HP instruments from the era before SPCI, based on `pymeasure.Instrument`

    """
    status_desc = StatusBitsBase  # To be overriden by subclasses

    def __init__(self, adapter, name="HP legacy instrument", **kwargs):
        super().__init__(
            adapter, name,
            includeSCPI=False,
            **kwargs,
        )

        self.status_bytes_count = ctypes.sizeof(self.status_desc)
        self.status_bits = self.status_desc

        log.info(f"Initializing {self.name}")

    def write(self, command):
        if command == "B":
            self.write_bytes(b"B")
        else:
            super().write(command)

    def values(self, command, **kwargs):
        if command == "B":
            self.write_bytes(b"B")
            return self.read_bytes(-1, **kwargs)
        else:
            return super().values(command, **kwargs)

    @property
    def status(self):
        """
        Get an object representing the current status of the unit.

        """
        self.write_bytes(b"B")
        reply = bytearray(self.read_bytes(self.status_bytes_count))
        return self.status_bits.from_buffer(reply)

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
        self.adapter.close()
        super().shutdown()
