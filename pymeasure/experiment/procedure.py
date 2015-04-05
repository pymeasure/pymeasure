"""

This file is part of the PyMeasure package.

Copyright (c) 2013-2015 Colin Jermain, Graham Rowlands

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""


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
    
    DATA_COLUMNS = []
    FINISHED, FAILED, ABORTED, QUEUED, RUNNING = 0, 1, 2, 3, 4
    
    _parameters = {}
    
    def __init__(self):
        self.status = Procedure.QUEUED
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
    
    def checkParameters(self):
        """ Raises an exception if any parameter is missing before calling
        the associated function. Ensures that each value can be set and
        got, which should cast it into the right format. Used as a decorator 
        @checkParameters on the enter method
        """
        for name, parameter in self._parameters.iteritems():
            value = getattr(self, name)
            if value is None:
                raise NameError("Missing %s '%s' in %s" % (
                    parameter.__class__, name, self.__class__))
    
    def parameterValues(self):
        """ Returns a dictionary of all the Parameter values and grabs any 
        current values that are not in the default definitions
        """
        result = {}
        for name, parameter in self._parameters.iteritems():
            value = getattr(self, name)
            if value is not None:
                parameter.value = value
                setattr(self, name, parameter.value)
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
                setattr(self, name, parameter.value)
            result[name] = parameter
        return result
        
    def refreshParameters(self):
        """ Enforces that all the parameters are re-cast and updated in the meta
        dictionary
        """
        for name, parameter in self._parameters.iteritems():
            value = getattr(self, name)
            parameter.value = value
            setattr(self, name, parameter.value)
        
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
    
    def enter(self):
        pass
        
    def execute(self):
        pass        
        
    def exit(self):
        pass
        
    def __str__(self):
        result = repr(self) + "\n"
        for name, obj in self.parameterObjects().iteritems():
            if obj.unit:
                result += "%s: %s %s\n" % (obj.name, obj.value, obj.unit)
            else:
                result += "%s: %s\n" % (obj.name, obj.value)
        return result


class UnknownProcedure(Procedure):
    """ Handles the case when a Procedure object can not be imported during
    loading in the Results class
    """
    
    def __init__(self, parameters):
        self._parameters = parameters
    
    def enter(self):
        raise Exception("UnknownProcedure can not be run")
