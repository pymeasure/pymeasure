class CSVWriter(object):
    """ Provides an implementation of a CSV file writer
    for slowly updating data, which is assumed to be in
    a dictionary format with keys being the field names.
    """
    
    def __init__(self, filename, delimiter=','):
        self.filename = filename
        self.delimiter = delimiter
        self._firstLine = True
        self._order = None
        
    def comment(self, comment, commentChar='#'):
        """ Appends a comment onto the file at the current location
        and adds the commentChar to each line to distinguish it from data
        """
        # Add commentChar to front of all lines
        comment = "\n".join([commentChar + x for x in comment.split("\n")])    
        with open(self.filename, 'a') as handle:
            handle.write(comment)
            
    def order(self, fields):
        self._order = fields
        
    def write(self, data):
        """ Appends the data to the file requiring a dictionary with
        field names as the keys. Writes the field names to the file
        the first time the write method is called.
        """ 
        with open(self.filename, 'a') as handle:
            if self._firstLine:
                if self._order is not None: fields = self._order
                else: fields = data.keys()
                handle.write(','.join(fields) + "\n")
                self._firstLine = False
            if self._order is not None: 
                values = [str(data[x]) for x in self._order]
            else: values = [str(x) for x in data.values()]
            handle.write(','.join(values) + "\n")
