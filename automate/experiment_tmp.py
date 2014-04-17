def connect(instruments):
    """ Loops through a list of instruments and calls their connect methods """
    for instrument in instruments:
        if hasattr(instrument, 'connect'): # Quacks like an instrument
            instrument.connect()
        else:
            raise Exception("Can not connect to an instrument that does not have "
                            "a connect method")

def disconnect(instruments):
    """ Loops through a list of instruments and calls their disconnect methods 
    """
    for instrument in instruments:
        if hasattr(instrument, 'disconnect'): # Quacks like an instrument
            instrument.disconnect()
        else:
            raise Exception("Can not disconnect an instrument that does not "
                            "have a connect method")

def typeFromString(string):
    """ Returns the expected type of the value in the provided string
    """
    if re.match("^\d+\.\d+([eE][-+]?\d+)?$", string) is not None:
        return 'float'
    elif re.match("^\d+$", string) is not None:
        return 'int'
    else:
        return 'str'

def castFromString(string):
    """ Returns a casted object based on the observed type in the
    string
    """
    types = {'float':float, 'int':int, 'str':str}
    return types[typeFromString(string)](string)


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
        match = re.match(r'^(?P<name>\w+)(\s\((?P<unit>\w+)\))?:\s(?P<default>.+)$', string)
        if match is None:
            raise Exception("Invalid Parameter formatting in string provided")
        else:
            args = match.groupdict()
            args['default'] = castFromString(args['default'])
            return Parameter(**args)
        
    def __str__(self):
        if self.unit is not None:
            return "%s (%s): %s" % (self.name, self.unit, str(self.value))
        else:
            return "%s: %s" % (self.name, str(self.value))

class Data(object):
    """ Provides a convenience layer over a numpy array for writing
    and reading data, as well as keeping the experiment parameters
    intacted with the data during saving and loading.
    """

    COMMENT_SYMBOL = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"
    
    DEFAULT_TYPES = {'float': np.float32,
                     'int': np.int32,
                     'str': np.str}
    
    @staticmethod
    def load(filename, fields=None):
        """ Extract Data from a file based on its filename.
        The fields will be drawn from the first uncommented line
        if they are not explicity specified
        """
        header = []
        headerRead = False
        with open(filename, 'r') as handle:
            while not headerRead:
                before = handle.tell()
                line = handle.readline()
                if line.startswith(Data.COMMENT_SYMBOL):
                    header.append(line)
                elif fields is None: 
                    # Treat first uncommented line as fields
                    fields = Data.parseRow(line)
                else:
                    break

            # Determine the dtype
            items = Data.parseRow(line)
            dtype = []
            for item, field in zip(items, fields):
                dtype.append((field, Data.DEFAULT_TYPES[typeFromString(item)]))
            dtype = np.dtype(dtype)

            # Read the data
            handle.seek(before)
            buffer = np.loadtxt(handle, dtype=dtype,
                        delimiter=Data.DELIMITER, 
                        comments=Data.COMMENT_SYMBOL)
            obj =  Data(dtype, buffer)
            
            # Parse the comments and parameters
            parameterLabel = "%sParameters:%s" % (Data.COMMENT_SYMBOL,
                                                  Data.LINE_BREAK)
            def clean(comment):
                return comment.replace("\t", '').replace(
                        Data.COMMENT_SYMBOL, '').replace(
                        Data.LINE_BREAK, '')
            if parameterLabel in header:
                index  = header.index(parameterLabel)
                for comment in header[1:index]:
                    obj.comment(clean(comment))
                for parameter in header[index+1:]:
                    obj.setParameter(Parameter.fromString(clean(parameter)))
            else:
                for comment in header[1:]:
                    obj.comment(clean(comment))

            return obj
            
    @staticmethod
    def fromArrays(fieldArrays):
        """ Returns a Data object from a dictionary of fields and their
        arrays
        """
        if type(fieldArrays) is not dict:
            raise Exception("Data requires a dictionary of fields and their "
                            "corresponding numpy arrays")
        dtype = []
        bufferSize = None
        for field, array in fieldArrays.iteritems():
            if bufferSize is None: bufferSize = len(array)
            elif bufferSize != len(array):
                raise Exception("Arrays must be of the same length")
            dtype.append((field, array.dtype))
        obj =  Data(np.dtype(dtype), bufferSize=bufferSize)
        
        # Load data in
        for field, array in fieldArrays.iteritems():
            obj[field] = array
        obj._fillPtr = bufferSize
        
        return obj

    def __init__(self, fields, buffer=None, bufferSize=None):
        """ Constructs a Data object with the given fields
        with the options to set an initial buffer and/or to buffer
        out a particular size for the full set. The fields can be
        defined as a list of string field names, or in the numpy
        dtype format. Unless the dtype format is used, all fields
        will be assumed to be DEFAULT_TYPES['float'].
        """
        if type(fields) is list:
            dtype = np.dtype(
                        [(str(x), Data.DEFAULT_TYPES['float']) for x in fields])
        elif type(fields) is np.dtype:
            dtype = fields
        else:
            raise Exception("Data fields must be a list or numpy dtype")
        if buffer is None: # No initial data to use
            if bufferSize is None or bufferSize <= 0:
                raise Exception("Buffer size must be larger than zero if "
                                "no initial buffer is supplied")
            else:
                self.data = np.empty((bufferSize,), dtype=dtype)
                self._fillPtr = 0
        elif type(buffer) is np.ndarray:
            if bufferSize is None or bufferSize <= 0:
                self.data = np.array(buffer, dtype=dtype)
                self._fillPtr = len(buffer)
            else:
                if bufferSize < len(buffer):
                    raise Exception("Buffer size must include specified"
                                    " initial buffer")
                self.data = np.empty((bufferSize,), dtype=dtype)
                self.data[:len(buffer)] = buffer
                self._fillPtr = len(buffer)
        else:
            raise Exception("Data buffer must be a numpy array")

        # Passthrough magic methods
        methods = ['__getitem__', '__setitem__', '__iter__', '__len__']
        for method in methods:
            setattr(self, method, getattr(self.data, method))

        self.parameters = []
        self.comments = []
        self._filename = None

    @staticmethod
    def parseRow(row):
        """ Returns a list of the row contents based on the class
        formats, defined as DELIMITER and LINE_BREAK
        """
        return row.replace(Data.LINE_BREAK, '').split(Data.DELIMITER)

    @staticmethod
    def formatRow(row):
        """ Returns the row formatted based on the class formats,
        defined as DELIMITER and LINE_BREAK
        """
        return Data.DELIMITER.join([str(x) for x in row]) + Data.LINE_BREAK

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

    def autoSave(self, filename):
        """ Sets the filename to be used for appended data
        """
        self._filename = filename
        
    def autoSaveUnique(self, directory, prefix='DATA'):
        """ Sets a unique filename for appending data
        """
        self._filename = self.uniqueFilename(directory, prefix)
        
    def filename(self):
        """ Return the filename used for auto saving
        """
        return self._filename
        
    def basename(self):
        """ Returns the basename of the auto save file
        """
        return basename(self._filename)

    def header(self):
        """ Returns the file header, including the comments and
        the parameters that have been defined
        """
        lines = []
        if len(self.comments) > 0:
            lines.append("Comments:")
            lines += ["\t" + x for x in self.comments]
        if len(self.parameters) > 0:
            lines.append("Parameters:")
            lines += ["\t" + str(x) for x in self.parameters]
        header = ""
        for line in lines:
            header += Data.COMMENT_SYMBOL + line + Data.LINE_BREAK
        header += Data.formatRow(self.data.dtype.fields.keys())
        return header

    def save(self, filename, format=[]):
        """ Save the filled section of the Data to the filename
        using the class format DELIMITER, with optional specified
        string formatting
        """
        if float('.'.join(np.__version__.split('.')[:2])) >= 1.7:
            # Numpy version 1.7.0 or greater is required
            np.savetxt(filename, self.data[:self._fillPtr], fmt=format,
                       delimiter=Data.DELIMITER, header=self.header(),
                       comments=Data.COMMENT_SYMBOL,
                       newline=Data.LINE_BREAK)
        else:
            # Write the slower way
            with open(filename, 'w') as handle:
                handle.write(str(self))
    
    def uniqueFilename(self, directory, prefix='DATA'):
        """ Returns a unique filename based on the directory and prefix
        """
        date = datetime.now().strftime("%Y%m%d")
        i = 1
        filename = "%s%s%s_%d.csv" % (directory, prefix, date, i)
        while os.path.exists(filename):
            i += 1
            filename = "%s%s%s_%d.csv" % (directory, prefix, date, i)  
        return filename      
                
    def saveUnique(self, directory, prefix='DATA'):
        """ Saves the filled section of the Data in the directory specified
        with a unique filename that follows todays date
        """
        filename = self.uniqueFilename(directory, prefix)
        self.save(filename, format)
        return filename

    def append(self, data):
        """ Append a row of data, and auto-save if the filename has
        been set by the autoSave method
        """
        if len(self.data) is self._fillPtr:
            raise Exception("Data buffer is full")
        if len(data) is not len(self.data.dtype):
            raise Exception("Appended data set is not the correct size")
        if type(data) is dict:
            for field in self.data.dtype.fields:
                self.data[self._fillPtr][field] = data[field]
        else:
            self.data[self._fillPtr] = data
        if self._filename is not None: # Auto-save
            with open(self._filename, 'a') as handle:
                if self._fillPtr is 0: # Header has not been written
                    handle.write(self.header())
                handle.write(Data.formatRow(self.data[self._fillPtr]))
        self._fillPtr += 1

    def setParameter(self, parameter):
        """ Adds a parameter to the list of parameters
        associated with this Data. They can be removed
        manually through the list self.parameters
        """
        if type(parameter) is not Parameter:
            raise Exception("Invalid Parameter object for Data")
        self.parameters.append(parameter)

    def comment(self, comment):
        """ Appends a comment to the comments list and adds a
        line break at the end
        """
        self.comments.append(comment)

    def __str__(self):
        """ Returns the Data object as a string in CSV
        format based on the class definitions of DELIMITER,
        LINE_BREAK, and COMMENT_SYMBOL
        """
        s = self.header()
        for row in self.data[:self._fillPtr]:
            s += Data.formatRow(row)
        return s

