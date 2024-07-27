from pymeasure.test import expected_protocol
from pymeasure.instruments.siglenttechnologies import SDS1072CML


def test_init():
    with expected_protocol(
        SDS1072CML,
        [],
    ):
        pass  # Verify the expected communication.


def test_channel_1_coupling_setter():
    with expected_protocol(
        SDS1072CML,
        [(b"C1:CPL A1M", None)],
    ) as inst:
        inst.channel_1.coupling = "AC"


def test_channel_1_coupling_getter():
    with expected_protocol(
        SDS1072CML,
        [(b"C1:CPL?", b"C1:CPL A1M\n")],
    ) as inst:
        assert inst.channel_1.coupling == "AC"


def test_channel_1_vertical_division_setter():
    with expected_protocol(
        SDS1072CML,
        [(b"C1:VDIV 2.00e+00V", None)],
    ) as inst:
        inst.channel_1.vertical_division = 2


def test_channel_1_vertical_division_getter():
    with expected_protocol(
        SDS1072CML,
        [(b"C1:VDIV?", b"C1:VDIV 2.00E+00V\n")],
    ) as inst:
        assert inst.channel_1.vertical_division == 2.0


def test_is_ready_getter():
    with expected_protocol(
        SDS1072CML,
        [(b"SAST?", b"SAST Ready\n")],
    ) as inst:
        assert inst.is_ready is True


def test_timeDiv_setter():
    with expected_protocol(
        SDS1072CML,
        [(b":TDIV 1.00e-03S", None)],
    ) as inst:
        inst.timeDiv = 0.001


def test_timeDiv_getter():
    with expected_protocol(
        SDS1072CML,
        [(b":TDIV?", b"TDIV 1.00E-03S\n")],
    ) as inst:
        assert inst.timeDiv == 0.001


def test_arm():
    with expected_protocol(
        SDS1072CML,
        [(b"SAST?", b"SAST Ready\n"), (b"ARM", None)],
    ) as inst:
        assert inst.arm() is True


def test_trigger_get_triggerConfig():
    with expected_protocol(
        SDS1072CML,
        [
            (b"TRSE?", b"TRSE EDGE,SR,EX,HT,TI,HV,100NS\n"),
            (b"TRLV?", b"C1:TRLV 0.00E+00V\n"),
            (b"TRSL?", b"C1:TRSL POS\n"),
            (b"TRMD?", b"TRMD SINGLE\n"),
            (b"TRCP?", b"C1:TRCP DC\n"),
        ],
    ) as inst:
        assert inst.trigger.get_triggerConfig() == {
            "type": "EDGE",
            "source": "C1",
            "hold_type": "TI",
            "hold_value1": "100NS",
            "level": 0.0,
            "slope": "POS",
            "mode": "SINGLE",
            "coupling": "DC",
        }


def test_trigger_set_triggerConfig():
    with expected_protocol(
        SDS1072CML,
        [
            (b"TRSE?", b"TRSE EDGE,SR,C1,HT,TI,HV,100NS\n"),
            (b"TRLV?", b"C1:TRLV 0.00E+00V\n"),
            (b"TRSL?", b"C1:TRSL POS\n"),
            (b"TRMD?", b"TRMD SINGLE\n"),
            (b"TRCP?", b"C1:TRCP DC\n"),
            (b"TRSE EDGE,SR,EX,HT,TI,HV,100NS", None),
            (b"EX:TRLV 5.00e-01V", None),
            (b"TRSE?", b"TRSE EDGE,SR,EX,HT,TI,HV,100NS\n"),
            (b"TRLV?", b"EX:TRLV 5.04E-01V\n"),
            (b"TRSL?", b"EX:TRSL POS\n"),
            (b"TRMD?", b"TRMD SINGLE\n"),
            (b"TRCP?", b"EX:TRCP DC\n"),
        ],
    ) as inst:
        assert (
            inst.trigger.set_triggerConfig(
                **{"source": "EX", "coupling": "DC", "level": 0.5, "slope": "POS"}
            )
            is True
        )


import pytest

from pymeasure.test import expected_protocol
from pymeasure.instruments.siglenttechnologies import SDS1072CML


def test_init():
    with expected_protocol(
        SDS1072CML,
        [],
    ):
        pass  # Verify the expected communication.


def test_waveform_setup_setter():
    with expected_protocol(
        SDS1072CML,
        [(b"WFSU SP,80,NP,20,FP,90", None)],
    ) as inst:
        inst.waveform_setup = {"sparsing": 80, "number": 20, "first": 90}


def test_waveform_setup_getter():
    with expected_protocol(
        SDS1072CML,
        [(b"WFSU?", b"WFSU SP,80,NP,20,FP,90,SN,0\n")],
    ) as inst:
        assert inst.waveform_setup == {"sparsing": 80, "number": 20, "first": 90}


def test_channel_1_get_waveform():
    with expected_protocol(
        SDS1072CML,
        [
            (
                b"C1:WF? ALL",
                b"C1:WF ALL,#9000000366WAVEDESC\x00\x00\x00\x00\x00\x00\x00\x00DSO\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00Z\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00SDS1072CML\x00\x00\x00\x00\x00\x00\xab\xcd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00P\x00\x00\xfeO\x00\x00\x00\x00\x00\x00\xffO\x00\x00Z\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\n\xd7\xa3=\xcd\xccL?\x00\x00\xfeB\x00\x00\x00\xc3\x08\x00\x01\x00\x95\xbf\xd64\x00\x00\x00\xc0\x0b\x8e\x97?\x00\x00\x00\xc0\x0b\x8e\x97?V\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00S\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00_p\x890\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10\x00\x04\x00\x00\x00\x80?\t\x00\x00\x00\x00\x00\x80?\xcd\xccL?\x00\x00\x12\x18\x1d\"&()*('$\x1f\x1a\x14\x0f\x08\x02\xfd\xf8\xf4\n\n",  # noqa: E501
            ),
            (
                b"C1:WF? DESC",
                b"C1:WF ALL,#9000000346WAVEDESC\x00\x00\x00\x00\x00\x00\x00\x00DSO\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00Z\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00SDS1072CML\x00\x00\x00\x00\x00\x00\xab\xcd\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00P\x00\x00\x00P\x00\x00\xfeO\x00\x00\x00\x00\x00\x00\xffO\x00\x00Z\x00\x00\x00P\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\n\xd7\xa3=\xcd\xccL?\x00\x00\xfeB\x00\x00\x00\xc3\x08\x00\x01\x00\x95\xbf\xd64\x00\x00\x00\x00\xd6\x8d\x97?\x00\x00\x00\x00\xd6\x8d\x97?V\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00S\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00_p\x890\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x10\x00\x04\x00\x00\x00\x80?\t\x00\x00\x00\x00\x00\x80?\xcd\xccL?\x00\x00\n",
            ),
            (b"WFSU?", b"WFSU SP,80,NP,20,FP,90,SN,0\n"),
        ],
    ) as inst:
        assert inst.channel_1.get_waveform() == (
            [
                0.02300199866294861,
                0.023002398662953283,
                0.023002798662957957,
                0.02300319866296263,
                0.023003598662967306,
                0.02300399866297198,
                0.023004398662976655,
                0.02300479866298133,
                0.023005198662986004,
                0.02300559866299068,
                0.023005998662995353,
                0.023006398663000027,
                0.0230067986630047,
                0.023007198663009376,
                0.02300759866301405,
                0.023007998663018725,
                0.0230083986630234,
                0.023008798663028074,
                0.02300919866303275,
                0.023009598663037423,
            ],
            [
                0.6399999558925629,
                1.1199999451637268,
                1.51999993622303,
                1.9199999272823334,
                2.239999920129776,
                2.3999999165534973,
                2.479999914765358,
                2.5599999129772186,
                2.3999999165534973,
                2.3199999183416367,
                2.0799999237060547,
                1.6799999326467514,
                1.2799999415874481,
                0.7999999523162842,
                0.3999999612569809,
                -0.1600000262260437,
                -0.6400000154972076,
                -1.040000006556511,
                -1.4399999976158142,
                -1.7599999904632568,
            ],
        )
