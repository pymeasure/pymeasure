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

import logging
import sys
import inspect
from copy import deepcopy
from importlib.machinery import SourceFileLoader

from .parameters import Parameter, Measurable
from .procedure import Procedure

log = logging.getLogger()
log.addHandler(logging.NullHandler())


class Routine:
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

    FINISHED, FAILED, ABORTED, QUEUED, RUNNING = 0, 1, 2, 3, 4
    STATUS_STRINGS = {
        FINISHED: 'Finished', FAILED: 'Failed',
        ABORTED: 'Aborted', QUEUED: 'Queued',
        RUNNING: 'Running'
    }

    _parameters = {}

    def __init__(self, **kwargs):
        self.status = Procedure.QUEUED
        for key in kwargs:
            if key in self._parameters.keys():
                setattr(self, key, kwargs[key])
                log.info(f'Setting parameter {key} to {kwargs[key]}')


    def startup(self):
        """ Executes the commands needed at the start-up of the measurement
        """
        pass

    def execute(self):
        """ Preforms the commands needed for the measurement itself. During
        execution the shutdown method will always be run following this method.
        This includes when Exceptions are raised.
        """
        log.info('Performing Analysis of data')
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
        )


