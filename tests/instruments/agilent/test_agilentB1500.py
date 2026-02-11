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

import pytest

from pymeasure.instruments.agilent import AgilentB1500
from pymeasure.instruments.agilent.agilentB1500 import (
    SPGU,
    ControlMode,
    PgSelectorConnectionStatus,
    PgSelectorPort,
    SPGUChannelOutputMode,
    SPGUOperationMode,
    SPGUOutputMode,
)
from pymeasure.test import expected_protocol


class TestB1500:
    """Tests for B1500 functionality."""

    def test_restore_settings(self):
        """Test restore_settings method."""
        with expected_protocol(
            AgilentB1500,
            [("RZ", None)],
        ) as inst:
            inst.restore_settings()

    @pytest.mark.parametrize("io_control_mode", list(ControlMode))
    def test_io_control_mode(self, io_control_mode):
        """Test io_control_mode property."""
        with expected_protocol(
            AgilentB1500,
            [(f"ERMOD {io_control_mode.value}", None), ("ERMOD?", io_control_mode.value)],
        ) as inst:
            inst.io_control_mode = io_control_mode
            assert inst.io_control_mode == io_control_mode

    @pytest.mark.parametrize("port", list(PgSelectorPort))
    @pytest.mark.parametrize("status", list(PgSelectorConnectionStatus))
    def test_set_port_connection(self, port, status):
        """Test set_port_connection method."""
        with expected_protocol(
            AgilentB1500,
            [(f"ERSSP {port.value}, {status.value}", None)],
        ) as inst:
            inst.set_port_connection(port, status)


class AgilentB1500Mock(AgilentB1500):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spgu1 = SPGU(self, 1)


class TestSPGU:
    """Tests for SPGU module functionality."""

    @pytest.mark.parametrize("output", [True, False])
    def test_output(self, output):
        """Test output property."""
        expected_command = "SRP" if output else "SPP"
        with expected_protocol(
            AgilentB1500Mock,
            [(expected_command, None)],
        ) as inst:
            inst.spgu1.output = output

    @pytest.mark.parametrize("operation_mode", list(SPGUOperationMode))
    def test_operation_mode(self, operation_mode):
        """Test operation_mode property."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"SIM {operation_mode.value}", None), ("SIM?", operation_mode.value)],
        ) as inst:
            inst.spgu1.operation_mode = operation_mode
            assert inst.spgu1.operation_mode == operation_mode

    def test_period(self):
        """Test period property."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"SPPER {0.5:.6f}", None), ("SPPER?", 0.5)],
        ) as inst:
            inst.spgu1.period = 0.5
            assert inst.spgu1.period == 0.5

    @pytest.mark.parametrize(
        "output_mode, condition", [(mode, 1) for mode in list(SPGUOutputMode)[1:]]
    )
    def test_output_mode(self, output_mode, condition):
        """Test set_output_mode and get_output_mode methods."""
        print(output_mode, condition)
        with expected_protocol(
            AgilentB1500Mock,
            [
                (f"SPRM {output_mode.value}, {condition}", None),
                ("SPRM?", f"{output_mode.value}, {condition}"),
            ],
        ) as inst:
            inst.spgu1.set_output_mode(output_mode, condition)
            assert inst.spgu1.get_output_mode() == (output_mode, condition)

    def test_complete(self):
        """Test complete property."""
        with expected_protocol(
            AgilentB1500Mock,
            [("SPST?", "0"), ("SPST?", "1")],
        ) as inst:
            assert inst.spgu1.complete
            assert not inst.spgu1.complete


class TestSPGUChannel:
    """Tests for SPGU channel functionality."""

    channel = 101

    @pytest.mark.parametrize("enabled", [True, False])
    def test_enabled(self, enabled):
        """Test enabled property."""
        expected_command = "CN" if enabled else "CL"
        with expected_protocol(
            AgilentB1500Mock,
            [(f"{expected_command} {self.channel}", None)],
        ) as inst:
            inst.spgu1.ch1.enabled = enabled

    def test_load_impedance(self):
        """Test load_impedance property."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"SER {self.channel}, {100:.6f}", None), (f"SER? {self.channel}", 100)],
        ) as inst:
            inst.spgu1.ch1.load_impedance = 100
            assert inst.spgu1.ch1.load_impedance == 100

    def test_output_voltage(self):
        """Test set_output_voltage and get_output_voltage methods."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                (f"SPV {self.channel}, 1, 0.5, 2.0", None),
                (f"SPV? {self.channel}, 1", "0.5, 2.0"),
            ],
        ) as inst:
            inst.spgu1.ch1.set_output_voltage(source=1, base_voltage=0.5, peak_voltage=2.0)
            assert inst.spgu1.ch1.get_output_voltage(source=1) == (0.5, 2.0)

    @pytest.mark.parametrize("output_mode", list(SPGUChannelOutputMode))
    def test_output_mode(self, output_mode):
        """Test output_mode property."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                (f"SPM {self.channel}, {output_mode.value}", None),
                (f"SPM? {self.channel}", str(output_mode.value)),
            ],
        ) as inst:
            inst.spgu1.ch1.output_mode = output_mode
            assert inst.spgu1.ch1.output_mode == output_mode

    def test_pulse_timings(self):
        """Test set_pulse_timings and get_pulse_timings methods."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                (f"SPT {self.channel}, 1, 0.0, 1e-07, 2e-08, 3e-08", None),
                (f"SPT? {self.channel}, 1", "0.0,1e-07,2e-08,3e-08"),
            ],
        ) as inst:
            inst.spgu1.ch1.set_pulse_timings(
                source=1, delay=0.0, width=1e-7, rise_time=2e-8, fall_time=3e-8
            )
            delay, width, rise_time, fall_time = inst.spgu1.ch1.get_pulse_timings(source=1)
            assert delay == 0.0
            assert width == 1e-7
            assert rise_time == 2e-8
            assert fall_time == 3e-08

    def test_apply_setup(self):
        """Test apply_setup method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"SPUPD {self.channel}", None)],
        ) as inst:
            inst.spgu1.ch1.apply_setup()
