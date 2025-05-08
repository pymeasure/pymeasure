#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2025 PyMeasure Developers
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

from io import StringIO
from pymeasure.experiment.sequencer import SequenceHandler, SequenceEvaluationError


def non_empty_lines(text):
    lines = text.split("\n")
    linect = 0
    for line in lines:
        if line.strip() != "":
            linect += 1
    return linect


seq_file_text_1 = """
- "P1", "[1,2]"
-- "P2", "[3, 4, 5]"
"""

seq_file_text_2 = """
- "P1", "[1,2]"
-- "P2", "[3, 4, 5]"
- "P1", "[4,5]"
"""

seq_file_text_3 = """
- "P1", "[1,2]"
-- "P2", "[3, 4, 5]"
--- "P3", "[4, 5, 6]"
"""


@pytest.mark.parametrize("seq_file_text",
                         [
                             (seq_file_text_1,
                              (0, 1),
                              (1, 0),
                              ("P1", "P2")),
                             (seq_file_text_2,
                              (0, 1, 0),
                              (1, 0, 0),
                              ("P1", "P2", "P1")),
                             (seq_file_text_3,
                              (0, 1, 2),
                              (1, 1, 0),
                              ("P1", "P2", "P3")),
                         ])
def test_sequencer(seq_file_text):

    file_text, levels, children, params = seq_file_text
    fd = StringIO(file_text)

    s = SequenceHandler(file_obj=fd)
    assert len(s._sequences) == non_empty_lines(file_text)

    for index, lev in enumerate(levels):
        assert s._sequences[index].level == lev
    for index, c in enumerate(children):
        assert len(s.children(s._sequences[index])) == c

    for index, c in enumerate(params):
        assert s._sequences[index].parameter == c


seq_file_text_err1 = """
- "P1", "[1,2"
-- "P2", "[3, 4, 5]"
"""

seq_file_text_err2 = """
- "P1", "[1,2]"
--- "P2", "[3, 4, 5]"
- "P1", "[4,5]"
"""

seq_file_text_err3 = """
- "P1", "[1,2]"
-- "P2", "[3, 4, 5]"
--- "P3", ""
"""


@pytest.mark.parametrize("seq_file_text_err",
                         [(seq_file_text_err1,
                           SequenceEvaluationError,
                           "SyntaxError, likely unbalanced brackets"),
                          (seq_file_text_err2,
                           SequenceEvaluationError,
                           'Invalid file format: level missing ?'),
                          (seq_file_text_err3,
                           SequenceEvaluationError,
                           "No sequence entered")])
def test_sequencer_errors(seq_file_text_err):

    file_text, exception, exc_text = seq_file_text_err

    fd = StringIO(file_text)

    with pytest.raises(exception, match=exc_text):
        seq = SequenceHandler(file_obj=fd)
        seq.parameters_sequence()
