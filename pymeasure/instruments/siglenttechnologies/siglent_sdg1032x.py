""" """

import re

from pymeasure.instruments import Channel, Instrument, SCPIUnknownMixin
from pymeasure.instruments.generic_types import SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_range, joined_validators
from time import time
from pyvisa.errors import VisaIOError

import logging
log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


string_validator = joined_validators(capitalize_string, strict_discrete_set)


BSWV_REPLY = re.compile("^C(\\d+):BSWV\\s+")


class ParameterExtractor:

    def __init__(self, param):
        self.param = param

    def __call__(self, reply):
        m = BSWV_REPLY.match(reply)
        if not m:
            return None
        assert m.start() == 0
        channel = m.group(1)
        reply = reply[m.end() :]
        reply_parts = reply.split(",")
        try:
            idx = reply_parts.index(self.param)
        except ValueError:
            return None
        if idx + 1 >= len(reply_parts):
            return None
        return reply_parts[idx + 1]


class SDG1023XChannel(Channel):
    """Represents the Siglent SDG1032X Function/Arbitrary Waveform Generator."""

    output = Instrument.control(
        "C{ch}:OUTP?", "C{ch}:OUTP %s,LOAD,%s,PLRT,%",
        """ """,
    )

    wave_type = Instrument.control(
        "C{ch}:BSWV?", "C{ch}:BSWV WVTP,%s",
        """Control the waveform type (string, strict from SINE, SQUARE, RAMP, PULSE, NOISE, ARB,
        DC, PRBS, IQ).""",
        validator=joined_validators(
            strict_discrete_set, string_validator
        ),
        values=[["SINE", "SQUARE", "RAMP", "PULSE", "NOISE", "ARB", "DC", "PRBS", "IQ"], ],
        preprocess_reply=ParameterExtractor("WVTP"),
    )

    frequency = Instrument.control(
        "C{ch}:BSWV?", "C{ch}:BSWV FREQ,%f",
        """Control the frequency of the output waveform. Depending on the output stage, the
        supported frequency range changes. Supplying out-of-bound values may silently be clipped
        by the device (float, in Hz)""",
        preprocess_reply=ParameterExtractor("FREQ"),
    )

    amplitude = Instrument.control(
        "C{ch}:BSWV?", "C{ch}:BSWV AMP,%f",
        """Contorl the amplitude of teh output waveform.""",
        preprocess_reply=ParameterExtractor("AMP"),
    )


class SDG1023X(SCPIMixin, Instrument):

    channel_1 = Instrument.ChannelCreator(SDG1023XChannel, "1")
    channel_2 = Instrument.ChannelCreator(SDG1023XChannel, "2")


    def __init__(self, adapter, name="Siglent SDG1032X Arbitrary Waveform Generator", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs
        )
