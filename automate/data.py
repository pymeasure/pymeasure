#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic classes and functions for experiment data
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from automate.experiment import Procedure
from os.path import exists, basename
from datetime import datetime
import re
import numpy as np
import pandas as pd
from os.path import exists

def uniqueFilename(directory, prefix='DATA', suffix='', ext='csv'):
    """ Returns a unique filename based on the directory and prefix
    """
    date = datetime.now().strftime("%Y%m%d")
    i = 1
    filename = "%s%s%s_%d%s.%s" % (directory, prefix, date, i, suffix, ext)
    while exists(filename):
        i += 1
        filename = "%s%s%s_%d%s.%s" % (directory, prefix, date, i, suffix, ext)  
    return filename

    
class Results(object):
    """ Provides a base class for experiment results tracking, which should be
    extended for the specific data/logs collected for a Procedure
    """
    
    COMMENT = '#'
    DELIMITER = ','
    LINE_BREAK = "\n"
    CHUNK_SIZE = 1000

    def __init__(self, procedure, data_filename):
        if not isinstance(procedure, Procedure):
            raise ValueError("Results require a Procedure object")
        self.procedure = procedure
        self.procedure_class = procedure.__class__
        self.parameters = procedure.parameterObjects()
        self._header_count = -1
        
        self.data_filename = data_filename
        if exists(data_filename): # Assume header is already written
            self._data = pd.read_csv(data_filename, comment=Results.COMMENT)
        else:
            with open(data_filename, 'w') as f:
                f.write(self.header())
            self._data = None
        
        
    def header(self):
        """ Returns a text header to accompany a datafile so that the procedure
        can be reconstructed
        """
        h = []
        procedure = re.search("'(?P<name>[^']+)'", repr(self.procedure_class)).group("name")
        h.append("Procedure: <%s>" % procedure)
        h.append("Parameters:")
        for name, parameter in self.parameters.iteritems():
            h.append("\t%s: %s" % (parameter.name, parameter.value))
            if parameter.unit:
                h[-1] += " %s" % parameter.unit
        h.append("Data:")
        self._header_count = len(h)
        h = [Results.COMMENT + l for l in h] # Comment each line
        return Results.LINE_BREAK.join(h) + Results.LINE_BREAK
        
    @staticmethod
    def parseHeader(header):
        """ Returns a Procedure object with the parameters as defined in the
        header text.
        """
        header = header.split(Results.LINE_BREAK)
        procedure_module = None
        procedure_class = None
        parameters = {}
        for line in header:
            if line.startswith(Results.COMMENT):
                line = line[1:] # Uncomment
            else:
                raise ValueError("Parsing a header which contains uncommented sections")
            if line.startswith("Procedure"):
                search = re.search("<(?:(?P<module>[^>]+)\.)?(?P<class>[^.>]+)>", line)
                procedure_module = search.group("module")
                procedure_class = search.group("class")
            elif line.startswith("\t"):
                search = re.search("\t(?P<name>[^:]+):\s(?P<value>[^\s]+)(?:\s(?P<unit>.+))?", line)
                parameters[search.group("name")] = (search.group("value"), search.group("unit"))
        if procedure_class is None:
            raise ValueError("Header does not contain the Procedure class")
        from importlib import import_module
        module = import_module(procedure_module)
        procedure_class = getattr(module, procedure_class)
        
        procedure = procedure_class()
        # Fill the procedure with the parameters found
        for name, parameter in procedure.parameterObjects().iteritems():
            if parameter.name in parameters:
                value, unit = parameters[parameter.name]
                setattr(procedure, name, value)
            else:
                raise Exception("Missing '%s' parameter when loading '%s' class" % (
                        parameter.name, procedure_class))
        procedure.parameterObjects() # Enforce update of meta data
        return procedure
                
    @staticmethod
    def load(data_filename):
        """ Returns a Results object with the associated Procedure object and
        data
        """
        header = ""
        header_read = False
        header_count = 0
        with open(data_filename, 'r') as f:
            while not header_read:
                line = f.readline()
                if line.startswith(Results.COMMENT):
                    header += line + Results.LINE_BREAK
                    header_count += 1
                else:
                    header_read = True
        procedure = Results.parseHeader(header)
        results = Results(procedure, data_filename)
        results._header_count = header_count
        return results
    
    @property
    def data(self):
        if self._header_count == -1: # Need to update header count for correct referencing
            self._header_count = len(self.header()[-1].split(Results.LINE_BREAK))
        if self._data is None or len(self._data) == 0: # Data has not been read
            try:
                self._data = pd.read_csv(self.data_filename, comment=Results.COMMENT)
            except:
                raise Exception("The data file is currently empty")
        else: # Concatenate additional data
            skiprows = len(self._data) + self._header_count
            chunks = pd.read_csv(self.data_filename, comment=Results.COMMENT, header=0,
                        names=self._data.columns,
                        chunksize=Results.CHUNK_SIZE, skiprows=skiprows, iterator=True)
            try:
                tmp_frame = pd.concat(chunks, ignore_index=True)
                self._data = pd.concat([self._data, tmp_frame], ignore_index=True)
            except:
                pass # All data is up to date
        return self._data
            


