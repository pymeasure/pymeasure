""" Temporary working file for Instrument and Command classes
"""

class Command(object):
    
    def __init__(self, writer, asker, doc=None, validator=None):
        """ Initailizes a new Command object based on the following inputs:
        
            writer -- string SCPI command for writing (setting)
            asker -- string SCPI command for asking (getting)
            doc -- string that describes the variable for the help docs
            validator -- a function that raises an exception if the value 
                        is invalid having been passed (self, instrument, value)
        """
        self._writer, self._asker = writer, asker
        self.doc, self.validator = doc, validator
        
    def set(self, instrument, value):
        """ Set method calls for a write on the instrument using the writer
        SCPI command passed in during initialization. The value is passed
        through the validator function if its callable
        """
        if callable(self.validator):
            self.validator(self, instrument, value)
        instrument.write(self._writer % value)
        
    def get(self, instrument):
        """ Get method calls for ask on the instrument using the asker
        SCPI command passed in during initalization.
        """
        instrument.ask(self._asker)
        
    def __str__(self):
        if self.doc is not None:
            return self.doc
        
    def __repr__(self):
        return "<Command(write='%s', ask='%s')>" % (self._writer, self._asker)


def range_validator(command, instrument, value, minimum, maximum):
    """ Validates a value between the inclusive set [minimum, maximum]
        
    Command(..., validator=lambda c,i,v: range_validator(c,i,v, MIN, MAX))
    """
    if value < minimum:
        raise ValueError("Value for '%s' is less than minimum (%s) on %s" % (
                command.name, str(maximum), repr(instrument))
    elif value > maximum:
        raise ValueError("Value for '%s' is greater than maximum (%s) on %s" % (
                command.name, str(maximum), repr(instrument))


def choices_validator(command, instrument, value, choice_list):
    """ Validates a value out of a list of choices, where the choice_list
    can be either a list or a string of the variable in the instrument
    that holds the list
    
    Command(..., validator=lambda c,i,v: choices_validator(c,i,v, CHOICES))
    """
    if type(choice_list) is str:
        choice_list = getattr(instrument, choice_list, [])
    if type(choice_list) is not list:
        raise ValueError("Incorrect type for choices list of validator "
                         "on %s" % repr(instrument))
    if value not in choice_list:
        raise ValueError("Invalid choice for property '%s' on %s" % (
            command.name, repr(instrument))
        

class Instrument(object):

    def __new__(cls, *args):
        """ Constructs a new Instrument object by stripping Command objects
        and storing them in the _cmds meta-data dictionary. These variables
        are replaced by properties (getter/setter pairs), which are deligated
        by the Command object.        
        """
        obj = super(Instrument, cls).__new__(cls)
        obj._cmds = {}
        for name in dir(obj):
            cmd = getattr(obj, name)
            if issubclass(type(cmd), Command):
                obj._cmds[name] = cmd
                cmd.name = name
                setattr(obj.__class__, name, property(cmd.get, cmd.set, 
                        doc=str(cmd)))
        return obj

    def __init__(self, connection):
        """ Initializes the Instrument by storing the connection. The connection
        object is checked to have the appropriate methods
        """
        self.connection = connection
        self._assert_connection_methods()
        
    def read(self):
        """ Reads until timeout from the connection using the read method """
        return self.connection.read()
        
    def write(self, command):
        """ Writes a command through the connection """
        print command # Debug only
        self.connection.write(command)
        
    def ask(self, command):
        """ Writes a query and then reads the result, after first flushing the
        connection to ensure an appropriate reponse
        """
        print command # Debug only
        self.connection.flush()
        self.write(command)
        return self.read()
        
    def _assert_connection_methods(self):
        """ Asserts that the connection has the appropriate methods:
        write, read, and flush
        """
        for name in ['write', 'read', 'flush']:
            method = getattr(self.connection, name, None)
            if not callable(write_method):
                raise Exception("Connection %s for %s has no %s method" % (
                            repr(self.connection), repr(self), name))
        
class ExampleInstrument(Instrument):
    
    VOLTAGE_CHOICES = [1, 2, 3]
    voltage = Command('VOLT %d', 'VOLT:MEASURE?', 'Measured voltage',
                    validator=lambda c,i,v: choices_validator(c,i,v, 
                    ExampleInstrument.VOLTAGE_CHOICES))
    
