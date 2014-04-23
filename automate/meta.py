""" Temporary working file for Instrument and Command classes
"""

class Command(object):
    
    def __init__(self, writer, asker, doc=None, choices=[]):
        self._writer, self._asker = writer, asker
        self.doc = doc
        self.choices = choices
        
    def set(self, instrument, value):
        if len(self.choices) > 0:
            if value not in self.choices:
                raise ValueError("Invalid choice for property '%s' on %s" % (
                    self.name, repr(instrument)))
        instrument.write(self._writer % value)
        
    def get(self, instrument):
        instrument.ask(self._asker)
        
    def __str__(self):
        if self.doc is not None:
            return self.doc
        
    def __repr__(self):
        return "<Command(write='%s', ask='%s')>" % (self._writer, self._asker)
    

class Instrument(object):

    def __new__(cls, *args):
        obj = super(Instrument, cls).__new__(cls)
        obj._cmds = {}
        for name in dir(obj):
            cmd = getattr(obj, name)
            if issubclass(type(cmd), Command):
                obj._cmds[name] = cmd
                cmd.name = name
                setattr(obj.__class__, name, property(cmd.get, cmd.set, doc=str(cmd)))
        return obj

    def __init__(self, connection):
        self.conn = connection
        
    def write(self, command):
        pass
        
    def ask(self, command):
        pass
        
        
class ExampleInstrument(Instrument):
    
    voltage = Command('VOLT %d', 'VOLT:MEASURE?', 'Measured voltage', choices=[1,2,3])
    
