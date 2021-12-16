from pymeasure.adapters import VISAAdapter
from pyvisa.errors import VisaIOError

import re
import logging


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class RetryVISAError(Exception):
    pass


class RetryingVISAAdapter(VISAAdapter):
    """Adapter class for the VISA library using PyVISA to communicate
    with instruments.
    Checks replies from instruments for sanity

    :param sanity: regex string of how a reply from the device must look like
                        defaults to accepting all replies
    :param resource: VISA resource name that identifies the address
    :param visa_library: VisaLibrary Instance, path of the VISA library or VisaLibrary spec string (@py or @ni).
                         if not given, the default for the platform will be used.
    :param preprocess_reply: optional callable used to preprocess strings
        received from the instrument. The callable returns the processed string.
    :param kwargs: Any valid key-word arguments for constructing a PyVISA instrument
    """

    connError = VisaIOError(-1073807194)
    timeouterror = VisaIOError(-1073807339)
    visaIOError = VisaIOError(-1073807298)
    visaNotFoundError = VisaIOError(-1073807343)

    def __init__(self, resource_name, sanity=".*", **kwargs):
        super().__init__(resource_name, **kwargs)
        self.sanity_regex = sanity

    def ask(self, command, count=0):
        """Write the command to the instrument and return the resulting
        ASCII response
        Do a sanity check for the returned value, if this fails recursively
        repeat

        :param command: SCPI command string to be sent to the instrument
        :returns: String ASCII response of the instrument
        """
        if count > 5:
            raise RetryVISAError(
                "5 times retried, no sane reply, maybe there is something worse at hand"
            )
        else:
            count += 1
        # log.debug(f"query for command {command} ")
        device_output = self.connection.query(command)
        # log.debug(f"device_output: {device_output}")
        reply_sane = self.sanity_handling(device_output, command, count=count)
        # log.debug(f"reply_sane: {reply_sane}")
        return reply_sane

    def sanity_handling(self, device_output, command, count=0, *args, **kwargs):
        """match the reply from a device with the specifying regex
        retry the request in case of mismatch


        :param device_output: String ASCII response of the device
        :param command: command used in the initial query
        :returns:   in case it matches: device_output,
                    else: recursively retry self.ask(command)
        """
        # log.debug("now handling sanity in general RetryingVISAAdapter")
        # log.debug(f"sanity regex = {self.sanity_regex}")
        # log.debug(f"device_output = {device_output}")
        try:
            if not re.match(self.sanity_regex, device_output):
                log.debug(
                    f"reply '{device_output}' is not sane, trying again, this is trial nr. {count}"
                )
                try:
                    self.read()
                except VisaIOError as e_visa:
                    if (
                        isinstance(e_visa, type(self.timeouterror))
                        and e_visa.args == self.timeouterror.args
                    ):
                        pass
                    else:
                        raise e_visa
                return self.ask(command, count=count)
        except TypeError:
            log.debug(f"got a TypeError, trying again")
            try:
                self.read()
            except VisaIOError as e_visa:
                if (
                    isinstance(e_visa, type(self.timeouterror))
                    and e_visa.args == self.timeouterror.args
                ):
                    pass
                else:
                    raise e_visa
            return self.ask(command, count=count)
        log.debug("finally, a sane reply!")
        return device_output

    def __repr__(self):
        return "<RetryingVISAAdapter(resource='%s')>" % self.connection.resource_name


class RetryingVISAAdapter_oinst(RetryingVISAAdapter):
    """docstring for RetryingVisaAdapter"""

    def __init__(self, resource_name, **kwargs):
        super().__init__(resource_name, sanity="{}.*", **kwargs)
        # self.sanity_regex = sanity    

    def write(self, command):
        """write command to instrument, check whether reply is sane"""
        try:
            answer = self.connection.query(command)
            log.debug("instrument answered: %s", answer)
            if answer[0] == "?":
                raise RetryVISAError(
                    f"The instrument did not understand this command: {command}"
                )
        except VisaIOError as e_visa:
            if (
                isinstance(e_visa, type(self.timeouterror))
                and e_visa.args == self.timeouterror.args
            ):
                pass
            else:
                raise e_visa

    def sanity_handling(self, device_output, command, count=0, *args, **kwargs):
        """match the reply from a device with the specifying regex
        retry the request in case of mismatch
        use custom sanity regex incorporating the command message


        :param device_output: String ASCII response of the device
        :param command: command used in the initial query
        :returns:   in case it matches: device_output,
                    else: recursively retry self.ask(command)
        """
        # log.debug(f"now handling sanity, this is trial nr. {count}")
        # log.debug(f"sanity regex pristine = {self.sanity_regex}, command={command}")
        san_regex = self.sanity_regex.format(command[0])
        # log.debug(f"sanity regex = {san_regex}")
        # log.debug(f"device_output = {device_output}")

        try:
            if not re.match(san_regex, device_output):
                log.debug(
                    f"reply '{device_output}' is not sane, trying again, this is trial nr. {count}"
                )
                try:
                    self.read()
                except VisaIOError as e_visa:
                    if (
                        isinstance(e_visa, type(self.timeouterror))
                        and e_visa.args == self.timeouterror.args
                    ):
                        pass
                    else:
                        raise e_visa
                return self.ask(command, count=count)
        except TypeError:
            # log.debug(f"got a TypeError, trying again")
            try:
                self.read()
            except VisaIOError as e_visa:
                if (
                    isinstance(e_visa, type(self.timeouterror))
                    and e_visa.args == self.timeouterror.args
                ):
                    pass
                else:
                    raise e_visa
            return self.ask(command, count=count)
        # log.debug("finally, a sane reply!")
        return device_output

    def __repr__(self):
        return (
            "<RetryingVISAAdapter_oinst(resource='%s')>" % self.connection.resource_name
        )
