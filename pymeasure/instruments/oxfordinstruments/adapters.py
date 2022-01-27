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


from pymeasure.adapters import VISAAdapter
from pyvisa.errors import VisaIOError

import re
import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RetryVISAError(Exception):
    pass


class OxfordInstrumentsAdapter(VISAAdapter):
    """Adapter class for the VISA library using PyVISA to communicate
    with instruments.
    Checks replies from instruments for sanity

    :param resource_name: VISA resource name that identifies the address
    :param sanity: regex string of how a reply from the device must look like
        default is for devices from Oxford Instruments
    :param max_attempts: Integer that sets how many attempts at getting a
        sensible response to a query can be made
    :param kwargs: key-word arguments for constructing a PyVISA Adapter
    """

    connError = VisaIOError(-1073807194)
    timeoutError = VisaIOError(-1073807339)
    visaIOError = VisaIOError(-1073807298)
    visaNotFoundError = VisaIOError(-1073807343)

    regex_pattern = r"^([?]?)([a-zA-Z])[\d.]*$"

    def __init__(self, resource_name, max_attempts=5, **kwargs):
        super().__init__(resource_name, **kwargs)
        self.max_attempts = max_attempts

    def ask(self, command, count=0):
        """Write the command to the instrument and return the resulting
        ASCII response
        Do a sanity check for the returned value, if this fails recursively
        repeat

        :param command: ASCII command string to be sent to the instrument
        :param count: Integer that counts how many attempts at getting a sane
            reply have been done.

        :returns: String ASCII response of the instrument
        """

        for attempt in range(self.max_attempts):
            response = super().ask(command)

            if self.is_valid_response(response, command):
                return response

            log.debug("Received invalid response to '%s': %s", command, response)

            # Clear the buffer and try again
            try:
                self.read()
            except VisaIOError as e_visa:
                if (isinstance(e_visa, type(self.timeoutError))
                        and e_visa.args == self.timeoutError.args):
                    pass
                else:
                    raise e_visa

        # No valid response has been received within the maximum allowed number of attempts
        raise RetryVISAError(f"Retried {self.max_attempts} times without getting a valid response, "
                             f"maybe there is something worse at hand.")

    def write(self, command):
        """Write command to instrument and check whether the reply indicates that the given command
        was not understood
        The devices from oxford instruments reply with '?xxx' to a command 'xxx' if this command is
        not known, and replies with 'x' if the command is understood.
        If the command starts with an "$" the instrument will not reply at all; hence in that case
        there will be done no checking for a reply.
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
                    raise RetryVISAError(f"The instrument did not understand this command: "
                                         f"{command}")
                else:
                    raise RetryVISAError(f"The response of the instrument to command '{command}' "
                                         f"is not valid: '{response}'")

    def is_valid_response(self, response, command):
        """Match the response from a device with a specified regex to check if the response is valid
        The regex is filled with the first letter of the command

        :param response: String ASCII response of the device
        :param command: command used in the initial query

        :returns:   True if the response matched the regex
        """

        try:
            match = re.match(self.regex_pattern, response)
        except TypeError:
            match = False

        # Check if the response indicates that the command is not recognized
        if match and match.groups()[0] == "?":
            log.debug("The instrument did not understand this command: %s", command)
            match = False

        if match and not match.groups()[1] == command[0]:
            match = False

        return bool(match)

    def __repr__(self):
        return "<OxfordInstrumentsAdapter(resource='%s')>" % self.connection.resource_name
