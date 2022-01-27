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

    def __init__(self, resource_name, sanity="{}.*", max_attempts=5, **kwargs):
        super().__init__(resource_name, **kwargs)
        self.sanity_regex = sanity
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
        if count > self.max_attempts:
            raise RetryVISAError(f"{self.max_attempts} times retried, "
                                 f"no sane reply, maybe there is something worse at hand")
        else:
            count += 1
        device_output = self.connection.query(command)
        log.debug("query for command %s; device_output: %s", command, device_output)
        reply_sane = self.sanity_handling(device_output, command, count=count)
        return reply_sane

    def write(self, command):
        """write command to instrument
        check whether the reply indicates that the given command was not understood
        The devices from oxford instruments reply with '?xxx' to
            a command 'xxx' if this command is not known
        """
        try:
            answer = self.connection.query(command)
            log.debug(
                "writing command to instrument: %s; instrument answered: %s",
                command,
                answer,
            )
            if answer[0] == "?":
                raise RetryVISAError(
                    f"The instrument did not understand this command: {command}"
                )
        except VisaIOError as e_visa:
            if (
                isinstance(e_visa, type(self.timeoutError))
                and e_visa.args == self.timeoutError.args
            ):
                pass
            else:
                raise e_visa

    def sanity_handling(self, device_output, command, count=0, *args, **kwargs):
        """match the reply from a device with the specifying regex
        retry the request in case of a mismatch
            use the custom sanity regex incorporating the command message

        :param device_output: String ASCII response of the device
        :param command: command used in the initial query
        :param count: Integer that counts how many attempts at getting a sane
            reply have been done.

        :returns:   in case it matches: device_output,
                    else: recursively retry self.ask(command)
        """

        san_regex = self.sanity_regex.format(command[0])

        try:
            if not re.match(san_regex, device_output):
                log.debug(
                    "reply '%s' is not sane for command '%s', trying again, this is trial nr. %s",
                    device_output,
                    command,
                    count,
                )
                try:
                    self.read()
                except VisaIOError as e_visa:
                    if (
                        isinstance(e_visa, type(self.timeoutError))
                        and e_visa.args == self.timeoutError.args
                    ):
                        pass
                    else:
                        raise e_visa
                return self.ask(command, count=count)
        except TypeError:
            try:
                self.read()
            except VisaIOError as e_visa:
                if (
                    isinstance(e_visa, type(self.timeoutError))
                    and e_visa.args == self.timeoutError.args
                ):
                    pass
                else:
                    raise e_visa
            return self.ask(command, count=count)
        return device_output

    def __repr__(self):
        return "<OxfordInstrumentsAdapter(resource='%s')>" % self.connection.resource_name
