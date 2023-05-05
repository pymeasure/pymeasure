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

import os
import re
import sys
from importlib import import_module
from importlib.machinery import SourceFileLoader
from datetime import datetime
from string import Formatter

import pandas as pd

import json
from time import sleep

from .procedure import Procedure, UnknownProcedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


def replace_placeholders(string, procedure, date_format="%Y-%m-%d", time_format="%H:%M:%S"):
    """Replace placeholders in string with values from procedure parameters.

    Replaces the placeholders in the provided string with the values of the
    associated parameters, as provided by the procedure. This uses the standard
    python string.format syntax. Apart from the parameter in the procedure (which
    should be called by their full names) "date" and "time" are also added as optional
    placeholders.

    :param string:
        The string in which the placeholders are to be replaced. Python string.format
        syntax is used, e.g. "{Parameter Name}" to insert a FloatParameter called
        "Parameter Name", or "{Parameter Name:.2f}" to also specifically format the
        parameter.

    :param procedure:
        The procedure from which to get the parameter values.

    :param date_format:
        A string to represent how the additional placeholder "date" will be formatted.

    :param time_format:
        A string to represent how the additional placeholder "time" will be formatted.

    """
    now = datetime.now()

    parameters = procedure.parameter_objects()
    placeholders = {param.name: param.value for param in parameters.values()}

    placeholders["date"] = now.strftime(date_format)
    placeholders["time"] = now.strftime(time_format)

    # Check keys against available parameters
    invalid_keys = [i[1] for i in Formatter().parse(string)
                    if i[1] is not None and i[1] not in placeholders]
    if invalid_keys:
        raise KeyError("The following placeholder-keys are not valid: '%s'; "
                       "valid keys are: '%s'." % (
                           "', '".join(invalid_keys),
                           "', '".join(placeholders.keys())
                       ))

    return string.format(**placeholders)


def unique_filename(directory, prefix='DATA', suffix='', ext='csv',
                    dated_folder=False, index=True, datetimeformat="%Y-%m-%d",
                    procedure=None):
    """ Returns a unique filename based on the directory and prefix
    """
    now = datetime.now()
    directory = os.path.abspath(directory)

    if procedure is not None:
        prefix = replace_placeholders(prefix, procedure)
        suffix = replace_placeholders(suffix, procedure)

    if dated_folder:
        directory = os.path.join(directory, now.strftime('%Y-%m-%d'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    if index:
        i = 1
        basename = f"{prefix}{now.strftime(datetimeformat)}"
        basepath = os.path.join(directory, basename)
        filename = "%s_%d%s.%s" % (basepath, i, suffix, ext)
        while os.path.exists(filename):
            i += 1
            filename = "%s_%d%s.%s" % (basepath, i, suffix, ext)
    else:
        basename = f"{prefix}{now.strftime(datetimeformat)}{suffix}.{ext}"
        filename = os.path.join(directory, basename)
    return filename


class CSVFormatter(logging.Formatter):
    """ Formatter of data results """

    def __init__(self, columns, delimiter=','):
        """Creates a csv formatter for a given list of columns (=header).

        :param columns: list of column names.
        :type columns: list
        :param delimiter: delimiter between columns.
        :type delimiter: str
        """
        super().__init__()
        self.columns = columns
        self.delimiter = delimiter

    def format(self, record):
        """Formats a record as csv.

        :param record: record to format.
        :type record: dict
        :return: a string
        """
        if isinstance(record, list):
            total = ""
            for dd in record:
                total += self.delimiter.join(f'{dd[x]}' for x in self.columns) + "\n"
            return total
        elif isinstance(record, dict):
            return self.delimiter.join(f'{record[x]}' for x in self.columns)

    def format_header(self):
        return self.delimiter.join(self.columns)


class CSVFormatter_Pandas(logging.Formatter):
    """ Formatter of data results """

    def __init__(self, columns, delimiter=',', line_break='\n'):
        """Creates a csv formatter for a given list of columns (=header).

        :param columns: list of column names.
        :type columns: list
        :param delimiter: delimiter between columns.
        :type delimiter: str
        """
        super().__init__()
        self.columns = columns
        self.delimiter = delimiter
        self.line_break = line_break

    def format(self, record):
        """Formats a record as csv.

        :param record: record to format.
        :type record: pandas.DataFrame
        :return: a string
        """
        return record.to_csv(
            sep=self.delimiter,
            header=False,
            index=False,
            # explicit line_terminator required, otherwise Windows
            # uses \r\n which results in double blank lines
            line_terminator=self.line_break
        )

    def format_header(self):
        return self.delimiter.join(self.columns)


class JSONFormatter(logging.Formatter):
    """ Formatter of data results """

    def __init__(self, parameters=None, procedure=None):
        """
        """
        # the default encoder doesn't understand FloatParameter, etc.
        # we could write our own encoder, but this one is easy enough.
        self.procedure = procedure
        base_types = {}
        for key, item in parameters.items():
            base_types[key] = item.value
        self.key = json.dumps(base_types)
        super().__init__()


    def format(self, record):
        """Formats a record as json.

        :param record: record to format.
        :type record: dict
        :return: a string
        """
        if self.procedure is not None:
            parameters = self.procedure.parameter_objects()
        else:
            parameters = self.parameters
        base_types = {}
        for key, item in parameters.items():
            base_types[key] = item.value
        self.key = json.dumps(base_types)
        return json.dumps({self.key: record}, indent=1)



class Results:
    """ The Results class provides a convenient interface to reading and
    writing data in connection with a :class:`.Procedure` object.

    :param procedure: Procedure object
    :param data_filename: The data filename where the data is or should be
                          stored
    :param output_format: Formatter which converts the emitted result data
                          so it can be written to file, defaults to CSV
    """

    COMMENT = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    def __init__(self, procedure, data_filename, routine=None, output_format='CSV'):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")
        self.procedure = procedure
        self.routine = routine
        self.procedure_class = procedure.__class__
        self.parameters = procedure.parameter_objects()
        self.output_format = output_format

        if self.output_format == 'CSV_PANDAS':
            self.formatter = CSVFormatter_Pandas(
                columns=self.procedure.DATA_COLUMNS,
                delimiter=self.DELIMITER,
                line_break=self.LINE_BREAK
            )

        elif self.output_format == 'JSON':
            self.formatter = JSONFormatter(parameters=self.parameters, procedure=self.procedure)

        else:  # default to CSV
            self.formatter = CSVFormatter(columns=self.procedure.DATA_COLUMNS)

        if isinstance(data_filename, (list, tuple)):
            data_filenames, data_filename = data_filename, data_filename[0]
        else:
            data_filenames = [data_filename]

        self.data_filename = data_filename
        self.data_filenames = data_filenames

        if os.path.exists(data_filename):  # Assume header is already written
            self.reload()
            self.procedure.status = Procedure.FINISHED
            # TODO: Correctly store and retrieve status
        else:
            for filename in self.data_filenames:
                with open(filename, 'w') as f:
                    if self.output_format == 'JSON':
                        json.dump({self.formatter.key:{c:[] for c in self.procedure.DATA_COLUMNS}},f)
                        # Need empty file for JSON, we dump everything all at once
                        self._header_count = 0
                    else:
                        f.write(self.header())
                        f.write(self.labels())
            self._data = None

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
        del state['procedure_class']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)

        # Restore the procedure
        module = SourceFileLoader(self._module, self._file).load_module()
        cls = getattr(module, self._class)

        self.procedure = cls()
        self.procedure.set_parameters(self._parameters)
        self.procedure.refresh_parameters()

        self.procedure_class = cls

        del self._parameters
        del self._class
        del self._package
        del self._module
        del self._file

    def header(self):
        """ Returns a text header to accompany a datafile so that the procedure
        can be reconstructed
        """
        h = []
        procedure = re.search("'(?P<name>[^']+)'",
                              repr(self.procedure_class)).group("name")
        h.append("Procedure: <%s>" % procedure)
        h.append("Parameters:")
        for name, parameter in self.parameters.items():
            h.append("\t{}: {}".format(parameter.name, str(
                parameter).encode("unicode_escape").decode("utf-8")))
        h.append("Data:")
        self._header_count = len(h)
        h = [Results.COMMENT + line for line in h]  # Comment each line
        return Results.LINE_BREAK.join(h) + Results.LINE_BREAK

    def labels(self):
        """ Returns the columns labels as a string to be written
        to the file
        """
        return self.formatter.format_header() + Results.LINE_BREAK

    def format(self, data):
        """ Returns a formatted string containing the data to be written
        to a file
        """
        return self.formatter.format(data)

    def parse(self, line):
        """ Returns a dictionary containing the data from the line """
        data = {}
        items = line.split(Results.DELIMITER)
        for i, key in enumerate(self.procedure.DATA_COLUMNS):
            data[key] = items[i]
        return data

    @staticmethod
    def parse_header(header, procedure_class=None):
        """ Returns a Procedure object with the parameters as defined in the
        header text.
        """
        if procedure_class is not None:
            procedure = procedure_class()
        else:
            procedure = None
        if isinstance(header, str):
            header = header.split(Results.LINE_BREAK)
            procedure_module = None
            parameters = {}
            for line in header:
                if line.startswith(Results.COMMENT):
                    line = line[1:]  # Uncomment
                else:
                    raise ValueError("Parsing a header which contains "
                                     "uncommented sections")
                if line.startswith("Procedure"):
                    regex = r"<(?:(?P<module>[^>]+)\.)?(?P<class>[^.>]+)>"
                    search = re.search(regex, line)
                    procedure_module = search.group("module")
                    procedure_class = search.group("class")
                elif line.startswith("\t"):
                    separator = ": "
                    partitioned_line = line[1:].partition(separator)
                    if partitioned_line[1] != separator:
                        raise Exception("Error partitioning header line %s." % line)
                    else:
                        parameters[partitioned_line[0]] = partitioned_line[2]

        elif isinstance(header, dict):
            # we loaded from json
            parameters = header

        if procedure is None:
            if procedure_class is None:
                raise ValueError("Header does not contain the Procedure class")
            try:
                procedure_module = import_module(procedure_module)
                procedure_class = getattr(procedure_module, procedure_class)
                procedure = procedure_class()
            except ImportError:
                procedure = UnknownProcedure(parameters)
                log.warning("Unknown Procedure being used")

        # Fill the procedure with the parameters found
        for name, parameter in procedure.parameter_objects().items():
            if parameter.name in parameters:
                value = parameters[parameter.name]
                setattr(procedure, name, value)
            else:
                raise Exception("Missing '{}' parameter when loading '{}' class".format(
                    parameter.name, procedure_class))

        procedure.refresh_parameters()  # Enforce update of meta data
        return procedure

    @staticmethod
    def load(data_filename, procedure_class=None):
        """ Returns a Results object with the associated Procedure object and
        data
        """
        header = ""
        header_read = False
        is_json = False
        header_count = 0
        with open(data_filename) as f:
            while not header_read:
                line = f.readline()
                if line.startswith('{\n}'):
                    #TODO untested
                    header = json.loads(list(json.load(f).keys())[0])
                    is_json = True
                    header_read = True
                elif line.startswith(Results.COMMENT):
                    header += line.strip() + Results.LINE_BREAK
                    header_count += 1
                else:
                    header_read = True
        if is_json:
            procedure = Results.parse_header(header, procedure_class)
        else:
            procedure = Results.parse_header(header[:-1], procedure_class)
        results = Results(procedure, data_filename)
        results._header_count = header_count
        return results

    @property
    def data(self):
        # Need to update header count for correct referencing
        if self._header_count == -1:
            self._header_count = len(
                self.header()[-1].split(Results.LINE_BREAK))
        if self._data is None or len(self._data) == 0:
            # Data has not been read
            try:
                self.reload()
            except Exception as e:
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
                # Empty dataframe

        else:  # Concatenate additional data, if any, to already loaded data
            if self.output_format == 'JSON':
                self.reload()
            else:
                skiprows = len(self._data) + self._header_count
                chunks = pd.read_csv(
                    self.data_filename,
                    comment=Results.COMMENT,
                    header=0,
                    names=self._data.columns,
                    chunksize=Results.CHUNK_SIZE, skiprows=skiprows, iterator=True
                )
                try:
                    tmp_frame = pd.concat(chunks, ignore_index=True)
                    # only append new data if there is any
                    # if no new data, tmp_frame dtype is object, which override's
                    # self._data's original dtype - this can cause problems plotting
                    # (e.g. if trying to plot int data on a log axis)
                    if len(tmp_frame) > 0:
                        self._data = pd.concat([self._data, tmp_frame],
                                               ignore_index=True)
                except Exception:
                    pass  # All data is up to date
        return self._data

    def reload(self):
        """ Preforms a full reloading of the file data, neglecting
        any changes in the comments
        """
        if self.output_format == 'JSON':
            self.old_data = self._data
            exit_condition = 5
            success = False
            i = 0
            while not success and i < exit_condition:

                try:
                    with open(self.data_filename,'r') as f:
                        if len(f.readlines()) != 0:
                            f.seek(0)
                            chunk = json.load(f)
                        else:
                            chunk = None
                except json.decoder.JSONDecodeError:
                    sleep(.1)
                    print('Json data reload error. Probably thread conflict')
                    chunk = None

                i = i + 1

                if chunk is not None:
                    keys = list(chunk.keys())
                    now = chunk[keys[0]]
                    if len(keys) == 1:
                        success = True

            if chunk is not None:
                keys = list(chunk.keys())
                now = chunk[keys[0]]
                if len(keys) != 1:
                    raise ValueError(f'Trying to load a non-JSON file as a JSON file'
                                     f'got {keys} in the chunk')
                self._data = pd.DataFrame(now)
            else:
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
        else:
            chunks = pd.read_csv(
                self.data_filename,
                comment=Results.COMMENT,
                chunksize=Results.CHUNK_SIZE,
                iterator=True
            )
            try:
                self._data = pd.concat(chunks, ignore_index=True)
            except Exception:
                self._data = chunks.read()

    def __repr__(self):
        return "<{}(filename='{}',procedure={},shape={})>".format(
            self.__class__.__name__, self.data_filename,
            self.procedure.__class__.__name__,
            self.data.shape
        )





