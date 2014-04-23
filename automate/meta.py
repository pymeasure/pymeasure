""" Temporary working file for Instrument and Command classes
"""

class Command(object):
    
    def __init__(self, writer, asker, doc=None):
        self._writer, self._asker = writer, asker
        self.doc = doc
        
    def set(self, instrument, value):
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
                setattr(obj.__class__, name, property(cmd.get, cmd.set, doc=str(cmd)))
        return obj

    def __init__(self, connection):
        self.conn = connection
        
    def write(self, command):
        pass
        
    def ask(self, command):
        pass
        
        
class ExampleInstrument(Instrument):
    
    voltage = Command('VOLT %d', 'VOLT:MEASURE?', 'Voltage')
    
