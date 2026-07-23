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
    CMU,
    SMU,
    SPGU,
    ControlMode,
    MFCMUMeasurementMode,
    PgSelectorConnectionStatus,
    PgSelectorPort,
    SCUUPath,
    SPGUChannelOutputMode,
    SPGUOperationMode,
    SPGUOutputMode,
    SpotCMU,
    SpotCMUMonitor,
    SpotIV,
    SweepMode,
    TimedSpotCMU,
    TimedSpotCMUMonitor,
    TimedSpotCurrent,
    TimedSpotIV,
    TimedSpotVoltage,
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
        self.cmu = CMU(self, 2)
        self.smu1 = SMU(self, index=1, smu_type="HRSMU", name="test", slot=1)


class TestSMU:
    """Tests for SMU module functionality."""

    channel = 1

    def test_enable(self):
        """Test enable method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"CN {self.channel}", None)],
        ) as inst:
            inst.smu1.enable()

    def test_disable(self):
        """Test disable method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"CL {self.channel}", None)],
        ) as inst:
            inst.smu1.disable()

    def test_measure_current(self):
        """Test measure_current method."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                ("FMT 1, 0", None),
                ("ERRX?", '+0,"No Error."'),
                (f"TI {self.channel}", "NAI+000.005E-09"),
                (f"TTI {self.channel}, 11", "NAT+000.123E+00,NAI+000.005E-09"),
            ],
        ) as inst:
            inst.data_format(1)
            assert inst.smu1.measure_current() == 5e-12
            result = inst.smu1.measure_current("1 nA", timestamp=True)
            assert isinstance(result, TimedSpotCurrent)
            assert result == (0.123, 5e-12)
            assert result.time == 0.123
            assert result.current == 5e-12

    def test_measure_voltage(self):
        """Test measure_voltage method."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                ("FMT 1, 0", None),
                ("ERRX?", '+0,"No Error."'),
                (f"TV {self.channel}", "NAV+001.500E+00"),
                (f"TTV {self.channel}, 20", "NAT+000.123E+00,NAV+001.500E+00"),
            ],
        ) as inst:
            inst.data_format(1)
            assert inst.smu1.measure_voltage() == 1.5
            result = inst.smu1.measure_voltage("2 V", timestamp=True)
            assert isinstance(result, TimedSpotVoltage)
            assert result == (0.123, 1.5)
            assert result.voltage == 1.5

    def test_measure_iv(self):
        """Test measure_iv method."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                ("FMT 1, 0", None),
                ("ERRX?", '+0,"No Error."'),
                (f"TIV {self.channel}", "NAI+000.005E-09,NAV+001.000E+00"),
                (
                    f"TTIV {self.channel}, 11, 0",
                    "NAT+000.123E+00,NAI+000.005E-09,NAV+001.000E+00",
                ),
            ],
        ) as inst:
            inst.data_format(1)
            result = inst.smu1.measure_iv()
            assert isinstance(result, SpotIV)
            assert result == (5e-12, 1.0)
            assert result.current == 5e-12
            assert result.voltage == 1.0
            timed_result = inst.smu1.measure_iv("1 nA", 0, timestamp=True)
            assert isinstance(timed_result, TimedSpotIV)
            assert timed_result == (0.123, 5e-12, 1.0)
            assert timed_result.time == 0.123

    def test_measure_iv_requires_both_ranges(self):
        """Test that measure_iv rejects current_range without voltage_range and vice versa."""
        with expected_protocol(AgilentB1500Mock, []) as inst:
            with pytest.raises(ValueError):
                inst.smu1.measure_iv(current_range="1 nA")
            with pytest.raises(ValueError):
                inst.smu1.measure_iv(voltage_range="2 V")


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


class TestCMU:
    """Tests for CMU module functionality."""

    @pytest.mark.parametrize("enabled", [True, False])
    def test_enabled(self, enabled):
        """Test enabled property."""
        expected_command = "CN" if enabled else "CL"
        with expected_protocol(
            AgilentB1500Mock,
            [(f"{expected_command} 2", None)],
        ) as inst:
            inst.cmu.enabled = enabled

    @pytest.mark.parametrize("voltage", [0.0, 0.25])
    def test_voltage_ac(self, voltage):
        """Test voltage_ac setting with boundary values."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"ACV 2, {voltage:f}", None)],
        ) as inst:
            inst.cmu.voltage_ac = voltage

    @pytest.mark.parametrize("frequency", [1e3, 5e6])
    def test_frequency_ac(self, frequency):
        """Test frequency_ac setting with boundary values."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"FC 2, {frequency:f}", None)],
        ) as inst:
            inst.cmu.frequency_ac = frequency

    @pytest.mark.parametrize("measurement_mode", list(MFCMUMeasurementMode))
    def test_set_measurement_mode(self, measurement_mode):
        """Test set_measurement_mode method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"IMP {measurement_mode.value}", None)],
        ) as inst:
            inst.cmu.set_measurement_mode(measurement_mode)

    @pytest.mark.parametrize("enabled", [True, False])
    def test_voltage_monitor_enabled(self, enabled):
        """Test voltage_monitor_enabled property."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                (f"LMN {int(enabled)}", None),
                ("*LRN? 71", f"LMN{int(enabled)}"),
            ],
        ) as inst:
            inst.cmu.voltage_monitor_enabled = enabled
            assert inst.cmu.voltage_monitor_enabled == enabled

    def test_measure(self):
        """Test measure method."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                ("FMT 1, 0", None),
                ("ERRX?", '+0,"No Error."'),
                ("TC 2, 0", "NBC+001.000E-12,NBY+002.000E-06"),
                ("TTC 2, 2, 1000", "NBT+000.123E+00,NBC+001.000E-12,NBY+002.000E-06"),
            ],
        ) as inst:
            inst.data_format(1)
            result = inst.cmu.measure()
            assert isinstance(result, SpotCMU)
            assert result == (1e-12, 2e-6)
            primary, secondary = result
            assert (primary, secondary) == (1e-12, 2e-6)
            timed_result = inst.cmu.measure(meas_range=1000, timestamp=True)
            assert isinstance(timed_result, TimedSpotCMU)
            assert timed_result == (0.123, 1e-12, 2e-6)
            assert timed_result.time == 0.123

    def test_measure_with_monitor(self):
        """Test that measure captures AC/DC voltage values (:attr:`voltage_monitor_enabled`)."""
        with expected_protocol(
            AgilentB1500Mock,
            [
                ("FMT 1, 0", None),
                ("ERRX?", '+0,"No Error."'),
                ("TC 2, 0", "NBC+001.000E-12,NBY+002.000E-06,NBV+000.030E+00,NBV+001.000E+00"),
                (
                    "TTC 2, 0",
                    "NBT+000.123E+00,NBC+001.000E-12,NBY+002.000E-06,"
                    "NBV+000.030E+00,NBV+001.000E+00",
                ),
            ],
        ) as inst:
            inst.data_format(1)
            result = inst.cmu.measure()
            assert isinstance(result, SpotCMUMonitor)
            assert result == (1e-12, 2e-6, 0.03, 1.0)
            primary, secondary, ac_voltage, dc_voltage = result
            assert (primary, secondary, ac_voltage, dc_voltage) == (1e-12, 2e-6, 0.03, 1.0)
            assert result.ac_voltage == 0.03
            assert result.dc_voltage == 1.0
            timed_result = inst.cmu.measure(timestamp=True)
            assert isinstance(timed_result, TimedSpotCMUMonitor)
            assert timed_result == (0.123, 1e-12, 2e-6, 0.03, 1.0)

    def test_measure_invalid_range(self):
        """Test that measure rejects a range not in MEASUREMENT_RANGES."""
        with expected_protocol(AgilentB1500Mock, []) as inst:
            with pytest.raises(ValueError):
                inst.cmu.measure(meas_range=500)

    def test_set_cv_timings(self):
        """Test set_cv_timings method."""
        with expected_protocol(
            AgilentB1500Mock,
            [("WTDCV 2, 0.5, 0.1, 0.0, 0.0", None)],
        ) as inst:
            inst.cmu.set_cv_timings(hold_time=0.5, delay_time=0.1)

    def test_set_cv_timings_all_params(self):
        """Test set_cv_timings with all parameters."""
        with expected_protocol(
            AgilentB1500Mock,
            [("WTDCV 2, 1.0, 0.5, 0.2, 0.1", None)],
        ) as inst:
            inst.cmu.set_cv_timings(
                hold_time=1.0,
                delay_time=0.5,
                step_delay_time=0.2,
                step_source_trigger_delay_time=0.1,
            )

    @pytest.mark.parametrize("mode", [SweepMode.LINEAR_SINGLE, SweepMode.LINEAR_DOUBLE])
    def test_set_cv_parameters(self, mode):
        """Test set_cv_parameters method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"WDCV 2, {mode.value}, -5, 5, 100", None)],
        ) as inst:
            inst.cmu.set_cv_parameters(mode=mode, start=-5, stop=5, steps=100)

    def test_force_dc_bias(self):
        """Test force_dc_bias method."""
        with expected_protocol(
            AgilentB1500Mock,
            [("DCV 2, 1.5", None)],
        ) as inst:
            inst.cmu.force_dc_bias(1.5)

    @pytest.mark.parametrize("path", list(SCUUPath))
    def test_set_scuu_path(self, path):
        """Test set_scuu_path method."""
        with expected_protocol(
            AgilentB1500Mock,
            [(f"SSP 2, {path.value}", None)],
        ) as inst:
            inst.cmu.set_scuu_path(path)
