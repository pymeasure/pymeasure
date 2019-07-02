#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2019 PyMeasure Developers
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


class Parameter(object):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and units if supplied.

    :var value: The value of the parameter

    :param name: The parameter name
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, default=None, ui_class=None):
        self.name = name
        self._value = default
        self.default = default
        self.ui_class = ui_class

    @property
    def value(self):
        if self.is_set():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        self._value = value

    def is_set(self):
        """ Returns True if the Parameter value is set
        """
        return self._value is not None

    def __str__(self):
        return str(self._value) if self.is_set() else ''

    def __repr__(self):
        return "<%s(name=%s,value=%s,default=%s)>" % (
            self.__class__.__name__, self.name, self._value, self.default)


class IntegerParameter(Parameter):
    """ :class:`.Parameter` sub-class that uses the integer type to
    store the value.

    :var value: The integer value of the parameter

    :param name: The parameter name
    :param units: The units of measure for the parameter
    :param minimum: The minimum allowed value (default: -1e9)
    :param maximum: The maximum allowed value (default: 1e9)
    :param default: The default integer value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, units=None, minimum=-1e9, maximum=1e9, **kwargs):
        super().__init__(name, **kwargs)
        self.units = units
        self.minimum = int(minimum)
        self.maximum = int(maximum)

    @property
    def value(self):
        if self.is_set():
            return int(self._value)
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            value = int(value)
        except ValueError:
            raise ValueError("IntegerParameter given non-integer value of "
                             "type '%s'" % type(value))
        if value < self.minimum:
            raise ValueError("IntegerParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("IntegerParameter value is above the maximum")
        else:
            self._value = value

    def __str__(self):
        if not self.is_set():
            return ''
        result = "%d" % self._value
        if self.units:
            result += " %s" % self.units
        return result

    def __repr__(self):
        return "<%s(name=%s,value=%s,units=%s,default=%s)>" % (
            self.__class__.__name__, self.name, self._value, self.units, self.default)


class BooleanParameter(Parameter):
    """ :class:`.Parameter` sub-class that uses the boolean type to
    store the value.

    :var value: The boolean value of the parameter

    :param name: The parameter name
    :param default: The default boolean value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    @property
    def value(self):
        if self.is_set():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            self._value = bool(value)
        except ValueError:
            raise ValueError("BooleanParameter given non-boolean value of "
                             "type '%s'" % type(value))


class FloatParameter(Parameter):
    """ :class:`.Parameter` sub-class that uses the floating point
    type to store the value.

    :var value: The floating point value of the parameter

    :param name: The parameter name
    :param units: The units of measure for the parameter
    :param minimum: The minimum allowed value (default: -1e9)
    :param maximum: The maximum allowed value (default: 1e9)
    :param default: The default floating point value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, units=None, minimum=-1e9, maximum=1e9, **kwargs):
        super().__init__(name, **kwargs)
        self.units = units
        self.minimum = minimum
        self.maximum = maximum

    @property
    def value(self):
        if self.is_set():
            return float(self._value)
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        try:
            value = float(value)
        except ValueError:
            raise ValueError("FloatParameter given non-float value of "
                             "type '%s'" % type(value))
        if value < self.minimum:
            raise ValueError("FloatParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("FloatParameter value is above the maximum")
        else:
            self._value = value

    def __str__(self):
        if not self.is_set():
            return ''
        result = "%g" % self._value
        if self.units:
            result += " %s" % self.units
        return result

    def __repr__(self):
        return "<%s(name=%s,value=%s,units=%s,default=%s)>" % (
            self.__class__.__name__, self.name, self._value, self.units, self.default)


class VectorParameter(Parameter):
    """ :class:`.Parameter` sub-class that stores the value in a
    vector format.

    :var value: The value of the parameter as a list of floating point numbers

    :param name: The parameter name
    :param length: The integer dimensions of the vector
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, length=3, units=None, **kwargs):
        super().__init__(name, **kwargs)
        self._length = length
        self.units = units

    @property
    def value(self):
        if self.is_set():
            return [float(ve) for ve in self._value]
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        # Strip initial and final brackets
        if isinstance(value, str):
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

    def __str__(self):
        """If we eliminate spaces within the list __repr__ then the
        csv parser will interpret it as a single value."""
        if not self.is_set():
            return ''
        result = "".join(repr(self.value).split())
        if self.units:
            result += " %s" % self.units
        return result

    def __repr__(self):
        return "<%s(name=%s,value=%s,units=%s,length=%s)>" % (
            self.__class__.__name__, self.name, self._value, self.units, self._length)


class ListParameter(Parameter):
    """ :class:`.Parameter` sub-class that stores the value as a list.

    :param name: The parameter name
    :param choices: An explicit list of choices, which is disregarded if None
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, choices=None, units=None, **kwargs):
        super().__init__(name, **kwargs)
        self._choices = tuple(choices) if choices is not None else None
        self.units = units

    @property
    def value(self):
        if self.is_set():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        if self._choices is not None and value in self._choices:
            self._value = value
        else:
            raise ValueError("Invalid choice for parameter. "
                             "Must be one of %s" % str(self._choices))

    @property
    def choices(self):
        """ Returns an immutable iterable of choices, or None if not set. """
        return self._choices


class PhysicalParameter(VectorParameter):
    """ :class:`.VectorParameter` sub-class of 2 dimensions to store a value
    and its uncertainty.

    :var value: The value of the parameter as a list of 2 floating point numbers

    :param name: The parameter name
    :param uncertainty_type: Type of uncertainty, 'absolute', 'relative' or 'percentage'
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(self, name, uncertaintyType='absolute', **kwargs):
        super().__init__(name, length=2, **kwargs)
        self._utype = ListParameter("uncertainty type",
                                    choices=['absolute', 'relative', 'percentage'],
                                    default=None)
        self._utype.value = uncertaintyType

    @property
    def value(self):
        if self.is_set():
            return [float(ve) for ve in self._value]
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value):
        # Strip initial and final brackets
        if isinstance(value, str):
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
        # Uncertainty must be non-negative
        self._value[1] = abs(self._value[1])

    @property
    def uncertainty_type(self):
        return self._utype.value

    @uncertainty_type.setter
    def uncertainty_type(self, uncertaintyType):
        oldType = self._utype.value
        self._utype.value = uncertaintyType
        newType = self._utype.value

        if self.is_set():
            # Convert uncertainty value to the new type
            if (oldType, newType) == ('absolute', 'relative'):
                self._value[1] = abs(self._value[1] / self._value[0])
            if (oldType, newType) == ('relative', 'absolute'):
                self._value[1] = abs(self._value[1] * self._value[0])
            if (oldType, newType) == ('relative', 'percentage'):
                self._value[1] = abs(self._value[1] * 100.0)
            if (oldType, newType) == ('percentage', 'relative'):
                self._value[1] = abs(self._value[1] * 0.01)
            if (oldType, newType) == ('percentage', 'absolute'):
                self._value[1] = abs(self._value[1] * self._value[0] * 0.01)
            if (oldType, newType) == ('absolute', 'percentage'):
                self._value[1] = abs(self._value[1] * 100.0 / self._value[0])

    def __str__(self):
        if not self.is_set():
            return ''
        result = "%g +/- %g" % (self._value[0], self._value[1])
        if self.units:
            result += " %s" % self.units
        if self._utype.value is not None:
            result += " (%s)" % self._utype.value
        return result

    def __repr__(self):
        return "<%s(name=%s,value=%s,units=%s,uncertaintyType=%s)>" % (
            self.__class__.__name__, self.name, self._value, self.units, self._utype.value)


class Measurable(object):
    """ Encapsulates the information for a measurable experiment parameter
    with information about the name, fget function and units if supplied.
    The value property is called when the procedure retrieves a datapoint
    and calls the fget function. If no fget function is specified, the value
    property will return the latest set value of the parameter (or default
    if never set).

    :var value: The value of the parameter

    :param name: The parameter name
    :param fget: The parameter fget function (e.g. an instrument parameter)
    :param default: The default value
    """
    DATA_COLUMNS = []

    def __init__(self, name, fget=None, units=None, measure=True, default=None, **kwargs):
        self.name = name
        self.units = units
        self.measure = measure
        if fget is not None:
            self.fget = fget
            self._value = fget()
        else:
            self._value = default
        Measurable.DATA_COLUMNS.append(name)

    def fget(self):
        return self._value

    @property
    def value(self):
        if hasattr(self, 'fget'):
            self._value = self.fget()
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
