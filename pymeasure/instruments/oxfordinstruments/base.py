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


from pymeasure.instruments import Instrument
from pyvisa.errors import VisaIOError
from pyvisa import constants as vconst
import re
import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class OxfordVISAError(Exception):
    pass


class OxfordInstrumentsBase(Instrument):
    """Base instrument for devices from Oxford Instruments.

    Checks the replies from instruments for validity.

    :param adapter: A string, integer, or :py:class:`~pymeasure.adapters.Adapter` subclass object
    :param string name: The name of the instrument. Often the model designation by default.
    :param max_attempts: Integer that sets how many attempts at getting a
        valid response to a query can be made
    :param \\**kwargs: In case ``adapter`` is a string or integer, additional arguments passed on
        to :py:class:`~pymeasure.adapters.VISAAdapter` (check there for details).
        Discarded otherwise.
    """

    timeoutError = VisaIOError(-1073807339)

    regex_pattern = r"^([a-zA-Z])[\d.+-]*$"

    def __init__(self, adapter, name="OxfordInstruments Base", max_attempts=5, **kwargs):
        kwargs.setdefault('read_termination', '\r')

        super().__init__(adapter,
                         name=name,
                         includeSCPI=False,
                         asrl={
                             'baud_rate': 9600,
                             'data_bits': 8,
                             'parity': vconst.Parity.none,
                             'stop_bits': vconst.StopBits.two,
                         },
                         **kwargs)
        self.max_attempts = max_attempts

    def ask(self, command):
        """Write the command to the instrument and return the resulting ASCII response. Also check
        the validity of the response before returning it; if the response is not valid, another
        attempt is made at getting a valid response, until the maximum amount of attempts is
        reached.

        :param command: ASCII command string to be sent to the instrument

        :returns: String ASCII response of the instrument

        :raises: :class:`~.OxfordVISAError` if the maximum number of attempts is surpassed without
            getting a valid response
        """

        for attempt in range(self.max_attempts):
            # Skip the checks in "write", because we explicitly want to get an answer here
            super().write(command)
            self.wait_for()
            response = self.read()

            if self.is_valid_response(response, command):
                if command.startswith("R"):
                    # Remove the leading R of the response
                    return response.strip("R")
                return response

            log.debug("Received invalid response to '%s': %s", command, response)

            # Clear the buffer and try again
            try:
                self.read()
            except VisaIOError as e_visa:
                if e_visa.args == self.timeoutError.args:
                    pass
                else:
                    raise e_visa

        # No valid response has been received within the maximum allowed number of attempts
        raise OxfordVISAError(f"Retried {self.max_attempts} times without getting a valid "
                              "response, maybe there is something worse at hand.")

    def write(self, command):
        """Write command to instrument and check whether the reply indicates that the given command
        was not understood.
        The devices from Oxford Instruments reply with '?xxx' to a command 'xxx' if this command is
        not known, and replies with 'x' if the command is understood.
        If the command starts with an "$" the instrument will not reply at all; hence in that case
        there will be done no checking for a reply.

        :raises: :class:`~.OxfordVISAError` if the instrument does not recognise the supplied
            command or if the response of the instrument is not understood
        """
        super().write(command)

        if not command[0] == "$":
            response = self.read()

            log.debug(
                "Wrote '%s' to instrument; instrument responded with: '%s'",
                command,
                response,
            )
            if not self.is_valid_response(response, command):
                if response[0] == "?":
                    raise OxfordVISAError("The instrument did not understand this command: "
                                          f"{command}")
                else:
                    raise OxfordVISAError(f"The response of the instrument to command '{command}' "
                                          f"is not valid: '{response}'")

    def is_valid_response(self, response, command):
        """Check if the response received from the instrument after a command is valid and
        understood by the instrument.

        :param response: String ASCII response of the device
        :param command: command used in the initial query

        :returns: True if the response is valid and the response indicates the instrument
            recognised the command
        """

        # Handle special cases
        # Check if the response indicates that the command is not recognized
        if response[0] == "?":
            log.debug("The instrument did not understand this command: %s", command)
            return False

        # Handle a special case for when the status is queried
        if command[0] == "X" and response[0] == "X":
            return True

        # Handle a special case for when the version is queried
        if command[0] == "V":
            return True

        # Handle the other, standard cases
        try:
            match = re.match(self.regex_pattern, response)
        except TypeError:
            match = False

        if match and not match.groups()[0] == command[0]:
            match = False

        return bool(match)

    def __repr__(self):
        return "<OxfordInstrumentsAdapter(adapter='%s')>" % self.adapter.connection.resource_name
