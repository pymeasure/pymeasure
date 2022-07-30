import pytest

from pymeasure.test import expected_protocol


from pymeasure.instruments.parker import ParkerGV6 as _ParkerGV6


class ParkerGV6(_ParkerGV6):
    def __init__(self, adapter):
        super(_ParkerGV6, self).__init__(adapter, name="GV6")
        self.set_defaults()

    def write(self, command):
        super(_ParkerGV6, self).write(command)


def test_init():
    with expected_protocol(
            ParkerGV6, [(b"ECHO0", None),
                        (b"LH0", None),
                        (b"MA1", None),
                        (b"MC0", None),
                        (b"AA1.0", None),
                        (b"A1.0", None),
                        (b"V3.0", None),
                        ]) as instr:
        pass
