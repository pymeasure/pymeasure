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


class SCPIKeyword(str):
    """Represents a SCPI keyword with shortform handling.

    A `SCPIKeyword` is a string subclass that enforces SCPI keyword syntax and automatically derives
    the valid shortform abbreviation (the uppercase portion, plus any digits). It can be compared
    case-insensitively against either its longform or shortform.

    Example:
        >>> k = SCPIKeyword("MEASure")
        >>> k.shortform
        'SOUR'
        >>> k == "meas"
        True
        >>> k == "measure"
        True
        >>> k == "measu"
        False

    Rules:
        * Must contain only alphanumeric characters.
        * Uppercase letters define the shortform abbreviation.
        * Must start with at least one uppercase letter to define the shortform.
        * Must follow the pattern <uppercase><lowercase><digits>.
    """

    def __new__(cls, value):
        """Validate and construct a new SCPIKeyword instance."""
        if isinstance(value, SCPIKeyword):
            value = str(value)

        if not isinstance(value, str):
            raise TypeError(f"Expected a string or SCPIKeyword, got {type(value).__name__}")

        if not value.isalnum():
            raise ValueError(f"Invalid SCPIKeyword '{value}': must be alphanumeric")

        upper = "".join(filter(str.isupper, value))
        lower = "".join(filter(str.islower, value))
        decimal = "".join(filter(str.isdecimal, value))

        if len(upper) == 0:
            raise ValueError(
                f"Invalid SCPIKeyword '{value}': Must start with at least one uppercase character."
            )

        if value != upper + lower + decimal:
            raise ValueError(
                f"Invalid SCPIKeyword '{value}': "
                "must be of the form '<uppercase><lowercase><decimal>'."
            )

        self = str.__new__(cls, value)
        self.shortform = upper + decimal
        return self

    def __eq__(self, other):
        """Compare against a string or SCPIKeyword, matching longform or shortform."""
        if isinstance(other, str):
            return other.upper() in [self.upper(), self.shortform]
        return NotImplemented

    def __repr__(self):
        return f"SCPIKeyword('{str(self)}')"
