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

import logging
from warnings import warn

from .instrument import Instrument

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class SCPIMixin:
    """Mixin class for SCPI instruments with the default implementation of base SCPI commands."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("includeSCPI", False)  # in order not to trigger the deprecation warning
        super().__init__(*args, **kwargs)

    # SCPI default properties
    complete = Instrument.measurement(
        "*OPC?",
        """Get the synchronization bit.

        This property allows synchronization between a controller and a device. The Operation
        Complete query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """,
        cast=str,
    )

    status = Instrument.measurement(
        "*STB?",
        """Get the status byte and Master Summary Status bit.""",
        cast=str,
    )

    options = Instrument.measurement(
        "*OPT?",
        """Get the device options installed.""",
        cast=str,
    )

    id = Instrument.measurement(
        "*IDN?",
        """Get the identification of the instrument.""",
        cast=str,
        maxsplit=0,
    )

    next_error = Instrument.measurement(
        "SYST:ERR?",
        """Get the next error in the queue.
        If you want to read and log all errors, use :meth:`check_errors` instead.
        """,
    )

    # SCPI default methods
    def clear(self):
        """Clear the instrument status byte."""
        self.write("*CLS")

    def reset(self):
        """Reset the instrument."""
        self.write("*RST")

    def check_errors(self):
        """ Read all errors from the instrument.

        :return: List of error entries.
        """
        errors = []
        while True:
            err = self.next_error
            if int(err[0]) != 0:
                log.error(f"{self.name}: {err[0]}, {err[1]}")
                errors.append(err)
            else:
                break
        return errors


class SCPIUnknownMixin(SCPIMixin):
    """Mixin which adds SCPI commands to an instrument from which it is not known whether it
    supports SCPI commands or not.
    """

    def __init__(self, *args, **kwargs):
        warn("It is not known whether this device support SCPI commands or not. Please inform "
             "the pymeasure maintainers if you know the answer.", FutureWarning)
        super().__init__(*args, **kwargs)
