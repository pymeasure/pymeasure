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
from warnings import warn

from .common_base import CommonBase, cast_or_str, identity

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class IEEE4882Mixin(CommonBase):
    """Mixin class for IEEE 488.2 protocol instruments with
    the default implementation of base commands.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # IEEE 488.2 default properties
    complete = CommonBase.measurement(
        "*OPC?",
        """Get the synchronization bit.

        This property allows synchronization between a controller and a device. The Operation
        Complete query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """,
        cast=str,
    )

    status = CommonBase.measurement(
        "*STB?",
        """Get the status byte and Master Summary Status bit.""",
        cast=str,
    )

    options = CommonBase.measurement(
        "*OPT?",
        """Get the device options installed.""",
        cast=str,
    )

    id = CommonBase.measurement(
        "*IDN?",
        """Get the identification of the instrument.""",
        cast=str,
        maxsplit=0,
    )

    def clear(self) -> None:
        """Clear the instrument status byte."""
        self.write("*CLS")

    def reset(self) -> None:
        """Reset the instrument."""
        self.write("*RST")


class SCPIMixin(IEEE4882Mixin):
    """Mixin class for SCPI instruments with the default implementation of base SCPI commands."""

    # SCPI default properties
    next_error = CommonBase.measurement(
        "SYST:ERR?",
        """Get the next error in the queue.
        If you want to read and log all errors, use :meth:`check_errors` instead.
        """,
        cast=cast_or_str(float),
        get_process_list=identity,
    )

    # SCPI default methods
    def check_errors(self) -> list[list[float | str]]:
        """Read all errors from the instrument.

        :return: List of error entries.
        """
        errors: list = []
        while True:
            err = self.next_error
            if int(err[0]) != 0:
                log.error(f"{self.name}: {err[0]}, {err[1]}")
                errors.append(err)
            else:
                break
        return errors

    def close(self) -> None:
        """Close the VISA connection."""
        self.adapter.close()

    def open(self) -> None:
        """Reopen the VISA connection after a close or network dropout."""
        self.adapter.open()

    def get_device_info(self) -> None:
        """Query ``*IDN?`` and populate identification attributes on this instance.

        Sets the following attributes from the parsed ``*IDN?`` response:

        * ``self.name`` — model designation (e.g. ``"NGP804"``)
        * ``self.vendor`` — manufacturer string
        * ``self.serial_number`` — serial number string
        * ``self.firmware_ref`` — firmware / software version string
        """
        resp_str = self.id
        vendor, name, serial_number, firmware_ref = resp_str.split(",")
        self.vendor = vendor
        self.name = name
        self.serial_number = serial_number
        self.firmware_ref = firmware_ref

    def check_is_dev_supported(self, instr_list: list[str], err_msg: str = "") -> None:
        """Check that ``self.name`` (the model from ``*IDN?``) is in *instr_list*.

        Call :meth:`get_device_info` first to populate ``self.name``.
        Closes the connection and raises :class:`AssertionError` if the model
        is not in *instr_list*.

        :param instr_list: List of supported model name strings.
        :param err_msg: Message suffix appended to the model name in the error.
        :raises AssertionError: If ``self.name`` is ``None`` or not found in *instr_list*.
        """
        if self.name is None:
            raise AssertionError("Instrument connection not opened!")

        if instr_list is not None and not any(self.name in instr for instr in instr_list):
            self.close()
            raise AssertionError(self.name + err_msg)


class SCPIUnknownMixin(SCPIMixin):
    """Mixin which adds SCPI commands to an instrument from which it is not known whether it
    supports SCPI commands or not.
    """

    def __init__(self, *args, **kwargs):
        warn("It is not known whether this device support SCPI commands or not. Please inform "
             "the pymeasure maintainers if you know the answer.", FutureWarning)
        super().__init__(*args, **kwargs)
