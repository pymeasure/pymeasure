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

from pymeasure.instruments import Channel, Instrument
from pymeasure.instruments.validators import strict_discrete_set

from .mksinst import MKSInstrument, RelayChannel


try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """Until StrEnum is broadly available from the standard library"""
        # Python>3.10 remove it


_ion_gauge_status = {"Wait": "W",
                     "Off": "O",
                     "Protect": "P",
                     "Degas": "D",
                     "Control": "C",
                     "Rear panel Ctrl off": "R",
                     "HC filament fault": "H",
                     "No gauge": "N",
                     "Good": "G",
                     "NOT_IONGAUGE": "NAK152",
                     "INVALID COMMAND": "NAK160",
                     }


class Unit(StrEnum):
    Torr = "TORR"
    mbar = "mBAR"
    Pa = "PASCAL"
    uHg = "MICRON"


class Relay(RelayChannel):

    enabled = Channel.control(
        "EN{ch}?", "EN{ch}!%s",
        """Control the relay function or disable the setpoint relay.

        Possible values are True/False to enable/disable pressure based
        activation of the relay and 'SET' to permanently energize the relay.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: "CLEAR",
                True: "ENABLE",
                "SET": "SET",
                },
        check_set_errors=True,
    )


class PressureChannel(Channel):
    pressure = Channel.measurement(
        "PR{ch}?",
        """Get the pressure on the channel in units selected on the device""",
    )

    power_enabled = Channel.control(
        "CP{ch}?", "CP{ch}!%s",
        """Control power status of the channel. (bool)""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON", False: "OFF"},
        check_set_errors=True,
    )


class IonGaugeAndPressureChannel(PressureChannel):
    """Channel having both a pressure and an ion gauge sensor"""
    ion_gauge_status = Channel.measurement(
        "T{ch}?",
        """Get ion gauge status of the channel.""",
        map_values=True,
        values=_ion_gauge_status,
    )


class MKS937B(MKSInstrument):
    """ MKS 937B vacuum gauge controller

    Connection to the device is made through an RS232/RS485 serial connection.

    The 937B gauge controller can connect up to 6 pressure measurement channels
    for gauges of various types which includes ionization gauges, Pirani and
    piezo gauges. Based on the pressure values of the gauges twelve setpoint
    relays can be energized when certain pressure values are reached. The
    assignment of the relays to measurement channels is fixed to have two
    relays for each pressure channel.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: The name of the instrument.
    :param address: device address included in every message to the instrument
                    (default=253)
    :param kwargs: Any valid key-word argument for Instrument
    """

    # Channels 1,3,5 have both an ion gauge and a pressure sensor, 2,4,6 only a pressure sensor
    ch_1 = Instrument.ChannelCreator(IonGaugeAndPressureChannel, 1)

    ch_2 = Instrument.ChannelCreator(PressureChannel, 2)

    ch_3 = Instrument.ChannelCreator(IonGaugeAndPressureChannel, 3)

    ch_4 = Instrument.ChannelCreator(PressureChannel, 4)

    ch_5 = Instrument.ChannelCreator(IonGaugeAndPressureChannel, 5)

    ch_6 = Instrument.ChannelCreator(PressureChannel, 6)

    relay_1 = Instrument.ChannelCreator(Relay, 1)

    relay_2 = Instrument.ChannelCreator(Relay, 2)

    relay_3 = Instrument.ChannelCreator(Relay, 3)

    relay_4 = Instrument.ChannelCreator(Relay, 4)

    relay_5 = Instrument.ChannelCreator(Relay, 5)

    relay_6 = Instrument.ChannelCreator(Relay, 6)

    relay_7 = Instrument.ChannelCreator(Relay, 7)

    relay_8 = Instrument.ChannelCreator(Relay, 8)

    relay_9 = Instrument.ChannelCreator(Relay, 9)

    relay_10 = Instrument.ChannelCreator(Relay, 10)

    relay_11 = Instrument.ChannelCreator(Relay, 11)

    relay_12 = Instrument.ChannelCreator(Relay, 12)

    def __init__(self, adapter, name="MKS 937B vacuum gauge controller", address=253, **kwargs):
        super().__init__(
            adapter,
            name,
            address=address,
            **kwargs
        )

    serial = Instrument.measurement(
        "SN?", """Get the serial number of the instrument """,
        cast=str,
    )

    all_pressures = Instrument.measurement(
        "PRZ?", """ Get pressures on all channels in selected units """,
    )

    combined_pressure1 = Instrument.measurement(
        "PC1?", """ Get pressure on channel 1 and its combination sensor """,
    )

    combined_pressure2 = Instrument.measurement(
        "PC2?", """ Get pressure on channel 2 and its combination sensor """,
    )

    unit = Instrument.control(
        "U?", "U!%s",
        """Control pressure unit used for all pressure readings from the instrument.

        Allowed units are Unit.Torr, Unit.mbar, Unit.Pa, Unit.uHg.""",
        validator=strict_discrete_set,
        map_values=True,
        values={u: u.value for u in Unit},
        check_set_errors=True,
    )
