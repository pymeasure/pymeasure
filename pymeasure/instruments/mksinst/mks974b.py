#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2024 PyMeasure Developers
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

from .mksinst import MKSInstrument


class SetpointChannel(Channel):
    """
    Settings of the optionally included setpoint relay.

    The relay is energized either below or above the setpoint 'value' depending on the
    'direction' property. The relay is de-energized when the reset value is crossed in
    the opposite direction.

    Note that 974B transducer has an auto hysteresis setting of 10% of the setpoint value that
    overwrites the current reset value whenever the setpoint value or setpoint direction is
    changed. If other hysteresis value than 10% is required, first set the setpoint value
    and setpoint direction before setting the reset value.
    """
    status = Channel.measurement(
        "SS{ch}?",
        """Get the setpoint relay status""",
        values={True: "SET", False: "CLEAR"},
    )

    value = Channel.control(
        "SP{ch}?", "SP{ch}!%s",
        """Control the relay switch value""",
        check_set_errors=True,
    )

    reset_value = Channel.control(
        "SH{ch}?", "SH{ch}!%s",
        """Control the relay switch off value""",
        check_set_errors=True,
    )

    direction = Channel.control(
        "SD{ch}?", "SD{ch}!%s",
        """Control the switching direction""",
        validator=strict_discrete_set,
        values=["ABOVE", "BELOW"],
        check_set_errors=True,
    )

    enable = Channel.control(
        "EN{ch}?", "EN{ch}!%s",
        """Control the assigned input channel or disable the setpoint relay.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: "OFF",
                True: "ON",
                "combined": "CMB",
                "pirani": "PIR",
                "piezo": "PZ",
                "cold cathode": "CC",
                },
        check_set_errors=True,
    )


class MKS974B(MKSInstrument):
    """ MKS 974B vacuum pressure transducer

    Connection to the device is made through an RS232/RS485 serial connection.
    The communication protocol of this device is as follows:

    Query: '@<aaa><Command>?;FF' with the response '@<aaa>ACK<Response>;FF'
    Set command: '@<aaa><Command>!<parameter>;FF' with the response '@<aaa>ACK<Response>;FF'
    Above <aaa> is an address from 001 to 254 which can be specified upon
    initialization. Since ';FF' is not supported by pyvisa as terminator this
    class overloads the device communication methods.

    :param adapter: pyvisa resource name of the instrument or adapter instance
    :param string name: The name of the instrument.
    :param address: device address included in every message to the instrument
                    (default=253)
    :param kwargs: Any valid key-word argument for :class:`Instrument`
    """

    setpoint_1 = Instrument.ChannelCreator(SetpointChannel, 1)

    setpoint_2 = Instrument.ChannelCreator(SetpointChannel, 2)

    setpoint_3 = Instrument.ChannelCreator(SetpointChannel, 3)

    def __init__(self, adapter, name="MKS 974B vacuum pressure transducer", address=253, **kwargs):
        super().__init__(
            adapter,
            name,
            address=address,
            **kwargs
        )

    def id(self):
        """ Get the identification of the instrument. """
        return f"{self.manufacturer}{self.model} {self.device_type} ({self.serial_number})"

    serial_number = Instrument.measurement(
        "SN?", """Get the serial number of the instrument""",
        cast=str,
    )

    hardware_version = Instrument.measurement(
        "HV?", """Get the hardware version of the instrument""",
        cast=str,
    )

    firmware_version = Instrument.measurement(
        "FV?", """Get the firmware version of the instrument""",
        cast=str,
    )

    device_type = Instrument.measurement(
        "DT?", """Get the device type""",
        cast=str,
    )

    manufacturer = Instrument.measurement(
        "MF?", """Get the manufacturer name""",
        cast=str,
    )

    model = Instrument.measurement(
        "MD?", """Get the transducer model number""",
        cast=str,
    )

    part_number = Instrument.measurement(
        "MD?", """Get the transducer part number""",
        cast=str,
    )

    operation_hours = Instrument.measurement(
        "TIM?", """Get the operation hours of the instrument""",
        cast=int,
    )

    temperature = Instrument.measurement(
        "TEM?", """Get the MicroPirani sensor temperature""",
    )

    status = Channel.measurement(
        "T?",
        """Get transducer status""",
        map_values=True,
        values={"Ok": "O",
                "MicroPirani failure": "M",
                "Cold Cathode failure": "C",
                "Piezo sensor failure": "Z",
                "pressure dose setpoint exceeded": "R",
                "Cold Cathode On": "G",
                },
    )

    pirani_pressure = Instrument.measurement(
        "PR1?", """Get MicroPirani sensor pressure""",
    )

    piezo_pressure = Instrument.measurement(
        "PR2?", """Get Piezo differential sensor pressure""",
    )

    pressure = Instrument.measurement(
        "PR4?", """Get combined pressure reading""",
    )

    coldcathode_pressure = Instrument.measurement(
        "PR5?", """ Get Cold Cathode sensor pressure""",
    )

    unit = Instrument.control(
        "U?", "U!%s",
        """Control pressure unit used for all pressure readings from the instrument""",
        validator=strict_discrete_set,
        map_values=True,
        values={"Torr": "TORR",
                "mBar": "MBAR",
                "Pascal": "PASCAL",
                },
        check_set_errors=True,
    )

    user_tag = Instrument.control(
        "UT?", "UT!%s",
        """Control the user programmable tag""",
        cast=str,
        check_set_errors=True,
    )

    switch_enabled = Instrument.control(
        "SW?", "SW!%s",
        """Control the user switch to prevent accidental execution of adjustments""",
        validator=strict_discrete_set,
        map_values=True,
        values={True: "ON",
                False: "OFF",
                },
        check_set_errors=True,
    )
