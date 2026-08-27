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

"""Rohde & Schwarz NGPx programmable power-supply family driver.

Supports NGP802 / NGP812 (2-channel) and NGP804 / NGP814 (4-channel) models.

Minimal usage example::

    from pymeasure.instruments.rohdeschwarz.ngpx import NGPx

    psu = NGPx("TCPIP::192.168.1.10::INSTR")   # or pass a shared ResourceManager

    psu.ch1.voltage_setpoint = 5.0
    psu.ch1.current_limit = 1.0
    psu.ch1.output = True
    print(psu.ch1.voltage, psu.ch1.current)
    psu.ch1.output = False

See https://www.rohde-schwarz.com/webhelp/NGP800_HTML_UserManual_en for the
full SCPI command reference.
"""

import logging
from time import sleep

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PwrChannel(Channel):
    """One output channel of an NGPx power supply.

    Channels are created dynamically by :class:`NGPx.__init__` based on the
    detected model, and exposed as ``inst.ch1``, ``inst.ch2``, etc.
    """

    _selection_status: bool = False
    _output_status: bool = False
    _tracking_status: bool = False

    _select = Instrument.control(
        "OUTP:SEL? (@{ch})",
        "OUTP:SEL %d,(@{ch})",
        """Control whether this channel is selected for bulk output control (bool).
        True = selected (included in master output toggle), False = not selected.
        Also updates internal _selection_status flag.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    _tracking_select = Instrument.control(
        "TRAC:SEL:CH{ch}?",
        "TRAC:SEL:CH{ch} %d",
        """Control whether this channel is selected for tracking configuration (bool).
        True = channel is selected for master tracking enable/disable.
        False = channel excluded from master tracking control.
        Also updates internal _tracking_select flag.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    _output = Instrument.control(
        "OUTP? (@{ch})",
        "OUTP %d,(@{ch})",
        "Control the individual per-channel output state (bool). True = ON, False = OFF.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    @property
    def select(self) -> bool:
        """Control whether this channel is selected for bulk output control (bool)."""
        self._selection_status = self._select  # type: ignore
        return self._selection_status

    @select.setter
    def select(self, v: bool) -> None:
        self._select = v
        self._selection_status = v

    @property
    def tracking_select(self) -> bool:
        """Control whether this channel is selected for tracking configuration (bool)."""
        self._tracking_status = self._tracking_select  # type: ignore
        return self._tracking_status

    @tracking_select.setter
    def tracking_select(self, v: bool) -> None:
        self._tracking_select = v
        self._tracking_status = v

    @property
    def output(self) -> bool:
        """Control the per-channel output state (bool). True = ON, False = OFF."""
        self._output_status = self._output  # type: ignore
        return self._output_status

    @output.setter
    def output(self, v: bool) -> None:
        self._output = v
        self._output_status = v

    voltage = Instrument.measurement(
        "MEAS:VOLT? (@{ch})",
        "Measure the actual output voltage (V).",
        get_process=float,
    )

    current = Instrument.measurement(
        "MEAS:CURR? (@{ch})",
        "Measure the actual output current (A).",
        get_process=float,
    )

    safety_limits_ena = Instrument.control(
        "ALIM? (@{ch})",
        "ALIM %d,(@{ch})",
        "Control the safety limit state (bool). True = enabled, False = disabled.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    voltage_upper_limit = Instrument.control(
        "VOLT:ALIM:UPP? (@{ch})",
        "VOLT:ALIM:UPP %.3f,(@{ch})",
        "Control the upper voltage safety limit (V). "
        "This limits the maximum allowable voltage setpoint. "
        "Range: 0.000 to 64.050 V (for 64 V models) or 0.000 to 32.050 V (for 32 V models). "
        r"Increment: 0.001 V. \*RST: model-dependent (64.050 or 32.050 V)",
        validator=truncated_range,
        values=[0.000, 64.050],  # use widest range; hardware rejects invalid values
    )

    current_upper_limit = Instrument.control(
        "CURR:ALIM:UPP? (@{ch})",
        "CURR:ALIM:UPP %.3f,(@{ch})",
        "Control the upper current safety limit (A). "
        "Range depends on model: up to 20.010 A (32V models) or 10.010 A (64V models).",
        validator=truncated_range,
        values=[0.001, 20.010],  # widest range — hardware will reject invalid values
    )

    voltage_setpoint = Instrument.control(
        "VOLT? (@{ch})",
        "VOLT %.3f,(@{ch})",
        "Control the output voltage setpoint in voltage source mode (V). "
        "This is the target voltage the channel regulates to. "
        "Range: 0.000 to 64.050 V (clamped by voltage_upper_limit if safety limits are enabled).",
        validator=truncated_range,
        values=[0.000, 64.050],
    )

    current_limit = Instrument.control(
        "CURR? (@{ch})",
        "CURR %.3f,(@{ch})",
        "Control the current limit in voltage source mode (A). "
        "Maximum current the channel will supply before switching to CC mode. "
        "Range: 0.001 to 20.010 A (32 V models) or 0.001 to 10.010 A (64 V models). "
        "Hardware limits max based on current voltage range.",
        validator=truncated_range,
        values=[0.001, 20.010],  # widest possible range — instrument will reject invalid values
    )

    sense = Instrument.control(
        "VOLT:SENS? (@{ch})",
        "VOLT:SENS %s,(@{ch})",
        "Control the remote sense state: 'INT' (internal), 'EXT' (external/remote).",
        validator=strict_discrete_set,
        values=["INT", "EXT"],
        cast=str,
        get_process=lambda v: v.strip(),
    )

    # Overvoltage Protection (OVP / VOLT:PROT)
    ovp_enabled = Instrument.control(
        "VOLT:PROT? (@{ch})",
        "VOLT:PROT %d,(@{ch})",
        """Control the Overvoltage Protection (OVP) state (bool).
        True = OVP enabled (active), False = disabled.

        When remote sense (EXT) is active, it is strongly recommended to enable OVP
        to protect the load from overvoltage in case of sense wire disconnection.""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    ovp_level = Instrument.control(
        "VOLT:PROT:LEV? (@{ch})",
        "VOLT:PROT:LEV %.3f,(@{ch})",
        r"""Control the overvoltage protection trip level (V).
        If the output voltage exceeds this value, the channel shuts down.
        Range: 0.000 to 64.050 V (64 V models) or 32.050 V (32 V models).
        \*RST: model maximum (64.050 or 32.050 V)

        Recommended setting in remote sense mode: slightly above your voltage_setpoint
        (e.g., voltage_setpoint + 2-5 V).""",
        validator=truncated_range,
        values=[0.000, 64.050],
    )

    ovp_tripped = Instrument.measurement(
        "VOLT:PROT:TRIP? (@{ch})",
        """Measure whether OVP has tripped (bool). True = tripped, the output is shut down.
        Use ovp_clear() to reset after fixing the cause.""",
        get_process=bool,
    )

    def ovp_clear(self):
        """Clear the OVP tripped state and re-enable output if possible."""
        self.write("VOLT:PROT:CLE (@{ch})")

    # Overcurrent Protection (OCP / Fuse)
    ocp_enabled = Instrument.control(
        "FUSE? (@{ch})",
        "FUSE %d,(@{ch})",
        "Control the Overcurrent Protection (OCP/Fuse) state (bool)."
        " True = enabled, False = disabled.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    ocp_delay_initial = Instrument.control(
        "FUSE:DEL:INIT? (@{ch})",
        "FUSE:DEL:INIT %.3f,(@{ch})",
        r"Control the initial fuse delay after output ON (s). Range: 0-60 s. \*RST: 0",
        validator=truncated_range,
        values=[0.0, 60.0],
    )

    ocp_delay = Instrument.control(
        "FUSE:DEL? (@{ch})",
        "FUSE:DEL %.3f,(@{ch})",
        r"Control the ongoing fuse delay during operation (s). Range: 0-10 s. \*RST: 0",
        validator=truncated_range,
        values=[0.0, 10.0],
    )

    ocp_tripped = Instrument.measurement(
        "FUSE:TRIP? (@{ch})",
        "Measure whether OCP (fuse) has tripped due to overcurrent (bool). True = tripped.",
        get_process=bool,
    )

    def ocp_clear(self):
        """Reset the OCP (fuse) tripped state after fixing overcurrent."""
        self.write("FUSE:TRIP:CLE (@{ch})")


class NGPx(SCPIMixin, Instrument):
    """Represent a Rohde & Schwarz NGPx programmable power supply.

    The constructor queries ``*IDN?`` to detect the connected model, populates
    :attr:`name`, :attr:`vendor`, :attr:`serial_number`, and
    :attr:`firmware_ref`, and creates channel objects (``ch1``, ``ch2``, …)
    based on the detected model.

    :param adapter: VISA resource string or a :class:`pyvisa.ResourceManager`
        (when a ``ResourceManager`` is passed, ``name`` is the VISA resource
        string and the manager is *not* closed on exit).
    :param name: VISA resource string when ``adapter`` is a
        ``ResourceManager``, otherwise an optional label.
    :param \\**kwargs: Forwarded to :class:`.Instrument`.
    """

    def __init__(self, adapter, name="Rohde Schwarz NGPx", **kwargs):
        super().__init__(adapter, name, **kwargs)

        resource = getattr(self, "resource_name", None) or ""
        if "TCPIP" in resource.upper():
            self.adapter.connection.write_termination = "\n"  # type: ignore
            self.adapter.connection.read_termination = "\n"  # type: ignore

        ids = []

        self.get_device_info()
        self.check_is_dev_supported(
            ["NGP804", "NGP814", "NGP802", "NGP812"], ": Instrument not supported!"
        )

        if self.name in ("NGP804", "NGP814"):
            ids = [1, 2, 3, 4]
        elif self.name in ("NGP802", "NGP812"):
            ids = [1, 2]
        else:
            pass

        self.channels = {ch_id: PwrChannel(self, ch_id) for ch_id in ids}
        for ch_id, channel in self.channels.items():
            setattr(self, f"ch{ch_id}", channel)

    def open(self):
        self.adapter.open()

        if "TCPIP" in self.adapter.resource_name.upper():
            self.adapter.connection.write_termination = "\n"  # type: ignore
            self.adapter.connection.read_termination = "\n"  # type: ignore

    def set2local(self):
        self.write("SYST:LOC")

    def set2remote(self):
        self.write("SYST:REM")

    def __del__(self):
        try:
            self.set2local()
        except Exception:  # noqa: BLE001
            log.info(self.name + " already disconnected.")

        try:
            self.close()
        except Exception:  # noqa: BLE001
            log.info(self.name + " already disconnected.")

    def clear_reset(self):
        """Clear instrument status and reset to factory defaults."""
        resource = getattr(self, "resource_name", None) or ""
        if "ASRL" in resource:
            self.write("*CLS;*RST;")
            sleep(0.7)
        else:
            self.write("*CLS;*RST;*OPC?")
            sleep(0.5)
            self.read().strip()

    def _get_selected_channel_list(self):
        """Return SCPI channel list string like '(@1,2,4)' or empty string if none selected."""
        selected: list[int] = [
            ch.id
            for ch in self.channels.values()
            if isinstance(ch.id, int) and getattr(ch, "_selection_status", False)
        ]
        if not selected:
            return ""
        return "(@" + ",".join(map(str, sorted(selected))) + ")"

    def _parse_outp_response(self, response: str) -> list[int]:
        """Parse a comma-separated ``OUTP?`` response into a list of integers."""
        if response is None:
            return []
        s = response.strip()
        if not s:
            return []
        return [int(p.strip()) for p in s.split(",")]

    @property
    def output(self) -> bool:
        """Control the master output state for all selected channels (bool).

        True  -> all selected channels are ON (all 1)
        False -> all selected channels are OFF (all 0) OR no channels selected
        False + warning -> mixed/undefined state (not identical)
        """
        ch_list = self._get_selected_channel_list()
        if not ch_list:
            log.info("No channels selected; output=False")
            return False

        try:
            response = self.ask(f"OUTP? {ch_list}")
            vals = self._parse_outp_response(response)

            if not vals:
                log.warning("OUTP? returned empty response for %s: %r", ch_list, response)
                return False

            # normalize: some devices might respond with more than 0/1; treat nonzero as 1?
            # If you want strict 0/1 only, keep the check below.
            if any(v not in (0, 1) for v in vals):
                log.warning(
                    "OUTP? returned non-binary values for %s: %r (parsed=%s)",
                    ch_list,
                    response,
                    vals,
                )
                return False

            if all(v == 1 for v in vals):
                return True
            if all(v == 0 for v in vals):
                return False

            # Mixed state
            log.warning(
                "Undefined output state for %s: %r (parsed=%s). Returning False.",
                ch_list,
                response,
                vals,
            )
            return False

        except Exception:
            log.exception("Failed to query master output state for %s", ch_list)
            return False

    @output.setter
    def output(self, value: bool) -> None:
        ch_list = self._get_selected_channel_list()
        if not ch_list:
            log.warning("No channels selected; master output command ignored.")
            return

        state = 1 if bool(value) else 0

        try:
            self.write(f"OUTP {state},{ch_list}")
        except Exception:
            log.exception("Failed to set master output state for %s", ch_list)
            raise

    output_general = Instrument.control(
        "OUTP:GEN?",
        "OUTP:GEN %d",
        "Control the primary output state (bool). True = on, False = off.",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    def get_ocp_linked_channels(self, master_channel) -> list[int]:
        """Query channels linked to *master_channel* for synchronized OCP tripping.

        When an OCP event occurs on any channel in a linked group, all channels
        in that group shut down to prevent back-feeding.

        :param master_channel: Channel number (int) or :class:`PwrChannel`.
        :returns: List of channel numbers linked to the master (excluding the
            master itself). Empty list when nothing is linked.
        """
        ch_id = master_channel.id if isinstance(master_channel, PwrChannel) else int(master_channel)
        response = self.ask(f"INST (@{ch_id});FUSE:LINK?")
        if not response.strip() or response.strip() == "0":
            return []
        return [int(x) for x in response.split(",") if x.strip().isdigit()]

    def link_ocp(self, master_channel, *linked_channels) -> None:
        """Link channels to *master_channel* for synchronized OCP protection.

        When OCP trips on any channel in the group all channels shut down
        simultaneously, preventing back-current in parallel/series setups.

        :param master_channel: Reference channel (int or :class:`PwrChannel`).
        :param linked_channels: One or more channels to link (int or
            :class:`PwrChannel`). Self-links are silently ignored.
        """
        master_id = (
            master_channel.id if isinstance(master_channel, PwrChannel) else int(master_channel)
        )
        links = []
        for ch in linked_channels:
            ch_id = ch.id if isinstance(ch, PwrChannel) else int(ch)
            if ch_id == master_id:
                continue  # avoid self-linking
            links.append(str(ch_id))

        if not links:
            log.info("No valid channels to link — command skipped.")
            return

        self.write(f"INST (@{master_id});FUSE:LINK {','.join(links)}")

    def unlink_ocp(self, master_channel, target_channel=None) -> None:
        """Remove OCP linking from channels linked to *master_channel*.

        :param master_channel: Master channel (int or :class:`PwrChannel`).
        :param target_channel: Specific channel to unlink (int or
            :class:`PwrChannel`). When ``None`` (default) all links from the
            master are removed.
        """
        master_id = (
            master_channel.id if isinstance(master_channel, PwrChannel) else int(master_channel)
        )

        if target_channel is None:
            self.write(f"INST (@{master_id});FUSE:UNL 0")
        else:
            target_id = (
                target_channel.id if isinstance(target_channel, PwrChannel) else int(target_channel)
            )
            self.write(f"INST (@{master_id});FUSE:UNL {target_id}")

    def _get_tracking_selected_list(self):
        """Return SCPI channel list like '(@1,2,4)' for tracking-selected channels."""
        selected: list[int] = [
            ch.id
            for ch in self.channels.values()
            if isinstance(ch.id, int) and getattr(ch, "_tracking_status", False)
        ]
        if not selected:
            return ""
        return "(@" + ",".join(map(str, sorted(selected))) + ")"

    @property
    def tracking_enabled(self):
        """Control the tracking state of all tracking-selected channels (boolean).

        Getter returns ``True`` only when every tracking-selected channel has
        tracking enabled; ``False`` when none are selected.
        Setter enables or disables tracking on all channels marked via
        :attr:`PwrChannel.tracking_select`.
        """
        ch_list = self._get_tracking_selected_list()
        if not ch_list:
            return False
        try:
            response = self.ask(f"TRAC? {ch_list}")
            return bool(int(response.strip()))
        except Exception:
            log.exception("Failed to query tracking state for %s", ch_list)
            return False

    @tracking_enabled.setter
    def tracking_enabled(self, value):
        ch_list = self._get_tracking_selected_list()
        if not ch_list:
            log.warning("No channels tracking-selected — tracking command ignored.")
            return

        state = 1 if bool(value) else 0
        try:
            self.write(f"TRAC {state},{ch_list}")
        except Exception:
            log.exception("Failed to set tracking state for %s", ch_list)
            raise

    @property
    def tracking_general_enabled(self):
        """Control the global (primary) tracking master switch (bool).

        This corresponds to TRACking:GENeral.
        Must be True for any per-channel tracking to be active.
        """
        return bool(int(self.ask("TRAC:GEN?").strip()))

    @tracking_general_enabled.setter
    def tracking_general_enabled(self, value):
        """Enable or disable the primary tracking function globally."""
        state = 1 if bool(value) else 0
        self.write(f"TRAC:GEN {state}")
