import pytest

from pymeasure.instruments.yokogawa.aq6370d import AQ6370D
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        AQ6370D,
        [],
    ):
        pass  # Verify the expected communication.


def test_automatic_sample_number_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:SWEep:POINts:AUTO 0", None)],
    ) as inst:
        inst.automatic_sample_number = False


def test_level_position_getter():
    with expected_protocol(
        AQ6370D,
        [(b":DISPlay:TRACe:Y1:RPOSition?", b"8\n")],
    ) as inst:
        assert inst.level_position == 8


def test_reference_level_setter():
    with expected_protocol(
        AQ6370D,
        [(b":DISPlay:TRACe:Y1:SCALe:RLEVel -10", None)],
    ) as inst:
        inst.reference_level = -10


def test_reference_level_getter():
    with expected_protocol(
        AQ6370D,
        [(b":DISPlay:TRACe:Y1:SCALe:RLEVel?", b"-1.00000000E+001\n")],
    ) as inst:
        assert inst.reference_level == -10.0


def test_resolution_bandwidth_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:BWIDth:RESolution 1e-09", None)],
    ) as inst:
        inst.resolution_bandwidth = 1e-09


def test_sample_number_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:SWEep:POINts 101", None)],
    ) as inst:
        inst.sample_number = 101


def test_sweep_mode_setter():
    with expected_protocol(
        AQ6370D,
        [(b":INITiate:SMODe 2", None)],
    ) as inst:
        inst.sweep_mode = "REPEAT"


def test_sweep_mode_getter():
    with expected_protocol(
        AQ6370D,
        [(b":INITiate:SMODe?", b"2\n")],
    ) as inst:
        assert inst.sweep_mode == "REPEAT"


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b":SENSe:SWEep:SPEed 0", None)], "1x"),
        ([(b":SENSe:SWEep:SPEed 1", None)], "2x"),
    ),
)
def test_sweep_speed_setter(comm_pairs, value):
    with expected_protocol(
        AQ6370D,
        comm_pairs,
    ) as inst:
        inst.sweep_speed = value


@pytest.mark.parametrize(
    "comm_pairs, value",
    (
        ([(b":SENSe:SWEep:SPEed?", b"0\n")], "1x"),
        ([(b":SENSe:SWEep:SPEed?", b"1\n")], "2x"),
    ),
)
def test_sweep_speed_getter(comm_pairs, value):
    with expected_protocol(
        AQ6370D,
        comm_pairs,
    ) as inst:
        assert inst.sweep_speed == value


def test_wavelength_center_getter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:CENTer?", b"+8.50000000E-007\n")],
    ) as inst:
        assert inst.wavelength_center == 8.5e-07


def test_wavelength_span_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:SPAN 1e-08", None)],
    ) as inst:
        inst.wavelength_span = 1e-08


def test_wavelength_span_getter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:SPAN?", b"+1.00000000E-007\n")],
    ) as inst:
        assert inst.wavelength_span == 1e-07


def test_wavelength_start_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:STARt 8e-07", None)],
    ) as inst:
        inst.wavelength_start = 8e-07


def test_wavelength_stop_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:STOP 9e-07", None)],
    ) as inst:
        inst.wavelength_stop = 9e-07


def test_get_xdata():
    with expected_protocol(
        AQ6370D,
        [
            (
                b":TRACe:X? TRA",
                b"+8.45000000E-007,+8.45100000E-007,+8.45200000E-007,+8.45300000E-007,+8.45400000E-007,+8.45500000E-007,+8.45600000E-007,+8.45700000E-007,+8.45800000E-007,+8.45900000E-007,+8.46000000E-007,+8.46100000E-007,+8.46200000E-007,+8.46300000E-007,+8.46400000E-007,+8.46500000E-007,+8.46600000E-007,+8.46700000E-007,+8.46800000E-007,+8.46900000E-007,+8.47000000E-007,+8.47100000E-007,+8.47200000E-007,+8.47300000E-007,+8.47400000E-007,+8.47500000E-007,+8.47600000E-007,+8.47700000E-007,+8.47800000E-007,+8.47900000E-007,+8.48000000E-007,+8.48100000E-007,+8.48200000E-007,+8.48300000E-007,+8.48400000E-007,+8.48500000E-007,+8.48600000E-007,+8.48700000E-007,+8.48800000E-007,+8.48900000E-007,+8.49000000E-007,+8.49100000E-007,+8.49200000E-007,+8.49300000E-007,+8.49400000E-007,+8.49500000E-007,+8.49600000E-007,+8.49700000E-007,+8.49800000E-007,+8.49900000E-007,+8.50000000E-007,+8.50100000E-007,+8.50200000E-007,+8.50300000E-007,+8.50400000E-007,+8.50500000E-007,+8.50600000E-007,+8.50700000E-007,+8.50800000E-007,+8.50900000E-007,+8.51000000E-007,+8.51100000E-007,+8.51200000E-007,+8.51300000E-007,+8.51400000E-007,+8.51500000E-007,+8.51600000E-007,+8.51700000E-007,+8.51800000E-007,+8.51900000E-007,+8.52000000E-007,+8.52100000E-007,+8.52200000E-007,+8.52300000E-007,+8.52400000E-007,+8.52500000E-007,+8.52600000E-007,+8.52700000E-007,+8.52800000E-007,+8.52900000E-007,+8.53000000E-007,+8.53100000E-007,+8.53200000E-007,+8.53300000E-007,+8.53400000E-007,+8.53500000E-007,+8.53600000E-007,+8.53700000E-007,+8.53800000E-007,+8.53900000E-007,+8.54000000E-007,+8.54100000E-007,+8.54200000E-007,+8.54300000E-007,+8.54400000E-007,+8.54500000E-007,+8.54600000E-007,+8.54700000E-007,+8.54800000E-007,+8.54900000E-007,+8.55000000E-007\n",  # noqa: E501
            )
        ],
    ) as inst:
        assert inst.get_xdata(
            *("TRA",),
        ) == [
            8.45e-07,
            8.451e-07,
            8.452e-07,
            8.453e-07,
            8.454e-07,
            8.455e-07,
            8.456e-07,
            8.457e-07,
            8.458e-07,
            8.459e-07,
            8.46e-07,
            8.461e-07,
            8.462e-07,
            8.463e-07,
            8.464e-07,
            8.465e-07,
            8.466e-07,
            8.467e-07,
            8.468e-07,
            8.469e-07,
            8.47e-07,
            8.471e-07,
            8.472e-07,
            8.473e-07,
            8.474e-07,
            8.475e-07,
            8.476e-07,
            8.477e-07,
            8.478e-07,
            8.479e-07,
            8.48e-07,
            8.481e-07,
            8.482e-07,
            8.483e-07,
            8.484e-07,
            8.485e-07,
            8.486e-07,
            8.487e-07,
            8.488e-07,
            8.489e-07,
            8.49e-07,
            8.491e-07,
            8.492e-07,
            8.493e-07,
            8.494e-07,
            8.495e-07,
            8.496e-07,
            8.497e-07,
            8.498e-07,
            8.499e-07,
            8.5e-07,
            8.501e-07,
            8.502e-07,
            8.503e-07,
            8.504e-07,
            8.505e-07,
            8.506e-07,
            8.507e-07,
            8.508e-07,
            8.509e-07,
            8.51e-07,
            8.511e-07,
            8.512e-07,
            8.513e-07,
            8.514e-07,
            8.515e-07,
            8.516e-07,
            8.517e-07,
            8.518e-07,
            8.519e-07,
            8.52e-07,
            8.521e-07,
            8.522e-07,
            8.523e-07,
            8.524e-07,
            8.525e-07,
            8.526e-07,
            8.527e-07,
            8.528e-07,
            8.529e-07,
            8.53e-07,
            8.531e-07,
            8.532e-07,
            8.533e-07,
            8.534e-07,
            8.535e-07,
            8.536e-07,
            8.537e-07,
            8.538e-07,
            8.539e-07,
            8.54e-07,
            8.541e-07,
            8.542e-07,
            8.543e-07,
            8.544e-07,
            8.545e-07,
            8.546e-07,
            8.547e-07,
            8.548e-07,
            8.549e-07,
            8.55e-07,
        ]


def test_get_ydata():
    with expected_protocol(
        AQ6370D,
        [
            (
                b":TRACe:Y? TRA",
                b"-4.86956280E+001,-2.10000000E+002,-5.16537424E+001,-2.10000000E+002,-4.86067300E+001,-4.78352284E+001,-2.10000000E+002,-4.81707215E+001,-2.10000000E+002,-5.43584664E+001,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-4.62890094E+001,-4.99632781E+001,-4.84670583E+001,-2.10000000E+002,-6.67897041E+001,-4.69517315E+001,-4.47765975E+001,-5.68119726E+001,-4.92760570E+001,-5.03743434E+001,-5.40501879E+001,-5.44914692E+001,-2.10000000E+002,-4.84519282E+001,-4.99197366E+001,-5.45284695E+001,-2.10000000E+002,-4.59264462E+001,-5.77729503E+001,-2.10000000E+002,-4.77913722E+001,-2.10000000E+002,-5.01532781E+001,-5.50815821E+001,-6.24957443E+001,-2.10000000E+002,-5.62660725E+001,-4.52742949E+001,-5.62840725E+001,-4.69330213E+001,-4.67175483E+001,-4.67265487E+001,-5.14409197E+001,-5.63270738E+001,-6.70597041E+001,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-4.93221653E+001,-5.19041404E+001,-2.10000000E+002,-6.05320117E+001,-2.10000000E+002,-5.17111700E+001,-5.00155046E+001,-4.87799287E+001,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-6.72347071E+001,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-4.69625487E+001,-5.25314604E+001,-2.10000000E+002,-5.14042656E+001,-5.37605969E+001,-5.16285723E+001,-4.66944256E+001,-4.79143931E+001,-4.88137215E+001,-2.10000000E+002,-2.10000000E+002,-4.77760915E+001,-2.10000000E+002,-2.10000000E+002,-5.09403438E+001,-4.70292309E+001,-5.74129731E+001,-5.03119184E+001,-4.75907315E+001,-6.74467138E+001,-4.75283861E+001,-6.24642367E+001,-4.63693293E+001,-4.75563865E+001,-2.10000000E+002,-4.84547693E+001,-4.80018574E+001,-4.59550538E+001,-2.10000000E+002,-2.10000000E+002\n",  # noqa: E501
            )
        ],
    ) as inst:
        assert inst.get_ydata(
            *("TRA",),
        ) == [
            -48.695628,
            -210.0,
            -51.6537424,
            -210.0,
            -48.60673,
            -47.8352284,
            -210.0,
            -48.1707215,
            -210.0,
            -54.3584664,
            -210.0,
            -210.0,
            -210.0,
            -46.2890094,
            -49.9632781,
            -48.4670583,
            -210.0,
            -66.7897041,
            -46.9517315,
            -44.7765975,
            -56.8119726,
            -49.276057,
            -50.3743434,
            -54.0501879,
            -54.4914692,
            -210.0,
            -48.4519282,
            -49.9197366,
            -54.5284695,
            -210.0,
            -45.9264462,
            -57.7729503,
            -210.0,
            -47.7913722,
            -210.0,
            -50.1532781,
            -55.0815821,
            -62.4957443,
            -210.0,
            -56.2660725,
            -45.2742949,
            -56.2840725,
            -46.9330213,
            -46.7175483,
            -46.7265487,
            -51.4409197,
            -56.3270738,
            -67.0597041,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -49.3221653,
            -51.9041404,
            -210.0,
            -60.5320117,
            -210.0,
            -51.71117,
            -50.0155046,
            -48.7799287,
            -210.0,
            -210.0,
            -210.0,
            -67.2347071,
            -210.0,
            -210.0,
            -210.0,
            -46.9625487,
            -52.5314604,
            -210.0,
            -51.4042656,
            -53.7605969,
            -51.6285723,
            -46.6944256,
            -47.9143931,
            -48.8137215,
            -210.0,
            -210.0,
            -47.7760915,
            -210.0,
            -210.0,
            -50.9403438,
            -47.0292309,
            -57.4129731,
            -50.3119184,
            -47.5907315,
            -67.4467138,
            -47.5283861,
            -62.4642367,
            -46.3693293,
            -47.5563865,
            -210.0,
            -48.4547693,
            -48.0018574,
            -45.9550538,
            -210.0,
            -210.0,
        ]


def test_initiate_sweep():
    with expected_protocol(
        AQ6370D,
        [(b":INITiate:IMMediate", None)],
    ) as inst:
        assert inst.initiate_sweep() is None


def test_reset():
    with expected_protocol(
        AQ6370D,
        [(b"*RST", None)],
    ) as inst:
        assert inst.reset() is None


def test_set_level_position_to_max():
    with expected_protocol(
        AQ6370D,
        [(b":CALCulate:MARKer:MAXimum:SRLevel", None)],
    ) as inst:
        assert inst.set_level_position_to_max() is None
