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

import copy
import argparse

try:
    import progressbar
    # Check that progressbar is progressbar2
    progressbar.streams
except (AttributeError, ImportError):
    progressbar = None
from .Qt import QtCore
import signal
from ..log import console_log

from .browser import BaseBrowserItem
from .manager import BaseManager, Experiment

from ..experiment import Results, Procedure, unique_filename

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class ConsoleBrowserItem(BaseBrowserItem):

    def __init__(self, progress_bar):
        self.bar = progress_bar

    def setStatus(self, status):
        if self.bar:
            self.bar.update(status=self.status_label[status])

    def setProgress(self, progress):
        if self.bar:
            self.bar.update(progress)


class ConsoleArgumentParser(argparse.ArgumentParser):
    special_options = {
        "no-progressbar":   {"default": False,
                             "desc": "Disable progressbar",
                             "help_fields": ["default"],
                             "action": 'store_true'},
        "log-level":        {"default": 'INFO',
                             "choices": list(logging._nameToLevel.keys()),
                             "desc": "Set log level (logging module values)",
                             "help_fields": ["default"]},
        "sequence-file":    {"default": None,
                             "desc": "Sequencer file as used/defined by the sequencer widget to "
                                     "execute a sequence of measurements",
                             "help_fields": ["default"]},
        "result-directory": {"default": ".",
                             "desc": "Directory where experiment's result are saved",
                             "help_fields": ["default"]},
        "result-file":      {"default": None,
                             "desc": "File name where results are stored; this string is handled "
                                     "by the `unique_filename` function and hence allows for "
                                     "filling in parameter values and is suffixed by the date "
                                     "(`YYYY-MM-DD`) and an index number",
                             "help_fields": ["default"]},
        "use-result-file":  {"default": None,
                             "desc": "Result file to retrieve params from",
                             "help_fields": ["default"]},
    }

    def __init__(self, procedure_class, **kwargs):
        super().__init__(**kwargs)
        self.procedure_class = procedure_class
        self.setup_parser()

    def setup_parser(self):
        """ Setup command line arguments parsing from parameters information """

        self.procedure = self.procedure_class()
        parameter_objects = self.procedure.parameter_objects()

        special_options = copy.deepcopy(self.special_options)
        special_opts_group = self.add_argument_group("Common options")
        for option, kwargs in special_options.items():
            help_fields = [('units are', 'units')] + kwargs['help_fields']
            desc = kwargs['desc']
            kwargs['help'] = self._cli_help_fields(desc, kwargs, help_fields)
            del kwargs['help_fields']
            del kwargs['desc']
            special_opts_group.add_argument("--" + option, **kwargs)

        experiment_opts_group = self.add_argument_group("Experiment options")
        for name in parameter_objects:
            if name in special_options:
                raise Exception(f"Experiment option {name} " +
                                "is already defined as common options")
            kwargs = {}
            parameter = parameter_objects[name]
            default, help_fields, _type = parameter.cli_args
            kwargs['help'] = self._cli_help_fields(parameter.name, parameter, help_fields)
            kwargs['default'] = default
            if _type is not None:
                kwargs['type'] = _type
            experiment_opts_group.add_argument("--" + name, **kwargs)

    @staticmethod
    def _cli_help_fields(name, inst, help_fields):
        def hasattr_dict(inst, key):
            return key in inst

        def getattr_dict(inst, key):
            return inst[key]

        if isinstance(inst, dict):
            hasattribute = hasattr_dict
            getattribute = getattr_dict
        else:
            hasattribute = hasattr
            getattribute = getattr

        message = name
        for field in help_fields:
            if isinstance(field, str):
                field = ["{} is".format(field), field]

            if hasattribute(inst, field[1]) and getattribute(inst, field[1]) is not None:
                prefix = field[0]
                value = getattribute(inst, field[1])
                message += ", {} {}".format(prefix, value)

        message = message.replace("%", "%%")
        return message


class ManagedConsole(QtCore.QCoreApplication):
    """
    Base class for console experiment management.

    Parameters for :code:`__init__` constructor.

    :param procedure_class: procedure class describing the experiment
            (see :class:`~pymeasure.experiment.procedure.Procedure`)
    :param log_channel: :code:`logging.Logger` instance to use for logging output
    :param log_level: logging level
    """

    def __init__(self,
                 procedure_class,
                 log_channel='',
                 log_level=logging.INFO,
                 ):

        super().__init__([])
        self.procedure_class = procedure_class
        self.log_channel = log_channel
        self.log = logging.getLogger(log_channel)
        self.log_level = log_level
        log.setLevel(log_level)
        self.log.setLevel(log_level)

        # Check if the get_estimates function is reimplemented
        self.use_estimator = not self.procedure_class.get_estimates == Procedure.get_estimates
        if self.use_estimator:
            log.warning("Estimator not yet implemented")

        # Handle Ctrl+C nicely
        signal.signal(signal.SIGINT, lambda sig, _: self.abort())

        # Parse command line arguments
        parser = ConsoleArgumentParser(procedure_class)
        args = vars(parser.parse_args())

        self.directory = args['result_directory']
        self.filename = args['result_file']
        try:
            log_level = int(args['log_level'])
        except ValueError:
            # Ignore and assume it is a valid level string
            log_level = args['log_level']
        self.log_level = log_level
        log.setLevel(self.log_level)
        self.log.setLevel(self.log_level)

        if args['sequence_file'] is not None:
            raise NotImplementedError("Sequencer not yet implemented")

        # Set procedure parameters
        self.parameter_values = {}

        if args['use_result_file'] is not None:
            # Special case set parameters from log file
            results = Results.load(args['use_result_file'])
            for name in results.parameters:
                self.parameter_values[name] = results.parameters[name].value
        else:
            for name in args:
                opt_name = name.replace("_", "-")
                if not (opt_name in parser.special_options):
                    self.parameter_values[name] = args[name]

        if progressbar and not args['no_progressbar']:
            progressbar.streams.wrap_stderr()
            self.bar = progressbar.ProgressBar(max_value=100,
                                               prefix='{variables.status}: ',
                                               variables={'status': "Unknown"})
        else:
            self.bar = None
        scribe = console_log(self.log, level=self.log_level)
        scribe.start()

        # Setup Manager
        self.manager = BaseManager(
            log_level=self.log_level,
            parent=self)
        self.manager.abort_returned.connect(self._terminate)
        self.manager.failed.connect(self._terminate)
        self.manager.finished.connect(self._terminate)
        self.manager.log.connect(self.log.handle)

    def get_filename(self, directory, procedure=None):
        """ Return filename for saving results file

        :param directory: directory of the returned filename.

        """
        if self.filename is not None:
            return unique_filename(directory, prefix=self.filename, procedure=procedure)
        else:
            return unique_filename(directory)

    def queue(self):
        procedure = self.procedure_class()
        procedure.set_parameters(self.parameter_values)
        filename = self.get_filename(self.directory, procedure)
        results = Results(procedure, filename)
        experiment = self.new_experiment(results)

        self.manager.queue(experiment)

    def _terminate(self):
        if not self.manager.experiments.has_next():
            self.quit()

    def abort(self):
        """ Aborts the currently running Experiment, but raises an exception if
        there is no running experiment
        """
        self.manager.abort()

    def new_experiment(self, results):
        browser_item = ConsoleBrowserItem(self.bar)
        return Experiment(results, browser_item=browser_item)

    def exec(self):
        self.queue()
        super().exec()
