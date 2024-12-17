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

import logging

from pymeasure.instruments import Instrument, Channel
from pymeasure.instruments.validators import strict_discrete_set, strict_range, \
                                                truncated_range


log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class TemperatureSensor(Channel):
    """
    A temperature sensor channel on the Oxford Instruments Mercury iTC.

    Depending on sensor type (e.g. diode, NTC/PTC resistor), some properties
    will not be valid. Therefore, sensor configuration must be known and set
    a priori. Only diode sensor types are currently implemented.

    Control loops are accessed via temeperature sensors, rather than heaters.
    Therefore loop control is kept with other temperature sensor properties.
    """

    def check_set_errors(self):
        """The MercuryiTC responds to every communication (get and set).
        This simply reads back on setting a property."""
        try:
            self.read()
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

    temperature = Channel.measurement(
        "READ:DEV:{ch}:TEMP:SIG:TEMP",
        """Get the measured temperature, in Kelvin.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("K", "")
    )

    voltage = Channel.measurement(
        "READ:DEV:{ch}:TEMP:SIG:VOLT",
        """Get the sensor voltage, in Volts.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("mV", ""),
        get_process=lambda v: v*1e-3
    )

    control_temperature = Channel.measurement(
        "READ:DEV:{ch}:TEMP:SIG:TEMP",
        """Get the control temperature, in Kelvin.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("K", "")
    )

    loop_PID_enabled = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:ENAB",
        "SET:DEV:{ch}:TEMP:LOOP:ENAB:%s",
        """Control whether the control-loop heater is controlled by
        the PID loop (``True``) or the manual heater percentage (``False``).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1],
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )

    loop_P = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:P",
        "SET:DEV:{ch}:TEMP:LOOP:P:%g",
        """Control the proportional term, P, of the control loop.""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1]
    )

    loop_I = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:I",
        "SET:DEV:{ch}:TEMP:LOOP:I:%g",
        """Control the integral term, I, of the control loop.""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1]
    )

    loop_D = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:D",
        "SET:DEV:{ch}:TEMP:LOOP:D:%g",
        """Control the derivative term, D, of the control loop.""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1]
    )

    loop_T_setpoint = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:TSET",
        "SET:DEV:{ch}:TEMP:LOOP:TSET:%g",
        """Control the control loop temperature setpoint, in Kelvin (in the range
        0 to 2000).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1].replace("K", ""),
        validator=truncated_range,
        values=[0, 2000]
    )

    loop_heater_pcnt = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:HSET",
        "SET:DEV:{ch}:TEMP:LOOP:HSET:%g",
        """Control the heater percentage when output configured to manual mode
        (in the range 0 to 100).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1],
        validator=truncated_range,
        values=[0, 100]
    )

    loop_ramp_rate = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:RSET",
        "SET:DEV:{ch}:TEMP:LOOP:RSET:%g",
        """Control the control loop ramp rate, in K/min, if enabled (in the
        range 0 to 100000).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1].replace("K/m", ""),
        validator=truncated_range,
        values=[0, 100000]
    )

    loop_ramp_enabled = Channel.control(
        "READ:DEV:{ch}:TEMP:LOOP:RENA",
        "SET:DEV:{ch}:TEMP:LOOP:RENA:%s",
        """Control whether the temperature ramping function is enabled (``True``) or
        disabled (``False``).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1],
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True
    )


class Heater(Channel):
    """
    A heater channel on the Oxford Instruments Mercury iTC.

    Various parameters of the heater output can be accessed, and some properties
    can be configured. PID control is accessed through an associated temperature sensor.
    It is assumed that the heater is already associated with a temperature sensor control
    loop, or otherwise set to operate in open-loop configuration.
    """

    def check_set_errors(self):
        """The MercuryiTC responds to every communication (get and set).
        This simply reads back on setting a property."""
        try:
            self.read()
        except Exception as exc:
            log.exception("Setting a property failed.", exc_info=exc)
            raise
        else:
            return []

    voltage = Channel.measurement(
        "READ:DEV:{ch}:HTR:SIG:VOLT",
        """Get the heater excitation voltage, in Volts.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("V", "")
    )

    current = Channel.measurement(
        "READ:DEV:{ch}:HTR:SIG:CURR",
        """Get the heater excitation current, in Amps.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("A", "")
    )

    power = Channel.measurement(
        "READ:DEV:{ch}:HTR:SIG:POWR",
        """Get the heater power dissipation, in Watts.""",
        preprocess_reply=lambda v: v.split(":")[-1].replace("W", "")
    )

    voltage_limit = Channel.control(
        "READ:DEV:{ch}:HTR:VLIM",
        "SET:DEV:{ch}:HTR:VLIM:%g",
        """Control the voltage limit of the heater output, in Volts (float strictly
        from 0 to 40).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1],
        validator=strict_range,
        values=[0, 40]
    )

    resistance = Channel.control(
        "READ:DEV:{ch}:HTR:RES",
        "SET:DEV:{ch}:HTR:RES:%g",
        """Control the programmed heater resistance, in Ohms (float strictly
        in the range of 10 to 2000).""",
        check_set_errors=True,
        preprocess_reply=lambda v: v.split(":")[-1],
        validator=strict_range,
        values=[10, 2000]
    )

    max_power = Channel.measurement(
        "READ:DEV:{ch}:HTR:PMAX",
        """Get the provisional maximum power of the heater, in Watts.""",
        preprocess_reply=lambda v: v.split(":")[-1]
    )


class MercuryiTC(Instrument):
    """
    Represents the Oxford Instruments Mercury iTC (Intelligent Temperature
    Controller) and provides a high-level interface for interacting with the instrument.
    Note thath the GPIB implementation on this instrument is not fully
    SCPI-compliant, with only the ``*IDN?`` command supported. The Mercury iTC
    can be configured to respond to a so-called SCPI instruction set (that is,
    again, not actually an SCPI implementation) or to a legacy instruction set.
    The implementation used here is the so-called SCPI instruction set.

    The iTC is expandable and supports a mixture temperature sensors,
    heaters, pressure sensors, cryogen level sensors and auxiliary I/O
    through the installation of additional, function-specific daughter boards.
    Currently, only temperature sensors and heaters are implemented.

    By default, there is a temperature sensor channel installed with Unique Identifier
    (``UID``) ``'MB1.T1'`` and a heater channel with UID ``'MB0.H1'``.
    These channels are created automatically at instantiation of the controller.
    These can be accessed as either ``.TS_MB``  and ``.HTR_MB``, or through the collections
    (dictionaries) ``.TS['MB1.T1']`` and ``.HTR['MB0.H1']``.

    Other sensors and heaters can be installed on additional daughter boards
    (with specific ``UID`` e.g. ``'DBX.T1'``, ``'DBX.H1'`` etc), and can be added manually
    to an already instantiated MercuryiTC using ``.add_temperature_sensor(UID)`` and
    ``.add_heater(UID)``. They must be given their correct UID as listed by the Mercury iTC
    itself as this is how they are addressed during communication. Additionally, they
    are accessed **only** through the instrument collections ``.TS[UID]`` and ``.HTR[UID]``.

    .. code-block:: python

        controller = MercuryiTC("GPIB::1")

        # Print the current measured temperature of the motherboard temperature sensor aka 'MB1.T1'
        print(controller.TS_MB.temperature)

        # Print the motherboard temperature sensor control-loop setpoint
        print(controller.TS['MB1.T1'].loop_T_setpoint)

        # Add new temperature sensor with UID 'DB6.T1'
        controller.add_temperature_sensor('DB6.T1')

        # Print the new sensor's temperature
        print(controller.TS['DBS.T1'].temperature)
    """

    def __init__(self, adapter, name='Oxford MercuryiTC', includeSCPI=False, **kwargs):
        super().__init__(
            adapter=adapter,
            name=name,
            read_termination="\n",
            write_termination="\n",
            **kwargs
        )

    identity = Instrument.measurement(
        "*IDN?",
        """Get identity of unit."""
    )

    TS_mobo = Instrument.ChannelCreator(
        TemperatureSensor,
        "MB1.T1",
        prefix="TS",
        collection="TS"
        )

    HTR_mobo = Instrument.ChannelCreator(
        Heater,
        "MB0.H1",
        prefix="HTR",
        collection="HTR",
        )

    def add_temperature_sensor(self, id, prefix="TS", **kwargs):
        """Add a temperature sensor with unique identifier ``id`` to collection
        of addressable temperature sensors: ``.TS[id]``"""
        self.add_child(TemperatureSensor,
                       id, collection="TS",
                       prefix=prefix, **kwargs)

    def add_heater(self, id, prefix="HTR", **kwargs):
        """Add a heater with unique identifier  ``id`` to collection of
        addressable heaters: ``.HTR[id]``"""
        self.add_child(Heater,
                       id, collection="HTR",
                       prefix=prefix, **kwargs)
