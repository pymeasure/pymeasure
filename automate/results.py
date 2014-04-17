from os.path import exists, basename
from datetime import datetime
import numpy as np
import re

class Parameter(object):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and unit if supplied.
    """

    def __init__(self, name, unit=None, default=None):
        self.name = name
        self.value = default
        self.unit = unit
        
    def get(self):
        return self.value
        
    def set(self, value):
        self.value = value
        
    def isSet(self):
        return self.value is not None
        
    @staticmethod
    def fromString(string):
        match = re.match(r'^(?P<name>[^()]+)(\s\((?P<unit>\w+)\))?:\s(?P<default>.+)$', string)
        if match is None:
            # Hack to handle empty strings
            match = re.match(r'^(?P<name>[^()]+)(\s\((?P<unit>\w+)\))?:\s$', string)
            if match is None:
                raise Exception("Invalid Parameter formatting in string provided")
            else:
                args = match.groupdict()
                args['default'] = ''
        else:
            args = match.groupdict()
            args['default'] = castFromString(args['default'])
        return Parameter(**args)
        
    def __str__(self):
        if self.unit is not None:
            return "%s (%s): %s" % (self.name, self.unit, str(self.value))
        else:
            return "%s: %s" % (self.name, str(self.value))

def typeFromString(string):
    """ Returns the expected type of the value in the provided string
    """
    if re.match("^[+-]?\d+\.\d+([eE][-+]?\d+)?$", string) is not None:
        return 'float'
    elif re.match("^\d+$", string) is not None:
        return 'int'
    else:
        return 'str'

def castFromString(string):
    """ Returns a casted object based on the observed type in the
    string
    """
    if string == 'None': return None
    types = {'float':float, 'int':int, 'str':str}
    return types[typeFromString(string)](string)

def uniqueFilename(directory, prefix='DATA'):
    """ Returns a unique filename based on the directory and prefix
    """
    date = datetime.now().strftime("%Y%m%d")
    i = 1
    filename = "%s%s%s_%d.csv" % (directory, prefix, date, i)
    while exists(filename):
        i += 1
        filename = "%s%s%s_%d.csv" % (directory, prefix, date, i)  
    return filename

class Data(object):

    DEFAULT_TYPES = {'float': np.float32,
                     'int': np.int32,
                     'str': np.str}

    def __init__(self, data):
        self.data = data
        # Passthrough magic methods
        methods = ['__getitem__', '__setitem__', '__iter__', '__len__']
        for method in methods:
            setattr(self, method, getattr(self.data, method))
        
    def header(self, fields=None):
        if fields is None:
            fields = self.data.dtype.fields.keys()
        return Data.formatRow(fields)
        
    @staticmethod
    def parseDtype(fields):
        if type(fields) is list:
            dtype = np.dtype(
                        [(str(x), Data.DEFAULT_TYPES['float']) for x in fields])
        elif type(fields) is np.dtype:
            dtype = fields
        else:
            raise Exception("Data fields must be a list or numpy dtype") 
        return dtype 

    @staticmethod
    def parseRow(row):
        """ Returns a list of the row contents based on the class
        formats, defined as DELIMITER and LINE_BREAK
        """
        return row.replace(Results.LINE_BREAK, '').split(Results.DELIMITER)

    @staticmethod
    def formatRow(row):
        """ Returns the row formatted based on the class formats,
        defined as DELIMITER and LINE_BREAK
        """
        return Results.DELIMITER.join([str(x) for x in row]) + Results.LINE_BREAK

    def __getitem__(self, key):
        if key in self.data.dtype.fields.keys():
            return self.data[key]
        else:
            raise Exception('Invalid key for referencing column in Data object')
            
    def __setitem__(self, key, value):
        if key in self.data.dtype.fields.keys():
            self.data[key] = value
        else:
            raise Exception('Invalid key for setting column in Data object')

    def save(self, filename, format=[]):
        """ Save the Data to the filename or file handle using the class
        format DELIMITER, with optional specified string formatting
        """
        np.savetxt(filename, self.data, fmt=format,
                   delimiter=Results.DELIMITER,
                   newline=Results.LINE_BREAK)
     
        
class BufferData(Data):

    def __init__(self, points, fields):
        dtype = Data.parseDtype(fields)
        data = np.empty((points,), dtype=dtype)
        self._ptr = 0
        Data.__init__(self, data)

    def __getitem__(self, key):
        if key in self.data.dtype.fields.keys():
            return self.data[key][:self._ptr]
        else:
            raise Exception('Invalid key for referencing column in Data object')
        
    def autoSave(self, filename):
        self._filename = filename
        
    def append(self, data):
        """ Append a row of data, and auto-save if the filename has
        been set by the autoSave method
        """
        if len(self.data) is self._ptr:
            raise Exception("Data buffer is full")
        if len(data) is not len(self.data.dtype):
            raise Exception("Appended data set is not the correct size")
        if type(data) is dict:
            for field in self.data.dtype.fields:
                self.data[self._ptr][field] = data[field]
        else:
            self.data[self._ptr] = data
        if hasattr(self, '_filename'): # Auto-save
            with open(self._filename, 'a') as handle:
                handle.write(Data.formatRow(self.data[self._ptr]))
        self._ptr += 1
        
    def save(self, filename, format='%.18e'):
        """ Save the filled section of the Data to the filename
        using the class format DELIMITER, with optional specified
        string formatting
        """
        np.savetxt(filename, self.data[:self._ptr], fmt=format,
                   delimiter=Results.DELIMITER,
                   newline=Results.LINE_BREAK)
        
        
class FileData(Data):
    
    def __init__(self, file, fields=None):
        """ Extract Data from a file based on its filename or open file handle
        """
        data = np.loadtxt(file, dtype=fields, delimiter=Results.DELIMITER)
        Data.__init__(self, data)
    


class Results(object):

    COMMENT_SYMBOL = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"

    def __init__(self, data):
        self.data = data
        self.comments = ''

    @classmethod
    def buffer(cls, points, dataFields=None):
        if hasattr(cls, 'dataFields') and dataFields is None:
            dataFields = cls.dataFields
        data = BufferData(points, dataFields)
        obj = cls(data)
        return obj
        
    @classmethod
    def load(cls, filename, dataFields=None):
        if hasattr(cls, 'dataFields') and dataFields is None:
            dataFields = cls.dataFields
        header = []
        headerRead = False
        with open(filename, 'r') as handle:
            while not headerRead:
                line = handle.readline()
                if line.startswith(Results.COMMENT_SYMBOL):
                    header.append(line)
                elif dataFields is None: 
                    # Treat first uncommented line as fields
                    dataFields = Data.parseRow(line)
                else:
                    break

            # Determine the dtype
            before = handle.tell()
            items = Data.parseRow(handle.readline())
            dtype = []
            for item, field in zip(items, dataFields):
                dtype.append((field, Data.DEFAULT_TYPES[typeFromString(item)]))
            dtype = np.dtype(dtype)

            # Read the data
            handle.seek(before)
            data = FileData(handle, dtype)
            obj = cls(data)
            obj._filename = filename
                        
            # Parse the comments and parameters
            parameterLabel = "%sParameters:%s" % (Results.COMMENT_SYMBOL,
                                                  Results.LINE_BREAK)
            def clean(comment):
                return comment.replace("\t", '').replace(
                        Results.COMMENT_SYMBOL, '').replace(
                        Results.LINE_BREAK, '')
            if parameterLabel in header:
                index  = header.index(parameterLabel)
                for comment in header[1:index]:
                    obj.comment(clean(comment))
                for parameter in header[index+1:]:
                    parameter = Parameter.fromString(clean(parameter))
                    variable = cls._findParameter(parameter.name)
                    if variable is None:
                        raise Exception("Parameter '%s' does not match the "
                            "class '%s'" % (parameter.name, cls))
                    setattr(obj, variable, parameter)
            else:
                for comment in header[1:]:
                    obj.comment(clean(comment))
            return obj
            
    @classmethod
    def _findParameter(cls, name):
        """ Returns the variable name if found or None
        """
        for item in dir(cls):
            parameter = getattr(cls, item)
            if issubclass(parameter.__class__, Parameter):
                if parameter.name == name:
                    return item
        return None
    
    def mirror(self, obj):
        """ Mirror the parameters of the obj
        """
        for item in dir(obj):
            parameter = getattr(obj, item)
            if issubclass(parameter.__class__, Parameter):
                setattr(self, item, parameter)                
        
    def filename(self):
        return self._filename
        
    def basename(self):
        return basename(self._filename)

    def _header(self):
        """ Returns the file header, including the comments and
        the parameters that have been defined
        """
        lines = []
        if len(self.comments) > 0:
            lines.append("Comments:")
            lines += ["\t" + x for x in self.comments]
        parameters = []
        for item in dir(self):
            parameter = getattr(self, item)
            if issubclass(parameter.__class__, Parameter):
                parameters.append(parameter)
        if len(parameters) > 0:
            lines.append("Parameters:")
            lines += ["\t" + str(x) for x in parameters]
        header = ""
        for line in lines:
            header += Results.COMMENT_SYMBOL + line + Results.LINE_BREAK
        if hasattr(self, 'dataFields'):
            header += self.data.header(self.dataFields)
        else:
            header += self.data.header()
        return header

        
    def save(self, filename, format=[]):
        """ Save the filled section of the Data to the filename
        using the class format DELIMITER, with optional specified
        string formatting
        """
        self._filename = filename
        with open(filename, 'w') as handle:
            handle.write(self._header())
            self.data.save(handle)              
                
    def autoSave(self, filename):
        if not isinstance(self.data, BufferData):
            raise Exception("Auto-saving can only occur with a buffer")
        self._filename = filename
        # Write the header
        with open(filename, 'w') as handle:
            handle.write(self._header())
        self.data.autoSave(filename)
                    

