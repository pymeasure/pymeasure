import pytest

from pymeasure.instruments.yokogawa.aq6370d import AQ6370D
from pymeasure.test import expected_protocol


def test_init():
    with expected_protocol(
        AQ6370D,
        [],
    ):
        pass  # Verify the expected communication.


def test_level_position_setter():
    with expected_protocol(
        AQ6370D,
        [(b":DISPlay:TRACe:Y1:RPOSition 5", None)],
    ) as inst:
        inst.level_position = 5


def test_reference_level_setter():
    with expected_protocol(
        AQ6370D,
        [(b":DISPlay:TRACe:Y1:SCALe:RLEVel -10", None)],
    ) as inst:
        inst.reference_level = -10


def test_resolution_bandwidth_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:BWIDth:RESolution 1e-10", None)],
    ) as inst:
        inst.resolution_bandwidth = 1e-10


def test_sweep_mode_setter():
    with expected_protocol(
        AQ6370D,
        [(b":INITiate:SMODe 2", None)],
    ) as inst:
        inst.sweep_mode = "REPEAT"


def test_sweep_speed_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:SWEep:SPEed 0", None)],
    ) as inst:
        inst.sweep_speed = "1x"


def test_wavelength_center_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:CENTer 8.5e-07", None)],
    ) as inst:
        inst.wavelength_center = 8.5e-07


def test_wavelength_span_setter():
    with expected_protocol(
        AQ6370D,
        [(b":SENSe:WAVelength:SPAN 1e-07", None)],
    ) as inst:
        inst.wavelength_span = 1e-07


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


def test_abort():
    with expected_protocol(
        AQ6370D,
        [(b":ABORt", None)],
    ) as inst:
        assert inst.abort() is None


def test_copy_trace():
    with expected_protocol(
        AQ6370D,
        [(b":TRACe:COPY TRB,TRC", None)],
    ) as inst:
        assert (
            inst.copy_trace(
                *("TRB", "TRC"),
            )
            is None
        )


def test_delete_trace():
    with expected_protocol(
        AQ6370D,
        [(b":TRACe:DELete TRB", None)],
    ) as inst:
        assert (
            inst.delete_trace(
                *("TRB",),
            )
            is None
        )


def test_get_xdata():
    with expected_protocol(
        AQ6370D,
        [
            (
                b":TRACe:X? TRA",
                b"""
                7.59e-07,
                7.591e-07,
                7.592e-07,
                7.593e-07,
                7.594e-07,
                7.595e-07,
                7.596e-07,
                7.597e-07,
                7.598e-07,
                7.599e-07,
                7.6e-07
                \n
                """,
            )
        ],
    ) as inst:
        assert inst.get_xdata(
            *("TRA",),
        ) == [
            7.59e-07,
            7.591e-07,
            7.592e-07,
            7.593e-07,
            7.594e-07,
            7.595e-07,
            7.596e-07,
            7.597e-07,
            7.598e-07,
            7.599e-07,
            7.6e-07,
        ]


def test_get_ydata():
    with expected_protocol(
        AQ6370D,
        [
            (
                b":TRACe:Y? TRA",
                b"""
                -2.10000000E+002,-3.80367327E+001,
                -2.10000000E+002,-2.10000000E+002,
                """,
            )
        ],
    ) as inst:
        assert inst.get_ydata(
            *("TRA",),
        ) == [
            -210.0,
            -38.0367327,
            -210.0,
            -210.0,
        ]


def test_initiate():
    with expected_protocol(
        AQ6370D,
        [(b":INITiate:IMMediate", None)],
    ) as inst:
        assert inst.initiate() is None


def test_level_position_max():
    with expected_protocol(
        AQ6370D,
        [(b":CALCulate:MARKer:MAXimum:SRLevel", None)],
    ) as inst:
        assert inst.level_position_max() is None
