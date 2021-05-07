from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import strict_discrete_set, \
    strict_range, joined_validators, truncated_range
import numpy as np

def capitalize_string(string: str, *args, **kwargs):
    return string.upper()


# Combine the capitalize function and validator
string_validator = joined_validators(capitalize_string, strict_discrete_set)


class Channel():
    """ Implementation of a channel on Tektronix TDS6000 series oscilliscope.
     Only tested on TDS620B and TDS6604. I couldn't find the TDS6604 programming manual, but the
     command set is similar enough that the TDS6604 also works using TDS620B commands."""

    parameters = Instrument.measurement(
        "?",
        """A property that returns all vertical paramters associated with the channel""",
    )

    bandwidth = Instrument.control(
        ":BANdwidth?", "BANdwidth %s",
        """
        String parameter that sets the channel bandwidth to 'TWEnty':20 MHz, 'TWOfifty':250 MHz, 'FULl': 500 MHz.
        """,
        validator=string_validator,
        values=['TWEnty', 'TWOfifty', 'FULl']
    )

    coupling = Instrument.control(
        ":COUPling?", ":COUPling %s",
        """
        String parameter that sets the channel coupling to 'AC', 'DC', 'GND'.
        """,
        validator=string_validator,
        values=['AC', 'DC', 'GND']
    )

    deskew = Instrument.control(
        ":DESKew?", ":DESKew %g",
        """
        Float parameter in range -25 ns to +25 ns with resolution of 1 ps. Used to compensate for cables of different
        lengths. Implemented for completeness, read about before using.
        """,
        validator=truncated_range,
        values=[-25e-9, 25e-9]
    )

    impedance = Instrument.control(
        ":IMPedance?", ":IMPedance %s",
        """
        String parameter that sets the channel impedance to  'FIFty', 'MEG'.
        """,
        validator=string_validator,
        values=['FIFty', 'MEG']
    )

    offset = Instrument.control(
        ":OFFSet?", ":OFFSet %g",
        """
        Float parameter that sets the channel offset. There are restrictions based on V/div
        """,
        validator=truncated_range,
        values=[-10, 10]
    )

    scale = Instrument.control(
        ":SCAle?", ":SCAle %g",
        """
        Float parameter that sets the channel scale (V/div), range is 100 mV to 1 V
        """,
        validator=truncated_range,
        values=[1e-3, 10]
    )

    def __init__(self, instrument, number):
        self.instrument = instrument
        self.number = number

    def values(self, command, **kwargs):
        """ Reads a set of values from the instrument through the adapter,
        passing on any key-word arguments. Because there is a CHn? query,
        colon's are included in the attribute definitions and not here.
        """
        return self.instrument.values("CH%d%s" % (
            self.number, command), **kwargs)

    def ask(self, command):
        self.instrument.ask("CH%d%s" % (self.number, command))

    def write(self, command):
        self.instrument.write("CH%d%s" % (self.number, command))

    def read(self):
        self.instrument.read()
