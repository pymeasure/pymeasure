# -*- coding: utf-8 -*-
"""
Created the 15/06/2023

@author: Sebastien Weber
"""
from pymeasure.instruments import Instrument
from pymeasure.instruments.validators import modular_range, truncated_discrete_set, truncated_range

import logging

from elliptec.tools import parse

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class Rotator(Instrument):
    def __init__(self, adapter, name="Elliptec Rotator", **kwargs):
        super().__init__(
            adapter,
            name,
            **kwargs)

    id = Instrument.measurement("0in",
                                """ Get the Motor ID """,
                                get_process=lambda x: parse(f'{x}\r\n'.encode()),
                                )


if __name__ == '__main__':
    rot = Rotator('ASRL19::INSTR')
    print(rot.id)
    rot.clear()
