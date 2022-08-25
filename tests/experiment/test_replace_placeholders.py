#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2022 PyMeasure Developers
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

from datetime import datetime

from pymeasure.experiment.results import replace_placeholders
from pymeasure.experiment.procedure import Procedure
from pymeasure.experiment import Parameter, BooleanParameter, FloatParameter


def test_replace_placeholders():
    class FakeProcedure(Procedure):
        str_param = Parameter("String Parameter")
        bool_param = BooleanParameter("Boolean Parameter")
        float_param = FloatParameter("Float Parameter")

    fake = FakeProcedure()
    fake.set_parameters({
        "str_param": "test",
        "bool_param": False,
        "float_param": 1.252
    })

    assert replace_placeholders("{String Parameter}", fake) == "test"
    assert replace_placeholders("{Boolean Parameter}", fake) == "False"
    assert replace_placeholders("{Float Parameter:.2f}", fake) == "1.25"
    assert replace_placeholders(
        "{String Parameter}_{Float Parameter}_{Boolean Parameter}", fake) == "test_1.252_False"

    with pytest.raises(KeyError):
        replace_placeholders("{Unknown Parameter}", fake)

    date_format = "%Y-%m"
    time_format = "%H:%M"
    now = datetime.now()
    date = now.strftime(date_format)
    time = now.strftime(time_format)
    assert replace_placeholders(
        "{date}--{time}", fake, date_format=date_format, time_format=time_format
    ) == date + '--' + time
