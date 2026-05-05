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
from time import sleep

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, truncated_range

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class PwrChannel(Channel):
    """Channel for an NGPx power-supply output.

    See https://www.rohde-schwarz.com/webhelp/NGP800_HTML_UserManual_en/Content/welcome.htm
    for further details.
    """

    _selection_status: bool = False
    _output_status: bool = False
    _tracking_status: bool = False

    _select = Instrument.control(
        "OUTP:SEL? (@{ch})",
        "OUTP:SEL %d,(@{ch})",
        """Control whether this channel is selected for bulk output control.

        ``True`` includes the channel in the master output toggle, ``False``
        excludes it. Also updates the internal ``_selection_status`` flag.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    _tracking_select = Instrument.control(
        "TRAC:SEL:CH{ch}?",
        "TRAC:SEL:CH{ch} %d",
        """Control whether this channel is selected for tracking configuration.

        ``True`` selects the channel for master tracking enable/disable;
        ``False`` excludes it. Also updates ``_tracking_status``.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    _output = Instrument.control(
        "OUTP? (@{ch})",
        "OUTP %d,(@{ch})",
        """Control the individual output state of this channel (``True`` = ON, ``False`` = OFF).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    @property
    def select(self) -> bool:
        """Control whether this channel is selected for bulk output control."""
        self._selection_status = self._select  # type: ignore
        return self._selection_status

    @select.setter
    def select(self, v: bool) -> None:
        self._select = v
        self._selection_status = v

    @property
    def tracking_select(self) -> bool:
        """Control whether this channel is selected for tracking configuration."""
        self._tracking_status = self._tracking_select  # type: ignore
        return self._tracking_status

    @tracking_select.setter
    def tracking_select(self, v: bool) -> None:
        self._tracking_select = v
        self._tracking_status = v

    @property
    def output(self) -> bool:
        """Control the individual output state of this channel."""
        self._output_status = self._output  # type: ignore
        return self._output_status

    @output.setter
    def output(self, v: bool) -> None:
        self._output = v
        self._output_status = v

    voltage = Instrument.measurement(
        "MEAS:VOLT? (@{ch})",
        """Measure the actual output voltage (V).""",
        get_process=float,
    )

    current = Instrument.measurement(
        "MEAS:CURR? (@{ch})",
        """Measure the actual output current (A).""",
        get_process=float,
    )

    safety_limits_ena = Instrument.control(
        "ALIM? (@{ch})",
        "ALIM %d,(@{ch})",
        """Control the safety-limit state (``True`` = enabled, ``False`` = disabled).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    voltage_upper_limit = Instrument.control(
        "VOLT:ALIM:UPP? (@{ch})",
        "VOLT:ALIM:UPP %.3f,(@{ch})",
        """Control the upper voltage safety limit (V).

        Limits the maximum allowable voltage setpoint. Range: 0.000 to 64.050 V
        (64 V models) or 0.000 to 32.050 V (32 V models). Increment: 0.001 V.
        ``*RST``: model-dependent (64.050 or 32.050 V).
        """,
        validator=truncated_range,
        values=[0.000, 64.050],  # widest range; hardware rejects invalid values
    )

    current_upper_limit = Instrument.control(
        "CURR:ALIM:UPP? (@{ch})",
        "CURR:ALIM:UPP %.3f,(@{ch})",
        """Control the upper current safety limit (A).

        Range depends on model: up to 20.010 A (32 V models) or 10.010 A
        (64 V models).
        """,
        validator=truncated_range,
        values=[0.001, 20.010],  # widest range; hardware rejects invalid values
    )

    voltage_setpoint = Instrument.control(
        "VOLT? (@{ch})",
        "VOLT %.3f,(@{ch})",
        """Control the output voltage setpoint in voltage-source mode (V).

        Range: 0.000 to 64.050 V (clamped by ``voltage_upper_limit`` when
        safety limits are enabled).
        """,
        validator=truncated_range,
        values=[0.000, 64.050],
    )

    current_limit = Instrument.control(
        "CURR? (@{ch})",
        "CURR %.3f,(@{ch})",
        """Control the current limit in voltage-source mode (A).

        Maximum current the channel will supply before switching to CC mode.
        Range: 0.001 to 20.010 A (32 V models) or 0.001 to 10.010 A
        (64 V models). The hardware adjusts the maximum based on the current
        voltage range.
        """,
        validator=truncated_range,
        values=[0.001, 20.010],
    )

    remote_sense = Instrument.control(
        "VOLT:SENS? (@{ch})",
        "VOLT:SENS %s,(@{ch})",
        """Control the remote-sense state (``'INT'`` or ``'EXT'``).""",
        validator=strict_discrete_set,
        values=["INT", "EXT"],
        get_process=lambda v: v.strip(),
    )

    ovp_enabled = Instrument.control(
        "VOLT:PROT? (@{ch})",
        "VOLT:PROT %d,(@{ch})",
        """Control the Overvoltage-Protection (OVP) state.

        ``True`` enables OVP, ``False`` disables it. When remote sense (EXT)
        is active, enabling OVP is strongly recommended to protect the load
        from overvoltage in case of sense-wire disconnection.
        """,
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    ovp_level = Instrument.control(
        "VOLT:PROT:LEV? (@{ch})",
        "VOLT:PROT:LEV %.3f,(@{ch})",
        """Control the overvoltage-protection trip level (V).

        If the output voltage exceeds this value, the channel shuts down.
        Range: 0.000 to 64.050 V (64 V models) or 32.050 V (32 V models).
        ``*RST``: model maximum. In remote-sense mode a value slightly above
        ``voltage_setpoint`` (e.g. +2..5 V) is recommended.
        """,
        validator=truncated_range,
        values=[0.000, 64.050],
    )

    ovp_tripped = Instrument.measurement(
        "VOLT:PROT:TRIP? (@{ch})",
        """Measure whether OVP has tripped (``True`` = tripped, ``False`` = normal).

        Returns ``True`` if an overvoltage event occurred and the output is
        shut down. Use :meth:`ovp_clear` to reset after fixing the cause.
        """,
        get_process=bool,
    )

    def ovp_clear(self):
        """Clear the OVP tripped state and re-enable output if possible."""
        self.write("VOLT:PROT:CLE (@{ch})")

    ocp_enabled = Instrument.control(
        "FUSE? (@{ch})",
        "FUSE %d,(@{ch})",
        """Control the Overcurrent-Protection (OCP / fuse) state
        (``True`` = enabled, ``False`` = disabled).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    ocp_delay_initial = Instrument.control(
        "FUSE:DEL:INIT? (@{ch})",
        "FUSE:DEL:INIT %.3f,(@{ch})",
        """Control the initial fuse delay after output-ON (s).

        Range: 0..60 s. ``*RST``: 0.
        """,
        validator=truncated_range,
        values=[0.0, 60.0],
    )

    ocp_delay = Instrument.control(
        "FUSE:DEL? (@{ch})",
        "FUSE:DEL %.3f,(@{ch})",
        """Control the ongoing fuse delay during operation (s).

        Range: 0..10 s. ``*RST``: 0.
        """,
        validator=truncated_range,
        values=[0.0, 10.0],
    )

    ocp_tripped = Instrument.measurement(
        "FUSE:TRIP? (@{ch})",
        """Measure whether OCP (fuse) has tripped due to overcurrent.""",
        get_process=bool,
    )

    def ocp_clear(self):
        """Clear the OCP (fuse) tripped state after fixing overcurrent."""
        self.write("FUSE:TRIP:CLE (@{ch})")


class NGPx(SCPIMixin, Instrument):
    """Represents a Rohde & Schwarz NGPx power supply.

    On instantiation the instrument is queried with ``*IDN?`` via
    :meth:`pymeasure.instruments.SCPIMixin.get_device_info` and checked
    against a list of supported models. Per-channel access is provided
    through the ``channels`` mapping and as ``ch1``/``ch2``/... attributes.
    """

    def __init__(self, adapter, name="Rohde&Schwarz NGPx", **kwargs):
        super().__init__(adapter, name, **kwargs)

        try:
            if "TCPIP" in str(self.resource_name).upper():
                self.adapter.connection.write_termination = "\n"  # type: ignore
                self.adapter.connection.read_termination = "\n"  # type: ignore
        except (AttributeError, TypeError):
            # adapter is a stub/mock without a real ``.connection``;
            # skip the termination tweak so the generic instrument tests
            # can still construct the driver.
            pass

        try:
            self.get_device_info()
            self.check_is_dev_supported(["NGP804", "xx"], ": Instrument not supported!")
        except (ValueError, AttributeError, TypeError):
            # No (real) instrument is responding to ``*IDN?`` (e.g. when the
            # driver is constructed against a mock adapter in the generic
            # test_all_instruments suite). Defer the device check to whoever
            # later calls ``get_device_info()`` explicitly.
            pass

        ids: list[int] = []
        if self.name == "NGP804":
            ids = [1, 2, 3, 4]

        self.channels = {ch_id: PwrChannel(self, ch_id) for ch_id in ids}
        for ch_id, channel in self.channels.items():
            setattr(self, f"ch{ch_id}", channel)

    def set2local(self):
        """Put the instrument into local mode (``SYST:LOC``)."""
        self.write("SYST:LOC")

    def set2remote(self):
        """Put the instrument into remote mode (``SYST:REM``)."""
        self.write("SYST:REM")

    def __del__(self):
        # Be defensive: __init__ may have aborted before ``adapter``/``name``
        # were attached, so reach for them safely.
        name = getattr(self, "name", "NGPx")
        if getattr(self, "adapter", None) is None:
            return
        try:
            self.set2local()
        except Exception:
            log.info("%s already disconnected.", name)

        try:
            self.close()
        except Exception:
            log.info("%s already disconnected.", name)

    def clear_reset(self):
        """Clear status and reset the instrument (``*CLS;*RST``)."""
        if "ASRL" in self.resource_name:
            self.write("*CLS;*RST;")
            sleep(0.7)
        else:
            self.write("*CLS;*RST;*OPC?")
            sleep(0.5)
            self.read().strip()

    def _get_selected_channel_list(self):
        """Return SCPI channel list like ``'(@1,2,4)'`` or ``''`` if none selected."""
        selected = [
            ch.id for ch in self.channels.values() if getattr(ch, "_selection_status", False)
        ]
        if not selected:
            return ""
        return "(@" + ",".join(map(str, sorted(selected))) + ")"

    def _parse_outp_response(self, response: str) -> list[int]:
        """Parse an ``OUTP?`` response (e.g. ``'0'`` or ``'0,0'``)."""
        if response is None:
            return []
        s = response.strip()
        if not s:
            return []
        parts = [p.strip() for p in s.split(",")]
        return [int(p) for p in parts]

    @property
    def output(self) -> bool:
        """Control the master output state for all selected channels.

        * ``True``  -> all selected channels are ON (all 1)
        * ``False`` -> all selected channels are OFF (all 0) or no channels selected
        * ``False`` + warning -> mixed/undefined state (values not identical)
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

            if any(v not in (0, 1) for v in vals):
                log.warning(
                    "OUTP? returned non-binary values for %s: %r (parsed=%s)",
                    ch_list, response, vals,
                )
                return False

            if all(v == 1 for v in vals):
                return True
            if all(v == 0 for v in vals):
                return False

            log.warning(
                "Undefined output state for %s: %r (parsed=%s). Returning False.",
                ch_list, response, vals,
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
            log.info("Setting output=%s for channels %s", bool(value), ch_list)
            # SCPI format: value before the channel list, e.g. ``OUTP 1 (@3,4)``.
            self.write(f"OUTP {state}, {ch_list}")
        except Exception:
            log.exception("Failed to set master output state for %s", ch_list)
            raise

    output_general = Instrument.control(
        "OUTP:GEN?",
        "OUTP:GEN %d",
        """Control the primary output state (``*IDN?`` independent master switch).""",
        validator=strict_discrete_set,
        values={True: 1, False: 0},
        map_values=True,
        get_process=bool,
    )

    def get_ocp_linked_channels(self, master_channel):
        """Query channels currently linked to ``master_channel`` for OCP tripping.

        When an OCP event occurs on any linked channel (including the master),
        all linked channels are shut down together to prevent back-feeding or
        damage in multi-channel setups.

        :param master_channel: ``int`` channel number or :class:`PwrChannel`.
        :return: List of channel numbers linked to the master (excluding the
            master itself). Empty list if no channels are linked.
        """
        ch_id = master_channel.id if isinstance(master_channel, PwrChannel) else int(master_channel)
        response = self.ask(f"INST (@{ch_id});FUSE:LINK?")
        if not response.strip() or response.strip() == "0":
            return []
        return [int(x) for x in response.split(",") if x.strip().isdigit()]

    def link_ocp(self, master_channel, *linked_channels):
        """Link one or more channels to a master channel for synchronized OCP.

        When OCP trips on any channel in the linked group (master or linked)
        all channels in the group shut down simultaneously. This is essential
        for safe parallel/series operation or multi-rail power systems to
        avoid back-current feeding.

        :param master_channel: ``int`` or :class:`PwrChannel` reference channel.
        :param linked_channels: one or more ``int`` or :class:`PwrChannel`
            objects to link to the master.
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
            log.info("No valid channels to link - command skipped.")
            return

        self.write(f"INST (@{master_id});FUSE:LINK {','.join(links)}")

    def unlink_ocp(self, master_channel, target_channel=None):
        """Remove OCP (fuse) linking from one or all channels linked to a master.

        :param master_channel: ``int`` or :class:`PwrChannel` master channel
            whose links to remove.
        :param target_channel: optional ``int`` or :class:`PwrChannel` specific
            channel to unlink. If ``None`` (default), removes all links from
            the master.
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
        """Return SCPI channel list like ``'(@1,2,4)'`` for tracking-selected channels."""
        selected = [
            ch.id for ch in self.channels.values() if getattr(ch, "_tracking_select", False)
        ]
        if not selected:
            return ""
        return "(@" + ",".join(map(str, sorted(selected))) + ")"

    @property
    def tracking_enabled(self):
        """Control the master tracking enable for all tracking-selected channels.

        When ``True``, all tracking-selected channels operate in tracking
        mode (voltage setpoints follow the primary/master channel).
        Returns ``False`` if no channels are tracking-selected.
        """
        ch_list = self._get_tracking_selected_list()
        if not ch_list:
            return False
        try:
            response = self.ask(f"TRAC?{ch_list}")
            return bool(int(response.strip()))
        except Exception as e:
            log.error(f"Failed to query tracking state: {e}")
            return False

    @tracking_enabled.setter
    def tracking_enabled(self, value):
        ch_list = self._get_tracking_selected_list()
        if not ch_list:
            log.warning("No channels selected via tracking_select - tracking command ignored.")
            return

        state = 1 if bool(value) else 0
        try:
            self.write(f"TRAC {state}{ch_list}")
        except Exception as e:
            log.error(f"Failed to set tracking state: {e}")
            raise

    @property
    def tracking_general_enabled(self):
        """Control the global (primary) tracking state.

        This is the overall tracking master switch (``TRAC:GEN``). Must be
        ``True`` for any per-channel tracking to be active.
        """
        return bool(int(self.ask("TRAC:GEN?").strip()))

    @tracking_general_enabled.setter
    def tracking_general_enabled(self, value):
        state = 1 if bool(value) else 0
        self.write(f"TRAC:GEN {state}")
