# Instrument Base Class
#
# Authors: Colin Jermain
# Copyright 2013 Cornell University

import re

class Property(object):
    
    def __init__(self, asker, writer=None, doc=None, validator=None, search=None, formatter=None):
        """ Initailizes a new Property object based on the following inputs:
        
            writer -- string command for writing (setting)
            asker -- string command for asking (getting)
            doc -- string that describes the variable for the help docs
            validator -- a function that raises an exception if the value 
                        is invalid having been passed (self, instrument, value)
        """
        self._writer, self._asker = writer, asker
        self.doc, self.validator = doc, validator
        self.search, self.formatter = search, formatter
        
    def set(self, instrument, value):
        """ Set method calls for a write on the instrument using the writer
        command passed in during initialization. The value is passed
        through the validator function if its callable
        """
        if self._writer is None:
            raise Exception("Can not write to property '%s' on %s" % (
                            self.name, repr(instrument)))
        if callable(self.validator):
            self.validator(self, instrument, value)
        instrument.write(self._writer % value)
        
    def get(self, instrument):
        """ Get method calls for ask on the instrument using the asker
        command passed in during initalization.
        """
        answer = instrument.ask(self._asker)
        if self.search:
            search = re.search(self.search, answer, re.MULTILINE)
            if search:
                answer = search.group()
            else:
                raise Exception("Search pattern did not match answer to property"
                        "'%s' on %s" % (self.name, repr(instrument)))
        if callable(self.formatter):
            answer = self.formatter(answer)
        return answer
        
    def __str__(self):
        if self.doc is not None:
            return self.doc
        
    def __repr__(self):
        return "<Property(write='%s', ask='%s')>" % (self._writer, self._asker)


class PropertySet(object):
    
    def __init__(self, parent, properties={}):
        super(PropertySet, self).__init__()
        self.parent = parent
        self._cmds = {}
        for name, prop in properties.iteritems():
            self.add(name, prop)
        
    def add(self, name, prop):
        """ Adds a new Property object onto the PropertySet and attaches it
        to the parent class
        """
        if self == prop:
            return # Avoid adding itself to itself!
        if not issubclass(type(prop), (Property, PropertySet)):
            raise TypeError("Property %s must be a child of the Property class" %
                            prop)
        self._cmds[name] = prop
        prop.name = name
        p = property(prop.get, prop.set, doc=str(prop))
        setattr(self.parent.__class__, name, p)
        setattr(self.parent.__class__, "get_%s" % name, lambda s: prop.get(self))
        setattr(self.parent.__class__, "set_%s" % name, lambda s,v: prop.set(self, v))
        
    def add_multiple(self, properties):
        """ Add multiple Properties and PropertySets through a dictonary
        """
        if type(properties) is not dict:
            raise TypeError("Multiple properties must be passed as a dictionary")
        for name, prop in properties.iteritems():
            if issubclass(type(prop), (Property, PropertySet)):
                self.add(name, prop)
                
    def add_dir(self, obj):
        """ Add multiple Propertys and PropertySets from an objects directory
        """
        self.add_multiple({x: getattr(obj, x) for x in dir(obj)})
        
    def __repr__(self):
        return "<PropertySet%s>" % repr(self._cmds)

def range_validator(prop, instrument, value, minimum, maximum):
    """ Raises an exception if the value is not between the inclusive 
    set [minimum, maximum]
        
    Property(..., validator=lambda c,i,v: range_validator(c,i,v, MIN, MAX))
    """
    if value < minimum:
        raise ValueError("Value for '%s' is less than minimum (%s) on %s" % (
                prop.name, str(maximum), repr(instrument)))
    elif value > maximum:
        raise ValueError("Value for '%s' is greater than maximum (%s) on %s" % (
                prop.name, str(maximum), repr(instrument)))


def choices_validator(prop, instrument, value, choice_list):
    """ Raises an exception if the value is not in the list of choices,
    where the choice_list can be either a list or a string of the variable
    in the instrument that holds the list
    
    Property(..., validator=lambda c,i,v: choices_validator(c,i,v, CHOICES))
    """
    if type(choice_list) is str:
        choice_list = getattr(instrument, choice_list, [])
    if type(choice_list) is not list:
        raise ValueError("Incorrect type for choices list of validator "
                         "on %s" % repr(instrument))
    if value not in choice_list:
        raise ValueError("Invalid choice for property '%s' on %s" % (
            prop.name, repr(instrument)))
        

class Instrument(object):

    def __new__(cls, *args):
        """ Constructs a new Instrument object by stripping Property objects
        and storing them in the _cmds meta-data dictionary. These variables
        are replaced by properties (getter/setter pairs), which are deligated
        by the Property object.        
        """
        obj = super(Instrument, cls).__new__(cls)
        obj._cmds = PropertySet(obj)
        obj._cmds.add_dir(obj)
        return obj

    def __init__(self, connection):
        """ Initializes the Instrument by storing the connection. The connection
        object is checked to have the appropriate methods
        """
        self.connection = connection
        self._assert_connection_methods()
        
    def read(self):
        """ Reads until timeout from the connection using the read method """
        return "\n".join(self.connection.readlines())
        
    def write(self, command):
        """ Writes a command through the connection """
        self.connection.write(command)
        
    def ask(self, command):
        """ Writes a query and then reads the result, after first flushing the
        connection to ensure an appropriate reponse
        """
        self.connection.flush()
        self.write(command)
        return self.read()
        
    def _assert_connection_methods(self):
        """ Asserts that the connection has the appropriate methods:
        write, read, and flush
        """
        for name in ['write', 'read', 'flush']:
            method = getattr(self.connection, name, None)
            if not callable(method):
                raise NameError("Connection %s has no %s method for %s" % (
                            repr(self.connection), name, repr(self)))


class RangeException(Exception): pass

def linearInverse(y, m, b): 
    """ Inverts the fitting parameters to calculate x(y) from y(x)=m*x+b
    """
    return (m**-1)*(float(y) - b)
    
def linearInverseError(y, yError, m, mError, b, bError):
    """ Inverts the fitting parameters to calculate the std(x) from y(x)=m*x+b    
    """
    return ((mError*(b-y)/m**2)**2 + (bError/m)**2 + (yError/m)**2)**0.5

def discreteTruncate(number, discreteSet):
    """ Truncates the number to the closest element in the positive discrete set.
    Returns False if the number is larger than the maximum value or negative.    
    """
    if number < 0:
        return False
    discreteSet.sort()
    for item in discreteSet:
        if number <= item:
            return item
    return False
