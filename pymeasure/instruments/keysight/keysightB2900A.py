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
from datetime import datetime, timedelta

import numpy as np
from pyvisa import VisaIOError

from pymeasure.instruments import Channel, Instrument, SCPIMixin
from pymeasure.instruments.validators import strict_discrete_set, strict_range, joined_validators


class KeysightB2900AChannel(Channel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    #######################################################################
    #                           source functions                          #
    #######################################################################

    source_output_enabled = Channel.control(
        ":outp{ch}?",
        ":outp{ch} %s",
        """Control whether to enable source output (bool).
        """,
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0.0, True: 1.0},
    )

    source_output_mode = Channel.control(
        ":sour{ch}:func:mode?",
        ":sour{ch}:func:mode %s",
        """Control the source output mode (str). Options are "CURR" or "VOLT".
        """,
        validator=strict_discrete_set,
        values=["CURR", "VOLT"],
    )

    source_output_shape = Channel.control(
        ":sour{ch}:func:shap?",
        ":sour{ch}:func:shap %s",
        """Control the source output mode (str). Options are "DC" or "PULS".
        """,
        validator=strict_discrete_set,
        values=["DC", "PULS"],
    )

    source_current = Channel.control(
        ":sour{ch}:curr?",
        ":sour{ch}:curr %g",
        """Control the source current (float). This takes immediate
        effect. `source_output_mode` needs to be set to "CURR".  """,
        validator=strict_range,
        values=[-3, 3],
    )

    source_current_triggered = Channel.control(
        ":sour{ch}:curr:trig?",
        ":sour{ch}:curr:trig %g",
        """Control the /triggered/ source current (float). This takes immediate
        effect. `source_output_mode` needs to be set to "CURR".  """,
        validator=strict_range,
        values=[-3, 3],
    )

    source_voltage = Channel.control(
        ":sour{ch}:volt?",
        ":sour{ch}:volt %g",
        """Control the source voltage (float). This takes immediate
        effect. `source_output_mode` needs to be set to "VOLT". See also `
        source_voltage_triggered`. """,
        validator=strict_range,
        values=[-210, 210],
    )

    source_voltage_triggered = Channel.control(
        ":sour{ch}:volt:trig?",
        ":sour{ch}:volt:trig %g",
        """Control the /triggered/ source voltage (float). This takes immediate
        effect. `source_output_mode` needs to be set to "VOLT".  """,
        validator=strict_range,
        values=[-210, 210],
    )

    output_protection_enabled = Channel.control(
        ":outp{ch}:prot?",
        ":outp{ch}:prot %s",
        """Control whether, when the compliance value is hit, the channel is
        disabled. """,
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0.0, True: 1.0},
    )

    compliance_current = Channel.control(
        ":sens{ch}:curr:prot?",
        ":sens{ch}:curr:prot %g",
        """Control the compliance current (float).""",
        validator=strict_range,
        values=[-3, 3],
    )

    compliance_voltage = Channel.control(
        ":sens{ch}:volt:prot?",
        ":sens{ch}:volt:prot %g",
        """Control the compliance voltage (float).""",
        validator=strict_range,
        values=[-210, 210],
    )

    pulse_delay = Channel.control(
        ":sour{ch}:pulse:del?",
        ":sour{ch}:pulse:del %g",
        """Control the pulse delay in s (float).""",
        validator=strict_range,
        values=[0, 99999],
    )

    pulse_width = Channel.control(
        ":sour{ch}:pulse:widt?",
        ":sour{ch}:pulse:widt %g",
        """Control the pulse width in s (float).""",
        validator=strict_range,
        values=[0, 99999],
    )

    #######################################################################
    #                          measure functions                          #
    #######################################################################

    current_measurement_range_auto = Channel.control(
        ":sens{ch}:curr:range:auto?",
        ":sens{ch}:curr:range:auto %s",
        """Control whether the current measurement range is automatically determined.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0.0, True: 1.0},
    )

    current_measurement_range = Channel.control(
        ":sens{ch}:curr:rang?",
        ":sens{ch}:curr:range %g",
        """Control the the range of a current measurement. Ensure that
        `current_measurement_range_auto` is set to false before use.""",
    )

    current_measurement_speed = Channel.control(
        ":sens{ch}:curr:aper?",
        ":sens{ch}:curr:aper %g",
        """Control the measurement speed for a current measurement in seconds.
        This the integration time of a single measurement. Consider also the alternative `current_measurement_speed_nplc`
        """,
    )

    current_measurement_speed_nplc = Channel.control(
        ":sens{ch}:curr:nplc?",
        ":sens{ch}:curr:nplc %g",
        """Control the measurement speed for a current measurement in #powerline cycles.
        This the integration time of a single measurement. Consider also the alternative `current_measurement_speed`.
        """,
        validator=strict_range,
        values=[4.8e-4, 120],  # 60-Hz system
    )

    measured_current = Channel.measurement(
        ":meas:curr? (@{ch})",
        """Perform a current spot measurement""",
    )

    @property
    def measured_current_array(self):
        """Fetch the measured current array (as float64)"""
        return self._get_measured_array("curr")

    voltage_measurement_range_auto = Channel.control(
        ":sens{ch}:volt:range:auto?",
        ":sens{ch}:volt:range:auto %s",
        """Control whether the voltage measurement range is automatically determined.""",
        validator=strict_discrete_set,
        map_values=True,
        values={False: 0.0, True: 1.0},
    )

    voltage_measurement_range = Channel.control(
        ":sens{ch}:volt:rang?",
        ":sens{ch}:volt:range %g",
        """Control the the range of a voltage measurement. Ensure that
        `voltage_measurement_range_auto` is set to false before use.""",
    )

    voltage_measurement_speed = Channel.control(
        ":sens{ch}:volt:aper?",
        ":sens{ch}:volt:aper %g",
        """Set the measurement speed for a voltage measurement in seconds.
        This the integration time of a single measurement. Consider also the alternative `voltage_measurement_speed_nplc`.
        """,
    )

    voltage_measurement_speed_nplc = Channel.control(
        ":sens{ch}:volt:nplc?",
        ":sens{ch}:volt:nplc %g",
        """Control the measurement speed for a current measurement in #powerline cycles.
        This the integration time of a single measurement. Consider also the alternative `voltage_measurement_speed`.
        """,
        validator=strict_range,
        values=[4.8e-4, 120],  # 60-Hz system
    )

    measured_voltage = Channel.measurement(
        ":meas:volt? (@{ch})",
        """Perform a voltage spot measurement""",
    )

    @property
    def measured_voltage_array(self):
        """Fetch the measured voltage array (as float64)"""
        return self._get_measured_array("volt")

    def _get_measured_array(self, v_or_c):
        """Fetch the a measurement array as float64"""
        old_format = self.ask(":form?").strip()
        self.write(":form REAL,64")
        self.write(f":fetc:arr:{v_or_c}? (@{self.id})")
        # We can't use instrument `binary_values` since we need to set
        # break_on_termchar=True.
        raw_bytes = self.read_bytes(-1, break_on_termchar=True)
        assert chr(raw_bytes[0]) == "#"
        size_nbytes = int(chr(raw_bytes[1]))  # size of the size integer
        nbytes = int(raw_bytes[2 : 2 + size_nbytes].decode())
        self.write(f":form {old_format}")
        # breakpoint()
        raw_bytes = raw_bytes[2 + size_nbytes : -1]  # remove headers + newline byte
        values = np.frombuffer(
            raw_bytes,
            dtype=np.dtype(">d"),
        ).astype(np.float64)
        assert values.size == nbytes // 8
        return values

    trigger_source = Channel.setting(
        ":trig{ch}:sour %s",
        """Set the trigger source. Currently supported options are "TIM" (internal timer) and "AINT" (auto). Note that this is not readable.

        If switching from an active triggering sequence (i.e. auto (AINT) & trigger count set to infinite), you'll need to call the abort() method first to avoid an error.
        """,
        validator=strict_discrete_set,
        values=["TIM", "AINT"],  # "AUTO", "BUS", "INT1" "INT2", "LAN"
    )

    source_trigger_delay = Channel.control(
        ":trig{ch}:tran:del?",
        ":trig{ch}:tran:del %g",
        """Sets the source delay time.
        """,
    )

    measurement_trigger_delay = Channel.control(
        ":trig{ch}:acq:del?",
        ":trig{ch}:acq:del %g",
        """Sets the measurement delay time.
        """,
    )

    source_trigger_timer_period = Channel.setting(
        ":trig{ch}:tran:tim %s",
        """Set the trigger period. `trigger_source` needs to be set to "TIM".
        Note that this is not readable.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[1e-5, 1e5], ["MIN", "MAX", "DEF"]],
        set_process=lambda v: v if isinstance(v, str) else f"{v:g}",
    )

    measurement_trigger_timer_period = Channel.setting(
        ":trig{ch}:acq:tim %s",
        """Set the trigger period of the measurement trigger. `trigger_source`
        needs to be set to "TIM". Note that this is not readable.""",
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[1e-5, 1e5], ["MIN", "MAX", "DEF"]],
        set_process=lambda v: v if isinstance(v, str) else f"{v:g}",
    )

    source_trigger_count = Channel.setting(
        ":trig{ch}:tran:coun %g",
        """Set the trigger count of the source trigger (from 1 to 100000 or 2147483647). Note that this is not readable. Set to 2147483647 for infinite. 
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[1, 100000], 2147483647],
    )

    measurement_trigger_count = Channel.setting(
        ":trig{ch}:acq:coun %g",
        """Set the trigger count of the measurement trigger. Note that this is not readable.
        """,
        validator=joined_validators(strict_range, strict_discrete_set),
        values=[[1, 100000], 2147483647],
    )

    def initiate(self):
        """This is the B2900A manual's terminology for triggering."""
        self.write(":INIT (@{ch})")

    idle = Channel.measurement(
        ":idle{ch}:all?",
        """Check whether the triggering system is idle (i.e. all source & measurements are complete)""",
        cast=bool,
    )

    def wait_idle(self, timeout=1):
        """Block until all device actions (source and measurements) are complete.

        Parameters
        ----------
        timeout : float
            Timeout in seconds (default 1).

        Raises
        ------
        ValueError
            If the timeout is reached before the channel becomes idle.
        """
        end = datetime.now() + timedelta(seconds=timeout)
        err = ValueError("timeout waiting for idle")
        while True:
            try:
                if self.idle:
                    return
                if datetime.now() >= end:
                    raise err
            except VisaIOError as e:
                err = e
                if datetime.now() >= end:
                    raise err

    def abort(self):
        """Abort any acquisition our source output device actions."""
        self.write(":ABOR:ALL (@{ch})")


class KeysightB2900A(SCPIMixin, Instrument):
    """Represents the Keysight B2900A Precision Source/Measure Unit.

    .. code-block:: python

        psmu = KeysightB2900A(resource)
    """

    ch1 = Instrument.ChannelCreator(KeysightB2900AChannel, 1)
    ch2 = Instrument.ChannelCreator(KeysightB2900AChannel, 2)

    def __init__(self, adapter, name="Keysight B2900A PSMU", **kwargs):
        super().__init__(adapter, name, **kwargs)

    def wait_for_complete(self, timeout=1):
        """Like the `SCPIMixin.complete` property, but tries until the
        `timeout` (in seconds) has passed. Note that this does not
        block until the trigger IDLE state (i.e. it does not wait for
        measurements to be complete)

        """
        end = datetime.now() + timedelta(seconds=timeout)
        err = ValueError("timeout is too short.")
        need_to_clear = False
        while True:
            try:
                retval = self.complete
                if need_to_clear:
                    self.clear()
                if int(retval) == 1:
                    return retval
                # Not complete yet, check timeout before next poll
                if datetime.now() >= end:
                    raise err
            except VisaIOError as e:
                # an error in the isntr is generated if the communication times
                # out. the need_to_clear flag keeps tracks of this and clears
                # it. TODO should we call check_error instead to ensure there
                # are no other errors?
                need_to_clear = True
                err = e
                if datetime.now() >= end:
                    print(f"DEBUG: VisaIOError timeout, {poll_count=}, {retval=}")
                    raise err

    def pop_err(self):
        """Pop an error off the device's error queue. Returns a tuple
        containing the code and error description. An error code 0
        indicates success.

        The Error queue can be cleared using the standard SCPI
        ``KeysightB2900A.clear()`` method.

        """
        error_str = self.ask("SYST:ERR?").strip()
        error_code_str, error_desc_str = error_str.split(",")
        error_code = int(error_code_str)
        error_desc = error_desc_str.strip('"')
        return error_code, error_desc
