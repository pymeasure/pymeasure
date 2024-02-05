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
import numpy as np

import json
from time import sleep

from .procedure import Procedure, UnknownProcedure

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())

try:
    import pyarrow as pa
    from pyarrow import feather
except:
    log.info('Pyarrow not installed, feather not available')


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


class ResultsBase:
    """
    The ResultsBase base class provides a Framework for creating a convenient interface to reading and
    writing data in connection with a :class:`.Procedure` object.

    A complete Results class must implement five things:
    - Make a header object (i.e. an object containing all parameters in the procedure)
     that can be written to file (`create_header`)
    - Reconstruct the parameter dictionary from the loaded data (`get_params_from_header`)
    - Create or initialize the resources/stores to write to (`create_resources`)
    - Create the handlers (derived from `Logging.Handler`)
     to dump the header object and raw data to a store (`create_handlers`)
    - Read the data from store (`reload`)

    """

    HANDLER = None
    FORMATTER = None

    def __init__(self, procedure, resource_specifier, **kwargs):

        self.procedure = procedure
        self.procedure_class = procedure.__class__
        self.parameters = procedure.parameter_objects()
        self._data = None

        if 'routine' in kwargs.keys():
            self.routine = kwargs.pop('routine')
        else:
            self.routine = None

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

    def create_handlers(self, **kwargs):
        raise NotImplementedError('Must be patched by subclass to return a list of handlers to write data to')

    def create_resources(self):
        raise NotImplementedError("Must be patched by subclass to create a resource to write to")

    def create_header(self):
        raise NotImplementedError("Must be patched by subclass to create a header object for writing to store")

    def reload(self):
        raise NotImplementedError('Must be patched by subclass to reload data from source')

    @staticmethod
    def get_params_from_header(header, procedure_class=None):
        raise NotImplementedError("Must be patched by subclass to get params from a header")

    @staticmethod
    def get_proc_from_params(parameters, procedure_module, procedure_class):

        if procedure_class is not None:
            procedure = procedure_class()
        else:
            procedure = None

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
    def parse_header(header, procedure_class=None):
        parameters, procedure_module, procedure_class = ResultsBase.get_params_from_header(header, procedure_class)
        procedure = ResultsBase.get_proc_from_params(parameters, procedure_module, procedure_class)
        return procedure



class FileBasedResults(ResultsBase):

    """
    FileBasedResults defines

    """

    def __init__(self, procedure, data_filename, **kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")

        super().__init__(procedure, data_filename, **kwargs)

        if isinstance(data_filename, (list, tuple)):
            data_filenames, data_filename = data_filename, data_filename[0]
        else:
            data_filenames = [data_filename]

        self.data_filename = data_filename
        self.data_filenames = data_filenames

        if self.resource_exists():  # Assume header is already written
            self.reload()
            self.procedure.status = Procedure.FINISHED
            # TODO: Correctly store and retrieve status
        else:
            self.create_resources()

    def create_handlers(self, **kwargs):
        handlers = []
        for filename in self.data_filenames:
            h = self.HANDLER(filename=filename, **kwargs)
            if self.FORMATTER is not None:
                h.setFormatter(self.FORMATTER)

            h.setLevel(logging.NOTSET)
            handlers.append(h)
        return handlers

    def resource_exists(self):
        if os.path.exists(self.data_filename):
            return True
        else:
            return False


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
            for i, dd in enumerate(record):
                if i != len(record)-1:
                    total += self.delimiter.join(f'{dd[x]}' for x in self.columns) + "\n"
                else:
                    total += self.delimiter.join(f'{dd[x]}' for x in self.columns)
            return total
        elif isinstance(record, dict):
            return self.delimiter.join(f'{record[x]}' for x in self.columns)

    def format_column_header(self):
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


class CSVHandler(logging.FileHandler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class CSVResults(FileBasedResults):

    """

    :cvar COMMENT: The character used to identify a comment (default: #)
    :cvar DELIMITER: The character used to delimit the data (default: ,)
    :cvar LINE_BREAK: The character used for line breaks (default \\n)
    :cvar CHUNK_SIZE: The length of the data chuck that is read
    """

    COMMENT = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    HANDLER = CSVHandler
    FORMATTER = CSVFormatter

    def __init__(self, procedure, data_filename,**kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")

        self._header_count = -1
        self.FORMATTER = CSVFormatter(columns=procedure.DATA_COLUMNS)
        super().__init__(procedure, data_filename, **kwargs)



    def labels(self):
        """ Returns the columns labels as a string to be written
        to the file
        """
        return self.FORMATTER.format_column_header() + CSVResults.LINE_BREAK

    def format(self, data):
        """ Returns a formatted string containing the data to be written
        to a file
        """
        return self.FORMATTER.format(data)

    def parse(self, line):
        """ Returns a dictionary containing the data from the line """
        data = {}
        items = line.split(CSVResults.DELIMITER)
        for i, key in enumerate(self.procedure.DATA_COLUMNS):
            data[key] = items[i]
        return data

    def create_header(self):
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
        h = [CSVResults.COMMENT + line for line in h]  # Comment each line
        return CSVResults.LINE_BREAK.join(h) + CSVResults.LINE_BREAK

    def create_resources(self):
        for filename in self.data_filenames:
            with open(filename, 'w') as f:
                f.write(self.create_header())
                f.write(self.labels())
        self._data = None

    def metadata(self):
        """ Returns a text header for the metadata to write into the datafile """
        if not self.procedure.metadata_objects():
            return

        m = ["Metadata:"]
        for _, metadata in self.procedure.metadata_objects().items():
            value = str(metadata).encode("unicode_escape").decode("utf-8")
            m.append(f"\t{metadata.name}: {value}")

        self._metadata_count = len(m)
        m = [Results.COMMENT + line for line in m]  # Comment each line
        return Results.LINE_BREAK.join(m) + Results.LINE_BREAK

    def store_metadata(self):
        """ Inserts the metadata header (if any) into the datafile """
        c_header = self.metadata()
        if c_header is None:
            return

        for filename in self.data_filenames:
            with open(filename, 'r+') as f:
                contents = f.readlines()
                contents.insert(self._header_count - 1, c_header)

                f.seek(0)
                f.writelines(contents)

        self._header_count += self._metadata_count

    @staticmethod
    def get_params_from_header(header, procedure_class=None):
        """ Returns a Procedure object with the parameters as defined in the
        header text.
        """

        header = header.split(CSVResults.LINE_BREAK)
        procedure_module = None
        parameters = {}
        for line in header:
            if line.startswith(CSVResults.COMMENT):
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
        return parameters, procedure_module, procedure_class

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
                if line.startswith(CSVResults.COMMENT):
                    header += line.strip() + CSVResults.LINE_BREAK
                    header_count += 1
                else:
                    header_read = True
        procedure = CSVResults.parse_header(header[:-1], procedure_class)
        results = CSVResults(procedure, data_filename)
        results._header_count = header_count
        return results

    @property
    def data(self):
        # Need to update header count for correct referencing
        if self._header_count == -1:
            self._header_count = len(
                self.create_header()[-1].split(CSVResults.LINE_BREAK))
        if self._data is None or len(self._data) == 0:
            # Data has not been read
            try:
                self.reload()
            except Exception as e:
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
                # Empty dataframe

        else:  # Concatenate additional data, if any, to already loaded data
            skiprows = len(self._data) + self._header_count
            chunks = pd.read_csv(
                self.data_filename,
                comment=CSVResults.COMMENT,
                header=0,
                names=self._data.columns,
                chunksize=CSVResults.CHUNK_SIZE, skiprows=skiprows, iterator=True
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
        """ Performs a full reloading of the file data, neglecting
        any changes in the comments
        """
        chunks = pd.read_csv(
            self.data_filename,
            comment=CSVResults.COMMENT,
            chunksize=CSVResults.CHUNK_SIZE,
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


class CSVPandas_Results(CSVResults):
    COMMENT = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    HANDLER = CSVHandler
    FORMATTER = CSVFormatter_Pandas

    def __init__(self, procedure, data_filename, **kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")

        self._header_count = -1
        self.FORMATTER = CSVFormatter_Pandas(columns=procedure.DATA_COLUMNS, **kwargs)
        super().__init__(procedure, data_filename)

class Results(CSVResults):
    def __init__(self,*args, **kwargs):
        super(Results, self).__init__(*args, **kwargs)

class JSONFileHandler(logging.FileHandler):

    def emit(self, record):
        """Method to override the normal logging FileHandler when the record is json.
        The record expected is a dictionary of dictionaries, so the first
        step is to re-extract the dict. Then we check various conditions. The end result is a file with a
        single (possibly updated) dictionary of dictionaries. Because it is json we can't just append, we have
        to rewrite the whole file. There may be a reason you want this so it is included."""

        with open(self.baseFilename, 'r') as f:
            extant = json.load(f)
        data = extant[list(extant.keys())[0]]

        for key in record.keys():
            if key in data.keys():
                for column, array in data.items():
                    if isinstance(record[column], (list, tuple)):
                        data[column] = list(np.concatenate([array, record[column]]))
                    elif isinstance(record[column], (float, int, str, bool,)):
                        array.append(record[column])
                    else:
                        raise TypeError(f'got unexpected type for {record[column]}, {type(record[column])}')
            else:
                datum = record[key]
                if not isinstance(datum, list):
                    datum = [datum,]
                data[key] = datum

        extant[list(extant.keys())[0]] = data
        with open(self.baseFilename, 'w') as f:
            json.dump(extant, f)

class JSONFormatter(logging.Formatter):
    """ Formatter of data results """

    def __init__(self, procedure=None, parameters=None):
        """
        """
        # the default encoder doesn't understand FloatParameter, etc.
        # we could write our own encoder, but this one is easy enough.
        super().__init__()
        self.procedure = procedure
        self.parameters = parameters
        if (self.procedure is None) and (self.parameters is None):
            raise ValueError('Neither procedure nor parameters specified/both are None')



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


class JSONResults(FileBasedResults):
    """The JSONResults class provides an interface to read an write data
    in JSON format in connection with a :class: `.Procedure` object."""

    HANDLER = JSONFileHandler
    FORMATTER = None

    def __init__(self, procedure, data_filename, **kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")
        self.procedure = procedure
        self.FORMATTER = None
        super().__init__(procedure, data_filename, **kwargs)

    def create_header(self):
        """Returns a JSON string to accompany datafile so that the procedure can be
        reconstructed.
        """
        param_dict = {}
        for name, parameter in self.parameters.items():
            param_dict[name] = parameter.value
        return json.dumps(param_dict)

    def create_resources(self):
        header = self.create_header()
        for filename in self.data_filenames:
            with open(filename, 'w') as f:
                json.dump({header : {}}, f)
        self._data = None

    @staticmethod
    def get_params_from_header(header, procedure_class=None):
        parameters = json.loads(header)

        regex = r"<(?:(?P<module>[^>]+)\.)?(?P<class>[^.>]+)>"
        search = re.search(regex, parameters['Procedure'])
        procedure_module = search.group("module")
        procedure_class = search.group("class")

        return parameters, procedure_module, procedure_class

    def reload(self):
        """ Performs a full reloading of the file data, neglecting
        any changes in the comments
        """

        with open(self.data_filename, 'r') as f:
            data = json.load(f)
        raw = data[list(data.keys())[0]]
        if raw == {}:
            self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
        else:
            self._data = pd.DataFrame(raw)

    @staticmethod
    def load(data_filename, procedure_class=None):
        """ Returns a Results object with the associated Procedure object and
        data
        """
        with open(data_filename, 'r') as f:
            data = json.load(f)
        header = json.loads(list(data.keys())[0])
        data = pd.DataFrame(data[list(data.keys())[0]])

        procedure = ResultsBase.parse_header(header, procedure_class)
        results = JSONResults(procedure, data_filename)
        return results

    @property
    def data(self):
        if self._data is None or len(self._data) == 0:
            # Data has not been read
            try:
                self.reload()
            except Exception:
                # Something went wrong when opening the data
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
        else:  # JSON has to be read all at once, no good choices to be made here unfortunately
            with open(self.data_filename, 'r') as f:
                data = json.load(f)
            self._data = pd.DataFrame(data[list(data.keys())[0]])  # The json should have only one entry.

        return self._data


class FeatherFileHandler(logging.FileHandler):

    def emit(self, record):
        """Method to override the normal logging FileHandler when the record is feather.
        The record expected is a dictionary of dictionaries, so the first
        step is to re-extract the dict. Then we check various conditions. The end result is a file with a
        single (possibly updated) dictionary of dictionaries. Because it is json we can't just append, we have
        to rewrite the whole file. There may be a reason you want this so it is included."""

        arrow_table = feather.read_table(self.baseFilename)
        header = arrow_table.schema.metadata[b'header']
        olddata = arrow_table.to_pandas()

        one_record = record[list(record.keys())[0]]
        if not isinstance(one_record, (list, tuple, np.ndarray)):
            newdata = pd.DataFrame(record,index=[0])
        else:

            newdata = pd.DataFrame(record)
        data = pd.concat([olddata,newdata], ignore_index=True)
        newtable = pa.Table.from_pandas(data, preserve_index=False, nthreads=1)

        existing_metadata = newtable.schema.metadata
        new_metadata = {**existing_metadata, **{'header': header}}
        newtable = newtable.replace_schema_metadata(new_metadata)
        feather.write_feather(newtable, self.baseFilename)


class FeatherResults(FileBasedResults):
    """The FeatherResults class provides an interface to read an write data
    in Feather format in connection with a :class: `.Procedure` object."""

    HANDLER = FeatherFileHandler
    FORMATTER = None

    def __init__(self, procedure, data_filename, handler=None, **kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")
        if handler is not None:
            self.HANDLER = handler
        self.procedure = procedure
        self.FORMATTER = None#self.FORMATTER(procedure=self.procedure)
        super().__init__(procedure, data_filename, **kwargs)

    def create_header(self):
        """Returns a JSON string to accompany datafile so that the procedure can be
        reconstructed.
        """
        param_dict = {}
        for name, parameter in self.parameters.items():
            param_dict[name] = parameter.value
        return json.dumps(param_dict)

    def create_resources(self):
        header = self.create_header()
        data = pd.DataFrame({col:[] for col in self.procedure.DATA_COLUMNS})
        newtable = pa.Table.from_pandas(data, preserve_index=False, nthreads=1)

        existing_metadata = newtable.schema.metadata
        new_metadata = {**existing_metadata, **{'header': header}}
        newtable = newtable.replace_schema_metadata(new_metadata)

        for filename in self.data_filenames:
            pa.feather.write_feather(newtable, filename)
        self._data = None

    @staticmethod
    def get_params_from_header(header, procedure_class=None):
        parameters = json.loads(header)

        regex = r"<(?:(?P<module>[^>]+)\.)?(?P<class>[^.>]+)>"
        search = re.search(regex, parameters['Procedure'])
        procedure_module = search.group("module")
        procedure_class = search.group("class")

        return parameters, procedure_module, procedure_class

    def reload(self):
        """ Performs a full reloading of the file data, neglecting
        any changes in the comments
        """
        data = feather.read_feather(self.data_filename)
        self._data = data

    @staticmethod
    def load(data_filename, procedure_class=None):
        """ Returns a Results object with the associated Procedure object and
        data
        """
        table = feather.read_table(data_filename)
        header = table.schema.metadata[b'header']

        procedure = ResultsBase.parse_header(header, procedure_class)
        results = FeatherResults(procedure, data_filename)
        return results

    @property
    def data(self):
        if self._data is None or len(self._data) == 0:
            # Data has not been read
            try:
                self.reload()
            except Exception:
                # Something went wrong when opening the data
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
        else:  # JSON has to be read all at once, no good choices to be made here unfortunately
            data = feather.read_feather(self.data_filename)
            self._data = data

        return self._data


class ParquetFileHandler(logging.FileHandler):

    def emit(self, record):
        """Method to override the normal logging FileHandler when the record is feather.
        The record expected is a dictionary of dictionaries, so the first
        step is to re-extract the dict. Then we check various conditions. The end result is a file with a
        single (possibly updated) dictionary of dictionaries. Because it is json we can't just append, we have
        to rewrite the whole file. There may be a reason you want this so it is included."""

        arrow_table = pq.ParquetFile(self.baseFilename)
        header = arrow_table.schema.to_arrow_schema().metadata[b'header']
        olddata = arrow_table.read().to_pandas()

        one_record = record[list(record.keys())[0]]
        if not isinstance(one_record, (list, tuple, np.ndarray)):
            newdata = pd.DataFrame(record,index=[0])
        else:

            newdata = pd.DataFrame(record)
        data = pd.concat([olddata,newdata], ignore_index=True)
        newtable = pa.Table.from_pandas(data, preserve_index=False, nthreads=1)

        existing_metadata = newtable.schema.metadata
        new_metadata = {**existing_metadata, **{'header': header}}
        newtable = newtable.replace_schema_metadata(new_metadata)
        pq.write_table(newtable, self.baseFilename)


class ParquetResults(FileBasedResults):
    """The FeatherResults class provides an interface to read an write data
    in Feather format in connection with a :class: `.Procedure` object."""

    HANDLER = ParquetFileHandler
    FORMATTER = None

    def __init__(self, procedure, data_filename, handler=None, **kwargs):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")
        if handler is not None:
            self.HANDLER = handler
        self.procedure = procedure
        self.FORMATTER = None#self.FORMATTER(procedure=self.procedure)
        super().__init__(procedure, data_filename, **kwargs)

    def create_header(self):
        """Returns a JSON string to accompany datafile so that the procedure can be
        reconstructed.
        """
        param_dict = {}
        for name, parameter in self.parameters.items():
            param_dict[name] = parameter.value
        return json.dumps(param_dict)

    def create_resources(self):
        header = self.create_header()
        data = pd.DataFrame({col:[] for col in self.procedure.DATA_COLUMNS})
        newtable = pa.Table.from_pandas(data, preserve_index=False, nthreads=1)

        existing_metadata = newtable.schema.metadata
        new_metadata = {**existing_metadata, **{'header': header}}
        newtable = newtable.replace_schema_metadata(new_metadata)

        for filename in self.data_filenames:
            pa.feather.write_feather(newtable, filename)
        self._data = None

    @staticmethod
    def get_params_from_header(header, procedure_class=None):
        parameters = json.loads(header)

        regex = r"<(?:(?P<module>[^>]+)\.)?(?P<class>[^.>]+)>"
        search = re.search(regex, parameters['Procedure'])
        procedure_module = search.group("module")
        procedure_class = search.group("class")

        return parameters, procedure_module, procedure_class

    def reload(self):
        """ Performs a full reloading of the file data, neglecting
        any changes in the comments
        """
        data = feather.read_feather(self.data_filename)
        self._data = data

    @staticmethod
    def load(data_filename, procedure_class=None):
        """ Returns a Results object with the associated Procedure object and
        data
        """
        table = feather.read_table(data_filename)
        header = table.schema.metadata[b'header']

        procedure = ResultsBase.parse_header(header, procedure_class)
        results = FeatherResults(procedure, data_filename)
        return results

    @property
    def data(self):
        if self._data is None or len(self._data) == 0:
            # Data has not been read
            try:
                self.reload()
            except Exception:
                # Something went wrong when opening the data
                self._data = pd.DataFrame(columns=self.procedure.DATA_COLUMNS)
        else:  # JSON has to be read all at once, no good choices to be made here unfortunately
            data = feather.read_feather(self.data_filename)
            self._data = data

        return self._data
