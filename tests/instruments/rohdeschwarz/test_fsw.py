from pymeasure.instruments.rohdeschwarz.fsseries import FSW
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        FSW,
        [],
    ):
        pass  # Verify the expected communication.


def test_freq_center_getter():
    with expected_protocol(
        FSW,
        [(b"FREQ:CENT?", b"750000000\n")],
    ) as inst:
        assert inst.freq_center == 750000000.0


def test_freq_span_getter():
    with expected_protocol(
        FSW,
        [(b"FREQ:SPAN?", b"300000000\n")],
    ) as inst:
        assert inst.freq_span == 300000000.0


def test_freq_start_setter():
    with expected_protocol(
        FSW,
        [(b"FREQ:STAR 600000000.0", None)],
    ) as inst:
        inst.freq_start = 600000000.0


def test_freq_stop_setter():
    with expected_protocol(
        FSW,
        [(b"FREQ:STOP 900000000.0", None)],
    ) as inst:
        inst.freq_stop = 900000000.0


def test_res_bandwidth_setter():
    with expected_protocol(
        FSW,
        [(b"BAND:RES 10kHz", None)],
    ) as inst:
        inst.res_bandwidth = "10kHz"


def test_res_bandwidth_getter():
    with expected_protocol(
        FSW,
        [(b"BAND:RES?", b"10000\n")],
    ) as inst:
        assert inst.res_bandwidth == 10000.0


def test_sweep_time_setter():
    with expected_protocol(
        FSW,
        [(b"SWE:TIME 2", None)],
    ) as inst:
        inst.sweep_time = 2


def test_sweep_time_getter():
    with expected_protocol(
        FSW,
        [(b"SWE:TIME?", b"2\n")],
    ) as inst:
        assert inst.sweep_time == 2.0


def test_video_bandwidth_setter():
    with expected_protocol(
        FSW,
        [(b"BAND:VID 10kHz", None)],
    ) as inst:
        inst.video_bandwidth = "10kHz"


def test_video_bandwidth_getter():
    with expected_protocol(
        FSW,
        [(b"BAND:VID?", b"10000\n")],
    ) as inst:
        assert inst.video_bandwidth == 10000.0


def test_reset():
    with expected_protocol(
        FSW,
        [(b"*RST", None)],
    ) as inst:
        assert inst.reset() is None


def test_auto_all():
    with expected_protocol(
        FSW,
        [(b":ADJ:ALL", None)],
    ) as inst:
        assert inst.auto_all() is None


def test_auto_freq():
    with expected_protocol(
        FSW,
        [(b":ADJ:FREQ", None)],
    ) as inst:
        assert inst.auto_freq() is None


def test_auto_level():
    with expected_protocol(
        FSW,
        [(b":ADJ:LEV", None)],
    ) as inst:
        assert inst.auto_level() is None


def test_create_channel():
    with expected_protocol(
        FSW,
        [
            (b"INST:CRE:NEW PNOISE, 'Phase Noise'", None),
            (b"INST:LIST?", b"PNOISE,'Phase Noise',SANALYZER,'Spectrum 1'\n"),
        ],
    ) as inst:
        inst.create_channel("PNOISE", "Phase Noise")

        assert inst.available_channels == {"Phase Noise": "PNOISE", "Spectrum 1": "SANALYZER"}
