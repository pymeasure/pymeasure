#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

from pyvisa.constants import ControlFlow

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Pro8Channel(Channel):
    """Base class for a plug-in module of a :class:`ThorlabsPro8000` mainframe.

    The PRO8000 protocol is stateful: a slot is selected with ``:SLOT <n>`` and
    all following module commands act on the selected slot. Each channel therefore
    selects its own slot before every command ("select-then-send"), so that the
    caller does not have to keep track of the active slot.
    """

    def write(self, command, **kwargs):
        """Select this channel's slot, then write the module command."""
        self.parent.write(f":SLOT {self.id}")
        self.parent.write(command, **kwargs)

    module_type = Channel.measurement(
        ":TYPE:TXT?",
        """Get the module type of this slot as text, e.g. ``LDC8xxx`` (str).""",
        cast=str,
        maxsplit=0,
    )


class LDCChannel(Pro8Channel):
    """A laser-diode current controller module (LDC8xxx)."""

    laser_enabled = Channel.control(
        ":LASER?", ":LASER %s",
        """Control whether the laser output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    current = Channel.measurement(
        ":ILD:ACT?",
        """Measure the actual laser diode current, in A (float).""",
    )

    current_setpoint = Channel.control(
        ":ILD:SET?", ":ILD:SET %g",
        """Control the laser diode current setpoint, in A (float).""",
    )

    current_min = Channel.measurement(
        ":ILD:MIN?",
        """Get the minimum allowed laser diode current, in A (float).""",
    )

    current_max = Channel.measurement(
        ":ILD:MAX?",
        """Get the maximum allowed laser diode current, in A (float).""",
    )

    current_limit = Channel.control(
        ":LIMC:SET?", ":LIMC:SET %g",
        """Control the software laser diode current limit, in A
        (float, must be below the hardware limit, see :attr:`current_hardware_limit`).""",
    )

    current_hardware_limit = Channel.measurement(
        ":LIMCP:ACT?",
        """Get the hardware laser diode current limit, in A (float).""",
    )

    voltage = Channel.measurement(
        ":VLD:ACT?",
        """Measure the actual laser diode voltage, in V (float).""",
    )

    ld_polarity = Channel.control(
        ":LDPOL?", ":LDPOL %s",
        """Control the laser diode polarity, ``AG`` (anode grounded) or ``CG``
        (cathode grounded) (str).""",
        validator=strict_discrete_set,
        values=["AG", "CG"],
        cast=str,
    )

    pd_polarity = Channel.control(
        ":PDPOL?", ":PDPOL %s",
        """Control the monitor photodiode polarity, ``AG`` (anode grounded) or
        ``CG`` (cathode grounded) (str).""",
        validator=strict_discrete_set,
        values=["AG", "CG"],
        cast=str,
    )

    mode = Channel.control(
        ":MODE?", ":MODE %s",
        """Control the operation mode, ``CC`` (constant current) or ``CP``
        (constant power) (str).""",
        validator=strict_discrete_set,
        values=["CC", "CP"],
        cast=str,
    )


class TEDChannel(Pro8Channel):
    """A thermo-electric temperature controller module (TED8xxx)."""

    tec_enabled = Channel.control(
        ":TEC?", ":TEC %s",
        """Control whether the TEC (temperature control) output is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    temperature = Channel.measurement(
        ":TEMP:ACT?",
        """Measure the actual temperature, in °C (float).""",
    )

    temperature_setpoint = Channel.control(
        ":TEMP:SET?", ":TEMP:SET %g",
        """Control the temperature setpoint, in °C (float).""",
    )

    tec_current = Channel.measurement(
        ":ITE:ACT?",
        """Measure the actual TEC current, in A (float).""",
    )

    pid_p_share = Channel.control(
        ":SHAREP:SET?", ":SHAREP:SET %g",
        """Control the proportional (P) share of the temperature control loop,
        in percent (float strictly in range 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    pid_i_share = Channel.control(
        ":SHAREI:SET?", ":SHAREI:SET %g",
        """Control the integral (I) share of the temperature control loop,
        in percent (float strictly in range 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )

    pid_d_share = Channel.control(
        ":SHARED:SET?", ":SHARED:SET %g",
        """Control the derivative (D) share of the temperature control loop,
        in percent (float strictly in range 0 to 100).""",
        validator=strict_range,
        values=[0, 100],
    )


class ITCChannel(LDCChannel, TEDChannel):
    """A combined laser current and temperature controller module (ITC8xxx).

    Exposes the union of the :class:`LDCChannel` (laser) and :class:`TEDChannel`
    (temperature) interfaces.
    """


class PDAPortChannel(Channel):
    """A single port of a PDA8xxx photodiode amplifier module.

    A PDA module has two independent ports. Each command selects the module's
    slot and the port (``:SLOT <slot>``, ``:PORT <port>``) before it is sent.
    """

    def write(self, command, **kwargs):
        """Select the parent module's slot and this port, then write the command."""
        frame = self.parent.parent
        # The slot must be selected first: selecting a slot resets the port to 1.
        frame.write(f":SLOT {self.parent.id}")
        frame.write(f":PORT {self.id}")
        frame.write(command, **kwargs)

    current = Channel.measurement(
        ":IPD:ACT?",
        """Measure the photodiode current, in A (float).""",
    )

    optical_power = Channel.measurement(
        ":POPT:ACT?",
        """Measure the optical power, in W (float).""",
    )

    sensitivity = Channel.control(
        ":CALPD:SET?", ":CALPD:SET %g",
        """Control the photodiode sensitivity used to convert current to optical
        power, in A/W (float).""",
    )

    pd_polarity = Channel.control(
        ":PDPOL?", ":PDPOL %s",
        """Control the photodiode polarity, ``AG`` (anode grounded) or ``CG``
        (cathode grounded) (str).""",
        validator=strict_discrete_set,
        values=["AG", "CG"],
        cast=str,
    )

    measurement_range = Channel.control(
        ":RANGE?", ":RANGE %d",
        """Control the measurement range as the full-scale photodiode current, in A.
        One of 10e-9, 100e-9, 1e-6, 10e-6, 100e-6, 1e-3 or 10e-3 (float).""",
        validator=strict_discrete_set,
        values={
            10e-9: 1,
            100e-9: 2,
            1e-6: 3,
            10e-6: 4,
            100e-6: 5,
            1e-3: 6,
            10e-3: 7,
        },
        map_values=True,
        cast=int,
    )

    bias_enabled = Channel.control(
        ":PDBIA?", ":PDBIA %s",
        """Control whether the photodiode bias voltage is enabled (bool).""",
        validator=strict_discrete_set,
        values={True: "ON", False: "OFF"},
        map_values=True,
        cast=str,
    )

    bias_voltage = Channel.control(
        ":VBIAS:SET?", ":VBIAS:SET %g",
        """Control the photodiode bias voltage, in V (float).""",
    )


class PDAChannel(Pro8Channel):
    """A photodiode amplifier module (PDA8xxx) with one or two independent ports.

    The number of ports depends on the module variant: the PDA8000-1 has a
    single port, the PDA8000-2 has two. The ports are accessible via the
    ``ports`` dictionary (keyed by port number) or the ``port_1`` / ``port_2``
    attributes.
    """

    def __init__(self, parent, id, port_count=2, **kwargs):
        super().__init__(parent, id, **kwargs)
        for port in range(1, port_count + 1):
            self.add_child(PDAPortChannel, port, collection="ports", prefix="port_")


# Module type ids reported by ``:CONFIG:PLUG?`` / ``:TYPE:ID?`` and the channel
# class used to control them. Ids without a dedicated class (0 = empty slot,
# 47 = MLC8xxx, 249 = WDM-B) do not create a channel.
MODULE_CHANNELS = {
    107: PDAChannel,
    159: ITCChannel,
    191: LDCChannel,
    223: TEDChannel,
}

MODULE_NAMES = {
    0: "empty",
    47: "MLC8xxx",
    107: "PDA8xxx",
    159: "ITC8xxx",
    191: "LDC8xxx",
    223: "TED8xxx",
    249: "WDM-B",
}


class ThorlabsPro8000(SCPIMixin, Instrument):
    """Represents a Thorlabs PRO8000 / PRO800 modular laser driver mainframe.

    On connection the mainframe is queried for its installed modules
    (``:CONFIG:PLUG?``) and a :class:`Channel` is created for every populated slot
    that holds a supported module. Channels are accessible through the ``channels``
    dictionary (keyed by slot number) or the ``ch_<slot>`` attributes:

    .. code-block:: python

        pro8000 = ThorlabsPro8000("GPIB::10")
        pro8000.channels[1].laser_enabled = True      # slot 1 holds an LDC module
        print(pro8000.channels[2].temperature)        # slot 2 holds a TED module

    Supported modules are LDC8xxx (:class:`LDCChannel`), TED8xxx
    (:class:`TEDChannel`), ITC8xxx (:class:`ITCChannel`) and PDA8xxx
    (:class:`PDAChannel`, whose one or two ports are :class:`PDAPortChannel`).

    Over the serial port the mainframe requires RTS/CTS hardware handshaking and
    needs a short pause between a command and its response; both are configured by
    default. The baud rate must match the setting of the mainframe's rear DIP
    switches (factory default 19200).
    """

    def __init__(self, adapter, name="Thorlabs Pro 8000", baud_rate=19200, **kwargs):
        kwargs.setdefault("timeout", 5000)
        super().__init__(
            adapter,
            name,
            asrl={
                "baud_rate": baud_rate,
                # The mainframe only sends once the host asserts RTS, and it needs
                # time to assemble the answer before it can be read back.
                "flow_control": ControlFlow.rts_cts,
                "query_delay": 0.05,
                "read_termination": "\n",
                "write_termination": "\n",
            },
            **kwargs,
        )
        # Respond with bare values (without the command mnemonic) to simplify parsing.
        self.write(":SYST:ANSW VALUE")
        self._create_module_channels()

    def get_module_ids(self):
        """Get the list of module type ids for all slots (``:CONFIG:PLUG?``).

        :return: List of integer module ids, one per slot (see
            :data:`~pymeasure.instruments.thorlabs.thorlabspro8000.MODULE_NAMES`).
        """
        values = self.values(":CONFIG:PLUG?")
        # (type, subtype) pairs are returned, one pair per slot.
        return [int(v) for v in values[0::2]]

    def _create_module_channels(self):
        """Create a channel for every slot holding a supported module."""
        self.channels = {}
        values = self.values(":CONFIG:PLUG?")
        # (type, subtype) pairs are returned, one pair per slot.
        module_ids = [int(v) for v in values[0::2]]
        subtypes = [int(v) for v in values[1::2]]
        for slot, (module_id, subtype) in enumerate(zip(module_ids, subtypes), start=1):
            channel_class = MODULE_CHANNELS.get(module_id)
            if channel_class is None:
                continue
            if channel_class is PDAChannel:
                # For the PDA the subtype is the model variant and equals the port
                # count: the PDA8000-1 (subtype 1) has one port, the PDA8000-2
                # (subtype 2) has two.
                self.add_child(channel_class, slot, port_count=subtype)
            else:
                self.add_child(channel_class, slot)
