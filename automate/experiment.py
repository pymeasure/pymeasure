from threading import Event, Queue

class Parameter(object):
    """ Encapsulates the information for an experiment parameter
    with information about the name, and unit if supplied.
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
        return self.value is not None
        
    def __repr__(self):
        result = "<Parameter(name='%s'"
        if self.isSet():
            result += ",value='%s'" % repr(self.value)
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
        result = super(IntegerParameter, self).__repr__()
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
                    delattr(self, item)
    
    def parametersAreSet(self):
        """ Returns True if all parameters are set """
        for name, parameter in self._parameters.iteritems():
            if not hasattr(self, name):
                return False
        return True
    
    def checkParameters(self, function):
        """ Raises an exception if any parameter is missing before calling
        the associated function. Ensures that each value can be set and
        got, which should cast it into the right format. Used as a decorator 
        @checkParameters on the enter method
        """
        for name, parameter in self._parameters.iteritems():
            if not hasattr(self, name):
                raise NameError("Missing %s '%s' in %s" % (
                    self.parameter.__class__, name, self.__class__))
            else:
                parameter.value = getattr(self, name)
                setattr(self, name, parameter.value)
    
    def parameterValues(self):
        """ Returns a dictionary of all the parameters and grabs any current
        values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.iteritems():
            if not hasattr(self, name):
                result[name] = parameter
            else:
                parameter.value = getattr(self, name)
                result[name] = parameter.value)
        return result
    
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
        self.logQueue = Queue()
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
        self.procedure.log = self.emitLog
        
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
            
    def log(self, message):
        self.logQueue.put(message)
    
    def hasAborted(self):
        return self.abortEvent.isSet()
        
    def abort(self, timeout=0):
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
        log = pyqtSignal(str)
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
            self.procedure.log = self.log.emit
            
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
            
        def abort(self, timeout=0):
            self.abortEvent.wait(timeout)
            if not self.abortEvent.isSet():
                self.abortEvent.set()
            super(QProcedureThread, self).wait()



