
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
            [(b'C1:CPL A1M', None)],
    ) as inst:
        inst.channel_1.coupling = 'AC'


def test_channel_1_coupling_getter():
    with expected_protocol(
            SDS1072CML,
            [(b'C1:CPL?', b'C1:CPL A1M\n')],
    ) as inst:
        assert inst.channel_1.coupling == 'AC'


def test_channel_1_vertical_division_setter():
    with expected_protocol(
            SDS1072CML,
            [(b'C1:VDIV 2.00e+00V', None)],
    ) as inst:
        inst.channel_1.vertical_division = 2


def test_channel_1_vertical_division_getter():
    with expected_protocol(
            SDS1072CML,
            [(b'C1:VDIV?', b'C1:VDIV 2.00E+00V\n')],
    ) as inst:
        assert inst.channel_1.vertical_division == 2.0


def test_is_ready_getter():
    with expected_protocol(
            SDS1072CML,
            [(b'SAST?', b'SAST Ready\n')],
    ) as inst:
        assert inst.is_ready is True


def test_timeDiv_setter():
    with expected_protocol(
            SDS1072CML,
            [(b':TDIV 1.00e-03S', None)],
    ) as inst:
        inst.timeDiv = 0.001


def test_timeDiv_getter():
    with expected_protocol(
            SDS1072CML,
            [(b':TDIV?', b'TDIV 1.00E-03S\n')],
    ) as inst:
        assert inst.timeDiv == 0.001


def test_arm():
    with expected_protocol(
            SDS1072CML,
            [(b'SAST?', b'SAST Ready\n'),
             (b'ARM', None)],
    ) as inst:
        assert inst.arm() is True


def test_trigger_get_triggerConfig():
    with expected_protocol(
            SDS1072CML,
            [(b'TRSE?', b'TRSE EDGE,SR,EX,HT,TI,HV,100NS\n'),
             (b'TRLV?', b'C1:TRLV 0.00E+00V\n'),
             (b'TRSL?', b'C1:TRSL POS\n'),
             (b'TRMD?', b'TRMD SINGLE\n'),
             (b'TRCP?', b'C1:TRCP DC\n')],
    ) as inst:
        assert inst.trigger.get_triggerConfig() == {
            'type': 'EDGE',
            'source': 'EX',
            'hold_type': 'TI',
            'hold_value1': '100NS',
            'level': 0.504,
            'slope': 'POS',
            'mode': 'SINGLE',
            'coupling': 'DC'}


def test_trigger_set_triggerConfig():
    with expected_protocol(
            SDS1072CML,
            [(b'TRSE?', b'TRSE EDGE,SR,C1,HT,TI,HV,100NS\n'),
             (b'TRLV?', b'C1:TRLV 0.00E+00V\n'),
             (b'TRSL?', b'C1:TRSL POS\n'),
             (b'TRMD?', b'TRMD SINGLE\n'),
             (b'TRCP?', b'C1:TRCP DC\n'),
             (b'TRSE EDGE,SR,EX,HT,TI,HV,100NS', None),
             (b'EX:TRLV 5.00e-01V', None),
             (b'TRSE?', b'TRSE EDGE,SR,EX,HT,TI,HV,100NS\n'),
             (b'TRLV?', b'EX:TRLV 5.04E-01V\n'),
             (b'TRSL?', b'EX:TRSL POS\n'),
             (b'TRMD?', b'TRMD SINGLE\n'),
             (b'TRCP?', b'EX:TRCP DC\n')],
    ) as inst:
        assert inst.trigger.set_triggerConfig(**{
            'source': 'EX', 'coupling': 'DC', 'level': 0.5, 'slope': 'POS'}) is True
