import struct

import numpy as np
import pytest

from pymeasure.instruments.exfo.ctp10 import CTP10, TraceChannel
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        CTP10,
        [],
    ):
        pass  # Verify the expected communication.


# TLS Channel Tests --------------------------------------------------------


def test_tls1_start_wavelength_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:WAVelength:STARt 1550NM", None)],
    ) as inst:
        inst.tls1.start_wavelength_nm = 1550.0


def test_tls1_start_wavelength_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:WAVelength:STARt?", b"1.55000000E-006\r\n")],
    ) as inst:
        assert inst.tls1.start_wavelength_nm == pytest.approx(1550.0)


def test_tls1_stop_wavelength_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:WAVelength:STOP 1580NM", None)],
    ) as inst:
        inst.tls1.stop_wavelength_nm = 1580.0


def test_tls1_stop_wavelength_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:WAVelength:STOP?", b"1.58000000E-006\r\n")],
    ) as inst:
        assert inst.tls1.stop_wavelength_nm == pytest.approx(1580.0)


def test_tls1_sweep_speed_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:SPEed 50", None)],
    ) as inst:
        inst.tls1.sweep_speed_nmps = 50


def test_tls1_sweep_speed_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:SPEed?", b"50\r\n")],
    ) as inst:
        assert inst.tls1.sweep_speed_nmps == 50


def test_tls1_laser_power_dbm_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:POWer 5DBM", None)],
    ) as inst:
        inst.tls1.laser_power_dbm = 5.0


def test_tls1_laser_power_dbm_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS1:POWer?", b"5.00000000E+000\r\n")],
    ) as inst:
        assert inst.tls1.laser_power_dbm == pytest.approx(5.0)


def test_tls2_start_wavelength_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:TLS2:WAVelength:STARt?", b"1.52000000E-006\r\n")],
    ) as inst:
        assert inst.tls2.start_wavelength_nm == pytest.approx(1520.0)


# Global Settings Tests ----------------------------------------------------


def test_resolution_pm_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAVelength:SAMPling 10PM", None)],
    ) as inst:
        inst.resolution_pm = 10


def test_resolution_pm_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:WAVelength:SAMPling?", b"1.00000000E-011\r\n")],
    ) as inst:
        assert inst.resolution_pm == pytest.approx(10.0)


def test_stabilization_setter():
    with expected_protocol(
        CTP10,
        [(b":INIT:STABilization 1,12.3", None)],
    ) as inst:
        inst.stabilization = (1, 12.3)


def test_stabilization_getter():
    with expected_protocol(
        CTP10,
        [(b":INIT:STABilization?", b"1,5.6\r\n")],
    ) as inst:
        assert inst.stabilization == [pytest.approx(1.0), pytest.approx(5.6)]


def test_condition_register():
    with expected_protocol(
        CTP10,
        [(b":STATus:OPERation:CONDition?", b"0\r\n")],
    ) as inst:
        assert inst.condition_register == 0


def test_sweep_complete_true():
    with expected_protocol(
        CTP10,
        [(b":STATus:OPERation:CONDition?", b"0\r\n")],
    ) as inst:
        assert inst.sweep_complete is True


def test_sweep_complete_false():
    with expected_protocol(
        CTP10,
        [(b":STATus:OPERation:CONDition?", b"4\r\n")],
    ) as inst:
        assert inst.sweep_complete is False


# Sweep Control Tests ------------------------------------------------------


def test_initiate_sweep():
    with expected_protocol(
        CTP10,
        [(b":INITiate:IMMediate", None)],
    ) as inst:
        inst.initiate_sweep()


# Trace Channel Tests ------------------------------------------------------


def test_trace_length():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:LENGth?", b"6001\r\n")],
    ) as inst:
        assert inst.tf_live[4, 1].length == 6001


def test_trace_sampling_pm():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:SAMPling?",
          b"1.00000000E-011\r\n")],
    ) as inst:
        assert inst.tf_live[4, 1].sampling_pm == pytest.approx(10.0)


def test_trace_start_wavelength_nm():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:STARt?",
          b"1.55000000E-006\r\n")],
    ) as inst:
        assert inst.tf_live[4, 1].start_wavelength_nm == pytest.approx(1550.0)


def test_trace_get_data_x():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:X[:IMMediate]?",
          b"1.55E-6,1.56E-6\r\n")],
    ) as inst:
        data = inst.tf_live[4, 1].get_data_x()
        assert data == [pytest.approx(1.55e-6), pytest.approx(1.56e-6)]


def test_trace_get_data_y_ascii():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA? ASCII,DB",
          b"-5.25,-6.32\r\n")],
    ) as inst:
        data = inst.tf_live[4, 1].get_data_y(unit='DB', format='ASCII')
        assert data == [pytest.approx(-5.25), pytest.approx(-6.32)]


def test_trace_get_data_y_raw_live():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE11:DATA? ASCII,DB",
          b"-5.25,-6.32\r\n")],
    ) as inst:
        data = inst.raw_live[4, 1].get_data_y(unit='DB', format='ASCII')
        assert data == [pytest.approx(-5.25), pytest.approx(-6.32)]


def test_trace_get_data_y_raw_reference():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE12:DATA? ASCII,DB",
          b"-5.25,-6.32\r\n")],
    ) as inst:
        data = inst.raw_reference[4, 1].get_data_y(unit='DB', format='ASCII')
        assert data == [pytest.approx(-5.25), pytest.approx(-6.32)]


def test_trace_save():
    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:SAVE", None)],
    ) as inst:
        inst.tf_live[4, 1].save()


def test_trace_create_reference():
    with expected_protocol(
        CTP10,
        [(b":REFerence:SENSe4:CHANnel1:INITiate", None)],
    ) as inst:
        inst.tf_live[4, 1].create_reference()


def test_trace_get_power():
    """Test power measurement (returns value in dBm)."""
    with expected_protocol(
        CTP10,
        [(b":CTP:SENSe4:CHANnel1:POWer?", b"-5.25\r\n")],
    ) as inst:
        assert inst.tf_live[4, 1].power == pytest.approx(-5.25)


def test_trace_power_simple():
    """Test power measurement with simple format (no comma)."""
    with expected_protocol(
        CTP10,
        [(b":CTP:SENSe4:CHANnel1:POWer?", b"-3.14\r\n")],
    ) as inst:
        assert inst.tf_live[4, 1].power == pytest.approx(-3.14)


def test_trace_wavelength_array():
    with expected_protocol(
        CTP10,
        [
            (b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:STARt?",
             b"1.55000000E-006\r\n"),
            (b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:SAMPling?",
             b"1.00000000E-011\r\n"),
            (b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:LENGth?", b"3\r\n"),
        ],
    ) as inst:
        wavelengths = inst.tf_live[4, 1].get_wavelength_array()
        expected = np.array([1550.0, 1550.01, 1550.02])
        np.testing.assert_array_almost_equal(wavelengths, expected, decimal=5)


# Test multiple trace channels ---------------------------------------------


def test_trace_multiple_channels():
    with expected_protocol(
        CTP10,
        [
            (b":TRACe:SENSe4:CHANnel1:TYPE1:DATA:LENGth?", b"6001\r\n"),
            (b":TRACe:SENSe4:CHANnel2:TYPE1:DATA:LENGth?", b"6002\r\n"),
            (b":TRACe:SENSe5:CHANnel1:TYPE1:DATA:LENGth?", b"6003\r\n"),
        ],
    ) as inst:
        assert inst.tf_live[4, 1].length == 6001
        assert inst.tf_live[4, 2].length == 6002
        assert inst.tf_live[5, 1].length == 6003


# SCPI Tests ---------------------------------------------------------------


def test_id():
    with expected_protocol(
        CTP10,
        [(b"*IDN?", b"EXFO,CTP10,12345,1.0.0\r\n")],
    ) as inst:
        assert inst.id == "EXFO,CTP10,12345,1.0.0"


def test_clear():
    with expected_protocol(CTP10, [(b"*CLS", None)]) as inst:
        inst.clear()


def test_reset():
    with expected_protocol(
        CTP10,
        [(b"*RST", None)],
    ) as inst:
        inst.reset()


# Error Handling and Edge Cases ----------------------------------------


def test_trace_channel_invalid_id():
    """Test that TraceChannel raises ValueError for invalid ID."""
    with expected_protocol(CTP10, []) as inst:
        with pytest.raises(ValueError,
                           match="TraceChannel ID must be a tuple"):
            # Try to create TraceChannel with non-tuple ID
            TraceChannel(inst, id=4)


def test_trace_channel_none_id():
    """Test that TraceChannel can be created with id=None."""
    with expected_protocol(CTP10, []) as inst:
        # Create TraceChannel with id=None (edge case for coverage)
        channel = TraceChannel(inst, id=None, trace_type=1)
        assert channel.module is None
        assert channel.channel is None
        assert channel.trace_type == 1


def test_trace_channel_insert_id_with_none():
    """Test insert_id returns command unchanged when id is None."""
    with expected_protocol(CTP10, []) as inst:
        channel = TraceChannel(inst, id=None, trace_type=1)
        # insert_id should return command unchanged when id is None
        cmd = ":TRACe:SENSe{ch}:TYPE{type}:DATA:LENGth?"
        result = channel.insert_id(cmd)
        assert result == cmd


def test_trace_get_data_y_binary():
    """Test binary trace data reading."""
    # Create a simple binary block: #27 means 2 digits for length,
    # length is 7 bytes (1 float32 + 3 bytes padding for test)
    # One float32 (4 bytes) with value -5.25 in big-endian
    float_value = -5.25
    binary_data = struct.pack('>f', float_value)
    # IEEE 488.2 format: #<length_of_length><length><data>
    length_str = str(len(binary_data))
    header = f"#{len(length_str)}{length_str}".encode()
    response = header + binary_data

    with expected_protocol(
        CTP10,
        [(b":TRACe:SENSe4:CHANnel1:TYPE1:DATA? BIN,DB", response)],
    ) as inst:
        data = inst.tf_live[4, 1].get_data_y(unit='DB', format='BIN')
        assert isinstance(data, np.ndarray)
        assert len(data) == 1
        assert data[0] == pytest.approx(float_value)


def test_wait_for_sweep_complete_success():
    """Test wait_for_sweep_complete returns True when sweep completes."""
    with expected_protocol(
        CTP10,
        [
            (b":STATus:OPERation:CONDition?", b"4\r\n"),  # Scanning
            (b":STATus:OPERation:CONDition?", b"0\r\n"),  # Complete
        ],
    ) as inst:
        result = inst.wait_for_sweep_complete()
        assert result is True


def test_wait_for_sweep_complete_should_stop():
    """Test wait_for_sweep_complete returns False when should_stop."""
    call_count = [0]

    def should_stop():
        call_count[0] += 1
        return call_count[0] > 1  # Stop after second call

    with expected_protocol(
        CTP10,
        [
            (b":STATus:OPERation:CONDition?", b"4\r\n"),  # Scanning
            (b":STATus:OPERation:CONDition?", b"4\r\n"),  # Still scanning
        ],
    ) as inst:
        result = inst.wait_for_sweep_complete(should_stop=should_stop)
        assert result is False


def test_check_errors():
    """Test check_errors method calls parent implementation."""
    with expected_protocol(
        CTP10,
        [(b"SYST:ERR?", b"0,No error\r\n")],
    ) as inst:
        inst.check_errors()  # Should not raise
