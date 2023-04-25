# -*- coding: utf-8 -*-
"""
Created the 25/04/2023

@author: Sebastien Weber
"""

from pymeasure.test import Generator  # This suppose you're going to put the Generator object there
from pymeasure.instruments.ametek.ametek7270 import Ametek7270


def generate():
    g = Generator()
    g.instantiate(Ametek7270, 'USB0::0x0A2D::0x001B::16216344::RAW', 'ametek',
                  read_termination='\x00', write_termination='\x00')

    g.test_property_getter('sensitivity')
    g.test_property_setter_batch('sensitivity', Ametek7270.SENSITIVITIES_IMODE[0])
    g.test_property_getter('sensitivity')
    g.test_property_getter('slope')
    g.test_property_setter('slope', 12)
    g.test_property_getter('time_constant')
    g.test_property_setter_batch('time_constant', Ametek7270.TIME_CONSTANTS)

    g.test_property_getter('x')
    g.test_property_getter('y')
    g.test_property_getter('x1')
    g.test_property_getter('y1')
    g.test_property_getter('x2')
    g.test_property_getter('y2')
    g.test_property_getter('xy')
    g.test_property_getter('mag')
    g.test_property_getter('theta')

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('phase')
    g.test_property_setter('phase', 250)

    g.test_property_getter('voltage')
    g.test_property_setter('voltage', 2.7)

    g.test_property_getter('frequency')
    g.test_property_setter('frequency', 12000)

    g.test_property_getter('dac1')
    g.test_property_setter('dac1', 7)

    g.test_property_getter('dac2')
    g.test_property_setter('dac2', -7)

    g.test_property_getter('dac3')
    g.test_property_setter('dac3', 2.6)

    g.test_property_getter('dac4')
    g.test_property_setter('dac4', 5.5)

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('harmonic')
    g.test_property_setter('harmonic', 7)

    g.test_property_getter('adc1')
    g.test_property_getter('adc2')
    g.test_property_getter('adc3')
    g.test_property_getter('adc4')

    g.test_property_getter('id')

    g.test_method('set_voltage_mode')
    g.test_method('set_differential_mode')
    g.test_method('set_current_mode', low_noise=False)
    g.test_method('set_current_mode', low_noise=True)

    g.test_method('set_channel_A_mode')

    g.test_method('identification')

    g.test_property_setter('autogain', True)
    g.test_property_setter('autogain', False)

    g.test_method('shutdown')

    g.write_file("test_ametek7270.py")


def run():
    dev = Ametek7270('USB0::0x0A2D::0x001B::16216344::RAW')
    dev.id
    dev.identification()
    dev.shutdown()


if __name__ == '__main__':
    # run()
    # generate()
    pass
