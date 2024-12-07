import pytest

from pymeasure.instruments.yokogawa.aq6370series import AQ6370D
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


def test_delete_trace():
    with expected_protocol(
        AQ6370D,
        [(b":TRACe:DELete TRA", None)],
    ) as inst:
        assert (
            inst.delete_trace(
                *("A",),
            )
            is None
        )


def test_execute_analysis():
    with expected_protocol(
        AQ6370D,
        [(b":CALCulate", None)],
    ) as inst:
        assert inst.execute_analysis() is None


def test_get_analysis():
    with expected_protocol(
        AQ6370D,
        [(b":CALCulate:DATA?", None)],
    ) as inst:
        assert inst.get_analysis() is None


def test_get_xdata():
    with expected_protocol(
        AQ6370D,
        [
            (
                b":TRACe:X? TRA",
                b"""+8.45000000E-007,+8.45100000E-007,+8.45200000E-007,+8.45300000E-007,
                +8.45400000E-007,+8.45500000E-007,+8.45600000E-007,+8.45700000E-007,
                +8.45800000E-007,+8.45900000E-007,+8.46000000E-007,+8.46100000E-007,
                +8.46200000E-007,+8.46300000E-007,+8.46400000E-007,+8.46500000E-007,
                +8.46600000E-007,+8.46700000E-007,+8.46800000E-007,+8.46900000E-007,
                +8.47000000E-007,+8.47100000E-007,+8.47200000E-007,+8.47300000E-007,
                +8.47400000E-007,+8.47500000E-007,+8.47600000E-007,+8.47700000E-007,
                +8.47800000E-007,+8.47900000E-007,+8.48000000E-007,+8.48100000E-007,
                +8.48200000E-007,+8.48300000E-007,+8.48400000E-007,+8.48500000E-007,
                +8.48600000E-007,+8.48700000E-007,+8.48800000E-007,+8.48900000E-007,
                +8.49000000E-007,+8.49100000E-007,+8.49200000E-007,+8.49300000E-007,
                +8.49400000E-007,+8.49500000E-007,+8.49600000E-007,+8.49700000E-007,
                +8.49800000E-007,+8.49900000E-007,+8.50000000E-007,+8.50100000E-007,
                +8.50200000E-007,+8.50300000E-007,+8.50400000E-007,+8.50500000E-007,
                +8.50600000E-007,+8.50700000E-007,+8.50800000E-007,+8.50900000E-007,
                +8.51000000E-007,+8.51100000E-007,+8.51200000E-007,+8.51300000E-007,
                +8.51400000E-007,+8.51500000E-007,+8.51600000E-007,+8.51700000E-007,
                +8.51800000E-007,+8.51900000E-007,+8.52000000E-007,+8.52100000E-007,
                +8.52200000E-007,+8.52300000E-007,+8.52400000E-007,+8.52500000E-007,
                +8.52600000E-007,+8.52700000E-007,+8.52800000E-007,+8.52900000E-007,
                +8.53000000E-007,+8.53100000E-007,+8.53200000E-007,+8.53300000E-007,
                +8.53400000E-007,+8.53500000E-007,+8.53600000E-007,+8.53700000E-007,
                +8.53800000E-007,+8.53900000E-007,+8.54000000E-007,+8.54100000E-007,
                +8.54200000E-007,+8.54300000E-007,+8.54400000E-007,+8.54500000E-007,
                +8.54600000E-007,+8.54700000E-007,+8.54800000E-007,+8.54900000E-007,
                +8.55000000E-007\n""",
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
                b"""-5.80586383E+001,-4.82452558E+001,-2.10000000E+002,-5.00581515E+001,
                -2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-5.39718179E+001,
                -2.10000000E+002,-4.83172555E+001,-2.10000000E+002,-5.40078179E+001,
                -9.28245811E+001,-4.71722994E+001,-2.10000000E+002,-5.20649217E+001,
                -2.10000000E+002,-2.10000000E+002,-4.58900745E+001,-4.76780332E+001,
                -4.88929655E+001,-4.59160745E+001,-5.89591856E+001,-6.04801307E+001,
                -4.56972546E+001,-5.37341531E+001,-4.68775174E+001,-4.63697811E+001,
                -2.10000000E+002,-4.58639117E+001,-2.10000000E+002,-5.04835809E+001,
                -2.10000000E+002,-4.55457108E+001,-2.10000000E+002,-2.10000000E+002,
                -5.25281289E+001,-5.25381299E+001,-6.83873225E+001,-4.97480469E+001,
                -5.03931511E+001,-4.94802372E+001,-4.99253305E+001,-5.57736026E+001,
                -4.43726648E+001,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,
                -2.10000000E+002,-5.35840271E+001,-2.10000000E+002,-2.10000000E+002,
                -4.61320419E+001,-2.10000000E+002,-4.82889238E+001,-4.89605452E+001,
                -4.80090332E+001,-2.10000000E+002,-5.24489220E+001,-5.59126029E+001,
                -4.93780799E+001,-2.10000000E+002,-5.22268893E+001,-4.99580469E+001,
                -2.10000000E+002,-5.37240266E+001,-6.86322957E+001,-2.10000000E+002,
                -2.10000000E+002,-2.10000000E+002,-4.70394921E+001,-4.96060890E+001,
                -2.10000000E+002,-4.75372963E+001,-2.10000000E+002,-2.10000000E+002,
                -2.10000000E+002,-2.10000000E+002,-5.42071536E+001,-4.70477584E+001,
                -2.10000000E+002,-2.10000000E+002,-2.10000000E+002,-2.10000000E+002,
                -5.67689941E+001,-4.81764150E+001,-2.10000000E+002,-4.87957619E+001,
                -2.10000000E+002,-2.10000000E+002,-5.51568122E+001,-2.10000000E+002,
                -5.09619656E+001,-2.10000000E+002,-5.43551546E+001,-4.71242549E+001,
                -5.27949223E+001,-5.43831531E+001,-2.10000000E+002,-4.94815222E+001,
                -6.89463024E+001\n""",
            )
        ],
    ) as inst:
        assert inst.get_ydata(
            *("TRA",),
        ) == [
            -58.0586383,
            -48.2452558,
            -210.0,
            -50.0581515,
            -210.0,
            -210.0,
            -210.0,
            -53.9718179,
            -210.0,
            -48.3172555,
            -210.0,
            -54.0078179,
            -92.8245811,
            -47.1722994,
            -210.0,
            -52.0649217,
            -210.0,
            -210.0,
            -45.8900745,
            -47.6780332,
            -48.8929655,
            -45.9160745,
            -58.9591856,
            -60.4801307,
            -45.6972546,
            -53.7341531,
            -46.8775174,
            -46.3697811,
            -210.0,
            -45.8639117,
            -210.0,
            -50.4835809,
            -210.0,
            -45.5457108,
            -210.0,
            -210.0,
            -52.5281289,
            -52.5381299,
            -68.3873225,
            -49.7480469,
            -50.3931511,
            -49.4802372,
            -49.9253305,
            -55.7736026,
            -44.3726648,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -53.5840271,
            -210.0,
            -210.0,
            -46.1320419,
            -210.0,
            -48.2889238,
            -48.9605452,
            -48.0090332,
            -210.0,
            -52.448922,
            -55.9126029,
            -49.3780799,
            -210.0,
            -52.2268893,
            -49.9580469,
            -210.0,
            -53.7240266,
            -68.6322957,
            -210.0,
            -210.0,
            -210.0,
            -47.0394921,
            -49.606089,
            -210.0,
            -47.5372963,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -54.2071536,
            -47.0477584,
            -210.0,
            -210.0,
            -210.0,
            -210.0,
            -56.7689941,
            -48.176415,
            -210.0,
            -48.7957619,
            -210.0,
            -210.0,
            -55.1568122,
            -210.0,
            -50.9619656,
            -210.0,
            -54.3551546,
            -47.1242549,
            -52.7949223,
            -54.3831531,
            -210.0,
            -49.4815222,
            -68.9463024,
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
