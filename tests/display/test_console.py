#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2023 PyMeasure Developers
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

import pytest

from pymeasure.experiment.parameters import (BooleanParameter,
                                             ListParameter,
                                             FloatParameter,
                                             IntegerParameter,
                                             Parameter,
                                             VectorParameter,
                                             PhysicalParameter)
from pymeasure.experiment.procedure import Procedure
from pymeasure.display.console import ConsoleArgumentParser


class TestArgParsing:
    @pytest.mark.parametrize("param", [
        ('plain_param', 'a'),
        ('int_param', 100),
        ('float_param', 0.5),
        ('bool_param', True),
        ('vector_param', [1.0, 2, 3]),
        ('list_param', '2'),
        ('physical_param', [1.0, 0.1])
    ])
    def test_init_from_param(self, param):
        class TestProcedure(Procedure):
            plain_param = Parameter('Plain parameter', default=100)
            int_param = IntegerParameter('Integer parameter', default=100)
            float_param = FloatParameter('Float parameter', units='s', default=0.2)
            bool_param = BooleanParameter('Boolean parameter', default=True)
            list_param = ListParameter('List parameter',
                                       default='1', choices=['1', '2', '3'])
            vector_param = VectorParameter('Vector parameter',
                                           default=[1, 5, 3])
            physical_param = PhysicalParameter('Physical parameter', units='s',
                                               default=[1.0, 0.1])

        name, value = param
        console = ConsoleArgumentParser(TestProcedure)
        args = vars(console.parse_args(['--' + name, str(value)]))
        assert args[name] == value


class TestArgHelpString:
    @pytest.mark.parametrize("klass, kwargs", [
        (Parameter, {'name': 'Plain parameter', 'default': 'a'}),
        (IntegerParameter, {'name': 'Integer parameter', 'default': 100}),
        (FloatParameter, {'name': 'Float parameter', 'default': 0.5}),
        (BooleanParameter, {'name': 'Boolean parameter', 'default': True}),
        (VectorParameter, {'name': 'Vector parameter', 'default': [1.0, 2, 3]}),
        (ListParameter, {'name': 'List parameter',
                         'default': '2', 'choices': ['1', '2', '3']}),
        (PhysicalParameter, {'name': 'Physical parameter',
                             'default': [1.0, 0.1]})
    ])
    def test_init_from_param(self, klass, kwargs):
        class TestProcedure(Procedure):
            parameter = klass(**kwargs)

        desc = kwargs['name']
        default_value = kwargs['default']
        console = ConsoleArgumentParser(TestProcedure)
        help_message = [value.strip() for value in console.format_help().split("\n")]
        assert '--parameter PARAMETER' in help_message
        for help_line in help_message:
            if desc in help_line:
                break
        assert desc in help_line
        assert 'default' in help_line
        assert str(default_value) in help_line
