#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# Generic classes for experiment procedures, parameters, and results
#
# automate Python package
# Authors: Colin Jermain, Graham Rowlands
# Copyright: 2014 Cornell University
#
#>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
from threading import Event, Thread
from Queue import Queue
from os.path import exists, basename
from datetime import datetime
import re
import numpy as np
import pandas as pd

class Parameter(object):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and unit if supplied.
    
    Parameter name can not contain a colon ':'.
    """

    def __init__(self, name, unit=None, default=None):
        self.name = name
        self._value = default
        self.unit = unit
        self.default = default
        
    @property
    def value(self):
        if self.isSet():
            return self._value
        else:
            raise ValueError("Parameter value is not set")
            
    @value.setter
    def value(self, value):
        self._value = value
        
    def isSet(self):
        return self._value is not None
        
    def __repr__(self):
        result = "<Parameter(name='%s'" % self.name
        if self.isSet():
            result += ",value=%s" % repr(self.value)
        if self.unit:
            result += ",unit='%s'" % self.unit
        return result + ")>"

class IntegerParameter(Parameter):
    
    @property
    def value(self):
        if self.isSet():
            return int(self._value)
        else:
            raise ValueError("Parameter value is not set")
        
    @value.setter
    def value(self, value):
        try:
            self._value = int(value)
        except ValueError:
            raise ValueError("IntegerParameter given non-integer value of "
                             "type '%s'" % type(value))
                             
    def __repr__(self):
        result = super(IntegerParameter, self).__repr__()
        return result.replace("<Parameter", "<IntegerParameter", 1)

class FloatParameter(Parameter):
    
    @property
    def value(self):
        if self.isSet():
            return float(self._value)
        else:
            raise ValueError("Parameter value is not set")
    
    @value.setter
    def value(self, value):
        try:
            self._value = float(value)
        except ValueError:
            raise ValueError("FloatParameter given non-float value of "
                             "type '%s'" % type(value))
    
    def __repr__(self):
        result = super(FloatParameter, self).__repr__()
        return result.replace("<Parameter", "<FloatParameter", 1)


class Procedure(object):
    """Provides the base class of a procedure to organize the experiment
    execution. Procedures should be run in ProcedureThreads to ensure that
    concurrent control is properly managed. Example:
    
    procedure = Procedure()
    thread = ProcedureThread() # or QProcedureThread()
    thread.load(procedure)
    thread.start()
        
    Inhereting classes should define the following methods:
    - enter --> commands needed to startup instruments
    - execute --> commands for procedure execution
    - exit --> commands needed to stop instruments
    
    The exit method is called on sucessful completion, software error, or
    abort.    
    """
    
    _parameters = {}
    
    def __init__(self):
        self._updateParameters()
    
    def _updateParameters(self):
        """ Collects all the Parameter objects for this procedure and stores
        them in a meta dictionary so that the actual values can be set in their
        stead
        """
        if not self._parameters:
            self._parameters = {}
        for item in dir(self):
            parameter = getattr(self, item)
            if isinstance(parameter, Parameter):
                self._parameters[item] = parameter
                if parameter.isSet():
                    setattr(self, item, parameter.value)
                else:
                    setattr(self, item, None)
    
    def parametersAreSet(self):
        """ Returns True if all parameters are set """
        for name, parameter in self._parameters.iteritems():
            if getattr(self, name) is None:
                return False
        return True
    
    def checkParameters(function):
        """ Raises an exception if any parameter is missing before calling
        the associated function. Ensures that each value can be set and
        got, which should cast it into the right format. Used as a decorator 
        @checkParameters on the enter method
        """
        def wrapper(self):
            for name, parameter in self._parameters.iteritems():
                value = getattr(self, name)
                if value is None:
                    raise NameError("Missing %s '%s' in %s" % (
                        self.parameter.__class__, name, self.__class__))
                else:
                    parameter.value = value
                    setattr(self, name, parameter.value)
            return function(self)
        return wrapper
    
    def parameterValues(self):
        """ Returns a dictionary of all the Parameter values and grabs any 
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.iteritems():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                result[name] = parameter.value
            else:
                result[name] = None
        return result
        
    def parameterObjects(self):
        """ Returns a dictionary of all the Parameter objects and grabs any 
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.iteritems():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
            result[name] = parameter
        return result
        
    def setParameters(self, parameters, exceptMissing=True):
        """ Sets a dictionary of parameters and raises an exception if additional
        parameters are present if exceptMissing is True
        """
        for name, value in parameters.iteritems():
            if name in self._parameters:
                self._parameters[name].value = value
                setattr(self, name, self._parameters[name].value)
            else:
                if exceptMissing:
                    raise NameError("Parameter '%s' does not belong to '%s'" % (
                            name, repr(self)))
    
    @checkParameters   
    def enter(self):
        pass
        
    def execute(self):
        pass        
        
    def exit(self):
        pass


class ProcedureThread(Thread):
    """Encapsulates the Procedure to be run within a thread."""
    
    def __init__(self):
        Thread.__init__(self)
        self.procedure = None
        self.abortEvent = Event()
        self.abortEvent.clear()
        self.dataQueues = []
        self.progressQueue = Queue()
        self.finished = Event()
        
    def load(self, procedure):
        if not isinstance(procedure, Procedure):
            raise ValueError("Loading object must be inhereted from the"
                             " Procedure class")
        self.procedure = procedure
        self.procedure.hasAborted = self.hasAborted
        self.procedure.emitData = self.emitData
        self.procedure.emitProgress = self.emitProgress
        
    def run(self):
        if self.procedure is None:
            raise Exception("Attempting to run Procedure object before loading")
        self.procedure.enter()
        try:
            self.procedure.execute()
        except:
            import sys, traceback
            traceback.print_exc(file=sys.stdout)
        finally:
            self.procedure.exit()
            self.finished.set()
                  
    def emitProgress(self, precent):
        self.progressQueue.put(precent)
    
    def emitFinished(self):
        self.finished.set()
    
    def addDataQueue(self, queue):
        self.dataQueues.append(queue)
            
    def emitData(self, data):
        for queue in self.dataQueues:
            queue.put(data)
    
    def hasAborted(self):
        return self.abortEvent.isSet()
        
    def abort(self):
        self.abortEvent.set()
        
    def join(self, timeout=0):
        self.abortEvent.wait(timeout)
        if not self.abortEvent.isSet():
            self.abortEvent.set()
        super(ProcedureThread, self).join()

try:

    from PyQt4.QtCore import QThread, pyqtSignal

    class QProcedureThread(QThread):
        """Encapsulates the Procedure to be run within a QThread,
        compatible with PyQt4.
        """
        
        data = pyqtSignal(dict) 
        progress = pyqtSignal(float)
        finished = pyqtSignal()
        
        def __init__(self, parent):
            QThread.__init__(self, parent)
            self.procedure = None
            self.settings = settings
            self.abortEvent = Event()
            self.abortEvent.clear()
        
        def load(self, procedure):
            if not isinstance(procedure, Procedure):
                raise ValueError("Loading object must be inhereted from the"
                                 " Procedure class")
            self.procedure = procedure
            self.procedure.hasAborted = self.hasAborted
            self.procedure.emitData = self.data.emit
            self.procedure.emitProgress = self.progress.emit
            
        def run(self):
            if self.procedure is None:
                raise Exception("Attempting to run Procedure object before loading")
            self.procedure.enter()
            try:
                self.procedure.execute()
            except:
                import sys, traceback
                traceback.print_exc(file=sys.stdout)
            finally:
                self.procedure.exit()
                self.finished.emit()
        
        def hasAborted(self):
            return self.abortEvent.isSet()
        
        def abort(self):
            self.abortEvent.set()
            
        def join(self, timeout=0):
            self.abortEvent.wait(timeout)
            if not self.abortEvent.isSet():
                self.abortEvent.set()
            super(QProcedureThread, self).wait()
except:
    pass # Qt4 is not installed
    

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
    extended for the specific data collected for a Procedure
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
                    header += line.strip() + Results.LINE_BREAK
                    header_count += 1
                else:
                    header_read = True
        procedure = Results.parseHeader(header[:-1])
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
            


