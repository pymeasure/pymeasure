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

from typing import Any, Callable, Generic, Literal, Type, TypeVar
import numpy as np
from numpy._core.fromnumeric import var
from qtpy import QtWidgets

from pymeasure.typing import GroupByType, GroupConditionType, SupportsStr

T = TypeVar("T")

class Parameter(Generic[T]):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and units if supplied.
1
    :var value: The value of the parameter

    :param name: The parameter name
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    :param group_by: Defines the Parameter(s) that controls the visibility
        of the associated input; can be a string containing the Parameter
        name, a list of strings with multiple Parameter names, or a dict
        containing {"Parameter name": condition} pairs.
    :param group_condition: The condition for the group_by Parameter
        that controls the visibility of this parameter, provided as a value
        or a (lambda)function. If the group_by argument is provided as a
        list of strings, this argument can be either a single condition or
        a list of conditions. If the group_by argument is provided as a dict
        this argument is ignored.
    :description: A string providing a human-friendly description for the
        parameter.
    """
    _value: T | None
    def __init__(self,
                 name: str,
                 default: T | None=None,
                 units: str | None=None,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType|None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str|None=None):
        self.name = name
        separator = ": "
        if separator in name:
            raise ValueError(f"The provided name argument '{name}' contains the "
                             f"separator '{separator}'.")

        self._value = None
        if default is not None:
            self.value = default
        self.default = default
        self.units = units
        self.ui_class = ui_class
        self.group_name = group_name
        self._help_fields = [('units are', 'units'), 'default']

        self.group_by = {}
        if isinstance(group_by, dict):
            self.group_by = group_by
        elif isinstance(group_by, str):
            self.group_by = {group_by: group_condition}
        elif isinstance(group_by, (list, tuple)) and all(isinstance(e, str) for e in group_by):
            if isinstance(group_condition, (list, tuple)):
                self.group_by = {g: c for g, c in zip(group_by, group_condition)}
            else:
                self.group_by = {g: group_condition for g in group_by}
        elif group_by is not None:
            raise TypeError("The provided group_by argument is not valid, should be either a "
                            "string, a list of strings, or a dict with {string: condition} pairs.")

        if description is not None and not isinstance(description, str):
            raise TypeError("The provided description argument is not a string.")
        self.description = description
    
    @property
    def value(self) -> T | None:
        if self.is_set():
            return self._value
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value: Any) -> None:
        self._value = self.convert(value)

    @property
    def cli_args(self) -> tuple[str,str,str]:
        """ helper for command line interface parsing of parameters

        This property returns a list of data to help formatting a command line
        interface interpreter, the list is composed of the following elements:
        - index 0: default value
        - index 1: List of value to format an help string, that is either,
        the name of the fields to be documented or a tuple with (helps_string,
        field)
        - index 2: type
        """
        return (self.default, self._help_fields, self.convert)

    def is_set(self) -> bool:
        """ Returns True if the Parameter value is set
        """
        return self._value is not None

    def convert(self, value: Any) -> T | None:
        """ Convert user input to python data format

        Subclasses are expected to customize this method.
        Default implementation is the identity function

        :param value: value to be converted

        :return: converted value
        """

        return value

    def _cli_help_fields(self):
        message = f"{self.name}:\n"
        if (description := self.description) is not None:
            if not description.endswith("."):
                description += "."
            message += f"{description}\n"

        for field in self._help_fields:
            if isinstance(field, str):
                field = (f"{field} is", field)

            if (value := getattr(self, field[1], None)) is not None:
                prefix = field[0].capitalize()
                if isinstance(value, str):
                    value = f'"{value}"'

                message += f"\n{prefix} {value}."

        return message
    
    def __str__(self) -> str:
        return str(self._value) if self.is_set() else ''

    def __repr__(self) -> str:
        return "<{}(name={},value={},default={})>".format(
            self.__class__.__name__, self.name, self._value, self.default)


class IntegerParameter(Parameter[int]):
    """ :class:`.Parameter` sub-class that uses the integer type to
    store the value.

    :var value: The integer value of the parameter

    :param name: The parameter name
    :param units: The units of measure for the parameter
    :param minimum: The minimum allowed value (default: -1e9)
    :param maximum: The maximum allowed value (default: 1e9)
    :param default: The default integer value
    :param ui_class: A Qt class to use for the UI of this parameter
    :param step: int step size for parameter's UI spinbox. If None, spinbox will have step disabled
    """
    def __init__(self,
                 name: str,
                 default: int | None = None,
                 units: str | None = None,
                 minimum: int = int(-1e9),
                 maximum: int = int(1e9),
                 step: int | None = None,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        self.units = units
        self.minimum = int(minimum)
        self.maximum = int(maximum)
        self.step = int(step) if step else None
        super().__init__(name, default, units, ui_class, group_name, group_by, group_condition, description)
        self._help_fields.append('minimum')
        self._help_fields.append('maximum')

    def convert(self, value):
        if isinstance(value, str):
            value, _, units = value.strip().partition(" ")
            if units != "" and units != self.units:
                raise ValueError("Units included in string (%s) do not match"
                                 "the units of the IntegerParameter (%s)" % (units, self.units))

        try:
            value = int(value)
        except ValueError:
            raise ValueError("IntegerParameter given non-integer value of "
                             "type '%s'" % type(value))
        if value < self.minimum:
            raise ValueError("IntegerParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("IntegerParameter value is above the maximum")

        return value

    def __str__(self):
        if not self.is_set():
            return ''
        result = "%d" % self._value
        if self.units:
            result += " %s" % self.units
        return result

    def __repr__(self):
        return "<{}(name={},value={},units={},default={})>".format(
            self.__class__.__name__, self.name, self._value, self.units, self.default)


class BooleanParameter(Parameter[bool|np.bool]):
    """ :class:`.Parameter` sub-class that uses the boolean type to
    store the value.

    :var value: The boolean value of the parameter

    :param name: The parameter name
    :param default: The default boolean value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def convert(self, value):
        if isinstance(value, str):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                raise ValueError("BooleanParameter given string value of '%s'" % value)
        elif isinstance(value, (int, float)) and value in [0, 1]:
            value = bool(value)
        elif isinstance(value, bool):
            value = value
        elif isinstance(value, np.bool):
            value = value
        else:
            raise ValueError("BooleanParameter given non-boolean value of "
                             "type '%s'" % type(value))
        return value


class FloatParameter(Parameter[float]):
    """ :class:`.Parameter` sub-class that uses the floating point
    type to store the value.

    :var value: The floating point value of the parameter

    :param name: The parameter name
    :param units: The units of measure for the parameter
    :param minimum: The minimum allowed value (default: -1e9)
    :param maximum: The maximum allowed value (default: 1e9)
    :param decimals: The number of decimals considered (default: 15)
    :param default: The default floating point value
    :param ui_class: A Qt class to use for the UI of this parameter
    :param step: step size for parameter's UI spinbox. If None, spinbox will have step disabled
    """
    def __init__(self,
                 name: str,
                 default: float | None = None,
                 units: str | None = None,
                 minimum: float = -1e9,
                 maximum: float = 1e9,
                 decimals: int = 15,
                 step: int | None = None,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        self.minimum = minimum
        self.maximum = maximum
        self.decimals = decimals
        self.step = step
        super().__init__(name, default, units, ui_class, group_name, group_by, group_condition, description)
        self._help_fields.append(('decimals are', 'decimals'))
        
    def convert(self, value):
        if isinstance(value, str):
            value, _, units = value.strip().partition(" ")
            if units != "" and units != self.units:
                raise ValueError("Units included in string (%s) do not match"
                                 "the units of the FloatParameter (%s)" % (units, self.units))

        try:
            value = float(value)
        except ValueError:
            raise ValueError("FloatParameter given non-float value of "
                             "type '%s'" % type(value))
        if value < self.minimum:
            raise ValueError("FloatParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("FloatParameter value is above the maximum")

        return value

    def __str__(self):
        if not self.is_set():
            return ''
        result = "%g" % self._value
        if self.units:
            result += " %s" % self.units
        return result

    def __repr__(self):
        return "<{}(name={},value={},units={},default={})>".format(
            self.__class__.__name__, self.name, self._value, self.units, self.default)


class VectorParameter(Parameter[list[float]]):
    """ :class:`.Parameter` sub-class that stores the value in a
    vector format.

    :var value: The value of the parameter as a list of floating point numbers

    :param name: The parameter name
    :param length: The integer dimensions of the vector
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """
    def __init__(self,
                 name: str,
                 default: list[float] | None = None,
                 units: str | None = None,
                 length: int = 3,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        self._length = length
        self.units = units
        super().__init__(name, default, units, ui_class, group_name, group_by, group_condition, description)
        self._help_fields.append('_length')
        
    def convert(self, value):
        if isinstance(value, str):
            # strip units if included
            if self.units is not None and value.endswith(" " + self.units):
                value = value[:-len(self.units)].strip()

            # Strip initial and final brackets
            if (value[0] != '[') or (value[-1] != ']'):
                raise ValueError("VectorParameter must be passed a vector"
                                 " denoted by square brackets if initializing"
                                 " by string.")
            raw_list = value[1:-1].split(",")
        elif isinstance(value, (list, tuple, np.ndarray)):
            raw_list = value
        else:
            raise ValueError("VectorParameter given undesired value of "
                             "type '%s'" % type(value))
        if len(raw_list) != self._length:
            raise ValueError("VectorParameter given value of length "
                             "%d instead of %d" % (len(raw_list), self._length))
        try:
            value = [float(ve) for ve in raw_list]

        except ValueError:
            raise ValueError("VectorParameter given input '%s' that could "
                             "not be converted to floats." % str(value))

        return value

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
        return "<{}(name={},value={},units={},length={})>".format(
            self.__class__.__name__, self.name, self._value, self.units, self._length)


class ListParameter(Parameter[SupportsStr]):
    """ :class:`.Parameter` sub-class that stores the value as a list.
    String representation of choices must be unique.

    :param name: The parameter name
    :param choices: An explicit list of choices, which is disregarded if None
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """
    def __init__(self,
                 name: str,
                 choices: list[SupportsStr] | None = None,
                 default: SupportsStr | None = None,
                 units: str | None = None,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        if choices is not None:
            keys = [str(c) for c in choices]
            # check that string representation is unique
            if not len(keys) == len(set(keys)):
                raise ValueError(
                    "String representation of choices is not unique!")
            self._choices = {k: c for k, c in zip(keys, choices)}
        else:
            self._choices = None
        super().__init__(name, default, units, ui_class, group_name, group_by, group_condition, description)
        self._help_fields.append(('choices are', 'choices'))

    def convert(self, value: str) -> SupportsStr:
        if self._choices is None:
            raise ValueError("ListParameter cannot be set since "
                             "allowed choices are set to None.")

        # strip units if included
        if isinstance(value, str):
            if self.units is not None and value.endswith(" " + self.units):
                value = value[:-len(self.units)].strip()

        if str(value) in self._choices.keys():
            return self._choices[str(value)]
        else:
            raise ValueError("Invalid choice for parameter. "
                             "Must be one of %s" % str(self._choices))

    @property
    def choices(self) -> tuple[SupportsStr,...] | None:
        """ Returns an immutable iterable of choices, or None if not set. """
        if self._choices:
            return tuple(self._choices.values())
        return None

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
    #TODO: Rework this class and add an Input that overrides value.
    def __init__(self,
                 name: str,
                 default: list[float] | None = None,
                 units: str | None = None,
                 uncertainty_type: Literal["absolute", "relative", "percentage"] = "absolute",
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        self._utype = ListParameter("uncertainty type",
                                    choices=['absolute', 'relative', 'percentage'],
                                    default=None)
        self._utype.value = uncertainty_type
        super().__init__(name, default, units, 2, ui_class, group_name, group_by, group_condition, description)

    def convert(self, value):
        if isinstance(value, str):
            # strip units if included
            if self.units is not None and value.endswith(" " + self.units):
                value = value[:-len(self.units)].strip()

            # Strip initial and final brackets
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
            value = [float(ve) for ve in raw_list]
        except ValueError:
            raise ValueError("VectorParameter given input '%s' that could "
                             "not be converted to floats." % str(value))
        # Uncertainty must be non-negative
        value[1] = abs(value[1])

        return value

    @property
    def uncertainty_type(self)->Literal["absolute", "relative", "percentage"]:
        return self._utype.value

    @uncertainty_type.setter
    def uncertainty_type(
            self, uncertaintyType: Literal["absolute", "relative", "percentage"]
    ) -> None:
        oldType = self._utype.value
        self._utype.value = uncertaintyType
        newType = self._utype.value

        if self.is_set():
            # Convert uncertainty value to the new type
            if (oldType, newType) == ('absolute', 'relative'):
                self.value[1] = abs(self.value[1] / self.value[0])
            if (oldType, newType) == ('relative', 'absolute'):
                self.value[1] = abs(self.value[1] * self.value[0])
            if (oldType, newType) == ('relative', 'percentage'):
                self.value[1] = abs(self.value[1] * 100.0)
            if (oldType, newType) == ('percentage', 'relative'):
                self.value[1] = abs(self.value[1] * 0.01)
            if (oldType, newType) == ('percentage', 'absolute'):
                self.value[1] = abs(self.value[1] * self.value[0] * 0.01)
            if (oldType, newType) == ('absolute', 'percentage'):
                self.value[1] = abs(self.value[1] * 100.0 / self.value[0])

    def __str__(self):
        if not self.is_set():
            return ''
        result = f"{self.value[0]:g} +/- {self.value[1]:g}"
        if self.units:
            result += " %s" % self.units
        if self._utype.value is not None:
            result += " (%s)" % self._utype.value
        return result

    def __repr__(self):
        return "<{}(name={},value={},units={},uncertaintyType={})>".format(
            self.__class__.__name__, self.name, self._value, self.units, self._utype.value)

class RangeParameter(Parameter[np.ndarray]):
    def __init__(self,
                 name: str,
                 minimum: float = -1e9,
                 maximum: float = 1e9,
                 default: np.ndarray | None = None,
                 units: str | None = None,
                 ui_class: QtWidgets.QWidget | None = None,
                 group_name: str | None = None,
                 group_by: GroupByType | None = None,
                 group_condition: GroupConditionType = bool(True),
                 description: str | None = None):
        super().__init__(name, default, units, ui_class, group_name, group_by, group_condition, description)
        self.minimum = minimum
        self.maximum = maximum

    def convert(self, value: tuple[float, float, float|None, int|None]) -> np.ndarray | None:
        pass

class ParameterGroup:
    
    """def __set_name__(self, owner, name):
        for var_name, parameter in self.parameters.items():
            setattr(owner, var_name, parameter)
        setattr(owner, name, self.value)"""

    def __init__(self, name: str, **parameters: Parameter) -> None:
        self.name = name
        self.group_by = {}
        self.parameters = parameters
        self.param_names = list(self.parameters.keys())
        for _, parameter in self.parameters.items():
            assert issubclass(parameter.__class__, Parameter)
            parameter.group_name = name

    def is_set(self):
        params_set = [param.is_set() for _, param in self.parameters.items()]
        return all(params_set)
        
    @property
    def value(self) -> list:
        return self.serialize()

    @value.setter
    def value(self, value_list: list):
        self.deserialize(value_list)

    def serialize(self):
        """Act on the parameter values and specify what the group should return.
           By default it returns a list of the parameter values.
           Modify in subclasses.
        """
        return [parameter.value for (_, parameter) in self.parameters.items()]

    def deserialize(self, value_list: list):
        for value, (_, parameter) in zip(value_list, self.parameters.items()):
            parameter.value = value

        
class RangeParameterGroup(ParameterGroup):

    def __init__(self, name: str, start_kwargs = {}, stop_kwargs = {}, no_step_kwargs = {}) -> None:
        self.var_name = name.lower().replace(" ", "_")
        parameters = {
            f"{self.var_name}_start": FloatParameter("Start",default=0, **start_kwargs),
            f"{self.var_name}_stop": FloatParameter("Stop",default=1, **stop_kwargs),
            f"{self.var_name}_no_steps": IntegerParameter("Number of steps",default=50, **no_step_kwargs)
        }
        super().__init__(name, **parameters)

    def serialize(self):
        start, stop, no_steps = super().serialize()
        return np.linspace(start, stop, no_steps)

    def deserialize(self, value_list: list):
        self.parameters[f"{self.var_name}_start"].value = value_list[0]
        self.parameters[f"{self.var_name}_stop"].value = value_list[-1]
        self.parameters[f"{self.var_name}_no_steps"].value = len(value_list)
        
class Measurable:
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


class Metadata(object):
    """ Encapsulates the information for metadata of the experiment with
    information about the name, the fget function and the units, if supplied.
    If no fget function is specified, the value property will return the
    latest set value of the parameter (or default if never set).

    :var value: The value of the parameter. This returns (if a value is set)
        the value obtained from the `fget` (after evaluation) or a manually
        set value. Returns `None` if no value has been set

    :param name: The parameter name
    :param fget: The parameter fget function; can be provided as a callable,
        or as a string, in which case it is assumed to be the name of a
        method or attribute of the `Procedure` class in which the Metadata is
        defined. Passing a string also allows for nested attributes by separating
        them with a period (e.g. to access an attribute or method of an
        instrument) where only the last attribute can be a method.
    :param units: The parameter units
    :param default: The default value, in case no value is assigned or if no
        fget method is provided
    :param fmt: A string used to format the value upon writing it to a file.
        Default is "%s"

    """
    def __init__(self, name, fget=None, units=None, default=None, fmt="%s"):
        self.name = name
        self.units = units

        self._value = default
        self.fget = fget
        self.fmt = fmt

        self.evaluated = False

    @property
    def value(self):
        if self.is_set():
            return self._value
        else:
            raise ValueError("Metadata value is not set")

    def is_set(self):
        """ Returns True if the Parameter value is set
        """
        return self._value is not None

    def evaluate(self, parent=None, new_value=None):
        if new_value is not None and self.fget is not None:
            raise ValueError("Metadata with a defined fget method"
                             " cannot be manually assigned a value")
        elif new_value is not None:
            self._value = new_value
        elif self.fget is not None:
            self._value = self.eval_fget(parent)

        self.evaluated = True
        return self.value

    def eval_fget(self, parent):
        fget = self.fget
        if isinstance(fget, str):
            obj = parent
            for obj_name in fget.split('.'):
                obj = getattr(obj, obj_name)
            fget = obj

        if callable(fget):
            return fget()
        else:
            return fget

    def __str__(self):
        result = self.fmt % self.value

        if self.units is not None:
            result += " %s" % self.units

        return result
