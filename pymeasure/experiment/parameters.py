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

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Generic, TypeVar, overload

import numpy as np

T = TypeVar('T')


class Parameter(Generic[T]):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and units if supplied.

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

    _attr_name: str = ""

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr_name = name

    @overload
    def __get__(self, obj: None, objtype: type): ...

    @overload
    def __get__(self, obj: object, objtype: type) -> T: ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        param_values = getattr(obj, '_param_values', None)
        if param_values is not None and self._attr_name in param_values:
            return param_values[self._attr_name]
        parameters = getattr(obj, '_parameters', None)
        if parameters is not None and self._attr_name in parameters:
            param = parameters[self._attr_name]
            if param.is_set():
                return param.value
        return None

    def __set__(self, obj: object, value: T | None) -> None:
        param_values = getattr(obj, '_param_values', None)
        if param_values is None:
            obj._param_values = {}
            param_values = obj._param_values
        param_values[self._attr_name] = value

    def __init__(
        self,
        name: str,
        default: T | None = None,
        ui_class: type | None = None,
        group_by: str | list[str] | tuple[str, ...] | dict[str, object] | None = None,
        group_condition: object = True,
        description: str | None = None,
    ):
        self.name: str = name
        separator = ": "
        if separator in name:
            raise ValueError(f"The provided name argument '{name}' contains the "
                             f"separator '{separator}'.")

        self._value: T | None = None
        if default is not None:
            self.value = default
        self.default: T | None = default
        self.ui_class: type | None = ui_class
        self._help_fields: list[tuple[str, str] | str] = [('units are', 'units'), 'default']

        self.group_by: dict[str, object] = {}
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
        self.description: str | None = description

    @property
    def value(self) -> T:
        if self.is_set():
            return self._value  # type: ignore[reportReturnType]
        else:
            raise ValueError("Parameter value is not set")

    @value.setter
    def value(self, value: T) -> None:
        self._value = self.convert(value)

    @property
    def cli_args(self) -> tuple[T | None, list[tuple[str, str] | str], Callable[[Any], T]]:
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

    def convert(self, value: T) -> T:
        """ Convert user input to python data format

        Subclasses are expected to customize this method.
        Default implementation is the identity function

        :param value: value to be converted

        :return: converted value
        """

        return value

    def _cli_help_fields(self) -> str:
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
        return (f"<{self.__class__.__name__}(name={self.name},value={self._value},"
                f"default={self.default})>")


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

    def __init__(
        self,
        name: str,
        units: str | None = None,
        minimum: int = -(10**9),
        maximum: int = 10**9,
        step: int | None = None,
        **kwargs,
    ):
        self.units: str | None = units
        self.minimum: int = int(minimum)
        self.maximum: int = int(maximum)
        super().__init__(name, **kwargs)
        self.step: int | None = int(step) if step else None
        self._help_fields.append('minimum')
        self._help_fields.append('maximum')

    def convert(self, value: int | float | bool | str) -> int:
        if isinstance(value, str):
            value, _, units = value.strip().partition(" ")
            if units != "" and units != self.units:
                raise ValueError(f"Units included in string ({units}) do not match "
                                 f"the units of the IntegerParameter ({self.units})")

        try:
            value = int(value)
        except ValueError:
            raise ValueError("IntegerParameter given non-integer value of "
                             f"type '{type(value)}'")
        if value < self.minimum:
            raise ValueError("IntegerParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("IntegerParameter value is above the maximum")

        return value

    def __index__(self) -> int:
        return int(self.value)

    def __str__(self) -> str:
        if not self.is_set():
            return ''
        result = f"{self._value:d}"
        if self.units:
            result += f" {self.units}"
        return result

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__}(name={self.name},value={self._value},"
                f"units={self.units},default={self.default})>")


class BooleanParameter(Parameter[bool]):
    """ :class:`.Parameter` sub-class that uses the boolean type to
    store the value.

    :var value: The boolean value of the parameter

    :param name: The parameter name
    :param default: The default boolean value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def convert(self, value: bool | int | float | str | np.bool_) -> bool:
        if isinstance(value, str):
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            else:
                raise ValueError(f"BooleanParameter given string value of '{value}'")
        elif isinstance(value, (int, float)) and value in [0, 1]:
            value = bool(value)
        elif isinstance(value, bool):
            value = value
        elif isinstance(value, np.bool_):
            value = bool(value)
        else:
            raise ValueError("BooleanParameter given non-boolean value of "
                             f"type '{type(value)}'")
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

    def __init__(
        self,
        name: str,
        units: str | None = None,
        minimum: float = -1e9,
        maximum: float = 1e9,
        decimals: int = 15,
        step: float | None = None,
        **kwargs,
    ):
        self.units: str | None = units
        self.minimum: float = minimum
        self.maximum: float = maximum
        super().__init__(name, **kwargs)
        self.decimals: int = decimals
        self.step: float | None = step
        self._help_fields.append(('decimals are', 'decimals'))

    def convert(self, value: float | int | bool | str) -> float:
        if isinstance(value, str):
            value, _, units = value.strip().partition(" ")
            if units != "" and units != self.units:
                raise ValueError(f"Units included in string ({units}) do not match "
                                 f"the units of the FloatParameter ({self.units})")

        try:
            value = float(value)
        except ValueError:
            raise ValueError("FloatParameter given non-float value of "
                             f"type '{type(value)}'")
        if value < self.minimum:
            raise ValueError("FloatParameter value is below the minimum")
        elif value > self.maximum:
            raise ValueError("FloatParameter value is above the maximum")

        return value

    def __float__(self) -> float:
        return float(self.value)

    def __str__(self) -> str:
        if not self.is_set():
            return ''
        result = f"{self._value:g}"
        if self.units:
            result += f" {self.units}"
        return result

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__}(name={self.name},value={self._value},"
                f"units={self.units},default={self.default})>")


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

    def __init__(self, name: str, length: int = 3, units: str | None = None, **kwargs):
        self._length: int = length
        self.units: str | None = units
        super().__init__(name, **kwargs)
        self._help_fields.append(("length is", "_length"))

    def convert(self, value: list[float] | tuple[float, ...] | np.ndarray | str) -> list[float]:
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
                             f"type '{type(value)}'")
        if len(raw_list) != self._length:
            raise ValueError("VectorParameter given value of length "
                             f"{len(raw_list)} instead of {self._length}")
        try:
            value = [float(ve) for ve in raw_list]

        except ValueError:
            raise ValueError(f"VectorParameter given input '{str(value)}' that could "
                             "not be converted to floats.")

        return value

    def __str__(self) -> str:
        """If we eliminate spaces within the list __repr__ then the
        csv parser will interpret it as a single value."""
        if not self.is_set():
            return ''
        result = "".join(repr(self.value).split())
        if self.units:
            result += f" {self.units}"
        return result

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__}(name={self.name},value={self._value},"
                f"units={self.units},length={self._length})>")


class ListParameter(Parameter[object]):
    """:class:`.Parameter` sub-class that stores the value as a list.
    String representation of choices must be unique.

    :param name: The parameter name
    :param choices: An explicit list of choices, which is disregarded if None
    :param units: The units of measure for the parameter
    :param default: The default value
    :param ui_class: A Qt class to use for the UI of this parameter
    """

    def __init__(
        self,
        name: str,
        choices: list[object] | tuple[object, ...] | None = None,
        units: str | None = None,
        **kwargs,
    ):
        self.units: str | None = units
        if choices is not None:
            keys = [str(c) for c in choices]
            # check that string representation is unique
            if not len(keys) == len(set(keys)):
                raise ValueError(
                    "String representation of choices is not unique!")
            self._choices: dict[str, object] | None = {k: c for k, c in zip(keys, choices)}
        else:
            self._choices = None
        super().__init__(name, **kwargs)
        self._help_fields.append(('choices are', 'choices'))

    def convert(self, value: object) -> object:
        if self._choices is None:
            raise ValueError("ListParameter cannot be set since "
                             "allowed choices are set to None.")

        # strip units if included
        if isinstance(value, str):
            if self.units is not None and value.endswith(" " + self.units):
                value = value[:-len(self.units)].strip()

        if str(value) in self._choices.keys():
            value = self._choices[str(value)]
        else:
            raise ValueError("Invalid choice for parameter. "
                             f"Must be one of {str(self._choices)}")

        return value

    @property
    def choices(self) -> tuple[object, ...] | None:
        """ Returns an immutable iterable of choices, or None if not set. """
        if self._choices is None:
            return None
        return tuple(self._choices.values())


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

    def __init__(self, name: str, uncertaintyType: str = "absolute", **kwargs):
        super().__init__(name, length=2, **kwargs)
        self._utype = ListParameter("uncertainty type",
                                    choices=['absolute', 'relative', 'percentage'],
                                    default=None)
        self._utype.value = uncertaintyType

    def convert(self, value: list[float] | tuple[float, ...] | np.ndarray | str) -> list[float]:
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
                             f"type '{type(value)}'")
        if len(raw_list) != self._length:
            raise ValueError("VectorParameter given value of length "
                             f"{len(raw_list)} instead of {self._length}")
        try:
            value = [float(ve) for ve in raw_list]
        except ValueError:
            raise ValueError(f"VectorParameter given input '{str(value)}' that could "
                             "not be converted to floats.")
        # Uncertainty must be non-negative
        value[1] = abs(value[1])

        return value

    @property
    def uncertainty_type(self) -> str:
        return self._utype.value  # type: ignore[reportReturnType]

    @uncertainty_type.setter
    def uncertainty_type(self, uncertaintyType: str) -> None:
        oldType = self._utype.value
        self._utype.value = uncertaintyType
        newType = self._utype.value

        if self.is_set():
            assert self._value is not None
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

    def __str__(self) -> str:
        if not self.is_set():
            return ''
        assert self._value is not None
        result = f"{self._value[0]:g} +/- {self._value[1]:g}"
        if self.units:
            result += f" {self.units}"
        if self._utype.value is not None:
            result += f" ({self._utype.value})"
        return result

    def __repr__(self) -> str:
        return (f"<{self.__class__.__name__}(name={self.name},value={self._value},"
                f"units={self.units},uncertaintyType={self._utype.value})>")


class Measurable(Generic[T]):
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
    DATA_COLUMNS: list[str] = []

    def __init__(
        self,
        name: str,
        fget: Callable[[], T] | None = None,
        units: str | None = None,
        measure: bool = True,
        default: T | None = None,
        **kwargs,
    ):
        self.name: str = name
        self.units: str | None = units
        self.measure: bool = measure
        self._value: T | None = default
        self.fget: Callable[[], T] | None = fget
        if fget is not None:
            self._value = fget()
        Measurable.DATA_COLUMNS.append(name)

    @property
    def value(self) -> T:
        if self.fget is not None:
            self._value = self.fget()
        return self._value  # type: ignore[reportReturnType]

    @value.setter
    def value(self, value: T) -> None:
        self._value = value


class Metadata(Generic[T]):
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

    _attr_name: str = ""

    def __init__(
        self,
        name: str,
        fget: Callable[[], T] | str | None = None,
        units: str | None = None,
        default: T | None = None,
        fmt: str = "%s",
    ):
        self.name: str = name
        self.units: str | None = units
        self._value: T | None = default
        self.fget: Callable[[], T] | str | None = fget
        self.fmt: str = fmt
        self.evaluated: bool = False

    def __set_name__(self, owner: type, name: str) -> None:
        self._attr_name = name

    @overload
    def __get__(self, obj: None, objtype: type) -> Metadata[T]: ...

    @overload
    def __get__(self, obj: object, objtype: type) -> T | None: ...

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        metadata_values = getattr(obj, '_metadata_values', None)
        if metadata_values is not None and self._attr_name in metadata_values:
            return metadata_values[self._attr_name]
        metadata = getattr(obj, '_metadata', None)
        if metadata is not None and self._attr_name in metadata:
            md = metadata[self._attr_name]
            if md.is_set():
                return md.value
        return None

    def __set__(self, obj: object, value: T | None) -> None:
        metadata_values = getattr(obj, '_metadata_values', None)
        if metadata_values is None:
            obj._metadata_values = {}
            metadata_values = obj._metadata_values
        metadata_values[self._attr_name] = value

    @property
    def value(self) -> T:
        if self.is_set():
            return self._value  # type: ignore[reportReturnType]
        else:
            raise ValueError("Metadata value is not set")

    def is_set(self) -> bool:
        """ Returns True if the Parameter value is set
        """
        return self._value is not None

    def evaluate(self, parent: object | None = None, new_value: T | None = None) -> T:
        if new_value is not None and self.fget is not None:
            raise ValueError("Metadata with a defined fget method"
                             " cannot be manually assigned a value")
        elif new_value is not None:
            self._value = new_value
        elif self.fget is not None:
            self._value = self.eval_fget(parent)

        self.evaluated = True
        return self.value

    def eval_fget(self, parent: object | None) -> T:
        fget = self.fget
        if isinstance(fget, str):
            obj = parent
            for obj_name in fget.split('.'):
                obj = getattr(obj, obj_name)
            fget = obj

        if callable(fget):
            return fget()  # type: ignore[reportReturnType]
        else:
            return fget  # type: ignore[reportReturnType]

    def __str__(self) -> str:
        result = self.fmt % self.value

        if self.units is not None:
            result += f" {self.units}"

        return result
