import datetime

import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.redpitaya import RedPitayaScpi


def test_init():
    with expected_protocol(
            RedPitayaScpi,
            [],
    ):
        pass  # Verify the expected communication.


def test_CLOCK_getter():
    with expected_protocol(
            RedPitayaScpi,
            [],
    ) as inst:
        assert inst.CLOCK == 125000000.0


def test_TRIGGER_SOURCES_getter():
    with expected_protocol(
            RedPitayaScpi,
            [],
    ) as inst:
        assert inst.TRIGGER_SOURCES == ('DISABLED', 'NOW', 'CH1_PE', 'CH1_NE', 'CH2_PE', 'CH2_NE',
                                        'EXT_PE', 'EXT_NE', 'AWG_PE', 'AWG_NE')


def test_acq_buffer_filled_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:TRig:FILL?', b'0')],
    ) as inst:
        assert inst.acq_buffer_filled is False


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:DATA:FORMAT ASCII', None)],
     'ASCII'),
    ([(b'ACQ:DATA:FORMAT BIN', None)],
     'BIN'),
    ([(b'ACQ:DATA:FORMAT BIN', None)],
     'BIN'),
    ([(b'ACQ:DATA:FORMAT ASCII', None)],
     'ASCII'),
))
def test_acq_format_setter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        inst.acq_format = value


def test_acq_size_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:BUF:SIZE?', b'16384')],
    ) as inst:
        assert inst.buffer_length == 16384


def test_acq_trigger_delay_ns_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:TRig:DLY -8182', None)],
    ) as inst:
        inst.acq_trigger_delay_ns = -65456


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:TRig:DLY?', b'0')],
     0),
    ([(b'ACQ:TRig:DLY?', b'500')],
     4000),
    ([(b'ACQ:TRig:DLY?', b'-8182')],
     -65456),
))
def test_acq_trigger_delay_ns_getter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        assert inst.acq_trigger_delay_ns == value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:TRig:DLY 0', None)],
     0),
    ([(b'ACQ:TRig:DLY 500', None)],
     500),
))
def test_acq_trigger_delay_samples_setter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        inst.acq_trigger_delay_samples = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:TRig:DLY?', b'0')],
     0),
    ([(b'ACQ:TRig:DLY?', b'500')],
     500),
    ([(b'ACQ:TRig:DLY?', b'-8182')],
     -8182),
))
def test_acq_trigger_delay_samples_getter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        assert inst.acq_trigger_delay_samples == value


def test_acq_trigger_level_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:TRig:LEV 0.500000', None)],
    ) as inst:
        inst.acq_trigger_level = 0.5


def test_acq_trigger_level_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:TRig:LEV?', b'0.5')],
    ) as inst:
        assert inst.acq_trigger_level == 0.5


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:TRig DISABLED', None)],
     'DISABLED'),
    ([(b'ACQ:TRig NOW', None)],
     'NOW'),
    ([(b'ACQ:TRig CH1_PE', None)],
     'CH1_PE'),
    ([(b'ACQ:TRig CH1_NE', None)],
     'CH1_NE'),
    ([(b'ACQ:TRig CH2_PE', None)],
     'CH2_PE'),
    ([(b'ACQ:TRig CH2_NE', None)],
     'CH2_NE'),
    ([(b'ACQ:TRig EXT_PE', None)],
     'EXT_PE'),
    ([(b'ACQ:TRig EXT_NE', None)],
     'EXT_NE'),
    ([(b'ACQ:TRig AWG_PE', None)],
     'AWG_PE'),
    ([(b'ACQ:TRig AWG_NE', None)],
     'AWG_NE'),
))
def test_acq_trigger_source_setter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        inst.acq_trigger_source = value


def test_acq_trigger_status_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:TRig:STAT?', b'TD')],
    ) as inst:
        assert inst.acq_trigger_status is True


def test_acq_units_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:DATA:Units RAW', None)],
    ) as inst:
        inst.acq_units = 'RAW'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:DATA:Units?', b'VOLTS')],
     'VOLTS'),
    ([(b'ACQ:DATA:Units?', b'RAW')],
     'RAW'),
))
def test_acq_units_getter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        assert inst.acq_units == value


def test_ain1_gain_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:SOUR1:GAIN LV', None)],
    ) as inst:
        inst.ain1.gain = 'LV'


def test_ain1_gain_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ACQ:SOUR1:GAIN?', b'LV')],
    ) as inst:
        assert inst.ain1.gain == 'LV'


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:AVG OFF', None)],
     False),
    ([(b'ACQ:AVG ON', None)],
     True),
))
def test_average_skipped_samples_setter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        inst.average_skipped_samples = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:AVG?', b'OFF')],
     False),
    ([(b'ACQ:AVG?', b'ON')],
     True),
))
def test_average_skipped_samples_getter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        assert inst.average_skipped_samples == value


def test_board_name_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'SYST:BRD:Name?', b'STEMlab 125-10')],
    ) as inst:
        assert inst.board_name == 'STEMlab 125-10'


def test_date_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'SYST:DATE 2023,12,22', None)],
    ) as inst:
        inst.date = datetime.date(2023, 12, 22)


def test_date_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'SYST:DATE?', b'2023,12,22')],
    ) as inst:
        assert inst.date == datetime.date(2023, 12, 22)


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:DEC 1', None)],
     1),
    ([(b'ACQ:DEC 2', None)],
     2),
    ([(b'ACQ:DEC 4', None)],
     4),
    ([(b'ACQ:DEC 8', None)],
     8),
    ([(b'ACQ:DEC 16', None)],
     16),
    ([(b'ACQ:DEC 32', None)],
     32),
    ([(b'ACQ:DEC 64', None)],
     64),
    ([(b'ACQ:DEC 128', None)],
     128),
    ([(b'ACQ:DEC 256', None)],
     256),
    ([(b'ACQ:DEC 512', None)],
     512),
    ([(b'ACQ:DEC 1024', None)],
     1024),
    ([(b'ACQ:DEC 2048', None)],
     2048),
    ([(b'ACQ:DEC 4096', None)],
     4096),
    ([(b'ACQ:DEC 8192', None)],
     8192),
    ([(b'ACQ:DEC 16384', None)],
     16384),
    ([(b'ACQ:DEC 32768', None)],
     32768),
    ([(b'ACQ:DEC 65536', None)],
     65536),
))
def test_decimation_setter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        inst.decimation = value


@pytest.mark.parametrize("comm_pairs, value", (
    ([(b'ACQ:DEC?', b'1')],
     1.0),
    ([(b'ACQ:DEC?', b'2')],
     2.0),
    ([(b'ACQ:DEC?', b'4')],
     4.0),
    ([(b'ACQ:DEC?', b'8')],
     8.0),
    ([(b'ACQ:DEC?', b'16')],
     16.0),
    ([(b'ACQ:DEC?', b'32')],
     32.0),
    ([(b'ACQ:DEC?', b'64')],
     64.0),
    ([(b'ACQ:DEC?', b'128')],
     128.0),
    ([(b'ACQ:DEC?', b'256')],
     256.0),
    ([(b'ACQ:DEC?', b'512')],
     512.0),
    ([(b'ACQ:DEC?', b'1024')],
     1024.0),
    ([(b'ACQ:DEC?', b'2048')],
     2048.0),
    ([(b'ACQ:DEC?', b'4096')],
     4096.0),
    ([(b'ACQ:DEC?', b'8192')],
     8192.0),
    ([(b'ACQ:DEC?', b'16384')],
     16384.0),
    ([(b'ACQ:DEC?', b'32768')],
     32768.0),
    ([(b'ACQ:DEC?', b'65536')],
     65536.0),
))
def test_decimation_getter(comm_pairs, value):
    with expected_protocol(
            RedPitayaScpi,
            comm_pairs,
    ) as inst:
        assert inst.decimation == value


def test_led_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'DIG:PIN? LED7', 1)],
    ) as inst:
        assert inst.led7.enabled


def test_time_setter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'SYST:TIME 13,07,20', None)],
    ) as inst:
        inst.time = datetime.time(13, 7, 20)


def test_time_getter():
    with expected_protocol(
            RedPitayaScpi,
            [(b'SYST:TIME?', '13,07,20')],
    ) as inst:
        assert inst.time == datetime.time(13, 7, 20)


def test_analog_reset():
    with expected_protocol(
            RedPitayaScpi,
            [(b'ANALOG:RST', None)],
    ) as inst:
        assert inst.analog_reset() is None


def test_digital_reset():
    with expected_protocol(
            RedPitayaScpi,
            [(b'DIG:RST', None)],
    ) as inst:
        assert inst.digital_reset() is None
