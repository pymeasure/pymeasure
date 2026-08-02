#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2026 PyMeasure Developers
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

"""Internal helper providing :class:`StrEnum` on all supported Python versions.

The standard library only ships :class:`enum.StrEnum` from Python 3.11 on.
pymeasure supports Python 3.10+, so this module re-exports the native class on
3.11+ and supplies a compatible fallback (``str`` + ``Enum`` with
``__str__`` returning the value) on 3.10.

Using ``sys.version_info`` instead of ``try: ... except ImportError`` keeps
static type checkers (pyright) happy across target versions: they pick the
matching branch unambiguously.
"""

import sys

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:  # pragma: no cover
    from enum import Enum

    class StrEnum(str, Enum):
        """Backport of :class:`enum.StrEnum` for Python 3.10."""

        def __str__(self) -> str:
            return self.value


__all__ = ["StrEnum"]
