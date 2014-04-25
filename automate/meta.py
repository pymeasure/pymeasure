""" Temporary working file for Instrument and Command classes
"""

class Command(object):
    
    def __init__(self, writer, asker, doc=None, choices=[]):
        """ Initailizes a new Command object based on the following inputs:
        
            writer -- string SCPI command for writing (setting)
            asker -- string SCPI command for asking (getting)
            doc -- string that describes the variable for the help docs
            choices -- a list of possible discrete choices
        """
        self._writer, self._asker = writer, asker
        self.doc = doc
        self.choices = choices
        
    def set(self, instrument, value):
        """ Set method calls for a write on the instrument using the writer
        SCPI command passed in during initialization. Choices are evaluated
        if there is a non-zero sized list of them.
        """
        if len(self.choices) > 0:
            if value not in self.choices:
                raise ValueError("Invalid choice for property '%s' on %s" % (
                    self.name, repr(instrument)))
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
    
    voltage = Command('VOLT %d', 'VOLT:MEASURE?', 'Measured voltage', choices=[1,2,3])
    
