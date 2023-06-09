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

import logging
import sys
import inspect
from copy import deepcopy
from importlib.machinery import SourceFileLoader
import re
from pint import UndefinedUnitError

from .parameters import Parameter, Measurable, Metadata
from pymeasure.units import ureg

log = logging.getLogger()
log.addHandler(logging.NullHandler())


class Procedure:
    """Provides the base class of a procedure to organize the experiment
    execution. Procedures should be run by Workers to ensure that
    asynchronous execution is properly managed.

    .. code-block:: python

        procedure = Procedure()
        results = Results(procedure, data_filename)
        worker = Worker(results, port)
        worker.start()

    Inheriting classes should define the startup, execute, and shutdown
    methods as needed. The shutdown method is called even with a
    software exception or abort event during the execute method.

    If keyword arguments are provided, they are added to the object as
    attributes.
    """

    DATA_COLUMNS = []
    MEASURE = {}
    FINISHED, FAILED, ABORTED, QUEUED, RUNNING = 0, 1, 2, 3, 4
    STATUS_STRINGS = {
        FINISHED: 'Finished', FAILED: 'Failed',
        ABORTED: 'Aborted', QUEUED: 'Queued',
        RUNNING: 'Running'
    }

    _parameters = {}

    def __init__(self, **kwargs):
        self.status = Procedure.QUEUED
        self._update_parameters()
        self._update_metadata()
        for key in kwargs:
            if key in self._parameters.keys():
                setattr(self, key, kwargs[key])
                log.info(f'Setting parameter {key} to {kwargs[key]}')
        self.gen_measurement()

    @staticmethod
    def parse_columns(columns):
        """Get columns with any units in parentheses.
        For each column, if there are matching parentheses containing text
        with no spaces, parse the value between the parentheses as a Pint unit. For example,
        "Source Voltage (V)" will be parsed and matched to :code:`Unit('volt')`.
        Raises an error if a parsed value is undefined in Pint unit registry.
        Return a dictionary of matched columns with their units.

        :param columns: List of columns to be parsed.
        :type record: dict
        :return: Dictionary of columns with Pint units.
        """
        units_pattern = r"\((?P<units>[\w/\(\)\*\t]+)\)"
        units = {}
        for column in columns:
            match = re.search(units_pattern, column)
            if match:
                try:
                    units[column] = ureg.Quantity(match.groupdict()['units']).units
                except UndefinedUnitError:
                    raise ValueError(
                        f"Column \"{column}\" with unit \"{match.groupdict()['units']}\""
                        " is not defined in Pint registry. Check procedure "
                        "DATA_COLUMNS contains valid Pint units.")
        return units

    def gen_measurement(self):
        """Create MEASURE and DATA_COLUMNS variables for get_datapoint method."""
        # TODO: Refactor measurable-s implementation to be consistent with parameters

        self.MEASURE = {}
        for item, parameter in inspect.getmembers(self.__class__):
            if isinstance(parameter, Measurable):
                if parameter.measure:
                    self.MEASURE.update({parameter.name: item})

        if not self.DATA_COLUMNS:
            self.DATA_COLUMNS = Measurable.DATA_COLUMNS

        # Validate DATA_COLUMNS fit pymeasure column header format
        self.parse_columns(self.DATA_COLUMNS)

    def get_datapoint(self):
        data = {key: getattr(self, self.MEASURE[key]).value for key in self.MEASURE}
        return data

    def measure(self):
        data = self.get_datapoint()
        log.debug("Produced numbers: %s" % data)
        self.emit('results', data)

    def _update_parameters(self):
        """ Collects all the Parameter objects for the procedure and stores
        them in a meta dictionary so that the actual values can be set in
        their stead
        """
        if not self._parameters:
            self._parameters = {}
        for item, parameter in inspect.getmembers(self.__class__):
            if isinstance(parameter, Parameter):
                self._parameters[item] = deepcopy(parameter)
                if parameter.is_set():
                    setattr(self, item, parameter.value)
                else:
                    setattr(self, item, None)

    def parameters_are_set(self):
        """ Returns True if all parameters are set """
        for name, parameter in self._parameters.items():
            if getattr(self, name) is None:
                return False
        return True

    def check_parameters(self):
        """ Raises an exception if any parameter is missing before calling
        the associated function. Ensures that each value can be set and
        got, which should cast it into the right format. Used as a decorator
        @check_parameters on the startup method
        """
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is None:
                raise NameError("Missing {} '{}' in {}".format(
                    parameter.__class__, name, self.__class__))

    def parameter_values(self):
        """ Returns a dictionary of all the Parameter values and grabs any
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                setattr(self, name, parameter.value)
                result[name] = parameter.value
            else:
                result[name] = None
        return result

    def parameter_objects(self):
        """ Returns a dictionary of all the Parameter objects and grabs any
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                setattr(self, name, parameter.value)
            result[name] = parameter
        return result

    def refresh_parameters(self):
        """ Enforces that all the parameters are re-cast and updated in the meta
        dictionary
        """
        for name, parameter in self._parameters.items():
            value = getattr(self, name)
            parameter.value = value
            setattr(self, name, parameter.value)

    def set_parameters(self, parameters, except_missing=True):
        """ Sets a dictionary of parameters and raises an exception if additional
        parameters are present if except_missing is True
        """
        for name, value in parameters.items():
            if name in self._parameters:
                self._parameters[name].value = value
                setattr(self, name, self._parameters[name].value)
            else:
                if except_missing:
                    raise NameError("Parameter '{}' does not belong to '{}'".format(
                        name, repr(self)))

    def _update_metadata(self):
        """ Collects all the Metadata objects for the procedure and stores
        them in a meta dictionary so that the actual values can be set and used
        in their stead
        """
        self._metadata = {}

        for item, metadata in inspect.getmembers(self.__class__):
            if isinstance(metadata, Metadata):
                self._metadata[item] = deepcopy(metadata)

                if metadata.is_set():
                    setattr(self, item, metadata.value)
                else:
                    setattr(self, item, None)

    def evaluate_metadata(self):
        """ Evaluates all Metadata objects, fixing their values to the current value
        """
        for item, metadata in self._metadata.items():
            # Evaluate the metadata, fixing its value
            value = metadata.evaluate(parent=self, new_value=getattr(self, item))

            # Make the value of the metadata easily accessible
            setattr(self, item, value)

    def metadata_objects(self):
        """ Returns a dictionary of all the Metadata objects
        """
        return self._metadata

    def startup(self):
        """ Executes the commands needed at the start-up of the measurement
        """
        pass

    def execute(self):
        """ Preforms the commands needed for the measurement itself. During
        execution the shutdown method will always be run following this method.
        This includes when Exceptions are raised.
        """
        pass

    def shutdown(self):
        """ Executes the commands necessary to shut down the instruments
        and leave them in a safe state. This method is always run at the end.
        """
        pass

    def emit(self, topic, record):
        raise NotImplementedError('should be monkey patched by a worker')

    def should_stop(self):
        raise NotImplementedError('should be monkey patched by a worker')

    def get_estimates(self):
        """ Function that returns estimates that are to be displayed by
        the EstimatorWidget. Must be reimplemented by subclasses. Should
        return an int or float representing the duration in seconds, or
        a list with a tuple for each estimate. The tuple should consists
        of two strings: the first will be used as the label of the
        estimate, the second as the displayed estimate.
        """
        raise NotImplementedError('Must be reimplemented by subclasses')

    def __str__(self):
        result = repr(self) + "\n"
        for parameter in self._parameters.items():
            result += str(parameter)
        return result

    def __repr__(self):
        return "<{}(status={},parameters_are_set={})>".format(
            self.__class__.__name__, self.STATUS_STRINGS[self.status],
            self.parameters_are_set()
        )


class UnknownProcedure(Procedure):
    """ Handles the case when a :class:`.Procedure` object can not be imported
    during loading in the :class:`.Results` class
    """

    def __init__(self, parameters):
        super().__init__()
        self._parameters = parameters

    def startup(self):
        raise NotImplementedError("UnknownProcedure can not be run")


class ProcedureWrapper:

    def __init__(self, procedure):
        self.procedure = procedure

    def __getstate__(self):
        # Get all information needed to reconstruct procedure
        self._parameters = self.procedure.parameter_values()
        self._class = self.procedure.__class__.__name__
        module = sys.modules[self.procedure.__module__]
        self._package = module.__package__
        self._module = module.__name__
        self._file = module.__file__

        state = self.__dict__.copy()
        del state['procedure']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        # Restore the procedure
        module = SourceFileLoader(self._module, self._file).load_module()
        cls = getattr(module, self._class)

        self.procedure = cls()
        self.procedure.set_parameters(self._parameters)
        self.procedure.refresh_parameters()

        del self._parameters
        del self._class
        del self._package
        del self._module
        del self._file
