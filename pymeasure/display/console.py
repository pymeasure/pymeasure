#
# This file is part of the PyMeasure package.
#
# Copyright (c) 2013-2021 PyMeasure Developers
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

import os
import subprocess, platform
import argparse

from ..log import console_log

from ..experiment import Results, Procedure, Worker, unique_filename

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

class ManagedConsole(object):
    """
    Base class for console experiment management .

    Parameters for :code:`__init__` constructor.

    :param procedure_class: procedure class describing the experiment (see :class:`~pymeasure.experiment.procedure.Procedure`)
    :param inputs: list of :class:`~pymeasure.experiment.parameters.Parameter` instance variable names, which the display will generate graphical fields for
    :param log_channel: :code:`logging.Logger` instance to use for logging output
    :param log_level: logging level
    :param sequence_file: simple text file to quickly load a pre-defined sequence with the :code:`Load sequence` button
    :param directory_input: specify, if present, where the experiment's result will be saved.
    """
    special_options = {
        "log-level":       {"default" :logging.INFO, "desc": "Set log level", "help_fields": ["default"]},
        "sequence-file":   {"default" :None, "desc": "Sequencer file", "help_fields": ["default"]},
        "directory-input": {"default" :False, "desc": "Log directory", "help_fields": ["default"]},
        "use-log-file":    {"default" :None, "help_fields": ["default"], "desc": "File to retrieve params from"},
    }
         
    def __init__(self,
                 procedure_class,
                 inputs=(),
                 log_channel='',
                 log_level=logging.INFO,
                 sequence_file=None,
                 directory_input=False,
                 ):

        super().__init__()
        self.procedure_class = procedure_class
        self.inputs = inputs
        self.sequence_file = sequence_file
        self.directory_input = directory_input
        self.log = logging.getLogger(log_channel)
        self.log_level = log_level
        log.setLevel(log_level)
        self.log.setLevel(log_level)

        # Check if the get_estimates function is reimplemented
        self.use_estimator = not self.procedure_class.get_estimates == Procedure.get_estimates
        self.parser = argparse.ArgumentParser()
        self._setup_parser()

    def _cli_help_fields(self, name, inst, help_fields):
        message = name
        for field in help_fields:
            if isinstance(field, str):
                field = ["{} is".format(field), field]
            if hasattr(inst, field[1]) and getattr(inst, field[1]) != None:
                message += ", {} {}".format(field[0], getattr(inst, field[1]))

        return message

    def _setup_parser(self):
        self.procedure = self.procedure_class()
        parameter_objects = self.procedure.parameter_objects()
        for name in self.inputs:
            parameter = parameter_objects[name]
            kwargs, help_fields, inst = parameter.cli_args
            kwargs['help'] = self._cli_help_fields(inst.name, inst, help_fields)
            self.parser.add_argument("--"+name, **kwargs)

        for option, kwargs in self.special_options.items():
            help_fields = kwargs['help_fields']
            desc = kwargs['desc']
            kwargs['help'] = self._cli_help_fields(desc, kwargs, help_fields)
            del kwargs['help_fields']
            del kwargs['desc']
            self.parser.add_argument("--" + option, **kwargs)
            
    def quit(self, evt=None):
        """
        TODO: Is it needed ?
        """
        if self.manager.is_running():
            self.abort()

        self.close()


    def open_experiment(self, filename):
        """
        TODO: To get params from previously run experiment
        """
        results = Results.load(filename)
        return results

    def exec_(self):
        # Parse command line arguments
        args = vars(self.parser.parse_args())
        procedure = self.procedure_class()
        # Set parameters
        parameter_values = {}
        
        if args['use_log_file'] != None:
            # Special case set parameters from log file
            logfile = args['use_log_file']
            results = self.open_experiment(logfile)
            for name in results.parameters:
                parameter_values[name] = results.parameters[name].value
        else:
            for name in args:
                opt_name = "--" + name.replace("_", "-")
                if not (opt_name in self.special_options):
                    parameter_values[name] = args[name]

        procedure.set_parameters(parameter_values)

        scribe = console_log(log, level=logging.DEBUG)
        scribe.start()
        
        results = Results(procedure, unique_filename("."))
        log.info("Set up Results")

        worker = Worker(results, scribe.queue, log_level=logging.DEBUG)
        log.info("Created worker for procedure {}".format(self.procedure_class.__name__))
        log.info("Starting worker...")
        worker.start()

        log.info("Joining with the worker in at most 20 min")
        worker.join(60*20)
        log.info("Worker has joined")
        scribe.stop()

    @property
    def directory(self):
        if not self.directory_input:
            raise ValueError("No directory input in the ManagedWindow")
        return self.directory_line.text()
