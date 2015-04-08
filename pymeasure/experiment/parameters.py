"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


class Parameter(object):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and unit if supplied.

    Parameter name can not contain a colon ':'.
    """

    def __init__(self, name, unit=None, default=None):
        self.name = name
        self._value = default
        self.unit = unit
        self.default = default

    @property
    def value(self):
        if self.isSet():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        self._value = value

    def isSet(self):
        return self._value is not None

    def __str__(self):
        result = ""
        if self.isSet():
            result += "%s" % str(self.value)
            if self.unit:
                result += " %s" % self.unit
        return result

    def __repr__(self):
        result = "<Parameter(name='%s'" % self.name
        if self.isSet():
            result += ",value=%s" % repr(self.value)
        if self.unit:
            result += ",unit='%s'" % self.unit
        return result + ")>"


class IntegerParameter(Parameter):

    @property
    def value(self):
        if self.isSet():
            return int(self._value)
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            self._value = int(value)
        except ValueError:
            raise ValueError("IntegerParameter given non-integer value of "
                             "type '%s'" % type(value))

    def __repr__(self):
        result = super(IntegerParameter, self).__repr__()
        return result.replace("<Parameter", "<IntegerParameter", 1)

class BooleanParameter(Parameter):

    @property
    def value(self):
        if self.isSet():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            if value == "True":
                self._value = True
            elif value == "False":
                self._value = False
            else:
                raise ValueError("Parameter value is not set, must be True or False.")
        except ValueError:
            raise ValueError("BooleanParameter given non-boolean value of "
                             "type '%s'" % type(value))

    def __repr__(self):
        result = super(BooleanParameter, self).__repr__()
        return result.replace("<Parameter", "<BooleanParameter", 1)


class FloatParameter(Parameter):

    @property
    def value(self):
        if self.isSet():
            return float(self._value)
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            self._value = float(value)
        except ValueError:
            raise ValueError("FloatParameter given non-float value of "
                             "type '%s'" % type(value))

    def __repr__(self):
        result = super(FloatParameter, self).__repr__()
        return result.replace("<Parameter", "<FloatParameter", 1)


class VectorParameter(Parameter):
    def __init__(self, name, length=3, unit=None, default=None):
        self.name = name
        self._value = default
        self.unit = unit
        self.default = default
        self._length = length

    @property
    def value(self):
        if self.isSet():
            return [float(ve) for ve in self._value]
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        # Strip initial and final brackets
        if isinstance(value, basestring):
            if (value[0] != '[') or (value[-1] != ']'):
                raise ValueError("VectorParameter must be passed a vector"
                                 " denoted by square brackets if initializing"
                                 " by string.")
            raw_list = value[1:-1].split(",")
        elif isinstance(value, (list, tuple)):
            raw_list = value
        else:
            raise ValueError("VectorParameter given undesired value of "
                             "type '%s'" % type(value))
        if len(raw_list) != self._length:
            raise ValueError("VectorParameter given value of length "
                             "%d instead of %d" % (len(raw_list), self._length))
        try:
            self._value = [float(ve) for ve in raw_list]

        except ValueError:
            raise ValueError("VectorParameter given input '%s' that could "
                             "not be converted to floats." % str(value))

    def __repr__(self):
        if not self.isSet():
            raise ValueError("Parameter value is not set")
        result = "<VectorParameter(name='%s'" % self.name
        result += ",value=%s" % "".join(repr(self.value).split())
        if self.unit:
            result += ",unit='%s'" % self.unit
        return result + ")>"

    def __str__(self):
        """If we eliminate spaces within the list __repr__ then the
        csv parser will interpret it as a single value."""
        if not self.isSet():
            raise ValueError("Parameter value is not set")
        result = ""
        result += "%s" % "".join(repr(self.value).split())
        if self.unit:
            result += " %s" % self.unit
        return result


class ListParameter(Parameter):

    def __init__(self, name, choices, unit=None, default=None):
        self.name = name
        self._value = default
        self.unit = unit
        self.default = default
        self._choices = choices

    @property
    def value(self):
        if self.isSet():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        if value in self._choices:
            self._value = value
        else:
            raise ValueError("Invalid choice for parameter. "
                             "Must be one of %s" % str(self._choices))

    def isSet(self):
        return self._value is not None
