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
import time
from warnings import warn

from .common_base import CommonBase
from ..adapters.visa import VISAAdapter

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Instrument(CommonBase):
    """ The base class for all Instrument definitions.

    It makes use of one of the :py:class:`~pymeasure.adapters.Adapter` classes for communication
    with the connected hardware device. This decouples the instrument/command definition from the
    specific communication interface used.

    When ``adapter`` is a string, this is taken as an appropriate resource name. Depending on your
    installed VISA library, this can be something simple like ``COM1`` or ``ASRL2``, or a more
    complicated
    `VISA resource name <https://pyvisa.readthedocs.io/en/latest/introduction/names.html>`__
    defining the target of your connection.

    When ``adapter`` is an integer, a GPIB resource name is created based on that.
    In either case a :py:class:`~pymeasure.adapters.VISAAdapter` is constructed based on that
    resource name.
    Keyword arguments can be used to further configure the connection.

    Otherwise, the passed :py:class:`~pymeasure.adapters.Adapter` object is used and any keyword
    arguments are discarded.

    This class defines basic SCPI commands by default. This can be disabled with
    :code:`includeSCPI` for instruments not compatible with the standard SCPI commands.

    :param adapter: A string, integer, or :py:class:`~pymeasure.adapters.Adapter` subclass object
    :param string name: The name of the instrument. Often the model designation by default.
    :param includeSCPI: An obligatory boolean, which toggles the inclusion of standard SCPI commands

        .. deprecated:: 0.14
            If True, inherit the :class:`~pymeasure.instruments.generic_types.SCPIMixin` class
            instead.

    :param preprocess_reply: An optional callable used to preprocess
        strings received from the instrument. The callable returns the
        processed string.

        .. deprecated:: 0.11
            Implement it in the instrument's `read` method instead.
    :param \\**kwargs: In case ``adapter`` is a string or integer, additional arguments passed on
        to :py:class:`~pymeasure.adapters.VISAAdapter` (check there for details).
        Discarded otherwise.
    """

    # noinspection PyPep8Naming
    def __init__(self, adapter, name, includeSCPI=None,
                 preprocess_reply=None,
                 **kwargs):
        # Setup communication before possible children require the adapter.
        if isinstance(adapter, (int, str)):
            try:
                adapter = VISAAdapter(adapter, **kwargs)
            except ImportError:
                raise Exception("Invalid Adapter provided for Instrument since"
                                " PyVISA is not present")
        self.adapter = adapter
        if includeSCPI is True:
            warn("Defining SCPI base functionality with `includeSCPI=True` is deprecated, inherit "
                 "the `SCPIMixin` class instead.", FutureWarning)
        elif includeSCPI is None:
            warn("It is deprecated to specify `includeSCPI` implicitly, use "
                 "`includeSCPI=False` or inherit the `SCPIMixin` class instead.", FutureWarning)
            includeSCPI = True
        self.SCPI = includeSCPI
        self.isShutdown = False
        self.name = name

        super().__init__(preprocess_reply=preprocess_reply)

        log.info("Initializing %s." % self.name)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()

    # SCPI default properties
    @property
    def complete(self):
        """Get the synchronization bit.

        This property allows synchronization between a controller and a device. The Operation
        Complete query places an ASCII character 1 into the device's Output Queue when all pending
        selected device operations have been finished.
        """
        if self.SCPI:
            return self.ask("*OPC?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def status(self):
        """ Get the status byte and Master Summary Status bit. """
        if self.SCPI:
            return self.ask("*STB?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def options(self):
        """ Get the device options installed. """
        if self.SCPI:
            return self.ask("*OPT?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def id(self):
        """ Get the identification of the instrument. """
        if self.SCPI:
            return self.ask("*IDN?").strip()
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    @property
    def next_error(self):
        """Get the next error of the instrument (tuple of code and message)."""
        if self.SCPI:
            return self.values("SYST:ERR?")
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    # Wrapper functions for the Adapter object
    def write(self, command, **kwargs):
        """Write a string command to the instrument appending `write_termination`.

        :param command: command string to be sent to the instrument
        :param kwargs: Keyword arguments for the adapter.
        """
        self.adapter.write(command, **kwargs)

    def write_bytes(self, content, **kwargs):
        """Write the bytes `content` to the instrument."""
        self.adapter.write_bytes(content, **kwargs)

    def read(self, **kwargs):
        """Read up to (excluding) `read_termination` or the whole read buffer."""
        return self.adapter.read(**kwargs)

    def read_bytes(self, count, **kwargs):
        """Read a certain number of bytes from the instrument.

        :param int count: Number of bytes to read. A value of -1 indicates to
            read the whole read buffer.
        :param kwargs: Keyword arguments for the adapter.
        :returns bytes: Bytes response of the instrument (including termination).
        """
        return self.adapter.read_bytes(count, **kwargs)

    def write_binary_values(self, command, values, *args, **kwargs):
        """Write binary values to the device.

        :param command: Command to send.
        :param values: The values to transmit.
        :param \\*args, \\**kwargs: Further arguments to hand to the Adapter.
        """
        self.adapter.write_binary_values(command, values, *args, **kwargs)

    def read_binary_values(self, **kwargs):
        """Read binary values from the device."""
        return self.adapter.read_binary_values(**kwargs)

    # Communication functions
    def wait_for(self, query_delay=None):
        """Wait for some time. Used by 'ask' to wait before reading.

        :param query_delay: Delay between writing and reading in seconds. None is default delay.
        """
        if query_delay:
            time.sleep(query_delay)

    # SCPI default methods
    def clear(self):
        """ Clears the instrument status byte
        """
        if self.SCPI:
            self.write("*CLS")
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    def reset(self):
        """ Resets the instrument. """
        if self.SCPI:
            self.write("*RST")
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    def shutdown(self):
        """Brings the instrument to a safe and stable state"""
        self.isShutdown = True
        log.info(f"Finished shutting down {self.name}")

    def check_errors(self):
        """Read all errors from the instrument and log them.

        :return: List of error entries.
        """
        if self.SCPI:
            errors = []
            while True:
                err = self.next_error
                if int(err[0]) != 0:
                    log.error(f"{self.name}: {err[0]}, {err[1]}")
                    errors.append(err)
                else:
                    break
            return errors
        else:
            raise NotImplementedError("Non SCPI instruments require implementation in subclasses")

    def check_get_errors(self):
        """Check for errors after having gotten a property and log them.

        Called if :code:`check_get_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.check_errors()

    def check_set_errors(self):
        """Check for errors after having set a property and log them.

        Called if :code:`check_set_errors=True` is set for that property.

        If you override this method, you may choose to raise an Exception for certain errors.

        :return: List of error entries.
        """
        return self.check_errors()
